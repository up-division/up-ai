@echo off
set "currentDir=%~dp0" 
@REM set Path=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\Scripts\;%PATH%
powershell -Command "$orig = [System.Environment]::GetEnvironmentVariable('PATH', 'user'); $pythonPath = 'C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\Scripts\'; [System.Environment]::SetEnvironmentVariable('PATH', $orig + ';' + $pythonPath, 'user')"
set "py_installer_dir=%currentDir%\app\python310_installer.exe"
set "py_installed_path=%LocalAppData%\Programs\Python\Python310"
set python_web=www.python.org
set git_web=github.com


echo "Install Visual C++......"
set "is_installed=0x0"
for /F "tokens=3" %%A in ('reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\X64" /v Installed') do (
    set "is_installed=%%A"
)
REM 啟用延遲展開來檢查結果
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

@REM reset %errorlevel%
cd .
set insatll_count=0
:install_python
echo "Check Python 3.10 now..."
if not exist "%py_installed_path%" (
    if !insatll_count! geq 3 (
        echo Python install fail more than 3 times!!!!!!
        goto install_fail_msg
    )
    set /a insatll_count+=1
    if not exist "%py_installer_dir%" (
        echo Download Python 3.10 install exe now.
        ping -n 1 %python_web% >nul 2>&1
        if %errorlevel%==0 (
            echo Connet Python Web now...
        ) else (
            echo Connet Python Web fail...
            goto install_fail_msg
        )
        curl https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -o %currentDir%/app/python310_installer.exe
    )
    echo Install Python 3.10 now.
    "%currentDir%/app/python310_installer.exe" /quite InstallAllUsers=0 PrependPath=0 Include_test=0 /passive
    goto install_python
)
echo "Python installed successfully!"

@REM reset %errorlevel%
cd .
set insatll_count=0
:install_git
echo "Install git now..."
if not exist "%programfiles%\Git" (
    if !insatll_count! geq 3 (
        echo GIT install fail more than 3 times!!!!!!
        goto install_fail_msg
    )
    set /a insatll_count+=1
    if not exist "%currentDir%\app\Git-2.47.0-64-bit.exe" (
        echo Download git 2.47 installer now.
        ping -n 1 %git_web% >nul 2>&1
        if %errorlevel%==0 (
            echo Connet Github now...
        ) else (
            echo Connet Github fail...
            goto install_fail_msg
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
:insatll_driver
%py_installed_path%\python.exe %currentDir%/app/scanf_driver.py --install_driver

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