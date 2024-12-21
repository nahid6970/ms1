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

; include files
#Include C:\ms1\scripts\ahk\version2\shadowFight3.ahk


; add v1 startups
; Run("C:\ms1\scripts\ahk\old\shadowFight3.ahk")
; Run("control.exe folders")


 #Requires AutoHotkey v2.0 

;;* AHK Related
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

^!+r:: {
    ; Kill dnplayer.exe
    Run("taskkill /F /IM dnplayer.exe",,"Hide")
    ; Kill python.exe
    Run("taskkill /F /IM python.exe",,"Hide")
    ; Run the command
    Run("C:\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")
}


; monitorcls
RAlt & Numpad1::Run("C:\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")
RAlt & Numpad2::Run("C:\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")
RAlt & Numpad3::Run("C:\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")

; gui
!b::Run("C:\ms1\scripts\ahk\version2\gui\Bio.ahk", "", "Hide")
!u::Run("C:\ms1\scripts\ahk\version2\gui\Ultimate_Gui.ahk", "", "Hide")

; shortcuts
^!n::Run("C:\ms1\scripts\ahk\version1\VScode_OpenWith.ahk", "", "Hide")
RAlt & -::Run("C:\ms1\scripts\ahk\version1\text\Replace_Dash_W_Space.ahk", "", "Hide")
!e::Run('pwsh -c explorer.exe', , 'Hide')
#x::Run("C:\ms1\mypygui.py", , "Hide")

; text
::;v1:: {#}Requires AutoHotkey v1.0
::;v2:: {#}Requires AutoHotkey v2.0

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



LAlt & c::Center_Focused_Window()
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




#HotIf WinActive("ahk_exe dnplayer.exe", )
!v::Center_Focused_Window_modLDplayer()
#HotIf  ; End the condition
; Initialize a variable to keep track of the toggle state
isFirstPosition := true
Center_Focused_Window_modLDplayer() {
    global isFirstPosition  ; Access the toggle variable
    ; Get the handle of the dnplayer.exe window
    hwnd := WinGetID("A")
    ; Toggle between the two positions
    if (isFirstPosition) {
        ; Set the window to x=1250, y=120
        WinMove(159, 49, , , "ahk_id " hwnd)
    } else {
        ; Set the window to x=1150, y=550
        WinMove(159, 865, , , "ahk_id " hwnd)
    }
    ; Toggle the position state for the next activation
    isFirstPosition := !isFirstPosition
}



#HotIf  ; Remove window-specific condition for general usage
; Define a shortcut to show the position of the foreground window under the mouse
^!v::ShowWindowPositionUnderMouse()
ShowWindowPositionUnderMouse() {
    ; Get the handle of the active (foreground) window
    hwnd := WinGetID("A")
    ; Get the position of the active window
    WinGetPos(&x, &y, &w, &h, "ahk_id " hwnd)
    ; Display the starting x and y coordinates as a tooltip under the mouse
    MouseGetPos(&mouseX, &mouseY)  ; Get the current mouse position
    ToolTip("Starting Position: `nX: " x "`nY: " y, mouseX, mouseY)
    ; Hide the tooltip after 2 seconds
    SetTimer(HideToolTip,-2000)
}
HideToolTip()
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ToolTip()  ; Clear the tooltip
return
} ; V1toV2: Added bracket in the end



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



^!m::CopyPath_File()
CopyPath_File() {
    ClipboardBackup := ClipboardAll()
    A_Clipboard := "" 
    Send("^c")
    Errorlevel := !ClipWait(1)
    if ErrorLevel
    {
    MsgBox("No valid file path found.")
    }
    else
    {
    ClipBoardContent := A_Clipboard
    ; V1toV2: StrReplace() is not case sensitive
    ; check for StringCaseSense in v1 source script
    ; and change the CaseSense param in StrReplace() if necessary
    ClipBoardContent := StrReplace(ClipBoardContent, "`n", "`t")
    A_Clipboard := ClipboardBackup
    A_Clipboard := ClipBoardContent
    TrayTip("Copy as Path", "Copied `"" ClipBoardContent "`" to clipboard.")
    }}



    ^!+Enter::
    ; Save the current clipboard content (the path of the script)
{ ; V1toV2: Added bracket
global ; V1toV2: Made function global
    ClipSaved := ClipboardAll()
    A_Clipboard := ""               ; Clear clipboard
    ; Get the active window title
    ActiveTitle := WinGetTitle("A")
    ; If the active window is VSCode, simulate the shortcut to copy the file path
    if InStr(ActiveTitle, "Visual Studio Code") {
        ; Simulate VSCode's shortcut to copy the current file path (Shift + Alt + C)
        Send("+!c")
        Errorlevel := !ClipWait(1)               ; Wait until clipboard has content
    } else {
        ; Send Ctrl+C to copy the selected file path in other environments
        Send("^c")
        Errorlevel := !ClipWait(1)               ; Wait until clipboard has content
    }
    if (A_Clipboard != "") {
        ; Get the selected file path from the clipboard
        FilePath := A_Clipboard
        Ext := SubStr(FilePath, (InStr(FilePath, ".", 0, -1) + 1)<1 ? (InStr(FilePath, ".", 0, -1) + 1)-1 : (InStr(FilePath, ".", 0, -1) + 1))
        ; Check the extension and run the appropriate command
        if (Ext = "py") {
            Run("cmd /k python `"" FilePath "`"", , , &PID)
        } else if (Ext = "ps1") {
            Run("cmd /k powershell -ExecutionPolicy Bypass -File `"" FilePath "`"", , , &PID)
        } else if (Ext = "bat") {
            Run("cmd /k `"" FilePath "`"", , , &PID)
        } else if (Ext = "ahk") {
            Run("cmd /k `"" FilePath "`"", , , &PID)
        } else {
            MsgBox("Unsupported file type: " Ext)
        }
    } else {
        MsgBox("No file path selected or copied.")
    }
    ; Restore original clipboard content
    A_Clipboard := ClipSaved
    return
} ; V1toV2: Added bracket in the end