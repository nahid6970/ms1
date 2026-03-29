# Required Assemblies
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, Microsoft.VisualBasic, System.Xml

# State Management
$jsonPath = Join-Path $PSScriptRoot "packages.json"
$global:allPackages = New-Object System.Collections.Generic.List[PSCustomObject]
$global:lastHoveredItem = $null

# Helper to create a standardized package object
function New-PackageObject {
    param($Name, $ID, $Source)
    return [PSCustomObject]@{
        Name          = [string]$Name
        ID            = [string]$ID
        Source        = [string]$Source
        IsSelected    = $false
        RowBackground = [System.Windows.Media.Brushes]::Transparent
        Checkmark     = ""
    }
}

function Load-Packages {
    if (Test-Path $jsonPath) {
        try {
            $content = Get-Content $jsonPath -Raw
            if ([string]::IsNullOrWhiteSpace($content)) { return }
            $data = $content | ConvertFrom-Json
            $global:allPackages.Clear()
            foreach ($item in @($data)) {
                if ($item.Name -and $item.ID) {
                    $global:allPackages.Add((New-PackageObject -Name $item.Name -ID $item.ID -Source $item.Source))
                }
            }
        } catch { }
    }
}

function Save-Packages {
    try {
        $cleanData = @()
        foreach($p in $global:allPackages) {
            if ($p.Name -and $p.ID) {
                $cleanData += [PSCustomObject]@{ Name = $p.Name; ID = $p.ID; Source = $p.Source }
            }
        }
        $json = $cleanData | ConvertTo-Json -Depth 10
        if ($cleanData.Count -eq 1 -and $json -notlike "[*") { $json = "[$json]" }
        [System.IO.File]::WriteAllText($jsonPath, $json)
    } catch { }
}

function Update-List {
    $term = [string]$txtSearch.Text.ToLower().Trim()
    $packageListUI.ItemsSource = $null
    
    if ([string]::IsNullOrWhiteSpace($term)) {
        $packageListUI.ItemsSource = $global:allPackages.ToArray()
    } else {
        $filtered = $global:allPackages | Where-Object { 
            $_.Name.ToLower().Contains($term) -or $_.ID.ToLower().Contains($term) 
        }
        $packageListUI.ItemsSource = @($filtered)
    }
}

function Set-RowButtonsVisibility {
    param($ItemContainer, $Opacity)
    if ($null -eq $ItemContainer) { return }
    $queue = New-Object System.Collections.Generic.Queue[System.Windows.DependencyObject]
    $queue.Enqueue($ItemContainer)
    while ($queue.Count -gt 0) {
        $parent = $queue.Dequeue()
        for ($i = 0; $i -lt [System.Windows.Media.VisualTreeHelper]::GetChildrenCount($parent); $i++) {
            $child = [System.Windows.Media.VisualTreeHelper]::GetChild($parent, $i)
            if ($child -is [System.Windows.Controls.Button] -and $child.ToolTip) { $child.Opacity = $Opacity }
            $queue.Enqueue($child)
        }
    }
}

