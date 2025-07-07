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

# Define the menu structure
$menu = [ordered]@{
    "Application Setup" = @{
        "jackett + qbittorrent" = {
            nw_pwsh -Command '
                # cd C:\Users\nahid
                Write-Host -ForegroundColor Green "Step 1: open qbittorrent -> view -> search engine -> Go To search engine tab -> search plugin -> check for updates -> now nova3 folder will be added"
                Write-Host -ForegroundColor Green "Step 2: Start Jackett and add the necessary indexes to th list"
                Write-Host -ForegroundColor Green "Step 3: Copy jacket api from webui to jackett.json"
                Start-Process "C:\Users\nahid\AppData\Local\qBittorrent\nova3\engines"
            '
        }
        "Ldplayer" = {
            nw_pwsh_asadmin -Command "
                Remove-Item 'C:\Users\nahid\AppData\Roaming\XuanZhi9\cache\*' -Recurse
                New-NetFirewallRule -DisplayName '@Block_Ld9BoxHeadless_OutInbound' -Direction Outbound -Program 'C:\LDPlayer\LDPlayer9\dnplayer.exe' -Action Block -Enabled True
            "
        }
        "Neovim_1.conf" = {
            nw_pwsh -Command "
                Write-Host 'Setting up Neovim...'
                $su Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim
                $su Remove-Item -Force -Recurse -Verbose C:\Users\nahid\AppData\Local\nvim-data
                $su New-Item -ItemType SymbolicLink -Path C:\Users\nahid\AppData\Local\nvim\init.lua -Target C:\ms1\asset\linux\neovim\init.lua -Force
            "
        }
        "Notepad++ Theme Setup" = {
            nw_pwsh -Command '
                cd C:\Users\nahid
                Write-Host -ForegroundColor Blue "Dracula Theme"
            '
        }
        "PotPlayer Register" = {
            nw_pwsh -Command "
                Start-Process 'C:\ms1\asset\potplayer\PotPlayerMini64.reg' -Verbose
            "
        }
    }
    "Github Projects" = @{
        "Microsoft Activation Scripts (MAS)" = {
            nw_powershell_asadmin -Command "irm https://get.activated.win | iex"
        }
        "ChrisTitus WinUtility" = {
            nw_powershell_asadmin -Command "iwr -useb https://christitus.com/win | iex"
        }
        "WIMUtil" = {
            nw_powershell_asadmin -Command "irm 'https://github.com/memstechtips/WIMUtil/raw/main/src/WIMUtil.ps1' | iex"
        }
        "AppControl Manager" = {
            nw_pwsh_asadmin -Command "(irm 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'AppControl'|iex"
        }
        "Harden Windows Security Using GUI" = {
            nw_powershell_asadmin -Command "(irm 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'P'|iex"
        }
        "Winhance" = {
            nw_powershell_asadmin -Command "irm 'https://github.com/memstechtips/Winhance/raw/main/Winhance.ps1' | iex"
        }
    }
}

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

    $menu.Keys | ForEach-Object { $mainMenuListBox.Items.Add($_) }
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

    # Event handler to populate submenu based on main menu selection
    $mainMenuListBox.Add_SelectionChanged({
        $submenuListBox.Items.Clear()
        $selectedMainMenu = $mainMenuListBox.SelectedItem
        if ($selectedMainMenu -and $menu.Contains($selectedMainMenu)) {
            $menu[$selectedMainMenu].Keys | ForEach-Object { $submenuListBox.Items.Add($_) }
        }
    })

    # Event handler for double-click on submenu to run command
    $submenuListBox.Add_MouseDoubleClick({
        $selectedMainMenu = $mainMenuListBox.SelectedItem
        $selectedSubMenu = $submenuListBox.SelectedItem
        if ($selectedMainMenu -and $selectedSubMenu -and $menu[$selectedMainMenu] -and $menu[$selectedMainMenu].ContainsKey($selectedSubMenu)) {
            . ($menu[$selectedMainMenu][$selectedSubMenu])
        }
    })

    # Show the main window
    $window.ShowDialog() | Out-Null
}

# Run the main menu with submenu system
Show-MainMenu
