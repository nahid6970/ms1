$close_bt       = & $xx     -content "X"           -onClick {$Main_Panel.Close()}
$maximize_bt    = & $mx  -content "⹇"              -onClick { if ($Main_Panel.WindowState -eq [Windows.WindowState]::Normal) { $Main_Panel.WindowState = [Windows.WindowState]::Maximized } else { $Main_Panel.WindowState = [Windows.WindowState]::Normal }}
$minimize_bt    = & $mm  -content "–"              -onClick { $Main_Panel.WindowState = [Windows.WindowState]::Minimized}
$Main_Panel.Content.Children.Add($close_bt)
$Main_Panel.Content.Children.Add($maximize_bt)
$Main_Panel.Content.Children.Add($minimize_bt)