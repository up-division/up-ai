@echo off
set "currentDir=%~dp0" 
set "hailodemoDir=%currentDir%\app\hailo\detection_with_tracker"
set "matched_instances=Intel;"
REM  List of Instance IDs that define Hailo and Nvidia classes
set "Hailo=2864"
set "Nvidia=24FA"

REM Temporary file used to store the output of pnputil
set "tempfile=%temp%\pnputil_output.txt"

setlocal enabledelayedexpansion
pnputil /enum-devices /connected > "%tempfile%"
set "com_instance_ids=Hailo;Nvidia"
REM Browse all categories
set "chatbot_matched_instances=!matched_instances!"
set "obj_matched_instances=!matched_instances!"
for %%I in (%com_instance_ids%) do (
    REM Dynamically expand variable values ​​for each category
    set "current_list=!%%I!"
    
    REM Iterate over each instance ID in a category
    for %%J in (!current_list!) do (
        REM Suppose the file tempfile.txt needs to match
        @REM set "device_instances=PCI\VEN_8086&DEV_%%J"
        findstr /c:"%%J" "%tempfile%" >nul
        if !errorlevel! equ 0 (
            REM If the match is successful, add the Instance ID to matched_instances
            set "obj_matched_instances=!obj_matched_instances!%%I;"
        )
    )
)

:main_menu
cls
echo ====================================
echo          Function Menu
echo ====================================
echo 1. Object Detection - video
echo 2. Object Detection - camera
echo 3. Chatbot
echo 0. exit
echo ====================================
set /p choice="Please input number: "

if "%choice%"=="1" goto obj_detect
if "%choice%"=="2" goto obj_detect1
if "%choice%"=="3" goto chatbot
if "%choice%"=="0" goto exit
echo unknow option,please rechoose!
pause
goto main_menu

:obj_detect
cls
set "counter=1"
echo ============================================
echo  Select Hardware (Object Detection - video)
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
REM Check if the input is a number
for /F "delims=0123456789" %%A in ("%hardware%") do (
    echo Invalid input. Please enter a number.
    goto :input
)
if %hardware% GTR !counter! (
    echo Invalid input.
    goto :input
) else if %hardware% LSS 0 (
    echo Invalid input.
    goto :input
)
if "%hardware%"=="0" (
    goto main_menu
)
REM map value
set "current_index=1"
for %%I in (%obj_matched_instances%) do (
    if !current_index! equ %hardware% (
        @REM echo The second value is: %%I
        set "demotype=%%I"
        goto :loop_end
    )
    set /a current_index+=1
)
:loop_end

@REM set "ov_demo_video=%currentDir%\..\videos\obj_video.mp4"
@REM set "hailo_demo_video=%currentDir%\..\videos\hailo_video.mp4"
@REM @REM set "pytorch_demo_video=%currentDir%\app\hailo\detection_with_tracker"
@REM echo ============================================
@REM echo  Select video source
@REM echo ============================================
@REM echo  1. Demo video
@REM echo  2. Custom video
@REM echo ============================================
@REM set /p v_source="Please input number: "
@REM REM 檢查輸入是否為數字
@REM for /F "delims=0123456789" %%A in ("%v_source%") do (
@REM     echo Invalid input. Please enter a number.
@REM     goto :input
@REM )
@REM if %v_source% GTR 2 (
@REM     echo Invalid input.
@REM     goto :input
@REM ) else if %v_source% LSS 0 (
@REM     echo Invalid input.
@REM     goto :input
@REM )
@REM if %v_source% == "1" (
@REM     echo Use demo video.
@REM     goto :Select_video_end
@REM ) else if %v_source% == "2" (
@REM     set /p input_string="Please enter video location: "
@REM     set "ov_demo_video=%input_string%"
@REM     set "hailo_demo_video=%input_string%"
@REM )

:Select_video_end
if "!demotype!"=="Intel" (
    if exist "%currentDir%/env/ov-obj_det/Scripts/activate.bat" (
        call %currentDir%/env/ov-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto obj_detect
    )
	echo Start Object Detect......
	cd  %~dp0\..\obj-detect
    @REM in run space, use 'python' comand
	python demo.py %currentDir%\..\videos\obj_video.mp4
    @REM python demo.py %ov_demo_video%
    cd %currentDir%
) else if "!demotype!"=="Hailo" (
    if exist "%currentDir%/env/hailo-obj_det/Scripts/activate.bat" (
        call %currentDir%/env/hailo-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto obj_detect
    )
	echo Start detection with tracker...
    @REM in run space, use 'python' comand
	python %hailodemoDir%\detection_with_tracker.py -n %currentDir%\..\models\yolov5m_wo_spp_60p.hef -i %currentDir%\..\videos\hailo_video.mp4 -l %hailodemoDir%\coco.txt
    @REM python %hailodemoDir%\detection_with_tracker.py -n %currentDir%\..\models\yolov5m_wo_spp_60p.hef -i %hailo_demo_video% -l %hailodemoDir%\coco.txt
) else if "!demotype!"=="Nvidia" (
    if exist "%currentDir%/env/torch_yolov11/Scripts/activate.bat" (
        call %currentDir%/env/torch_yolov11/Scripts/activate.bat
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto obj_detect
    )
    echo Start Yolov11 by pytorch!
    cd %currentDir%\app\pytorch
    @REM in run space, use 'python' comand
    python yolov11_predict.py %currentDir%\..\videos\obj_video.mp4
    @REM python yolov11_predict.py %ov_demo_video%
    cd %currentDir%

) else if "!demotype!"=="0" (
    goto main_menu
) else (
    echo unknow option,please rechoose!
    pause
    goto obj_detect
)
pause
goto obj_detect

