#Requires AutoHotkey v2.0
Run("powershell.exe -Command Start-Process 'C:\\@delta\\msBackups\\Display\\win11-toggle-rounded-corners.exe' -ArgumentList '--disable' -Verb RunAs", "", "Hide")
