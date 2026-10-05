#Requires AutoHotkey v2.0

; Set the tray icon
TraySetIcon("shell32.dll", 278)
; Create a custom tray menu
Tray := A_TrayMenu
Tray.Delete() ; Remove default items
Tray.Add("Restart Explorer", (*) => RestartExplorer())
Tray.SetIcon("Restart Explorer", "shell32.dll", 239)
Tray.Add("Screen Dimmer", (*) => Run("C:\@delta\ms1\scripts\Autohtokey\version1\Display\ScreenDimmer.ahk"))
Tray.SetIcon("Screen Dimmer", "shell32.dll", 35)
Tray.Add("Reset WS", (*) => Toggle_Reset_Workspace())
Tray.SetIcon("Reset WS", "shell32.dll", 238)
Tray.Add("Suspend", (*) => Suspend(-1))
Tray.Default := "Suspend"
Tray.ClickCount := 1
Tray.Add() ; Add a separator
Tray.Add("🕐 BD / ET Time", (*) => ToggleTimezone())
Tray.SetIcon("🕐 BD / ET Time", "shell32.dll", 24)
Tray.Add() ; Add a separator
Tray.Add("Exit", (*) => ExitApp()) ; Add Exit button
Tray.SetIcon("Exit","shell32.dll", 240)

; Function to restart explorer.exe using PowerShell
RestartExplorer() {
    Run('pwsh -Command "Stop-Process -Name explorer -Force; Start-Process explorer"', , "")
}

; Rotate between Bangladesh Time (UTC+6) and Eastern Time (US & Canada)
ToggleTimezone() {
    static isBD := true

    if (isBD) {
        ; Switch TO Bangladesh Standard Time
        tzId := "Bangladesh Standard Time"
        label := "🇧🇩 Switched to Bangladesh Time (UTC+6)"
    } else {
        ; Switch TO Eastern Time
        tzId := "Eastern Standard Time"
        label := "🇺🇸 Switched to Eastern Time (US & Canada)"
    }

    ; Run PowerShell as admin to set the timezone
    Run('pwsh -Command "Set-TimeZone -Id \"' tzId '\""', , "RunAs")

    ToolTip(label)
    SetTimer(() => ToolTip(), -3000)

    isBD := !isBD
}