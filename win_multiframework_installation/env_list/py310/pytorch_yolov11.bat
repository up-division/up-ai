@echo off
echo =====================================
echo         Install Yolov11 demo
echo =====================================
py -m venv %currentDir%/env/torch_yolov11
call %currentDir%/env/torch_yolov11/Scripts/activate.bat
pip install ultralytics
pip install argparse
@REM git clone https://github.com/ultralytics/ultralytics.git 
echo ===========================================
echo Yolov11 Environment Installation Completed!
echo ===========================================

echo "Check demo video now!"
if exist "%currentDir%\video\people.mp4" (
    echo Hailo demo video exist.
) else (
    echo Download demo video now.
    curl https://cdn.pixabay.com/video/2016/11/15/6398-191712356_small.mp4?download -o %currentDir%\video\people.mp4
)