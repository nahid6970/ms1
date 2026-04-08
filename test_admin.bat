@echo off
net session >nul 2>&1
if %errorlevel% == 0 (
    echo Running as Admin: YES
) else (
    echo Running as Admin: NO
)
pause
