from ultralytics import YOLO
import argparse
import cv2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from win_multiframework_installation.app.monitor import Monitor

model = YOLO('yolo11n.pt')  # 使用預訓練的 YOLOv8 模型

def arg_parser() :
    parser = argparse.ArgumentParser()
    parser.add_argument("input_source", help="Please input inference source.ex. C:\\<path>\\inference_video.mp4 or camera number")
    return parser
# load YOLO model（"yolov8n", "yolov8s" ...）

def main(args):
    if  args.input_source.isdigit():
        print("Init USB Camera in Windows,Please wait about 20 Second!")
        cap = cv2.VideoCapture(0)
    else:
        print("Streaming video!")
        # now_dir=os.path.dirname(os.path.abspath(__file__))
        # now_dir=now_dir.split('\\')
        # video_path=now_dir[:-2]
        # video_path=os.path.join('\\'.join(video_path),'videos','people.mp4')# 影片路徑
        # print(video_path)
        # cap = cv2.VideoCapture(video_path)
        cap = cv2.VideoCapture(args.input_source)
    video_h,video_w = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    monitor=Monitor(video_h,video_w)
    monitor.start_cpu_monitor()
    monitor.start_mem_monitor()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # 進行推論
        results = model(frame)
        annotated_frame = results[0].plot()
        if monitor.show_device['CPU']:
            chart = monitor.draw_cpu_chart()
            annotated_frame[-(video_h//3):, 10:-10] = chart  # put cpu monitor in bottom
        if monitor.show_device['Memory']:
            annotated_frame=monitor.draw_memory_usage_bar(annotated_frame)
        if monitor.show_help:
            annotated_frame=monitor.draw_helptext(annotated_frame)
        # show result
        cv2.imshow('YOLO Video Prediction', annotated_frame)
        input_key=cv2.waitKey(1)
        if input_key & 0xFF == ord('q'):
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
            monitor.show_help=not monitor.show_help
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
        elif input_key == ord('h'):  # press 'h' open/close help
            monitor.show_help=not monitor.show_help

    monitor.stop_cpu_monitor()
    monitor.stop_mem_monitor()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    args = arg_parser().parse_args()
    main(args)
