@echo off
cls
:: Check it is running with administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator rights to run.
    choice /m "Do you want to restart this script with administrator rights?" /c YN /d N /t 10
    if errorlevel 2 (
        echo Cancel execution.
        goto Start
    )
    echo Restarting script, please wait...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Executed as administrator!

:Start

winget >nul 2>&1
if %errorlevel% equ 0 (
    echo Have Winget 
) else (
    call %~dp0%inst\win\winget_install.bat
)

call %~dp0%inst\win\set_env.bat

if %winpkg% equ 0 (

:: =====================Check vc_redist.x64.exe===========
echo [Step 1 / %total_step%]
cmd /c "exit /b 0"
setlocal
REM Query the registry
reg query %vc_redist_key% /v %vc_redist_value% >nul 2>&1
REM Check the result of the query
if %errorlevel% equ 0 (
    echo Visual C++ Redistributable is installed.
) else (
    echo Visual C++ Redistributable is NOT installed.
     %vs_installer% /quiet installAllUsers=1 PerpendPath=0 Include_test=0 /passive
    echo Visual C++ installation Complete!
)
endlocal



:: ======================Install Python===================
echo [Step 2 / %total_step%]
cmd /c "exit /b 0"
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python 3.10 already in OS!
) ELSE (
    echo Python 3.10 not find!
    IF not exist "%py_installer%"  (
	call %chk_net%
	curl https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -o %py_installer%
    )
    %py_installer% /quite InstallAllUsers=1 PrependPath=1 Include_test=0 /passive
    call %refresh%
    pip install -r requirements.txt
)

:: ======================Install git===================
echo [Step 3 / %total_step%]
cmd /c "exit /b 0"
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo git have installed on the System
) ELSE (
    echo "Install git now..."
    if not exist %git_installer% (
	call %chk_net%
	curl https://github.com/git-for-windows/git/releases/download/v2.47.0.windows.1/Git-2.47.0-64-bit.exe -L -o  %git_installer%
    )
    %git_installer% /SILENT    call %refresh%

)

) else (
    echo [Step 1 / %total_step%]
    winget %vs_installer%
    echo [Step 2 / %total_step%]
    winget %py_installer%
    echo [Step 3 / %total_step%]
    winget %git_installer%

)
call %refresh%
:: ======================Install Node.js===================
echo [Step 4 / %total_step%]
call %chk_net%

echo Creating shortcut for start and stop scripts
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\start.lnk'); $s.TargetPath = '%STARTBAT%'; $s.Save()"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\stop.lnk'); $s.TargetPath = '%STOPBAT%'; $s.Save()"

echo Checking if Node.js is installed...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Node.js is already installed.
    node --version
) else (
    echo Installing Node.js...
    winget install --id OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements --custom INSTALLDIR="C:\NodeJS" && (
        echo Node.js installed successfully.
    ) || (
        echo Failed to install Node.js. Check your internet connection.
        echo Press any key to exit...
        pause >nul
        exit /b
    )
)

call %refresh%

REM Disable path length limit for Python
echo Disabling path length limit...
set "REG_PATH=HKLM\SYSTEM\CurrentControlSet\Control\FileSystem"
set "REG_KEY=LongPathsEnabled"
set "REG_VALUE=1"

REM Check if the registry key exists and set it
reg query "%REG_PATH%" /v "%REG_KEY%" >nul 2>&1
if %errorlevel%==0 (
    reg add "%REG_PATH%" /v "%REG_KEY%" /t REG_DWORD /d %REG_VALUE% /f
    echo Path length limit disabled
) else (
    echo Failed to modify registry. Please check permissions.
    pause
)

echo Node.js Installation complete.


:: ======================Install Driver===================
echo [Step 5 / %total_step%]
call %chk_net%
%install_driver%


:: ======================build environment===================
echo [Step 6 / %total_step%]
call %chk_net%
%build_env%


:install_ok_msg
echo      *** Installation complete! ***
echo ========================================
echo         Please reboot computer!
echo ========================================
goto end

:install_fail_msg
echo ***************************************************
echo Please Check yor computer environment and reinstall
echo ***************************************************

:end
pause
