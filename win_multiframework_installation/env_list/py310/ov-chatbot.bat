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
echo "Check Chatbot Model!"
set FILE_URL=https://aaeon365-my.sharepoint.com/:u:/g/personal/dannyzhang_aaeon_com_tw/Ee8WFbG9QvRPmIUYY859Gr4B3CXQhMlG2_m0ROpBYVXfsg?download=1
set "model_path=%currentDir%\..\chatbot\tiny-llama-1b-chat\INT4_compressed_weights\openvino_model.bin"
@REM get model size(local)
for %%A in ("%model_path%") do set FILE_SIZE=%%~zA
@REM SIZE_LIMIT=10MB
set /a SIZE_LIMIT=10485760
echo Chatbot Model Size:%FILE_SIZE%
if %FILE_SIZE% LSS %SIZE_LIMIT% (
    del %model_path%
)
if exist %model_path% (
    echo Chatbot model exist.
) else (
    echo Download Chatbot Model now!
    powershell -command "wget %FILE_URL% -o %model_path%"
    echo Download done!
)