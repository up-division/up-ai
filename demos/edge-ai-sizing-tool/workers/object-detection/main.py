# Copyright (C) 2025 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import argparse
from ast import Global
import cv2
import logging
import math
import numpy as np
import os
import sys
import re
import socket
import signal
import uvicorn
import threading
import subprocess as sp
import requests
import time
import urllib.parse
import zipfile
import platform
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
from yolo_download import export_yolo_model

import openvino as ov
import torch
from utils.augmentations import letterbox
from PIL import Image
from utils.plots import Annotator, colors
from notebook_utils import VideoPlayer
import collections
from typing import List, Tuple
from utils.general import scale_boxes, non_max_suppression


import xml.etree.ElementTree as ET

core=ov.Core()

latest_frame = None
lock = threading.Lock()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

VIDEO_DIR = Path("../assets/media")
MODEL_DIR = Path("./models")
CUSTOM_MODELS_DIR = Path("../custom_models/object-detection")
RTSP_SERVER_URL = "rtsp://localhost:8554"


def update_payload_status(workload_id: int, status):
    """
    Update the workload status in a safe way, allow-listing scheme, authority,
    and preventing unsafe path traversal.
    """
    if not is_valid_id(workload_id):
        logging.error(f"Invalid workload ID: {workload_id}. Refusing to update status.")
        return

    # Hardcode scheme & authority (safe allow-list)
    allowed_scheme = "http"
    allowed_netloc = "127.0.0.1:8080"

    # Build the path carefully. Reject characters such as '../'
    # in a real system, you might strictly allow digits only
    path = f"/api/workloads/{workload_id}"

    # Use urllib.parse to verify
    composed_url = f"{allowed_scheme}://{allowed_netloc}{path}"
    parsed_url = urllib.parse.urlparse(composed_url)

    # Enforce scheme & authority are what we expect
    if parsed_url.scheme != allowed_scheme or parsed_url.netloc != allowed_netloc:
        logging.error(f"URL scheme or authority not allowed: {parsed_url.geturl()}")
        return

    # Basic check for path traversal attempts (../, //, whitespace, etc.)
    if ".." in path or "//" in path or " " in path:
        logging.error(f"Invalid characters in URL path: {path}")
        return

    # Now safe to use
    url = parsed_url.geturl()

    data = {"status": status, "port": args.port}
    try:
        response = requests.patch(url, json=data)
        response.raise_for_status()
        logging.info(f"Successfully updated status to {status} for {workload_id}.")
    except requests.exceptions.RequestException as e:
        logging.info(f"Failed to update status: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("--- Initializing object detection worker ---")
    app.state.pipeline_metrics = {
        "total_fps": None,
        "number_streams": None,
        "average_fps_per_stream": None,
        "fps_streams": None,
        "timestamp": None,
    }
    thread = threading.Thread(target=main, daemon=True)
    thread.start()
    yield
    logging.info("--- Shutting down object detection worker ---")
    thread.join()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="FastAPI server for Intel® DLStreamer object detection model"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=f"{VIDEO_DIR}/people-detection.mp4",
        help="Input source e.g. /dev/video0, videofile.mp4, etc",
    )
    parser.add_argument(
        "--inference_mode",
        type=str,
        default="gvadetect",
        help="Inference mode: gvadetect or gvaclassify (default: gvadetect)",
    )
    parser.add_argument(
        "--model", type=str, default="yolo11n", help="Model name (default: yolo11n)"
    )
    parser.add_argument(
        "--model_parent_dir",
        type=str,
        default=MODEL_DIR,
        help=f"Path to the model directory (default: {MODEL_DIR})",
    )
    parser.add_argument(
        "--model_precision",
        type=str,
        default="FP16",
        help="Model precision (default: FP16)",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="CPU",
        help="Device to run inference on (default: CPU)",
    )
    parser.add_argument(
        "--decode_device",
        type=str,
        default="CPU",
        help="Device to run decode on (default: CPU)",
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size for inference (default: 1)",
    )
    parser.add_argument(
        "--tcp_port",
        type=int,
        default=5000,
        help="Port to spawn the DLStreamer pipeline (default: 5000)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5997,
        help="Port to run the FastAPI server on (default: 5997)",
    )
    parser.add_argument(
        "--id", type=int, help="Workload ID to update the workload status"
    )
    parser.add_argument(
        "--number_of_streams",
        type=int,
        default=1,
        help="Number of streams to run (default: 1)",
    )
    parser.add_argument(
        "--width_limit",
        type=int,
        default=640,
        help="Width limit for the video stream (default: 640)",
    )
    parser.add_argument(
        "--height_limit",
        type=int,
        default=480,
        help="Height limit for the video stream (default: 480)",
    )
    return parser.parse_args()


