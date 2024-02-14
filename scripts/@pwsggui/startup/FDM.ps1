$Startup_LabelPanel = New-Object Windows.Controls.StackPanel
$Startup_LabelPanel.Orientation = [Windows.Controls.Orientation]::Horizontal
$Startup_LabelPanel.HorizontalAlignment = [Windows.HorizontalAlignment]::Center

$Startup_Label = & $csLabel -content "FDM"
$Startup_CheckBox = New-Object Windows.Controls.CheckBox
$Startup_CheckBox.Content = ""
# Set vertical alignment and margin for checkbox
$Startup_CheckBox.VerticalAlignment = [Windows.VerticalAlignment]::Center
$Startup_CheckBox.Margin = New-Object Windows.Thickness(5, 0, 0, 0)
$Startup_LabelPanel.Children.Add($Startup_Label)
$Startup_LabelPanel.Children.Add($Startup_CheckBox)
$StartupApps_Panel.Children.Add($Startup_LabelPanel)
$Startup_CheckBox.IsChecked = [System.IO.File]::Exists([System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\Startup', 'fdm.lnk'))
# Add an event handler for the checkbox
$Startup_CheckBox.Add_Checked({
$shortcutPath = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\Startup', 'fdm.lnk')

if (-not (Test-Path $shortcutPath)) {
$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "C:\Users\nahid\scoop\apps\freedownloadmanager\current\fdm.exe"
$shortcut.Save() } })

$Startup_CheckBox.Add_Unchecked({
$shortcutPath = [System.IO.Path]::Combine($env:APPDATA, 'Microsoft\Windows\Start Menu\Programs\Startup', 'fdm.lnk')
if (Test-Path $shortcutPath) { Remove-Item $shortcutPath } })