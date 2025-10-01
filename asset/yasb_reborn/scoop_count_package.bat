@echo off
setlocal enabledelayedexpansion

for /f %%i in ('scoop status ^| findstr /v "WARN Name ----" ^| findstr /r "." ^| find /c /v ""') do set count=%%i

echo {"count":%count%}