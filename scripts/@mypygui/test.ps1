Import-Module -Name D:\@git\ms1\scripts\@pwsggui\cs.ps1

Add-Type -AssemblyName PresentationFramework

$Main_Panel = New-Object Windows.Window
$Main_Panel.Title = "PowerShell GUI"
$Main_Panel.Width = 400
$Main_Panel.Height = 700
$Main_Panel.Opacity = 1.0
$Main_Panel.WindowStartupLocation = [Windows.WindowStartupLocation]::CenterScreen
$Main_Panel.Background = [Windows.Media.SolidColorBrush]::New([Windows.Media.Color]::Fromrgb(29, 32, 39))
$Main_Panel.Foreground = [Windows.Media.Brushes]::Green
$Main_Panel.WindowStyle = [Windows.WindowStyle]::None
$Main_Panel.AllowsTransparency = $true
$mouseDown = [Windows.Input.MouseButtonEventHandler]{ param( [Object]$senderr, [Windows.Input.MouseButtonEventArgs]$e ) if ($e.ChangedButton -eq [Windows.Input.MouseButton]::Left) { $Main_Panel.DragMove() } }
$Main_Panel.Add_MouseLeftButtonDown($mouseDown)


$Main_Panel.Content = New-Object Windows.Controls.StackPanel

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$Tools_bt = & $cs2 -content "Tools ⚡" -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Tools_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Rclone_bt = & $rcl -content "Rclone" -onClick{ $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Rclone_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$Health_bt = & $hth -content "Health 💊" -onClick { $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Health_Grid ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content }
$FFmpeg_bt = & $cs1 -content "FFmpeg 📺" -onClick({ $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $FFmpeg_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content })
$Find_bt = & $cs1 -content "Find 🔎" -onClick({ $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Find_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content })
$Folder_bt = & $fldr -content "Folders 📂" -onClick({ $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Folder_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content })
$Valorant_bt = & $vlr -content "Valorant 🎮" -onClick({ $Prev_Content = $Main_Panel.Content ; $Main_Panel.Content = $Valorant_Panel ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 ; $BackToMain_bt.Tag = $Prev_Content })
$backup_bt = & $bkup -content "Backup 🔃" -onClick { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\backup.ps1`"" }
$Update_bt = & $updt -content "Update 👍🏻" -onClick({ Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\update.ps1`"" })

$Main_Panel.Content.Children.Add($close_bt)
$Main_Panel.Content.Children.Add($maximize_bt)
$Main_Panel.Content.Children.Add($minimize_bt)
$Main_Panel.Content.Children.Add($Tools_bt)
$Main_Panel.Content.Children.Add($backup_bt)
$Main_Panel.Content.Children.Add($Update_bt)
$Main_Panel.Content.Children.Add($Rclone_bt)
$Main_Panel.Content.Children.Add($FFmpeg_bt)
$Main_Panel.Content.Children.Add($Find_bt)
$Main_Panel.Content.Children.Add($Folder_bt)
$Main_Panel.Content.Children.Add($Health_bt)
$Main_Panel.Content.Children.Add($Valorant_bt)





$Tools_Panel = New-Object Windows.Controls.StackPanel
$Tools_Panel.Margin = New-Object Windows.Thickness(0, 0, 0, 0)

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$Tools_Panel.Children.Add($close_bt)
$Tools_Panel.Children.Add($maximize_bt)
$Tools_Panel.Children.Add($minimize_bt)
$Tools_Panel.Children.Add($BackToMain_bt)

$dxdiag_bt = & $cs2 -content "DxDiag" -onClick { dxdiag ; $Main_Panel.Content = $Tools_Panel }
$systeminfo_bt = & $cs2 -content "Systeminfo" -onClick { Start-Process systeminfo ; $Main_Panel.Content = $Tools_Panel }
$msinfo32_bt = & $cs2 -content "Msinfo32" -onClick { msinfo32 ; $Main_Panel.Content = $Tools_Panel }
$snip_bt = & $cs2 -content "Snipping Tool" -onClick { Start-Process snippingtool; $Main_Panel.Content = $Tools_Panel }
$paint_bt = & $cs2 -content "Paint" -onClick { Start-Process mspaint; $Main_Panel.Content = $Tools_Panel }
$winutility_bt = & $cs2 -content "Windows Utility by CTT" -onClick { Invoke-RestMethod christitus.com/win | Invoke-Expression; $Main_Panel.Content = $Tools_Panel }

$Tools_Panel.Children.Add($dxdiag_bt)
$Tools_Panel.Children.Add($systeminfo_bt)
$Tools_Panel.Children.Add($msinfo32_bt)
$Tools_Panel.Children.Add($snip_bt)
$Tools_Panel.Children.Add($paint_bt)
$Tools_Panel.Children.Add($winutility_bt)





