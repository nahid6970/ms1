# Required Assemblies
Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, Microsoft.VisualBasic, System.Xml

# State Management
$jsonPath = Join-Path $PSScriptRoot "packages.json"
$global:allPackages = New-Object System.Collections.Generic.List[PSCustomObject]
$global:lastHoveredItem = $null

# Helper to create a standardized package object
# Sources: array of @{Source; ID} for multi-source packages.
function New-PackageObject {
    param($Name, $ID, $Source, $Category = "General", $Sources = $null)
    $srcs = if ($Sources) { $Sources } else { @(@{Source=$Source; ID=$ID}) }
    $badge = ($srcs | ForEach-Object { if ($_.Source -eq "scoop") { "[S]" } else { "[W]" } }) -join "+"
    return [PSCustomObject]@{
        Name          = [string]$Name
        ID            = [string]($srcs[0].ID)
        Source        = [string]($srcs[0].Source)
        Sources       = $srcs
        SourceBadge   = $badge
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
            # Group by base name (strip [S]/[W] suffix) to merge duplicates
            $groups = @{}
            foreach ($item in @($data)) {
                if (-not ($item.Name -and $item.ID)) { continue }
                # If item already has Sources array, use it directly
                if ($item.Sources) {
                    $srcs = @($item.Sources | ForEach-Object { @{Source=[string]$_.Source; ID=[string]$_.ID} })
                    $global:allPackages.Add((New-PackageObject -Name $item.Name -ID $srcs[0].ID -Source $srcs[0].Source -Category $item.Category -Sources $srcs))
                    continue
                }
                # Legacy: detect [S]/[W] suffix and group by base name
                $baseName = $item.Name -replace '\s*\[(S|W)\]$', ''
                if (-not $groups.ContainsKey($baseName)) { $groups[$baseName] = @{Cat=$item.Category; Srcs=@()} }
                $groups[$baseName].Srcs += @{Source=[string]$item.Source; ID=[string]$item.ID}
            }
            foreach ($baseName in $groups.Keys) {
                $g = $groups[$baseName]
                $srcs = $g.Srcs
                $global:allPackages.Add((New-PackageObject -Name $baseName -ID $srcs[0].ID -Source $srcs[0].Source -Category $g.Cat -Sources $srcs))
            }
        } catch { }
    }
}

