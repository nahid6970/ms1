@echo off
title Webhook Notification Server
cd /d "%~dp0"

echo.
echo  [*] Starting Webhook Notification Server...
echo.

REM Use the same python that's in PATH
python server.py %*

pause
