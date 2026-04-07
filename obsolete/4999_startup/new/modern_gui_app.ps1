Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName PresentationCore
Add-Type -AssemblyName WindowsBase
Add-Type -AssemblyName System.Xaml

$xaml = @'
<Window
    xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
    x:Name="Window"
    Title="My Modern PowerShell GUI App"
    Width="400"
    Height="300"
    Background="#2e2e2e">
    <Window.Resources>
        <Style TargetType="Button">
            <Setter Property="Background" Value="#505050" />
            <Setter Property="Foreground" Value="White" />
            <Setter Property="BorderBrush" Value="#707070" />
            <Setter Property="BorderThickness" Value="1" />
            <Setter Property="FontFamily" Value="Segoe UI" />
            <Setter Property="FontSize" Value="14" />
            <Setter Property="Template">
                <Setter.Value>
                    <ControlTemplate TargetType="Button">
                        <Border Background="{TemplateBinding Background}"
                                BorderBrush="{TemplateBinding BorderBrush}"
                                BorderThickness="{TemplateBinding BorderThickness}"
                                CornerRadius="5">
                            <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center" />
                        </Border>
                    </ControlTemplate>
                </Setter.Value>
            </Setter>
        </Style>
        <Style TargetType="TextBox">
            <Setter Property="Background" Value="#3a3a3a" />
            <Setter Property="Foreground" Value="White" />
            <Setter Property="BorderBrush" Value="#707070" />
            <Setter Property="BorderThickness" Value="1" />
            <Setter Property="FontFamily" Value="Segoe UI" />
            <Setter Property="FontSize" Value="12" />
            <Setter Property="Padding" Value="5,0,0,0" />
            <Setter Property="Template">
                <Setter.Value>
                    <ControlTemplate TargetType="TextBox">
                        <Border Background="{TemplateBinding Background}"
                                BorderBrush="{TemplateBinding BorderBrush}"
                                BorderThickness="{TemplateBinding BorderThickness}"
                                CornerRadius="5">
                            <ScrollViewer x:Name="PART_ContentHost" />
                        </Border>
                    </ControlTemplate>
                </Setter.Value>
            </Setter>
        </Style>
    </Window.Resources>
    <Grid Margin="10">
        <Grid.RowDefinitions>
            <RowDefinition Height="Auto" />
            <RowDefinition Height="*" />
            <RowDefinition Height="Auto" />
        </Grid.RowDefinitions>
        <StackPanel Grid.Row="0" Orientation="Horizontal" Margin="0,0,0,10">
            <TextBox x:Name="AppNameTextBox"
                     Width="150"
                     Height="25"
                     VerticalAlignment="Center"
                     Margin="0,0,10,0"
                     ToolTip="Application Name" />
            <TextBox x:Name="AppPathTextBox"
                     Width="200"
                     Height="25"
                     VerticalAlignment="Center"
                     Margin="0,0,10,0"
                     ToolTip="Application Path (e.g., C:\path\to\app.exe)" />
            <Button x:Name="BrowseButton"
                    Content="Browse..."
                    Width="80"
                    Height="25"
                    VerticalAlignment="Center"
                    Margin="0,0,10,0" />
            <Button x:Name="AddButton"
                    Content="Add App"
                    Width="80"
                    Height="25"
                    VerticalAlignment="Center" />
        </StackPanel>
        <ListBox x:Name="AutoStartListBox"
                 Grid.Row="1"
                 Margin="0,0,0,10"
                 Background="#3a3a3a"
                 Foreground="White"
                 BorderBrush="#707070"
                 BorderThickness="1"
                 FontFamily="Segoe UI"
                 FontSize="12" />
        <Button x:Name="RemoveButton"
                Grid.Row="2"
                Content="Remove Selected"
                Width="120"
                Height="30"
                HorizontalAlignment="Left" />
    </Grid>
</Window>
'@

# Load XAML
[xml]$xamlContent = $xaml
$reader = (New-Object System.Xml.XmlNodeReader $xamlContent)
$Window = [Windows.Markup.XamlReader]::Load($reader)

#region Functions for Auto-Start Management

