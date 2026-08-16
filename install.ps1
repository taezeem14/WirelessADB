# ==============================================================================
# WirelessADB - PowerShell Installer
# ==============================================================================
# Works with: powershell.exe (5.1) and pwsh (7+)
# Works via:  irm url | iex   OR   .\install.ps1 (local)
# ==============================================================================

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '======================================================================' -ForegroundColor Cyan
Write-Host '  WIRELESS ADB - POWERSHELL SUITE INSTALLER' -ForegroundColor Cyan
Write-Host '======================================================================' -ForegroundColor Cyan
Write-Host ''

# 1. Check Python
$pythonOk = $false
try {
    $pythonVersion = & python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $pythonVersion detected." -ForegroundColor Green
        $pythonOk = $true
    }
} catch {}
if (-not $pythonOk) {
    Write-Host '[FATAL] Python is not installed or not in PATH!' -ForegroundColor Red
    Write-Host "Download Python 3 from https://python.org (Check 'Add to PATH'!)" -ForegroundColor Yellow
    return
}

# 2. Check ADB
try {
    $adbOutput = & adb version 2>&1
    $adbLine = ($adbOutput | Select-String 'Android Debug Bridge').Line
    if ($adbLine) {
        Write-Host "[OK] $adbLine detected." -ForegroundColor Green
    } else {
        Write-Host '[WARN] ADB not detected in PATH. (https://developer.android.com/studio/releases/platform-tools)' -ForegroundColor Yellow
    }
} catch {
    Write-Host '[WARN] ADB not detected in PATH.' -ForegroundColor Yellow
}

# 3. Determine Install Directory
$isAdmin = $false
try {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
} catch {}

if ($isAdmin) {
    $installDir = 'C:\WirelessADB'
    $binDir = 'C:\Windows'
    Write-Host "[SYSTEM] Installing with Administrator privileges to $installDir" -ForegroundColor Cyan
} else {
    $installDir = [System.IO.Path]::Combine($env:USERPROFILE, '.wireless_adb')
    $binDir = $installDir
    Write-Host "[USER] Installing in User Mode to $installDir" -ForegroundColor Cyan
}

if (-not (Test-Path $installDir)) {
    [void](New-Item -ItemType Directory -Path $installDir -Force)
    Write-Host "[OK] Created directory: $installDir" -ForegroundColor Green
}

# 4. Fetch or Copy wireless_adb.py
$targetScript = [System.IO.Path]::Combine($installDir, 'wireless_adb.py')
$gotLocal = $false

# Only attempt local copy if PSScriptRoot is a real non-empty path (not piped via iex)
if ($PSScriptRoot -and ($PSScriptRoot -ne '')) {
    $localScript = [System.IO.Path]::Combine($PSScriptRoot, 'wireless_adb.py')
    if (Test-Path $localScript) {
        Copy-Item -Path $localScript -Destination $targetScript -Force
        Write-Host "[OK] Copied local wireless_adb.py to $targetScript" -ForegroundColor Green
        $gotLocal = $true
    }
}

if (-not $gotLocal) {
    Write-Host '[*] Downloading latest wireless_adb.py from GitHub...' -ForegroundColor Cyan
    $url = 'https://raw.githubusercontent.com/taezeem14/WirelessADB/main/wireless_adb.py'
    try {
        Invoke-WebRequest -Uri $url -OutFile $targetScript -UseBasicParsing
        Write-Host "[OK] Downloaded wireless_adb.py to $targetScript" -ForegroundColor Green
    } catch {
        Write-Host "[FATAL] Failed to download wireless_adb.py: $_" -ForegroundColor Red
        return
    }
}

# 5. Create Batch Wrappers in binDir
if (-not (Test-Path $binDir)) {
    [void](New-Item -ItemType Directory -Path $binDir -Force)
}

$wrapperPath = [System.IO.Path]::Combine($binDir, 'wireless-adb.bat')
$aliasPath = [System.IO.Path]::Combine($binDir, 'wadb.bat')
$batchContent = "@echo off`r`npython `"$targetScript`" %*`r`n"
$asciiEncoding = [System.Text.Encoding]::ASCII

try {
    [System.IO.File]::WriteAllText($wrapperPath, $batchContent, $asciiEncoding)
    [System.IO.File]::WriteAllText($aliasPath, $batchContent, $asciiEncoding)
    Write-Host "[OK] Created launcher: $wrapperPath" -ForegroundColor Green
    Write-Host "[OK] Created shortcut alias: $aliasPath" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Could not write to $binDir - trying user directory..." -ForegroundColor Yellow
    $fallbackDir = [System.IO.Path]::Combine($env:USERPROFILE, '.wireless_adb')
    if (-not (Test-Path $fallbackDir)) {
        [void](New-Item -ItemType Directory -Path $fallbackDir -Force)
    }
    $wrapperPath = [System.IO.Path]::Combine($fallbackDir, 'wireless-adb.bat')
    $aliasPath = [System.IO.Path]::Combine($fallbackDir, 'wadb.bat')
    [System.IO.File]::WriteAllText($wrapperPath, $batchContent, $asciiEncoding)
    [System.IO.File]::WriteAllText($aliasPath, $batchContent, $asciiEncoding)
    $binDir = $fallbackDir
    Write-Host "[OK] Created launcher: $wrapperPath" -ForegroundColor Green
    Write-Host "[OK] Created shortcut alias: $aliasPath" -ForegroundColor Green
}

# 6. Update User PATH if needed
if (-not $isAdmin) {
    try {
        $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
        if (-not $userPath) { $userPath = '' }
        $pathEntries = $userPath -split ';' | Where-Object { $_ -ne '' }
        $normalizedEntries = $pathEntries | ForEach-Object { $_.TrimEnd('\', ' ') }
        if ($normalizedEntries -notcontains $binDir.TrimEnd('\', ' ')) {
            if ([string]::IsNullOrEmpty($userPath)) { $newPath = $binDir } else { $newPath = ($userPath.TrimEnd(';') + ';' + $binDir) }
            [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
            $env:Path = $env:Path + ';' + $binDir
            Write-Host "[OK] Added $binDir to User PATH permanently!" -ForegroundColor Green
        } else {
            Write-Host "[OK] $binDir already in User PATH." -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARN] Could not update PATH. Add '$binDir' to PATH manually." -ForegroundColor Yellow
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
