# Check for Administrator rights and self-elevate if necessary
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script needs to be run as Administrator. Relaunching..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    Exit
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Installing Visual C++ All-in-One Redistributables & DirectX" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

# 1. Install Visual C++ All-in-One Redistributable (2005 - 2022)
Write-Host "Installing Visual C++ Redistributable AIO (abbodi1406)..." -ForegroundColor Cyan
winget install --id abbodi1406.vcredist --silent --accept-package-agreements --accept-source-agreements

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Visual C++ Redistributables installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Visual C++ Redistributables (Exit Code: $LASTEXITCODE)." -ForegroundColor Red
}

Write-Host ""

# 2. Install DirectX End-User Runtime
Write-Host "Installing DirectX End-User Runtime..." -ForegroundColor Cyan
winget install --id Microsoft.DirectX --silent --accept-package-agreements --accept-source-agreements

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ DirectX Runtime installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install DirectX Runtime (Exit Code: $LASTEXITCODE)." -ForegroundColor Red
}

Write-Host ""
Write-Host "All installation tasks completed. Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
