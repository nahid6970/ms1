@echo off
setlocal EnableDelayedExpansion
title Fresh Setup - Winget + PWSH + Scoop

:: ============================================================
::  Auto-elevate to Administrator
:: ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting Administrator privileges...
    powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/k \"%~f0\"' -Verb RunAs"
    exit /b
)

:: ============================================================
::  STEP 1: Check & repair winget
:: ============================================================
echo.
echo [1/4] Checking winget...
where winget >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] winget not found. Opening Microsoft Store to install App Installer...
    start ms-windows-store://pdp/?ProductId=9NBLGGH4NNS1
    echo     Install "App Installer" from the Store, then re-run this script.
    pause & exit /b 1
)

echo [*] Updating winget sources...
winget source update
echo [*] Upgrading winget itself (App Installer)...
winget upgrade --id Microsoft.AppInstaller --silent --accept-source-agreements --accept-package-agreements

:: ============================================================
::  Fix PowerShell execution policy (both scopes)
:: ============================================================
echo.
echo [*] Fixing PowerShell execution policy...
powershell -NoProfile -Command "Set-ExecutionPolicy RemoteSigned -Scope LocalMachine -Force; Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

:: ============================================================
::  STEP 2: Install PowerShell 7
:: ============================================================
echo.
echo [2/4] Installing PowerShell 7...
winget install --id Microsoft.PowerShell --silent --accept-source-agreements --accept-package-agreements

:: ============================================================
::  STEP 3: Install Scoop (via pwsh if available, else powershell)
:: ============================================================
echo.
echo [3/4] Setting up Scoop...

:: Prefer pwsh (just installed), fall back to powershell
set "PS=pwsh"
where pwsh >nul 2>&1
if %errorlevel% neq 0 set "PS=powershell"

%PS% -NoProfile -ExecutionPolicy Bypass -Command ^
    "if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) { ^
        Invoke-RestMethod https://get.scoop.sh | Invoke-Expression ^
    } else { Write-Host 'Scoop already installed.' -ForegroundColor Yellow }"

:: Add buckets
echo [*] Adding scoop buckets...
%PS% -NoProfile -ExecutionPolicy Bypass -Command ^
    "scoop bucket add main; scoop bucket add extras; scoop bucket add versions"

:: ============================================================
::  STEP 4: Install scoop packages
:: ============================================================
echo.
echo [4/4] Installing packages...
%PS% -NoProfile -ExecutionPolicy Bypass -Command ^
    "scoop install git python fzf bat ripgrep fd eza ^
     oh-my-posh scoop-search scoop-completion ^
     ffmpeg yt-dlp rclone ^
     7zip curl wget jq ^
     neovim"

echo.
echo ============================================================
echo  Done! Restart your terminal to use all installed tools.
echo ============================================================
pause
