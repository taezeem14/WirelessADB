@echo off
REM WirelessADB Windows Installer
REM Run this as Administrator for system-wide installation

echo ============================================================
echo   WirelessADB - Windows Installation
echo ============================================================
echo.

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Check for ADB
adb version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ADB not found in PATH
    echo.
    echo Please install Android Platform Tools:
    echo 1. Download from: https://developer.android.com/studio/releases/platform-tools
    echo 2. Extract to C:\platform-tools\
    echo 3. Run: setx PATH "%%PATH%%;C:\platform-tools"
    echo 4. Restart this installer
    echo.
    pause
    exit /b 1
)

echo [OK] ADB found
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Not running as Administrator
    echo       Installing for current user only...
    echo.
    
    REM User installation
    set INSTALL_DIR=%USERPROFILE%\.wireless_adb
    set WRAPPER_PATH=%USERPROFILE%\wireless-adb.bat
    
    mkdir "%INSTALL_DIR%" 2>nul
    copy /Y wireless_adb.py "%INSTALL_DIR%\wireless_adb.py" >nul
    
    REM Create wrapper batch file
    echo @echo off > "%WRAPPER_PATH%"
    echo python "%INSTALL_DIR%\wireless_adb.py" %%* >> "%WRAPPER_PATH%"
    
    echo [OK] Installed to: %INSTALL_DIR%
    echo [OK] Wrapper created: %WRAPPER_PATH%
    echo.
    echo Add to PATH manually:
    echo setx PATH "%%PATH%%;%USERPROFILE%"
    
) else (
    echo [INFO] Running as Administrator
    echo       Installing system-wide...
    echo.
    
    REM System-wide installation
    set INSTALL_DIR=C:\WirelessADB
    set WRAPPER_PATH=C:\Windows\wireless-adb.bat
    
    mkdir "%INSTALL_DIR%" 2>nul
    copy /Y wireless_adb.py "%INSTALL_DIR%\wireless_adb.py" >nul
    
    REM Create wrapper batch file
    echo @echo off > "%WRAPPER_PATH%"
    echo python "%INSTALL_DIR%\wireless_adb.py" %%* >> "%WRAPPER_PATH%"
    
    echo [OK] Installed to: %INSTALL_DIR%
    echo [OK] Wrapper created: %WRAPPER_PATH%
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo Test with: wireless-adb status
echo.
echo Note: You may need to restart your terminal/PowerShell
echo       for the PATH changes to take effect.
echo.
pause
