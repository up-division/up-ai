@echo off
set current_dir=%~dp0%
call %current_dir%\..\..\..\inst\win\set_env.bat

if  not defined root_dir (
    echo  Please call set_env.bat to set the environment variables
    pause
    exit
)

if exist "%root_dir%\build\ov-obj_det" (
    echo The Demo env already exists. Do you want to delete it?
    choice /c yn /m "Please choose (y/n):"
    if errorlevel 2 (
        exit
    ) else (
        rmdir /S /Q %root_dir%\build\ov-obj_det
    )
)

echo ========================================
echo Install openvino objecet detect packages
echo ========================================

py -3.10 -m venv %root_dir%/build/ov-obj_det
call %root_dir%/build/ov-obj_det/Scripts/activate.bat

pip install psutil
pip install -r  %current_dir%\requirements.txt

echo ===============================================
echo Openvino Objecet Detect Installation Completed!
echo ===============================================

echo "Check openvino objecet detect run data now!"

if not exist "%root_dir%\videos\" (
    mkdir %root_dir%\videos\
)

if exist "%root_dir%\videos\obj_video.mp4" (
    echo Openvino objecet detect demo video exist.
) else (
    echo Download demo video now.
    curl https://storage.openvinotoolkit.org/repositories/openvino_notebooks/data/data/video/people.mp4 -o %root_dir%\videos\obj_video.mp4
)
echo "Download openvino objecet detect data Completed!"
pause
exit