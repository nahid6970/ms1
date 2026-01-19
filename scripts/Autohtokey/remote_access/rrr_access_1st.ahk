#Requires AutoHotkey v2.0

; Kill dnplayer.exe
Run("taskkill /F /IM dnplayer.exe",,"Hide")
; Kill python.exe
Run("taskkill /F /IM python.exe",,"Hide")
; Run the command

; Use PsExec to run the command in the interactive session
Run('C:\@delta\msBackups\PSTools\PsExec64.exe -i 1 "C:\@delta\msBackups\Display\DisplaySwitch.exe" /internal', "", "Hide")

