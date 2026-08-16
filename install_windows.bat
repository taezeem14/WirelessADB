@echo off
setlocal EnableDelayedExpansion
title WirelessADB Installer

echo.
echo ======================================================================
echo   WIRELESS ADB - WINDOWS INSTALLATION SUITE
echo ======================================================================
echo.

REM 1. Admin Privilege Detection
net session >nul 2>&1
if %errorlevel% == 0 (
    set "IS_ADMIN=1"
    set "INSTALL_DIR=C:\WirelessADB"
    set "BIN_DIR=C:\Windows"
) else (
    set "IS_ADMIN=0"
    set "INSTALL_DIR=%USERPROFILE%\.wireless_adb"
    set "BIN_DIR=%USERPROFILE%\.wireless_adb"
)

if "!IS_ADMIN!"=="1" (
    echo [SYSTEM] Running with elevated Administrator privileges.
) else (
    echo [USER] Running in User Mode.
)
echo.

REM 2. Pre-flight Diagnostics
echo [*] Checking Python runtime...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [FATAL] Python is not installed or not in PATH!
    echo         Download Python 3 from https://python.org
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i detected.

echo [*] Checking Android Debug Bridge...
adb version >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARN] ADB not detected in PATH.
    echo        Download: https://developer.android.com/studio/releases/platform-tools
) else (
    for /f "tokens=*" %%i in ('adb version 2^>^&1 ^| findstr /i "Android Debug Bridge"') do echo [OK] %%i detected.
)
echo.

REM 3. Create Target Directory
if not exist "!INSTALL_DIR!" mkdir "!INSTALL_DIR!" 2>nul

REM 4. Get wireless_adb.py
set "TARGET_PY=!INSTALL_DIR!\wireless_adb.py"
set "GOT_LOCAL=0"

REM Check if wireless_adb.py exists next to this batch file
if exist "%~dp0wireless_adb.py" (
    copy /Y "%~dp0wireless_adb.py" "!TARGET_PY!" >nul
    echo [OK] Copied local wireless_adb.py to !TARGET_PY!
    set "GOT_LOCAL=1"
)

if "!GOT_LOCAL!"=="0" (
    echo [*] Downloading wireless_adb.py from GitHub...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/taezeem14/WirelessADB/main/wireless_adb.py' -OutFile '!TARGET_PY!' -UseBasicParsing } catch { exit 1 }"
    if not exist "!TARGET_PY!" (
        echo [FATAL] Failed to download wireless_adb.py from GitHub.
        pause
        exit /b 1
    )
    echo [OK] Downloaded wireless_adb.py to !TARGET_PY!
)

REM 5. Generate Batch Wrappers
set "WRAPPER=!BIN_DIR!\wireless-adb.bat"
set "ALIAS=!BIN_DIR!\wadb.bat"

echo @echo off> "!WRAPPER!"
echo python "!TARGET_PY!" %%*>> "!WRAPPER!"

echo @echo off> "!ALIAS!"
echo python "!TARGET_PY!" %%*>> "!ALIAS!"

echo [OK] Generated command launcher: !WRAPPER!
echo [OK] Generated shortcut alias: !ALIAS!
echo.

REM 6. Register in PATH if running in User mode
if "!IS_ADMIN!"=="0" (
    echo [*] Checking User PATH...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($p -notmatch [regex]::Escape('!INSTALL_DIR!')) { [Environment]::SetEnvironmentVariable('Path', $p + ';!INSTALL_DIR!', 'User'); Write-Host '[OK] User PATH updated.' } else { Write-Host '[OK] Already in PATH.' }"
)

echo.
echo ======================================================================
echo   INSTALLATION COMPLETE! SYSTEM IS ONLINE.
echo ======================================================================
echo.
echo Commands available in your terminal:
echo   1. wireless-adb           Launch interactive control center menu
echo   2. wadb                   Short alias for wireless-adb
echo   3. wireless-adb connect   One-shot USB to wireless auto-connect
echo   4. wireless-adb doctor    System environment diagnostics
echo.
echo [Note: Restart your terminal to reload PATH if this is your first install]
echo.
pause
endlocal