function Save-Packages {
    try {
        $cleanData = @()
        foreach ($p in $global:allPackages) {
            if ($p.Name -and $p.ID) {
                $cleanData += [PSCustomObject]@{ Name = $p.Name; ID = $p.ID; Source = $p.Source; Sources = $p.Sources; Category = $p.Category }
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

# Prompt user to pick a source when package has multiple sources
function Select-Source {
    param($pkg)
    if ($pkg.Sources.Count -le 1) { return $pkg.Sources[0] }
    $dlg = New-Object System.Windows.Window
    $dlg.Title = "Choose Source"; $dlg.Width = 280; $dlg.Height = 160
    $dlg.WindowStartupLocation = "CenterOwner"; $dlg.Owner = $window
    $dlg.Background = [System.Windows.Media.Brushes]::White; $dlg.ResizeMode = "NoResize"
    $sp = New-Object System.Windows.Controls.StackPanel; $sp.Margin = "20"; $dlg.Content = $sp
    $lbl = New-Object System.Windows.Controls.TextBlock
    $lbl.Text = "Install '$($pkg.Name)' via:"; $lbl.Margin = "0,0,0,12"; [void]$sp.Children.Add($lbl)
    $spBtns = New-Object System.Windows.Controls.StackPanel; $spBtns.Orientation = "Horizontal"; $spBtns.HorizontalAlignment = "Center"; [void]$sp.Children.Add($spBtns)
    $script:chosenSource = $null
    foreach ($src in $pkg.Sources) {
        $label = if ($src.Source -eq "scoop") { "Scoop" } else { "Winget" }
        $btn = New-Object System.Windows.Controls.Button; $btn.Content = $label; $btn.Width = 80; $btn.Height = 32; $btn.Margin = "5,0"
        $btn.Tag = $src
        $btn.Add_Click({ $script:chosenSource = $this.Tag; $dlg.Close() })
        [void]$spBtns.Children.Add($btn)
    }
    $dlg.ShowDialog() | Out-Null
    return $script:chosenSource
}

function Show-PackageDialog {
    param($ExistingPkg = $null)
    $dlg = New-Object System.Windows.Window
    $dlg.Title = if ($ExistingPkg) { "Edit Package" } else { "Add New Package" }
    $dlg.Width = 420; $dlg.Height = 340; $dlg.WindowStartupLocation = "CenterOwner"; $dlg.Owner = $window
    $dlg.Background = [System.Windows.Media.Brushes]::White; $dlg.ResizeMode = "NoResize"
    $grid = New-Object System.Windows.Controls.Grid; $grid.Margin = "20"; $dlg.Content = $grid

    [void]$grid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=[System.Windows.GridLength]::Auto}))
    [void]$grid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition))
    for ($i = 0; $i -lt 7; $i++) { [void]$grid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition -Property @{Height=[System.Windows.GridLength]::Auto})) }
    $grid.RowDefinitions[6].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)

    function Add-Row { param($row, $labelText, $ctrl)
        $lbl = New-Object System.Windows.Controls.TextBlock; $lbl.Text = $labelText; $lbl.VerticalAlignment = "Center"; $lbl.Margin = "0,0,15,10"
        [System.Windows.Controls.Grid]::SetRow($lbl, $row); [System.Windows.Controls.Grid]::SetColumn($lbl, 0); [void]$grid.Children.Add($lbl)
        $ctrl.Margin = "0,0,0,10"; [System.Windows.Controls.Grid]::SetRow($ctrl, $row); [System.Windows.Controls.Grid]::SetColumn($ctrl, 1); [void]$grid.Children.Add($ctrl)
    }

    $txtName = New-Object System.Windows.Controls.TextBox; $txtName.Padding = "5"
    if ($ExistingPkg) { $txtName.Text = $ExistingPkg.Name }
    Add-Row 0 "Display Name:" $txtName

    # Primary source row
    $spSrc1 = New-Object System.Windows.Controls.StackPanel; $spSrc1.Orientation = "Horizontal"
    $cmbSrc1 = New-Object System.Windows.Controls.ComboBox; $cmbSrc1.Width = 80; [void]$cmbSrc1.Items.Add("winget"); [void]$cmbSrc1.Items.Add("scoop")
    $cmbSrc1.SelectedItem = if ($ExistingPkg -and $ExistingPkg.Sources) { $ExistingPkg.Sources[0].Source } else { "winget" }
    $txtID1 = New-Object System.Windows.Controls.TextBox; $txtID1.Padding = "5"; $txtID1.Width = 200; $txtID1.Margin = "8,0,0,0"
    if ($ExistingPkg -and $ExistingPkg.Sources) { $txtID1.Text = $ExistingPkg.Sources[0].ID }
    [void]$spSrc1.Children.Add($cmbSrc1); [void]$spSrc1.Children.Add($txtID1)
    Add-Row 1 "Source 1 / ID:" $spSrc1

    # Secondary source row
    $spSrc2 = New-Object System.Windows.Controls.StackPanel; $spSrc2.Orientation = "Horizontal"
    $cmbSrc2 = New-Object System.Windows.Controls.ComboBox; $cmbSrc2.Width = 80; [void]$cmbSrc2.Items.Add("(none)"); [void]$cmbSrc2.Items.Add("winget"); [void]$cmbSrc2.Items.Add("scoop")
    $txtID2 = New-Object System.Windows.Controls.TextBox; $txtID2.Padding = "5"; $txtID2.Width = 200; $txtID2.Margin = "8,0,0,0"
    if ($ExistingPkg -and $ExistingPkg.Sources -and $ExistingPkg.Sources.Count -gt 1) {
        $cmbSrc2.SelectedItem = $ExistingPkg.Sources[1].Source; $txtID2.Text = $ExistingPkg.Sources[1].ID
    } else { $cmbSrc2.SelectedIndex = 0 }
    [void]$spSrc2.Children.Add($cmbSrc2); [void]$spSrc2.Children.Add($txtID2)
    Add-Row 2 "Source 2 / ID:" $spSrc2

    $lblCat = New-Object System.Windows.Controls.TextBlock; $lblCat.Text = "Category:"; $lblCat.VerticalAlignment = "Center"; $lblCat.Margin = "0,0,15,10"
    [System.Windows.Controls.Grid]::SetRow($lblCat, 3); [System.Windows.Controls.Grid]::SetColumn($lblCat, 0); [void]$grid.Children.Add($lblCat)
    $cmbCat = New-Object System.Windows.Controls.ComboBox; $cmbCat.IsEditable = $true; $cmbCat.Padding = "5"; $cmbCat.Margin = "0,0,0,10"
    $cmbCat.Text = if ($ExistingPkg) { $ExistingPkg.Category } else { "General" }
    $global:allPackages.Category | Where-Object { $_ } | Select-Object -Unique | Sort-Object | ForEach-Object { [void]$cmbCat.Items.Add($_) }
    [System.Windows.Controls.Grid]::SetRow($cmbCat, 3); [System.Windows.Controls.Grid]::SetColumn($cmbCat, 1); [void]$grid.Children.Add($cmbCat)

    $spBtns = New-Object System.Windows.Controls.StackPanel; $spBtns.Orientation = "Horizontal"; $spBtns.HorizontalAlignment = "Right"; $spBtns.VerticalAlignment = "Bottom"
    [System.Windows.Controls.Grid]::SetRow($spBtns, 6); [System.Windows.Controls.Grid]::SetColumnSpan($spBtns, 2); [void]$grid.Children.Add($spBtns)
    $btnSave = New-Object System.Windows.Controls.Button; $btnSave.Content = "Save"; $btnSave.Width = 70; $btnSave.Height = 30; $btnSave.Margin = "0,0,10,0"
    $btnSave.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13,110,253)); $btnSave.Foreground = [System.Windows.Media.Brushes]::White
    $btnCancel = New-Object System.Windows.Controls.Button; $btnCancel.Content = "Cancel"; $btnCancel.Width = 70; $btnCancel.Height = 30
    [void]$spBtns.Children.Add($btnSave); [void]$spBtns.Children.Add($btnCancel)

    $btnSave.Add_Click({
        if ([string]::IsNullOrWhiteSpace($txtName.Text) -or [string]::IsNullOrWhiteSpace($txtID1.Text)) { return }
        $srcs = @(@{Source=[string]$cmbSrc1.SelectedItem; ID=$txtID1.Text.Trim()})
        if ($cmbSrc2.SelectedItem -ne "(none)" -and -not [string]::IsNullOrWhiteSpace($txtID2.Text)) {
            $srcs += @{Source=[string]$cmbSrc2.SelectedItem; ID=$txtID2.Text.Trim()}
        }
        $script:dialogResult = New-PackageObject -Name $txtName.Text.Trim() -ID $srcs[0].ID -Source $srcs[0].Source -Category $cmbCat.Text.Trim() -Sources $srcs
        $dlg.Close()
    })
    $btnCancel.Add_Click({ $dlg.Close() })
    $script:dialogResult = $null; $dlg.ShowDialog() | Out-Null; return $script:dialogResult
}

