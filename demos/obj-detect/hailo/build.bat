@echo off

set current_dir=%~dp0%
call %current_dir%\..\..\..\inst\win\set_env.bat

if  not defined root_dir (
    echo  Please call set_env.bat to set the environment variables
    pause
    exit
)
setlocal enabledelayedexpansion
::Setting Multiple Devices' VID and PID
set "devices=1E60:2864"


::Check if a device is connected
for %%d in (%devices%) do (
    for /f "tokens=1,2 delims=:" %%i in ("%%d") do (
        set "VEN=%%i"
        set "DEV=%%j"
	for /f "tokens=*" %%k in ('wmic path Win32_PnPEntity get DeviceID ^| findstr /i "VEN_!VEN!&DEV_!DEV!"') do (
    		echo find device : "VEN_!VEN!&DEV_!DEV!"
    		goto start
	)
    )
)

endlocal

exit

:start
if exist "%root_dir%\build\hailo-obj_det" (
    echo The Demo env already exists. Do you want to delete it?
    choice /c yn /m "Please choose (y/n):"
    if errorlevel 2 (
        exit
    ) else (
        rmdir /S /Q %root_dir%\build\hailo-obj_det
    )
)
echo =====================================
echo Install hailo objecet detect packages
echo =====================================

py -3.10 -m venv %root_dir%/build/hailo-obj_det
call %root_dir%/build/hailo-obj_det/Scripts/activate.bat

pip install wheel
pip install psutil
pip install %current_dir%\py_pkg\netifaces-0.11.0-cp310-cp310-win_amd64.whl
pip install "%ProgramFiles%\HailoRT\python\hailort-4.19.0-cp310-cp310-win_amd64.whl"
pip install -r %current_dir%\requirements.txt
echo ========================================================
echo Hailo objecet detect Environment Installation Completed!
echo ========================================================

echo "Check Hailo detect data now!"
if not exist "%root_dir%\videos\" (
    mkdir %root_dir%\videos\
)
if not exist "%root_dir%\models\" (
    mkdir %root_dir%\models\
)

if exist "%root_dir%\videos\hailo_video.mp4" (
    echo Hailo demo video exist.
) else (
    echo Download demo video now.
    curl https://cdn.pixabay.com/video/2016/11/15/6398-191712356_small.mp4?download -o %root_dir%\videos\hailo_video.mp4
)
if exist "%root_dir%\models\yolov5m_wo_spp_60p.hef" (
    echo Hailo inference weight exist.
) else (
    echo Download inference weight now.
    curl https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v2.11.0/hailo8/yolov5m_wo_spp_60p.hef -o %root_dir%\models\yolov5m_wo_spp_60p.hef
)
echo "Download Hailo detect data Completed!"
pause
exit