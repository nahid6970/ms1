;;* AHK Related
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

;;! Kill Commands
!+v::RunWait, taskkill /f /im VALORANT-Win64-Shipping.exe,,Hide
!+o::RunWait, taskkill /f /im whkd.exe,,Hide
!+p::RunWait, taskkill /f /im python.exe
!+g::RunWait, taskkill /f /im glazewm.exe,,Hide
!+k::RunWait, taskkill /f /im komorebi.exe,,Hide
~Esc & q::KillForeground()

;;* Start Apps / Scripts
#x::RunWait, C:\ms1\mypygui.py ,,Hide                                                  ;* mypygui
!y::RunWait, python.exe C:\ms1\yasb\main.py,,Hide                                      ;* yasb
!r::RunWait, python.exe C:\ms1\running_apps.py,,Hide                                   ;* running apps
!o::RunWait, C:\Users\nahid\scoop\apps\whkd\current\whkd.exe,,Hide                     ;* whkd
!g::RunWait, C:\Users\nahid\scoop\apps\glazewm\current\GlazeWM.exe,,Hide               ;* GlazeWM
!x::RunWait, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs",,Hide ;* cmd as admin
!k::RunWait, komorebic start,,Hide                                                     ;* Komorebi

;;* Komorebic Commands
Pause::Run, komorebic quick-load-resize,,Hide
Esc & w::Run, komorebic toggle-float,,Hide

;;* Others
!1::ChangeMonitorApps()
#t:: WinSet, AlwaysOnTop, Toggle, A
^!h::ToggleHiddenFiles()
^!m::CopyPath_File()
^!n::VScode_OpenWith()
^!o::CopyPath_DoubleSlash()
^!p::CopyPath_wsl()
^+Esc::Run pwsh -c Taskmgr.exe,,Hide

;*   $$$$$$\  $$\                  $$\     
;*  $$  __$$\ $$ |                 $$ |    
;*  $$ /  \__|$$$$$$$\   $$$$$$\ $$$$$$\   
;*  $$ |      $$  __$$\  \____$$\\_$$  _|  
;*  $$ |      $$ |  $$ | $$$$$$$ | $$ |    
;*  $$ |  $$\ $$ |  $$ |$$  __$$ | $$ |$$\ 
;*  \$$$$$$  |$$ |  $$ |\$$$$$$$ | \$$$$  |
;*   \______/ \__|  \__| \_______|  \____/ 

;! Valorant Trash Talk
::;vv1::u guys r so trash garbage get good..
::;vv2::trash garbage stupid noobs..
::;vv3::stupid kids get good.

;! keyboard mod buttons
::;a::ALT
::;c::CTRL
::;s::SHIFT
::;ca::CTRL{+}ALT
::;cs::CTRL{+}SHIFT
::;csa::CTRL{+}SHIFT{+}ALT
::;sa::SHIFT{+}ALT
::;ss::<SPACE>

::;;::,=:[]()
::;font::font=("Jetbrainsmono nfp", 12, "bold")

;*   $$$$$$\  $$\                                      $$\  $$\   $$\ $$\       $$\           
;*  $$  __$$\ $$ |                                    $$  | $$ |  $$ |\__|      $$ |          
;*  $$ /  \__|$$$$$$$\   $$$$$$\  $$\  $$\  $$\      $$  /  $$ |  $$ |$$\  $$$$$$$ | $$$$$$\  
;*  \$$$$$$\  $$  __$$\ $$  __$$\ $$ | $$ | $$ |    $$  /   $$$$$$$$ |$$ |$$  __$$ |$$  __$$\ 
;*   \____$$\ $$ |  $$ |$$ /  $$ |$$ | $$ | $$ |   $$  /    $$  __$$ |$$ |$$ /  $$ |$$$$$$$$ |
;*  $$\   $$ |$$ |  $$ |$$ |  $$ |$$ | $$ | $$ |  $$  /     $$ |  $$ |$$ |$$ |  $$ |$$   ____|
;*  \$$$$$$  |$$ |  $$ |\$$$$$$  |\$$$$$\$$$$  | $$  /      $$ |  $$ |$$ |\$$$$$$$ |\$$$$$$$\ 
;*   \______/ \__|  \__| \______/  \_____\____/  \__/       \__|  \__|\__| \_______| \_______|

