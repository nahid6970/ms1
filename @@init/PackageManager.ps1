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

# --- Custom Add/Edit Dialog Function ---
function Show-PackageDialog {
    param($ExistingPkg = $null)
    
    $dlg = New-Object System.Windows.Window
    $dlg.Title = if ($ExistingPkg) { "Edit Package" } else { "Add New Package" }
    $dlg.Width = 350; $dlg.Height = 350
    $dlg.WindowStartupLocation = "CenterOwner"
    $dlg.Owner = $window
    $dlg.Background = [System.Windows.Media.Brushes]::White
    $dlg.ResizeMode = "NoResize"

    $grid = New-Object System.Windows.Controls.Grid; $grid.Margin = "20"
    $dlg.Content = $grid
    for($i=0; $i -lt 5; $i++){ $grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition)) }
    $grid.RowDefinitions[4].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)

    # Name
    $lbl1 = New-Object System.Windows.Controls.TextBlock; $lbl1.Text = "Display Name:"; $lbl1.Margin = "0,0,0,5"
    [System.Windows.Controls.Grid]::SetRow($lbl1, 0); $grid.Children.Add($lbl1)
    $txtName = New-Object System.Windows.Controls.TextBox; $txtName.Margin = "0,0,0,15"; $txtName.Padding = "5"
    if($ExistingPkg){ $txtName.Text = $ExistingPkg.Name }
    [System.Windows.Controls.Grid]::SetRow($txtName, 1); $grid.Children.Add($txtName)

    # ID
    $lbl2 = New-Object System.Windows.Controls.TextBlock; $lbl2.Text = "Package ID (e.g. git):"; $lbl2.Margin = "0,0,0,5"
    [System.Windows.Controls.Grid]::SetRow($lbl2, 2); $grid.Children.Add($lbl2)
    $txtID = New-Object System.Windows.Controls.TextBox; $txtID.Margin = "0,0,0,15"; $txtID.Padding = "5"
    if($ExistingPkg){ $txtID.Text = $ExistingPkg.ID }
    [System.Windows.Controls.Grid]::SetRow($txtID, 3); $grid.Children.Add($txtID)

    # Source (Dropdown)
    $spSource = New-Object System.Windows.Controls.StackPanel; $spSource.Orientation = "Horizontal"; $spSource.Margin = "0,0,0,20"
    [System.Windows.Controls.Grid]::SetRow($spSource, 4); $grid.Children.Add($spSource)
    $lbl3 = New-Object System.Windows.Controls.TextBlock; $lbl3.Text = "Source:"; $lbl3.VerticalAlignment = "Center"; $lbl3.Margin = "0,0,10,0"
    $spSource.Children.Add($lbl3)
    $cmbSource = New-Object System.Windows.Controls.ComboBox; $cmbSource.Width = 100; $cmbSource.Height = 25
    [void]$cmbSource.Items.Add("winget"); [void]$cmbSource.Items.Add("scoop")
    $cmbSource.SelectedItem = if($ExistingPkg){ $ExistingPkg.Source } else { "winget" }
    $spSource.Children.Add($cmbSource)

    # Buttons
    $spBtns = New-Object System.Windows.Controls.StackPanel; $spBtns.Orientation = "Horizontal"; $spBtns.HorizontalAlignment = "Right"; $spBtns.VerticalAlignment = "Bottom"
    [System.Windows.Controls.Grid]::SetRow($spBtns, 4); $grid.Children.Add($spBtns)
    
    $btnSave = New-Object System.Windows.Controls.Button; $btnSave.Content = "Save"; $btnSave.Width = 70; $btnSave.Height = 30; $btnSave.Margin = "0,0,10,0"
    $btnSave.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253)); $btnSave.Foreground = [System.Windows.Media.Brushes]::White
    $spBtns.Children.Add($btnSave)
    
    $btnCancel = New-Object System.Windows.Controls.Button; $btnCancel.Content = "Cancel"; $btnCancel.Width = 70; $btnCancel.Height = 30
    $spBtns.Children.Add($btnCancel)

    $btnSave.Add_Click({
        if($txtName.Text -and $txtID.Text){
            $script:dialogResult = [PSCustomObject]@{ Name = $txtName.Text; ID = $txtID.Text; Source = $cmbSource.SelectedItem; IsSelected = $false }
            $dlg.Close()
        }
    })
    $btnCancel.Add_Click({ $dlg.Close() })

    $script:dialogResult = $null
    $dlg.ShowDialog() | Out-Null
    return $script:dialogResult
}

# --- Main Window Setup ---
$window = New-Object System.Windows.Window
$window.Title = "Package Manager Pro"
$window.Width = 520; $window.Height = 650
$window.Background = [System.Windows.Media.Brushes]::White
$window.WindowStartupLocation = "CenterScreen"

