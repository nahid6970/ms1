#Requires AutoHotkey v2.0

Run("*RunAs powershell.exe -Command restart-Service sshd", "", "Hide")
