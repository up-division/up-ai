@echo off
set current_dir=%~dp0%
call %current_dir%\..\..\inst\win\set_env.bat

if  not defined root_dir (
	echo  Please call set_env.bat to set the environment variables
	pause
	exit
)

set "matched_instances=Intel;"
REM  List of Instance IDs that define Hailo and Nvidia classes
set "Hailo=2864"
set "Nvidia=24FA"

REM Temporary file used to store the output of pnputil
set "tempfile=%temp%\pnputil_output.txt"

setlocal enabledelayedexpansion
pnputil /enum-devices /connected > "%tempfile%"
set "com_instance_ids=Hailo;Nvidia"
REM Browse all categories
set "chatbot_matched_instances=!matched_instances!"
set "obj_matched_instances=!matched_instances!"
for %%I in (%com_instance_ids%) do (
	REM Dynamically expand variable values ​​for each category
	set "current_list=!%%I!"
	
	REM Iterate over each instance ID in a category
	for %%J in (!current_list!) do (
		REM Suppose the file tempfile.txt needs to match
		@REM set "device_instances=PCI\VEN_8086&DEV_%%J"
		findstr /c:"%%J" "%tempfile%" >nul
		if !errorlevel! equ 0 (
			REM If the match is successful, add the Instance ID to matched_instances
			set "obj_matched_instances=!obj_matched_instances!%%I;"
		)
	)
)



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
REM Check if the input is a number
for /F "delims=0123456789" %%A in ("%hardware%") do (
	echo Invalid input. Please enter a number.
	goto :chatbot
)
if %hardware% GTR !counter! (
	echo Invalid input.
	goto :chatbot
) else if %hardware% LSS 0 (
	echo Invalid input.
	goto :chatbot
)
if "%hardware%"=="0" (
	exit
)
REM map value
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
	if exist "%root_dir%/build/ov-chatbot/Scripts/activate.bat" (
		call %root_dir%/build/ov-chatbot/Scripts/activate.bat
		@REM echo Use Local Environment!!!
	) else (
		echo This demo environment not install,please rechoose!
		pause
		goto chatbot
	)
	echo Start Chatbot......
	@REM in run space, use 'python' comand
	python %current_dir%\chatbot.py
) else if "%hardware%"=="0" (
	exit
) else (
	echo unknow option,please rechoose!
	pause
	goto chatbot
)

exit