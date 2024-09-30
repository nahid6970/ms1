#? ██████╗ ██╗███████╗██████╗ ██╗      █████╗ ██╗   ██╗    ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
#? ██╔══██╗██║██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝    ████╗ ████║██╔════╝████╗  ██║██║   ██║
#? ██║  ██║██║███████╗██████╔╝██║     ███████║ ╚████╔╝     ██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
#? ██║  ██║██║╚════██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝      ██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
#? ██████╔╝██║███████║██║     ███████╗██║  ██║   ██║       ██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
#? ╚═════╝ ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝
# Function to display the main menu
function Main_Menu {
    Clear-Host
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "    Menu Options      " -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "1. Install Packages"    -ForegroundColor Green
    Write-Host "2. Git Pull"            -ForegroundColor Green
    Write-Host "3. Mklink"              -ForegroundColor Green
    Write-Host "4. pip packages"        -ForegroundColor Green
    Write-Host "5. Port Register"        -ForegroundColor Green
}

# Function to display the Git Push sub-menu
function Git_Pull_Menu {
    Clear-Host
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "         Git Pull        " -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "1. ms1"                    -ForegroundColor Green
    Write-Host "2. ms2"                    -ForegroundColor Green
    Write-Host "3. ms3"                    -ForegroundColor Green
    Write-Host "X. Go Back"                -ForegroundColor White
}

# Function to display the mklink sub-menu
function mklink_menu {
    Clear-Host
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "          mklink         " -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "1. xx"                     -ForegroundColor Green
    Write-Host "2. xx"                     -ForegroundColor Green
    Write-Host "3. xx"                     -ForegroundColor Green
    Write-Host "X. Go Back"                -ForegroundColor White
}

# Function to display the Port sub-menu
function port_menu {
    Clear-Host
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "           Port          " -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "1. Port 5000"              -ForegroundColor Green
    Write-Host "2. Port 5001"              -ForegroundColor Green
    Write-Host "3. Port 5002"              -ForegroundColor Green
    Write-Host "X. Go Back"                -ForegroundColor White
}

#!  ██╗ ██╗
#! ████████╗
#! ╚██╔═██╔╝
#! ████████╗
#! ╚██╔═██╔╝
#!  ╚═╝ ╚═╝

