#Requires AutoHotkey v2.0

; Kill dnplayer.exe
Run("taskkill /F /IM dnplayer.exe",,"Hide")
; Kill python.exe
Run("taskkill /F /IM python.exe",,"Hide")
; Run the command

; Use PsExec to run the command in the interactive session
Run('C:\Users\nahid\ms\msBackups\PSTools\PsExec64.exe -i 1 "C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe" /internal', "", "Hide")