$mainGrid = New-Object System.Windows.Controls.Grid; $mainGrid.Margin = "15"
$window.Content = $mainGrid
for($i=0; $i -lt 4; $i++){ $mainGrid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition)) }
$mainGrid.RowDefinitions[0].Height = [System.Windows.GridLength]::Auto
$mainGrid.RowDefinitions[1].Height = [System.Windows.GridLength]::Auto
$mainGrid.RowDefinitions[2].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)
$mainGrid.RowDefinitions[3].Height = [System.Windows.GridLength]::Auto

# Title
$title = New-Object System.Windows.Controls.TextBlock; $title.Text = "App Manager"; $title.FontSize = 26; $title.FontWeight = "Bold"; $title.Margin = "0,0,0,15"
[System.Windows.Controls.Grid]::SetRow($title, 0); $mainGrid.Children.Add($title)

# Header
$headerStack = New-Object System.Windows.Controls.StackPanel; $headerStack.Orientation = "Horizontal"; $headerStack.Margin = "0,0,0,15"
[System.Windows.Controls.Grid]::SetRow($headerStack, 1); $mainGrid.Children.Add($headerStack)

$selectAll = New-Object System.Windows.Controls.CheckBox; $selectAll.Content = "Select All"; $selectAll.VerticalAlignment = "Center"; $selectAll.Margin = "5,0,20,0"
$headerStack.Children.Add($selectAll)

$btnAdd = New-Object System.Windows.Controls.Button; $btnAdd.Content = "+"; $btnAdd.Width = 35; $btnAdd.Height = 35; $btnAdd.FontWeight = "Bold"; $btnAdd.FontSize = 18
$btnAdd.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253)); $btnAdd.Foreground = [System.Windows.Media.Brushes]::White
$headerStack.Children.Add($btnAdd)

$btnInstallSelected = New-Object System.Windows.Controls.Button; $btnInstallSelected.Content = "Install Selected"; $btnInstallSelected.Margin = "15,0,0,0"; $btnInstallSelected.Padding = "15,5"
$btnInstallSelected.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(25, 135, 84)); $btnInstallSelected.Foreground = [System.Windows.Media.Brushes]::White
$headerStack.Children.Add($btnInstallSelected)

# Package List
$packageListUI = New-Object System.Windows.Controls.ListView; $packageListUI.Background = [System.Windows.Media.Brushes]::White
[System.Windows.Controls.Grid]::SetRow($packageListUI, 2); $mainGrid.Children.Add($packageListUI)

# --- Programmatic DataTemplate ---
$dataTemplate = New-Object System.Windows.DataTemplate
$borderFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Border])
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0,0,0,1)))
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderBrushProperty, (New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(241, 243, 245))))
$borderFactory.SetValue([System.Windows.Controls.Border]::PaddingProperty, (New-Object System.Windows.Thickness(5)))

$gridFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Grid])
$gridFactory.SetValue([System.Windows.Controls.Grid]::WidthProperty, 450.0)

$c1 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition])
$c1.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(35)))
$gridFactory.AppendChild($c1)

$c2 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition])
$c2.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)))
$gridFactory.AppendChild($c2)

$c3 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition])
$c3.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(150)))
$gridFactory.AppendChild($c3)

# Checkbox
$cb = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.CheckBox])
$cb.SetBinding([System.Windows.Controls.CheckBox]::IsCheckedProperty, (New-Object System.Windows.Data.Binding "IsSelected"))
$cb.SetValue([System.Windows.Controls.CheckBox]::VerticalAlignmentProperty, [System.Windows.VerticalAlignment]::Center)
$gridFactory.AppendChild($cb)

# Info
$spInfo = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spInfo.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 1)
$txtName = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock])
$txtName.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Name"))
$txtName.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::SemiBold); $txtName.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 14.0)
$spInfo.AppendChild($txtName)
$txtID = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock])
$txtID.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "ID"))
$txtID.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 11.0); $txtID.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::Gray)
$spInfo.AppendChild($txtID)
$txtSource = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock])
$txtSource.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Source"))
$txtSource.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $txtSource.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::DodgerBlue); $txtSource.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::Bold)
$spInfo.AppendChild($txtSource)
$gridFactory.AppendChild($spInfo)

