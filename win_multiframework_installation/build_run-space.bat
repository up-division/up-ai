@echo off
set "currentDir=%~dp0" 
cd %currentDir%
@REM git clone https://github.com/up-division/up-ai.git %currentDir%\up-ai
set pip_web=pypi.org
setlocal enabledelayedexpansion
:chk_net
cd .
ping -n 1 %pip_web% >nul 2>&1
if errorlevel 1 (
    echo Connect network fail...
    echo Please connect to the Internet and click any button to continue.
    pause
    goto chk_net
    
) else (
    echo Connect successfully!
)
endlocal

echo "Upgrade pip......"
python -m pip install --upgrade pip

if not exist "%currentDir%\..\videos" (
    echo Make video folder
    mkdir %currentDir%\..\videos
)

if not exist "%currentDir%\..\models" (
    echo Make model folder
    mkdir %currentDir%\..\models
)

:main_menu
REM First level choice - item detection or chatbot
cls
echo =========================================
echo                Install Menu
echo =========================================
echo 1. Install Environment and Inefrence Data
echo 2. Auto install all 
echo 0. exit
echo =========================================
set /p funct="Please input number: "

if "%funct%"=="1" goto install_env
if "%funct%"=="2" goto auto
if "%funct%"=="0" goto exit
echo unknow option,please rechoose!
pause
goto main_menu

:install_env
REM Second level selection - select hardware
cls
echo ============================================
echo       Select Environment Installation
echo ============================================
echo 1. Object Detection
echo 2. Chatbot
echo 0. Return to the menu
echo ============================================
set /p app="Please input number: "
if "%app%"=="1" (
    @REM call %currentDir%\env_list\py310\ov-obj_det.bat
    @REM call %currentDir%\env_list\py310\hailo-obj_det.bat
    @REM call %currentDir%\env_list\py310\pytorch_yolov11.bat
    python %currentDir%\app\scanf_driver.py -env -at 1
) else if "%app%"=="2" (
	@REM call %currentDir%\env_list\py310\ov-chatbot.bat
    python %currentDir%\app\scanf_driver.py -env -at 2
) else if "%app%"=="0" (
    goto main_menu
) else (
    echo unknow option,please rechoose!
    pause
    goto install_env
)
pause
goto main_menu

:auto
REM Second level selection - select hardware
cls
echo ====================================
echo          Auto install all 
echo ====================================
@REM call %currentDir%\env_list\py310\ov-obj_det.bat
@REM call %currentDir%\env_list\py310\hailo-obj_det.bat
@REM call %currentDir%\env_list\py310\ov-chatbot.bat
python %currentDir%\app\scanf_driver.py -env -at 0
pause
goto main_menu

:exit
REM end script
echo Thanks for using AAEON AI inference tool, goodbye!
pause
exit

pause