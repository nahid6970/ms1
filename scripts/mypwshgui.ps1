function req {
param (
[string]$content,
[scriptblock[]]$styles,
[scriptblock]$onClick
)
$label = New-Object Windows.Controls.Label
$label.Content = $content
$styles | ForEach-Object { & $_ $label }
$label.Add_MouseLeftButtonDown($onClick)
return $label
}

$csLabel = {
param(
[string]$content
)
$label = New-Object Windows.Controls.Label
$label.Content = $content
$label.FontSize = 20
$label.Margin = New-Object Windows.Thickness(0, 5, 0, 0)
$label.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::FromRgb(0, 0, 0))
$label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(111, 237, 139))
$label.Width = 250
$label.FontWeight = 'Bold'
$label.FontStyle = "Normal"
$label.HorizontalContentAlignment = [Windows.HorizontalAlignment]::Center
return $label
}

#$sdsf = { param ( [Windows.Controls.Button]$button ) $button.Effect = New-Object Windows.Media.Effects.DropShadowEffect }
#$ssd = { param ( [Windows.Controls.Button]$button ) $button.Effect.ShadowDepth = 5 }
#$seb = { param ( [Windows.Controls.Button]$button ) $button.Effect.BlurRadius = 100 }
#$sed = { param ( [Windows.Controls.Button]$button ) $button.Effect.Direction = 45 }
#$sec = { param ( [Windows.Controls.Button]$button ) $button.Effect.Color = [Windows.Media.Color]::FromArgb(255, 255, 0, 0) }
#$sop = { param ( [Windows.Controls.Button]$button ) $button.Effect.Opacity = 1.0 }


$hand = { param ( [Windows.Controls.Button]$button ) $button.Cursor = [Windows.Input.Cursors]::Hand }

$ff01 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Agency FB")}
$ff02 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Candara")}
$ff03 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Cascadia Code PL Nerd Font")}
$ff04 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Consolas")}
$ff05 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Courier New")}
$ff06 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("DejaVu Sans Mono Nerd Font")}
$ff07 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("FiraCode Nerd Font")}
$ff08 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Hack Nerd Font")}
$ff09 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Inconsolata Nerd Font")}
$ff10 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("JetBrainsMono Nerd Font")}
$ff11 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Lucida Console")}
$ff12 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Meslo Nerd Font")}
$ff13 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Mononoki Nerd Font")}
$ff14 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Palatino Linotype")}
$ff15 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Segoe UI")}
$ff16 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Source Code Pro Nerd Font")}
$ff17 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("SpaceMono Nerd Font")}
$ff18 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Trebuchet MS")}
$ff19 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Arial")}
$ff20 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Calibri")}
$ff21 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Comic Sans MS")}
$ff22 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Georgia")}
$ff23 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Helvetica")}
$ff24 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Tahoma")}
$ff25 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Times New Roman")}
$ff26 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Verdana")}
$ff27 = { param ( [Windows.Controls.Label]$Label ) $label.FontFamily = New-Object Windows.Media.FontFamily("Victoria")}

# Font Bold/Normal/Italic
$i = { param ( [Windows.Controls.Button]$button ) $button.FontStyle = "Italic" }
$b = { param ( [Windows.Controls.Label]$label ) $label.FontWeight = 'Bold' }

# Font Size

$fz16 = { param ( [Windows.Controls.Label]$label ) $label.FontSize = 16 }

# Color Related
# Font Background Color
$bg00 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0) )}
$bg01 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(255, 255, 255) )}
$bg02 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(16, 124, 65))}
$bg03 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 71, 171) )}
$bg04 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(255, 224, 135) )}
$bg05 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(237, 72, 87) )}
$bg06 = { param ( [Windows.Controls.Label]$label ) $label.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(112, 203, 242))}

# Font Foreground Color
$fg00= { param ( [Windows.Controls.Label]$label ) $label.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0) )}
$fg01= { param ( [Windows.Controls.Label]$label ) $label.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(255, 255, 255) )}

# Thickness color
$br = { param ( [Windows.Controls.Button]$button ) $button.BorderBrush = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0) )}