args = parse_arguments()

def stop_signal_handler(sig, frame):
    """
    Signal handler for SIGINT to terminate worker
    """
    logging.info("SIGINT received. Stopping the application...")
    exit(0)


signal.signal(signal.SIGINT, stop_signal_handler)

def is_rtsp_stream_running(rtsp_url, retries=5, delay=1):
    """
    Check if the RTSP stream is running by attempting to open it with OpenCV.
    Retry every second for a maximum number of retries.
    """
    for attempt in range(retries):
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                logging.info(f"RTSP stream is running at: {rtsp_url}")
                cap.release()
                return True
            else:
                logging.warning(
                    f"RTSP stream is not running at: {rtsp_url}. Retrying... ({attempt + 1}/{retries})"
                )
        except Exception as e:
            logging.error(
                f"Error checking RTSP stream: {e}. Retrying... ({attempt + 1}/{retries})"
            )
        time.sleep(delay)
    return False


def is_valid_video_file(filepath):
    """
    Check if the given file is a valid video file using OpenCV.
    """
    if not os.path.isfile(filepath):
        return False
    cap = cv2.VideoCapture(filepath)
    valid = cap.isOpened()
    cap.release()
    return valid


def is_valid_id(id):
    """
    Validate the workload ID to prevent URL manipulation and ensure it is a positive integer.
    """
    if isinstance(id, int) and id >= 0:
        return True
    return False

def opencv_server_image(
        tcp_port,
        input,
        model_full_path,
        model_label_path,
        device):
    
    TCP_IP = "127.0.0.1"
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((TCP_IP, tcp_port))
    server_socket.listen(5)
    conn, addr = server_socket.accept()


    player = None
    try:
        player = VideoPlayer(source=input, flip=False, fps=30, skip_first_frames=0)
        # Start capturing.
        player.start()
        processing_times = collections.deque()
        while True:
            frame = player.next()
            if frame is None:
                player = VideoPlayer(source=input, flip=False, fps=30, skip_first_frames=0)
                # Start capturing.
                player.start()
                continue
            
            _, jpeg = cv2.imencode('.jpg', frame)


            start_time = time.time()
            
            jpeg_bytes = jpeg.tobytes()
            header = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
            footer = b"\r\n"
            conn.sendall(header + jpeg_bytes + footer)
        
            stop_time = time.time()
            processing_times.append(stop_time - start_time)
            if len(processing_times) > 200:
                processing_times.popleft()
            processing_time = np.mean(processing_times) * 1000
            fps = 1000 / processing_time
            
            app.state.pipeline_metrics.update({
            "total_fps": fps,
            "number_streams": 1,
            "average_fps_per_stream": fps,
            "fps_streams": fps,
            "timestamp": time.time(),
            })
    except RuntimeError as e:
        print(e)
    finally:
        if player is not None:
            # Stop capturing.
            player.stop()
            
    # if(input.isdigit()):
    #     cap = cv2.VideoCapture(int(input))
    # else:
    #     cap=cv2.VideoCapture(input)

    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    #         continue
        # _, jpeg = cv2.imencode('.jpg', frame)
        # jpeg_bytes = jpeg.tobytes()
        # header = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
        # footer = b"\r\n"
        # conn.sendall(header + jpeg_bytes + footer)
            
    # cap.release()
    conn.close()
    server_socket.close()
    
