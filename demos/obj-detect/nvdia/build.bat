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
set "devices=10de:24fa"


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
if exist "%root_dir%\build\torch_yolov11" (
    echo The Demo env already exists. Do you want to delete it?
    choice /c yn /m "Please choose (y/n):"
    if errorlevel 2 (
        exit
    ) else (
        rmdir /S /Q %root_dir%\build\torch_yolov11

    )
)

echo =====================================
echo         Install Yolov11 demo
echo =====================================

py -3.10 -m venv %root_dir%/build/torch_yolov11
call %root_dir%/build/torch_yolov11/Scripts/activate.bat

python.exe -m pip install --upgrade pip
pip install -r %current_dir%requirement.txt
pip install --upgrade -r %current_dir%requirement_cuda.txt
@REM git clone https://github.com/ultralytics/ultralytics.git 

echo ===========================================
echo Yolov11 Environment Installation Completed!
echo ===========================================

echo "Check demo video now!"
if not exist "%root_dir%\videos\" (
    mkdir %root_dir%\videos\
)

if exist "%root_dir%\videos\obj_video.mp4" (
    echo nvdia demo video exist.
) else (
    echo Download demo video now.
    curl https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4 -o %root_dir%\videos\obj_video.mp4
)
pause
exit