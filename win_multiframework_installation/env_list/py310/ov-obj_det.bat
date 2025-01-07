@echo off
echo ========================================
echo Install openvino objecet detect packages
echo ========================================
py -m venv %currentDir%/env/ov-obj_det
call %currentDir%/env/ov-obj_det/Scripts/activate.bat
pip install -r %currentDir%\app/openvino\obj-detect\requirements.txt
echo ===============================================
echo Openvino Objecet Detect Installation Completed!
echo ===============================================

echo "Check openvino objecet detect run data now!"
@REM if exist "%video_path%" (
@REM     echo Hailo demo video exist.
@REM     echo Hailo model video exist.
@REM )
@REM else (
@REM )
echo "Download openvino objecet detect data Completed!"