Add-Type -AssemblyName PresentationFramework

# Function to create a new styled pop-up window
function Show-NewWindow {
    param (
        [string]$Title,
        [string]$Message
    )

    # Create a new window
    $newWindow = New-Object System.Windows.Window
    $newWindow.Title = $Title
    $newWindow.Width = 400
    $newWindow.Height = 200
    $newWindow.Background = [System.Windows.Media.Brushes]::SlateGray
    $newWindow.WindowStartupLocation = "CenterScreen"
    
    $stackPanel = New-Object System.Windows.Controls.StackPanel
    $stackPanel.Margin = "20"
    $newWindow.Content = $stackPanel

    $titleTextBlock = New-Object System.Windows.Controls.TextBlock
    $titleTextBlock.Text = $Title
    $titleTextBlock.FontSize = 20
    $titleTextBlock.FontWeight = "Bold"
    $titleTextBlock.Foreground = [System.Windows.Media.Brushes]::White
    $titleTextBlock.HorizontalAlignment = "Center"
    $stackPanel.Children.Add($titleTextBlock)

    $messageTextBlock = New-Object System.Windows.Controls.TextBlock
    $messageTextBlock.Text = $Message
    $messageTextBlock.FontSize = 14
    $messageTextBlock.Foreground = [System.Windows.Media.Brushes]::LightYellow
    $messageTextBlock.HorizontalAlignment = "Center"
    $messageTextBlock.Margin = "0,10,0,0"
    $stackPanel.Children.Add($messageTextBlock)

    $closeButton = New-Object System.Windows.Controls.Button
    $closeButton.Content = "Close"
    $closeButton.Width = 80
    $closeButton.HorizontalAlignment = "Center"
    $closeButton.Background = [System.Windows.Media.Brushes]::LightSlateGray
    $closeButton.Foreground = [System.Windows.Media.Brushes]::White
    $closeButton.Margin = "0,20,0,0"
    $closeButton.Add_Click({ $newWindow.Close() })
    $stackPanel.Children.Add($closeButton)

    $newWindow.ShowDialog() | Out-Null
}

# Function to run a command in a new PowerShell window
function New_Window_powershell {
    param (
        [string]$Command
    )
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Command
}

function New_Window_pwsh {
    param (
        [string]$Command
    )
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", $Command
}

