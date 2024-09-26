# Function to display the main menu
function Main_Menu {
    # Clear-Host
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "    Menu Options      " -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "1. Install Packages"    -ForegroundColor Green
    Write-Host "2. Git Pull"            -ForegroundColor Green
    Write-Host "3. Mklink"              -ForegroundColor Green
    Write-Host "4. Exit"                -ForegroundColor Green
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

# Function to install packages (dummy function for example)
function Install-Packages {
    Write-Host "Installing packages..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Packages installed successfully!" -ForegroundColor Green
}

# Function to set up Neovim (dummy function for example)
function Setup-Neovim {
    Write-Host "Setting up Neovim..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Neovim setup completed!" -ForegroundColor Green
}

# Function to push to origin (dummy function for example)
function Push-Origin {
    Write-Host "Pushing to origin..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Pushed to origin successfully!" -ForegroundColor Green
}

# Function to push to upstream (dummy function for example)
function Push-Upstream {
    Write-Host "Pushing to upstream..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    Write-Host "Pushed to upstream successfully!" -ForegroundColor Green
}

# Main script loop
while ($true) {
    Main_Menu
    $choice = Read-Host "Enter Choice"  # Updated to [1-4]

    switch ($choice) {
        1 { Install-Packages }
        2 {
            $returnToMain = $false
            while (-not $returnToMain) {
                Git_Pull_Menu
                $gitChoice = Read-Host "Enter Choice"
                
                switch ($gitChoice) {
                    1 {
                        Push-Origin
                    }
                    2 {
                        Push-Upstream
                    }
                    3 {
                        $returnToMain = $true
                    }
                    default {
                        Write-Host "Invalid option. Please try again." -ForegroundColor Red
                    }
                }
            }
        }
        3 { Setup-Neovim }
        4 {
            echo 4
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
}