# --- Main Window ---
$window = New-Object System.Windows.Window; $window.Title = "Package Manager Pro"; $window.Width = 650; $window.Height = 650; $window.Background = [System.Windows.Media.Brushes]::White; $window.WindowStartupLocation = "CenterScreen"
$mainGrid = New-Object System.Windows.Controls.Grid; $mainGrid.Margin = "15"; $window.Content = $mainGrid
for ($i = 0; $i -lt 3; $i++) { [void]$mainGrid.RowDefinitions.Add((New-Object System.Windows.Controls.RowDefinition)) }
$mainGrid.RowDefinitions[0].Height = [System.Windows.GridLength]::Auto
$mainGrid.RowDefinitions[1].Height = New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star)
$mainGrid.RowDefinitions[2].Height = [System.Windows.GridLength]::Auto

$headerGrid = New-Object System.Windows.Controls.Grid; $headerGrid.Margin = "0,0,0,15"; [System.Windows.Controls.Grid]::SetRow($headerGrid, 0); [void]$mainGrid.Children.Add($headerGrid)
[void]$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Auto))}))
[void]$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star))}))
[void]$headerGrid.ColumnDefinitions.Add((New-Object System.Windows.Controls.ColumnDefinition -Property @{Width=(New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Auto))}))

$leftStack = New-Object System.Windows.Controls.StackPanel; $leftStack.Orientation = "Horizontal"; $leftStack.Margin = "0,0,10,0"; [void]$headerGrid.Children.Add($leftStack)
$selectAll = New-Object System.Windows.Controls.CheckBox; $selectAll.Content = "All"; $selectAll.VerticalAlignment = "Center"; $selectAll.Margin = "5,0,10,0"; [void]$leftStack.Children.Add($selectAll)
$btnAdd = New-Object System.Windows.Controls.Button; $btnAdd.Content = "+"; $btnAdd.Width = 35; $btnAdd.Height = 35; $btnAdd.FontWeight = "Bold"; $btnAdd.FontSize = 18; $btnAdd.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(13,110,253)); $btnAdd.Foreground = [System.Windows.Media.Brushes]::White; [void]$leftStack.Children.Add($btnAdd)

