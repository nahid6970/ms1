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
    Write-Host "4. Go Back"                -ForegroundColor Green
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
    Write-Host "4. Go Back"                -ForegroundColor Green
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
    Write-Host "4. Go Back"                -ForegroundColor Green
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
    Write-Host "Pulled successfully!" -ForegroundColor Green
}

# Function to push to upstream (dummy function for example)
function git_pull_ms2 {
    Write-Host "Git Pull ms2..." -ForegroundColor Yellow
    Set-Location C:\
    Write-Host "Pulled successfully!" -ForegroundColor Green
}

# Function to push to upstream (dummy function for example)
function git_pull_ms3 {
    Write-Host "Git Pull ms3..."      -ForegroundColor Yellow
    Set-Location C:\
    Write-Host "Pulled successfully!" -ForegroundColor Green
}

"@ ; Start-Process PWSH -ArgumentList "-NoExit", "-Command", "& { $functions; & $FunctionName }" }
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
                    1 { git_pull_ms1 }
                    2 { git_pull_ms2 }
                    3 { git_pull_ms3 }
                    4 { $returnToMain = $true }
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
                    4 { $returnToMain = $true }
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
                    4 { $returnToMain = $true }
                    default { Write-Host "Invalid option. Please try again." -ForegroundColor Red }
                }
            }
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
}
