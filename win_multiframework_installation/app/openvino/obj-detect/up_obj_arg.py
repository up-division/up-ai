import collections
import time
import cv2
import sys
import os
import openvino as ov
import threading
import numpy as np
from pathlib import Path
from typing import List, Tuple
import torch
import torchvision
import yaml
import argparse
import ctypes
from ctypes import *

core=ov.Core()

def initialize_arg_parser():
    """Initialize argument parser for the script."""
    parser = argparse.ArgumentParser(
        description="Detection Example - Tracker with ByteTrack and Supervision"
    )
    parser.add_argument(
        "-m", "--model", help="Path for the HEF model.", default="yolov11n.xml"
    )
    parser.add_argument(
        "-i", "--input", default="input_video.mp4", help="The input source."
    )
    parser.add_argument(
        "-d", "--device", default="input_video.mp4", help="Inefrence device."
    )
    parser.add_argument(
        "-hm", "--hardware_moinitor", action="store_true",default=False, help="Path to the input video."
    )
    return parser

class Colors:
    # Ultralytics color palette https://ultralytics.com/
    def __init__(self):
        # hex = matplotlib.colors.TABLEAU_COLORS.values()
        hexs = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb(f'#{c}') for c in hexs]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


colors = Colors()  # create instance for 'from utils.plots import colors'

def yaml_load(file='data.yaml'):
    # Single-line safe yaml loading
    with open(file, errors='ignore') as f:
        return yaml.safe_load(f)

def clip_boxes(boxes, shape):
    # Clip boxes (xyxy) to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2


def scale_boxes(img1_shape, boxes, img0_shape, ratio_pad=None):
    # Rescale boxes (xyxy) from img1_shape to img0_shape
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    boxes[:, [0, 2]] -= pad[0]  # x padding
    boxes[:, [1, 3]] -= pad[1]  # y padding
    boxes[:, :4] /= gain
    clip_boxes(boxes, img0_shape)
    return boxes

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    y[..., 2] = x[..., 0] + x[..., 2] / 2  # bottom right x
    y[..., 3] = x[..., 1] + x[..., 3] / 2  # bottom right y
    return y

def is_ascii(s=''):
    # Is string composed of all ASCII (no UTF) characters? (note str().isascii() introduced in python 3.7)
    s = str(s)  # convert list, tuple, None, etc. to str
    return len(s.encode().decode('ascii', 'ignore')) == len(s)

