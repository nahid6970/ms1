Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$notifyIcon = New-Object System.Windows.Forms.NotifyIcon
$notifyIcon.Icon = [System.Drawing.SystemIcons]::Information
$notifyIcon.Visible = $true
$notifyIcon.BalloonTipTitle = "Codex"
$notifyIcon.BalloonTipText = "Task Completed Successfully"
$notifyIcon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
$notifyIcon.ShowBalloonTip(3000)

Start-Sleep -Seconds 4

$notifyIcon.Visible = $false
$notifyIcon.Dispose()
