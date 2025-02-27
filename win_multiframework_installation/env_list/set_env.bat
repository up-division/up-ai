@echo off

::root locate
set root_dir=%~dp0%\..\..\

::install env
set vs_installer=%~dp0%\..\app\vc_redist.x64.exe
set py_installer=%~dp0%\..\app\python310_installer.exe
set git_installer=%~dp0%\..\app\Git.exe
set total_step=5

set video_path=%~dp0%\..\..\videos
set model_path=%~dp0%\..\..\models
set build_loaction=%~dp0%\..\env


::module
set chk_net=%~dp0%\chk_net.bat
set refresh=%~dp0%\RefreshEnv.bat
set install_driver=python %~dp0%\..\app\install_driver.py
set build_env=python %~dp0%\..\app\build_env.py
set download_file=python %~dp0%\..\app\download.py

:: set "vc_redist_key=HKLM\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64"
set "vc_redist_key=HKLM\SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\X64"
set "vc_redist_value=Installed"