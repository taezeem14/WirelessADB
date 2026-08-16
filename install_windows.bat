@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title ⚡ WirelessADB Pro Installer

echo.
echo  ======================================================================
echo    ⚡ WIRELESS ADB - NEXT-GEN SUITE INSTALLER 🚀
echo  ======================================================================
echo.

:: 1. Admin Privilege Detection
net session >nul 2>&1
if %errorLevel% == 0 (
    set "IS_ADMIN=1"
    set "INSTALL_DIR=C:\WirelessADB"
    set "WRAPPER_PATH=C:\Windows\wireless-adb.bat"
    set "ALIAS_PATH=C:\Windows\wadb.bat"
    echo  [SYSTEM] Running with elevated Administrator privileges. 🛡️
) else (
    set "IS_ADMIN=0"
    set "INSTALL_DIR=%USERPROFILE%\.wireless_adb"
    set "WRAPPER_PATH=%USERPROFILE%\wireless-adb.bat"
    set "ALIAS_PATH=%USERPROFILE%\wadb.bat"
    echo  [USER] Running in User Mode. (Run as Administrator for system-wide install) 💻
)
echo.

:: 2. Pre-flight Diagnostics
echo [*] Checking Python runtime...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [FATAL] Python is not installed or not in PATH! 😭
    echo         Download and install Python 3 from https://python.org
    echo         (Make sure to check 'Add python.exe to PATH' during installation!)
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i detected. 👌

echo [*] Checking Android Debug Bridge (ADB)...
adb version >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARN] ADB not detected in PATH! ⚠️
    echo        Download Platform Tools: https://developer.android.com/studio/releases/platform-tools
) else (
    for /f "tokens=*" %%i in ('adb version 2^>^&1 ^| findstr /i "Android Debug Bridge"') do echo [OK] %%i detected. 📱
)
echo.

:: 3. Create Target Directory & Copy Files
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%" 2>nul
if not exist "wireless_adb.py" (
    echo [FATAL] wireless_adb.py missing from current folder! ❌
    pause
    exit /b 1
)

copy /Y "wireless_adb.py" "%INSTALL_DIR%\wireless_adb.py" >nul
echo [OK] Core payload installed to: %INSTALL_DIR%\wireless_adb.py 🎯

:: 4. Generate Batch Wrappers (wireless-adb & wadb)
echo @echo off > "%WRAPPER_PATH%"
echo python "%INSTALL_DIR%\wireless_adb.py" %%* >> "%WRAPPER_PATH%"

echo @echo off > "%ALIAS_PATH%"
echo python "%INSTALL_DIR%\wireless_adb.py" %%* >> "%ALIAS_PATH%"

echo [OK] Generated command launcher: %WRAPPER_PATH% 🛠️
echo [OK] Generated shortcut alias: %ALIAS_PATH% ⚡
echo.

:: 5. Register in PATH if running in User mode
if %IS_ADMIN%==0 (
    echo [*] Ensuring wrapper directory is in User PATH...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$path = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($path -notmatch [regex]::Escape('%USERPROFILE%')) { [Environment]::SetEnvironmentVariable('Path', $path + ';%USERPROFILE%', 'User') }" >nul 2>&1
    echo [OK] User PATH updated permanently! 🧠
)

echo.
echo  ======================================================================
echo    🎉 INSTALLATION COMPLETE! SYSTEM IS ONLINE. 🚀🔥
echo  ======================================================================
echo.
echo  Commands available in your terminal:
echo    1. wireless-adb           Launch interactive control center menu
echo    2. wadb                   Short alias for wireless-adb
echo    3. wireless-adb connect   One-shot USB to wireless auto-connect
echo    4. wireless-adb doctor    System environment diagnostics
echo.
echo  (Note: If this is your first install, restart your terminal to reload PATH!)
echo.
pause
