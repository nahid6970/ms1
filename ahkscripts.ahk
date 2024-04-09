; shift = +
; alt 	= !
; ctrl 	= ^

; alt + x = launch pwsh
; ctrl + alt + h = show/hide files in explore
; ctrl + alt + m = copy file path
; ctrl + alt + n = open with vscode
; ctrl + alt + p = copy path for linux
; ctrl + alt + x = launch pwsh admin mode
; ctrl + h = launch pygui
; ctrl + shift + r = reload autohotkey script
; win + alt + x = mypwshgui.ps1
; win + t = always on top
; win + v = launch valo.ahk
; win + x = pyscript
; win + z = taskmanager
; CTRL+ALT+R = RegEdit  open Run Path


; ;now = Current date and time
; ;vv1 = u guys r so trash garbage get good..
; ;vv2 = trash garbage stupid noobs..
; ;vv3 = stupid kids get good.





^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R


;!  ███╗   ███╗██╗   ██╗██████╗ ██╗   ██╗ ██████╗ ██╗   ██╗██╗
;!  ████╗ ████║╚██╗ ██╔╝██╔══██╗╚██╗ ██╔╝██╔════╝ ██║   ██║██║
;!  ██╔████╔██║ ╚████╔╝ ██████╔╝ ╚████╔╝ ██║  ███╗██║   ██║██║
;!  ██║╚██╔╝██║  ╚██╔╝  ██╔═══╝   ╚██╔╝  ██║   ██║██║   ██║██║
;!  ██║ ╚═╝ ██║   ██║   ██║        ██║   ╚██████╔╝╚██████╔╝██║
;!  ╚═╝     ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝  ╚═════╝ ╚═╝

; ; ;! alt1 🎯 Launch My PYGui
#x:: 
IfWinExist, ahk_exe python.exe
{
WinActivate
}
else
{
Run, "C:\ms1\mypygui.py"
}
return

; ;!🎯 Launch My PYGui
; ; Initialize a flag to keep track of whether the script has been launched
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

#t::
WinSet, AlwaysOnTop, Toggle, A
return

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
    ; Open Registry Editor
    Run, regedit.exe
    ; Wait for Registry Editor to open (adjust the sleep time as needed)
    Sleep, 500
    ; Copy the registry path to clipboard
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
        StringReplace, ClipBoardContent, ClipBoardContent, C:\, /mnt/c/, All
        StringReplace, ClipBoardContent, ClipBoardContent, D:\, /mnt/d/, All
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
