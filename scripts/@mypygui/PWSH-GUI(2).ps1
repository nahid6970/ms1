
Import-Module -Name D:\@git\ms1\scripts\@pwsggui\cs.ps1
Add-Type -AssemblyName PresentationFramework
$window = New-Object Windows.Window
$window.Title = "PowerShell GUI"
$window.Width = 400
$window.Height = 700
$window.Opacity = 1.0  # Adjust this value as needed
$window.WindowStartupLocation = [Windows.WindowStartupLocation]::CenterScreen
$window.Background = [Windows.Media.SolidColorBrush]::New([Windows.Media.Color]::Fromrgb(29, 32, 39))
$window.Foreground = [Windows.Media.Brushes]::Green
#Removes top and side and bottom window bar
$window.WindowStyle = [Windows.WindowStyle]::None
$window.AllowsTransparency = $true
# Define the event handler for mouse down event
$mouseDown = [Windows.Input.MouseButtonEventHandler]{ param( [Object]$senderr, [Windows.Input.MouseButtonEventArgs]$e ) if ($e.ChangedButton -eq [Windows.Input.MouseButton]::Left) { $window.DragMove() } }
# Attach the mouse down event to the window
$window.Add_MouseLeftButtonDown($mouseDown)

$stackPanel = New-Object Windows.Controls.StackPanel
$window.Content = $stackPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$stackPanel.Children.Add($close_bt)
$stackPanel.Children.Add($maximize_bt)
$stackPanel.Children.Add($minimize_bt)

$Tools_bt = & $cs1 -content "Tools ⚡"-onClick({$window.Content = $Tools_Panel})
$backup_bt = & $bkup -content "Backup 🔃" -onClick({ Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\backup.ps1`"" })
$FFmpeg_bt = & $cs1 -content "FFmpeg 📺" -onClick({ $window.Content = $FFmpeg_Panel })
$Find_bt = & $cs1 -content "Find 🔎" -onClick({ $window.Content = $Find_Panel })
$Folder_bt = & $fldr -content "Folders 📂" -onClick({ $window.Content = $Folder_Panel })
$Valorant_bt = & $vlr -content "Valorant 🎮" -onClick({ $window.Content = $Valorant_Panel })
$Rclone_bt = & $rcl -content "Rclone" -onClick({ $window.Content = $Rclone_Panel })
$Health_bt = & $hth -content "Health 💊" -onClick({ $window.Content = $Health_Panel })
$Update_bt = & $updt -content "Update 👍🏻" -onClick({ Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\update.ps1`"" })

$stackPanel.Children.Add($backup_bt)
$stackPanel.Children.Add($Update_bt)
$stackPanel.Children.Add($Tools_bt)
$stackPanel.Children.Add($Rclone_bt)
$stackPanel.Children.Add($FFmpeg_bt)
$stackPanel.Children.Add($Find_bt)
$stackPanel.Children.Add($Folder_bt)
$stackPanel.Children.Add($Health_bt)
$stackPanel.Children.Add($Valorant_bt)


#wrappanel example
#$Tools_Panel = New-Object Windows.Controls.WrapPanel
#$Tools_Panel.HorizontalAlignment = [Windows.HorizontalAlignment]::Center
#$Tools_Panel.VerticalAlignment = [Windows.VerticalAlignment]::Center

$Tools_Panel = New-Object Windows.Controls.StackPanel
$Tools_Panel.Margin = New-Object Windows.Thickness(0, 0, 0, 0)

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$Tools_Panel.Children.Add($close_bt)
$Tools_Panel.Children.Add($maximize_bt)
$Tools_Panel.Children.Add($minimize_bt)
$Tools_Panel.Children.Add($back_bt)

$dxdiag_bt = & $cs2 -content "DxDiag" -onClick { dxdiag ; $window.Content = $stackPanel }
$systeminfo_bt = & $cs2 -content "Systeminfo" -onClick { Start-Process systeminfo ; $window.Content = $stackPanel }
$msinfo32_bt = & $cs2 -content "Msinfo32" -onClick { msinfo32 ; $window.Content = $stackPanel }
$snip_bt = & $cs2 -content "Snipping Tool" -onClick { Start-Process snippingtool; $window.Content = $stackPanel }
$paint_bt = & $cs2 -content "Paint" -onClick { Start-Process mspaint; $window.Content = $stackPanel }
$winutility_bt = & $cs2 -content "Windows Utility by CTT" -onClick { Invoke-RestMethod christitus.com/win | Invoke-Expression; $window.Content = $stackPanel }

$Tools_Panel.Children.Add($dxdiag_bt)
$Tools_Panel.Children.Add($systeminfo_bt)
$Tools_Panel.Children.Add($msinfo32_bt)
$Tools_Panel.Children.Add($snip_bt)
$Tools_Panel.Children.Add($paint_bt)
$Tools_Panel.Children.Add($winutility_bt)