$txtSearch = New-Object System.Windows.Controls.TextBox; $txtSearch.Height = 35; $txtSearch.VerticalAlignment = "Center"; $txtSearch.Padding = "10,5"; $txtSearch.FontSize = 14; $txtSearch.VerticalContentAlignment = "Center"; $txtSearch.Margin = "10,0"; $txtSearch.ToolTip = "Search by Name or ID"; [System.Windows.Controls.Grid]::SetColumn($txtSearch, 1); [void]$headerGrid.Children.Add($txtSearch)

$rightStack = New-Object System.Windows.Controls.StackPanel; $rightStack.Orientation = "Horizontal"; $rightStack.HorizontalAlignment = "Right"; $rightStack.Margin = "10,0,0,0"; [System.Windows.Controls.Grid]::SetColumn($rightStack, 2); [void]$headerGrid.Children.Add($rightStack)
$cmbCategory = New-Object System.Windows.Controls.ComboBox; $cmbCategory.Width = 120; $cmbCategory.Height = 35; $cmbCategory.Margin = "0,0,10,0"; $cmbCategory.VerticalContentAlignment = "Center"; [void]$rightStack.Children.Add($cmbCategory)
$btnCheckStatus = New-Object System.Windows.Controls.Button; $btnCheckStatus.Content = "Check Status"; $btnCheckStatus.Padding = "10,5"; $btnCheckStatus.Margin = "0,0,10,0"; $btnCheckStatus.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(108,117,125)); $btnCheckStatus.Foreground = [System.Windows.Media.Brushes]::White; [void]$rightStack.Children.Add($btnCheckStatus)
$btnInstallSelected = New-Object System.Windows.Controls.Button; $btnInstallSelected.Content = "Install Selected"; $btnInstallSelected.Padding = "10,5"; $btnInstallSelected.Background = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(25,135,84)); $btnInstallSelected.Foreground = [System.Windows.Media.Brushes]::White; [void]$rightStack.Children.Add($btnInstallSelected)

$packageListUI = New-Object System.Windows.Controls.ListView; $packageListUI.Background = [System.Windows.Media.Brushes]::White; [System.Windows.Controls.Grid]::SetRow($packageListUI, 1); [void]$mainGrid.Children.Add($packageListUI)

# --- DataTemplate ---
$dataTemplate = New-Object System.Windows.DataTemplate
$borderFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Border])
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0,0,0,1)))
$borderFactory.SetValue([System.Windows.Controls.Border]::BorderBrushProperty, (New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(241,243,245))))
$borderFactory.SetValue([System.Windows.Controls.Border]::PaddingProperty, (New-Object System.Windows.Thickness(5)))
$borderFactory.SetBinding([System.Windows.Controls.Border]::BackgroundProperty, (New-Object System.Windows.Data.Binding "RowBackground"))

$gridFactory = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Grid])
$gridFactory.SetValue([System.Windows.Controls.Grid]::WidthProperty, 510.0)
$c1 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition]); $c1.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(35))); $gridFactory.AppendChild($c1)
$c2 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition]); $c2.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(1, [System.Windows.GridUnitType]::Star))); $gridFactory.AppendChild($c2)
$c3 = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.ColumnDefinition]); $c3.SetValue([System.Windows.Controls.ColumnDefinition]::WidthProperty, (New-Object System.Windows.GridLength(150))); $gridFactory.AppendChild($c3)

$cb = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.CheckBox])
$cb.SetBinding([System.Windows.Controls.CheckBox]::IsCheckedProperty, (New-Object System.Windows.Data.Binding "IsSelected"))
$cb.SetValue([System.Windows.Controls.CheckBox]::VerticalAlignmentProperty, [System.Windows.VerticalAlignment]::Center)
$gridFactory.AppendChild($cb)

$spInfo = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spInfo.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 1)
$spName = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spName.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal)
$tfName = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $tfName.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Name")); $tfName.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::SemiBold); $tfName.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 14.0); $spName.AppendChild($tfName)
$tfCheck = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $tfCheck.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Checkmark")); $tfCheck.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::SeaGreen); $tfCheck.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::Bold); $tfCheck.SetValue([System.Windows.Controls.TextBlock]::MarginProperty, (New-Object System.Windows.Thickness(5,0,0,0))); $spName.AppendChild($tfCheck)
$spInfo.AppendChild($spName)
$tfID = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $tfID.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "ID")); $tfID.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 11.0); $tfID.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::Gray); $spInfo.AppendChild($tfID)

