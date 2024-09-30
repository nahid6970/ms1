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
function New_Window {
    param (
        [string]$Command
    )
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Command
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
    $mainMenuListBox.Background = [System.Windows.Media.Brushes]::Teal
    $mainMenuListBox.Foreground = [System.Windows.Media.Brushes]::White
    $mainMenuListBox.FontSize = 14
    $mainMenuListBox.FontFamily = New-Object System.Windows.Media.FontFamily("JetBrainsMono NFP")
    $mainMenuListBox.Items.Add("Packages Management")
    $mainMenuListBox.Items.Add("Git Setup")
    $mainMenuListBox.Items.Add("Neovim Setup")
    $mainMenuListBox.Items.Add("Port")
    $mainMenuListBox.Items.Add("mklink")
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
    $submenuListBox.Background = [System.Windows.Media.Brushes]::LightSlateGray
    $submenuListBox.Foreground = [System.Windows.Media.Brushes]::White
    $submenuListBox.FontSize = 14
    $submenuListBox.FontFamily = New-Object System.Windows.Media.FontFamily("JetBrainsMono NFP")
    $submenuPanel.Children.Add($submenuListBox)

    # Event handler to populate submenu based on main menu selection
    $mainMenuListBox.Add_SelectionChanged({
        $submenuListBox.Items.Clear()

        switch ($mainMenuListBox.SelectedItem) {
            "Packages Management" {
                $submenuListBox.Items.Add("Install Packages")
                $submenuListBox.Items.Add("Update Packages")
            }
            "Neovim Setup" {
                $submenuListBox.Items.Add("Set up Neovim")
                $submenuListBox.Items.Add("Configure Neovim Plugins")
            }
            "Git Setup" {
                $submenuListBox.Items.Add("Push to Origin")
                $submenuListBox.Items.Add("Push to Upstream")
            }
            "Port" {
                $submenuListBox.Items.Add("5000")
                $submenuListBox.Items.Add("5001")
                $submenuListBox.Items.Add("5002")
            }
            "mklink" {
                $submenuListBox.Items.Add("Path_Var")
            }
        }
    })

    # Event handler for double-click on submenu to open pop-up window or run command
    $submenuListBox.Add_MouseDoubleClick({
        switch ($submenuListBox.SelectedItem) {
            "Install Packages" {
                New_Window -Command "Write-Host 'Packages installed successfully!'"
            }
            "Update Packages" {
                New_Window -Command "Write-Host 'Packages updated successfully!'"
            }
            "Set up Neovim" {
                New_Window -Command "Write-Host 'Neovim setup completed!'"
            }
            "Configure Neovim Plugins" {
                New_Window -Command "Write-Host 'Neovim plugins configured!'"
            }
            "Push to Origin" {
                New_Window -Command "Write-Host 'Repo pushed to origin!'"
            }
            "Push to Upstream" {
                New_Window -Command "Write-Host 'Repo pushed to upstream!'"
            }
            "5000" {
                New_Window -Command 'sudo New-NetFirewallRule -DisplayName "Allow_Port_5000" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any'
            }
            "5001" {
                New_Window -Command 'sudo New-NetFirewallRule -DisplayName "Allow_Port_5001" -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any'
            }
            "5002" {
                New_Window -Command 'sudo New-NetFirewallRule -DisplayName "Allow_Port_5002" -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any'
            }
            "Path_Var" {
                New_Window -Command 'sudo New-Item -ItemType SymbolicLink -Path "C:\Users\nahid\scoop\apps\python\current\Lib\Path_Var.py" -Target "C:\ms1\Path_Var.py" -Force #[pwsh]'
            }
        }
    })

    # Show the main window
    $window.ShowDialog() | Out-Null
}

# Run the main menu with submenu system
Show-MainMenu