# Required Assemblies
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, Microsoft.VisualBasic, System.Xml

# State Management
$jsonPath = Join-Path $PSScriptRoot "packages.json"
$global:allPackages = New-Object System.Collections.Generic.List[PSCustomObject]
$global:lastHoveredItem = $null

# Helper to create a standardized package object
function New-PackageObject {
    param($Name, $ID, $Source, $Category = "General")
    return [PSCustomObject]@{
        Name          = [string]$Name
        ID            = [string]$ID
        Source        = [string]$Source
        Category      = [string]$Category
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
                    $global:allPackages.Add((New-PackageObject -Name $item.Name -ID $item.ID -Source $item.Source -Category $item.Category))
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
                $cleanData += [PSCustomObject]@{ Name = $p.Name; ID = $p.ID; Source = $p.Source; Category = $p.Category }
            }
        }
        $json = $cleanData | ConvertTo-Json -Depth 10
        if ($cleanData.Count -eq 1 -and $json -notlike "[*") { $json = "[$json]" }
        [System.IO.File]::WriteAllText($jsonPath, $json)
    } catch { }
}

function Update-Categories {
    $script:suppressCatChange = $true
    $current = $cmbCategory.SelectedItem
    $categories = @("All") + ($global:allPackages.Category | Where-Object { $_ } | Select-Object -Unique | Sort-Object)
    $cmbCategory.Items.Clear()
    foreach ($cat in $categories) { [void]$cmbCategory.Items.Add($cat) }
    if ($cmbCategory.Items.Contains($current)) { $cmbCategory.SelectedItem = $current } else { $cmbCategory.SelectedIndex = 0 }
    $script:suppressCatChange = $false
}