# Sub-line: SourceBadge • Category
$spSub = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spSub.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal)
$tfBadge = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $tfBadge.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "SourceBadge")); $tfBadge.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $tfBadge.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::DodgerBlue); $tfBadge.SetValue([System.Windows.Controls.TextBlock]::FontWeightProperty, [System.Windows.FontWeights]::Bold); $spSub.AppendChild($tfBadge)
$tfSep = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $tfSep.SetValue([System.Windows.Controls.TextBlock]::TextProperty, " • "); $tfSep.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $tfSep.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::Silver); $spSub.AppendChild($tfSep)
$tfCat = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.TextBlock]); $tfCat.SetBinding([System.Windows.Controls.TextBlock]::TextProperty, (New-Object System.Windows.Data.Binding "Category")); $tfCat.SetValue([System.Windows.Controls.TextBlock]::FontSizeProperty, 10.0); $tfCat.SetValue([System.Windows.Controls.TextBlock]::ForegroundProperty, [System.Windows.Media.Brushes]::MediumPurple); $spSub.AppendChild($tfCat)
$spInfo.AppendChild($spSub)
$gridFactory.AppendChild($spInfo)

function Create-IconButton {
    param($PathStr, $Color, $Tip)
    $btn = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Button]); $btn.SetValue([System.Windows.Controls.Button]::WidthProperty, 28.0); $btn.SetValue([System.Windows.Controls.Button]::HeightProperty, 28.0); $btn.SetValue([System.Windows.Controls.Button]::MarginProperty, (New-Object System.Windows.Thickness(2))); $btn.SetValue([System.Windows.Controls.Button]::ToolTipProperty, $Tip); $btn.SetValue([System.Windows.Controls.Button]::BackgroundProperty, [System.Windows.Media.Brushes]::Transparent); $btn.SetValue([System.Windows.Controls.Button]::BorderThicknessProperty, (New-Object System.Windows.Thickness(0))); $btn.SetBinding([System.Windows.Controls.Button]::TagProperty, (New-Object System.Windows.Data.Binding)); $btn.SetValue([System.Windows.Controls.Button]::OpacityProperty, 0.0)
    $vb = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.Viewbox]); $vb.SetValue([System.Windows.Controls.Viewbox]::WidthProperty, 16.0); $p = New-Object System.Windows.FrameworkElementFactory([System.Windows.Shapes.Path]); $p.SetValue([System.Windows.Shapes.Path]::DataProperty, [System.Windows.Media.Geometry]::Parse($PathStr)); $p.SetValue([System.Windows.Shapes.Path]::FillProperty, $Color); $vb.AppendChild($p); $btn.AppendChild($vb); return $btn
}

$spRowBtns = New-Object System.Windows.FrameworkElementFactory([System.Windows.Controls.StackPanel]); $spRowBtns.SetValue([System.Windows.Controls.StackPanel]::OrientationProperty, [System.Windows.Controls.Orientation]::Horizontal); $spRowBtns.SetValue([System.Windows.Controls.Grid]::ColumnProperty, 2); $spRowBtns.SetValue([System.Windows.Controls.StackPanel]::HorizontalAlignmentProperty, [System.Windows.HorizontalAlignment]::Right)
$spRowBtns.AppendChild((Create-IconButton "M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z" ([System.Windows.Media.Brushes]::SeaGreen) "Install"))
$spRowBtns.AppendChild((Create-IconButton "M13 3c-4.97 0-9 4.03-9 9H1l3.89 3.89.07.14L9 12H6c0-3.87 3.13-7 7-7s7 3.13 7 7-3.13 7-7 7c-1.93 0-3.68-.79-4.94-2.06l-1.42 1.42C8.27 19.99 10.51 21 13 21c4.97 0 9-4.03 9-9s-4.03-9-9-9zm-1 5v5l4.28 2.54.72-1.21-3.5-2.08V8H12z" ([System.Windows.Media.Brushes]::Crimson) "Uninstall"))
$spRowBtns.AppendChild((Create-IconButton "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" ([System.Windows.Media.Brushes]::DodgerBlue) "Edit"))
$spRowBtns.AppendChild((Create-IconButton "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" ([System.Windows.Media.Brushes]::Crimson) "Remove"))
$gridFactory.AppendChild($spRowBtns); $borderFactory.AppendChild($gridFactory); $dataTemplate.VisualTree = $borderFactory; $packageListUI.ItemTemplate = $dataTemplate

