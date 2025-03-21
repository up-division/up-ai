@echo off

start %~dp0%\hailo\build.bat
start %~dp0%\intel\build.bat
start %~dp0%\nvdia\build.bat
exit