function Update-List {
    $term = [string]$txtSearch.Text.ToLower().Trim()
    $selectedCat = [string]$cmbCategory.SelectedItem
    $filtered = [object[]]@($global:allPackages | Where-Object {
        ($null -eq $selectedCat -or $selectedCat -eq "All" -or $_.Category -eq $selectedCat) -and
        ($_.Name.ToLower().Contains($term) -or $_.ID.ToLower().Contains($term))
    } | Where-Object { $_ -ne $null } | Sort-Object Name)
    $script:pendingList = $filtered
    $packageListUI.Dispatcher.BeginInvoke([System.Windows.Threading.DispatcherPriority]::Loaded, [System.Windows.Threading.DispatcherOperationCallback]{ param($arg); $packageListUI.ItemsSource = $null; $packageListUI.ItemsSource = $script:pendingList; $null }, $null)
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
    $dlg.Width = 400; $dlg.Height = 280; $dlg.WindowStartupLocation = "CenterOwner"; $dlg.Owner = $window; $dlg.Background = [System.Windows.Media.Brushes]::White; $dlg.ResizeMode = "NoResize"
    $grid = New-Object System.Windows.Controls.Grid; $grid.Margin = "20"; $dlg.Content = $grid
    
    [void]$grid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=[System.Windows.GridLength]::Auto}))
    [void]$grid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition))
    
    for($i=0; $i -lt 5; $i++){ [void]$grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition -Property @{Height=[System.Windows.GridLength]::Auto})) }
    $grid.RowDefinitions[4].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)
    
    $lbl1 = New-Object System.Windows.Controls.TextBlock; $lbl1.Text = "Display Name:"; $lbl1.VerticalAlignment = "Center"; $lbl1.Margin = "0,0,15,15"; [System.Windows.Controls.Grid]::SetRow($lbl1, 0); [System.Windows.Controls.Grid]::SetColumn($lbl1, 0); [void]$grid.Children.Add($lbl1)
    $txtName = New-Object System.Windows.Controls.TextBox; $txtName.Padding = "5"; $txtName.Margin = "0,0,0,15"; if($ExistingPkg){ $txtName.Text = $ExistingPkg.Name }; [System.Windows.Controls.Grid]::SetRow($txtName, 0); [System.Windows.Controls.Grid]::SetColumn($txtName, 1); [void]$grid.Children.Add($txtName)
    
    $lbl2 = New-Object System.Windows.Controls.TextBlock; $lbl2.Text = "Package ID:"; $lbl2.VerticalAlignment = "Center"; $lbl2.Margin = "0,0,15,15"; [System.Windows.Controls.Grid]::SetRow($lbl2, 1); [System.Windows.Controls.Grid]::SetColumn($lbl2, 0); [void]$grid.Children.Add($lbl2)
    $txtID = New-Object System.Windows.Controls.TextBox; $txtID.Padding = "5"; $txtID.Margin = "0,0,0,15"; if($ExistingPkg){ $txtID.Text = $ExistingPkg.ID }; [System.Windows.Controls.Grid]::SetRow($txtID, 1); [System.Windows.Controls.Grid]::SetColumn($txtID, 1); [void]$grid.Children.Add($txtID)
    
    $lblCat = New-Object System.Windows.Controls.TextBlock; $lblCat.Text = "Category:"; $lblCat.VerticalAlignment = "Center"; $lblCat.Margin = "0,0,15,15"; [System.Windows.Controls.Grid]::SetRow($lblCat, 2); [System.Windows.Controls.Grid]::SetColumn($lblCat, 0); [void]$grid.Children.Add($lblCat)
    $cmbCat = New-Object System.Windows.Controls.ComboBox; $cmbCat.IsEditable = $true; $cmbCat.Padding = "5"; $cmbCat.Margin = "0,0,0,15"; $cmbCat.Text = if($ExistingPkg){ $ExistingPkg.Category } else { "General" }
    $categories = $global:allPackages.Category | Where-Object { $_ } | Select-Object -Unique | Sort-Object
    foreach ($cat in $categories) { [void]$cmbCat.Items.Add($cat) }
    [System.Windows.Controls.Grid]::SetRow($cmbCat, 2); [System.Windows.Controls.Grid]::SetColumn($cmbCat, 1); [void]$grid.Children.Add($cmbCat)
    
    $lbl3 = New-Object System.Windows.Controls.TextBlock; $lbl3.Text = "Source:"; $lbl3.VerticalAlignment = "Center"; $lbl3.Margin = "0,0,15,0"; [System.Windows.Controls.Grid]::SetRow($lbl3, 3); [System.Windows.Controls.Grid]::SetColumn($lbl3, 0); [void]$grid.Children.Add($lbl3)
    $cmbSource = New-Object System.Windows.Controls.ComboBox; $cmbSource.Width = 100; $cmbSource.Height = 25; $cmbSource.HorizontalAlignment = "Left"; [void]$cmbSource.Items.Add("winget"); [void]$cmbSource.Items.Add("scoop"); $cmbSource.SelectedItem = if($ExistingPkg){ $ExistingPkg.Source } else { "winget" }; [System.Windows.Controls.Grid]::SetRow($cmbSource, 3); [System.Windows.Controls.Grid]::SetColumn($cmbSource, 1); [void]$grid.Children.Add($cmbSource)
    
    $spBtns = New-Object System.Windows.Controls.StackPanel; $spBtns.Orientation = "Horizontal"; $spBtns.HorizontalAlignment = "Right"; $spBtns.VerticalAlignment = "Bottom"; [System.Windows.Controls.Grid]::SetRow($spBtns, 4); [System.Windows.Controls.Grid]::SetColumn($spBtns, 0); [System.Windows.Controls.Grid]::SetColumnSpan($spBtns, 2); [void]$grid.Children.Add($spBtns)
    $btnSave = New-Object System.Windows.Controls.Button; $btnSave.Content = "Save"; $btnSave.Width = 70; $btnSave.Height = 30; $btnSave.Margin = "0,0,10,0"; $btnSave.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253)); $btnSave.Foreground = [System.Windows.Media.Brushes]::White; [void]$spBtns.Children.Add($btnSave)
    $btnCancel = New-Object System.Windows.Controls.Button; $btnCancel.Content = "Cancel"; $btnCancel.Width = 70; $btnCancel.Height = 30; [void]$spBtns.Children.Add($btnCancel)
    
    $btnSave.Add_Click({ 
        if(-not [string]::IsNullOrWhiteSpace($txtName.Text) -and -not [string]::IsNullOrWhiteSpace($txtID.Text)){ 
            $script:dialogResult = New-PackageObject -Name $txtName.Text -ID $txtID.Text -Source $cmbSource.SelectedItem -Category $cmbCat.Text.Trim()
            $dlg.Close() 
        } 
    })
    $btnCancel.Add_Click({ $dlg.Close() })
    $script:dialogResult = $null; $dlg.ShowDialog() | Out-Null; return $script:dialogResult
}

