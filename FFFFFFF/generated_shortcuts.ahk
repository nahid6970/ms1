#Requires AutoHotkey v2.0
#SingleInstance
Persistent

;! === SCRIPT SHORTCUTS ===
;! Open Terminal Admin
;! Opens PowerShell as administrator
!x::RunWait("pwsh -Command `"cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs`"", , "Hide")

;! Run Python Script
;! Opens run.py in the ms1 directory
!Space::Run("C:\Users\nahid\ms\ms1\run.py", , "Show")

;! Monitor Internal
;! Switch to internal monitor only
RAlt & Numpad1::Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")

;! Monitor External
;! Switch to external monitor only
RAlt & Numpad2::Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")

;! Monitor Extend
;! Extend display to both monitors
RAlt & Numpad3::Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")

;! Bio GUI
;! Opens Bio.ahk GUI
!b::Run("C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\gui\Bio.ahk", "", "Hide")

;! Ultimate GUI
;! Opens Ultimate_Gui.py
!u::Run("C:\Users\nahid\ms\ms1\Ultimate_Gui.py", "", "Hide")

;! Always On Top Toggle
;! Toggles always on top for active window
#t:: {
    Always_on_Top()
    Always_on_Top(){
        static alwaysOnTop := false
        if (alwaysOnTop) {
            WinSetAlwaysOnTop(false, "A")
        } else {
            WinSetAlwaysOnTop(true, "A")
        }
        alwaysOnTop := !alwaysOnTop
    }
}

;! Center Window
;! Centers the focused window on screen
LAlt & c:: {
    Center_Focused_Window()
    Center_Focused_Window() {
        hwnd := WinGetID("A")
        WinGetPos(&x, &y, &w, &h, "ahk_id " hwnd)
        ScreenWidth := SysGet(78)
        ScreenHeight := SysGet(79)
        newX := (ScreenWidth - w) / 2
        newY := (ScreenHeight - h) / 2
        WinMove(newX, newY, , , "ahk_id " hwnd)
    }
}

;! Kill Foreground Process
;! Forcefully kills the process under mouse cursor
!q:: {
    KillForeground()
    KillForeground() {
        MouseGetPos(, , &WinID)
        ProcessID := WinGetPID("ahk_id " WinID)
        Run("taskkill /f /pid " ProcessID, , "Hide")
    }
}

;! === TEXT SHORTCUTS ===
;! AutoHotkey Version 1
;! Inserts AHK v1 header requirement
::;v1::#Requires AutoHotkey v1.0

;! AutoHotkey Version 2
;! Inserts AHK v2 header requirement
::;v2::#Requires AutoHotkey v2.0

;! Registry Run Path
;! Windows startup registry path
::;run::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run

;! PowerShell Symlink
;! PowerShell command to create symbolic link
::;mklink::New-Item -ItemType SymbolicLink -Path "Fake" -Target "Original" -Force

;! Arrow Symbol
;! Right-pointing arrow symbol
::;--::nigga
