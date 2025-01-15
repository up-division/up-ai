@echo off
set "currentDir=%~dp0" 
set "hailodemoDir=%currentDir%\app\hailo\detection_with_tracker"
set "matched_instances=Intel;"
REM 定義 Hailo 和 Nvidia 類的 Instance ID 列表
set "Hailo=2864"
set "Nvidia=24FA"

REM 臨時文件用於存儲 pnputil 的輸出
set "tempfile=%temp%\pnputil_output.txt"

setlocal enabledelayedexpansion
pnputil /enum-devices /connected > "%tempfile%"
set "com_instance_ids=Hailo;Nvidia"
REM 遍歷所有類別
set "chatbot_matched_instances=!matched_instances!"
set "obj_matched_instances=!matched_instances!"
for %%I in (%com_instance_ids%) do (
    REM 動態展開每個類別的變數值
    set "current_list=!%%I!"
    
    REM 遍歷該類別中的每個 Instance ID
    for %%J in (!current_list!) do (
        REM 假設文件 tempfile.txt 中需要匹配
        @REM set "device_instances=PCI\VEN_8086&DEV_%%J"
        findstr /c:"%%J" "%tempfile%" >nul
        if !errorlevel! equ 0 (
            REM 如果匹配成功，將該 Instance ID 添加到 matched_instances
            set "obj_matched_instances=!obj_matched_instances!%%I;"
        )
    )
)

:main_menu
cls
echo ====================================
echo          Function Menu
echo ====================================
echo 1. Object Detection - vedio
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
echo  Select Hardware (Object Detection - vedio)
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
REM 檢查輸入是否為數字
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
REM 映射數值
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
        goto obj_detect
    )
	echo Start Object Detect......
	cd  %~dp0\..\obj-detect
    @REM in run space, use 'python' comand
	python demo.py %currentDir%\..\videos\obj_video.mp4
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
REM 檢查輸入是否為數字
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
REM 映射數值
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
REM 檢查輸入是否為數字
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
REM 映射數值
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
