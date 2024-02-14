$close_bt = & $xx -content "X" -onClick({$Main_Panel.Close()})
$maximize_bt = & $mx -content "⹇" -onClick({ if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }})
$minimize_bt = & $mm -content "–" -onClick({ $Main_Panel.WindowState = [Windows.WindowState]::Minimized})
$BackToMain_bt = & $bk -content "⇠" -onClick { $Main_Panel.Content = $BackToMain_bt.Tag ; $Main_Panel.Width = 400 ; $Main_Panel.Height = 700 }

$StartupApps_Panel.Children.Add($close_bt)
$StartupApps_Panel.Children.Add($maximize_bt)
$StartupApps_Panel.Children.Add($minimize_bt)
$StartupApps_Panel.Children.Add($BackToMain_bt)