def main():

    """
    Main function to start the GStreamer pipeline.
    """
    logging.info(
        f"View stream at url: http://localhost:{args.port}/result/{args.tcp_port}"
    )

    if os.path.realpath(args.input) != os.path.abspath(
        args.input
    ):  # Check if the model path is a symlink
        logging.info(
            f"Error: Input file {args.input} is a symlink or contains a symlink in its path. Refusing to open for security reasons."
        )
        update_payload_status(args.id, status="failed")
        sys.exit(1)

    # Ensure the video file exists
    if not os.path.exists(args.input):
        if args.input.isdigit():
            # args.input = "/dev/video" + args.input
            logging.info(
                f"Input is a device index or webcam: {args.input}. Skipping file download."
            )
        else:
            logging.error(
                "Input video file not found and no webcam detected. Please provide a valid input source."
            )
            update_payload_status(args.id, status="failed")
            exit(1)
    else:
        if not is_valid_video_file(args.input):
            logging.error(
                f"Input file '{args.input}' is not a valid video file. Please provide a valid video file."
            )
            update_payload_status(args.id, status="failed")
            exit(1)
    
    
    model_label_path = None

    if args.model.endswith(".zip"):
        model_zipfile_name = Path(args.model).stem
        model_extract_dir = MODEL_DIR / model_zipfile_name
        if not model_extract_dir.exists():
            logging.info(f"Extracting {args.model} to {model_extract_dir}")
            try:
                with zipfile.ZipFile(args.model, 'r') as zip_ref:
                    zip_ref.extractall(model_extract_dir)
            except Exception as e:
                logging.error(f"Failed to extract zip file {args.model}: {e}")
                update_payload_status(args.id, status="failed")
                exit(1)
        else:
            logging.info(f"Model directory {model_extract_dir} already exists, skipping extraction.")
        # Find for .xml file
        model_files = list(model_extract_dir.glob("*.xml"))
        if not model_files:
            logging.error(f"No model XML files found in {model_extract_dir}.")
            update_payload_status(args.id, status="failed")
            exit(1)
        model_full_path = model_files[0]
        
        # Find model label file
        label_files = list(model_extract_dir.glob("*.txt"))
        if label_files:
            model_label_path = label_files[0]
    else:
        # handle custom model uploaded to directory
        custom_model_path = CUSTOM_MODELS_DIR / args.model
        if not custom_model_path.exists():
            # predefined model
            model_status = export_yolo_model(
                model_name=args.model, model_parent_dir=args.model_parent_dir
            )
            
            if not model_status:
                update_payload_status(args.id, status="failed")
                exit(1)
                
            model_full_path = (
                Path(args.model_parent_dir)
                / f"{args.model}-{args.model_precision}"
                / f"{args.model}.xml"
            )
        else:
            custom_model_files = list(custom_model_path.glob("*.xml"))
            if not custom_model_files:
                logging.error(f"No model XML files found in {custom_model_path}.")
                update_payload_status(args.id, status="failed")
                exit(1)
            model_full_path = custom_model_files[0]
            label_files = list(custom_model_path.glob("*.txt"))
            if label_files:
                model_label_path = label_files[0]

    global NAMES
    tree = ET.parse(model_full_path)
    root = tree.getroot()
    rt_info = root.find("rt_info")
    model_info = rt_info.find("model_info")
    labels_str = model_info.find("labels").attrib["value"]
    labels_list = labels_str.split()

    NAMES = {i: label for i, label in enumerate(labels_list)}
    
    # Start the pipeline
    logging.info("Starting the pipeline...")
    try:
        update_payload_status(args.id, status="active")
        run_object_detection( source= int(args.input) if args.input.isdigit() else args.input,
                                 flip=False,
                                 skip_first_frames=0,
                                 model=model_full_path,
                                 device=args.device)
        
        # opencv_server_image(tcp_port=args.tcp_port,
        #                     input=args.input,
        #                     model_full_path=model_full_path,
        #                     model_label_path=model_label_path,
        #                     device=args.device)
        
    except KeyboardInterrupt:
        logging.info("Pipeline interrupted. Exiting...")
    except Exception as e:
        update_payload_status(args.id, status="failed")
        logging.error(f"An error occurred while running the pipeline: {e}")


def mjpeg_stream(host: str = "127.0.0.1", port: int = 5000):
    """
    Connect to the GStreamer TCP server and yield MJPEG frames.
    """
    # Connect to the TCP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        buffer = b""

        while True:
            # Read data from the TCP server
            data = client_socket.recv(4096)
            if not data:
                break

            buffer += data
            while b"\r\n\r\n" in buffer:
                frame, _, buffer = buffer.partition(b"\r\n\r\n")

                try:
                    # Convert raw frame data to a NumPy array and decode the frame
                    np_frame = np.frombuffer(frame, dtype=np.uint8)
                    image = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
                    if image is None:
                        continue

                    # Encode the image as JPEG
                    _, jpeg_frame = cv2.imencode(".jpg", image)

                    # Yield the encoded JPEG frame
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n"
                        + jpeg_frame.tobytes()
                        + b"\r\n"
                    )
                except Exception as e:
                    logging.info(f"Error processing frame: {e}")