# Icons Helper
function Create-IconButton {
    param($PathStr, $Color, $Tip)
    $btn = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Button])
    $btn.SetValue([System.Windows.Controls.Button]::WidthProperty, 28.0); $btn.SetValue([System.Windows.Controls.Button]::HeightProperty, 28.0)
    $btn.SetValue([System.Windows.Controls.Button]::MarginProperty, (New-Object System.Windows.Thickness(2))); $btn.SetValue([System.Windows.Controls.Button]::ToolTipProperty, $Tip)
    $btn.SetValue([System.Windows.Controls.Button]::BackgroundProperty, [System.Windows.Media.Brushes]::Transparent); $btn.SetValue([System.Windows.Controls.Button]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0)))
    $btn.SetBinding([System.Windows.Controls.Button]::TagProperty, (New-Object System.Windows.Data.Binding))
    
    $vb = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Viewbox]); $vb.SetValue([System.Windows.Controls.Viewbox]::WidthProperty, 16.0)
    $p = New-Object System.Windows.FrameworkElementFactory([System.Windows.Shapes.Path])
    $p.SetValue([System.Windows.Shapes.Path]::DataProperty, [System.Windows.Media.Geometry]::Parse($PathStr))
    $p.SetValue([System.Windows.Shapes.Path]::FillProperty, $Color)
    $vb.AppendChild($p); $btn.AppendChild($vb)
    return $btn
}

$spBtns = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spBtns.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal)
$spBtns.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 2); $spBtns.SetValue([System.Windows.Controls.StackPanel]::HorizontalAlignmentProperty, [System.Windows.HorizontalAlignment]::Right)

$spBtns.AppendChild((Create-IconButton "M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" ([System.Windows.Media.Brushes]::SeaGreen) "Install"))
$spBtns.AppendChild((Create-IconButton "M5 4v2h14V4H5zm0 10h4v6h6v-6h4l-7-7-7 7z" ([System.Windows.Media.Brushes]::OrangeRed) "Uninstall"))
$spBtns.AppendChild((Create-IconButton "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" ([System.Windows.Media.Brushes]::DodgerBlue) "Edit"))
$spBtns.AppendChild((Create-IconButton "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" ([System.Windows.Media.Brushes]::Crimson) "Remove"))

$gridFactory.AppendChild($spBtns); $borderFactory.AppendChild($gridFactory); $dataTemplate.VisualTree = $borderFactory
$packageListUI.ItemTemplate = $dataTemplate

# Status
$statusBar = New-Object System.Windows.Controls.Primitives.StatusBar; $statusBar.Background = [System.Windows.Media.Brushes]::Transparent; $statusBar.Margin = "0,10,0,0"
[System.Windows.Controls.Grid]::SetRow($statusBar, 3); $mainGrid.Children.Add($statusBar)
$statusText = New-Object System.Windows.Controls.TextBlock; $statusText.Text = "Ready"; $statusText.Foreground = [System.Windows.Media.Brushes]::Gray
$statusItem = New-Object System.Windows.Controls.Primitives.StatusBarItem; $statusItem.Content = $statusText; $statusBar.Items.Add($statusItem)

# Data
$global:packages = @()
$loadedData = Load-Packages
if ($loadedData) { foreach ($item in $loadedData) { $global:packages += [PSCustomObject]@{ Name=$item.Name; ID=$item.ID; Source=$item.Source; IsSelected=$false } } }
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
    $res = Show-PackageDialog
    if($res){
        $global:packages += $res
        $packageListUI.ItemsSource = $null; $packageListUI.ItemsSource = $global:packages
        $global:packages | Select-Object Name, ID, Source | Save-Packages
    }
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
    $target = $source
    while ($target -ne $null -and $target -isnot [System.Windows.Controls.Button]) { $target = [System.Windows.Media.VisualTreeHelper]::GetParent($target) }

    if ($target -is [System.Windows.Controls.Button] -and $target.ToolTip -ne $null) {
        $pkg = $target.Tag
        switch ($target.ToolTip) {
            "Install" { Execute-Action -Action "install" -Pkg $pkg }
            "Uninstall" { Execute-Action -Action "uninstall" -Pkg $pkg }
            "Edit" {
                $res = Show-PackageDialog -ExistingPkg $pkg
                if($res){
                    $pkg.Name = $res.Name; $pkg.ID = $res.ID; $pkg.Source = $res.Source
                    $packageListUI.Items.Refresh()
                    $global:packages | Select-Object Name, ID, Source | Save-Packages
                }
            }
            "Remove" {
                if([System.Windows.MessageBox]::Show("Remove $($pkg.Name) from list?", "Confirm", "YesNo", "Warning") -eq "Yes"){
                    $global:packages = $global:packages | Where-Object { $_ -ne $pkg }
                    $packageListUI.ItemsSource = $null; $packageListUI.ItemsSource = $global:packages
                    $global:packages | Select-Object Name, ID, Source | Save-Packages
                }
            }
        }
    }
})

$window.ShowDialog() | Out-Null
