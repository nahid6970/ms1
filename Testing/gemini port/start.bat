@echo off
echo ========================================
echo   Gemini CLI Dashboard Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
) else (
    echo Dependencies already installed
)

echo.
echo [2/3] Starting Flask server...
echo.
echo Dashboard will be available at: http://localhost:4785
echo Press Ctrl+C to stop the server
echo.

start http://localhost:4785

python gemini_server.py

pause
