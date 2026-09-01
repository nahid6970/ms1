Write-Host "Requesting admin privileges..." -ForegroundColor Cyan

Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoExit -Command `"
    Write-Host 'Disabling Windows Defender real-time monitoring...' -ForegroundColor Yellow;
    Set-MpPreference -DisableRealtimeMonitoring `$true;
    `$status = (Get-MpPreference).DisableRealtimeMonitoring;
    if (`$status -eq `$true) {
        Write-Host 'Done. Real-time monitoring is now DISABLED.' -ForegroundColor Green
    } else {
        Write-Host 'Something went wrong. Real-time monitoring may still be active.' -ForegroundColor Red
    };
    Write-Host 'Press any key to close...';
    `$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
`""