# --- Main Window ---
$window = New-Object System.Windows.Window; $window.Title = "Package Manager Pro"; $window.Width = 650; $window.Height = 650; $window.Background = [System.Windows.Media.Brushes]::White; $window.WindowStartupLocation = "CenterScreen"
$mainGrid = New-Object System.Windows.Controls.Grid; $mainGrid.Margin = "15"; $window.Content = $mainGrid
for($i=0; $i -lt 3; $i++){ [void]$mainGrid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition)) }
$mainGrid.RowDefinitions[0].Height = [System.Windows.GridLength]::Auto
$mainGrid.RowDefinitions[1].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)
$mainGrid.RowDefinitions[2].Height = [System.Windows.GridLength]::Auto

$headerGrid = New-Object System.Windows.Controls.Grid; $headerGrid.Margin = "0,0,0,15"; [System.Windows.Controls.Grid]::SetRow($headerGrid, 0); [void]$mainGrid.Children.Add($headerGrid)
[void]$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Auto))}))
[void]$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star))}))
[void]$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Auto))}))

$leftStack = New-Object System.Windows.Controls.StackPanel; $leftStack.Orientation = "Horizontal"; $leftStack.Margin = "0,0,10,0"; [void]$headerGrid.Children.Add($leftStack)
$selectAll = New-Object System.Windows.Controls.CheckBox; $selectAll.Content = "All"; $selectAll.VerticalAlignment = "Center"; $selectAll.Margin = "5,0,10,0"; [void]$leftStack.Children.Add($selectAll)
$btnAdd = New-Object System.Windows.Controls.Button; $btnAdd.Content = "+"; $btnAdd.Width = 35; $btnAdd.Height = 35; $btnAdd.FontWeight = "Bold"; $btnAdd.FontSize = 18; $btnAdd.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13, 110, 253)); $btnAdd.Foreground = [System.Windows.Media.Brushes]::White; [void]$leftStack.Children.Add($btnAdd)

$txtSearch = New-Object System.Windows.Controls.TextBox; $txtSearch.Height = 35; $txtSearch.VerticalAlignment = "Center"; $txtSearch.Padding = "10,5"; $txtSearch.FontSize = 14; $txtSearch.VerticalContentAlignment = "Center"; $txtSearch.Margin = "10,0"; $txtSearch.ToolTip = "Search by Name or ID"; [System.Windows.Controls.Grid]::SetColumn($txtSearch, 1); [void]$headerGrid.Children.Add($txtSearch)

$rightStack = New-Object System.Windows.Controls.StackPanel; $rightStack.Orientation = "Horizontal"; $rightStack.HorizontalAlignment = "Right"; $rightStack.Margin = "10,0,0,0"; [System.Windows.Controls.Grid]::SetColumn($rightStack, 2); [void]$headerGrid.Children.Add($rightStack)

$cmbCategory = New-Object System.Windows.Controls.ComboBox; $cmbCategory.Width = 120; $cmbCategory.Height = 35; $cmbCategory.Margin = "0,0,10,0"; $cmbCategory.VerticalContentAlignment = "Center"; [void]$rightStack.Children.Add($cmbCategory)

$btnCheckStatus = New-Object System.Windows.Controls.Button; $btnCheckStatus.Content = "Check Status"; $btnCheckStatus.Padding = "10,5"; $btnCheckStatus.Margin = "0,0,10,0"; $btnCheckStatus.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(108, 117, 125)); $btnCheckStatus.Foreground = [System.Windows.Media.Brushes]::White; [void]$rightStack.Children.Add($btnCheckStatus)
$btnInstallSelected = New-Object System.Windows.Controls.Button; $btnInstallSelected.Content = "Install Selected"; $btnInstallSelected.Padding = "10,5"; $btnInstallSelected.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(25, 135, 84)); $btnInstallSelected.Foreground = [System.Windows.Media.Brushes]::White; [void]$rightStack.Children.Add($btnInstallSelected)

