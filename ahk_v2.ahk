#Requires AutoHotkey v2.0

;! wont pop up older verson running
#SingleInstance 
Persistent

;! v2 startups
#Include C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\tray.ahk
#Include C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\shadowFight3.ahk
#Include C:\Users\nahid\ms\ms1\scripts\pyautogui\Clash_of_Clans.ahk
#Include C:\Users\nahid\ms\ms1\scripts\Autohtokey\math.ahk
#Include "C:\Users\nahid\ms\ms1\FFFFFFF\generated_shortcuts.ahk"
#Include "C:\Users\nahid\ms\ms1\scripts\Autohtokey\gemini_helper.ahk"
; #Include "C:\Users\nahid\ms\ms1\scripts\Autohtokey\recordKey.ahk"

;! Explorer Tab Manager
SetTimer(ManageExplorerTabs, 200)

;! v1 startups
; Run("C:\Users\nahid\ms\ms1\scripts\ahk\old\shadowFight3.ahk")
; Run("control.exe folders")

;! AHK Related
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R




#HotIf WinActive("ahk_exe chrome.exe")
; Switch to the last visited tab (most recent in history)
switchToLastTab() {
    Send("^+a")           ; Open Chrome's tab search  
    Sleep(100)            ; Wait for search to open
    Send("{Enter}")       ; Press Enter to go to first result (last visited tab)
}
; Use Ctrl+Tab to switch to the last tab you were on
^Tab::switchToLastTab()

#HotIf




;! gui
; !u::Run("C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\gui\Ultimate_Gui.ahk", "", "Hide")







^!t::Toggle_Reset_Workspace() ; Define the shortcut outside
Toggle_Reset_Workspace() {
    static taskbarVisible := 1 ; Initialize the taskbar visibility state (1 for visible, 0 for hidden)

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








#HotIf WinExist("ahk_exe dnplayer.exe") ; Apply condition for dnplayer.exe
!v::Center_Focused_Window_modLDplayer() ; Define the shortcut outside
#HotIf  ; End the condition

Center_Focused_Window_modLDplayer() {
    static isFirstPosition := true ; Initialize the toggle state (true for first position)
    hwnd := WinGetID("ahk_exe dnplayer.exe") ; Get the handle of dnplayer.exe

    ; Check if the window is active
    if (!WinActive("ahk_id " hwnd)) {
        WinActivate("ahk_id " hwnd) ; Activate the window if it's not focused
        WinWaitActive("ahk_id " hwnd) ; Wait until the window is active
    }

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


;! Explorer Tab Manager Function
ManageExplorerTabs() {
    static knownExplorers := Map()
    
    ; Get current explorer windows
    currentExplorers := WinGetList("ahk_class CabinetWClass")
    
    ; Check for new windows
    for hWnd in currentExplorers {
        if (!knownExplorers.Has(hWnd)) {
            ; This is a new window
            
            ; Check if we have other 'valid' explorer windows open
            targetHWnd := 0
            
            for knownhWnd, _ in knownExplorers {
                if WinExist(knownhWnd) {
                     ; Found a target, make sure it's not the same window just in case (though Has check prevents that)
                    targetHWnd := knownhWnd
                    break 
                }
            }
            
            if (targetHWnd) {
                ; Merge logic
                try {
                    ; Get path
                    path := ""
                    sh := ComObject("Shell.Application")
                    for window in sh.Windows {
                        try {
                            if (window.hwnd = hWnd) {
                                path := window.Document.Folder.Self.Path
                                break
                            }
                        }
                    }
                    
                    if (path != "") {
                        ; Close the new isolated window
                        WinClose(hWnd)
                        
                        ; Activate the existing window
                        WinActivate(targetHWnd)
                        if WinWaitActive(targetHWnd,, 1) {
                            ; Open New Tab
                            Send("^t") 
                            Sleep(150)
                            ; Focus Address Bar and Navigate
                            Send("!d") 
                            Sleep(50)
                            SendText(path)
                            Sleep(50)
                            Send("{Enter}")
                            ; Optional: Move focus back
                            Send("{Esc}") 
                        }
                        
                        ; Mark as known so we don't process again if close failed
                        knownExplorers[hWnd] := true 
                    } else {
                        ; Could not get path, let it be
                        knownExplorers[hWnd] := true 
                    }
                } catch {
                     knownExplorers[hWnd] := true 
                }
            } else {
                ; First window, just track it
                knownExplorers[hWnd] := true
            }
        }
    }
    
    ; Cleanup closed windows from known list
    listToDelete := []
    for hWnd, _ in knownExplorers {
        if (!WinExist(hWnd))
            listToDelete.Push(hWnd)
    }
    for hWnd in listToDelete {
        knownExplorers.Delete(hWnd)
    }
}









; #s:: ; Define the shortcut outside
; {
;     global ; Declare global scope for variables
;     i := 1 ; Initialize the variable if not already set
 
;     ; Get the process ID of the active window
;     PID := WinGetPID("A")
 
;     ; Set process priority based on the value of 'i'
;     ProcessSetPriority(((i = 1) ? "L" : ((i = 2) ? "N" : "H")), PID)
 
;     ; Update 'i' for the next use, cycling through 1, 2, and 3
;     i := (i > 2) ? 1 : i + 1
; }
 
 
 
; ; Detect when the right mouse button is pressed down
; RButton::
; {
;     ; Keep sending 'j' while the right mouse button is held down
;     while (GetKeyState("RButton", "P")) {
;         Send("j")
;         Sleep(50) ; Adjust the delay for how fast 'j' is sent
;     }
; }
 
 
 
; Persistent
; SetTitleMatchMode(2) ; Allow partial matching of window titles
; ; Allow the right mouse button to work normally in other apps
; ~RButton::
; {
;     ; Check if 'dnplayer' is the active window
;     if (WinActive("ahk_exe dnplayer.exe")) {
;         ; Keep sending 'j' while the right mouse button is held down
;         while (GetKeyState("RButton", "P") && WinActive("ahk_exe dnplayer.exe")) {
;             Send("j")
;             Sleep(50) ; Adjust the delay for how fast 'j' is sent
;         }
;     }
;     return
; }
