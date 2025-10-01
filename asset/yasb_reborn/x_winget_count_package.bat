@echo off
setlocal enabledelayedexpansion

for /f %%i in ('winget upgrade ^| findstr /v "Name ---" ^| findstr "winget" ^| find /c /v ""') do set count=%%i

if %count% NEQ 0 (
    echo {"count":%count%}
)
