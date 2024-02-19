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


; ;now = Current date and time
; ;vv1 = u guys r so trash garbage get good..
; ;vv2 = trash garbage stupid noobs..
; ;vv3 = stupid kids get good.





^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R


; ;! alt1 🎯 Launch My PYGui
#x:: 
IfWinExist, ahk_exe python.exe
{
WinActivate
}
else
{
Run, "D:\@git\ms1\mypygui.py"
}
return

; ;!alt2 🎯 Launch My PYGui
; #x:: 
; Run, "D:\@git\ms1\mypygui.py"
; return

; ;!alt3 🎯 Launch My PYGui
; #x:: 
; IfWinExist, ahk_exe python.exe
; {
;     ; If Python is running, find its process ID (PID)
;     WinGet, pid, PID, ahk_exe python.exe
;     ; If PID is found, terminate the process
;     if (pid)
;         Process, Close, %pid%
; }
; ; Run My PYGui script
; Run, "D:\@git\ms1\mypygui.py"
; return




; ;!alt1 ; 🎯 Launch My PWSHGui
; #!x:: 
; IfWinExist, ahk_exe python.exe
; {
; WinActivate
; }
; else
; {
; Run, "D:\@git\ms1\scripts\mypwshgui.ps1"
; }
; return

; ; !alt2 🎯 Launch My PWSHGui
; 🎯 Launch My PWSHGui
#!x:: 
IfWinExist, ahk_exe pwsh.exe
{
    ; If pwsh window exists, activate it
    WinActivate
}
else
{
    ; If pwsh window does not exist, run the pwsh script
    Run, pwsh.exe -File "D:\@git\ms1\scripts\mypwshgui.ps1"
}
return





#v:: ; Win + V
Run, D:\@git\ms1\scripts\valorant\valo.ahk
return




; 🎯 Launch TaskManager
#z::
Run, taskmgr
return



; 🎯 Launch Pwsh
!x:: ; alt + x
Run, %comspec% /c cd %USERPROFILE% && pwsh
return

; 🎯 Launch Pwsh in admin mode
^!x::
Run, %comspec% /c cd %USERPROFILE% && start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process pwsh -Verb RunAs"
return


; 🎯 Always on Top
#t::
WinSet, AlwaysOnTop, Toggle, A
return




; 🎯 Show/Hide Hidden Files
^!h::
RegRead, HiddenFiles_Status, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced, Hidden
If (HiddenFiles_Status = 2)
{
RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced, Hidden, 1
SendMessage, 0x111, 4146,,, ahk_class Progman
}
Else
{
RegWrite, REG_DWORD, HKEY_CURRENT_USER, Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced, Hidden, 2
SendMessage, 0x111, 4146,,, ahk_class Progman
}
return



; 🎯 Close All And Reload Main Ahk Script
::cc-close::
Run, "D:\@git\ms1\scripts\ahkcloseopen.py"
return    



; 🎯 Open-File-Using-Vscode
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



; 🎯 Copy File Path
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

; 🎯 Copy WSL Path
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








::;now::
FormatTime, CurrentDateTime,, yyyy-MM-dd HH-mm-ss
SendInput %CurrentDateTime%
return

; Valorant Trash Talk
::;vv1::u guys r so trash garbage get good..
::;vv2::trash garbage stupid noobs..
::;vv3::stupid kids get good.


::a;::ALT
::c;::CTRL
::s;::SHIFT
::ca;::CTRL{+}ALT
::cs;::CTRL{+}SHIFT
::csa;::CTRL{+}SHIFT{+}ALT
::sa;::SHIFT{+}ALT
::ss;::<SPACE>