# Function to run commands in a new PowerShell window
function Run_NewWindow {
    param (
        [string]$FunctionName
    )
    # Define functions in the new PowerShell window
    $functions = @"

#* ██████╗  █████╗  ██████╗██╗  ██╗ █████╗  ██████╗ ███████╗███████╗
#* ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔════╝ ██╔════╝██╔════╝
#* ██████╔╝███████║██║     █████╔╝ ███████║██║  ███╗█████╗  █████╗
#* ██╔═══╝ ██╔══██║██║     ██╔═██╗ ██╔══██║██║   ██║██╔══╝  ██╔══╝
#* ██║     ██║  ██║╚██████╗██║  ██╗██║  ██║╚██████╔╝███████╗███████╗
#* ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝
# Function to install packages (dummy function for example)
function Install_Packages_scoop {
    Write-Host "Installing Scoop packages..." -ForegroundColor Yellow
    scoop install git
    scoop install python

    scoop install ack
    scoop install adb
    scoop install bat
    scoop install capture2text
    scoop install ditto
    scoop install ffmpeg
    scoop install fzf
    scoop install highlight
    scoop install komorebi
    scoop install oh-my-posh
    scoop install rclone
    scoop install rssguard
    scoop install rufus
    scoop install scoop-completion
    scoop install scoop-search
    scoop install sudo
    scoop install ventoy
    scoop install winaero-tweaker
    scoop install yt-dlp
    Write-Host "Packages installed successfully!" -ForegroundColor Green
}

function Install_Packages_winget {
    Write-Host "Installing Winget packages..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Packages installed successfully!" -ForegroundColor Green
}

function Install_Packages_pip {
    Write-Host "Installing pip packages..." -ForegroundColor Yellow
    pip install cryptography
    pip install customtkinter
    pip install importlib
    pip install keyboard
    pip install pillow
    pip install psutil
    pip install pyadl
    pip install pyautogui
    pip install pycryptodomex
    pip install PyDictionary
    pip install pywin32
    pip install screeninfo
    pip install winshell
    pip install Flask

# pip list
# Package                Version
# ---------------------- -----------
# aes                    1.2.0
# ahk                    1.7.8
# annotated-types        0.7.0
# anyio                  4.4.0
# asttokens              2.4.1
# bcrypt                 4.2.0
# beautifulsoup4         4.12.3
# blinker                1.8.2
# BlurWindow             1.2.1
# bs4                    0.0.2
# Cerberus               1.3.5
# certifi                2024.2.2
# cffi                   1.16.0
# charset-normalizer     3.3.2
# cipher                 0.1
# click                  8.1.7
# clr-loader             0.2.6
# colorama               0.4.6
# colorzero              2.0
# comm                   0.2.2
# comtypes               1.4.2
# crypto                 1.4.1
# cryptography           42.0.7
# cssutils               2.10.2
# customtkinter          5.2.2
# darkdetect             0.8.0
# debugpy                1.8.5
# decorator              5.1.1
# diffusers              0.31.0.dev0
# executing              2.0.1
# filelock               3.15.4
# Flask                  3.0.3
# fsspec                 2024.6.1
# futures                3.0.5
# goslate                1.5.4
# gpiozero               2.0.1
# greenlet               3.1.1
# h11                    0.14.0
# httpcore               1.0.5
# httpx                  0.27.0
# huggingface-hub        0.24.6
# humanize               4.9.0
# idna                   3.7
# importlib              1.0.4
# importlib_metadata     8.3.0
# ipykernel              6.29.5
# ipython                8.26.0
# itsdangerous           2.2.0
# jedi                   0.19.1
# Jinja2                 3.1.4
# jupyter_client         8.6.2
# jupyter_core           5.7.2
# keyboard               0.13.5
# MarkupSafe             2.1.5
# matplotlib-inline      0.1.7
# mccabe                 0.7.0
# MouseInfo              0.1.3
# mpmath                 1.3.0
# msgpack                1.1.0
# mss                    9.0.1
# Naked                  0.1.32
# neovim                 0.3.1
# nest-asyncio           1.6.0
# networkx               3.3
# numpy                  1.26.4
# ollama                 0.2.1
# opencv-python          4.9.0.80
# opencv-python-headless 4.9.0.80
# packaging              24.0
# paramiko               3.5.0
# parso                  0.8.4
# pillow                 10.3.0
# pip                    24.2
# platformdirs           4.2.2
# playsound              1.3.0
# prompt_toolkit         3.0.47
# psutil                 5.9.8
# pure_eval              0.2.3
# pyadl                  0.1
# PyAutoGUI              0.9.54
# pycodestyle            2.11.1
# pycparser              2.22
# pycryptodome           3.20.0
# pycryptodomex          3.20.0
# pydantic               2.8.2
# pydantic_core          2.20.1
# PyDictionary           2.0.1
# PyDirectInput          1.0.4
# pydocstyle             6.3.0
# pyflakes               3.2.0
# PyGetWindow            0.0.9
# Pygments               2.18.0
# pylama                 8.4.1
# PyMsgBox               1.0.9
# PyNaCl                 1.5.0
# pynput                 1.7.7
# pynvim                 0.5.0
# pyperclip              1.8.2
# PyQt6                  6.7.0
# PyQt6-Qt6              6.7.0
# PyQt6-sip              13.6.0
# PyRect                 0.2.0
# PyScreeze              0.1.30
# pytesseract            0.3.10
# python-dateutil        2.9.0.post0
# pythonnet              3.0.3
# pytweening             1.2.0
# pytz                   2024.1
# pywin32                306
# pywinauto              0.6.8
# PyYAML                 6.0.1
# pyzmq                  26.1.0
# regex                  2024.7.24
# replicate              0.31.0
# requests               2.31.0
# safetensors            0.4.4
# screeninfo             0.8.1
# setuptools             73.0.0
# shellescape            3.8.1
# six                    1.16.0
# sniffio                1.3.1
# snowballstemmer        2.2.0
# soupsieve              2.5
# stack-data             0.6.3
# sympy                  1.13.2
# tesseract              0.1.3
# tkinter-tooltip        3.1.0
# tkinterdnd2            0.3.0
# torch                  2.4.0
# tornado                6.4.1
# tqdm                   4.66.5
# traitlets              5.14.3
# ttkbootstrap           1.10.1
# typing_extensions      4.12.2
# tzdata                 2024.1
# tzlocal                5.2
# urllib3                2.2.1
# watchdog               4.0.0
# wcwidth                0.2.13
# Werkzeug               3.0.4
# wheel                  0.44.0
# winsdk                 1.0.0b10
# winshell               0.6
# WMI                    1.5.1
# zipp                   3.20.0
    Write-Host "Packages installed successfully!" -ForegroundColor Green
}

#* ███╗   ███╗██╗  ██╗██╗     ██╗███╗   ██╗██╗  ██╗
#* ████╗ ████║██║ ██╔╝██║     ██║████╗  ██║██║ ██╔╝
#* ██╔████╔██║█████╔╝ ██║     ██║██╔██╗ ██║█████╔╝
#* ██║╚██╔╝██║██╔═██╗ ██║     ██║██║╚██╗██║██╔═██╗
#* ██║ ╚═╝ ██║██║  ██╗███████╗██║██║ ╚████║██║  ██╗
#* ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
# Function to set up Neovim (dummy function for example)
function mklink {
    Write-Host "Setting up Neovim..."    -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Neovim setup completed!" -ForegroundColor Green
}


#* ██████╗  ██████╗ ██████╗ ████████╗
#* ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝
#* ██████╔╝██║   ██║██████╔╝   ██║
#* ██╔═══╝ ██║   ██║██╔══██╗   ██║
#* ██║     ╚██████╔╝██║  ██║   ██║
#* ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝

# Function to set up Neovim (dummy function for example)
function port_5000 {
    Write-Host "Setting up Neovim..."    -ForegroundColor Yellow
    sudo New-NetFirewallRule -DisplayName "Allow_Port_5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any
    Write-Host "Neovim setup completed!" -ForegroundColor Green
}

function port_5001 {
    Write-Host "Setting up Neovim..."    -ForegroundColor Yellow
    sudo New-NetFirewallRule -DisplayName "Allow_Port_5001" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any
    Write-Host "Neovim setup completed!" -ForegroundColor Green
}

function port_5002 {
    Write-Host "Setting up Neovim..."    -ForegroundColor Yellow
    sudo New-NetFirewallRule -DisplayName "Allow_Port_5002" -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any
    Write-Host "Neovim setup completed!" -ForegroundColor Green
}

#*  ██████╗ ██╗████████╗
#* ██╔════╝ ██║╚══██╔══╝
#* ██║  ███╗██║   ██║
#* ██║   ██║██║   ██║
#* ╚██████╔╝██║   ██║
#*  ╚═════╝ ╚═╝   ╚═╝
# Function to push to origin (dummy function for example)
function git_pull_ms1 {
    Write-Host "Git Pull ms1..."      -ForegroundColor Yellow
    Set-Location C:\
    git clone https://github.com/nahid6970/ms1
    Write-Host "Pulled successfully!" -ForegroundColor Green
}

# Function to push to upstream (dummy function for example)
function git_pull_ms2 {
    Write-Host "Git Pull ms2..." -ForegroundColor Yellow
    Set-Location C:\
    git clone https://github.com/nahid6970/ms2
    Write-Host "Pulled successfully!" -ForegroundColor Green
}

# Function to push to upstream (dummy function for example)
function git_pull_ms3 {
    Write-Host "Git Pull ms3..."      -ForegroundColor Yellow
    Set-Location C:\
    git clone https://github.com/nahid6970/ms3
    Write-Host "Pulled successfully!" -ForegroundColor Green
}

"@ ; Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { $functions; & $FunctionName }" }
#!  ██╗ ██╗
#! ████████╗
#! ╚██╔═██╔╝
#! ████████╗
#! ╚██╔═██╔╝
#!  ╚═╝ ╚═╝

