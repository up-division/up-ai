@echo off

set current_dir=%~dp0%
call %current_dir%\..\..\inst\win\set_env.bat

if  not defined root_dir (
    echo  Please call set_env.bat to set the environment variables
    pause
    exit
)

if exist "%root_dir%\build\ov-chatbot" (
    echo The Demo env already exists. Do you want to delete it?
    choice /c yn /m "Please choose (y/n):"
    if errorlevel 2 (
        goto download
    ) else (
        rmdir /S /Q %root_dir%\build\ov-chatbot
    )
)

echo =====================================
echo   Install openvino chatbot packages
echo =====================================

py -3.10 -m venv %root_dir%/build/ov-chatbot
call %root_dir%/build/ov-chatbot/Scripts/activate.bat

@REM pip install onnx==1.16.1
pip install -r %current_dir%\requirements.txt

echo ===========================================
echo Chatbot Environment Installation Completed!
echo ===========================================
call %root_dir%/build/ov-chatbot/Scripts/deactivate.bat


:download
echo "Download Chatbot Model!"
if not exist "%current_dir%\tiny-llama-1b-chat\" (
    mkdir %current_dir%\tiny-llama-1b-chat\
)
%download_file% -url "https://aaeon365-my.sharepoint.com/:u:/g/personal/junyinglai_aaeon_com_tw/ERzwCuBCBbZNh0-08aTXsj4BpZyy0o0X2NoZBUbrxGtbCQ?e=8ANs3B" -o %current_dir%\tiny-llama-1b-chat\

pause
exit