$Rclone_Panel = New-Object Windows.Controls.StackPanel
$Rclone_Panel.Margin = New-Object Windows.Thickness(0, 0, 0, 0)

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$Rclone_Panel.Children.Add($close_bt)
$Rclone_Panel.Children.Add($maximize_bt)
$Rclone_Panel.Children.Add($minimize_bt)
$Rclone_Panel.Children.Add($BackToMain_bt)

$sync_bt = & $cs2 -content "Sync" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\sync.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }
$about_bt = & $cs2 -content "Storage Info" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\about.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }
$delete_trashgu_bt = & $cs2 -content "Delete GU Trash" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\delete_gu.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }
$touch_bt = & $cs2 -content "Touch Drives" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\rclone\touch.ps1`"" ; $Main_Panel.Content = $Rclone_Panel  }

$Rclone_Panel.Children.Add($sync_bt)
$Rclone_Panel.Children.Add($about_bt)
$Rclone_Panel.Children.Add($delete_trashgu_bt)
$Rclone_Panel.Children.Add($touch_bt)





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
$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$Health_UpperPart.Children.Add($close_bt)
$Health_UpperPart.Children.Add($maximize_bt)
$Health_UpperPart.Children.Add($minimize_bt)
$Health_UpperPart.Children.Add($BackToMain_bt)

# Create WrapPanel for buttons at the bottom
$Health_LowerPart = New-Object Windows.Controls.WrapPanel
$Health_LowerPart.Orientation = [Windows.Controls.Orientation]::Horizontal
$Health_LowerPart.HorizontalAlignment = [Windows.HorizontalAlignment]::Center
$Health_LowerPart.VerticalAlignment = [Windows.VerticalAlignment]::Bottom

# Create buttons for the bottom wrap panel
$bottomButton1 = & $mm -content "1" -onClick {  Add your action for bottomButton1 here }
$bottomButton2 = & $mm -content "2" -onClick {  Add your action for bottomButton2 here }
$bottomButton3 = & $mm -content "3" -onClick {  Add your action for bottomButton3 here }

# Add buttons to the bottom wrap panel
$Health_LowerPart.Children.Add($bottomButton1)
$Health_LowerPart.Children.Add($bottomButton2)
$Health_LowerPart.Children.Add($bottomButton3)

# Create buttons inside Health_Grid
$dism_bt = & $cs3 -content "DISM" -onClick { Start-Process -FilePath "DISM" -ArgumentList "/Online /Cleanup-Image /RestoreHealth" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$sfc_bt = & $cs3 -content "SFC" -onClick { Start-Process -FilePath "sfc" -ArgumentList "/scannow" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$chkdsk_bt = & $cs3 -content "Chkdsk" -onClick { Start-Process -FilePath "chkdsk" -ArgumentList "/f /r" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$diskcleanup_bt = & $cs3 -content "Disk Cleanup" -onClick { Start-Process -FilePath "cleanmgr" -ArgumentList "/sagerun:1" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$taskmanager_bt = & $cs3 -content "Task Manager" -onClick { Start-Process -FilePath "taskmgr" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$eventviewer_bt = & $cs3 -content "Event Viewer" -onClick { Start-Process -FilePath "eventvwr" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$flushdns_bt = & $cs3 -content "Flush DNS" -onClick { Start-Process -FilePath "cmd" -ArgumentList "/k ipconfig /flushdns" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }
$resetwinsock_bt = & $cs3 -content "Reset Winsock" -onClick { Start-Process -FilePath "cmd" -ArgumentList "/k netsh winsock reset" -Verb RunAs ; $Main_Panel.Content = $Health_Grid }

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

[Windows.Controls.Grid]::SetRow($eventviewer_bt, 3)
[Windows.Controls.Grid]::SetColumn($eventviewer_bt, 1)

[Windows.Controls.Grid]::SetRow($flushdns_bt,3)
[Windows.Controls.Grid]::SetColumn($flushdns_bt, 2)

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






$FFmpeg_Panel = New-Object Windows.Controls.StackPanel
$FFmpeg_Panel.Margin = New-Object Windows.Thickness 0

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$FFmpeg_Panel.Children.Add($close_bt)
$FFmpeg_Panel.Children.Add($maximize_bt)
$FFmpeg_Panel.Children.Add($minimize_bt)
$FFmpeg_Panel.Children.Add($BackToMain_bt)

$trim_bt = & $cs2 -content "Trim" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\trim.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$convert_bt = & $cs2 -content "Convert Video" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\convert.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$dimension_bt = & $cs2 -content "Video Dimension" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\dimension.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$imgdim_bt = & $cs2 -content "Image Dimension" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\imgdim.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }
$merge_bt = & $cs2 -content "Merge Videos" -onClick {  Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\ffmpeg\merge.ps1`"" ; $Main_Panel.Content = $FFmpeg_Panel  }

