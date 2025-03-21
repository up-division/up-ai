@echo off
setlocal enabledelayedexpansion
set current_dir=%~dp0%
call %current_dir%\..\..\inst\win\set_env.bat

if not defined root_dir (
    echo Please call set_env.bat to set the environment variables
    pause
    exit
)

set "hailodemoDir=%currentDir%\app\hailo\detection_with_tracker"
set "matched_instances=Intel;"
set "Hailo=2864"
set "Nvidia=24FA"
set "tempfile=%temp%\pnputil_output.txt"

pnputil /enum-devices /connected > "%tempfile%"
set "com_instance_ids=Hailo;Nvidia"
set "chatbot_matched_instances=!matched_instances!"
set "obj_matched_instances=!matched_instances!"

for %%I in (%com_instance_ids%) do (
    set "current_list=!%%I!"
    for %%J in (!current_list!) do (
        findstr /c:"%%J" "%tempfile%" >nul
        if !errorlevel! equ 0 (
            set "obj_matched_instances=!obj_matched_instances!%%I;"
        )
    )
)

if "%1"=="1" goto obj_detect
if "%1"=="2" goto obj_detect1

:obj_detect
cls
set "counter=1"
echo ============================================
echo Select Hardware (Object Detection - video)
echo ============================================
if defined obj_matched_instances (
    for %%M in (!obj_matched_instances!) do (
        echo !counter!.%%M
        set /a counter+=1
    )
) else (
    echo No matching Instance IDs found.
)
echo 0. exit
echo ============================================
set /p hardware="Please input number: "

for /F "delims=0123456789" %%A in ("%hardware%") do (
    echo Invalid input. Please enter a number.
    goto :obj_detect
)
if %hardware% GTR !counter! (
    echo Invalid input.
    goto :obj_detect
) else if %hardware% LSS 0 (
    echo Invalid input.
    goto :obj_detect
)
if "%hardware%"=="0" (
    exit
)
set "current_index=1"
for %%I in (!obj_matched_instances!) do (
    if !current_index! equ %hardware% (
        set "demotype=%%I"
        goto :Select_video_end
    )
    set /a current_index+=1
)

:Select_video_end
if "!demotype!"=="Intel" (
    if exist "%root_dir%/build/ov-obj_det/Scripts/activate.bat" (
        call %root_dir%/build/ov-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install, please rechoose!
        pause
        goto obj_detect
    )
    echo Start Object Detect......
    python %current_dir%\intel\demo.py %root_dir%\videos\obj_video.mp4
) else if "!demotype!"=="Hailo" (
    if exist "%root_dir%/build/hailo-obj_det/Scripts/activate.bat" (
        call %root_dir%/build/hailo-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install, please rechoose!
        pause
        goto obj_detect
    )
    echo Start detection with tracker...
    python %current_dir%\hailo\detection_with_tracker.py -n %root_dir%\models\yolov5m_wo_spp_60p.hef -i %root_dir%\videos\hailo_video.mp4 -l %current_dir%\hailo\coco.txt
) else if "!demotype!"=="Nvidia" (
    if exist "%root_dir%/build/torch_yolov11/Scripts/activate.bat" (
        call %root_dir%/build/torch_yolov11/Scripts/activate.bat
    ) else (
        echo This demo environment not install, please rechoose!
        pause
        goto obj_detect
    )
    echo Start Yolov11 by pytorch!
    python %current_dir%\nvdia\yolov11_predict.py %root_dir%\videos\obj_video.mp4
) else (
    echo Unknown option, please rechoose!
    pause
    goto obj_detect
)
exit

:obj_detect1
set "counter=1"
echo ============================================
echo Select Hardware (Object Detection - camera)
echo ============================================
if defined obj_matched_instances (
    for %%M in (!obj_matched_instances!) do (
        echo !counter!.%%M
        set /a counter+=1
    )
) else (
    echo No matching Instance IDs found.
)
echo 0. exit
echo ============================================
set /p hardware="Please input number: "
for /F "delims=0123456789" %%A in ("%hardware%") do (
    echo Invalid input. Please enter a number.
    goto :obj_detect1
)
if %hardware% GTR !counter! (
    echo Invalid input.
    goto :obj_detect1
) else if %hardware% LSS 0 (
    echo Invalid input.
    goto :obj_detect1
)
if "%hardware%"=="0" (
    exit
)
set "current_index=1"
for %%I in (!obj_matched_instances!) do (
    if !current_index! equ %hardware% (
        set "demotype=%%I"
        goto :loop_end
    )
    set /a current_index+=1
)
:loop_end

if "!demotype!"=="Intel" (
    if exist "%root_dir%/build/ov-obj_det/Scripts/activate.bat" (
        call %root_dir%/build/ov-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install, please rechoose!
        pause
        goto obj_detect1
    )
    echo Start Object Detect......
    python %current_dir%/intel/demo.py 0
) else if "!demotype!"=="Hailo" (
    if exist "%root_dir%/build/hailo-obj_det/Scripts/activate.bat" (
        call %root_dir%/build/hailo-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install, please rechoose!
        pause
        goto obj_detect1
    )
    echo Start detection with tracker...
    python %current_dir%\hailo\detection_with_tracker.py -n %root_dir%\models\yolov5m_wo_spp_60p.hef -l %current_dir%\hailo\coco.txt
) else if "!demotype!"=="Nvidia" (
    if exist "%root_dir%/build/torch_yolov11/Scripts/activate.bat" (
        call %root_dir%/build/torch_yolov11/Scripts/activate.bat
    ) else (
        echo This demo environment not install, please rechoose!
        pause
        goto obj_detect1
    )
    echo Start Yolov11 by pytorch!
    python  %current_dir%\nvdia\yolov11_predict.py 0
) else (
    echo Unknown option, please rechoose!
    pause
    goto obj_detect1
)

exit