#Width
$w025 = { param ( [Windows.Controls.Label]$label ) $label.Width = 25 }
$w050 = { param ( [Windows.Controls.Label]$label ) $label.Width = 50 }
$w060 = { param ( [Windows.Controls.Label]$label ) $label.Width = 60 }
$w070 = { param ( [Windows.Controls.Label]$label ) $label.Width = 70 }
$w080 = { param ( [Windows.Controls.Label]$label ) $label.Width = 80 }
$w090 = { param ( [Windows.Controls.Label]$label ) $label.Width = 90 }
$w100 = { param ( [Windows.Controls.Label]$label ) $label.Width = 100 }
$w110 = { param ( [Windows.Controls.Label]$label ) $label.Width = 110 }
$w120 = { param ( [Windows.Controls.Label]$label ) $label.Width = 120 }
$w130 = { param ( [Windows.Controls.Label]$label ) $label.Width = 130 }
$w140 = { param ( [Windows.Controls.Label]$label ) $label.Width = 140 }
$w150 = { param ( [Windows.Controls.Label]$label ) $label.Width = 150 }
$w160 = { param ( [Windows.Controls.Label]$label ) $label.Width = 160 }
$w170 = { param ( [Windows.Controls.Label]$label ) $label.Width = 170 }
$w180 = { param ( [Windows.Controls.Label]$label ) $label.Width = 180 }
$w190 = { param ( [Windows.Controls.Label]$label ) $label.Width = 190 }
$w200 = { param ( [Windows.Controls.Label]$label ) $label.Width = 200 }
$w250 = { param ( [Windows.Controls.Label]$label ) $label.Width = 250 }
$w300 = { param ( [Windows.Controls.Label]$label ) $label.Width = 300 }
$w350 = { param ( [Windows.Controls.Label]$label ) $label.Width = 350 }
$w360 = { param ( [Windows.Controls.Label]$label ) $label.Width = 360 }
$w370 = { param ( [Windows.Controls.Label]$label ) $label.Width = 370 }
$w380 = { param ( [Windows.Controls.Label]$label ) $label.Width = 380 }
$w390 = { param ( [Windows.Controls.Label]$label ) $label.Width = 390 }
$w400 = { param ( [Windows.Controls.Label]$label ) $label.Width = 400 }

#Height
$hauto = { param ( [Windows.Controls.Button]$button ) }
$h010 = { param ( [Windows.Controls.Label]$label ) $label.Height = 10 }
$h020 = { param ( [Windows.Controls.Label]$label ) $label.Height = 20 }
$h025 = { param ( [Windows.Controls.Label]$label ) $label.Height = 25 }
$h040 = { param ( [Windows.Controls.Label]$label ) $label.Height = 40 }
$h060 = { param ( [Windows.Controls.Label]$label ) $label.Height = 60 }
$h080 = { param ( [Windows.Controls.Label]$label ) $label.Height = 80 }
$h100 = { param ( [Windows.Controls.Label]$label ) $label.Height = 100 }

# Margin
$M0 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 0 }
$M1 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 1 }
$M2 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 2 }
$M3 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 3 }
$M4 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 4 }
$M5 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 5 }
$M6 = { param ( [Windows.Controls.Label]$label ) $label.Margin = New-Object Windows.Thickness 6 }

# Padding
$p0 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 0 }
$p1 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 1 }
$p2 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 2 }
$p3 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 3 }
$p4 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 4 }
$p5 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 5 }
$p6 = { param ( [Windows.Controls.Button]$button ) $button.Padding = New-Object Windows.Thickness 6 }

# Windows Thikness
$th0 = { param ( [Windows.Controls.Button]$button ) $button.BorderThickness = New-Object Windows.Thickness 0 }
$th1 = { param ( [Windows.Controls.Button]$button ) $button.BorderThickness = New-Object Windows.Thickness 1 }
$th2 = { param ( [Windows.Controls.Button]$button ) $button.BorderThickness = New-Object Windows.Thickness 2 }
$th3 = { param ( [Windows.Controls.Button]$button ) $button.BorderThickness = New-Object Windows.Thickness 3 }
$th4 = { param ( [Windows.Controls.Button]$button ) $button.BorderThickness = New-Object Windows.Thickness 4 }
$th5 = { param ( [Windows.Controls.Button]$button ) $button.BorderThickness = New-Object Windows.Thickness 5 }

