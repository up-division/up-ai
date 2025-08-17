import cv2
from cv2_enumerate_cameras import enumerate_cameras

#reference https://pypi.org/project/cv2-enumerate-cameras/

for camera_info in enumerate_cameras(cv2.CAP_MSMF):
    print(f'{camera_info.index}: {camera_info.name}\n')
