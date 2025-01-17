import cv2
import numpy as np
# 定义文本和参数
text = "Hello, OpenCV123123123!"
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1.0
thickness = 2

# 使用 cv2.getTextSize 计算文本大小
text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
text_width, text_height = text_size  # 文本宽度和高度

# 打印计算结果
print(f"Text width: {text_width} pixels")
print(f"Text height: {text_height} pixels")
print(f"Baseline: {baseline} pixels")

# 创建空白图像并绘制文本
img = 255 * np.ones((text_height + 20, text_width + 20, 3), dtype=np.uint8)
cv2.putText(img, text, (10, text_height + 10), font, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)

# 显示图像
cv2.imshow("Text Size Example", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
