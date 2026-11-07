#Requires AutoHotkey v2.0
#SingleInstance
Persistent

; Auto-elevate: re-launch this script as administrator if not already elevated.
if !A_IsAdmin {
    Run '*RunAs ' . A_AhkPath . ' "' . A_ScriptFullPath . '"'
    ExitApp
}

; Red tray icon to distinguish the elevated admin instance
TraySetIcon("C:\@delta\ms1\autohotkey\shortcut_manager\ahk_admin.ico")

;! === ADMIN SHORTCUTS (elevated) ===

;! Center Apps Window
LAlt & c:: {
    Center_Focused_Window()
    Center_Focused_Window() {
        ; Get the handle of the active (focused) window
        hwnd := WinGetID("A")
        ; Get the position and size of the active window
        WinGetPos(&x, &y, &w, &h, "ahk_id " hwnd)
        ; Get the screen width and height
        ScreenWidth := SysGet(78)
        ScreenHeight := SysGet(79)
        ; Calculate new position to center the window
        newX := (ScreenWidth - w) / 2
        newY := (ScreenHeight - h) / 2
        ; Move the window to the calculated position
        WinMove(newX, newY, , , "ahk_id " hwnd)
    }
}

;! Minimize Apps
#d:: {
    MinimizeActiveWindow()
    MinimizeActiveWindow() {
        hwnd := WinExist("A")
        if !hwnd
            return
        ; Method 1: Standard system command (best for most apps + many games)
        PostMessage(0x0112, 0xF020, 0, , hwnd)   ; WM_SYSCOMMAND + SC_MINIMIZE
        ; Method 2: Direct ShowWindow call (helps stubborn windows)
        DllCall("ShowWindow", "Ptr", hwnd, "Int", 6)  ; SW_MINIMIZE = 6
        ; Method 3: Fallback to WinMinimize
        try WinMinimize("ahk_id " hwnd)
    }
}

;! Game Speed Control
!g::Run('"D:\speed\src-tauri\target\release\tempo-speed-control.exe"', 'D:\speed\src-tauri\target\release', "Hide")
