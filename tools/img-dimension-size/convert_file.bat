@echo off
setlocal enabledelayedexpansion

if "%~4"=="" (
    echo Usage: %~nx0 input_file output_file dimension max_size_kb
    echo Example: %~nx0 input.pdf output.jpg 800x800 400
    echo Example: %~nx0 input.jpg output.pdf 1200x1200 500
    exit /b 1
)

set INPUT=%~1
set OUTPUT=%~2
set DIM=%~3
set MAX_KB=%~4
set QUALITY=95

:: Get file extension
for %%A in ("%OUTPUT%") do set EXT=%%~xA

:: PDF to Image
echo %INPUT% | findstr /i "\.pdf$" >nul
if %errorlevel%==0 (
    magick -density 150 "%INPUT%[0]" -resize %DIM% -quality %QUALITY% -background white -alpha remove "%OUTPUT%"
) else if "%EXT%"==".pdf" (
    magick "%INPUT%" -resize %DIM% -quality %QUALITY% "%OUTPUT%"
) else (
    magick "%INPUT%" -resize %DIM% -quality %QUALITY% "%OUTPUT%"
)

:: Check size and reduce quality if needed
:check_size
for %%A in ("%OUTPUT%") do set SIZE=%%~zA
set /a MAX_BYTES=%MAX_KB%*1024
if !SIZE! gtr !MAX_BYTES! (
    if !QUALITY! gtr 50 (
        set /a QUALITY-=5
        echo %INPUT% | findstr /i "\.pdf$" >nul
        if !errorlevel!==0 (
            magick -density 150 "%INPUT%[0]" -resize %DIM% -quality !QUALITY! -background white -alpha remove "%OUTPUT%"
        ) else if "%EXT%"==".pdf" (
            magick "%INPUT%" -resize %DIM% -quality !QUALITY! "%OUTPUT%"
        ) else (
            magick "%INPUT%" -resize %DIM% -quality !QUALITY! "%OUTPUT%"
        )
        goto check_size
    )
)

for %%A in ("%OUTPUT%") do set SIZE=%%~zA
set /a SIZE_KB=!SIZE!/1024
echo Created: %OUTPUT% (%DIM%, !SIZE_KB!KB)
