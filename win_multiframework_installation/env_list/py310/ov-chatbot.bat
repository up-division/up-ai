@echo off
echo =====================================
echo   Install openvino chatbot packages
echo =====================================
py -m venv %currentDir%/env/ov-chatbot
call %currentDir%/env/ov-chatbot/Scripts/activate.bat
pip install onnx==1.16.1
pip install -r %currentDir%\app/openvino\chatbot\requirements.txt
echo ===========================================
echo Chatbot Environment Installation Completed!
echo ===========================================

@REM echo "Check Chatbot run data now!"
@REM if exist "%video_path%" (
@REM     echo Hailo demo video exist.
@REM     echo Hailo model video exist.
@REM )
@REM else (
@REM )
@REM echo "Download Chatbot run data Completed!"