; ^!h::
; RegRead, HiddenFiles_Status, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced, Hidden
; If (HiddenFiles_Status = 2)
; {
; RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced, Hidden, 1
; SendMessage, 0x111, 4146,,, ahk_class Progman
; }
; Else
; {
; RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced, Hidden, 2
; SendMessage, 0x111, 4146,,, ahk_class Progman
; }
; return

; ;! Initialize a variable to keep track of the toggle state
; toggleState := 0
; ^!h::
;     ; Launch Control Panel with the "folders" argument
;     Run, control.exe folders,, Max
;     ; Wait for the Control Panel window to open (adjust the sleep time as needed)
;     Sleep, 500
;     ; Send keys to navigate to the "View" tab
;     Send, ^{Tab}
;     Send, {Tab}
;     ; Wait for the "View" tab to be selected
;     Sleep, 500
;     ; Send keys to navigate to the "Hidden files and folders" options
;     Loop % (toggleState ? 8 : 7) {
;         Send, {Down}
;         Sleep, 1
;     }
;     ; Toggle the option
;     Send, {Space}
;     ; Close the Control Panel window
;     Send, {Tab 2}{Enter}
;     ; Toggle the state for the next time
;     toggleState := !toggleState
; return

ToggleHiddenFiles() {
    ; Initialize a static variable to keep track of the toggle state
    static toggleState := 0

    ; Launch Control Panel with the "folders" argument
    Run, control.exe folders,, Max
    ; Wait for the Control Panel window to open (adjust the sleep time as needed)
    Sleep, 500
    ; Send keys to navigate to the "View" tab
    Send, ^{Tab}
    Send, {Tab}

    ; Wait for the "View" tab to be selected
    Sleep, 500
    ; Send keys to navigate to the "Hidden files and folders" options
    Loop % (toggleState ? 8 : 7) {
        Send, {Down}
        Sleep, 1
    }
    ; Toggle the option
    Send, {Space}
    ; Close the Control Panel window
    Send, {Tab 2}{Enter}

    ; Toggle the state for the next time
    toggleState := !toggleState
}


;*   $$$$$$$\                                          $$$$$$$\                      
;*   $$  __$$\                                         $$  __$$\                     
;*   $$ |  $$ | $$$$$$\   $$$$$$\                      $$ |  $$ |$$\   $$\ $$$$$$$\  
;*   $$$$$$$  |$$  __$$\ $$  __$$\       $$$$$$\       $$$$$$$  |$$ |  $$ |$$  __$$\ 
;*   $$  __$$< $$$$$$$$ |$$ /  $$ |      \______|      $$  __$$< $$ |  $$ |$$ |  $$ |
;*   $$ |  $$ |$$   ____|$$ |  $$ |                    $$ |  $$ |$$ |  $$ |$$ |  $$ |
;*   $$ |  $$ |\$$$$$$$\ \$$$$$$$ |                    $$ |  $$ |\$$$$$$  |$$ |  $$ |
;*   \__|  \__| \_______| \____$$ |                    \__|  \__| \______/ \__|  \__|
;*                       $$\   $$ |                                                  
;*                       \$$$$$$  |                                                  
;*                        \______/                                                   

;! 🎯 open Run Path
^!r::
    Run, regedit.exe
    Sleep, 500
    Clipboard := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
return

;*   $$\    $$\  $$$$$$\   $$$$$$\                  $$\           
;*   $$ |   $$ |$$  __$$\ $$  __$$\                 $$ |          
;*   $$ |   $$ |$$ /  \__|$$ /  \__| $$$$$$\   $$$$$$$ | $$$$$$\  
;*   \$$\  $$  |\$$$$$$\  $$ |      $$  __$$\ $$  __$$ |$$  __$$\ 
;*    \$$\$$  /  \____$$\ $$ |      $$ /  $$ |$$ /  $$ |$$$$$$$$ |
;*     \$$$  /  $$\   $$ |$$ |  $$\ $$ |  $$ |$$ |  $$ |$$   ____|
;*      \$  /   \$$$$$$  |\$$$$$$  |\$$$$$$  |\$$$$$$$ |\$$$$$$$\ 
;*       \_/     \______/  \______/  \______/  \_______| \_______|
                                     

;! 🎯 Open-File-Using-Vscode
VScode_OpenWith() {
Clipboard := ""
Send, ^c
ClipWait 1
if ErrorLevel
{
MsgBox, No valid file path found.
return
}
ClipBoardContent := Clipboard
IfInString, ClipBoardContent, \
{
Run, "C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe" "%ClipBoardContent%"
}
else
{
MsgBox, No valid file path found.
}}

