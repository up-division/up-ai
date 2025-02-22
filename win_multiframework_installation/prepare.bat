@echo off
set "currentDir=%~dp0" 
set "py_installer_dir=%currentDir%\app\python310_installer.exe"
set "py_installed_path_user=%LocalAppData%\Programs\Python\Python310"
set "py_installed_path_alluser=%ProgramFiles%\Python310"
set python_web=www.python.org
set git_web=github.com

@echo off
:: Check it is running with administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator rights to run.
    choice /m "Do you want to restart this script with administrator rights?" /c YN /d N /t 10
    if errorlevel 2 (
        echo Cancel execution.
        pause
        exit /b
    )
    echo Restarting script, please wait...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo Executed as administrator!

echo "Install Visual C++......"
set "is_installed=0x0"
for /F "tokens=3" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" /v Installed') do (
    set "is_installed=%%A"
)
REM Enable delayed expansion to check the results
setlocal enabledelayedexpansion

if "!is_installed!"=="0x1" (
    goto vc_menu
) else (
    echo Install VC++ 2022 now...
    %currentDir%/app/vc_redist.x64.exe /quiet installAllUsers=1 PerpendPath=0 Include_test=0 /passive
    echo Visual C++ installation Complete!
    goto vc_end
)
:vc_menu
echo [Y] Update VC++
echo [N] Pass update VC++
set /p choice="Please choose (Y/N): "

if /i "!choice!"=="Y" (
    echo Updating VC++ to 2022 now...
    REM start /wait "" "..\vc_redist.x64"
    %currentDir%/app/vc_redist.x64.exe /quiet installAllUsers=1 PerpendPath=0 Include_test=0 /passive
    echo Visual C++ installation Complete!
    goto vc_end
) else if /i "!choice!"=="N" (
    echo Pass update VC++!
    goto vc_end
) else (
    echo Input error, please rechoose!
    goto vc_menu
)

:vc_end
endlocal

:install_python
@REM reset %errorlevel%
cd .
py -3.10 --version
if %errorlevel%==0 (
    echo Python 3.10 already in OS!
    goto install_python_end
) else (
    echo Python 3.10 not find!
    @REM goto online_install_python
)
echo "Install python 3.10 now..."
:online_install_python
cd .
if not exist "%py_installer_dir%" (
    echo Download Python 3.10 install exe now.
    ping -n 1 %python_web% >nul 2>&1
    if errorlevel 1 (
        echo Connet Python Web fail...
        echo Please connect to the Internet and click any button to continue.
        pause
        goto online_install_python
        
    ) else (
        echo Connet Python Web now...
        curl https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -o %currentDir%/app/python310_installer.exe
    )
)
endlocal
echo ==============================================
echo           Install Python 3.10 now.
echo ==============================================
echo For which users do you want to install python?
echo 1. All users
echo 2. Local users
echo ==============================================  

:install_python_input
set /p py_usr="Please input number:"
if "%py_usr%"=="1" (
    "%currentDir%/app/python310_installer.exe" /quite InstallAllUsers=1 PrependPath=1 Include_test=0 /passive
    echo "Python installed successfully(For All User)!"
    goto install_python_end
) else if "%py_usr%"=="2" (
    "%currentDir%/app/python310_installer.exe" /quite InstallAllUsers=0 PrependPath=1 Include_test=0 /passive
    echo "Python installed successfully(For Local User)!"
    goto install_python_end
) else (
    echo unknow option,please rechoose!
    goto install_python_input
)

:install_python_end

@REM reset %errorlevel%
cd .
:install_git
echo "Install git now..."
if not exist "%programfiles%\Git\git-cmd.exe" (
    if not exist "%currentDir%\app\Git-2.47.0-64-bit.exe" (
        echo Download git 2.47 installer now.
        ping -n 1 %git_web% >nul 2>&1
        if %errorlevel%==0 (
            echo Connet Github now...
        ) else (
            echo Connet Github fail...
            echo Please connect to the Internet and click any button to continue.
            goto install_git
        )
        curl -L -o %currentDir%/app/git-installer.exe "https://github.com/git-for-windows/git/releases/download/v2.47.0.windows.1/Git-2.47.0-64-bit.exe"
        @REM curl -L -o %currentDir%/app/git-lfs.exe  "https://github.com/git-lfs/git-lfs/releases/download/v3.5.1/git-lfs-windows-v3.5.1.exe"
    )
    echo Install git 2.47
    %currentDir%/app/git-installer.exe /SILENT
    @REM %currentDir%/app/git-lfs.exe /SILENT
    goto install_git
)
echo "GIT installed successfully!"

@REM renew env variables
@REM for /f "tokens=2,* delims= " %%a in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set PATH=%%b
@REM for /f "tokens=2,* delims= " %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set PATH=%%b

:insatll_driver
py -3.10 %currentDir%/app/scanf_driver.py --install_driver

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