function Get-AutoStartApps {
    $autoStartApps = @()

    # Registry Run keys
    $RunKeys = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    )
    foreach ($key in $RunKeys) {
        if (Test-Path $key) {
            Get-ItemProperty -Path $key | Select-Object -Skip 1 | ForEach-Object {
                $propertyName = $_.PSObject.Properties | Where-Object { $_.Name -ne "PSPath" -and $_.Name -ne "PSParentPath" -and $_.Name -ne "PSChildName" -and $_.Name -ne "PSDrive" -and $_.Name -ne "PSProvider" } | Select-Object -ExpandProperty Name
                foreach ($name in $propertyName) {
                    $autoStartApps += [PSCustomObject]@{
                        Name = $name
                        Path = $_.$name
                        Source = $key
                    }
                }
            }
        }
    }

    # Startup folder
    $StartupFolders = @(
        "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
        "$env:ALLUSERSPROFILE\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    foreach ($folder in $StartupFolders) {
        if (Test-Path $folder) {
            Get-ChildItem -Path $folder -File | ForEach-Object {
                $autoStartApps += [PSCustomObject]@{
                    Name = $_.BaseName
                    Path = $_.FullName
                    Source = $folder
                }
            }
        }
    }
    return $autoStartApps
}

function Add-AutoStartApp {
    param (
        [string]$Name,
        [string]$Path
    )
    if (-not (Test-Path (Split-Path $Path))) {
        [System.Windows.Forms.MessageBox]::Show("Error: Application path does not exist.", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return $false
    }
    try {
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name $Name -Value $Path -Force
        [System.Windows.Forms.MessageBox]::Show("Application '$Name' added to auto-start.", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
        return $true
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show("Error adding application to auto-start: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return $false
    }
}

function Remove-AutoStartApp {
    param (
        [string]$Name,
        [string]$Source
    )
    try {
        if ($Source -like "HKCU:*") {
            Remove-ItemProperty -Path $Source -Name $Name -ErrorAction Stop
            [System.Windows.Forms.MessageBox]::Show("Application '$Name' removed from auto-start (Registry).", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
            return $true
        }
        elseif ($Source -like "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup*") {
            Remove-Item -Path (Join-Path $Source "$Name*") -Force -Recurse -ErrorAction Stop
            [System.Windows.Forms.MessageBox]::Show("Application '$Name' removed from auto-start (Startup Folder).", "Success", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
            return $true
        }
        else {
            [System.Windows.Forms.MessageBox]::Show("Unsupported auto-start source: $Source", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
            return $false
        }
    }
    catch {
        [System.Windows.Forms.MessageBox]::Show("Error removing application from auto-start: $($_.Exception.Message)", "Error", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
        return $false
    }
}
#endregion

# Get UI elements
$AppNameTextBox = $Window.FindName("AppNameTextBox")
$AppPathTextBox = $Window.FindName("AppPathTextBox")
$BrowseButton = $Window.FindName("BrowseButton")
$AddButton = $Window.FindName("AddButton")
$AutoStartListBox = $Window.FindName("AutoStartListBox")
$RemoveButton = $Window.FindName("RemoveButton")

# Populate initial list
$AutoStartListBox.ItemsSource = (Get-AutoStartApps | Sort-Object Name)

# Add event handlers
$BrowseButton.Add_Click({
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    $openFileDialog.Filter = "Executable Files (*.exe)|*.exe|All Files (*.*)|*.*"
    if ($openFileDialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
        $AppPathTextBox.Text = $openFileDialog.FileName
        $AppNameTextBox.Text = [System.IO.Path]::GetFileNameWithoutExtension($openFileDialog.FileName)
    }
})

$AddButton.Add_Click({
    $appName = $AppNameTextBox.Text
    $appPath = $AppPathTextBox.Text

    if ([string]::IsNullOrWhiteSpace($appName) -or [string]::IsNullOrWhiteSpace($appPath)) {
        [System.Windows.Forms.MessageBox]::Show("Please provide both application name and path.", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }

    if (Add-AutoStartApp -Name $appName -Path $appPath) {
        $AutoStartListBox.ItemsSource = (Get-AutoStartApps | Sort-Object Name)
        $AppNameTextBox.Clear()
        $AppPathTextBox.Clear()
    }
})

$RemoveButton.Add_Click({
    $selectedApp = $AutoStartListBox.SelectedItem
    if (-not $selectedApp) {
        [System.Windows.Forms.MessageBox]::Show("Please select an application to remove.", "Warning", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)
        return
    }

    if ([System.Windows.Forms.MessageBox]::Show("Are you sure you want to remove '$($selectedApp.Name)'?", "Confirm Removal", [System.Windows.Forms.MessageBoxButtons]::YesNo, [System.Windows.Forms.MessageBoxIcon]::Question) -eq [System.Windows.Forms.DialogResult]::Yes) {
        if (Remove-AutoStartApp -Name $selectedApp.Name -Source $selectedApp.Source) {
            $AutoStartListBox.ItemsSource = (Get-AutoStartApps | Sort-Object Name)
        }
    }
})

# Show the window
$Window.ShowDialog()