:obj_detect1
cls
set "counter=1"
echo ============================================
echo  Select Hardware (Object Detection - camera)
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
REM Check if the input is a number
for /F "delims=0123456789" %%A in ("%hardware%") do (
    echo Invalid input. Please enter a number.
    goto :input
)
if %hardware% GTR !counter! (
    echo Invalid input.
    goto :input
) else if %hardware% LSS 0 (
    echo Invalid input.
    goto :input
)
if "%hardware%"=="0" (
    goto main_menu
)
REM map value
set "current_index=1"
for %%I in (%obj_matched_instances%) do (
    if !current_index! equ %hardware% (
        @REM echo The second value is: %%I
        set "demotype=%%I"
        goto :loop_end
    )
    set /a current_index+=1
)
:loop_end

if "!demotype!"=="Intel" (
    if exist "%currentDir%/env/ov-obj_det/Scripts/activate.bat" (
        call %currentDir%/env/ov-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto obj_detect1
    )
	echo Start Object Detect......
    cd  %~dp0\..\obj-detect
    @REM in run space, use 'python' comand
	python demo.py 0
    cd %currentDir%
) else if "!demotype!"=="Hailo" (
    if exist "%currentDir%/env/hailo-obj_det/Scripts/activate.bat" (
        call %currentDir%/env/hailo-obj_det/Scripts/activate.bat
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto obj_detect1
    )
	echo Start detection with tracker...
    @REM in run space, use 'python' comand
	python %hailodemoDir%/detection_with_tracker.py -n %currentDir%\..\models\yolov5m_wo_spp_60p.hef -l %hailodemoDir%\coco.txt

) else if "!demotype!"=="Nvidia" (
    if exist "%currentDir%/env/torch_yolov11/Scripts/activate.bat" (
        call %currentDir%/env/torch_yolov11/Scripts/activate.bat
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto obj_detect1
    )
    echo Start Yolov11 by pytorch!
    cd %currentDir%\app\pytorch
    @REM in run space, use 'python' comand
    python yolov11_predict.py 0
    cd %currentDir%

) else if "!demotype!"=="0" (
    goto main_menu
) else (
    echo unknow option,please rechoose!
    pause
    goto obj_detect1
)
pause
goto obj_detect1

:chatbot
cls
set "counter=1"
echo ====================================
echo       Select Hardware (Chatbot)
echo ====================================
if defined chatbot_matched_instances (
    for %%M in (!chatbot_matched_instances!) do (
        echo !counter!.%%M
        set /a counter+=1
    )
) else (
    echo No matching Instance IDs found.
)
echo 0. exit
echo ============================================
set /p hardware="Please input number: "
REM Check if the input is a number
for /F "delims=0123456789" %%A in ("%hardware%") do (
    echo Invalid input. Please enter a number.
    goto :input
)
if %hardware% GTR !counter! (
    echo Invalid input.
    goto :input
) else if %hardware% LSS 0 (
    echo Invalid input.
    goto :input
)
if "%hardware%"=="0" (
    goto main_menu
)
REM map value
set "current_index=1"
for %%I in (%chatbot_matched_instances%) do (
    if !current_index! equ %hardware% (
        @REM echo The second value is: %%I
        set "demotype=%%I"
        goto :loop_end
    )
    set /a current_index+=1
)
:loop_end

if "%demotype%"=="Intel" (
    if exist "%currentDir%/env/ov-chatbot/Scripts/activate.bat" (
        call %currentDir%/env/ov-chatbot/Scripts/activate.bat
        @REM echo Use Local Environment!!!
    ) else (
        echo This demo environment not install,please rechoose!
        pause
        goto chatbot
    )
	echo Start Chatbot......
	cd %~dp0\..\chatbot
    @REM in run space, use 'python' comand
	python chatbot.py
    cd %currentDir%
) else if "%hardware%"=="0" (
    goto main_menu
) else (
    echo unknow option,please rechoose!
    pause
    goto chatbot
)
pause
goto chatbot