# Alignment Related
$hal = { param ( [Windows.Controls.Button]$button ) $button.HorizontalAlignment = [Windows.HorizontalAlignment]::Left }
$hac = { param ( [Windows.Controls.Button]$button ) $button.HorizontalAlignment = [Windows.HorizontalAlignment]::Center }
$har = { param ( [Windows.Controls.Button]$button ) $button.HorizontalAlignment = [Windows.HorizontalAlignment]::Right }
$val = { param ( [Windows.Controls.Button]$button ) $button.VerticalAlignment = [Windows.VerticalAlignment]::Left }
$vac = { param ( [Windows.Controls.Button]$button ) $button.VerticalAlignment = [Windows.VerticalAlignment]::Center }
$var = { param ( [Windows.Controls.Button]$button ) $button.VerticalAlignment = [Windows.VerticalAlignment]::Right }

# Content Alignment
$cal = { param ( [Windows.Controls.Button]$button ) $button.HorizontalContentAlignment = [Windows.HorizontalAlignment]::left }
$cac = { param ( [Windows.Controls.Button]$button ) $button.HorizontalContentAlignment = [Windows.HorizontalAlignment]::Center }
$car = { param ( [Windows.Controls.Button]$button ) $button.HorizontalContentAlignment = [Windows.HorizontalAlignment]::right }

#$DD?????? = { param ( [Windows.Controls.Button]$button ) $button.IsCancel = $false }
#$benable = { param ( [Windows.Controls.Button]$button ) $button.IsEnabled = $true }


#rgb(255, 18, 60)

Import-Module -Name C:\ms1\scripts\@pwsggui\cls_mx_mn_bk.ps1
Add-Type -AssemblyName PresentationFramework

$Main_Panel = New-Object Windows.Window
$Main_Panel.Title = "PowerShell GUI"
$Main_Panel.Width = 400
$Main_Panel.Height = 700
$Main_Panel.Opacity = 1.0

$Main_Panel.BorderBrush = [Windows.Media.Brushes]::Red
$Main_Panel.BorderThickness = '1'

$Main_Panel.WindowStartupLocation = [Windows.WindowStartupLocation]::CenterScreen
$Main_Panel.Background = [Windows.Media.SolidColorBrush]::New([Windows.Media.Color]::Fromrgb(29, 32, 39))
#$Main_Panel.Foreground = [Windows.Media.Brushes]::Green
$Main_Panel.WindowStyle = [Windows.WindowStyle]::None
$Main_Panel.AllowsTransparency = $true
$mouseDown = [Windows.Input.MouseButtonEventHandler]{ param( [Object]$senderr, [Windows.Input.MouseButtonEventArgs]$e ) if ($e.ChangedButton -eq [Windows.Input.MouseButton]::Left) { $Main_Panel.DragMove() } }
$Main_Panel.Add_MouseLeftButtonDown($mouseDown)

$Main_Panel.Content = New-Object Windows.Controls.StackPanel
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Main_Panel.ps1

