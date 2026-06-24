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
set "HAILO_DEVICE="

::Check if a device is connected
for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Get-PnpDevice | Where-Object {$_.DeviceID -like '*VEN_1E60&DEV_45C4*'} | Select-Object -ExpandProperty DeviceID" 2^>nul') do (
    set "HAILO_DEVICE=HAILO_10"
)

if not "%HAILO_DEVICE%"=="HAILO_10" (
    for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Get-PnpDevice | Where-Object {$_.DeviceID -like '*VEN_1E60&DEV_2864*'} | Select-Object -ExpandProperty DeviceID" 2^>nul') do (
        set "HAILO_DEVICE=HAILO_8"
    )
)

if "%HAILO_DEVICE%"=="HAILO_10" (
    echo [INFO] Find device: Hailo 10
    goto hailo10_start
) else (
    echo [INFO] Find device: Hailo 8
    goto hailo8_start
)

:hailo10_start
if exist "%root_dir%\build\hailo_10h-obj_det" (
    echo The Demo env already exists. Do you want to delete it?
    choice /c yn /m "Please choose (y/n):"
    if errorlevel 2 (
        exit
    ) else (
        rmdir /S /Q %root_dir%\build\hailo_10h-obj_det
    )
)

echo ========================================
echo Install hailo 10h objecet detect packages
echo ========================================
py -3.10 -m venv %root_dir%/build/hailo_10h-obj_det
call %root_dir%/build/hailo_10h-obj_det/Scripts/activate.bat
pip install "C:\Program Files\HailoRT\python\hailort-5.3.2-cp310-cp310-win_amd64.whl"
git clone https://github.com/hailo-ai/hailo-apps.git "%root_dir%\demos\obj-detect\hailo\hailo_10h"
python %current_dir%\patch_toolbox.py
winget install --id Microsoft.VisualStudio.2022.BuildTools ^
--override "--quiet --wait --norestart --nocache ^
--add Microsoft.VisualStudio.Workload.VCTools ^
--add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
--add Microsoft.VisualStudio.Component.Windows10SDK.19041" ^
--accept-source-agreements ^
--accept-package-agreements
start /wait "" "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe" modify --installPath "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools" --add Microsoft.VisualStudio.Component.VC.140 --add Microsoft.VisualStudio.Component.Windows10SDK.19041 --passive --norestart
cd %root_dir%\demos\obj-detect\hailo\hailo_10h\hailo_apps\python\standalone_apps\object_detection
pip install -r %current_dir%\hailo_10h\hailo_apps\python\standalone_apps\object_detection\requirements.txt
echo ========================================================
echo Hailo 10h objecet detect Environment Installation Completed!
echo ========================================================

echo "Check Hailo 10h detect data now!"
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
    curl https://hailo-model-zoo.s3.eu-west-2.amazonaws.com/ModelZoo/Compiled/v5.3.0/hailo10h/yolov5m_wo_spp.hef -o %root_dir%\models\yolov5m_wo_spp.hef
)
echo "Download Hailo 10h detect data Completed!"
pause
exit

:hailo8_start
if exist "%root_dir%\build\hailo_8-obj_det" (
    echo The Demo env already exists. Do you want to delete it?
    choice /c yn /m "Please choose (y/n):"
    if errorlevel 2 (
        exit
    ) else (
        rmdir /S /Q %root_dir%\build\hailo_8-obj_det
    )
)
echo =====================================
echo Install hailo 8 objecet detect packages
echo =====================================

py -3.10 -m venv %root_dir%/build/hailo_8-obj_det
call %root_dir%/build/hailo_8-obj_det/Scripts/activate.bat

pip install wheel
pip install psutil
pip install %current_dir%\hailo_8\py_pkg\netifaces-0.11.0-cp310-cp310-win_amd64.whl
pip install "%ProgramFiles%\HailoRT\python\hailort-4.23.0-cp310-cp310-win_amd64.whl"
pip install -r %current_dir%\hailo_8\requirements.txt
echo ========================================================
echo Hailo 8 objecet detect Environment Installation Completed!
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
echo "Download Hailo 8 detect data Completed!"
pause
exit