#?  ██████╗██╗  ██╗ ██████╗ ██╗ ██████╗███████╗███████╗
#? ██╔════╝██║  ██║██╔═══██╗██║██╔════╝██╔════╝██╔════╝
#? ██║     ███████║██║   ██║██║██║     █████╗  ███████╗
#? ██║     ██╔══██║██║   ██║██║██║     ██╔══╝  ╚════██║
#? ╚██████╗██║  ██║╚██████╔╝██║╚██████╗███████╗███████║
#?  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝ ╚═════╝╚══════╝╚══════╝
# Main script loop
while ($true) {
    Main_Menu
    $choice = Read-Host "Enter Choice"  # Updated to [1-4]

    switch ($choice) {
        1 {
            Run_NewWindow 'Install_Packages_scoop ; Install_Packages_winget' 
            }
        2 {
            $returnToMain = $false
            while (-not $returnToMain) {
                Git_Pull_Menu
                $pickChoice = Read-Host "Enter Choice"
                switch ($pickChoice) {
                    1 { Run_NewWindow git_pull_ms1 }
                    2 { Run_NewWindow git_pull_ms2 }
                    3 { Run_NewWindow git_pull_ms3 }
                    x { $returnToMain = $true }
                    default { Write-Host "Invalid option. Please try again." -ForegroundColor Red }
                }
            }
        }
        3 {
            $returnToMain = $false
            while (-not $returnToMain) {
                mklink_menu
                $pickChoice = Read-Host "Enter Choice"
                switch ($pickChoice) {
                    1 { git_pull_ms1 }
                    2 { git_pull_ms2 }
                    3 { git_pull_ms3 }
                    x { $returnToMain = $true }
                    default { Write-Host "Invalid option. Please try again." -ForegroundColor Red }
                }
            }
        }
        
        4 {
            Run_NewWindow "Install_Packages_pip"
        }
        5 {
            $returnToMain = $false
            while (-not $returnToMain) {
                port_menu
                $pickChoice = Read-Host "Enter Choice"
                switch ($pickChoice) {
                    1 { Run_NewWindow port_5000 }
                    2 { Run_NewWindow port_5001 }
                    3 { Run_NewWindow port_5002 }
                    x { $returnToMain = $true }
                    default { Write-Host "Invalid option. Please try again." -ForegroundColor Red }
                }
            }
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
}
