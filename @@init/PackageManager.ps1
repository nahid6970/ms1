# Required Assemblies
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, Microsoft.VisualBasic, System.Xml

# State Management
$jsonPath = Join-Path $PSScriptRoot "packages.json"
function Load-Packages {
    if (Test-Path $jsonPath) {
        try { Get-Content $jsonPath -Raw | ConvertFrom-Json } catch { @() }
    } else { @() }
}
function Save-Packages {
    param($Packages)
    $Packages | ConvertTo-Json -Depth 10 | Set-Content $jsonPath
}

# Create Window
$window = New-Object System.Windows.Window
$window.Title = "Package Manager"
$window.Width = 480
$window.Height = 600
$window.Background = [System.Windows.Media.Brushes]::White
$window.WindowStartupLocation = "CenterScreen"

# Main Container
$mainGrid = New-Object System.Windows.Controls.Grid
$mainGrid.Margin = "15"
$window.Content = $mainGrid

# Row Definitions
$row1 = New-Object System.Windows.Controls.RowDefinition; $row1.Height = "Auto"; $mainGrid.RowDefinitions.Add($row1)
$row2 = New-Object System.Windows.Controls.RowDefinition; $row2.Height = "Auto"; $mainGrid.RowDefinitions.Add($row2)
$row3 = New-Object System.Windows.Controls.RowDefinition; $row3.Height = "*";    $mainGrid.RowDefinitions.Add($row3)
$row4 = New-Object System.Windows.Controls.RowDefinition; $row4.Height = "Auto"; $mainGrid.RowDefinitions.Add($row4)

# Title
$title = New-Object System.Windows.Controls.TextBlock
$title.Text = "App Manager"
$title.FontSize = 26
$title.FontWeight = "Bold"
$title.Margin = "0,0,0,15"
[System.Windows.Controls.Grid]::SetRow($title, 0)
$mainGrid.Children.Add($title)

# Header Bar (Select All + Add + Install Selected)
$headerStack = New-Object System.Windows.Controls.StackPanel
$headerStack.Orientation = "Horizontal"
$headerStack.Margin = "0,0,0,15"
[System.Windows.Controls.Grid]::SetRow($headerStack, 1)
$mainGrid.Children.Add($headerStack)

$selectAll = New-Object System.Windows.Controls.CheckBox
$selectAll.Content = "Select All"
$selectAll.VerticalAlignment = "Center"
$selectAll.Margin = "5,0,20,0"
$headerStack.Children.Add($selectAll)

$btnAdd = New-Object System.Windows.Controls.Button
$btnAdd.Content = "+"
$btnAdd.Width = 35
$btnAdd.Height = 35
$btnAdd.FontWeight = "Bold"
$btnAdd.FontSize = 18
$btnAdd.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253))
$btnAdd.Foreground = [System.Windows.Media.Brushes]::White
$headerStack.Children.Add($btnAdd)

$btnInstallSelected = New-Object System.Windows.Controls.Button
$btnInstallSelected.Content = "Install Selected"
$btnInstallSelected.Margin = "15,0,0,0"
$btnInstallSelected.Padding = "15,5"
$btnInstallSelected.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(25, 135, 84))
$btnInstallSelected.Foreground = [System.Windows.Media.Brushes]::White
$headerStack.Children.Add($btnInstallSelected)

# Package List (ListView)
$packageListUI = New-Object System.Windows.Controls.ListView
$packageListUI.Background = [System.Windows.Media.Brushes]::White
[System.Windows.Controls.Grid]::SetRow($packageListUI, 2)
$mainGrid.Children.Add($packageListUI)

# --- Programmatic DataTemplate (Zero XAML) ---
$dataTemplate = New-Object System.Windows.DataTemplate

$borderFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Border])
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0,0,0,1)))
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderBrushProperty, (New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(241, 243, 245))))
$borderFactory.SetValue([System.Windows.Controls.Border]::PaddingProperty, (New-Object System.Windows.Thickness(5)))

$gridFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Grid])
$gridFactory.SetValue([System.Windows.Controls.Grid]::WidthProperty, 410.0)

$col1 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition])
$col1.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(35)))
$gridFactory.AppendChild($col1)

$col2 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition])
$col2.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)))
$gridFactory.AppendChild($col2)

$col3 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition])
$col3.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(140)))
$gridFactory.AppendChild($col3)

# CheckBox
$cbFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.CheckBox])
$cbFactory.SetBinding([System.Windows.Controls.CheckBox]::IsCheckedProperty, (New-Object System.Windows.Data.Binding "IsSelected"))
$cbFactory.SetValue([System.Windows.Controls.CheckBox]::VerticalAlignmentProperty, [System.Windows.VerticalAlignment]::Center)
$cbFactory.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 0)
$gridFactory.AppendChild($cbFactory)

# StackPanel Info
$spInfo = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel])
$spInfo.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 1)

$txtName = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock])
$txtName.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Name"))
$txtName.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::SemiBold)
$spInfo.AppendChild($txtName)

$txtID = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock])
$txtID.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "ID"))
$txtID.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 11.0)
$txtID.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::Gray)
$spInfo.AppendChild($txtID)

$gridFactory.AppendChild($spInfo)

# Buttons Container
$spBtns = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel])
$spBtns.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal)
$spBtns.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 2)
$spBtns.SetValue([System.Windows.Controls.StackPanel]::HorizontalAlignmentProperty, [System.Windows.HorizontalAlignment]::Right)