function Show-PackageDialog {
    param($ExistingPkg = $null)
    $dlg = New-Object System.Windows.Window
    $dlg.Title = if ($ExistingPkg) { "Edit Package" } else { "Add New Package" }
    $dlg.Width = 350; $dlg.Height = 350; $dlg.WindowStartupLocation = "CenterOwner"; $dlg.Owner = $window; $dlg.Background = [System.Windows.Media.Brushes]::White; $dlg.ResizeMode = "NoResize"
    $grid = New-Object System.Windows.Controls.Grid; $grid.Margin = "20"; $dlg.Content = $grid
    for($i=0; $i -lt 5; $i++){ $grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition)) }
    $grid.RowDefinitions[4].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)
    
    $lbl1 = New-Object System.Windows.Controls.TextBlock; $lbl1.Text = "Display Name:"; [System.Windows.Controls.Grid]::SetRow($lbl1, 0); $grid.Children.Add($lbl1)
    $txtName = New-Object System.Windows.Controls.TextBox; $txtName.Margin = "0,5,0,15"; $txtName.Padding = "5"; if($ExistingPkg){ $txtName.Text = $ExistingPkg.Name }; [System.Windows.Controls.Grid]::SetRow($txtName, 1); $grid.Children.Add($txtName)
    
    $lbl2 = New-Object System.Windows.Controls.TextBlock; $lbl2.Text = "Package ID:"; [System.Windows.Controls.Grid]::SetRow($lbl2, 2); $grid.Children.Add($lbl2)
    $txtID = New-Object System.Windows.Controls.TextBox; $txtID.Margin = "0,5,0,15"; $txtID.Padding = "5"; if($ExistingPkg){ $txtID.Text = $ExistingPkg.ID }; [System.Windows.Controls.Grid]::SetRow($txtID, 3); $grid.Children.Add($txtID)
    
    $spSource = New-Object System.Windows.Controls.StackPanel; $spSource.Orientation = "Horizontal"; [System.Windows.Controls.Grid]::SetRow($spSource, 4); $grid.Children.Add($spSource)
    $cmbSource = New-Object System.Windows.Controls.ComboBox; $cmbSource.Width = 100; $cmbSource.Height = 25; [void]$cmbSource.Items.Add("winget"); [void]$cmbSource.Items.Add("scoop"); $cmbSource.SelectedItem = if($ExistingPkg){ $ExistingPkg.Source } else { "winget" }; $spSource.Children.Add($cmbSource)
    
    $spBtns = New-Object System.Windows.Controls.StackPanel; $spBtns.Orientation = "Horizontal"; $spBtns.HorizontalAlignment = "Right"; $spBtns.VerticalAlignment = "Bottom"; [System.Windows.Controls.Grid]::SetRow($spBtns, 4); $grid.Children.Add($spBtns)
    $btnSave = New-Object System.Windows.Controls.Button; $btnSave.Content = "Save"; $btnSave.Width = 70; $btnSave.Height = 30; $btnSave.Margin = "0,0,10,0"; $btnSave.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253)); $btnSave.Foreground = [System.Windows.Media.Brushes]::White; $spBtns.Children.Add($btnSave)
    $btnCancel = New-Object System.Windows.Controls.Button; $btnCancel.Content = "Cancel"; $btnCancel.Width = 70; $btnCancel.Height = 30; $spBtns.Children.Add($btnCancel)
    
    $btnSave.Add_Click({ 
        if(-not [string]::IsNullOrWhiteSpace($txtName.Text) -and -not [string]::IsNullOrWhiteSpace($txtID.Text)){ 
            $script:dialogResult = New-PackageObject -Name $txtName.Text -ID $txtID.Text -Source $cmbSource.SelectedItem
            $dlg.Close() 
        } 
    })
    $btnCancel.Add_Click({ $dlg.Close() })
    $script:dialogResult = $null; $dlg.ShowDialog() | Out-Null; return $script:dialogResult
}

# --- Main Window ---
$window = New-Object System.Windows.Window; $window.Title = "Package Manager Pro"; $window.Width = 580; $window.Height = 650; $window.Background = [System.Windows.Media.Brushes]::White; $window.WindowStartupLocation = "CenterScreen"
$mainGrid = New-Object System.Windows.Controls.Grid; $mainGrid.Margin = "15"; $window.Content = $mainGrid
for($i=0; $i -lt 3; $i++){ $mainGrid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition)) }
$mainGrid.RowDefinitions[0].Height = [System.Windows.GridLength]::Auto
$mainGrid.RowDefinitions[1].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)
$mainGrid.RowDefinitions[2].Height = [System.Windows.GridLength]::Auto

$headerGrid = New-Object System.Windows.Controls.Grid; $headerGrid.Margin = "0,0,0,15"; [System.Windows.Controls.Grid]::SetRow($headerGrid, 0); $mainGrid.Children.Add($headerGrid)
$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Auto))}))
$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star))}))
$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Auto))}))

$leftStack = New-Object System.Windows.Controls.StackPanel; $leftStack.Orientation = "Horizontal"; $leftStack.Margin = "0,0,10,0"; $headerGrid.Children.Add($leftStack)
$selectAll = New-Object System.Windows.Controls.CheckBox; $selectAll.Content = "All"; $selectAll.VerticalAlignment = "Center"; $selectAll.Margin = "5,0,10,0"; $leftStack.Children.Add($selectAll)
$btnAdd = New-Object System.Windows.Controls.Button; $btnAdd.Content = "+"; $btnAdd.Width = 35; $btnAdd.Height = 35; $btnAdd.FontWeight = "Bold"; $btnAdd.FontSize = 18; $btnAdd.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253)); $btnAdd.Foreground = [System.Windows.Media.Brushes]::White; $leftStack.Children.Add($btnAdd)