;*    $$$$$$\                                      $$$$$$$\            $$\     $$\       
;*   $$  __$$\                                     $$  __$$\           $$ |    $$ |      
;*   $$ /  \__| $$$$$$\   $$$$$$\  $$\   $$\       $$ |  $$ |$$$$$$\ $$$$$$\   $$$$$$$\  
;*   $$ |      $$  __$$\ $$  __$$\ $$ |  $$ |      $$$$$$$  |\____$$\\_$$  _|  $$  __$$\ 
;*   $$ |      $$ /  $$ |$$ /  $$ |$$ |  $$ |      $$  ____/ $$$$$$$ | $$ |    $$ |  $$ |
;*   $$ |  $$\ $$ |  $$ |$$ |  $$ |$$ |  $$ |      $$ |     $$  __$$ | $$ |$$\ $$ |  $$ |
;*   \$$$$$$  |\$$$$$$  |$$$$$$$  |\$$$$$$$ |      $$ |     \$$$$$$$ | \$$$$  |$$ |  $$ |
;*    \______/  \______/ $$  ____/  \____$$ |      \__|      \_______|  \____/ \__|  \__|
;*                       $$ |      $$\   $$ |                                            
;*                       $$ |      \$$$$$$  |                                            
;*                       \__|       \______/                                             

; ;! 🎯 Copy File Path
; ^!m::
; ClipboardBackup := ClipboardAll
; Clipboard := "" 
; Send, ^c 
; ClipWait, 1
; if ErrorLevel
; {
; MsgBox, No valid file path found.
; }
; else
; {
; ClipBoardContent := Clipboard
; StringReplace, ClipBoardContent, ClipBoardContent, `n, `t, All
; Clipboard := ClipboardBackup
; Clipboard := ClipBoardContent
; TrayTip, Copy as Path, Copied "%ClipBoardContent%" to clipboard.
; }
; return

;! 🎯 Copy File Path
CopyPath_File() {
    ClipboardBackup := ClipboardAll
    Clipboard := "" 
    Send, ^c 
    ClipWait, 1
    if ErrorLevel
    {
    MsgBox, No valid file path found.
    }
    else
    {
    ClipBoardContent := Clipboard
    StringReplace, ClipBoardContent, ClipBoardContent, `n, `t, All
    Clipboard := ClipboardBackup
    Clipboard := ClipBoardContent
    TrayTip, Copy as Path, Copied "%ClipBoardContent%" to clipboard.
    }
}


; ;! 🎯 Copy WSL Path
; ^!p::
;     ClipboardBackup := ClipboardAll
;     Clipboard := ""
;     Send, ^c
;     ClipWait, 1
;     if ErrorLevel
;     {
;         MsgBox, No valid file path found.
;     }
;     else
;     {
;         ClipBoardContent := Clipboard
;         ; Replace drive letter and backslashes with WSL path format
;         StringReplace, ClipBoardContent, ClipBoardContent, C:\, C:/, All
;         StringReplace, ClipBoardContent, ClipBoardContent, D:\, D:/, All
;         StringReplace, ClipBoardContent, ClipBoardContent, \, /, All
;         Clipboard := ClipboardBackup
;         Clipboard := ClipBoardContent
;         TrayTip, Copy as WSL Path, Copied "%ClipBoardContent%" to clipboard.
;     }
;     return


;! 🎯 Copy WSL Path
CopyPath_wsl() {
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No valid file path found.
    }
    else
    {
        ClipBoardContent := Clipboard
        ; Replace drive letter and backslashes with WSL path format
        StringReplace, ClipBoardContent, ClipBoardContent, C:\, C:/, All
        StringReplace, ClipBoardContent, ClipBoardContent, D:\, D:/, All
        StringReplace, ClipBoardContent, ClipBoardContent, \, /, All
        Clipboard := ClipboardBackup
        Clipboard := ClipBoardContent
        TrayTip, Copy as WSL Path, Copied "%ClipBoardContent%" to clipboard.
    }
}

