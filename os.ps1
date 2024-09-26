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

# Function to display the Git Push sub-menu
function mklink_menu {
    Clear-Host
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "          mklink         " -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "1. xx"                    -ForegroundColor Green
    Write-Host "2. xx"                    -ForegroundColor Green
    Write-Host "3. xx"                    -ForegroundColor Green
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
function Install_Packages {
    Write-Host "Installing packages..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
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
            Run_NewWindow 'Install_Packages' 
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
            RNewWindow -FunctionName "echo 4"
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
}