$txtSearch = New-Object System.Windows.Controls.TextBox; $txtSearch.Height = 35; $txtSearch.VerticalAlignment = "Center"; $txtSearch.Padding = "10,5"; $txtSearch.FontSize = 14; $txtSearch.VerticalContentAlignment = "Center"; $txtSearch.Margin = "10,0"; $txtSearch.ToolTip = "Search by Name or ID"; [System.Windows.Controls.Grid]::SetColumn($txtSearch, 1); $headerGrid.Children.Add($txtSearch)

$rightStack = New-Object System.Windows.Controls.StackPanel; $rightStack.Orientation = "Horizontal"; $rightStack.HorizontalAlignment = "Right"; $rightStack.Margin = "10,0,0,0"; [System.Windows.Controls.Grid]::SetColumn($rightStack, 2); $headerGrid.Children.Add($rightStack)
$btnCheckStatus = New-Object System.Windows.Controls.Button; $btnCheckStatus.Content = "Check Status"; $btnCheckStatus.Padding = "10,5"; $btnCheckStatus.Margin = "0,0,10,0"; $btnCheckStatus.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(108, 117, 125)); $btnCheckStatus.Foreground = [System.Windows.Media.Brushes]::White; $rightStack.Children.Add($btnCheckStatus)
$btnInstallSelected = New-Object System.Windows.Controls.Button; $btnInstallSelected.Content = "Install Selected"; $btnInstallSelected.Padding = "10,5"; $btnInstallSelected.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(25, 135, 84)); $btnInstallSelected.Foreground = [System.Windows.Media.Brushes]::White; $rightStack.Children.Add($btnInstallSelected)

$packageListUI = New-Object System.Windows.Controls.ListView; $packageListUI.Background = [System.Windows.Media.Brushes]::White; [System.Windows.Controls.Grid]::SetRow($packageListUI, 1); $mainGrid.Children.Add($packageListUI)

# --- DataTemplate ---
$dataTemplate = New-Object System.Windows.DataTemplate
$borderFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Border])
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0,0,0,1))); $borderFactory.SetValue([System.Windows.Controls.Border]::BorderBrushProperty, (New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(241, 243, 245)))); $borderFactory.SetValue([System.Windows.Controls.Border]::PaddingProperty, (New-Object System.Windows.Thickness(5)))
$borderFactory.SetBinding([System.Windows.Controls.Border]::BackgroundProperty, (New-Object System.Windows.Data.Binding "RowBackground"))

$gridFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Grid]); $gridFactory.SetValue([System.Windows.Controls.Grid]::WidthProperty, 510.0)
$c1 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition]); $c1.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(35))); $gridFactory.AppendChild($c1)
$c2 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition]); $c2.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star))); $gridFactory.AppendChild($c2)
$c3 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition]); $c3.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(150))); $gridFactory.AppendChild($c3)
$cb = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.CheckBox]); $cb.SetBinding([System.Windows.Controls.CheckBox]::IsCheckedProperty, (New-Object System.Windows.Data.Binding "IsSelected")); $cb.SetValue([System.Windows.Controls.CheckBox]::VerticalAlignmentProperty, [System.Windows.VerticalAlignment]::Center); $gridFactory.AppendChild($cb)

$spInfo = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spInfo.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 1)
$spName = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spName.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal)
$txtName = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtName.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Name")); $txtName.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::SemiBold); $txtName.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 14.0); $spName.AppendChild($txtName)
$txtCheck = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtCheck.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Checkmark")); $txtCheck.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::SeaGreen); $txtCheck.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::Bold); $txtCheck.SetValue([System.Windows.Controls.TextBlock]::MarginProperty, (New-Object System.Windows.Thickness(5,0,0,0))); $spName.AppendChild($txtCheck)
$spInfo.AppendChild($spName)
$txtID = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtID.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "ID")); $txtID.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 11.0); $txtID.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::Gray); $spInfo.AppendChild($txtID)
$txtS = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtS.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Source")); $txtS.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $txtS.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::DodgerBlue); $txtS.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::Bold); $spInfo.AppendChild($txtS)
$gridFactory.AppendChild($spInfo)

