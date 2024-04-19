
;!  ███╗   ███╗██╗   ██╗██████╗ ██╗   ██╗ ██████╗ ██╗   ██╗██╗
;!  ████╗ ████║╚██╗ ██╔╝██╔══██╗╚██╗ ██╔╝██╔════╝ ██║   ██║██║
;!  ██╔████╔██║ ╚████╔╝ ██████╔╝ ╚████╔╝ ██║  ███╗██║   ██║██║
;!  ██║╚██╔╝██║  ╚██╔╝  ██╔═══╝   ╚██╔╝  ██║   ██║██║   ██║██║
;!  ██║ ╚═╝ ██║   ██║   ██║        ██║   ╚██████╔╝╚██████╔╝██║
;!  ╚═╝     ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝  ╚═════╝ ╚═╝

; ; ;! alt1 🎯 Launch My PYGui


; ; ;! alt1 🎯 Launch My PYGui
; #x:: 
; IfWinExist, ahk_exe python.exe
; {
; WinActivate
; }
; else
; {
; Run, "C:\ms1\mypygui.py"
; }
; return

; ;!🎯 Launch My PYGui
; Initialize a flag to keep track of whether the script has been launched
; Launched := false

; ; Define a hotkey (Win + X) to launch the script
; #x::
; ; Check if the script has already been launched
; if (!Launched) {
;     ; Check if Python is running
;     IfWinNotExist, ahk_exe python.exe
;     {
;         ; Run the Python script
;         Run, "C:\ms1\mypygui.py"
;         ; Set the flag to indicate that the script has been launched
;         Launched := true
;     }
; }
; return



;!   █████╗ ██╗     ██╗    ██╗ █████╗ ██╗   ██╗███████╗    ████████╗ ██████╗ ██████╗ 
;!  ██╔══██╗██║     ██║    ██║██╔══██╗╚██╗ ██╔╝██╔════╝    ╚══██╔══╝██╔═══██╗██╔══██╗
;!  ███████║██║     ██║ █╗ ██║███████║ ╚████╔╝ ███████╗       ██║   ██║   ██║██████╔╝
;!  ██╔══██║██║     ██║███╗██║██╔══██║  ╚██╔╝  ╚════██║       ██║   ██║   ██║██╔═══╝ 
;!  ██║  ██║███████╗╚███╔███╔╝██║  ██║   ██║   ███████║       ██║   ╚██████╔╝██║     
;!  ╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝       ╚═╝    ╚═════╝ ╚═╝     



;!  ███████╗██╗  ██╗ ██████╗ ██╗    ██╗     ██╗ ██╗  ██╗██╗██████╗ ███████╗
;!  ██╔════╝██║  ██║██╔═══██╗██║    ██║    ██╔╝ ██║  ██║██║██╔══██╗██╔════╝
;!  ███████╗███████║██║   ██║██║ █╗ ██║   ██╔╝  ███████║██║██║  ██║█████╗  
;!  ╚════██║██╔══██║██║   ██║██║███╗██║  ██╔╝   ██╔══██║██║██║  ██║██╔══╝  
;!  ███████║██║  ██║╚██████╔╝╚███╔███╔╝ ██╔╝    ██║  ██║██║██████╔╝███████╗
;!  ╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝  ╚═╝     ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝

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

;!  ██████╗ ███████╗ ██████╗ ███████╗██████╗ ██╗████████╗
;!  ██╔══██╗██╔════╝██╔════╝ ██╔════╝██╔══██╗██║╚══██╔══╝
;!  ██████╔╝█████╗  ██║  ███╗█████╗  ██║  ██║██║   ██║   
;!  ██╔══██╗██╔══╝  ██║   ██║██╔══╝  ██║  ██║██║   ██║   
;!  ██║  ██║███████╗╚██████╔╝███████╗██████╔╝██║   ██║   
;!  ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝   ╚═╝   

;! 🎯 open Run Path
^!r::
    Run, regedit.exe
    Sleep, 500
    Clipboard := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
return

;?  ██╗   ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗     ██████╗ ██████╗ ███████╗███╗   ██╗
;?  ██║   ██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝    ██╔═══██╗██╔══██╗██╔════╝████╗  ██║
;?  ██║   ██║███████╗██║     ██║   ██║██║  ██║█████╗      ██║   ██║██████╔╝█████╗  ██╔██╗ ██║
;?  ╚██╗ ██╔╝╚════██║██║     ██║   ██║██║  ██║██╔══╝      ██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║
;?   ╚████╔╝ ███████║╚██████╗╚██████╔╝██████╔╝███████╗    ╚██████╔╝██║     ███████╗██║ ╚████║
;?    ╚═══╝  ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝     ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝

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

;!   ██████╗ ██████╗ ██████╗ ██╗   ██╗    ██████╗  █████╗ ████████╗██╗  ██╗
;!  ██╔════╝██╔═══██╗██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
;!  ██║     ██║   ██║██████╔╝ ╚████╔╝     ██████╔╝███████║   ██║   ███████║
;!  ██║     ██║   ██║██╔═══╝   ╚██╔╝      ██╔═══╝ ██╔══██║   ██║   ██╔══██║
;!  ╚██████╗╚██████╔╝██║        ██║       ██║     ██║  ██║   ██║   ██║  ██║
;!   ╚═════╝ ╚═════╝ ╚═╝        ╚═╝       ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

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
        StringReplace, ClipBoardContent, ClipBoardContent, C:\, c:/, All
        StringReplace, ClipBoardContent, ClipBoardContent, D:\, d:/, All
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

;!  ██████╗  █████╗ ████████╗███████╗       ██╗       ████████╗██╗███╗   ███╗███████╗
;!  ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝       ██║       ╚══██╔══╝██║████╗ ████║██╔════╝
;!  ██║  ██║███████║   ██║   █████╗      ████████╗       ██║   ██║██╔████╔██║█████╗  
;!  ██║  ██║██╔══██║   ██║   ██╔══╝      ██╔═██╔═╝       ██║   ██║██║╚██╔╝██║██╔══╝  
;!  ██████╔╝██║  ██║   ██║   ███████╗    ██████║         ██║   ██║██║ ╚═╝ ██║███████╗
;!  ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚═════╝         ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝

::;now::
FormatTime, CurrentDateTime,, yyyy-MM-dd HH-mm-ss
SendInput %CurrentDateTime%
return

;!   ██████╗██╗  ██╗ █████╗ ████████╗
;!  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝
;!  ██║     ███████║███████║   ██║   
;!  ██║     ██╔══██║██╔══██║   ██║   
;!  ╚██████╗██║  ██║██║  ██║   ██║   
;!   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   

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
#x:: Run, C:\ms1\mypygui.py
Pause::Run, komorebic quick-load-resize
!+g::Run, taskkill /f /im glazewm.exe

^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

::;;::,=:[]()