$statusBar = New-Object System.Windows.Controls.Primitives.StatusBar; $statusBar.Background = [System.Windows.Media.Brushes]::Transparent; $statusBar.Margin = "0,10,0,0"; [System.Windows.Controls.Grid]::SetRow($statusBar, 2); [void]$mainGrid.Children.Add($statusBar)
$statusText = New-Object System.Windows.Controls.TextBlock; $statusText.Text = "Ready"; $statusText.Foreground = [System.Windows.Media.Brushes]::Gray
$statusItem = New-Object System.Windows.Controls.Primitives.StatusBarItem; $statusItem.Content = $statusText; [void]$statusBar.Items.Add($statusItem)

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
    $installedColor = New-Object System.Windows.Media.SolidColorBrush([System.Windows.Media.Color]::FromRgb(232,245,233))
    $scoopNames = @(); try { $scoopNames = (scoop export 2>$null | ConvertFrom-Json).apps.Name } catch {}
    $wingetList = (winget list --source winget 2>$null) -join " "
    foreach ($pkg in $global:allPackages) {
        $found = $false
        foreach ($src in $pkg.Sources) {
            if ($src.Source -eq "scoop") { if ($scoopNames -contains $src.ID) { $found = $true; break } }
            else { if ($wingetList -like "*$($src.ID)*") { $found = $true; break } }
        }
        if ($found) { $pkg.RowBackground = $installedColor; $pkg.Checkmark = " ✔️" }
        else { $pkg.RowBackground = [System.Windows.Media.Brushes]::Transparent; $pkg.Checkmark = "" }
    }
    Update-List; $window.Cursor = [System.Windows.Input.Cursors]::Arrow; $statusText.Text = "Scan complete."
})

$btnInstallSelected.Add_Click({
    $selected = @($global:allPackages | Where-Object { $_.IsSelected })
    if ($selected.Count -eq 0) { [System.Windows.MessageBox]::Show("No apps selected."); return }
    $statusText.Text = "Installing selected..."; $window.UpdateLayout()
    foreach ($pkg in $selected) {
        $src = Select-Source $pkg
        if (-not $src) { continue }
        $cmd = if ($src.Source -eq "scoop") { "scoop install $($src.ID)" } else { "winget install --id $($src.ID) --exact --silent" }
        Start-Process powershell -ArgumentList "-NoProfile -Command $cmd" -Wait
    }
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
            "Install" {
                $src = Select-Source $pkg
                if ($src -and [System.Windows.MessageBox]::Show("Install $($pkg.Name) via $($src.Source)?", "Confirm", "YesNo") -eq "Yes") {
                    $statusText.Text = "Installing..."; $window.UpdateLayout()
                    $cmd = if ($src.Source -eq "scoop") { "scoop install $($src.ID)" } else { "winget install --id $($src.ID) --exact --silent" }
                    Start-Process powershell -ArgumentList "-NoProfile -Command $cmd; pause" -Wait -Verb RunAs
                    $statusText.Text = "Finished."
                }
            }
            "Uninstall" {
                $src = Select-Source $pkg
                if ($src -and [System.Windows.MessageBox]::Show("Uninstall $($pkg.Name) via $($src.Source)?", "Confirm", "YesNo") -eq "Yes") {
                    $statusText.Text = "Uninstalling..."; $window.UpdateLayout()
                    $cmd = if ($src.Source -eq "scoop") { "scoop uninstall $($src.ID)" } else { "winget uninstall --id $($src.ID) --exact --silent" }
                    Start-Process powershell -ArgumentList "-NoProfile -Command $cmd; pause" -Wait -Verb RunAs
                    $statusText.Text = "Finished."
                }
            }
            "Edit" {
                $res = Show-PackageDialog -ExistingPkg $pkg
                if ($res -is [PSCustomObject]) {
                    $pkg.Name = $res.Name; $pkg.ID = $res.ID; $pkg.Source = $res.Source
                    $pkg.Sources = $res.Sources; $pkg.SourceBadge = $res.SourceBadge; $pkg.Category = $res.Category
                    Update-Categories; Update-List; Save-Packages
                }
            }
            "Remove" {
                if ([System.Windows.MessageBox]::Show("Remove from list?", "Confirm", "YesNo") -eq "Yes") {
                    [void]$global:allPackages.Remove($pkg); Update-Categories; Update-List; Save-Packages
                }
            }
        }
    }
})

$window.Add_Closing({ Save-Packages })
$window.ShowDialog() | Out-Null
