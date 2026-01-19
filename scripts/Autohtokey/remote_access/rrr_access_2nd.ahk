#Requires AutoHotkey v2.0

; Path to PsExec and DisplaySwitch command
Run('C:\@delta\msBackups\PSTools\PsExec64.exe -i 1 "C:\@delta\msBackups\Display\DisplaySwitch.exe" /external', "", "Hide")
