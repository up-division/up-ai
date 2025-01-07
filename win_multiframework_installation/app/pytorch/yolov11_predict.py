from ultralytics import YOLO
import argparse
import cv2
import os

model = YOLO('yolo11n.pt')  # 使用預訓練的 YOLOv8 模型

def arg_parser() :
    parser = argparse.ArgumentParser()
    parser.add_argument("input_source", help="Please input inference source.ex. C:\\<path>\\inference_vedio.mp4 or camera number")
    return parser
# load YOLO model（"yolov8n", "yolov8s" ...）

def main(args):
    if  args.input_source.isdigit():
        print("Init USB Camera in Windows,Please wait about 20 Second!")
        cap = cv2.VideoCapture(0)
    else:
        print("Streaming video!")
        now_dir=os.path.dirname(os.path.abspath(__file__))
        now_dir=now_dir.split('\\')
        video_path=now_dir[:-2]
        video_path=os.path.join('\\'.join(video_path),'video','people.mp4')# 影片路徑
        # print(video_path)
        cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 進行推論
        results = model(frame)

        annotated_frame = results[0].plot()

        # 顯示推論結果
        cv2.imshow('YOLO Video Prediction', annotated_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    args = arg_parser().parse_args()
    main(args)