$FFmpeg_Panel.Children.Add($convert_bt)
$FFmpeg_Panel.Children.Add($dimension_bt)
$FFmpeg_Panel.Children.Add($imgdim_bt)
$FFmpeg_Panel.Children.Add($merge_bt)
$FFmpeg_Panel.Children.Add($trim_bt)





$Find_Panel = New-Object Windows.Controls.StackPanel
$Find_Panel.Margin = New-Object Windows.Thickness 0

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$Find_Panel.Children.Add($close_bt)
$Find_Panel.Children.Add($maximize_bt)
$Find_Panel.Children.Add($minimize_bt)
$Find_Panel.Children.Add($BackToMain_bt)

$find_file_bt = & $cs2 -content "Find File" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\find\find_file.ps1`"" ; $Main_Panel.Content = $Find_Panel }
$find_size_bt = & $cs2 -content "Find Size" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\find\find_size.ps1`"" ; $Main_Panel.Content = $Find_Panel }
$find_pattern_bt = & $cs2 -content "Find Pattern" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\find\find_pattern.ps1`"" ; $Main_Panel.Content = $Find_Panel }

$Find_Panel.Children.Add($find_file_bt)
$Find_Panel.Children.Add($find_size_bt)
$Find_Panel.Children.Add($find_pattern_bt)





$Folder_Panel = New-Object Windows.Controls.stackPanel      #WrapPanel
$Folder_Panel.Margin = New-Object Windows.Thickness 0

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$Folder_Panel.Children.Add($close_bt)
$Folder_Panel.Children.Add($maximize_bt)
$Folder_Panel.Children.Add($minimize_bt)
$Folder_Panel.Children.Add($BackToMain_bt)

$scoop_bt = & $fldr -content "Scoop" -onClick  { start-Process C:\Users\nahid\scoop ; $Main_Panel.Content = $Folder_Panel }
$startup_bt = & $fldr -content "Startup" -onClick  { start-Process "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" ; $Main_Panel.Content = $Folder_Panel }
$windowsapp_bt = & $fldr -content "WindowsApp" -onClick  { start-Process "C:\Program Files\WindowsApps" ; $Main_Panel.Content = $Folder_Panel }
$Packages_bt = & $fldr -content "Packages" -onClick  { start-Process "C:\Users\nahid\AppData\Local\Packages" ; $Main_Panel.Content = $Folder_Panel }
$appdata_bt = & $fldr -content "AppData" -onClick  { start-Process "C:\Users\nahid\AppData" ; $Main_Panel.Content = $Folder_Panel }
$apps_bt = & $fldr -content "All Apps" -onClick  { start-Process "shell:appsfolder" ; $Main_Panel.Content = $Folder_Panel }
$temp1_bt = & $fldr -content "TempAppDate 🗑️" -onClick  { start-Process "C:\Users\nahid\AppData\Local\Temp" ; $Main_Panel.Content = $Folder_Panel }
$temp2_bt = & $fldr -content "TempWindows 🗑️" -onClick  { start-Process "C:\Windows\Temp" ; $Main_Panel.Content = $Folder_Panel }
$song_bt = & $fldr -content "Song 🎶" -onClick  { start-Process "D:\song" ; $Main_Panel.Content = $Folder_Panel }
$sftr_bt = & $fldr -content "Software 🍎" -onClick  { start-Process "D:\software" ; $Main_Panel.Content = $Folder_Panel }
$git_bt = & $fldr -content "Git Projects" -onClick  { start-Process "D:\@git" ; $Main_Panel.Content = $Folder_Panel }

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
$Valorant_Panel.Margin = New-Object Windows.Thickness 0

$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$Valorant_Panel.Children.Add($close_bt)
$Valorant_Panel.Children.Add($maximize_bt)
$Valorant_Panel.Children.Add($minimize_bt)
$Valorant_Panel.Children.Add($BackToMain_bt)

$valo_ahk_bt = & $vlr -content "Valorant-AHK" -onClick { D:\@git\ms1\scripts\valorant\valo.ahk; $Main_Panel.Content = $Valorant_Panel}
$valorant_qbit_bt = & $vlr -content "Valorant + Qbit" -onClick  { Start-Process -FilePath "pwsh" -ArgumentList "-NoExit -File `"D:\@git\ms1\scripts\valorant\valo_qbit.ps1`"" ; $Main_Panel.Content = $Valorant_Panel }

$Valorant_Panel.Children.Add($valo_ahk_bt)
$Valorant_Panel.Children.Add($valorant_qbit_bt)



$Main_Panel.ShowDialog() | Out-Null
