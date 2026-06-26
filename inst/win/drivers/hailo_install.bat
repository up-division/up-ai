echo off

set current_dir=%~dp0%
call %current_dir%\..\..\win\set_env.bat

echo ==========================================
echo       HailoRT Automatic Installer        
echo ==========================================

for /f "tokens=*" %%i in ('powershell -NoProfile -Command "Get-PnpDevice | Where-Object {$_.DeviceID -like '*VEN_1E60&DEV_45C4*'} | Select-Object -ExpandProperty DeviceID" 2^>nul') do (
    set "HAILO_10H_FOUND=1"
)

if "%HAILO_10H_FOUND%"=="1" (
    echo [INFO] Hailo 10 device detected! Install hailort 5.3.2......
    %download_file% -url "https://aaeon365-my.sharepoint.com/:u:/g/personal/nas_aaeon_com_tw/IQBpEakgVnFiQ4t-2Okr8ErsAQYL_6db-EIYYaPx1BMyVbQ?e=jqj5xm" -o %current_dir%
    msiexec /i "hailort_5.3.2_windows_installer.msi" INSTALL_ROOT="C:\Program Files\HailoRT" GSTPLUGININSTALL=1 GSTREAMERPLUGINSDIR="C:\GStreamerPlugins" P_HAILORTSERVICE_ENABLE=1 ARPINSTALLLOCATION="C:\Program Files\HailoRT" TARGETDIR="C:\" ADDLOCAL=VCRedist_x64,ProductFeature,VCRedist_x86,CM_C_copyright,CM_C_driver_pcie,CM_C_driver_usb,CM_C_hailonet,CM_C_hailoollama,CM_C_hailortcli,CM_C_headers,CM_C_libhailort,CM_C_pyhailort /quiet /norestart
) else (
    echo [INFO] Install hailort 4.23.0......
    msiexec /i "hailort_4.23.0_windows_installer.msi" INSTALL_ROOT="C:\Program Files\HailoRT" GSTPLUGININSTALL=1 GSTREAMERPLUGINSDIR="C:\GStreamerPlugins" P_HAILORTSERVICE_ENABLE=1 ARPINSTALLLOCATION="C:\Program Files\HailoRT" TARGETDIR="C:\" ADDLOCAL=VCRedist_x64,ProductFeature,VCRedist_x86,CM_C_copyright,CM_C_driver,CM_C_hailonet,CM_C_hailort_service,CM_C_hailort_service_enabling,CM_C_hailortcli,CM_C_headers,CM_C_libhailort,CM_C_pyhailort,CM_C_support /quiet /norestart
)