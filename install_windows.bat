@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title WirelessADB Installer - Mark II 🤖

echo ============================================================
echo        WIRELESS ADB - ADVANCED DEPLOYMENT (MARK II) 🔥
echo ============================================================
echo.

:: 1. Admin Privilege Detection 🛡️
net session >nul 2>&1
if %errorLevel% == 0 (
    set "IS_ADMIN=1"
    set "INSTALL_DIR=C:\WirelessADB"
    set "WRAPPER_PATH=C:\Windows\wireless-adb.bat"
    echo [INFO] Running with SYSTEM privileges. Absolute power. 😈
) else (
    set "IS_ADMIN=0"
    set "INSTALL_DIR=%USERPROFILE%\.wireless_adb"
    set "WRAPPER_PATH=%USERPROFILE%\wireless-adb.bat"
    echo [INFO] Running in User mode. (Right-click "Run as Admin" for system-wide 💀)
)
echo.

:: 2. Pre-flight Diagnostics (Python & ADB) 🚀
echo [*] Running pre-flight diagnostics...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [FATAL] Python is missing! Go fetch it bro. 😭
    pause
    exit /b 1
)
adb version >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARN] ADB not found in PATH! Make sure to fix that later. 😳
) else (
    echo [OK] ADB detected.
)
echo [OK] Core dependencies verified. 👌
echo.

:: 3. Python Dependency Auto-Installer 📦
echo [*] Checking Python dependencies...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt --quiet
    echo [OK] Dependencies locked and loaded. 💯
) else (
    echo [SKIP] No requirements.txt found. Moving on. 🏃‍♂️
)
echo.

:: 4. Installation & Update Protocol 💾
if exist "%INSTALL_DIR%\wireless_adb.py" (
    echo [INFO] Existing installation detected at %INSTALL_DIR%.
    echo [*] Initiating Overwrite/Update protocol... 🔄
) else (
    echo [*] Creating fresh directories... 🏗️
    mkdir "%INSTALL_DIR%" 2>nul
)

:: Payload check so the user doesn't brick their setup 💀
if not exist "wireless_adb.py" (
    echo [FATAL] wireless_adb.py not found in current folder! Bruh, where is the payload? 😭
    pause
    exit /b 1
)

copy /Y "wireless_adb.py" "%INSTALL_DIR%\wireless_adb.py" >nul
echo [OK] Payload injected to %INSTALL_DIR%. 🎯

:: 5. Dynamic Wrapper Creation 🛠️
echo @echo off > "%WRAPPER_PATH%"
:: Using double percents to escape the arg variable properly
echo python "%INSTALL_DIR%\wireless_adb.py" %%* >> "%WRAPPER_PATH%"
echo [OK] Global wrapper forged at %WRAPPER_PATH%. 🔨
echo.

:: 6. The PATH Power Move ⚡
if %IS_ADMIN%==0 (
    echo [*] Injecting wrapper into User PATH... 💉
    :: PowerShell injection prevents the 1024 char truncation bug native to setx
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$path = [Environment]::GetEnvironmentVariable('Path', 'User'); if ($path -notmatch [regex]::Escape('%USERPROFILE%')) { [Environment]::SetEnvironmentVariable('Path', $path + ';%USERPROFILE%', 'User') }" >nul 2>&1
    echo [OK] User PATH updated safely! No manual setup needed. 🧠
) else (
    :: C:\Windows is already in System PATH. No registry edit needed! 🤯
    echo [OK] Wrapper placed in C:\Windows. Inheriting default System PATH. 🌌
)
echo.

echo ============================================================
echo   DEPLOYMENT SUCCESSFUL. SYSTEM IS ONLINE. 🚀🔥
echo ============================================================
echo.
echo Next Steps:
echo 1. Restart your terminal (to reload the PATH variables).
echo 2. Type 'wireless-adb' to execute.
echo.
pause