def generate_frames():
    cap = cv2.VideoCapture(args.input)  # 改成影片路徑也可以
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    delay = int(1000 / fps)
    
    prev_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        app.state.pipeline_metrics.update({
            "total_fps": fps,
            "number_streams": 1,
            "average_fps_per_stream": fps,
            "fps_streams": fps,
            "timestamp": time.time(),
            })
        cv2.waitKey(delay)
    cap.release()
    
def prepare_input_tensor(image: np.ndarray):
    """
    Converts preprocessed image to tensor format according to YOLOv9 input requirements.
    Takes image in np.array format with unit8 data in [0, 255] range and converts it to torch.Tensor object with float data in [0, 1] range

    Parameters:
      image (np.ndarray): image for conversion to tensor
    Returns:
      input_tensor (torch.Tensor): float tensor ready to use for YOLOv9 inference
    """
    input_tensor = image.astype(np.float32)  # uint8 to fp16/32
    input_tensor /= 255.0  # 0 - 255 to 0.0 - 1.0

    if input_tensor.ndim == 3:
        input_tensor = np.expand_dims(input_tensor, 0)
    return input_tensor

def preprocess_image(img0: np.ndarray):
    """
    Preprocess image according to YOLOv9 input requirements.
    Takes image in np.array format, resizes it to specific size using letterbox resize, converts color space from BGR (default in OpenCV) to RGB and changes data layout from HWC to CHW.

    Parameters:
      img0 (np.ndarray): image for preprocessing
    Returns:
      img (np.ndarray): image after preprocessing
      img0 (np.ndarray): original image
    """
    # resize
    img = letterbox(img0, auto=False)[0]

    # Convert
    img = img.transpose(2, 0, 1)
    img = np.ascontiguousarray(img)
    return img, img0

def detect(
    model: ov.Model,
    image_path: Path,
    conf_thres: float = 0.25,
    iou_thres: float = 0.45,
    classes: List[int] = None,
    agnostic_nms: bool = False,
):
    """
    OpenVINO YOLOv9 model inference function. Reads image, preprocess it, runs model inference and postprocess results using NMS.
    Parameters:
        model (Model): OpenVINO compiled model.
        image_path (Path): input image path.
        conf_thres (float, *optional*, 0.25): minimal accepted confidence for object filtering
        iou_thres (float, *optional*, 0.45): minimal overlap score for removing objects duplicates in NMS
        classes (List[int], *optional*, None): labels for prediction filtering, if not provided all predicted labels will be used
        agnostic_nms (bool, *optional*, False): apply class agnostic NMS approach or not
    Returns:
       pred (List): list of detections with (n,6) shape, where n - number of detected boxes in format [x1, y1, x2, y2, score, label]
       orig_img (np.ndarray): image before preprocessing, can be used for results visualization
       inpjut_shape (Tuple[int]): shape of model input tensor, can be used for output rescaling
    """
    if isinstance(image_path, np.ndarray):
        img = image_path
    else:
        img = np.array(Image.open(image_path))
    preprocessed_img, orig_img = preprocess_image(img)
    input_tensor = prepare_input_tensor(preprocessed_img)
    predictions = torch.from_numpy(model(input_tensor)[0])
    pred = non_max_suppression(predictions, conf_thres, iou_thres, classes=classes, agnostic=agnostic_nms)
    return pred, orig_img, input_tensor.shape

def draw_boxes(
    predictions: np.ndarray,
    input_shape: Tuple[int],
    image: np.ndarray,
    names,
    # names: List[str],
):
    """
    Utility function for drawing predicted bounding boxes on image
    Parameters:
        predictions (np.ndarray): list of detections with (n,6) shape, where n - number of detected boxes in format [x1, y1, x2, y2, score, label]
        image (np.ndarray): image for boxes visualization
        names (List[str]): list of names for each class in dataset
        colors (Dict[str, int]): mapping between class name and drawing color
    Returns:
        image (np.ndarray): box visualization result
    """
    if not len(predictions):
        return image

    annotator = Annotator(image, line_width=1, example=str(names))
    # Rescale boxes from input size to original image size
    predictions[:, :4] = scale_boxes(input_shape[2:], predictions[:, :4], image.shape).round()

    # Write results
    for *xyxy, conf, cls in reversed(predictions):
        label = f"{names.get(int(cls),'Unkown')} {conf:.2f}"        

        annotator.box_label(xyxy, label, color=colors(int(cls), True))
    return image