class Annotator:
    # YOLOv5 Annotator for train/val mosaics and jpgs and detect/hub inference annotations
    def __init__(self, im, line_width=None, font_size=None, font='Arial.ttf', pil=False, example='abc'):
        assert im.data.contiguous, 'Image not contiguous. Apply np.ascontiguousarray(im) to Annotator() input images.'
        non_ascii = not is_ascii(example)  # non-latin labels, i.e. asian, arabic, cyrillic
        self.pil = pil or non_ascii
        if self.pil:  # use PIL
            self.im = im if isinstance(im, Image.Image) else Image.fromarray(im)
            self.draw = ImageDraw.Draw(self.im)
            self.font = check_pil_font(font='Arial.Unicode.ttf' if non_ascii else font,
                                       size=font_size or max(round(sum(self.im.size) / 2 * 0.035), 12))
        else:  # use cv2
            self.im = im
        self.lw = line_width or max(round(sum(im.shape) / 2 * 0.003), 2)  # line width

    def box_label(self, box, label='', color=(128, 128, 128), txt_color=(255, 255, 255)):
        # Add one xyxy box to image with label
        if self.pil or not is_ascii(label):
            self.draw.rectangle(box, width=self.lw, outline=color)  # box
            if label:
                w, h = self.font.getsize(label)  # text width, height
                outside = box[1] - h >= 0  # label fits outside box
                self.draw.rectangle(
                    (box[0], box[1] - h if outside else box[1], box[0] + w + 1,
                     box[1] + 1 if outside else box[1] + h + 1),
                    fill=color,
                )
                # self.draw.text((box[0], box[1]), label, fill=txt_color, font=self.font, anchor='ls')  # for PIL>8.0
                self.draw.text((box[0], box[1] - h if outside else box[1]), label, fill=txt_color, font=self.font)
        else:  # cv2
            p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
            cv2.rectangle(self.im, p1, p2, color, thickness=self.lw, lineType=cv2.LINE_AA)
            if label:
                tf = max(self.lw - 1, 1)  # font thickness
                w, h = cv2.getTextSize(label, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
                outside = p1[1] - h >= 3
                p2 = p1[0] + w, p1[1] - h - 3 if outside else p1[1] + h + 3
                cv2.rectangle(self.im, p1, p2, color, -1, cv2.LINE_AA)  # filled
                cv2.putText(self.im,
                            label, (p1[0], p1[1] - 2 if outside else p1[1] + h + 2),
                            0,
                            self.lw / 3,
                            txt_color,
                            thickness=tf,
                            lineType=cv2.LINE_AA)

    def masks(self, masks, colors, im_gpu=None, alpha=0.5):
        """Plot masks at once.
        Args:
            masks (tensor): predicted masks on cuda, shape: [n, h, w]
            colors (List[List[Int]]): colors for predicted masks, [[r, g, b] * n]
            im_gpu (tensor): img is in cuda, shape: [3, h, w], range: [0, 1]
            alpha (float): mask transparency: 0.0 fully transparent, 1.0 opaque
        """
        if self.pil:
            # convert to numpy first
            self.im = np.asarray(self.im).copy()
        if im_gpu is None:
            # Add multiple masks of shape(h,w,n) with colors list([r,g,b], [r,g,b], ...)
            if len(masks) == 0:
                return
            if isinstance(masks, torch.Tensor):
                masks = torch.as_tensor(masks, dtype=torch.uint8)
                masks = masks.permute(1, 2, 0).contiguous()
                masks = masks.cpu().numpy()
            # masks = np.ascontiguousarray(masks.transpose(1, 2, 0))
            masks = scale_image(masks.shape[:2], masks, self.im.shape)
            masks = np.asarray(masks, dtype=np.float32)
            colors = np.asarray(colors, dtype=np.float32)  # shape(n,3)
            s = masks.sum(2, keepdims=True).clip(0, 1)  # add all masks together
            masks = (masks @ colors).clip(0, 255)  # (h,w,n) @ (n,3) = (h,w,3)
            self.im[:] = masks * alpha + self.im * (1 - s * alpha)
        else:
            if len(masks) == 0:
                self.im[:] = im_gpu.permute(1, 2, 0).contiguous().cpu().numpy() * 255
            colors = torch.tensor(colors, device=im_gpu.device, dtype=torch.float32) / 255.0
            colors = colors[:, None, None]  # shape(n,1,1,3)
            masks = masks.unsqueeze(3)  # shape(n,h,w,1)
            masks_color = masks * (colors * alpha)  # shape(n,h,w,3)

            inv_alph_masks = (1 - masks * alpha).cumprod(0)  # shape(n,h,w,1)
            mcs = (masks_color * inv_alph_masks).sum(0) * 2  # mask color summand shape(n,h,w,3)

            im_gpu = im_gpu.flip(dims=[0])  # flip channel
            im_gpu = im_gpu.permute(1, 2, 0).contiguous()  # shape(h,w,3)
            im_gpu = im_gpu * inv_alph_masks[-1] + mcs
            im_mask = (im_gpu * 255).byte().cpu().numpy()
            self.im[:] = scale_image(im_gpu.shape, im_mask, self.im.shape)
        if self.pil:
            # convert im back to PIL and update draw
            self.fromarray(self.im)

    def rectangle(self, xy, fill=None, outline=None, width=1):
        # Add rectangle to image (PIL-only)
        self.draw.rectangle(xy, fill, outline, width)

    def text(self, xy, text, txt_color=(255, 255, 255), anchor='top'):
        # Add text to image (PIL-only)
        if anchor == 'bottom':  # start y from font bottom
            w, h = self.font.getsize(text)  # text width, height
            xy[1] += 1 - h
        self.draw.text(xy, text, fill=txt_color, font=self.font)

    def fromarray(self, im):
        # Update self.im from a numpy array
        self.im = im if isinstance(im, Image.Image) else Image.fromarray(im)
        self.draw = ImageDraw.Draw(self.im)

    def result(self):
        # Return annotated image as array
        return np.asarray(self.im)



def draw_boxes(
    predictions: np.ndarray,
    input_shape: Tuple[int],
    image: np.ndarray,
    names: List[str],
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
        label = f"{names[int(cls)]} {conf:.2f}"
        annotator.box_label(xyxy, label, color=colors(int(cls), True))
    return image

def non_max_suppression(
        prediction,
        conf_thres=0.25,
        iou_thres=0.45,
        classes=None,
        agnostic=False,
        multi_label=False,
        labels=(),
        max_det=300,
        nm=0,  # number of masks
):
    """Non-Maximum Suppression (NMS) on inference results to reject overlapping detections

    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """

    if isinstance(prediction, (list, tuple)):  # YOLO model in validation model, output = (inference_out, loss_out)
        prediction = prediction[0]  # select only inference output

    device = prediction.device
    mps = 'mps' in device.type  # Apple MPS
    if mps:  # MPS not fully supported yet, convert tensors to CPU before NMS
        prediction = prediction.cpu()
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[1] - nm - 4  # number of classes
    mi = 4 + nc  # mask start index
    xc = prediction[:, 4:mi].amax(1) > conf_thres  # candidates

    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    max_wh = 7680  # (pixels) maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 2.5 + 0.05 * bs  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS

    t = time.time()
    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[:, 2:4] < min_wh) | (x[:, 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x.T[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 5), device=x.device)
            v[:, :4] = lb[:, 1:5]  # box
            v[range(len(lb)), lb[:, 0].long() + 4] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Detections matrix nx6 (xyxy, conf, cls)
        box, cls, mask = x.split((4, nc, nm), 1)
        box = xywh2xyxy(box)  # center_x, center_y, width, height) to (x1, y1, x2, y2)
        if multi_label:
            i, j = (cls > conf_thres).nonzero(as_tuple=False).T
            x = torch.cat((box[i], x[i, 4 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = cls.max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Apply finite constraint
        # if not torch.isfinite(x).all():
        #     x = x[torch.isfinite(x).all(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence
        else:
            x = x[x[:, 4].argsort(descending=True)]  # sort by confidence

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
            # update boxes as boxes(i,4) = weights(i,n) * boxes(n,4)
            iou = box_iou(boxes[i], boxes) > iou_thres  # iou matrix
            weights = iou * scores[None]  # box weights
            x[i, :4] = torch.mm(weights, x[:, :4]).float() / weights.sum(1, keepdim=True)  # merged boxes
            if redundant:
                i = i[iou.sum(1) > 1]  # require redundancy

        output[xi] = x[i]
        if mps:
            output[xi] = output[xi].to(device)
        if (time.time() - t) > time_limit:
            LOGGER.warning(f'WARNING ⚠️ NMS time limit {time_limit:.3f}s exceeded')
            break  # time limit exceeded

    return output


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)

def draw_chart(usages, history, width, height):
    """
    绘制实时CPU使用率图表
    :param usages: 当前CPU使用率列表
    :param history: 历史数据列表
    :param width: 图表区域的宽度
    :param height: 图表区域的高度
    :return: 带有图表的图像
    """
    POINT_SPACING=5
    margin = 10
    graph_width = width - margin * 2
    graph_height = height - margin * 2

    # 创建黑色画布用于绘制图表
    # img = np.zeros((height, width, 3), dtype=np.uint8)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img.fill(255)
    cv2.rectangle(img, (0, - margin * 2), (width, height), (169, 169, 169), -1)  # 灰色背景
    # 绘制坐标轴
    cv2.line(img, (margin, height - margin), (width - margin, height - margin), (255, 255, 255), 2)  # X轴
    cv2.line(img, (margin, margin), (margin, height - margin), (255, 255, 255), 2)  # Y轴

    # 绘制Y轴刻度
    for i in range(0, 101, 20):  # 0%到100%的刻度
        y = height - margin - int(i / 100 * graph_height)
        cv2.line(img, (margin - 5, y), (margin, y), (255, 255, 255), 1)
        cv2.putText(img, f"{i}%", (10, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    # 更新历史数据
    history.append(usages)
    # print(history)
    if len(history) > graph_width // POINT_SPACING:
        history.pop(0)  # 移除旧数据，保证图宽度不超过画布

    # 绘制折线图
    colors = [
        (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0),
        (0, 255, 255), (255, 0, 255), (200, 100, 50), (50, 100, 200)
    ]  # 为每个核心分配不同颜色
    for core in range(len(usages)):
        for x in range(1, len(history)):
            # print('draw line')
            prev_x = margin + (x - 1) * POINT_SPACING
            curr_x = margin + x * POINT_SPACING
            prev_y = height - margin - int(history[x - 1][core] / 100 * graph_height)
            curr_y = height - margin - int(history[x][core] / 100 * graph_height)
            cv2.line(img, (prev_x, prev_y), (curr_x, curr_y), colors[core % len(colors)], 1)

        # 显示核心标记
        cv2.putText(img, f"Core {core + 1}: {usages[core]:.1f}%", 
                    (width - margin - 150, margin + core * 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[core % len(colors)], 1)

    return img

def draw_progress_bar(image, value, position, size, bar_color=(0, 255, 0), bg_color=(50, 50, 50), thickness=1):
    """
    Draw a progress bar on an image.

    :param image: The image on which to draw the progress bar.
    :param value: The progress value (0 to 100).
    :param position: (x, y) tuple for the top-left corner of the bar.
    :param size: (width, height) tuple for the size of the bar.
    :param bar_color: Color of the progress bar in BGR format.
    :param bg_color: Background color of the bar in BGR format.
    :param thickness: Thickness of the bar border.
    """
    x, y = position
    width, height = size

    # Draw the background rectangle
    cv2.rectangle(image, (x, y), (x + width, y + height), bg_color, -1)

    # Calculate the width of the filled part
    fill_width = int((value / 100) * width)

    # Draw the filled rectangle
    cv2.rectangle(image, (x, y), (x + fill_width, y + height), bar_color, -1)

    # Draw the border rectangle
    cv2.rectangle(image, (x, y), (x + width, y + height), (255, 255, 255), thickness)

def quest_device_usage():
    global thread_runing_flag
    mem_use_c=c_uint()
    global cpu_use,cpu_num,mem_use
    while thread_runing_flag:
        if show_device['CPU']:
            cpu_read_ok = dll.GetCPUUsage(cpu_use,cpu_num)
            device_usage['CPU']=list(cpu_use[:cpu_num])
            # device_usage['CPU']=[value / 100 for value in cpu_use_] 
            # print("device_usage['CPU']: "+str(device_usage['CPU']))
        if show_device['Memory']:
            mem_read_ok = dll.GetMemoryUsage(ctypes.byref(mem_use_c))
            # mem_use=mem_use_c
            device_usage['Memory']['use_mem']=mem_use_c.value/1000#/100
            device_usage['Memory']['use_per']=device_usage['Memory']['use_mem']/device_usage['Memory']['tot_mem']
            # print("device_usage['Memory']: "+str(device_usage['Memory']))
        threading.Event().wait(0.1)  # 定时 1 秒

def display_multi_cpu_usage_on_image(image, device_usage, display_cont, start_x=150, start_y=300, bar_width=200, bar_height=20, spacing=35):
    
    # 創建透明區域的圖層
    overlay = image.copy()
    word_width = 80
    rect_x1 = start_x - 10
    rect_y1 = start_y - 10
    rect_x2 = start_x + bar_width + word_width + 10
    rect_y2 = start_y + spacing
    # rect_y2 = start_y + spacing * len(device_usage) #for multi device
    
    # 繪製半透明背景色塊
    cv2.rectangle(overlay, (rect_x1, rect_y1), (rect_x2, rect_y2), (50, 50, 50), -1)
    opacity = 0.7
    image = cv2.addWeighted(overlay, opacity, image, 1 - opacity, 0)
    
    # 繪製進度條和文字
    for i, (device, usage) in enumerate(device_usage.items()):
        if device == "CPU": #and not display_cont['CPU']:
            continue  # 跳過 CPU 的顯示
        if device == "Memory" and not display_cont['Memory']:
            continue  # 跳過 Memory 的顯示
        # 計算進度條座標
        bar_x1 = start_x + word_width
        bar_y1 = start_y
        # bar_y1 = start_y + i * spacing
        bar_x2 = int(bar_x1 + bar_width * usage['use_per'])
        bar_y2 = bar_y1+ bar_height
        # bar_y2 = bar_y1 + bar_height #for multi device
        
        # 繪製進度條背景
        cv2.rectangle(image, (bar_x1, bar_y1), (bar_x1 + bar_width, bar_y2), (100, 100, 100), -1)
        
        # 繪製進度條填充部分
        cv2.rectangle(image, (bar_x1, bar_y1), (bar_x2, bar_y2), (255, 105, 180), -1)
        
        # 顯示硬體類別
        cv2.putText(image, f"{device}", (start_x + 5, bar_y1 + bar_height - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        # 顯示使用率
        cv2.putText(image, "{use_mem:.1f}/{tot_mem:.1f} GB".format(**usage), (bar_x1 + 5, bar_y1 + bar_height - 5), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        # cv2.putText(image, f"{device}", (bar_x1 - 70, bar_y1 + bar_height - 5), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA) #for multi device
    
    return image

class VideoPlayer:
    """
    Custom video player to fulfill FPS requirements. You can set target FPS and output size,
    flip the video horizontally or skip first N frames.

    :param source: Video source. It could be either camera device or video file.
    :param size: Output frame size.
    :param flip: Flip source horizontally.
    :param fps: Target FPS.
    :param skip_first_frames: Skip first N frames.
    """

    def __init__(self, source, size=None, flip=False, fps=None, skip_first_frames=0):
        import cv2

        self.cv2 = cv2  # This is done to access the package in class methods
        self.__cap = cv2.VideoCapture(source)
        if not self.__cap.isOpened():
            raise RuntimeError(f"Cannot open {'camera' if isinstance(source, int) else ''} {source}")
        # skip first N frames
        self.__cap.set(cv2.CAP_PROP_POS_FRAMES, skip_first_frames)
        # fps of input file
        self.__input_fps = self.__cap.get(cv2.CAP_PROP_FPS)
        if self.__input_fps <= 0:
            self.__input_fps = 60
        # target fps given by user
        self.__output_fps = fps if fps is not None else self.__input_fps
        self.__flip = flip
        self.__size = None
        self.__interpolation = None
        if size is not None:
            self.__size = size
            # AREA better for shrinking, LINEAR better for enlarging
            self.__interpolation = cv2.INTER_AREA if size[0] < self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH) else cv2.INTER_LINEAR
        # first frame
        _, self.__frame = self.__cap.read()
        self.__lock = threading.Lock()
        self.__thread = None
        self.__stop = False

    """
    Start playing.
    """

    def start(self):
        self.__stop = False
        self.__thread = threading.Thread(target=self.__run, daemon=True)
        self.__thread.start()

    """
    Stop playing and release resources.
    """

    def stop(self):
        self.__stop = True
        if self.__thread is not None:
            self.__thread.join()
        self.__cap.release()

    def __run(self):
        prev_time = 0
        while not self.__stop:
            t1 = time.time()
            ret, frame = self.__cap.read()
            if not ret:
                break

            # fulfill target fps
            if 1 / self.__output_fps < time.time() - prev_time:
                prev_time = time.time()
                # replace by current frame
                with self.__lock:
                    self.__frame = frame

            t2 = time.time()
            # time to wait [s] to fulfill input fps
            wait_time = 1 / self.__input_fps - (t2 - t1)
            # wait until
            time.sleep(max(0, wait_time))

        self.__frame = None

    """
    Get current frame.
    """

    def next(self):
        import cv2

        with self.__lock:
            if self.__frame is None:
                return None
            # need to copy frame, because can be cached and reused if fps is low
            frame = self.__frame.copy()
        if self.__size is not None:
            frame = self.cv2.resize(frame, self.__size, interpolation=self.__interpolation)
        if self.__flip:
            frame = self.cv2.flip(frame, 1)
        return frame
    
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

# Main processing function to run object detection.
def run_object_detection(
    source=0,
    flip=False,
    use_popup=False,
    skip_first_frames=0,
    model="",
    device="",
    monitor=False,

):
    player = None
    now_dir=os.getcwd()
    # print(now_dir)
    global thread_runing_flag,cpu_use,cpu_num,mem_use,dll
    thread_runing_flag=True
    dll = ctypes.CDLL(now_dir+'\AaeonHWUsage.dll')
    C_Integers = c_int * 256
    # C_Integers1 = c_int
    cpu_use=C_Integers()
    cpu_num=dll.GetCoreCount()
    # mem_use=c_int(100)
    # mem_use=ctypes.c_int32

    compiled_model = core.compile_model(model, device)
    global show_device,device_usage
    tot_mem=c_uint()
    _ = dll.GetTotMemory(ctypes.byref(tot_mem))
    tot_mem=tot_mem.value/1000
    show_device = {
    "CPU": True,
    "Memory": True,
    }
    device_usage = {
    "CPU": [0.0]*cpu_num,
    "Memory": {'use_per':0.1,'tot_mem':tot_mem,'use_mem':1000},
    }
    history = []
    try:
        # Create a video player to play with target fps.
        player = VideoPlayer(source=source, flip=flip, fps=30, skip_first_frames=skip_first_frames)
        # Start capturing.
        player.start()
        if use_popup:
            title = "Press ESC to Exit"
            cv2.namedWindow(winname=title, flags=cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_AUTOSIZE)

        processing_times = collections.deque()
        usage_quest = threading.Thread(target=quest_device_usage, daemon=True)
        usage_quest.start()
        while True:
            # Grab the frame.
            frame = player.next()
            if frame is None:
                print("Source ended")
                break
            # If the frame is larger than full HD, reduce size to improve the performance.
            scale = 1280 / max(frame.shape)
            if scale < 1:
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
            # model expects RGB image, while video capturing in BGR
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
            frame1=cv2.putText(
                img=frame,
                text=f"Inference time: {processing_time:.1f}ms ({fps:.1f} FPS)",
                org=(int(f_width/3), 40),
                fontFace=cv2.FONT_HERSHEY_COMPLEX,
                fontScale=f_width / 1000,
                color=(0, 0, 255),
                thickness=3,
                lineType=cv2.LINE_AA,
            )
            if show_device['Memory']:
                frame1=display_multi_cpu_usage_on_image(
                    frame1,  # Replace with your input image path
                    device_usage,
                    show_device
                    )
            if show_device['CPU']:
                chart_height = frame1.shape[0] // 3  # 图片高度的三分之一
                chart = draw_chart(device_usage['CPU'], history, frame1.shape[1] - 20, chart_height)
                # 创建叠加图片，将图表放置在图片底部
                # overlay_image = frame1.copy()
                frame1[-chart_height:, 10:-10] = chart  # 将图表放置在底部
            # Use this workaround if there is flickering.
            if use_popup:
                #cv2.imshow(winname=title, mat=frame)
                cv2.imshow(title, frame1)
                key = cv2.waitKey(1)
                # escape = 27
                if key == 27:
                    break
                elif key == ord('a') and monitor:  # 按下 'A' 切換 surprise 的顯示
                    all_show=True
                    for device, device_stat in show_device.items():
                        if show_device[device]==False:
                            all_show=False
                            break
                    if all_show:    #全開就全關閉
                        for device, device_stat in show_device.items():
                            show_device[device]=False
                            history=[]
                    else:           #如果沒全開就先全開
                        for device, device_stat in show_device.items():
                            show_device[device]=True
                elif key == ord('c') and monitor:  # 按下 'A' 切換 surprise 的顯示
                    show_device['CPU'] = not show_device['CPU']
                    if show_device['CPU']==False:
                        history=[]
                elif key == ord('m') and monitor:  # 按下 'A' 切換 surprise 的顯示
                    show_device['Memory'] = not show_device['Memory']
            else:
                # Encode numpy array to jpg.
                _, encoded_img = cv2.imencode(ext=".jpg", img=frame, params=[cv2.IMWRITE_JPEG_QUALITY, 100])
                # Create an IPython image.⬆️
                i = display.Image(data=encoded_img)
                # Display the image in this notebook.
                display.clear_output(wait=True)
                display.display(i)
    # ctrl-c
    except KeyboardInterrupt:
        print("Interrupted")
    # any different error
    except RuntimeError as e:
        print(e)
    finally:
        if player is not None:
            # Stop capturing.
            player.stop()
        if use_popup:
            cv2.destroyAllWindows()
        thread_runing_flag=False


def main(argv):
    
    # model_file=Path("model")/ "yolo11n.xml"
    model_file=argv.model
    print(model_file)
    quantized_model = core.read_model(model_file)
    weights = model_file
    # metadata = yaml_load(Path("model")/ "metadata.yaml")
    metadata=model_file.split('\\')[:-1]
    metadata='\\'.join(metadata)
    print(metadata)
    metadata = yaml_load(metadata+'\\'+'metadata.yaml')
    global NAMES
    NAMES = metadata["names"]

    if len(args.input)<2:
        input_source=int(args.input)
        print("open camera "+str(input_source))
    else:
        input_source=args.input
        print("open video")
    VIDEO_SOURCE=input_source
    # if(len(argv)<2):
    #     VIDEO_SOURCE="https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4"
    # else:
    #     if(argv[1].isdigit()):
    #         VIDEO_SOURCE = int(argv[1])


    # os.system("cls")
    
    # while(1):
    #     print("Select you wanted running device:")
    #     detect=core.available_devices
    #     index=1
    #     device_dict={}
    #     for i in detect:
    #         print(str(index)+"."+str(i))
    #         device_dict[str(index)]=str(i)
    #         index+=1
    #     print(str(index)+"."+"AUTO")
    #     device_dict[str(index)]="AUTO"
    
    #     sel_dev=input()
    #     if(int(sel_dev)>0 and int(sel_dev) <= index):
    #         print("select " +device_dict[str(sel_dev)]+ " to running" )
    #         break
    #     else:
    #         os.system("cls")
    #         print("Not invild input!!!!!!!!!!!!!!!!!")
        
    run_object_detection(
        source=VIDEO_SOURCE,
        flip=True,
        use_popup=True,
        model=quantized_model,
        device=argv.device,
        monitor=args.hardware_moinitor
        )


if __name__ == "__main__":
    args = initialize_arg_parser().parse_args()
    main(args)