function Create-IconButton {
    param($PathStr, $Color, $Tip)
    $btn = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Button]); $btn.SetValue([System.Windows.Controls.Button]::WidthProperty, 28.0); $btn.SetValue([System.Windows.Controls.Button]::HeightProperty, 28.0); $btn.SetValue([System.Windows.Controls.Button]::MarginProperty, (New-Object System.Windows.Thickness(2))); $btn.SetValue([System.Windows.Controls.Button]::ToolTipProperty, $Tip); $btn.SetValue([System.Windows.Controls.Button]::BackgroundProperty, [System.Windows.Media.Brushes]::Transparent); $btn.SetValue([System.Windows.Controls.Button]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0))); $btn.SetBinding([System.Windows.Controls.Button]::TagProperty, (New-Object System.Windows.Data.Binding)); $btn.SetValue([System.Windows.Controls.Button]::OpacityProperty, 0.0)
    $vb = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Viewbox]); $vb.SetValue([System.Windows.Controls.Viewbox]::WidthProperty, 16.0); $p = New-Object System.Windows.FrameworkElementFactory([System.Windows.Shapes.Path]); $p.SetValue([System.Windows.Shapes.Path]::DataProperty, [System.Windows.Media.Geometry]::Parse($PathStr)); $p.SetValue([System.Windows.Shapes.Path]::FillProperty, $Color); $vb.AppendChild($p); $btn.AppendChild($vb); return $btn
}

$spBtns = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spBtns.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal); $spBtns.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 2); $spBtns.SetValue([System.Windows.Controls.StackPanel]::HorizontalAlignmentProperty, [System.Windows.HorizontalAlignment]::Right)
$spBtns.AppendChild((Create-IconButton "M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" ([System.Windows.Media.Brushes]::SeaGreen) "Install"))
$spBtns.AppendChild((Create-IconButton "M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" ([System.Windows.Media.Brushes]::Crimson) "Uninstall"))
$spBtns.AppendChild((Create-IconButton "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" ([System.Windows.Media.Brushes]::DodgerBlue) "Edit"))
$spBtns.AppendChild((Create-IconButton "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" ([System.Windows.Media.Brushes]::Crimson) "Remove"))
$gridFactory.AppendChild($spBtns); $borderFactory.AppendChild($gridFactory); $dataTemplate.VisualTree = $borderFactory; $packageListUI.ItemTemplate = $dataTemplate

$statusBar = New-Object System.Windows.Controls.Primitives.StatusBar; $statusBar.Background = [System.Windows.Media.Brushes]::Transparent; $statusBar.Margin = "0,10,0,0"; [System.Windows.Controls.Grid]::SetRow($statusBar, 2); $mainGrid.Children.Add($statusBar)
$statusText = New-Object System.Windows.Controls.TextBlock; $statusText.Text = "Ready"; $statusText.Foreground = [System.Windows.Media.Brushes]::Gray; $statusItem = New-Object System.Windows.Controls.Primitives.StatusBarItem; $statusItem.Content = $statusText; $statusBar.Items.Add($statusItem)

# --- Events ---
Load-Packages; Update-List
$txtSearch.Add_TextChanged({ Update-List })
$btnAdd.Add_Click({ $res = Show-PackageDialog; if ($res) { $global:allPackages.Add($res); $txtSearch.Text = ""; Update-List; Save-Packages } })
$selectAll.Add_Checked({ foreach ($p in $packageListUI.ItemsSource) { $p.IsSelected = $true }; $packageListUI.Items.Refresh() })
$selectAll.Add_Unchecked({ foreach ($p in $packageListUI.ItemsSource) { $p.IsSelected = $false }; $packageListUI.Items.Refresh() })