$Rclone_Panel = New-Object Windows.Controls.StackPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$Rclone_Panel.Children.Add($close_bt)
$Rclone_Panel.Children.Add($maximize_bt)
$Rclone_Panel.Children.Add($minimize_bt)
$Rclone_Panel.Children.Add($back_bt)

$sync_bt = & $cs2 -content "Sync" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\sync.ps1`"" ; $window.Content = $stackPanel  }
$about_bt = & $cs2 -content "Storage Info" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\about.ps1`"" ; $window.Content = $stackPanel  }
$delete_trashgu_bt = & $cs2 -content "Delete GU Trash" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\delete_gu.ps1`"" ; $window.Content = $stackPanel  }
$touch_bt = & $cs2 -content "Touch Drives" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\touch.ps1`"" ; $window.Content = $stackPanel  }

$Rclone_Panel.Children.Add($sync_bt)
$Rclone_Panel.Children.Add($about_bt)
$Rclone_Panel.Children.Add($delete_trashgu_bt)
$Rclone_Panel.Children.Add($touch_bt)




$Health_Panel = New-Object Windows.Controls.StackPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$Health_Panel.Children.Add($close_bt)
$Health_Panel.Children.Add($maximize_bt)
$Health_Panel.Children.Add($minimize_bt)
$Health_Panel.Children.Add($back_bt)

#DISM /Online /Cleanup-Image /RestoreHealth
$dism_bt = & $cs2 -content "DISM" -onClick { Start-Process -FilePath "DISM" -ArgumentList "/Online /Cleanup-Image /RestoreHealth" -Verb RunAs ; $window.Content = $stackPanel }
$sfc_bt = & $cs2 -content "SFC" -onClick { Start-Process -FilePath "sfc" -ArgumentList "/scannow" -Verb RunAs ; $window.Content = $stackPanel }
$chkdsk_bt = & $cs2 -content "Chkdsk" -onClick { Start-Process -FilePath "chkdsk" -ArgumentList "/f /r" -Verb RunAs ; $window.Content = $stackPanel }
$update_bt = & $cs2 -content "Check for Updates" -onClick { Start-Process -FilePath "ms-settings:windowsupdate-action" ; $window.Content = $stackPanel }
$diskcleanup_bt = & $cs2 -content "Disk Cleanup" -onClick { Start-Process -FilePath "cleanmgr" -ArgumentList "/sagerun:1" -Verb RunAs ; $window.Content = $stackPanel }
$taskmanager_bt = & $cs2 -content "Task Manager" -onClick { Start-Process -FilePath "taskmgr" -Verb RunAs ; $window.Content = $stackPanel }
$eventviewer_bt = & $cs2 -content "Event Viewer" -onClick { Start-Process -FilePath "eventvwr" -Verb RunAs ; $window.Content = $stackPanel }
$flushdns_bt = & $cs2 -content "Flush DNS" -onClick { Start-Process -FilePath "cmd" -ArgumentList "/k ipconfig /flushdns" -Verb RunAs ; $window.Content = $stackPanel }
$resetwinsock_bt = & $cs2 -content "Reset Winsock" -onClick { Start-Process -FilePath "cmd" -ArgumentList "/k netsh winsock reset" -Verb RunAs ; $window.Content = $stackPanel }

$Health_Panel.Children.Add($chkdsk_bt) 
$Health_Panel.Children.Add($diskcleanup_bt) 
$Health_Panel.Children.Add($dism_bt)
$Health_Panel.Children.Add($eventviewer_bt) 
$Health_Panel.Children.Add($flushdns_bt) 
$Health_Panel.Children.Add($resetwinsock_bt) 
$Health_Panel.Children.Add($sfc_bt) 
$Health_Panel.Children.Add($taskmanager_bt) 
$Health_Panel.Children.Add($update_bt) 




$FFmpeg_Panel = New-Object Windows.Controls.StackPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$FFmpeg_Panel.Children.Add($close_bt)
$FFmpeg_Panel.Children.Add($maximize_bt)
$FFmpeg_Panel.Children.Add($minimize_bt)
$FFmpeg_Panel.Children.Add($back_bt)