def run_object_detection(
    source=0,
    flip=False,
    skip_first_frames=0,
    model="",
    device=args.device,
    video_width: int = None,  # if not set the original size is used
):
    global latest_frame
    player = None
    
    ov_model = core.read_model(model)

    global NAMES
    compiled_model = core.compile_model(ov_model, device)
    
    try:
        while True:
            # Create a video player to play with target fps.
            # player = VideoPlayer(source=source, flip=flip, fps=30, skip_first_frames=skip_first_frames)
            player = VideoPlayer(source=source, flip=flip, fps=60, skip_first_frames=skip_first_frames)

            # Start capturing.
            player.start()
    
            processing_times = collections.deque()
            while True:
                # Grab the frame.
                frame = player.next()
                if frame is None:
                    print("Source ended")
                    # player.start()
                    # continue
                    break
    
                if video_width:
                    # If the frame is larger than video_width, reduce size to improve the performance.
                    # If more, increase size for better demo expirience.
    
                    scale = video_width / max(frame.shape)
                    frame = cv2.resize(
                        src=frame,
                        dsize=None,
                        fx=scale,
                        fy=scale,
                        interpolation=cv2.INTER_AREA,
                    )
    
                # Get the results.
                input_image = np.array(frame)
    
                start_time = time.time()
                detections, _, input_shape = detect(compiled_model, input_image[:, :, ::-1])
                stop_time = time.time()
                
                image_with_boxes = draw_boxes(detections[0], input_shape, input_image, NAMES)
    
                frame = image_with_boxes

                processing_times.append(stop_time - start_time)
                # Use processing times from last 200 frames.
                if len(processing_times) > 200:
                    processing_times.popleft()

                _, f_width = frame.shape[:2]
                # Mean processing time [ms].
                processing_time = np.mean(processing_times) * 1000
                fps = 1000 / processing_time
                
                app.state.pipeline_metrics.update({
                "total_fps": fps,
                "number_streams": 1,
                "average_fps_per_stream": fps,
                "fps_streams": fps,
                "timestamp": time.time(),
                })
                with lock:
                    latest_frame = frame
            if player is not None:
            # Stop capturing.
                player.stop()
                
    # ctrl-c
    except KeyboardInterrupt:
        print("Interrupted")
    # any different error
    except RuntimeError as e:
        print(e)

        
def mjpeg_generator():
    global latest_frame
    while True:
        with lock:
            if latest_frame is None:
                continue
            ret, jpeg = cv2.imencode('.jpg', latest_frame)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")


@app.get("/video")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/result")
def get_mjpeg_stream():
    """
    Serve the MJPEG stream as an HTTP response.
    """
    
    try:
        return StreamingResponse(
            mjpeg_generator(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )
    except Exception as e:
        return JSONResponse(
            {
                "status": False,
                "message": "An error occurred while retrieving mjpeg stream",
            }
        )
    
# @app.get("/result")
# def get_mjpeg_stream():
#     """
#     Serve the MJPEG stream as an HTTP response.
#     """
#     try:
#         return StreamingResponse(
#             mjpeg_stream(port=args.tcp_port),
#             media_type="multipart/x-mixed-replace; boundary=frame",
#         )
#     except Exception as e:
#         return JSONResponse(
#             {
#                 "status": False,
#                 "message": "An error occurred while retrieving mjpeg stream",
#             }
#         )


@app.get("/api/metrics")
def get_pipeline_metrics():
    """
    Return the current pipeline metrics.
    """
    try:
        result = {
            "data": app.state.pipeline_metrics,
            "status": "success",
        }
        return JSONResponse(result)
    except Exception as e:
        logging.error(f"Error retrieving metrics: {e}")
        return JSONResponse(
            {"status": False, "message": "An error occurred while retrieving metrics"}
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=args.port)
