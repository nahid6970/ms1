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
    $newWindow.Width = 450
    $newWindow.Height = 250
    $newWindow.Background = [System.Windows.Media.Brushes]::Transparent
    $newWindow.WindowStartupLocation = "CenterScreen"
    $newWindow.WindowStyle = "None"
    $newWindow.AllowsTransparency = $true
    
    # Create main border with rounded corners and shadow effect
    $mainBorder = New-Object System.Windows.Controls.Border
    $mainBorder.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(45, 45, 48))
    $mainBorder.CornerRadius = "12"
    $mainBorder.BorderBrush = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 76, 80))
    $mainBorder.BorderThickness = "1"
    $mainBorder.Margin = "10"
    
    # Drop shadow effect
    $dropShadow = New-Object System.Windows.Media.Effects.DropShadowEffect
    $dropShadow.Color = [System.Windows.Media.Colors]::Black
    $dropShadow.ShadowDepth = 5
    $dropShadow.BlurRadius = 15
    $dropShadow.Opacity = 0.3
    $mainBorder.Effect = $dropShadow
    
    $newWindow.Content = $mainBorder
    
    $stackPanel = New-Object System.Windows.Controls.StackPanel
    $stackPanel.Margin = "30"
    $mainBorder.Child = $stackPanel

    # Title with gradient effect
    $titleTextBlock = New-Object System.Windows.Controls.TextBlock
    $titleTextBlock.Text = $Title
    $titleTextBlock.FontSize = 22
    $titleTextBlock.FontWeight = "Bold"
    $titleTextBlock.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(100, 181, 246))
    $titleTextBlock.HorizontalAlignment = "Center"
    $titleTextBlock.Margin = "0,0,0,15"
    $stackPanel.Children.Add($titleTextBlock)

    # Message text
    $messageTextBlock = New-Object System.Windows.Controls.TextBlock
    $messageTextBlock.Text = $Message
    $messageTextBlock.FontSize = 14
    $messageTextBlock.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(220, 220, 220))
    $messageTextBlock.HorizontalAlignment = "Center"
    $messageTextBlock.TextWrapping = "Wrap"
    $messageTextBlock.Margin = "0,0,0,20"
    $stackPanel.Children.Add($messageTextBlock)

    # Close button with hover effects
    $closeButton = New-Object System.Windows.Controls.Button
    $closeButton.Content = "Close"
    $closeButton.Width = 100
    $closeButton.Height = 35
    $closeButton.HorizontalAlignment = "Center"
    $closeButton.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 175, 80))
    $closeButton.Foreground = [System.Windows.Media.Brushes]::White
    $closeButton.BorderThickness = "0"
    $closeButton.FontWeight = "Bold"
    $closeButton.FontSize = 12
    
    # Button styling
    $closeButton.Template = New-Object System.Windows.Controls.ControlTemplate
    $closeButton.Style = New-Object System.Windows.Style
    $closeButton.Style.TargetType = [System.Windows.Controls.Button]
    
    $closeButton.Add_Click({ $newWindow.Close() })
    $stackPanel.Children.Add($closeButton)

    # Make window draggable
    $mainBorder.Add_MouseLeftButtonDown({
        if ($_.LeftButton -eq [System.Windows.Input.MouseButtonState]::Pressed) {
            $newWindow.DragMove()
        }
    })

    $newWindow.ShowDialog() | Out-Null
}

# Function to run a command in a new PowerShell window
function nw_powershell {
    param (
        [scriptblock]$Command
    )
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Command
}

function nw_powershell_asadmin {
    param (
        [scriptblock]$Command
    )
    Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "-Command", $Command
}

function nw_pwsh_asadmin {
    param (
        [scriptblock]$Command
    )
    Start-Process pwsh -Verb RunAs -ArgumentList "-NoExit", "-Command", $Command
}

function nw_pwsh {
    param (
        [scriptblock]$Command
    )
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", $Command
}

