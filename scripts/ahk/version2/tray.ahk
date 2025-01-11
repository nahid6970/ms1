#Requires AutoHotkey v2.0

; Set the tray icon
TraySetIcon("C:\msBackups\icon\shutdown3.png")
; Create a custom tray menu
Tray := A_TrayMenu
Tray.Delete() ; Remove default items
Tray.Add("Restart Explorer", (*) => RestartExplorer())
Tray.SetIcon("Restart Explorer", "C:\msBackups\icon\system_icon\shell32\965.ico")
Tray.Add("Screen Dimmer", (*) => Run("C:\ms1\scripts\ahk\version1\Display\ScreenDimmer.ahk"))
Tray.Add("Reset WS", (*) => Toggle_Reset_Workspace())
Tray.Add() ; Add a separator
Tray.Add("Exit", (*) => ExitApp()) ; Add Exit button
Tray.SetIcon("Exit","C:\msBackups\icon\system_icon\shell32\295.ico")

; Function to restart explorer.exe using PowerShell
RestartExplorer() {
    Run('pwsh -Command "Stop-Process -Name explorer -Force; Start-Process explorer"', , "")
}