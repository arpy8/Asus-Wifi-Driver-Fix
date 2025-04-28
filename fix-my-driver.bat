@echo off
:: Auto-elevate to admin privileges
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if "%errorlevel%" NEQ "0" (
    echo Requesting administrative privileges...
    goto UACPrompt
) else (
    goto gotAdmin
)

:UACPrompt
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    exit /B

:gotAdmin
    if exist "%temp%\getadmin.vbs" del "%temp%\getadmin.vbs"
    pushd "%CD%"
    CD /D "%~dp0"

:: Main script starts here
title WiFi Driver Management Script by arpy8
color 0A

:menu
cls
echo WiFi Driver Management Script by arpy8
echo ======================================
echo.
echo Current Network Adapters:
netsh interface show interface

echo.
echo Options:
echo 1. List available network drivers
echo 2. Restart a network adapter
echo 3. Uninstall and reinstall a specific driver
echo 4. Auto-Reinstall Wi-Fi Driver
echo 5. Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto list_drivers
if "%choice%"=="2" goto restart_adapter
if "%choice%"=="3" goto reinstall_driver
if "%choice%"=="4" goto auto_wifi_reinstall
if "%choice%"=="5" goto exit_script
echo Invalid choice. Please try again.
pause
goto menu

:list_drivers
cls
echo Listing network drivers...
echo.
pnputil /enum-drivers | findstr /i "net wireless wifi"
echo.
pause
goto menu

:restart_adapter
cls
echo Current Network Adapters:
netsh interface show interface
echo.
set /p adapter_name=Enter the name of the network adapter to restart: 
echo.
echo Disabling %adapter_name%...
netsh interface set interface "%adapter_name%" admin=disable
echo Waiting 3 seconds...
timeout /t 3 /nobreak > nul
echo Enabling %adapter_name%...
netsh interface set interface "%adapter_name%" admin=enable
echo %adapter_name% adapter has been restarted.
echo.
pause
goto menu

:reinstall_driver
cls
echo Listing network drivers...
echo.
pnputil /enum-drivers | findstr /i "net wireless wifi"
echo.
set /p driver_name=Enter the driver filename to uninstall (e.g., oem12.inf): 
echo.
echo Removing driver %driver_name%...
pnputil /delete-driver %driver_name% /force
echo Driver removed.
echo.
echo Scanning for hardware changes to reinstall driver...
echo This may take a moment...

:: Check if devcon.exe exists
if exist "%SystemRoot%\System32\devcon.exe" (
    "%SystemRoot%\System32\devcon.exe" rescan
) else (
    :: Alternative method using pnputil
    echo devcon.exe not found. Using pnputil method instead.
    pnputil /scan-devices
)

echo Hardware scan complete. Driver should be reinstalled automatically.
echo.
pause
goto menu

:auto_wifi_reinstall
cls
echo Current Network Adapters:
netsh interface show interface
echo.

:: Check for Wi-Fi adapter and automatically select it
echo Searching for Wi-Fi adapter...
for /f "tokens=*" %%a in ('netsh interface show interface ^| findstr /i "Wi-Fi"') do (
    set "wifi_line=%%a"
    goto :found_wifi
)

echo No Wi-Fi adapter found.
echo Please enter the name of the network adapter to restart:
set /p adapter_name=
goto :continue_restart

:found_wifi
:: Extract the adapter name from the line
for /f "tokens=4*" %%b in ("%wifi_line%") do (
    set "adapter_name=%%b %%c"
)
:: Remove trailing spaces
set "adapter_name=%adapter_name: =%"
echo Found Wi-Fi adapter: %adapter_name%

:continue_restart
echo.
echo Disabling %adapter_name%...
netsh interface set interface "%adapter_name%" admin=disable
echo Waiting 3 seconds...
timeout /t 3 /nobreak > nul
echo Enabling %adapter_name%...
netsh interface set interface "%adapter_name%" admin=enable
echo %adapter_name% adapter has been restarted.
echo.
pause
goto menu

:exit_script
echo Exiting script...
exit /b