$backup_bt       = req ` -content "[B]ackup"          ` -styles @($ff10, $b, $fg01, $bg02, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\backup.ps1`"" }
$FFmpeg_bt       = req ` -content "[F]Fmpeg"          ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $FFmpeg_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Find_bt         = req ` -content "[F]ind"            ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Find_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Folder_bt       = req ` -content "[F]olders"         ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Folder_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Health_bt       = req ` -content "[H]ealth"          ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Health_Grid ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Package_bt      = req ` -content "[P]ackage Manager" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Package_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Rclone_bt       = req ` -content "[R]clone"          ` -styles @($ff10, $b, $fg00, $bg06, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Rclone_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$StartStop_bt    = req ` -content "[S]top [R]estart"  ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $StartStop_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Startupapps_bt  = req ` -content "[S]tartup Apps"    ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $StartupApps_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Tools_bt        = req ` -content "[T]ools"           ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Tools_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Update_bt       = req ` -content "[U]pdate"          ` -styles @($ff10, $b, $fg01, $bg03, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\update.ps1`"" }
$Valorant_bt     = req ` -content "[V]alorant"        ` -styles @($ff10, $b, $fg01, $bg05, $fz16, $w250, $h040) ` -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Valorant_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }

$Main_Panel.Content.Children.Add($backup_bt)
$Main_Panel.Content.Children.Add($FFmpeg_bt)
$Main_Panel.Content.Children.Add($Find_bt)
$Main_Panel.Content.Children.Add($Folder_bt)
$Main_Panel.Content.Children.Add($Health_bt)
$Main_Panel.Content.Children.Add($Package_bt)
$Main_Panel.Content.Children.Add($Rclone_bt)
$Main_Panel.Content.Children.Add($StartStop_bt)
$Main_Panel.Content.Children.Add($Startupapps_bt)
$Main_Panel.Content.Children.Add($Tools_bt)
$Main_Panel.Content.Children.Add($Update_bt)
$Main_Panel.Content.Children.Add($Valorant_bt)

#rgb(0, 206, 162)

$Tools_Panel = New-Object Windows.Controls.StackPanel
$Tools_Panel.Margin = New-Object Windows.Thickness(0, 0, 0, 0)
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Tool_Panel.ps1

# Create WrapPanel for the first two buttons (dxdiag and systeminfo)
$wrapPanel = New-Object Windows.Controls.WrapPanel
$wrapPanel.Orientation = [Windows.Controls.Orientation]::Horizontal
$wrapPanel.HorizontalAlignment = [Windows.HorizontalAlignment]::Center

$dxdiag_bt = req ` -content "DxDiag"         ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w100, $h040) ` -onClick { dxdiag ; $Main_Panel.Content = $Tools_Panel }
$systeminfo_bt = req ` -content "Systeminfo" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w150, $h040) ` -onClick { Start-Process -FilePath "cmd" -ArgumentList "/K systeminfo" <# -NoNewWindow #> ; $Main_Panel.Content = $Tools_Panel }

$wrapPanel.Children.Add($dxdiag_bt)
$wrapPanel.Children.Add($systeminfo_bt)

# Create StackPanel for the rest of the buttons
$stackPanel = New-Object Windows.Controls.StackPanel
$stackPanel.Orientation = [Windows.Controls.Orientation]::vertical
$stackPanel.HorizontalAlignment = [Windows.HorizontalAlignment]::Center

$msinfo32_bt = req ` -content "Msinfo32"                 ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { msinfo32 ; $Main_Panel.Content = $Tools_Panel }
$snip_bt = req ` -content "Snipping Tool"                ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process snippingtool; $Main_Panel.Content = $Tools_Panel }
$paint_bt = req ` -content "Paint"                       ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process mspaint; $Main_Panel.Content = $Tools_Panel }
$winutility_bt = req ` -content "Windows Utility by CTT" ` -styles @($ff10, $b, $fg00, $bg05, $fz16, $w250, $h040) ` -onClick { Invoke-RestMethod christitus.com/win | Invoke-Expression; $Main_Panel.Content = $Tools_Panel }

$stackPanel.Children.Add($msinfo32_bt)
$stackPanel.Children.Add($snip_bt)
$stackPanel.Children.Add($paint_bt)
$stackPanel.Children.Add($winutility_bt)

# Add the panels to Tools_Panel
$Tools_Panel.Children.Add($wrapPanel)
$Tools_Panel.Children.Add($stackPanel)

#rgb(0, 206, 162)

$Package_Panel = New-Object Windows.Controls.StackPanel
$Package_Panel.Margin = New-Object Windows.Thickness(0, 0, 0, 0)
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Package_Panel.ps1

$scp_bckt_bt = req ` -content "Buckets Update (Scoop)"      ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w300, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -Command scoop update && Set-Location " ; $Main_Panel.Content = $Package_Panel }
$scp_sts_bt  = req ` -content "Check Lates Version (Scoop)" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w300, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -Command scoop status && Set-Location " ; $Main_Panel.Content = $Package_Panel }
$scp_uptd_bt = req ` -content "Update Apps (Scoop)"         ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w300, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -Command scoop update * && Set-Location " ; $Main_Panel.Content = $Package_Panel }
$scp_cln_bt  = req ` -content "Cleanup Older Apps (Scoop)"  ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w300, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -Command scoop cleanup * && Set-Location " ; $Main_Panel.Content = $Package_Panel }

$Package_Panel.Children.Add($scp_bckt_bt)
$Package_Panel.Children.Add($scp_sts_bt)
$Package_Panel.Children.Add($scp_uptd_bt)
$Package_Panel.Children.Add($scp_cln_bt)

#rgb(0, 206, 162)

$Rclone_Panel = New-Object Windows.Controls.StackPanel
$Rclone_Panel.Margin = New-Object Windows.Thickness(0, 0, 0, 0)
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Rclone_Panel.ps1

$sync_bt           = req ` -content "Sync"             ` -styles @($ff10, $b, $fg00, $bg06, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\rclone\sync.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }
$about_bt          = req ` -content "Storage Info"     ` -styles @($ff10, $b, $fg00, $bg06, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\rclone\about.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }
$delete_trashgu_bt = req ` -content "Delete GU Trash"  ` -styles @($ff10, $b, $fg00, $bg06, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\rclone\delete_gu.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }
$touch_bt          = req ` -content "Touch Drives"     ` -styles @($ff10, $b, $fg00, $bg06, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\rclone\touch.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }

$Rclone_Panel.Children.Add($sync_bt)
$Rclone_Panel.Children.Add($about_bt)
$Rclone_Panel.Children.Add($delete_trashgu_bt)
$Rclone_Panel.Children.Add($touch_bt)

#rgb(0, 206, 162)

# Define a Grid for ValoSchedule buttons
$Health_Grid = New-Object Windows.Controls.Grid
$Health_Grid.Margin = New-Object Windows.Thickness 0

# Create WrapPanel for buttons at the top
$Health_UpperPart = New-Object Windows.Controls.WrapPanel
$Health_UpperPart.Orientation = [Windows.Controls.Orientation]::vertical
$Health_UpperPart.HorizontalAlignment = [Windows.HorizontalAlignment]::Right
#$Health_UpperPart.HorizontalContentAlignment = [Windows.HorizontalAlignment]::Center
#$Health_UpperPart.VerticalAlignment = [Windows.VerticalAlignment]::Center

# Create buttons for the top wrap panel
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Health_Grid.ps1

# Create WrapPanel for buttons at the bottom
$Health_LowerPart = New-Object Windows.Controls.WrapPanel
$Health_LowerPart.Orientation = [Windows.Controls.Orientation]::Horizontal
$Health_LowerPart.HorizontalAlignment = [Windows.HorizontalAlignment]::Center

# Create buttons for the bottom wrap panel
$bottomButton1 = & $mm -content "1" -onClick {  Add your action for bottomButton1 here }
$bottomButton2 = & $mm -content "2" -onClick {  Add your action for bottomButton2 here }
$bottomButton3 = & $mm -content "3" -onClick {  Add your action for bottomButton3 here }

# Add buttons to the bottom wrap panel
$Health_LowerPart.Children.Add($bottomButton1)
$Health_LowerPart.Children.Add($bottomButton2)
$Health_LowerPart.Children.Add($bottomButton3)

# Create buttons inside Health_Grid
$dism_bt         = req ` -content "DISM"          ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W400, $H040, $m1) ` -onClick { Start-Process -FilePath "DISM" -ArgumentList "/Online /Cleanup-Image /RestoreHealth" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$sfc_bt          = req ` -content "SFC"           ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H040, $m1) ` -onClick { Start-Process -FilePath "sfc" -ArgumentList "/scannow" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$chkdsk_bt       = req ` -content "Chkdsk"        ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H040, $m1) ` -onClick { Start-Process -FilePath "chkdsk" -ArgumentList "/f /r" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$diskcleanup_bt  = req ` -content "Disk Cleanup"  ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H040, $m1) ` -onClick { Start-Process -FilePath "cleanmgr" -ArgumentList "/sagerun:1" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$taskmanager_bt  = req ` -content "Task Manager"  ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H080, $m1) ` -onClick { Start-Process -FilePath "taskmgr" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$eventviewer_bt  = req ` -content "Event Viewer"  ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H040, $m1) ` -onClick { Start-Process -FilePath "eventvwr" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$flushdns_bt     = req ` -content "Flush DNS"     ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H080, $m1) ` -onClick { Start-Process -FilePath "cmd" -ArgumentList "/k ipconfig /flushdns" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$resetwinsock_bt = req ` -content "Reset Winsock" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $W130, $H040, $m1) ` -onClick { Start-Process -FilePath "cmd" -ArgumentList "/k netsh winsock reset" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }

# Set button positions in the Grid
$Health_Grid.ColumnDefinitions.Add((New-Object Windows.Controls.ColumnDefinition))
$Health_Grid.ColumnDefinitions.Add((New-Object Windows.Controls.ColumnDefinition))
$Health_Grid.ColumnDefinitions.Add((New-Object Windows.Controls.ColumnDefinition))

$Health_Grid.RowDefinitions.Add((New-Object Windows.Controls.RowDefinition)) 
$Health_Grid.RowDefinitions.Add((New-Object Windows.Controls.RowDefinition))
$Health_Grid.RowDefinitions.Add((New-Object Windows.Controls.RowDefinition))
$Health_Grid.RowDefinitions.Add((New-Object Windows.Controls.RowDefinition))
$Health_Grid.RowDefinitions.Add((New-Object Windows.Controls.RowDefinition))
$Health_Grid.RowDefinitions.Add((New-Object Windows.Controls.RowDefinition))

$Health_Grid.RowDefinitions[0].Height = [Windows.GridLength]::Auto
$Health_Grid.RowDefinitions[1].Height = [Windows.GridLength]::Auto
$Health_Grid.RowDefinitions[2].Height = [Windows.GridLength]::Auto
$Health_Grid.RowDefinitions[3].Height = [Windows.GridLength]::Auto
$Health_Grid.RowDefinitions[4].Height = [Windows.GridLength]::Auto
$Health_Grid.RowDefinitions[5].Height = [Windows.GridLength]::Auto

[Windows.Controls.Grid]::SetRow($dism_bt, 1)
[Windows.Controls.Grid]::SetColumn($dism_bt, 0)
#[Windows.Controls.Grid]::SetRowSpan($dism_bt, 3 )
[Windows.Controls.Grid]::SetColumnSpan($dism_bt, 3)

[Windows.Controls.Grid]::SetRow($sfc_bt, 2)
[Windows.Controls.Grid]::SetColumn($sfc_bt, 0)

[Windows.Controls.Grid]::SetRow($chkdsk_bt, 2)
[Windows.Controls.Grid]::SetColumn($chkdsk_bt, 1)

[Windows.Controls.Grid]::SetRow($diskcleanup_bt, 2)
[Windows.Controls.Grid]::SetColumn($diskcleanup_bt, 2)

[Windows.Controls.Grid]::SetRow($taskmanager_bt,3)
[Windows.Controls.Grid]::SetColumn($taskmanager_bt, 0)
[Windows.Controls.Grid]::SetRowSpan($taskmanager_bt, 2 )

[Windows.Controls.Grid]::SetRow($eventviewer_bt, 3)
[Windows.Controls.Grid]::SetColumn($eventviewer_bt, 1)

[Windows.Controls.Grid]::SetRow($flushdns_bt,3)
[Windows.Controls.Grid]::SetColumn($flushdns_bt, 2)
[Windows.Controls.Grid]::SetRowSpan($flushdns_bt, 2 )

[Windows.Controls.Grid]::SetRow($resetwinsock_bt, 4)
[Windows.Controls.Grid]::SetColumn($resetwinsock_bt, 1)

# Add buttons to the Grid
$Health_Grid.Children.Add($dism_bt)
$Health_Grid.Children.Add($sfc_bt)
$Health_Grid.Children.Add($chkdsk_bt)
$Health_Grid.Children.Add($diskcleanup_bt)
$Health_Grid.Children.Add($taskmanager_bt)
$Health_Grid.Children.Add($eventviewer_bt)
$Health_Grid.Children.Add($flushdns_bt)
$Health_Grid.Children.Add($resetwinsock_bt)

# Add Top, Middle, and Bottom WrapPanels to Health_Grid
[Windows.Controls.Grid]::SetRow($Health_UpperPart, 0)
[Windows.Controls.Grid]::SetColumn($Health_UpperPart, 0)
[Windows.Controls.Grid]::SetColumnSpan($Health_UpperPart, 9) # Health_UpperPart spans all 3 columns

[Windows.Controls.Grid]::SetRow($Health_LowerPart, 5)
[Windows.Controls.Grid]::SetColumn($Health_LowerPart, 1)
[Windows.Controls.Grid]::SetColumnSpan($Health_LowerPart, 1) # Health_LowerPart spans all 3 columns

$Health_Grid.Children.Add($Health_UpperPart)
$Health_Grid.Children.Add($Health_LowerPart)

#rgb(0, 206, 162)




#rgb(0, 206, 162)

$FFmpeg_Panel = New-Object Windows.Controls.StackPanel
$FFmpeg_Panel.Margin = New-Object Windows.Thickness 0
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\FFmpeg_Panel.ps1

$trim_bt      =  req ` -content "Trim"            ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\ffmpeg\trim.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$convert_bt   =  req ` -content "Convert Video"   ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\ffmpeg\convert.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$dimension_bt =  req ` -content "Video Dimension" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\ffmpeg\dimension.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$imgdim_bt    =  req ` -content "Image Dimension" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\ffmpeg\imgdim.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$merge_bt     =  req ` -content "Merge Videos"    ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\ffmpeg\merge.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }

$FFmpeg_Panel.Children.Add($convert_bt)
$FFmpeg_Panel.Children.Add($dimension_bt)
$FFmpeg_Panel.Children.Add($imgdim_bt)
$FFmpeg_Panel.Children.Add($merge_bt)
$FFmpeg_Panel.Children.Add($trim_bt)

#rgb(0, 206, 162)

$Find_Panel = New-Object Windows.Controls.StackPanel
$Find_Panel.Margin = New-Object Windows.Thickness 0
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Find_Panel.ps1

$find_file_bt    = req ` -content "Find File"    ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\find\find_file.ps1`"" ; $Main_Panel.Content = $Find_Panel }
$find_size_bt    = req ` -content "Find Size"    ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\find\find_size.ps1`"" ; $Main_Panel.Content = $Find_Panel }
$find_pattern_bt = req ` -content "Find Pattern" ` -styles @($ff10, $b, $fg00, $bg01, $fz16, $w250, $h040) ` -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"C:\ms1\scripts\find\find_pattern.ps1`"" ; $Main_Panel.Content = $Find_Panel }

$Find_Panel.Children.Add($find_file_bt)
$Find_Panel.Children.Add($find_size_bt)
$Find_Panel.Children.Add($find_pattern_bt)

#rgb(0, 206, 162)