# Main Menu and Submenu in a side-by-side view
function Show-MainMenu {
    $window = New-Object System.Windows.Window
    $window.Title = "OS_v2"
    $window.Width = 600
    $window.Height = 300
    $window.Background = [System.Windows.Media.Brushes]::DarkSlateGray
    $window.WindowStartupLocation = "CenterScreen"

    # Grid Layout for side-by-side view
    $grid = New-Object System.Windows.Controls.Grid
    $grid.ShowGridLines = $false
    $window.Content = $grid

    # Define two columns (one for main menu, one for submenu)
    $column1 = New-Object System.Windows.Controls.ColumnDefinition
    $column1.Width = "2*"
    $column2 = New-Object System.Windows.Controls.ColumnDefinition
    $column2.Width = "3*"
    $grid.ColumnDefinitions.Add($column1)
    $grid.ColumnDefinitions.Add($column2)

    # Main Menu (Left Panel)
    $mainMenuPanel = New-Object System.Windows.Controls.StackPanel
    $mainMenuPanel.Margin = "10"
    [System.Windows.Controls.Grid]::SetColumn($mainMenuPanel, 0)
    $grid.Children.Add($mainMenuPanel)

    $mainMenuTitle = New-Object System.Windows.Controls.TextBlock
    $mainMenuTitle.Text = "Main Menu"
    $mainMenuTitle.FontSize = 18
    $mainMenuTitle.FontWeight = "Bold"
    $mainMenuTitle.Foreground = [System.Windows.Media.Brushes]::White
    $mainMenuTitle.HorizontalAlignment = "Center"
    $mainMenuPanel.Children.Add($mainMenuTitle)

    # ListBox for main menu options
    $mainMenuListBox = New-Object System.Windows.Controls.ListBox
    $mainMenuListBox.Background = [System.Windows.Media.Brushes]::White
    $mainMenuListBox.Foreground = [System.Windows.Media.Brushes]::Black
    $mainMenuListBox.FontSize = 14
    $mainMenuListBox.FontFamily = New-Object System.Windows.Media.FontFamily("JetBrainsMono NFP")
    #* ███████╗██╗██████╗ ███████╗████████╗
    #* ██╔════╝██║██╔══██╗██╔════╝╚══██╔══╝
    #* █████╗  ██║██████╔╝███████╗   ██║
    #* ██╔══╝  ██║██╔══██╗╚════██║   ██║
    #* ██║     ██║██║  ██║███████║   ██║
    #* ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝
    $mainMenuListBox.Items.Add("Initial Setup")
    $mainMenuListBox.Items.Add("Application Setup")
    $mainMenuListBox.Items.Add("Git Setup")
    $mainMenuListBox.Items.Add("Neovim Setup")
    $mainMenuListBox.Items.Add("Port")
    $mainMenuListBox.Items.Add("mklink")
    $mainMenuListBox.Items.Add("Echo")
    $mainMenuPanel.Children.Add($mainMenuListBox)

    # Submenu (Right Panel)
    $submenuPanel = New-Object System.Windows.Controls.StackPanel
    $submenuPanel.Margin = "10"
    [System.Windows.Controls.Grid]::SetColumn($submenuPanel, 1)
    $grid.Children.Add($submenuPanel)

    $submenuTitle = New-Object System.Windows.Controls.TextBlock
    $submenuTitle.Text = "Submenu"
    $submenuTitle.FontSize = 18
    $submenuTitle.FontWeight = "Bold"
    $submenuTitle.Foreground = [System.Windows.Media.Brushes]::White
    $submenuTitle.HorizontalAlignment = "Center"
    $submenuPanel.Children.Add($submenuTitle)

    $submenuListBox = New-Object System.Windows.Controls.ListBox
    $submenuListBox.Background = [System.Windows.Media.Brushes]::Black
    $submenuListBox.Foreground = [System.Windows.Media.Brushes]::White
    $submenuListBox.FontSize = 14
    $submenuListBox.FontFamily = New-Object System.Windows.Media.FontFamily("JetBrainsMono NFP")
    $submenuPanel.Children.Add($submenuListBox)

    #* ███████╗██╗   ██╗██████╗ ███╗   ███╗███████╗███╗   ██╗██╗   ██╗
    #* ██╔════╝██║   ██║██╔══██╗████╗ ████║██╔════╝████╗  ██║██║   ██║
    #* ███████╗██║   ██║██████╔╝██╔████╔██║█████╗  ██╔██╗ ██║██║   ██║
    #* ╚════██║██║   ██║██╔══██╗██║╚██╔╝██║██╔══╝  ██║╚██╗██║██║   ██║
    #* ███████║╚██████╔╝██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║╚██████╔╝
    #* ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝
    # Event handler to populate submenu based on main menu selection
    $mainMenuListBox.Add_SelectionChanged({
        $submenuListBox.Items.Clear()

        switch ($mainMenuListBox.SelectedItem) {
            "Initial Setup" {
                $submenuListBox.Items.Add("Setup Winget")
                $submenuListBox.Items.Add("Setup Scoop")
                $submenuListBox.Items.Add("Must Packages")
                $submenuListBox.Items.Add("Install Winget Packages")
                $submenuListBox.Items.Add("Install Scoop Packages")
                $submenuListBox.Items.Add("Update Packages ")
                $submenuListBox.Items.Add("pip Packages")
                $submenuListBox.Items.Add("Font Setup")
            }
            "Application Setup" {
                $submenuListBox.Items.Add("Set up Neovim")
            }
            "Git Setup" {
                $submenuListBox.Items.Add("clone ms1")
                $submenuListBox.Items.Add("clone ms2")
                $submenuListBox.Items.Add("clone ms3")

            }
            "Port" {
                $submenuListBox.Items.Add("5000")
                $submenuListBox.Items.Add("5001")
                $submenuListBox.Items.Add("5002")
            }
            "mklink" {
                $submenuListBox.Items.Add("Path_Var")
                $submenuListBox.Items.Add("Sonarr")
                $submenuListBox.Items.Add("Radarr")
                $submenuListBox.Items.Add("Prowlarr")
                $submenuListBox.Items.Add("Komorebi")
            }
            "Echo" {
                $submenuListBox.Items.Add("SSH [PC-->Android]")
                $submenuListBox.Items.Add("SSH [Android-->PC]")

            }
        }
    })

    #* ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗███████╗
    #* ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║██╔════╝
    #* █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║███████╗
    #* ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║╚════██║
    #* ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║███████║
    #* ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝

    # Event handler for double-click on submenu to open pop-up window or run command
    $submenuListBox.Add_MouseDoubleClick({
        switch ($submenuListBox.SelectedItem) {
            # package
            "Setup Scoop" {
                New_Window_pwsh -Command "
                    if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
                        Invoke-Expression (New-Object Net.WebClient).DownloadString('https://get.scoop.sh')
                    } else {
                        Write-Host 'Scoop is already installed. Skipping installation.' -ForegroundColor Yellow
                    }
                    scoop bucket add main
                    scoop bucket add extras
                    scoop bucket add versions
                    scoop bucket add nonportable
                    scoop config cache_path D:\@install\scoop\cache
                                         "
            }
            "Must Packages" {
                New_Window_powershell -Command "
                    winget install Microsoft.PowerShell
                    scoop install git
                    scoop install sudo
                    scoop install python
                    scoop install oh-my-posh
                    scoop install fzf
                    scoop install komorebi
                                        "
            }
            "Install Scoop Packages" {
                New_Window_pwsh -Command "
                    # scoop install scoop-completion
                    # scoop install scoop-search
                    scoop install ack
                    scoop install adb
                    scoop install bat
                    scoop install capture2text
                    scoop install ditto
                    scoop install ffmpeg
                    scoop install highlight
                    scoop install rclone
                    scoop install rssguard
                    scoop install rufus
                    scoop install ventoy
                    scoop install winaero-tweaker
                    scoop install yt-dlp
                    scoop install putty
                    Write-Host 'Packages installed successfully' --ForegroundColor Green
                                        "
            }
            "Install Winget Packages" {
                New_Window_pwsh -Command "
                    winget install 9NQ8Q8J78637
                                        "
            }
            "Pip Packages" {
                New_Window_pwsh -Command "
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
                                         "
            }
            "Setup Winget" {
                New_Window_pwsh -Command "
                    winget upgrade --source msstore
                    winget upgrade --source winget
                    Write-Host 'winget Source updated successfully!' -ForegroundColor Green
                                        "
            }
            "Update Packages " {
                New_Window_pwsh -Command "scoop status
                                     scoop update
                                     Write-Host 'Scoop Status & Bucked Updated ☑️'
                                     scoop update *
                                     scoop export > C:\Users\nahid\OneDrive\backup\installed_apps\list_scoop.txt
                                     Write-Host 'scoop updated ☑️'
                                     scoop cleanup *
                                     Write-Host 'Scoop Cleanedup ☑️'
                                     winget upgrade --all
                                     winget export C:\Users\nahid\OneDrive\backup\installed_apps\list_winget.txt > C:\Users\nahid\OneDrive\backup\installed_apps\ex_wingetlist.txt
                                     Write-Host 'Winget Upgraded ☑️'
                                     Write-Host 'Packages updated successfully' -ForegroundColor Green"
            }
            "Font Setup" {
                New_Window_powershell -Command "
                    sudo oh-my-posh font install
                                               "
            }
            # neovim
            "Set up Neovim" {
                New_Window_pwsh -Command "
                Write-Host 'Setting up Neovim...'
                #sudo rm data folder  and init folder
                scoop install neovim
                #mklink
                "
            }
            # git
            "clone ms1" {
                New_Window_pwsh -Command "
                Write-Host Cloning ms1 to c:\
                cd c:\
                git clone https://github.com/nahid6970/ms1
                Write-Host Cloned ms1 successfully! -ForegroundColor Green
                                         "
            }
            "clone ms2" {
                New_Window_pwsh -Command "
                    Write-Host Cloning ms2 to c:\ 
                    cd c:\
                    git clone https://github.com/nahid6970/ms2
                    Write-Host Cloned ms2 successfully! -ForegroundColor Green
                                         "
            }
            "clone ms3" {
                New_Window_pwsh -Command "
                Write-Host Cloning ms3 to c:\
                cd c:\
                git clone https://github.com/nahid6970/ms3
                Write-Host Cloned ms3 successfully! -ForegroundColor Green
                                         "
            }
            # port
            "5000" {
                New_Window_pwsh -Command "
                    sudo New-NetFirewallRule -DisplayName 'Allow_Port_5000' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any
                                         "
            }
            "5001" {
                New_Window_pwsh -Command "
                sudo New-NetFirewallRule -DisplayName 'Allow_Port_5001' -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any
                                         "
            }
            "5002" {
                New_Window_pwsh -Command "
                    sudo New-NetFirewallRule -DisplayName 'Allow_Port_5002' -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any
                                         "
            }
            # mklink
            "Path_Var" {
                New_Window_pwsh -Command 'sudo New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\python\current\Lib\Path_Var.py" -Target "C:\ms1\Path_Var.py" -Force #[pwsh]'
            }
            "Sonarr" {
                New_Window_pwsh -Command "
                    Winget install TeamSonarr.Sonarr
                    sudo Stop-Process -Name 'Sonarr' -Verbose
                    Remove-Item C:\ProgramData\Sonarr\sonarr.db -Verbose
                    New-Item -ItemType SymbolicLink -Path C:\ProgramData\Sonarr\sonarr.db -Target C:\Users\nahid\OneDrive\backup\@mklink\sonarr\sonarr.db -Force -Verbose
                    Start-Process C:\ProgramData\Sonarr\bin\Sonarr.exe -Verbose
                                         "
            }
            "Radarr" {
                New_Window_pwsh -Command "
                    Winget install TeamRadarr.Radarr
                    sudo Stop-Process -Name 'Radarr' -Verbose
                    Remove-Item C:\ProgramData\Radarr\radarr.db -Verbose
                    New-Item -ItemType SymbolicLink -Path C:\ProgramData\Radarr\radarr.db -Target C:\Users\nahid\OneDrive\backup\@mklink\radarr\radarr.db -Force -Verbose
                    Start-Process C:\ProgramData\Radarr\bin\Radarr.exe -Verbose
                                         "
            }
            "Prowlarr" {
                New_Window_pwsh -Command "
                    Winget install TeamProwlarr.Prowlarr
                    sudo Stop-Process -Name 'Prowlarr' -Verbose
                    Remove-Item C:\ProgramData\Prowlarr\prowlarr.db -Verbose
                    New-Item -ItemType SymbolicLink -Path C:\ProgramData\Prowlarr\prowlarr.db -Target C:\Users\nahid\OneDrive\backup\@mklink\prowlarr\prowlarr.db -Force -Verbose
                    Start-Process C:\ProgramData\Prowlarr\bin\Prowlarr.exe -Verbose
                                         "
            }
            "Komorebi" {
                New_Window_pwsh -Command "
                    Komorebic quickstart
                    Remove-Item 'C:\Users\nahid\komorebi.json'
                    New-Item -ItemType SymbolicLink -Path 'C:\Users\nahid\komorebi.json' -Target 'C:\ms1\mklink\komorebi\komorebi.json' -Force #[pwsh]
                                         "
            }
            # echo
            "SSH [PC-->Android]" {
                New_Window_pwsh -Command "
                    # 'Hello, World!'
                    'plink -ssh -P 8022 -pw XXX u0_a827@192.168.0.102 #give double quota to XXX later' 
                                         "
            }
            "SSH [Android-->PC]" {
                New_Window_pwsh -Command "
                    # 'Hello, World!'
                    'sshpass -p xxx ssh nahid@192.168.0.101'
                                         "
            }
        }
    })

    # Show the main window
    $window.ShowDialog() | Out-Null
}

# Run the main menu with submenu system
Show-MainMenu