$btnCheckStatus.Add_Click({
    $window.Cursor = [System.Windows.Input.Cursors]::Wait; $statusText.Text = "Scanning..."; $window.UpdateLayout()
    $installedColor = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(232, 245, 233))
    $scoopNames = @(); try { $scoopNames = (scoop export 2>$null | ConvertFrom-Json).apps.Name } catch {}
    $scoopList = (scoop list) -join " "
    $wingetList = (winget list --source winget) -join " "
    
    foreach ($pkg in $global:allPackages) {
        $found = if ($pkg.Source -eq "scoop") { $scoopNames -contains $pkg.ID } else { $wingetList -like "*$($pkg.ID)*" }
        if ($found) { $pkg.RowBackground = $installedColor; $pkg.Checkmark = " ✓" } else { $pkg.RowBackground = [System.Windows.Media.Brushes]::Transparent; $pkg.Checkmark = "" }
    }
    Update-List; $window.Cursor = [System.Windows.Input.Cursors]::Arrow; $statusText.Text = "Scan complete."
})

$btnInstallSelected.Add_Click({
    $selected = @($global:allPackages | Where-Object { $_.IsSelected }); if ($selected.Count -eq 0) { [System.Windows.MessageBox]::Show("No apps selected."); return }
    $statusText.Text = "Installing selected..."; $window.UpdateLayout()
    foreach ($pkg in $selected) { $cmd = if ($pkg.Source -eq "scoop") { "scoop install $($pkg.ID)" } else { "winget install --id $($pkg.ID) --silent" }; Start-Process powershell -ArgumentList "-NoProfile -Command $cmd" -Wait }
    $statusText.Text = "Batch installation complete."; Update-List
})

$packageListUI.Add_MouseMove({
    $target = $_.OriginalSource
    while ($target -ne $null -and $target -isnot [System.Windows.Controls.ListViewItem]) { $target = [System.Windows.Media.VisualTreeHelper]::GetParent($target) }
    if ($target -is [System.Windows.Controls.ListViewItem]) {
        if ($target -ne $global:lastHoveredItem) { Set-RowButtonsVisibility -ItemContainer $global:lastHoveredItem -Opacity 0.0; Set-RowButtonsVisibility -ItemContainer $target -Opacity 1.0; $global:lastHoveredItem = $target }
    } else { Set-RowButtonsVisibility -ItemContainer $global:lastHoveredItem -Opacity 0.0; $global:lastHoveredItem = $null }
})
$packageListUI.Add_MouseLeave({ Set-RowButtonsVisibility -ItemContainer $global:lastHoveredItem -Opacity 0.0; $global:lastHoveredItem = $null })

$packageListUI.Add_PreviewMouseLeftButtonUp({
    $target = $_.OriginalSource
    while ($target -ne $null -and $target -isnot [System.Windows.Controls.Button]) { $target = [System.Windows.Media.VisualTreeHelper]::GetParent($target) }
    if ($target -is [System.Windows.Controls.Button] -and $target.ToolTip) {
        $pkg = $target.Tag
        switch ($target.ToolTip) {
            "Install" { if ([System.Windows.MessageBox]::Show("Install $($pkg.Name)?", "Confirm", "YesNo") -eq "Yes") { $statusText.Text = "Installing..."; $window.UpdateLayout(); Start-Process powershell -ArgumentList "-NoProfile -Command $(if ($pkg.Source -eq 'scoop') { 'scoop install ' + $pkg.ID } else { 'winget install --id ' + $pkg.ID + ' --silent' }); pause" -Wait; $statusText.Text = "Finished." } }
            "Uninstall" { if ([System.Windows.MessageBox]::Show("Uninstall $($pkg.Name)?", "Confirm", "YesNo") -eq "Yes") { $statusText.Text = "Uninstalling..."; $window.UpdateLayout(); Start-Process powershell -ArgumentList "-NoProfile -Command $(if ($pkg.Source -eq 'scoop') { 'scoop uninstall ' + $pkg.ID } else { 'winget uninstall --id ' + $pkg.ID + ' --silent' }); pause" -Wait; $statusText.Text = "Finished." } }
            "Edit" { $res = Show-PackageDialog -ExistingPkg $pkg; if ($res) { $pkg.Name = $res.Name; $pkg.ID = $res.ID; $pkg.Source = $res.Source; Update-List; Save-Packages } }
            "Remove" { if ([System.Windows.MessageBox]::Show("Remove from list?", "Confirm", "YesNo") -eq "Yes") { [void]$global:allPackages.Remove($pkg); Update-List; Save-Packages } }
        }
    }
})

$window.Add_Closing({ Save-Packages })
$window.ShowDialog() | Out-Null