; ;! 🎯 Copy Path with '\\' double Backslashes
; ^!o::
;     ClipboardBackup := ClipboardAll
;     Clipboard := ""
;     Send, ^c
;     ClipWait, 1
;     if ErrorLevel
;     {
;         MsgBox, No valid file path found.
;     }
;     else
;     {
;         ClipBoardContent := Clipboard
;         StringReplace, ClipBoardContent, ClipBoardContent, \, \\, All
        
;         Clipboard := ClipboardBackup
;         Clipboard := ClipBoardContent
;         TrayTip, Copy with Doubled Backslashes, Copied "%ClipBoardContent%" to clipboard.
;     }
;     return


CopyPath_DoubleSlash() {
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel {
        MsgBox, No valid file path found.
    } else {
        ClipBoardContent := Clipboard
        StringReplace, ClipBoardContent, ClipBoardContent, \, \\, All
        
        Clipboard := ClipboardBackup
        Clipboard := ClipBoardContent
        TrayTip, Copy with Doubled Backslashes, Copied "%ClipBoardContent%" to clipboard.
    }
}





;;!  $$\   $$\ $$\ $$\ $$\       $$\      $$\ $$\                 $$\
;;!  $$ | $$  |\__|$$ |$$ |      $$ | $\  $$ |\__|                $$ |
;;!  $$ |$$  / $$\ $$ |$$ |      $$ |$$$\ $$ |$$\ $$$$$$$\   $$$$$$$ | $$$$$$\  $$\  $$\  $$\
;;!  $$$$$  /  $$ |$$ |$$ |      $$ $$ $$\$$ |$$ |$$  __$$\ $$  __$$ |$$  __$$\ $$ | $$ | $$ |
;;!  $$  $$<   $$ |$$ |$$ |      $$$$  _$$$$ |$$ |$$ |  $$ |$$ /  $$ |$$ /  $$ |$$ | $$ | $$ |
;;!  $$ |\$$\  $$ |$$ |$$ |      $$$  / \$$$ |$$ |$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ | $$ | $$ |
;;!  $$ | \$$\ $$ |$$ |$$ |      $$  /   \$$ |$$ |$$ |  $$ |\$$$$$$$ |\$$$$$$  |\$$$$$\$$$$  |
;;!  \__|  \__|\__|\__|\__|      \__/     \__|\__|\__|  \__| \_______| \______/  \_____\____/

; #Persistent
; SetTimer, ResetKeyPresses, 500 ; Adjust the timing interval as needed (in milliseconds)
; KeyPressCount := 0
; ~Esc::
;     KeyPressCount++
;     If (KeyPressCount = 1)
;         SetTimer, CheckKeyPresses, -200 ; Set the check timer to fire after 200 milliseconds
; return
; ~q::
;     If (GetKeyState("Esc", "P")) ; Check if Esc is held down
;     {
;         Send, {Alt Down}{F4}{Alt Up} ; Sends Alt+F4 to close the active window
;         KeyPressCount := 0 ; Reset the key press count
;     }
; return
; CheckKeyPresses:
;     SetTimer, CheckKeyPresses, Off
;     KeyPressCount := 0 ; Reset the key press count
; return

; ResetKeyPresses:
;     KeyPressCount := 0 ; Reset the key press count after a certain duration
; return



; #Persistent
; SetTimer, ResetKeyPresses, 500 ; Adjust the timing interval as needed (in milliseconds)
; KeyPressCount := 0
; ~Esc::
;     KeyPressCount++
;     If (KeyPressCount = 1)
;         SetTimer, CheckKeyPresses, -200 ; Set the check timer to fire after 200 milliseconds
; return
; ~q::
;     If (GetKeyState("Esc", "P")) ; Check if Esc is held down
;     {
;         WinGet, ProcessName, ProcessName, A ; Get the process name of the active window
;         Run, %ComSpec% /c taskkill /IM %ProcessName% /F, , Hide ; Kill the process using taskkill
;         KeyPressCount := 0 ; Reset the key press count
;     }
; return
; CheckKeyPresses:
;     SetTimer, CheckKeyPresses, Off
;     KeyPressCount := 0 ; Reset the key press count
; return
; ResetKeyPresses:
;     KeyPressCount := 0 ; Reset the key press count after a certain duration
; return


; Press Esc+Q to kill the foreground application
; ; Define the hotkey combination
; ~Esc & q::KillForeground()
; ; Function to kill the foreground application
; KillForeground() {
;     ; Get the ID of the foreground window
;     WinGet, hWnd, ID, A
;     ; Close the window
;     WinClose, ahk_id %hWnd%
; }


; ~Esc & q::WinClose, % "ahk_id " . WinExist("A")