$packageListUI = New-Object System.Windows.Controls.ListView; $packageListUI.Background = [System.Windows.Media.Brushes]::White; [System.Windows.Controls.Grid]::SetRow($packageListUI, 1); [void]$mainGrid.Children.Add($packageListUI)

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
$spSub = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spSub.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal)
$txtS = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtS.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Source")); $txtS.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $txtS.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::DodgerBlue); $txtS.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::Bold); $spSub.AppendChild($txtS)
$txtSep = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtSep.SetValue([System.Windows.Controls.TextBlock]::TextProperty, " • "); $txtSep.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $txtSep.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::Silver); $spSub.AppendChild($txtSep)
$txtC = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $txtC.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Category")); $txtC.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $txtC.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::MediumPurple); $spSub.AppendChild($txtC)
$spInfo.AppendChild($spSub)
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

$statusBar = New-Object System.Windows.Controls.Primitives.StatusBar; $statusBar.Background = [System.Windows.Media.Brushes]::Transparent; $statusBar.Margin = "0,10,0,0"; [System.Windows.Controls.Grid]::SetRow($statusBar, 2); [void]$mainGrid.Children.Add($statusBar)
$statusText = New-Object System.Windows.Controls.TextBlock; $statusText.Text = "Ready"; $statusText.Foreground = [System.Windows.Media.Brushes]::Gray; $statusItem = New-Object System.Windows.Controls.Primitives.StatusBarItem; $statusItem.Content = $statusText; [void]$statusBar.Items.Add($statusItem)

# --- Events ---
Load-Packages; Update-Categories; Update-List
$txtSearch.Add_TextChanged({ Update-List })
$script:suppressCatChange = $false
$cmbCategory.Add_SelectionChanged({ if (-not $script:suppressCatChange) { Update-List } })
$btnAdd.Add_Click({ $res = Show-PackageDialog; if ($res) { $global:allPackages.Add($res); $txtSearch.Text = ""; Update-Categories; Update-List; Save-Packages } })
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
        if ($found) { $pkg.RowBackground = $installedColor; $pkg.Checkmark = " ✔️" } else { $pkg.RowBackground = [System.Windows.Media.Brushes]::Transparent; $pkg.Checkmark = "" }
    }
    Update-List; $window.Cursor = [System.Windows.Input.Cursors]::Arrow; $statusText.Text = "Scan complete."
})

$btnInstallSelected.Add_Click({
    $selected = @($global:allPackages | Where-Object { $_.IsSelected }); if ($selected.Count -eq 0) { [System.Windows.MessageBox]::Show("No apps selected."); return }
    $statusText.Text = "Installing selected..."; $window.UpdateLayout()
    foreach ($pkg in $selected) { $cmd = if ($pkg.Source -eq "scoop") { "scoop install $($pkg.ID)" } else { "winget install --id $($pkg.ID) --exact --silent" }; Start-Process powershell -ArgumentList "-NoProfile -Command $cmd" -Wait }
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
            "Install" { if ([System.Windows.MessageBox]::Show("Install $($pkg.Name)?", "Confirm", "YesNo") -eq "Yes") { $statusText.Text = "Installing..."; $window.UpdateLayout(); Start-Process powershell -ArgumentList "-NoProfile -Command $(if ($pkg.Source -eq 'scoop') { 'scoop install ' + $pkg.ID } else { 'winget install --id ' + $pkg.ID + ' --exact --silent' }); pause" -Wait -Verb RunAs; $statusText.Text = "Finished." } }
            "Uninstall" { if ([System.Windows.MessageBox]::Show("Uninstall $($pkg.Name)?", "Confirm", "YesNo") -eq "Yes") { $statusText.Text = "Uninstalling..."; $window.UpdateLayout(); Start-Process powershell -ArgumentList "-NoProfile -Command $(if ($pkg.Source -eq 'scoop') { 'scoop uninstall ' + $pkg.ID } else { 'winget uninstall --id ' + $pkg.ID + ' --exact --silent' }); pause" -Wait -Verb RunAs; $statusText.Text = "Finished." } }
            "Edit" { $res = Show-PackageDialog -ExistingPkg $pkg; if ($res -is [PSCustomObject]) { $pkg.Name = $res.Name; $pkg.ID = $res.ID; $pkg.Source = $res.Source; $pkg.Category = $res.Category; Update-Categories; Update-List; Save-Packages } }
            "Remove" { if ([System.Windows.MessageBox]::Show("Remove from list?", "Confirm", "YesNo") -eq "Yes") { [void]$global:allPackages.Remove($pkg); Update-Categories; Update-List; Save-Packages } }
        }
    }
})

$window.Add_Closing({ Save-Packages })
$window.ShowDialog() | Out-NullOut-NullullOut-Null