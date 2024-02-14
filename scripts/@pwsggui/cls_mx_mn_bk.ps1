$xx = {
    param(
    [string]$content,
    [scriptblock]$onClick
    )
    $button = New-Object Windows.Controls.Button
    $button.Content = $content
    $button.Add_Click($onClick)
    $button.FontSize = 16
    $button.FontWeight = "Bold"
    $button.Width = 25
    $button.HorizontalAlignment = [Windows.HorizontalAlignment]::right
    $button.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(232, 17, 35))
    $button.BorderBrush = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    $button.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    return $button
    }
    
    $mm = {
    param(
    [string]$content,
    [scriptblock]$onClick
    )
    $button = New-Object Windows.Controls.Button
    $button.Content = $content
    $button.Add_Click($onClick)
    $button.FontSize = 16
    $button.FontWeight = "Bold"
    $button.Width = 25
    $button.HorizontalAlignment = [Windows.HorizontalAlignment]::right
    $button.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(72, 109, 194))
    $button.BorderBrush = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    $button.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    return $button
    }
    
    $mx = {
    param(
    [string]$content,
    [scriptblock]$onClick
    )
    $button = New-Object Windows.Controls.Button
    $button.Content = $content
    $button.Add_Click($onClick)
    $button.FontSize = 16
    $button.FontWeight = "Bold"
    $button.Width = 25
    $button.HorizontalAlignment = [Windows.HorizontalAlignment]::right
    $button.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(250, 138, 83))
    $button.BorderBrush = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    $button.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    return $button
    }
    
    $bk = {
    param(
    [string]$content,
    [scriptblock]$onClick
    )
    $button = New-Object Windows.Controls.Button
    $button.Content = $content
    $button.Add_Click($onClick)
    $button.FontSize = 16
    $button.FontWeight = "Bold"
    $button.Width = 25
    $button.HorizontalAlignment = [Windows.HorizontalAlignment]::right
    $button.Background = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    $button.BorderBrush = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(0, 0, 0))
    $button.Foreground = New-Object Windows.Media.SolidColorBrush ([Windows.Media.Color]::Fromrgb(247, 249, 255))
    return $button
    
    return $button
    }