$Folder_Panel = New-Object Windows.Controls.stackPanel      #WrapPanel
$Folder_Panel.Margin = New-Object Windows.Thickness 0
Import-Module -Name C:\ms1\scripts\@pwsggui\cs_mx_mm_bk\Folder_Panel.ps1

$appdata_bt     = req ` -content "AppData"        ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\Users\nahid\AppData" ; $Main_Panel.Content = $Folder_Panel }
$apps_bt        = req ` -content "All Apps"       ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "shell:appsfolder" ; $Main_Panel.Content = $Folder_Panel }
$git_bt         = req ` -content "Git Projects"   ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "D:\@git" ; $Main_Panel.Content = $Folder_Panel }
$Packages_bt    = req ` -content "Packages"       ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\Users\nahid\AppData\Local\Packages" ; $Main_Panel.Content = $Folder_Panel }
$scoop_bt       = req ` -content "Scoop"          ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process C:\Users\nahid\scoop ; $Main_Panel.Content = $Folder_Panel }
$sftr_bt        = req ` -content "Software"       ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "D:\software" ; $Main_Panel.Content = $Folder_Panel }
$song_bt        = req ` -content "Song"           ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "D:\song" ; $Main_Panel.Content = $Folder_Panel }
$startupsys_bt  = req ` -content "Startup System" ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" ; $Main_Panel.Content = $Folder_Panel }
$startupusr_bt  = req ` -content "Startup User"   ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" ; $Main_Panel.Content = $Folder_Panel }
$temp1_bt       = req ` -content "Temp-AppDate"   ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\Users\nahid\AppData\Local\Temp" ; $Main_Panel.Content = $Folder_Panel }
$temp2_bt       = req ` -content "Temp-Windows"   ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\Windows\Temp" ; $Main_Panel.Content = $Folder_Panel }
$windowsapp_bt  = req ` -content "WindowsApp"     ` -styles @($ff10, $b, $fg00, $bg04, $fz16, $w250, $h040) ` -onClick { start-Process "C:\Program Files\WindowsApps" ; $Main_Panel.Content = $Folder_Panel }

$Folder_Panel.Children.Add($appdata_bt)
$Folder_Panel.Children.Add($apps_bt)
$Folder_Panel.Children.Add($git_bt)
$Folder_Panel.Children.Add($Packages_bt)
$Folder_Panel.Children.Add($scoop_bt)
$Folder_Panel.Children.Add($sftr_bt)
$Folder_Panel.Children.Add($song_bt)
$Folder_Panel.Children.Add($startupsys_bt)
$Folder_Panel.Children.Add($startupusr_bt)
$Folder_Panel.Children.Add($temp1_bt)
$Folder_Panel.Children.Add($temp2_bt)
$Folder_Panel.Children.Add($windowsapp_bt)

#rgb(0, 206, 162)



#rgb(0, 206, 162)



$Main_Panel.ShowDialog() | Out-Null
