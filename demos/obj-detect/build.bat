@echo off

call %~dp0%\hailo\build.bat
call %~dp0%\intel\build.bat
call %~dp0%\nvdia\build.bat
exit
