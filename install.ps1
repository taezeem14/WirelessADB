# ==============================================================================
# WirelessADB - PowerShell Installer
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '======================================================================' -ForegroundColor Cyan
Write-Host '  WIRELESS ADB - POWERSHELL SUITE INSTALLER' -ForegroundColor Cyan
Write-Host '======================================================================' -ForegroundColor Cyan
Write-Host ''

# 1. Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion detected." -ForegroundColor Green
} catch {
    Write-Host '[FATAL] Python is not installed or not in PATH!' -ForegroundColor Red
    Write-Host "Download Python 3 from https://python.org (Check 'Add to PATH'!)" -ForegroundColor Yellow
    exit 1
}

# 2. Check ADB
try {
    $adbVersion = (adb version 2>&1 | Select-String 'Android Debug Bridge').Line
    if ($adbVersion) {
        Write-Host "[OK] $adbVersion detected." -ForegroundColor Green
    } else {
        Write-Host '[WARN] ADB not detected in PATH. (Download: https://developer.android.com/studio/releases/platform-tools)' -ForegroundColor Yellow
    }
} catch {
    Write-Host '[WARN] ADB not detected in PATH.' -ForegroundColor Yellow
}

# 3. Determine Install Directory
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    $installDir = 'C:\WirelessADB'
    $binDir = 'C:\Windows'
    Write-Host "[SYSTEM] Installing with Administrator privileges to $installDir" -ForegroundColor Cyan
} else {
    $installDir = Join-Path $env:USERPROFILE '.wireless_adb'
    $binDir = $installDir
    Write-Host "[USER] Installing in User Mode to $installDir" -ForegroundColor Cyan
}

if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# 4. Fetch or Copy wireless_adb.py
$targetScript = Join-Path $installDir 'wireless_adb.py'
$hasLocal = $false

if ($PSScriptRoot) {
    $localScript = Join-Path $PSScriptRoot 'wireless_adb.py'
    if (Test-Path $localScript) {
        Copy-Item -Path $localScript -Destination $targetScript -Force
        Write-Host "[OK] Copied local wireless_adb.py to $targetScript" -ForegroundColor Green
        $hasLocal = $true
    }
}

if (!$hasLocal) {
    Write-Host '[*] Downloading latest wireless_adb.py from GitHub...' -ForegroundColor Cyan
    $url = 'https://raw.githubusercontent.com/taezeem14/WirelessADB/main/wireless_adb.py'
    Invoke-WebRequest -Uri $url -OutFile $targetScript -UseBasicParsing
    Write-Host "[OK] Downloaded wireless_adb.py to $targetScript" -ForegroundColor Green
}

# 5. Create Batch Wrappers in binDir
$wrapperPath = Join-Path $binDir 'wireless-adb.bat'
$aliasPath = Join-Path $binDir 'wadb.bat'

$batchLines = @(
    '@echo off',
    ('python "' + $targetScript + '" %*')
)
[System.IO.File]::WriteAllLines($wrapperPath, $batchLines)
[System.IO.File]::WriteAllLines($aliasPath, $batchLines)

Write-Host "[OK] Created launcher: $wrapperPath" -ForegroundColor Green
Write-Host "[OK] Created shortcut alias: $aliasPath" -ForegroundColor Green

# 6. Update User PATH if needed
if (!$isAdmin) {
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -split ';' -notcontains $binDir) {
        [Environment]::SetEnvironmentVariable('Path', ($userPath + ';' + $binDir), 'User')
        $env:Path = $env:Path + ';' + $binDir
        Write-Host "[OK] Added $binDir to User PATH permanently!" -ForegroundColor Green
    }
}

Write-Host ''
Write-Host '======================================================================' -ForegroundColor Green
Write-Host '  INSTALLATION COMPLETE! SYSTEM IS ONLINE.' -ForegroundColor Green
Write-Host '======================================================================' -ForegroundColor Green
Write-Host ''
Write-Host 'Available commands in your terminal:' -ForegroundColor White
Write-Host '  1. wireless-adb           Launch interactive control center menu' -ForegroundColor Cyan
Write-Host '  2. wadb                   Short alias for wireless-adb' -ForegroundColor Cyan
Write-Host '  3. wireless-adb connect   Auto-connect USB device to wireless' -ForegroundColor Cyan
Write-Host '  4. wireless-adb doctor    Pre-flight system diagnostics' -ForegroundColor Cyan
Write-Host ''
Write-Host '(Note: If this is your first install, restart your terminal to reload PATH!)' -ForegroundColor Gray
Write-Host ''
