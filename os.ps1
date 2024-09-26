# Function to display the main menu
function Show-Menu {
    Clear-Host
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "    Menu Options      " -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "1. Install Packages" -ForegroundColor Green
    Write-Host "2. Set up Neovim" -ForegroundColor Green
    Write-Host "3. Git Push Repo" -ForegroundColor Green
}

# Function to display the Git Push sub-menu
function Show-GitMenu {
    Clear-Host
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "    Git Push Sub-Menu     " -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "1. Push to Origin" -ForegroundColor Green
    Write-Host "2. Push to Upstream" -ForegroundColor Green
    Write-Host "3. Go Back to Main Menu" -ForegroundColor Green
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
    Show-Menu
    $choice = Read-Host "Please enter your choice [1-3]"

    switch ($choice) {
        1 {
            Install-Packages
        }
        2 {
            Setup-Neovim
        }
        3 {
            $returnToMain = $false
            while (-not $returnToMain) {
                Show-GitMenu
                $gitChoice = Read-Host "Please select a Git option [1-3]"

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
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
}
