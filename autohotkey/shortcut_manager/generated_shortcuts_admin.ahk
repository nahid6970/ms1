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

RunWithoutConsole(commandLine, workingDir := "") {
    si := Buffer(A_PtrSize = 8 ? 104 : 68, 0)
    NumPut("UInt", si.Size, si, 0)
    pi := Buffer(A_PtrSize * 2 + 8, 0)
    cmd := Buffer(StrPut(commandLine, "UTF-16") * 2, 0)
    StrPut(commandLine, cmd, "UTF-16")
    if !DllCall("CreateProcessW", "Ptr", 0, "Ptr", cmd, "Ptr", 0, "Ptr", 0, "Int", 0, "UInt", 0x08000000, "Ptr", 0, "Ptr", workingDir ? StrPtr(workingDir) : 0, "Ptr", si, "Ptr", pi, "Int")
        throw OSError()
    DllCall("CloseHandle", "Ptr", NumGet(pi, 0, "Ptr"))
    DllCall("CloseHandle", "Ptr", NumGet(pi, A_PtrSize, "Ptr"))
}

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
!g::RunWithoutConsole('"D:\speed\src-tauri\target\release\tempo-speed-control.exe"', 'D:\speed\src-tauri\target\release')
