#Requires AutoHotkey v2.0

; wont pop up older verson running
#SingleInstance 
Persistent

; Set the tray icon
TraySetIcon("C:\msBackups\icon\shutdown3.png")

; Create a custom tray menu
Tray := A_TrayMenu
Tray.Delete() ; Remove default items

Tray.Add("Restart Explorer", (*) => RestartExplorer())
Tray.SetIcon("Restart Explorer", "C:\msBackups\icon\system_icon\imageres\31.ico")

Tray.Add("Reset WS", (*) => Toggle_Reset_Workspace())

Tray.Add() ; Add a separator
Tray.Add("Exit", (*) => ExitApp()) ; Add Exit button
Tray.SetIcon("Exit","C:\msBackups\icon\system_icon\shell32\295.ico")

; Function to restart explorer.exe using PowerShell
RestartExplorer() {
    Run('pwsh -Command "Stop-Process -Name explorer -Force; Start-Process explorer"', , "")
}


#Include C:\ms1\scripts\ahk\v2_shadowFight3.ahk

; Run the v1 AHK script when this v2 script starts
; Run("C:\ms1\scripts\ahk\old\shadowFight3.ahk")



;;* AHK Related
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

RAlt & Numpad1::Run("C:\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")
RAlt & Numpad2::Run("C:\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")
RAlt & Numpad3::Run("C:\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")

!b::Run("C:\ms1\scripts\ahk\Bio.ahk", "", "Hide")
!u::Run("C:\ms1\scripts\ahk\Ultimate_Gui.ahk", "", "Hide")
^!n::Run("C:\ms1\scripts\ahk\v1_VScode_OpenWith.ahk", "", "Hide")

!e::Run('pwsh -c explorer.exe', , 'Hide')



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



#t::Always_on_Top()
Always_on_Top(){
    static alwaysOnTop := false  ; Static variable to track the AlwaysOnTop state
    if (alwaysOnTop) {
        WinSetAlwaysOnTop(false, "A")  ; Remove AlwaysOnTop
    } else {
        WinSetAlwaysOnTop(true, "A")   ; Set AlwaysOnTop
    }
    alwaysOnTop := !alwaysOnTop  ; Toggle the state
}



!c::Center_Focused_Window()
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



^!b::Toggle_Screen_Blackout()
; Define a variable to track the state of the screen blackout
blackoutState := 0
; Define a global variable to store the Gui object
myGui := ""

; Define a function to toggle the screen blackout
Toggle_Screen_Blackout() {
    global blackoutState, myGui  ; Declare the variables as global so they can be accessed inside the function
    
    if (blackoutState = 0) {
        ; If the screen is not blacked out, create a black fullscreen window
        blackoutState := 1

        ; Create the black window to cover the entire screen
        myGui := Gui()
        myGui.Opt("+LastFound +AlwaysOnTop -Caption +ToolWindow") ; Remove caption and border
        myGui.BackColor := "Black"
        myGui.Show("w" . A_ScreenWidth . " h" . A_ScreenHeight . " x0 y0 NoActivate")
    } else {
        ; If the screen is already blacked out, close the window
        blackoutState := 0
        myGui.Destroy()
        myGui := ""  ; Clear the myGui object
    }
}



^!w::Toggle_Screen_Whiteout()
; Define a variable to track the state of the screen blackout
whiteState := 0
; Define a global variable to store the Gui object
myGui := ""

; Define a function to toggle the screen blackout
Toggle_Screen_Whiteout() {
    global whiteState, myGui  ; Declare the variables as global so they can be accessed inside the function

    if (whiteState = 0) {
        ; If the screen is not blacked out, create a black fullscreen window
        whiteState := 1

        ; Create the black window to cover the entire screen
        myGui := Gui()
        myGui.Opt("+LastFound +AlwaysOnTop -Caption +ToolWindow") ; Remove caption and border
        myGui.BackColor := "ffffff"
        myGui.Show("w" . A_ScreenWidth . " h" . A_ScreenHeight . " x0 y0 NoActivate")
    } else {
        ; If the screen is already blacked out, close the window
        whiteState := 0
        myGui.Destroy()
        myGui := ""  ; Clear the myGui object
    }
}



!q::KillForeground()
KillForeground() {
    ; Get the window handle of the window under the mouse cursor
    MouseGetPos(, , &WinID)
    
    ; Get the process ID of the window
    ProcessID := WinGetPID("ahk_id " WinID)
    
    ; Use taskkill command to forcefully terminate the process by ID
    Run("taskkill /f /pid " ProcessID, , "Hide")
}



; ^!m::CopyPath_File()
; CopyPath_File() {
;     ClipboardBackup := ClipboardAll()
;     A_Clipboard := "" 
;     Send("^c")
;     Errorlevel := !ClipWait(1)
;     if ErrorLevel
;     {
;     MsgBox("No valid file path found.")
;     }
;     else
;     {
;     ClipBoardContent := A_Clipboard
;     ; V1toV2: StrReplace() is not case sensitive
;     ; check for StringCaseSense in v1 source script
;     ; and change the CaseSense param in StrReplace() if necessary
;     ClipBoardContent := StrReplace(ClipBoardContent, "`n", "`t")
;     A_Clipboard := ClipboardBackup
;     A_Clipboard := ClipBoardContent
;     TrayTip("Copy as Path", "Copied `"" ClipBoardContent "`" to clipboard.")
;     }}


^!m::CopyPath_File()
CopyPath_File() {
    ClipboardBackup := ClipboardAll()  ; Backup current clipboard content
    A_Clipboard := ""  ; Clear the clipboard
    Send("^c")  ; Simulate pressing Ctrl + C to copy
    Errorlevel := !ClipWait(1)  ; Wait for the clipboard content
    if (Errorlevel) {
        MsgBox("No valid file path found.")
    } else {
        ClipBoardContent := A_Clipboard  ; Get the copied content
        ; Prompt for the type of path you want (backslash, double backslash, or normal slash)
        choice := MsgBox("Choose the format for the path: `nYes: Double Backslash `nNo: Single Backslash `nCancel: Normal Slash", "Choose Path Format", 3)  ; Message box with options

        if (choice = "Yes") {  ; Double backslash
            ClipBoardContent := StrReplace(ClipBoardContent, "\", "\\")
        } else if (choice = "No") {  ; Single backslash
            ; Do nothing as we keep the default single backslash
        } else if (choice = "Cancel") {  ; Normal slash
            ClipBoardContent := StrReplace(ClipBoardContent, "\", "/")
        }
        A_Clipboard := ClipboardBackup  ; Restore original clipboard content
        A_Clipboard := ClipBoardContent  ; Set the clipboard to the modified content
        TrayTip("Copy as Path", "Copied path: " ClipBoardContent " to clipboard.")
    }
}