#Requires AutoHotkey v2.0

; wont pop up older verson running
#SingleInstance 
Persistent


; Set the tray icon
TraySetIcon("C:\msBackups\icon\shutdown3.png")

; Create a custom tray menu
Tray := A_TrayMenu
Tray.Delete() ; Remove default items
Tray.Add("Restart Explorer", (*) => RestartExplorer()) ; Attach the function
Tray.Add("Reset WS", (*) => Toggle_Reset_Workspace()) ; Attach the function
Tray.Add() ; Add a separator
Tray.Add("Exit", (*) => ExitApp()) ; Add Exit button

; Function to restart explorer.exe using PowerShell
RestartExplorer() {
    Run('pwsh -Command "Stop-Process -Name explorer -Force; Start-Process explorer"', , "")
}





RAlt & Numpad1::Run("C:\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")
RAlt & Numpad2::Run("C:\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")
RAlt & Numpad3::Run("C:\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")


^!t::Toggle_Reset_Workspace()
taskbarVisible := 1  ; 1 for visible, 0 for hidden
Toggle_Reset_Workspace() {
    global taskbarVisible
    ; Get the handle of the taskbar
    taskbarHandle := WinGetID("ahk_class Shell_TrayWnd")
    if taskbarVisible {
        ; Hide the taskbar
        WinSetExStyle("+0x80", "ahk_id " taskbarHandle)  ; WS_EX_TOOLWINDOW
        WinSetExStyle("+0x20", "ahk_id " taskbarHandle)  ; WS_EX_TRANSPARENT
        WinSetStyle("-0x800000", "ahk_id " taskbarHandle)  ; WS_DISABLED
        taskbarVisible := 0
    } else {
        ; Unhide the taskbar
        WinSetStyle("+0x800000", "ahk_id " taskbarHandle)  ; WS_DISABLED
        WinSetExStyle("-0x80", "ahk_id " taskbarHandle)  ; WS_EX_TOOLWINDOW
        WinSetExStyle("-0x20", "ahk_id " taskbarHandle)  ; WS_EX_TRANSPARENT
        taskbarVisible := 1
    }
}
