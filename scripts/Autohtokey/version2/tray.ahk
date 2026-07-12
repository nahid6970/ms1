#Requires AutoHotkey v2.0

; Set the tray icon
TraySetIcon("shell32.dll", 278)
; Create a custom tray menu
Tray := A_TrayMenu
Tray.Delete() ; Remove default items
Tray.Add("Restart Explorer", (*) => RestartExplorer())
Tray.SetIcon("Restart Explorer", "shell32.dll", 239)
Tray.Add("Screen Dimmer", (*) => Run("C:\@delta\ms1\scripts\Autohtokey\version1\Display\ScreenDimmer.ahk"))
Tray.Add("Reset WS", (*) => Toggle_Reset_Workspace())
Tray.Add("Suspend", (*) => Suspend(-1))
Tray.Default := "Suspend"
Tray.ClickCount := 1
Tray.Add() ; Add a separator
Tray.Add("Exit", (*) => ExitApp()) ; Add Exit button
Tray.SetIcon("Exit","shell32.dll", 240)

; Function to restart explorer.exe using PowerShell
RestartExplorer() {
    Run('pwsh -Command "Stop-Process -Name explorer -Force; Start-Process explorer"', , "")
}