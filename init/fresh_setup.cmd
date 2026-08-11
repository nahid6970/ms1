@echo off
:: Set default .ps1 handler to pwsh if available, else powershell
where pwsh >nul 2>&1
if %errorlevel% equ 0 (
    set "PS_EXE=pwsh"
) else (
    set "PS_EXE=powershell"
)
reg add "HKCU\Software\Classes\Microsoft.PowerShellScript.1\Shell\Open\Command" /ve /d "\"%PS_EXE%\" -NoProfile -ExecutionPolicy Bypass -File \"%%1\"" /f >nul 2>&1

%PS_EXE% -NoProfile -ExecutionPolicy Bypass -File "%~dp0fresh_setup.ps1"
