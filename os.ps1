# Before u Start
# 'UNblock with right click context menu'
# 'Open store and update AppManager'
# 'run powrshell as admin'

Set-Location c:\
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
function nw_powershell {
    param (
        [string]$Command
    )
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Command
}

function nw_powershell_asadmin {
    param (
        [string]$Command
    )
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", $Command
}

function nw_pwsh_asadmin {
    param (
        [string]$Command
    )
    Start-Process pwsh -Verb RunAs -ArgumentList "-NoExit", "-Command", $Command
}


function nw_pwsh {
    param (
        [string]$Command
    )
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", $Command
}

$su = "C:\Users\nahid\scoop\shims\sudo.ps1"

# Main Menu and Submenu in a side-by-side view
function Show-MainMenu {
    $window = New-Object System.Windows.Window
    $window.Title = "OS_v2"
    $window.Width = 600
    $window.Height = 500
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
    $mainMenuListBox.Items.Add("Clone Projects")
    $mainMenuListBox.Items.Add("Backup & Restore")
    $mainMenuListBox.Items.Add("Port")
    $mainMenuListBox.Items.Add("mklink")
    $mainMenuListBox.Items.Add("Github Projects")
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
                $submenuListBox.Items.Add("PKG Manager & Must Apps")
                $submenuListBox.Items.Add("Policies")
                $submenuListBox.Items.Add("Install Scoop Packages")
                $submenuListBox.Items.Add("Install Pwsh Modules")
                $submenuListBox.Items.Add("Font Setup")
                $submenuListBox.Items.Add("pip Packages")
                $submenuListBox.Items.Add("Update Packages ")
            }
            "Application Setup" {
                $submenuListBox.Items.Add("jackett + qbittorrent")
                $submenuListBox.Items.Add("Ldplayer")
                $submenuListBox.Items.Add("Neovim_1.conf")
                $submenuListBox.Items.Add("Neovim_2.conf")
                $submenuListBox.Items.Add("Notepad++ Theme Setup")
                $submenuListBox.Items.Add("PotPlayer Register")
            }
            "Clone Projects" {
                $submenuListBox.Items.Add("clone ms1")
                $submenuListBox.Items.Add("clone ms2")
                $submenuListBox.Items.Add("clone ms3")
            }
            "Port" {
                $submenuListBox.Items.Add("22 [SSH]") # ssh
                $submenuListBox.Items.Add("5000")
                $submenuListBox.Items.Add("5001")
                $submenuListBox.Items.Add("5002")
            }
            "mklink" {
                $submenuListBox.Items.Add("Komorebi")
                $submenuListBox.Items.Add("Reference")
                $submenuListBox.Items.Add("PowerShell Profile")
                $submenuListBox.Items.Add("Prowlarr")
                $submenuListBox.Items.Add("Radarr")
                $submenuListBox.Items.Add("RssGuard")
                $submenuListBox.Items.Add("Sonarr")
                $submenuListBox.Items.Add("Terminal Profile")
                $submenuListBox.Items.Add("VSCode")
            }
            "Github Projects" {
                $submenuListBox.Items.Add("Microsoft Activation Scripts (MAS)")
                $submenuListBox.Items.Add("ChrisTitus WinUtility")
                $submenuListBox.Items.Add("WIMUtil")
                $submenuListBox.Items.Add("AppControl Manager")
                $submenuListBox.Items.Add("Harden Windows Security Using GUI")
                $submenuListBox.Items.Add("Winhance")
            }
            "Backup & Restore" {
                $submenuListBox.Items.Add("decrypt rclone.conf & move")
                $submenuListBox.Items.Add("------------------*------------------")
                $submenuListBox.Items.Add("msBackups [rs]")
                $submenuListBox.Items.Add("msBackups [bk]")
                $submenuListBox.Items.Add("------------------*------------------")
                $submenuListBox.Items.Add("nilesoft nss [bk]")
                $submenuListBox.Items.Add("------------------*------------------")
                $submenuListBox.Items.Add("song [rclone] [bk]")
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
            "ChrisTitus WinUtility" {
                nw_powershell_asadmin -Command "iwr -useb https://christitus.com/win | iex"
            }
            "Microsoft Activation Scripts (MAS)" {
                nw_powershell_asadmin -Command "irm https://get.activated.win | iex"
            }

            "WIMUtil" {
                nw_powershell_asadmin -Command "irm 'https://github.com/memstechtips/WIMUtil/raw/main/src/WIMUtil.ps1' | iex"
            }
            
            "Harden Windows Security Using GUI" {
                nw_powershell_asadmin -Command "(irm 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'P'|iex"
            }
            
            "Winhance" {
                nw_powershell_asadmin -Command "irm 'https://github.com/memstechtips/Winhance/raw/main/Winhance.ps1' | iex"
            }

            "AppControl Manager" {
                nw_pwsh_asadmin -Command "(irm 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'AppControl'|iex"
            }

            "Policies" {
                nw_powershell -Command "
                Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
                Set-ExecutionPolicy RemoteSigned
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
                Install-Module -Name Microsoft.WinGet.Client -Force -AllowClobber
                                         "
            }

            "PKG Manager & Must Apps" {
                nw_powershell -Command "
                    if (-not (Get-Command scoop -ErrorAction SilentlyContinue)) {
                        Invoke-Expression (New-Object Net.WebClient).DownloadString('https://get.scoop.sh')
                    } else {
                        Write-Host 'Scoop is already installed. Skipping installation.' -ForegroundColor Yellow
                    }

                    'Change cache Path'
                    scoop config cache_path D:\@install\scoop\cache

                    scoop install git

                    'Add Buckets'
                    scoop bucket add nonportable
                  # scoop bucket add main
                    scoop bucket add extras
                    scoop bucket add versions
                    scoop bucket add games

                    scoop install sudo
                    scoop install python312
                    scoop install oh-my-posh
                    scoop install fzf
                    scoop install komorebi
                    scoop install rclone
                    scoop install ditto
                    scoop install text-grab
                    scoop install yt-dlp
                    scoop install ffmpeg
                    scoop install highlight
                    scoop install zoxide

                    winget upgrade --source msstore
                    winget upgrade --source winget
                    Write-Host 'winget Source updated successfully!' -ForegroundColor Green
                    winget upgrade --all
                    winget export C:\Users\nahid\OneDrive\backup\installed_apps\list_winget.txt > C:\Users\nahid\OneDrive\backup\installed_apps\ex_wingetlist.txt
                    Write-Host 'Winget Upgraded ☑️'
                    Write-Host 'Packages updated successfully' -ForegroundColor Green

                    winget install Microsoft.PowerShell
                    winget install Notepad++.Notepad++
                    winget install 9NQ8Q8J78637 # ahk (probably need to check)
                                         "
            }

            "Install Scoop Packages" {
                nw_powershell -Command "
                    # scoop install scoop-completion
                    # scoop install scoop-search
                    scoop install ack
                    scoop install adb
                    scoop install bat
                    scoop install capture2text
                    scoop install ditto
                    scoop install ffmpeg
                    scoop install highlight
                    scoop install kitty
                    scoop install neovim
                    scoop install putty
                    scoop install rssguard
                    scoop install rufus
                    scoop install ventoy
                    scoop install winaero-tweaker
                    scoop install yt-dlp
                    Write-Host 'Packages installed successfully' --ForegroundColor Green
                                        "
            }

            "Pip Packages" {
                nw_pwsh -Command "
            # needed
                    # pip install customtkinter
                    # pip install pyautogui
                    # pip install pillow
                    # pip install pyadl
                    # pip install keyboard
                    # pip install psutil
                    # pip install Flask
                    # pip install pycryptodomex
                    # pip install opencv-python
                    # pip install pynput
                    # pip install mss # for 2nd display
                    # pip install screeninfo # for 2nd display
            # not sure if needed
                    # pip install cryptography
                    # pip install importlib
                    # pip install PyDictionary
                    # pip install pywin32
                    # pip install screeninfo
                    # pip install winshell

                    $su C:\Users\nahid\scoop\apps\python312\current\python.exe -m pip install -r C:\ms1\asset\pip\pip_required.txt
                                         "
            }

            "Update Packages " {
                nw_pwsh -Command "scoop status
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
                nw_powershell -Command "
                    $su oh-my-posh font install
                                               "
            }

            "Install Pwsh Modules" {
                nw_pwsh_asadmin -Command "
                    Install-Module -Name BurntToast -Scope CurrentUser
                                               "
            }

            # neovim
            "Neovim_1.conf" {
                nw_pwsh -Command "
                Write-Host 'Setting up Neovim...'
                $su Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim
                $su Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim-data
                $su New-Item -ItemType SymbolicLink -Path C:\Users\nahid\AppData\Local\nvim\init.lua -Target C:\ms1\asset\linux\neovim\init.lua -Force
                "
            }
            "Neovim_2.conf" {
                nw_pwsh -Command "
                Write-Host 'Setting up Neovim...'
                Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim
                Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim-data
                New-Item -ItemType SymbolicLink -Path C:\Users\nahid\AppData\Local\nvim\init.lua -Target C:\ms1\asset\linux\neovim\init2.lua -Force
                "
            }

            "Notepad++ Theme Setup" {
                nw_pwsh -Command '
                cd C:\Users\nahid

                Write-Host -ForegroundColor Blue "Dracula Theme"
                git clone https://github.com/dracula/notepad-plus-plus.git
                Start-Process "C:\Users\nahid\notepad-plus-plus"

                # Write-Host -ForegroundColor Blue "Material Theme"
                # git clone https://github.com/Codextor/npp-material-theme.git
                # Start-Process "C:\Users\nahid\npp-material-theme"

                Start-Process "$env:AppData\Notepad++\themes"
                
                Write-Host -ForegroundColor Green step1: Copy Example.xml from github folder to %AppData%\Notepad++\themes
                Write-Host -ForegroundColor Green step2: Restart Notepad++
                Write-Host -ForegroundColor Green step3: Dracula will be available in Settings > Style Configurator
                '
            }

            "RssGuard" {
                nw_pwsh_asadmin -Command '
                scoop install rssguard
                Stop-Process -Name "rssguard"
                Remove-Item "C:\Users\nahid\scoop\apps\rssguard\current\data4\database" -Recurse
                Remove-Item "C:\Users\nahid\scoop\apps\rssguard\current\data4\config" -Recurse
                New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\rssguard\current\data4\config" -Target "C:\msBackups\@mklink\rssguard\config" -Force
                New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\rssguard\current\data4\database" -Target "C:\msBackups\@mklink\rssguard\database" -Force
                '
            }

            "Ldplayer" {
                nw_pwsh_asadmin -Command "
                Remove-Item 'C:\Users\nahid\AppData\Roaming\XuanZhi9\cache\*' -Recurse
                New-NetFirewallRule -DisplayName '@Block_Ld9BoxHeadless_OutInbound' -Direction Outbound -Program 'C:\LDPlayer\LDPlayer9\dnplayer.exe' -Action Block -Enabled True
                "
            }

            "jackett + qbittorrent" {
                nw_pwsh -Command '
                # cd C:\Users\nahid
                Write-Host -ForegroundColor Green Step 1: open qbittorrent -> view -> search engine -> Go To search engine tab -> search plugin -> check for updates -> now nova3 folder will be added
                Write-Host -ForegroundColor Green Step 2: Start Jackett and add the necessary indexes to th list
                Write-Host -ForegroundColor Green Step 3: Copy jacket api from webui to jackett.json
                Start-Process "C:\Users\nahid\AppData\Local\qBittorrent\nova3\engines"
                '
            }

            # git
            "clone ms1" {
                nw_powershell -Command "
                Write-Host Cloning ms1 to c:\
                cd c:\
                git clone https://github.com/nahid6970/ms1
                Write-Host Cloned ms1 successfully! -ForegroundColor Green
                                         "
            }
            "clone ms2" {
                nw_powershell -Command "
                    Write-Host Cloning ms2 to c:\ 
                    cd c:\
                    git clone https://github.com/nahid6970/ms2
                    Write-Host Cloned ms2 successfully! -ForegroundColor Green
                                         "
            }
            "clone ms3" {
                nw_powershell -Command "
                Write-Host Cloning ms3 to c:\
                cd c:\
                git clone https://github.com/nahid6970/ms3
                Write-Host Cloned ms3 successfully! -ForegroundColor Green
                                         "
            }

            "nilesoft nss [bk]" {
                nw_powershell -Command "
                    # cd c:\
                    Copy-Item -Path 'C:\Program Files\Nilesoft Shell\shell.nss'  -Destination 'C:\ms1\asset\nilesoft_shell\shell.nss' -Force -Verbose
                    Copy-Item -Path 'C:\Program Files\Nilesoft Shell\imports'  -Destination 'C:\ms1\asset\nilesoft_shell\' -Recurse -Force -Verbose
                                         "
            }

            "song [rclone] [bk]" {
                nw_pwsh -Command "
                    rclone sync D:/song/ gu:/song/ -P --check-first --transfers=1 --track-renames --fast-list #--dry-run
                                         "
            }

            # port
            "5000" {
                nw_pwsh -Command "
                    $su New-NetFirewallRule -DisplayName 'Allow_Port_5000' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any
                                         "
            }
            "5001" {
                nw_pwsh -Command "
                $su New-NetFirewallRule -DisplayName 'Allow_Port_5001' -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any
                                         "
            }
            "5002" {
                nw_pwsh -Command "
                    $su New-NetFirewallRule -DisplayName 'Allow_Port_5002' -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any
                                         "
            }
            "22 [SSH]" {
                nw_pwsh -Command "
                    $su New-NetFirewallRule -DisplayName 'Allow_Port_22' -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Profile Any
                                         "
            }
            # mklink
            "Reference" {
                nw_pwsh -Command "$su New-Item -ItemType SymbolicLink -Path 'C:\Users\nahid\scoop\apps\python312\current\Lib\Reference.py' -Target 'C:\ms1\Reference.py' -Force #[pwsh]"
            }
            # sonarr will take some time to resolve the issue internally just wait
            "Sonarr" {
                nw_pwsh -Command "
                    Winget install TeamSonarr.Sonarr
                    # $su Stop-Process -Name 'Sonarr' -Verbose
                    # Remove-Item C:\ProgramData\Sonarr\sonarr.db -Verbose
                    # $su New-Item -ItemType SymbolicLink -Path C:\ProgramData\Sonarr\sonarr.db -Target C:\msBackups\@mklink\sonarr\sonarr.db -Force -Verbose
                    # Start-Process C:\ProgramData\Sonarr\bin\Sonarr.exe -Verbose
                Write-Host Do it with manual Restore! -ForegroundColor Green && Start-Process 'C:\msBackups\ARR_timely'
                                         "
            }
            "Radarr" {
                nw_pwsh -Command "
                    Winget install TeamRadarr.Radarr
                    # $su Stop-Process -Name 'Radarr' -Verbose
                    # $su Stop-Process -Name 'Radarr.Console' -Verbose
                    # Remove-Item C:\ProgramData\Radarr\radarr.db -Verbose
                    # $su New-Item -ItemType SymbolicLink -Path C:\ProgramData\Radarr\radarr.db -Target C:\msBackups\@mklink\radarr\radarr.db -Force -Verbose
                    # Start-Process C:\ProgramData\Radarr\bin\Radarr.exe -Verbose
                Write-Host Do it with manual Restore! -ForegroundColor Green && Start-Process 'C:\msBackups\ARR_timely'
                                         "
            }
            "Prowlarr" {
                nw_pwsh -Command "
                    Winget install TeamProwlarr.Prowlarr
                    # $su Stop-Process -Name 'Prowlarr' -Verbose
                    # Remove-Item C:\ProgramData\Prowlarr\prowlarr.db -Verbose
                    # $su New-Item -ItemType SymbolicLink -Path C:\ProgramData\Prowlarr\prowlarr.db -Target C:\msBackups\@mklink\prowlarr\prowlarr.db -Force -Verbose
                    # Start-Process C:\ProgramData\Prowlarr\bin\Prowlarr.exe -Verbose
                Write-Host Do it with manual Restore! -ForegroundColor Green && Start-Process 'C:\msBackups\ARR_timely'
                                         "
            }
	# initially after creating with  quickstart have to run komorebi with the default profile then we can mklink
    # it will try to replace ms1 komorebi profile just let it and then copy it from git and paste the code in
            "Komorebi" {
                nw_pwsh -Command "
                    Komorebic quickstart
                    Remove-Item 'C:\Users\nahid\komorebi.json'
                    $su New-Item -ItemType SymbolicLink -Path 'C:\Users\nahid\komorebi.json' -Target 'C:\ms1\asset\komorebi\komorebi.json' -Force #[pwsh]
                                         "
            }
            "VSCode" {
                nw_pwsh -Command "
                    New-Item -ItemType SymbolicLink -Path C:\Users\nahid\AppData\Roaming\Code\User\keybindings.json -Target C:\ms1\asset\vscode\keybindings.json -Force
                    New-Item -ItemType SymbolicLink -Path C:\Users\nahid\AppData\Roaming\Code\User\settings.json -Target C:\ms1\asset\vscode\settings.json -Force
                                         "
            }
            "PowerShell Profile" {
                nw_pwsh -Command "
                    $su New-Item -ItemType SymbolicLink -Path C:\Users\nahid\Documents\PowerShell\Microsoft.PowerShell_profile.ps1 -Target C:\ms1\asset\Powershell\Microsoft.PowerShell_profile.ps1 -Force
                                         "
            }
            "Terminal Profile" {
                nw_pwsh -Command "
                    $su New-Item -ItemType SymbolicLink -Path C:\Users\nahid\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json -Target C:\ms1\asset\terminal\settings.json -Force
                                         "
            }
            "PotPlayer Register" {
                nw_pwsh -Command "
                    Start-Process 'C:\ms1\asset\potplayer\PotPlayerMini64.reg' -Verbose
                                         "
            }
        }
    })

    # Show the main window
    $window.ShowDialog() | Out-Null
}

# Run the main menu with submenu system
Show-MainMenu
