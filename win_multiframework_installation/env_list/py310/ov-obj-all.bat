@echo off
call %~dp0%\..\set_env.bat

start %~dp0%\hailo-obj_det.bat
start %~dp0%\ov-obj_det.bat
start %~dp0%\pytorch_yolov11.bat
exit
