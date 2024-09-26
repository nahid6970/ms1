# Function to display the menu
function Show-Menu {
    Clear-Host
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "    Menu Options      " -ForegroundColor Cyan
    Write-Host "======================" -ForegroundColor Cyan
    Write-Host "1. Install Packages" -ForegroundColor Green
    Write-Host "2. Set up Neovim" -ForegroundColor Green
    Write-Host "3. Git Push Repo" -ForegroundColor Green
    Write-Host "4. Exit" -ForegroundColor Green
}

# Function to install packages (dummy function for example)
function Install-Packages {
    Write-Host "Installing packages..." -ForegroundColor Yellow
    # Simulate installation delay
    Start-Sleep -Seconds 2
    Write-Host "Packages installed successfully!" -ForegroundColor Green
}

# Function to set up Neovim (dummy function for example)
function Setup_Neovim {
    Write-Host "Setting up Neovim..." -ForegroundColor Yellow
    # Simulate setup delay
    Start-Sleep -Seconds 2
    Write-Host "Neovim setup completed!" -ForegroundColor Green
}

# Function to push git repository (dummy function for example)
function Git_Push {
    Write-Host "Pushing repository to remote..." -ForegroundColor Yellow
    # Simulate push delay
    Start-Sleep -Seconds 2
    Write-Host "Repository pushed successfully!" -ForegroundColor Green
}

# Main script loop
while ($true) {
    Show-Menu
    $choice = Read-Host "Please enter your choice [1-4]"

    switch ($choice) {
        1 {
            Install-Packages
        }
        2 {
            Setup_Neovim
        }
        3 {
            Git_Push
        }
        4 {
            Write-Host "Exiting the script. Goodbye!" -ForegroundColor Cyan
            break
        }
        default {
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
    
    # Wait for user to press Enter before showing the menu again
    Read-Host "Press Enter to continue"
}
