@echo off
echo =====================================
echo Install hailo objecet detect packages
echo =====================================
py -3.10 -m venv %currentDir%/env/hailo-obj_det
call %currentDir%/env/hailo-obj_det/Scripts/activate.bat
pip install wheel
pip install psutil
pip install %currentDir%\app\hailo\py_pkg\netifaces-0.11.0-cp310-cp310-win_amd64.whl
pip install "%ProgramFiles%\HailoRT\python\hailort-4.19.0-cp310-cp310-win_amd64.whl"
pip install -r %currentDir%\app\hailo\detection_with_tracker\requirements.txt
echo ========================================================
echo Hailo objecet detect Environment Installation Completed!
echo ========================================================

echo "Check Hailo detect data now!"
if exist "%currentDir%\videos\hailo_video.mp4" (
    echo Hailo demo video exist.
) else (
    echo Download demo video now.
    curl https://cdn.pixabay.com/video/2016/11/15/6398-191712356_small.mp4?download -o %currentDir%\..\videos\hailo_video.mp4
)
if exist "%currentDir%\..\models\yolov5m_wo_spp_60p.hef" (
    echo Hailo inference weight exist.
) else (
    echo Download inference weight now.
    curl https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v2.11.0/hailo8/yolov5m_wo_spp_60p.hef -o %currentDir%\..\models\yolov5m_wo_spp_60p.hef
)
echo "Download Hailo detect data Completed!"