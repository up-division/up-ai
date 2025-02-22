@echo off
echo ========================================
echo Install openvino objecet detect packages
echo ========================================
py -3.10 -m venv %currentDir%/env/ov-obj_det
call %currentDir%/env/ov-obj_det/Scripts/activate.bat
pip install psutil
pip install -r %currentDir%\..\obj-detect\requirements.txt
echo ===============================================
echo Openvino Objecet Detect Installation Completed!
echo ===============================================

echo "Check openvino objecet detect run data now!"
if exist "%currentDir%\..\videos\obj_video.mp4" (
    echo Openvino objecet detect demo video exist.
) else (
    echo Download demo video now.
    curl https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4 -o %currentDir%\..\videos\obj_video.mp4
)
echo "Download openvino objecet detect data Completed!"