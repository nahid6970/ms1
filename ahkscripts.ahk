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

;! Initialize a variable to keep track of the toggle state
toggleState := 0
^!h::
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
return

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
^!n::
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
}
return

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

;! 🎯 Copy File Path
^!m::
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
return

;! 🎯 Copy WSL Path
^!p::
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
    return

;! 🎯 Copy Path with '\\' double Backslashes
^!o::
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
        StringReplace, ClipBoardContent, ClipBoardContent, \, \\, All
        
        Clipboard := ClipboardBackup
        Clipboard := ClipBoardContent
        TrayTip, Copy with Doubled Backslashes, Copied "%ClipBoardContent%" to clipboard.
    }
    return






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

#Persistent
SetTimer, ResetKeyPresses, 500 ; Adjust the timing interval as needed (in milliseconds)
KeyPressCount := 0
~Esc::
    KeyPressCount++
    If (KeyPressCount = 1)
        SetTimer, CheckKeyPresses, -200 ; Set the check timer to fire after 200 milliseconds
return
~q::
    If (GetKeyState("Esc", "P")) ; Check if Esc is held down
    {
        WinGet, ProcessName, ProcessName, A ; Get the process name of the active window
        Run, %ComSpec% /c taskkill /IM %ProcessName% /F, , Hide ; Kill the process using taskkill
        KeyPressCount := 0 ; Reset the key press count
    }
return
CheckKeyPresses:
    SetTimer, CheckKeyPresses, Off
    KeyPressCount := 0 ; Reset the key press count
return
ResetKeyPresses:
    KeyPressCount := 0 ; Reset the key press count after a certain duration
return



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

;*   $$$$$$\  $$\                            $$\                           $$\               
;*  $$  __$$\ $$ |                           $$ |                          $$ |              
;*  $$ /  \__|$$$$$$$\   $$$$$$\   $$$$$$\ $$$$$$\    $$$$$$$\ $$\   $$\ $$$$$$\    $$$$$$$\ 
;*  \$$$$$$\  $$  __$$\ $$  __$$\ $$  __$$\\_$$  _|  $$  _____|$$ |  $$ |\_$$  _|  $$  _____|
;*   \____$$\ $$ |  $$ |$$ /  $$ |$$ |  \__| $$ |    $$ /      $$ |  $$ |  $$ |    \$$$$$$\  
;*  $$\   $$ |$$ |  $$ |$$ |  $$ |$$ |       $$ |$$\ $$ |      $$ |  $$ |  $$ |$$\  \____$$\ 
;*  \$$$$$$  |$$ |  $$ |\$$$$$$  |$$ |       \$$$$  |\$$$$$$$\ \$$$$$$  |  \$$$$  |$$$$$$$  |
;*   \______/ \__|  \__| \______/ \__|        \____/  \_______| \______/    \____/ \_______/ 
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

!+k::RunWait, taskkill /f /im komorebi.exe
!+v::RunWait, taskkill /f /im VALORANT-Win64-Shipping.exe
!+o::RunWait, taskkill /f /im whkd.exe
!+p::RunWait, taskkill /f /im python.exe
!k::RunWait, komorebic start
!o::RunWait, C:\Users\nahid\scoop\apps\whkd\current\whkd.exe, ,Hide
!g::RunWait, C:\Users\nahid\scoop\apps\glazewm\current\GlazeWM.exe
!r::RunWait, python.exe C:\ms1\running_apps.py, , Hide
!x::RunWait, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs"
!y::RunWait, python.exe C:\ms1\yasb\main.py, , Hide
#t:: WinSet, AlwaysOnTop, Toggle, A
#x:: Run, C:\ms1\mypygui.py , ,Hide
!+g::Run, taskkill /f /im glazewm.exe


Pause::Run, komorebic quick-load-resize
^e::Run, komorebic toggle-float




