@echo off
call "c:\Program Files (x86)\Intel\openvino_2024.1.0\setupvars.bat"

rem input could be set camera id or video path
set input=0


python demo.py %input%

pause