$btnInstall = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Button])
$btnInstall.SetValue([System.Windows.Controls.Button]::ContentProperty, "Install")
$btnInstall.SetValue([System.Windows.Controls.Button]::MarginProperty, (New-Object System.Windows.Thickness(2)))
$btnInstall.SetBinding([System.Windows.Controls.Button]::TagProperty, (New-Object System.Windows.Data.Binding))
$spBtns.AppendChild($btnInstall)

$btnUninstall = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Button])
$btnUninstall.SetValue([System.Windows.Controls.Button]::ContentProperty, "Uninstall")
$btnUninstall.SetValue([System.Windows.Controls.Button]::MarginProperty, (New-Object System.Windows.Thickness(2)))
$btnUninstall.SetValue([System.Windows.Controls.Button]::ForegroundProperty, [System.Windows.Media.Brushes]::Red)
$btnUninstall.SetBinding([System.Windows.Controls.Button]::TagProperty, (New-Object System.Windows.Data.Binding))
$spBtns.AppendChild($btnUninstall)

$gridFactory.AppendChild($spBtns)
$borderFactory.AppendChild($gridFactory)
$dataTemplate.VisualTree = $borderFactory
$packageListUI.ItemTemplate = $dataTemplate

# Status Bar
$statusBar = New-Object System.Windows.Controls.Primitives.StatusBar
$statusBar.Background = [System.Windows.Media.Brushes]::Transparent
$statusBar.Margin = "0,10,0,0"
[System.Windows.Controls.Grid]::SetRow($statusBar, 3)
$mainGrid.Children.Add($statusBar)

$statusText = New-Object System.Windows.Controls.TextBlock
$statusText.Text = "Ready"
$statusText.Foreground = [System.Windows.Media.Brushes]::Gray
$statusItem = New-Object System.Windows.Controls.Primitives.StatusBarItem
$statusItem.Content = $statusText
$statusBar.Items.Add($statusItem)

# State
$global:packages = @()
$loadedData = Load-Packages
if ($loadedData) {
    foreach ($item in $loadedData) {
        $global:packages += [PSCustomObject]@{
            Name       = $item.Name
            ID         = $item.ID
            Source     = $item.Source
            IsSelected = $false
        }
    }
}
$packageListUI.ItemsSource = $global:packages

# Logic
function Execute-Action {
    param($Action, $Pkg)
    $confirm = [System.Windows.MessageBox]::Show("Are you sure you want to $Action $($Pkg.Name)?", "Confirm", "YesNo", "Question")
    if ($confirm -eq "Yes") {
        $statusText.Text = "Status: Processing $($Pkg.Name)..."
        $script = if ($Pkg.Source -eq "scoop") { "scoop $Action $($Pkg.ID)" } else { "winget $Action --id $($Pkg.ID) --silent" }
        Start-Process powershell -ArgumentList "-NoProfile -Command $script; pause" -Wait
        $statusText.Text = "Status: Finished $Action $($Pkg.Name)"
    }
}

# Events
$btnAdd.Add_Click({
    $name = [Microsoft.VisualBasic.Interaction]::InputBox("Enter App Name", "Add Package")
    if ([string]::IsNullOrWhiteSpace($name)) { return }
    $id = [Microsoft.VisualBasic.Interaction]::InputBox("Enter App ID", "Add Package")
    if ([string]::IsNullOrWhiteSpace($id)) { return }
    $source = [Microsoft.VisualBasic.Interaction]::InputBox("Enter Source (scoop/winget)", "Add Package", "winget")
    if ([string]::IsNullOrWhiteSpace($source)) { $source = "winget" }
    
    $newPkg = [PSCustomObject]@{ Name = $name; ID = $id; Source = $source; IsSelected = $false }
    $global:packages += $newPkg
    $packageListUI.ItemsSource = $null
    $packageListUI.ItemsSource = $global:packages
    $global:packages | Select-Object Name, ID, Source | Save-Packages
})

$selectAll.Add_Checked({ foreach ($p in $global:packages) { $p.IsSelected = $true }; $packageListUI.Items.Refresh() })
$selectAll.Add_Unchecked({ foreach ($p in $global:packages) { $p.IsSelected = $false }; $packageListUI.Items.Refresh() })

$btnInstallSelected.Add_Click({
    $selected = $global:packages | Where-Object { $_.IsSelected }
    if ($selected.Count -eq 0) { [System.Windows.MessageBox]::Show("No packages selected."); return }
    $statusText.Text = "Status: Installing selected packages..."
    foreach ($pkg in $selected) {
        $cmd = if ($pkg.Source -eq "scoop") { "scoop install $($pkg.ID)" } else { "winget install --id $($pkg.ID) --silent" }
        Start-Process powershell -ArgumentList "-NoProfile -Command $cmd" -Wait
    }
    $statusText.Text = "Status: Batch installation complete."
})

$packageListUI.Add_PreviewMouseLeftButtonUp({
    $source = $_.OriginalSource
    if ($source -is [System.Windows.Controls.Button]) {
        $pkg = $source.Tag
        if ($source.Content -eq "Install") { Execute-Action -Action "install" -Pkg $pkg }
        elseif ($source.Content -eq "Uninstall") { Execute-Action -Action "uninstall" -Pkg $pkg }
    }
})

$window.ShowDialog() | Out-Null
