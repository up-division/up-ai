from ultralytics import YOLO
import argparse
import cv2
import os
from monitor import monitor

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
        if not cap.isOpened():
            print("Error: Unable to access the camera.")
            sys.exit()
    else:
        print("Streaming video!")
        cap = cv2.VideoCapture(args.input_source)

    # vedio_h,vedio_w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_h,video_w = (720,1280)

    from monitor import monitor
    monitor=monitor(video_h,video_w)
    monitor.start_cpu_monitor()
    monitor.start_mem_monitor()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        else:
            frame_resized = cv2.resize(frame, (video_w,video_h))
            # print(frame_resized.shape)

        # 進行推論
        results = model(frame_resized)

        annotated_frame = results[0].plot()
        if monitor.show_device['CPU']:
            chart = monitor.draw_cpu_chart()
            annotated_frame[-(video_h//3):, 10:-10] = chart  # put cpu monitor in bottom
        if monitor.show_device['Memory']:
            annotated_frame=monitor.draw_memory_usage_bar(annotated_frame)
        # show result
        cv2.imshow('YOLO Video Prediction', annotated_frame)
        input_key=cv2.waitKey(1)
        if input_key == 27:
            break
        elif input_key & 0xFF == ord('q'):
            monitor.stop_cpu_monitor()
            monitor.stop_mem_monitor()
            break
        elif input_key == ord('a'):  # press 'a' ,open/close cpu & memory monitor
            all_show=True
            for device, device_stat in monitor.show_device.items():
                if monitor.show_device[device]==False:
                    all_show=False
                    break
            if all_show:    #全開就全關閉
                monitor.stop_cpu_monitor()
                monitor.stop_mem_monitor()
            else:           #如果沒全開就先全開
                monitor.start_cpu_monitor()
                monitor.start_mem_monitor()
        elif input_key == ord('c'):  # press 'c' open/close cpu  monitor
            # monitor.show_device['CPU'] = not monitor.show_device['CPU']
            if monitor.show_device['CPU']:
                monitor.stop_cpu_monitor()
            else:
                monitor.start_cpu_monitor()
        elif input_key == ord('m'):  # press 'm' open/close memory monitor
            if monitor.show_device['Memory']:
                monitor.stop_mem_monitor()
            else:
                monitor.start_mem_monitor()
    monitor.stop_cpu_monitor()
    monitor.stop_mem_monitor()
    cap.release()
    cv2.destroyAllWindows()
if __name__ == "__main__":
    args = arg_parser().parse_args()
    main(args)
