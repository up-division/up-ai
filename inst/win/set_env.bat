@echo off

::root locate
set root_dir=%~dp0%..\..\

::install env
winget >nul 2>&1
if %errorlevel% equ 0 (
echo Windows package-manager supported.
set winpkg=1
set vs_installer=install -e --id Microsoft.VCRedist.2015+.x64
set py_installer=install -e --id Python.Python.3.10
set git_installer=Git.Git --override "/SP /SUPPRESSMSGBOXES /NORESTART /ALLUSERS"
) else (
set winpkg=0
set vs_installer=%~dp0%vc_redist.x64.exe
set py_installer=%~dp0%python310_installer.exe
set git_installer=%~dp0%Git.exe
)
set total_step=6

set video_path=%~dp0%..\..\videos
set model_path=%~dp0%..\..\models

set "DESKTOP=%USERPROFILE%\Desktop"
set "STARTBAT=%root_dir%demos\edge-ai-sizing-tool\start.bat"
set "STOPBAT=%root_dir%demos\edge-ai-sizing-tool\stop.bat"

::module
set chk_net=%~dp0%bat\chk_net.bat
set refresh=%~dp0%bat\RefreshEnv.bat
set install_driver=python %~dp0%install_driver.py
set build_env=python %~dp0%..\common\build_env.py
set download_file=python %~dp0%..\common\download.py

:: set "vc_redist_key=HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
set "vc_redist_key=HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\X64"
set "vc_redist_value=Installed"