$trim_bt = & $cs2 -content "Trim" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\trim.ps1`"" ; $window.Content = $stackPanel  }
$convert_bt = & $cs2 -content "Convert Video" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\convert.ps1`"" ; $window.Content = $stackPanel  }
$dimension_bt = & $cs2 -content "Video Dimension" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\dimension.ps1`"" ; $window.Content = $stackPanel  }
$imgdim_bt = & $cs2 -content "Image Dimension" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\imgdim.ps1`"" ; $window.Content = $stackPanel  }
$merge_bt = & $cs2 -content "Merge Videos" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\merge.ps1`"" ; $window.Content = $stackPanel  }

$FFmpeg_Panel.Children.Add($convert_bt)
$FFmpeg_Panel.Children.Add($dimension_bt)
$FFmpeg_Panel.Children.Add($imgdim_bt)
$FFmpeg_Panel.Children.Add($merge_bt)
$FFmpeg_Panel.Children.Add($trim_bt)




$Find_Panel = New-Object Windows.Controls.StackPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$Find_Panel.Children.Add($close_bt)
$Find_Panel.Children.Add($maximize_bt)
$Find_Panel.Children.Add($minimize_bt)
$Find_Panel.Children.Add($back_bt)

$find_file_bt = & $cs2 -content "Find File" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\find\find_file.ps1`"" ; $window.Content = $stackPanel }
$find_size_bt = & $cs2 -content "Find Size" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\find\find_size.ps1`"" ; $window.Content = $stackPanel }
$find_pattern_bt = & $cs2 -content "Find Pattern" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\find\find_pattern.ps1`"" ; $window.Content = $stackPanel }

$Find_Panel.Children.Add($find_file_bt)
$Find_Panel.Children.Add($find_size_bt)
$Find_Panel.Children.Add($find_pattern_bt)




$Folder_Panel = New-Object Windows.Controls.stackPanel      #WrapPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$Folder_Panel.Children.Add($close_bt)
$Folder_Panel.Children.Add($maximize_bt)
$Folder_Panel.Children.Add($minimize_bt)
$Folder_Panel.Children.Add($back_bt)

$scoop_bt = & $fldr -content "Scoop" -onClick  { start-Process C:\Users\nahid\scoop ; $window.Content = $stackPanel }
$startup_bt = & $fldr -content "Startup" -onClick  { start-Process "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" ; $window.Content = $stackPanel }
$windowsapp_bt = & $fldr -content "WindowsApp" -onClick  { start-Process "C:\Program Files\WindowsApps" ; $window.Content = $stackPanel }
$Packages_bt = & $fldr -content "Packages" -onClick  { start-Process "C:\Users\nahid\AppData\Local\Packages" ; $window.Content = $stackPanel }
$appdata_bt = & $fldr -content "AppData" -onClick  { start-Process "C:\Users\nahid\AppData" ; $window.Content = $stackPanel }
$apps_bt = & $fldr -content "All Apps" -onClick  { start-Process "shell:appsfolder" ; $window.Content = $stackPanel }
$temp1_bt = & $fldr -content "TempAppDate 🗑️" -onClick  { start-Process "C:\Users\nahid\AppData\Local\Temp" ; $window.Content = $stackPanel }
$temp2_bt = & $fldr -content "TempWindows 🗑️" -onClick  { start-Process "C:\Windows\Temp" ; $window.Content = $stackPanel }
$song_bt = & $fldr -content "Song 🎶" -onClick  { start-Process "D:\song" ; $window.Content = $stackPanel }
$sftr_bt = & $fldr -content "Software 🍎" -onClick  { start-Process "D:\software" ; $window.Content = $stackPanel }
$git_bt = & $fldr -content "Git Projects" -onClick  { start-Process "D:\@git" ; $window.Content = $stackPanel }

$Folder_Panel.Children.Add($appdata_bt)
$Folder_Panel.Children.Add($apps_bt)
$Folder_Panel.Children.Add($git_bt)
$Folder_Panel.Children.Add($Packages_bt)
$Folder_Panel.Children.Add($scoop_bt)
$Folder_Panel.Children.Add($sftr_bt)
$Folder_Panel.Children.Add($song_bt)
$Folder_Panel.Children.Add($startup_bt)
$Folder_Panel.Children.Add($temp1_bt)
$Folder_Panel.Children.Add($temp2_bt)
$Folder_Panel.Children.Add($windowsapp_bt)





$Valorant_Panel = New-Object Windows.Controls.StackPanel

$close_bt = & $xx -content "X" -onClick({$window.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($window.WindowState -eq [Windows.WindowState]::Normal) { $window.WindowState = [Windows.WindowState]::Maximized } else { $window.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $window.WindowState = [Windows.WindowState]::Minimized})
$back_bt = & $bk -content "⇠" -onClick  { $window.Content = $stackPanel }
$Valorant_Panel.Children.Add($close_bt)
$Valorant_Panel.Children.Add($maximize_bt)
$Valorant_Panel.Children.Add($minimize_bt)
$Valorant_Panel.Children.Add($back_bt)

$valo_ahk_bt = & $vlr -content "Valorant-AHK" -onClick { D:\@git\ms1\scripts\valorant\valo.ahk; $window.Content = $stackPanel}
$valorant_qbit_bt = & $vlr -content "Valorant + Qbit" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\valorant\valo_qbit.ps1`"" ; $window.Content = $stackPanel }

$Valorant_Panel.Children.Add($valo_ahk_bt)
$Valorant_Panel.Children.Add($valorant_qbit_bt)











$window.ShowDialog() | Out-Null
