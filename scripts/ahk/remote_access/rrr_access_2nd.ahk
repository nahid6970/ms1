#Requires AutoHotkey v2.0

; Path to PsExec and DisplaySwitch command
Run('C:\msBackups\PSTools\PsExec64.exe -i 1 "C:\msBackups\Display\DisplaySwitch.exe" /external', "", "Hide")
