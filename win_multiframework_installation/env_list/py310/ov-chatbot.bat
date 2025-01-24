@echo off
echo =====================================
echo   Install openvino chatbot packages
echo =====================================
py -3.10 -m venv %currentDir%/env/ov-chatbot
call %currentDir%/env/ov-chatbot/Scripts/activate.bat
@REM pip install onnx==1.16.1
pip install -r %currentDir%\..\chatbot\requirements.txt
echo ===========================================
echo Chatbot Environment Installation Completed!
echo ===========================================
