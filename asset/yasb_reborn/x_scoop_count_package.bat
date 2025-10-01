@echo off
setlocal enabledelayedexpansion

for /f %%i in ('scoop status ^| findstr /v "Everything Scoop WARN Name ----" ^| findstr /r "." ^| find /c /v ""') do set count=%%i

if %count% NEQ 0 (
    echo {"count":%count%}
)