# Define the menu structure
$menu = [ordered]@{
    ">> Github Projects" = [ordered]@{
        "[*] Microsoft Activation Scripts (MAS)" = {
            nw_powershell_asadmin -Command {Invoke-RestMethod https://get.activated.win | Invoke-Expression}
        }
        "[+] ChrisTitus WinUtility" = {
            nw_powershell_asadmin -Command {Invoke-WebRequest -useb https://christitus.com/win | Invoke-Expression}
        }
        "[#] WIMUtil" = {
            nw_powershell_asadmin -Command {Invoke-RestMethod 'https://github.com/memstechtips/WIMUtil/raw/main/src/WIMUtil.ps1' | Invoke-Expression}
        }
        "[!] AppControl Manager" = {
            nw_pwsh_asadmin -Command {(Invoke-RestMethod 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'AppControl'|Invoke-Expression}
        }
        "[&] Harden Windows Security Using GUI" = {
            nw_powershell_asadmin -Command {(Invoke-RestMethod 'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1')+'P'|Invoke-Expression}
        }
        "[~] Winhance" = {
            nw_powershell_asadmin -Command {Invoke-RestMethod 'https://github.com/memstechtips/Winhance/raw/main/Winhance.ps1' | Invoke-Expression}
        }
    }
}

# Main Menu and Submenu in a side-by-side view
function Show-MainMenu {
    $window = New-Object System.Windows.Window
    $window.Title = "OS Tools v2.0"
    $window.Width = 800
    $window.Height = 600
    $window.Background = [System.Windows.Media.Brushes]::Transparent
    $window.WindowStartupLocation = "CenterScreen"
    $window.WindowStyle = "None"
    $window.AllowsTransparency = $true
    
    # Main container with rounded corners and gradient background
    $mainBorder = New-Object System.Windows.Controls.Border
    $mainBorder.CornerRadius = "15"
    $mainBorder.BorderThickness = "2"
    $mainBorder.Margin = "10"
    
    # Gradient background
    $gradientBrush = New-Object System.Windows.Media.LinearGradientBrush
    $gradientBrush.StartPoint = "0,0"
    $gradientBrush.EndPoint = "1,1"
    $gradientBrush.GradientStops.Add((New-Object System.Windows.Media.GradientStop([System.Windows.Media.Color]::FromRgb(30, 30, 30), 0.0)))
    $gradientBrush.GradientStops.Add((New-Object System.Windows.Media.GradientStop([System.Windows.Media.Color]::FromRgb(45, 45, 48), 1.0)))
    $mainBorder.Background = $gradientBrush
    
    # Border gradient
    $borderGradient = New-Object System.Windows.Media.LinearGradientBrush
    $borderGradient.StartPoint = "0,0"
    $borderGradient.EndPoint = "1,1"
    $borderGradient.GradientStops.Add((New-Object System.Windows.Media.GradientStop([System.Windows.Media.Color]::FromRgb(100, 181, 246), 0.0)))
    $borderGradient.GradientStops.Add((New-Object System.Windows.Media.GradientStop([System.Windows.Media.Color]::FromRgb(156, 39, 176), 1.0)))
    $mainBorder.BorderBrush = $borderGradient
    
    # Drop shadow effect
    $dropShadow = New-Object System.Windows.Media.Effects.DropShadowEffect
    $dropShadow.Color = [System.Windows.Media.Colors]::Black
    $dropShadow.ShadowDepth = 8
    $dropShadow.BlurRadius = 20
    $dropShadow.Opacity = 0.4
    $mainBorder.Effect = $dropShadow
    
    $window.Content = $mainBorder

    # Main container
    $mainContainer = New-Object System.Windows.Controls.DockPanel
    $mainContainer.Margin = "20"
    $mainBorder.Child = $mainContainer

    # Title bar
    $titleBar = New-Object System.Windows.Controls.Border
    $titleBar.Height = 60
    $titleBar.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(25, 25, 25))
    $titleBar.CornerRadius = "10,10,0,0"
    $titleBar.BorderBrush = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 76, 80))
    $titleBar.BorderThickness = "0,0,0,1"
    [System.Windows.Controls.DockPanel]::SetDock($titleBar, "Top")
    $mainContainer.Children.Add($titleBar)

    # Title content
    $titleContent = New-Object System.Windows.Controls.Grid
    $titleBar.Child = $titleContent

    # App title
    $appTitle = New-Object System.Windows.Controls.TextBlock
    $appTitle.Text = "[OS Tools v2.0]"
    $appTitle.FontSize = 24
    $appTitle.FontWeight = "Bold"
    $appTitle.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(100, 181, 246))
    $appTitle.HorizontalAlignment = "Center"
    $appTitle.VerticalAlignment = "Center"
    $titleContent.Children.Add($appTitle)

    # Close button
    $closeBtn = New-Object System.Windows.Controls.Button
    $closeBtn.Content = "✕"
    $closeBtn.Width = 30
    $closeBtn.Height = 30
    $closeBtn.HorizontalAlignment = "Right"
    $closeBtn.VerticalAlignment = "Center"
    $closeBtn.Margin = "0,0,10,0"
    $closeBtn.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(244, 67, 54))
    $closeBtn.Foreground = [System.Windows.Media.Brushes]::White
    $closeBtn.BorderThickness = "0"
    $closeBtn.FontWeight = "Bold"
    $closeBtn.Add_Click({ $window.Close() })
    $titleContent.Children.Add($closeBtn)

    # Content Grid Layout for side-by-side view
    $contentGrid = New-Object System.Windows.Controls.Grid
    $contentGrid.Margin = "10"
    $mainContainer.Children.Add($contentGrid)

    # Define two columns
    $column1 = New-Object System.Windows.Controls.ColumnDefinition
    $column1.Width = "2*"
    $column2 = New-Object System.Windows.Controls.ColumnDefinition
    $column2.Width = "3*"
    $contentGrid.ColumnDefinitions.Add($column1)
    $contentGrid.ColumnDefinitions.Add($column2)

    # Main Menu (Left Panel)
    $mainMenuBorder = New-Object System.Windows.Controls.Border
    $mainMenuBorder.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(35, 35, 35))
    $mainMenuBorder.CornerRadius = "10"
    $mainMenuBorder.BorderBrush = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 76, 80))
    $mainMenuBorder.BorderThickness = "1"
    $mainMenuBorder.Margin = "5"
    [System.Windows.Controls.Grid]::SetColumn($mainMenuBorder, 0)
    $contentGrid.Children.Add($mainMenuBorder)

    $mainMenuPanel = New-Object System.Windows.Controls.StackPanel
    $mainMenuPanel.Margin = "15"
    $mainMenuBorder.Child = $mainMenuPanel

    $mainMenuTitle = New-Object System.Windows.Controls.TextBlock
    $mainMenuTitle.Text = ">> Categories"
    $mainMenuTitle.FontSize = 18
    $mainMenuTitle.FontWeight = "Bold"
    $mainMenuTitle.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(156, 39, 176))
    $mainMenuTitle.HorizontalAlignment = "Center"
    $mainMenuTitle.Margin = "0,0,0,15"
    $mainMenuPanel.Children.Add($mainMenuTitle)

    # ListBox for main menu options
    $mainMenuListBox = New-Object System.Windows.Controls.ListBox
    $mainMenuListBox.Background = [System.Windows.Media.Brushes]::Transparent
    $mainMenuListBox.BorderThickness = "0"
    $mainMenuListBox.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(220, 220, 220))
    $mainMenuListBox.FontSize = 14
    $mainMenuListBox.FontWeight = "Medium"
    $mainMenuListBox.SelectionMode = "Single"

    $menu.Keys | ForEach-Object { 
        $item = New-Object System.Windows.Controls.ListBoxItem
        $item.Content = $_
        $item.Padding = "10,8"
        $item.Margin = "0,2"
        $mainMenuListBox.Items.Add($item)
    }
    $mainMenuPanel.Children.Add($mainMenuListBox)

    # Submenu (Right Panel)
    $submenuBorder = New-Object System.Windows.Controls.Border
    $submenuBorder.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(40, 40, 40))
    $submenuBorder.CornerRadius = "10"
    $submenuBorder.BorderBrush = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 76, 80))
    $submenuBorder.BorderThickness = "1"
    $submenuBorder.Margin = "5"
    [System.Windows.Controls.Grid]::SetColumn($submenuBorder, 1)
    $contentGrid.Children.Add($submenuBorder)

    $submenuPanel = New-Object System.Windows.Controls.StackPanel
    $submenuPanel.Margin = "15"
    $submenuBorder.Child = $submenuPanel

    $submenuTitle = New-Object System.Windows.Controls.TextBlock
    $submenuTitle.Text = ">> Tools"
    $submenuTitle.FontSize = 18
    $submenuTitle.FontWeight = "Bold"
    $submenuTitle.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 175, 80))
    $submenuTitle.HorizontalAlignment = "Center"
    $submenuTitle.Margin = "0,0,0,15"
    $submenuPanel.Children.Add($submenuTitle)

    $submenuListBox = New-Object System.Windows.Controls.ListBox
    $submenuListBox.Background = [System.Windows.Media.Brushes]::Transparent
    $submenuListBox.BorderThickness = "0"
    $submenuListBox.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(220, 220, 220))
    $submenuListBox.FontSize = 14
    $submenuListBox.SelectionMode = "Single"
    $submenuPanel.Children.Add($submenuListBox)

    # Status bar
    $statusBar = New-Object System.Windows.Controls.TextBlock
    $statusBar.Text = ">> Double-click an item to execute - Right-click for options"
    $statusBar.FontSize = 12
    $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(158, 158, 158))
    $statusBar.HorizontalAlignment = "Center"
    $statusBar.Margin = "0,10,0,0"
    $submenuPanel.Children.Add($statusBar)

    # Event handler to populate submenu based on main menu selection
    $mainMenuListBox.Add_SelectionChanged({
        $submenuListBox.Items.Clear()
        $selectedItem = $mainMenuListBox.SelectedItem
        if ($selectedItem) {
            $selectedMainMenu = $selectedItem.Content
            if ($selectedMainMenu -and $menu.Contains($selectedMainMenu)) {
                $menu[$selectedMainMenu].Keys | ForEach-Object { 
                    $subItem = New-Object System.Windows.Controls.ListBoxItem
                    $subItem.Content = $_
                    $subItem.Padding = "10,8"
                    $subItem.Margin = "0,2"
                    $submenuListBox.Items.Add($subItem)
                }
            }
        }
    })

    # Event handler for double-click on submenu to run command
    $submenuListBox.Add_MouseDoubleClick({
        $selectedMainItem = $mainMenuListBox.SelectedItem
        $selectedSubItem = $submenuListBox.SelectedItem
        if ($selectedMainItem -and $selectedSubItem) {
            $selectedMainMenu = $selectedMainItem.Content
            $selectedSubMenu = $selectedSubItem.Content
            if ($selectedMainMenu -and $selectedSubMenu -and $menu.Contains($selectedMainMenu) -and $menu[$selectedMainMenu].Contains($selectedSubMenu)) {
                $statusBar.Text = ">> Executing: $selectedSubMenu"
                $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 175, 80))
                . ($menu[$selectedMainMenu][$selectedSubMenu])
                Start-Sleep -Milliseconds 2000
                $statusBar.Text = ">> Double-click an item to execute - Right-click for options"
                $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(158, 158, 158))
            }
        }
    })

    # Event handler for right-click context menu on submenu
    $submenuListBox.Add_MouseRightButtonUp({
        $selectedSubItem = $submenuListBox.SelectedItem
        if ($selectedSubItem) {
            $contextMenu = New-Object System.Windows.Controls.ContextMenu
            $contextMenu.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(45, 45, 48))
            $contextMenu.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(220, 220, 220))
            
            # Execute option
            $executeItem = New-Object System.Windows.Controls.MenuItem
            $executeItem.Header = "Execute"
            $executeItem.Add_Click({
                $selectedMainItem = $mainMenuListBox.SelectedItem
                $selectedSubItem = $submenuListBox.SelectedItem
                if ($selectedMainItem -and $selectedSubItem) {
                    $selectedMainMenu = $selectedMainItem.Content
                    $selectedSubMenu = $selectedSubItem.Content
                    if ($selectedMainMenu -and $selectedSubMenu -and $menu.Contains($selectedMainMenu) -and $menu[$selectedMainMenu].Contains($selectedSubMenu)) {
                        $statusBar.Text = ">> Executing: $selectedSubMenu"
                        $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 175, 80))
                        . ($menu[$selectedMainMenu][$selectedSubMenu])
                        Start-Sleep -Milliseconds 2000
                        $statusBar.Text = ">> Double-click an item to execute - Right-click for options"
                        $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(158, 158, 158))
                    }
                }
            })
            $contextMenu.Items.Add($executeItem)
            
            # Execute as Admin option
            $adminItem = New-Object System.Windows.Controls.MenuItem
            $adminItem.Header = "Run as Administrator"
            $adminItem.Add_Click({
                $selectedMainItem = $mainMenuListBox.SelectedItem
                $selectedSubItem = $submenuListBox.SelectedItem
                if ($selectedMainItem -and $selectedSubItem) {
                    $selectedMainMenu = $selectedMainItem.Content
                    $selectedSubMenu = $selectedSubItem.Content
                    if ($selectedMainMenu -and $selectedSubMenu -and $menu.Contains($selectedMainMenu) -and $menu[$selectedMainMenu].Contains($selectedSubMenu)) {
                        $statusBar.Text = ">> Running as Admin: $selectedSubMenu"
                        $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(255, 152, 0))
                        . ($menu[$selectedMainMenu][$selectedSubMenu])
                        Start-Sleep -Milliseconds 2000
                        $statusBar.Text = ">> Double-click an item to execute - Right-click for options"
                        $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(158, 158, 158))
                    }
                }
            })
            $contextMenu.Items.Add($adminItem)
            
            # Separator
            $separator1 = New-Object System.Windows.Controls.Separator
            $contextMenu.Items.Add($separator1)
            
            # Copy command option
            $copyItem = New-Object System.Windows.Controls.MenuItem
            $copyItem.Header = "Copy Command"
            $copyItem.Add_Click({
                $selectedMainItem = $mainMenuListBox.SelectedItem
                $selectedSubItem = $submenuListBox.SelectedItem
                if ($selectedMainItem -and $selectedSubItem) {
                    $selectedMainMenu = $selectedMainItem.Content
                    $selectedSubMenu = $selectedSubItem.Content
                    if ($selectedMainMenu -and $selectedSubMenu -and $menu.Contains($selectedMainMenu) -and $menu[$selectedMainMenu].Contains($selectedSubMenu)) {
                        $command = $menu[$selectedMainMenu][$selectedSubMenu].ToString()
                        [System.Windows.Clipboard]::SetText($command)
                        $statusBar.Text = ">> Command copied to clipboard"
                        $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(100, 181, 246))
                        Start-Sleep -Milliseconds 2000
                        $statusBar.Text = ">> Double-click an item to execute - Right-click for options"
                        $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(158, 158, 158))
                    }
                }
            })
            $contextMenu.Items.Add($copyItem)
            
            # View details option
            $detailsItem = New-Object System.Windows.Controls.MenuItem
            $detailsItem.Header = "View Details"
            $detailsItem.Add_Click({
                $selectedSubItem = $submenuListBox.SelectedItem
                if ($selectedSubItem) {
                    $toolName = $selectedSubItem.Content
                    $description = switch ($toolName) {
                        "[*] Microsoft Activation Scripts (MAS)" { "A comprehensive Windows activation solution using official Microsoft methods." }
                        "[+] ChrisTitus WinUtility" { "An all-in-one Windows utility for system optimization and customization." }
                        "[#] WIMUtil" { "A powerful tool for Windows image management and deployment." }
                        "[!] AppControl Manager" { "Advanced application control and security management for Windows." }
                        "[&] Harden Windows Security Using GUI" { "GUI-based tool for enhancing Windows security settings." }
                        "[~] Winhance" { "Windows enhancement and optimization toolkit." }
                        default { "A useful Windows administration tool." }
                    }
                    Show-NewWindow -Title "Tool Details" -Message "$toolName`n`n$description"
                }
            })
            $contextMenu.Items.Add($detailsItem)
            
            # Separator
            $separator2 = New-Object System.Windows.Controls.Separator
            $contextMenu.Items.Add($separator2)
            
            # Refresh option
            $refreshItem = New-Object System.Windows.Controls.MenuItem
            $refreshItem.Header = "Refresh Menu"
            $refreshItem.Add_Click({
                $statusBar.Text = ">> Menu refreshed"
                $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(76, 175, 80))
                Start-Sleep -Milliseconds 1000
                $statusBar.Text = ">> Double-click an item to execute - Right-click for options"
                $statusBar.Foreground = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(158, 158, 158))
            })
            $contextMenu.Items.Add($refreshItem)
            
            # Show context menu
            $submenuListBox.ContextMenu = $contextMenu
            $contextMenu.IsOpen = $true
        }
    })

    # Make window draggable
    $titleBar.Add_MouseLeftButtonDown({
        if ($_.LeftButton -eq [System.Windows.Input.MouseButtonState]::Pressed) {
            $window.DragMove()
        }
    })

    # Auto-select first item
    if ($mainMenuListBox.Items.Count -gt 0) {
        $mainMenuListBox.SelectedIndex = 0
    }

    # Show the main window
    $window.ShowDialog() | Out-Null
}

# Run the main menu with submenu system
Show-MainMenu