; Press Esc+Q to kill the foreground application


KillForeground() {
    WinGet, ProcessName, ProcessName, A
    Run, taskkill /f /im %ProcessName%,, Hide
}


;*   $$$$$$$\             $$\                      $$$\           $$$$$$$$\ $$\                         
;*   $$  __$$\            $$ |                    $$ $$\          \__$$  __|\__|                        
;*   $$ |  $$ | $$$$$$\ $$$$$$\    $$$$$$\        \$$$\ |            $$ |   $$\ $$$$$$\$$$$\   $$$$$$\  
;*   $$ |  $$ | \____$$\\_$$  _|  $$  __$$\       $$\$$\$$\          $$ |   $$ |$$  _$$  _$$\ $$  __$$\ 
;*   $$ |  $$ | $$$$$$$ | $$ |    $$$$$$$$ |      $$ \$$ __|         $$ |   $$ |$$ / $$ / $$ |$$$$$$$$ |
;*   $$ |  $$ |$$  __$$ | $$ |$$\ $$   ____|      $$ |\$$\           $$ |   $$ |$$ | $$ | $$ |$$   ____|
;*   $$$$$$$  |\$$$$$$$ | \$$$$  |\$$$$$$$\        $$$$ $$\          $$ |   $$ |$$ | $$ | $$ |\$$$$$$$\ 
;*   \_______/  \_______|  \____/  \_______|       \____\__|         \__|   \__|\__| \__| \__| \_______|

::;now::
FormatTime, CurrentDateTime,, yyyy-MM-dd HH-mm-ss
SendInput %CurrentDateTime%
return

;*   $$$$$$\  $$\                            $$\                           $$\               
;*  $$  __$$\ $$ |                           $$ |                          $$ |              
;*  $$ /  \__|$$$$$$$\   $$$$$$\   $$$$$$\ $$$$$$\    $$$$$$$\ $$\   $$\ $$$$$$\    $$$$$$$\ 
;*  \$$$$$$\  $$  __$$\ $$  __$$\ $$  __$$\\_$$  _|  $$  _____|$$ |  $$ |\_$$  _|  $$  _____|
;*   \____$$\ $$ |  $$ |$$ /  $$ |$$ |  \__| $$ |    $$ /      $$ |  $$ |  $$ |    \$$$$$$\  
;*  $$\   $$ |$$ |  $$ |$$ |  $$ |$$ |       $$ |$$\ $$ |      $$ |  $$ |  $$ |$$\  \____$$\ 
;*  \$$$$$$  |$$ |  $$ |\$$$$$$  |$$ |       \$$$$  |\$$$$$$$\ \$$$$$$  |  \$$$$  |$$$$$$$  |
;*   \______/ \__|  \__| \______/ \__|        \____/  \_______| \______/    \____/ \_______/ 

ChangeMonitorApps() {
; Move all windows from the secondary monitor to the primary monitor
; Use Win+M to trigger the script
#NoEnv
SendMode Input
SetWorkingDir %A_ScriptDir%
; Win + 1 hotkey to toggle window between primary and secondary monitors
{
    ; Get the handle of the active window
    WinGet, hwnd, ID, A
    ; Get the position and size of the active window
    WinGetPos, x, y, w, h, ahk_id %hwnd%
    ; Get the work area of the primary and secondary monitors
    SysGet, MonitorPrimary, MonitorWorkArea, 1
    SysGet, MonitorSecondary, MonitorWorkArea, 2
    ; Check if the window is on the primary monitor
    if (x >= MonitorPrimaryLeft and x < MonitorPrimaryRight and y >= MonitorPrimaryTop and y < MonitorPrimaryBottom)
    {
        ; Calculate the new position to center the window on the secondary monitor
        newX := MonitorSecondaryLeft + ((MonitorSecondaryRight - MonitorSecondaryLeft - w) / 2)
        newY := MonitorSecondaryTop + ((MonitorSecondaryBottom - MonitorSecondaryTop - h) / 2)
    }
    else
    {
        ; Calculate the new position to center the window on the primary monitor
        newX := MonitorPrimaryLeft + ((MonitorPrimaryRight - MonitorPrimaryLeft - w) / 2)
        newY := MonitorPrimaryTop + ((MonitorPrimaryBottom - MonitorPrimaryTop - h) / 2)
    }
    ; Move the window to the calculated position
    WinMove, ahk_id %hwnd%, , newX, newY
}}
