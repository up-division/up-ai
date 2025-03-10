import threading
import numpy as np
import cv2
import psutil
import os

class Monitor:
    def __init__(self,image_height,image_width):
        cpu_num=psutil.cpu_count(logical=True)
        self.show_device = {
        "CPU": False,
        "Memory": False,
        }
        self.show_help=True
        self.device_usage = {
        "CPU": {'core_num':cpu_num,'core_usage':[0.0]*cpu_num},
        "ALL_memory": {'use_per':0.1,'tot_mem':psutil.virtual_memory().total/((1024*1024*1024)),'use_mem':1.0},
        "program_memory": {'use_per':0.1,'tot_mem':psutil.virtual_memory().total/((1024*1024*1024)),'use_mem':1.0},
        }
        self.program_process = psutil.Process(os.getpid())
        self.input_h=image_height//3
        self.input_w=image_width-20
        self.history=[]#CPU

        self.mem_bar_config = {
            'x': int(image_width * 0.02),
            'y': int(image_height * 0.05),
            'width': int(image_width * 0.3),
            'height': int(image_height * 0.02),
            'space': int(image_height * 0.03),
            'opacity': 0.7,
            'colors': {
                'background': (50, 50, 50),
                'bar_background': (100, 100, 100),
                'bar_fill': (255, 105, 180)
            },
            'text' : {
                'width' : 150,
                'height' : 15,
                'fontFace' : cv2.FONT_HERSHEY_SIMPLEX,
                'fontScale' : float(format(image_width / 2400,'.1f')),
                'color' : (255, 255, 255),
                'thickness' : 1,
                'lineType' : cv2.LINE_AA,
            }
        }
        self.cal_mem_bar_text()
        self.fps_text_config = {
            'x': int(image_width * 0.5),
            'y': int(image_height * 0.05),
            'width': int(image_width * 0.3),
            'height': int(image_height * 0.02),
            'fontScale' : float(format(image_width / 1500,'.1f')),
            'space': int(image_height * 0.03),
            'fontFace' : cv2.FONT_HERSHEY_SIMPLEX,
            'color' : (0, 0, 255),
            'thickness' : 1,
            'lineType' : cv2.LINE_AA
        }
        fps_text_width,self.fps_text_config['y']=self.cal_fps_loca(self.fps_text_config['fontFace'], self.fps_text_config['fontScale'],
                                                                              self.fps_text_config['thickness'],self.fps_text_config['space'])
        self.fps_text_config['x'] = image_width - fps_text_width
        # print(str(self.fps_text_config['x']),str(self.fps_text_config['y']))


    def start_cpu_monitor(self):
        self.show_device['CPU'] = True
        print('CPU tread strart')
        self.cpu_thread = threading.Thread(target=self.update_cpu_usage)
        self.cpu_thread.start()
    def stop_cpu_monitor(self):
        self.show_device['CPU'] = False
        print('CPU tread end')
        self.history=[]
        # self.cpu_thread.join()

    def start_mem_monitor(self):
        self.show_device['Memory'] = True
        print('Mem tread strart')
        self.memory_thread = threading.Thread(target=self.update_mem_usage)
        self.memory_thread.start()
    def stop_mem_monitor(self):
        self.show_device['Memory'] = False
        print('Mem tread end')
        # self.memory_thread.join()

    def update_cpu_usage(self):
        while self.show_device['CPU']:
            self.device_usage['CPU']['core_usage'] = psutil.cpu_percent(interval=1, percpu=True)
            threading.Event().wait(0.1)  # 定时 1 秒

    def update_mem_usage(self):
        while self.show_device['Memory']:
            # mem_read_ok =  psutil.virtual_memory()
            # self.device_usage['ALL_memory']['use_mem']=psutil.virtual_memory()[3]/(1024*1024*1024)
            # self.device_usage['ALL_memory']['use_per']=psutil.virtual_memory()[2]/self.device_usage['ALL_memory']['tot_mem']
            self.device_usage['ALL_memory']['use_mem']=psutil.virtual_memory().used/(1024*1024*1024)
            self.device_usage['ALL_memory']['use_per']=psutil.virtual_memory().percent/100
            program_memory = self.program_process.memory_info()
            self.device_usage['program_memory']['use_mem']=program_memory.rss/(1024*1024*1024)
            self.device_usage['program_memory']['use_per']=self.device_usage['program_memory']['use_mem']/self.device_usage['ALL_memory']['tot_mem']
            threading.Event().wait(1)  # 定时 1 秒
    def cal_fps_loca(self, fontface, font_scale, thickness,space):
        defualt_str='Inference time: 10000 ms 1000 FPS'
        text_size, baseline = cv2.getTextSize(defualt_str, fontface, font_scale, thickness)
        text_width, text_height = text_size
        return text_width, text_height
    
    def show_fps(self, image,frame_infer_time):
        fps = 1 / frame_infer_time
        infer_time_ms = frame_infer_time * 1000
        proccessed_image=cv2.putText(
                img=image,
                text=f"Inference time: {infer_time_ms:.1f}ms ({fps:.1f} FPS)",
                org=(self.fps_text_config['x'], self.fps_text_config['y']),
                fontFace=self.fps_text_config['fontFace'],
                fontScale=self.fps_text_config['fontScale'],
                color=self.fps_text_config['color'],
                thickness=self.fps_text_config['thickness'],
                lineType=self.fps_text_config['lineType'],
            )
        return proccessed_image
    
    def cal_mem_bar_text(self):
        max_len_device=''
        for device in self.device_usage:
            if len(device) > len(max_len_device):
                max_len_device=device
        (self.mem_bar_config['text']['width'],self.mem_bar_config['text']['height']), baseline = cv2.getTextSize(max_len_device, self.mem_bar_config['text']['fontFace'],  self.mem_bar_config['text']['fontScale'],  self.mem_bar_config['text']['thickness'])

    def draw_cpu_chart(self):
        """
        CPU使用率表
        :param usages: 當前CPU使用率列表
        :param history: 過去資訊
        :param width: 寬度
        :param height: 高度
        :return: 回傳圖表
        """
        POINT_SPACING=5
        margin = 10
        graph_width = self.input_w - margin * 2
        graph_height = self.input_h - margin * 2

        # 建空畫布
        # img = np.zeros((height, width, 3), dtype=np.uint8)
        img = np.zeros((self.input_h, self.input_w, 3), dtype=np.uint8)
        img.fill(255)
        cv2.rectangle(img, (0, - margin * 2), (self.input_w, self.input_h), (169, 169, 169), -1)  # 灰色背景
        # 畫座標軸
        cv2.line(img, (margin, self.input_h - margin), (self.input_w - margin, self.input_h - margin), (255, 255, 255), 2)  # X轴
        cv2.line(img, (margin, margin), (margin, self.input_h - margin), (255, 255, 255), 2)  # Y轴

        # 畫Y座標
        for i in range(0, 101, 20):  # 0%到100%的刻度
            y = self.input_h - margin - int(i / 100 * graph_height)
            cv2.line(img, (margin - 5, y), (margin, y), (255, 255, 255), 1)
            cv2.putText(img, f"{i}%", (10, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        # 更新history
        self.history.append(self.device_usage['CPU']['core_usage'])
        if len(self.history) > graph_width // POINT_SPACING:
            self.history.pop(0)  # 移除過舊history

        # 畫折線圖
        colors = [
            (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0),
            (0, 255, 255), (255, 0, 255), (200, 100, 50), (50, 100, 200)
        ]  # 每个核心分配不同颜色

        for core in range(len(self.device_usage['CPU']['core_usage'])):
            for x in range(1, len(self.history)):
                prev_x = margin + (x - 1) * POINT_SPACING
                curr_x = margin + x * POINT_SPACING
                prev_y = self.input_h - margin - int(self.history[x - 1][core] / 100 * graph_height)
                curr_y = self.input_h - margin - int(self.history[x][core] / 100 * graph_height)
                cv2.line(img, (prev_x, prev_y), (curr_x, curr_y), colors[core % len(colors)], 1)

            # 顯示核心標記
            cv2.putText(img, f"Core {core + 1}: {self.device_usage['CPU']['core_usage'][core]:.1f}%", 
                        (self.input_w - margin - 150, margin + core * 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[core % len(colors)], 1)

        return img
    
    def draw_memory_usage_bar(self, image):
        """
        在插入的圖像上繪制存儲使用情況的進度條，且根據圖像大小調整條型大小。

        Args:
            image: 原始圖像 (numpy 數據)
        """
        height, width, _ = image.shape
        mem_dict = self.device_usage.copy()
        mem_dict.pop("CPU")


        # 創建透明區域的圖層
        overlay = image.copy()
        text_width=int(self.mem_bar_config['width'] * 0.35)
        # 計算區塊的區域
        rect_x1 = self.mem_bar_config['x'] - 10 
        rect_y1 = self.mem_bar_config['y'] - 10
        rect_x2 = self.mem_bar_config['x'] + self.mem_bar_config['width'] + text_width +20 
        rect_y2 = self.mem_bar_config['y'] + self.mem_bar_config['space'] * len(mem_dict)

        # 繪制區塊
        cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), self.mem_bar_config['colors']['background'], -1)

        # 添加透明效果
        image = cv2.addWeighted(overlay, self.mem_bar_config['opacity'], image, 1 - self.mem_bar_config['opacity'], 0)

        # 繪制進度條和文字
        for i, (device, usage) in enumerate(mem_dict.items()):
            if device == "Memory" and not self.show_device.get('Memory', True):
                continue  # 跳過 Memory
            
            # 計算進度條座標
            start_point_x=self.mem_bar_config['x']
            bar_x1 = self.mem_bar_config['x'] + self.mem_bar_config['text']['width']
            bar_y1 = self.mem_bar_config['y'] + i * self.mem_bar_config['space']
            bar_x2 = int(bar_x1 + self.mem_bar_config['width'] * usage['use_per'])# + text_width
            bar_y2 = bar_y1 + self.mem_bar_config['height']

            # 繪制進度條背景
            cv2.rectangle(image, (bar_x1, bar_y1), (bar_x1 + self.mem_bar_config['width'], bar_y2), self.mem_bar_config['colors']['bar_background'], -1)

            # 繪制進度條填充部分
            cv2.rectangle(image, (bar_x1, bar_y1), (bar_x2, bar_y2), self.mem_bar_config['colors']['bar_fill'], -1)

            # 顯示硬體類別文字
            cv2.putText(image, f"{' '.join(device.split('_'))}", (start_point_x , bar_y1 + self.mem_bar_config['height']), self.mem_bar_config['text']['fontFace'],
                        self.mem_bar_config['text']['fontScale'], self.mem_bar_config['text']['color'], self.mem_bar_config['text']['thickness'], self.mem_bar_config['text']['lineType'])

            # 顯示使用率
            cv2.putText(image, "{use_mem:.1f}/{tot_mem:.1f} GB".format(**usage), (bar_x1 + 5, bar_y1 + self.mem_bar_config['height']),self.mem_bar_config['text']['fontFace'],
                        self.mem_bar_config['text']['fontScale'], self.mem_bar_config['text']['color'], self.mem_bar_config['text']['thickness'], self.mem_bar_config['text']['lineType'])

        return image
    
    def draw_helptext(self, image):
        # if self.show_help:
        rect_w = 225
        rect_h = 100
        margin = 200
        overlay = image.copy()

        # 繪製灰色矩形
        # rect_top_left = (self.input_w - rect_w, margin)  # 矩形左上角位置
        # rect_bottom_right = (self.input_w - margin, margin + rect_h)  # 矩形右下角位置
        # rect_top_left = (image.shape[1] - rect_w - margin, margin)  # 图片的最右边减去矩形宽度和 margin
        # rect_bottom_right = (image.shape[1] - margin, margin + rect_h)  # 矩形右下角
        # cv2.rectangle(overlay, rect_top_left, rect_bottom_right, (50, 50, 50), -1)
        # cv2.addWeighted(overlay, 0.5, image, 1 - 0.5, 0, image)

        text_lines = [
            "Quit : 'Esc' or 'q'",
            "Open/Close CPU&Mem : 'a'",
            "Open/Close CPU : 'c'",
            "Open/Close Mem : 'm'",
            "Open/Close Help : 'h'"
        ]
        
        # 設置字體、大小和颜色
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.45
        color = (255, 255, 255)  # 白色文字
        thickness = 1
        
        # 初始y坐標
        y0, dy = margin + 20, 25
        
        for i, line in enumerate(text_lines):
            y = y0 + i * dy
            cv2.putText(image, line, (image.shape[1] - rect_w + 10, y), font, font_scale, color, thickness)
            # cv2.putText(image, line, (self.input_w - rect_w + 10, y), font, font_scale, color, thickness)

        return image
