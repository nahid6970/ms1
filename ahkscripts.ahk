;;* AHK Related
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

; Display Related
; !Numpad1::Run, pwsh -c "Start-Process "C:\Windows\System32\DisplaySwitch.exe" -ArgumentList "/internal"",,Hide
; !Numpad2::Run, pwsh -c "Start-Process "C:\Windows\System32\DisplaySwitch.exe" -ArgumentList "/external"",,Hide
; !Numpad3::Run, pwsh -c "Start-Process "C:\Windows\System32\DisplaySwitch.exe" -ArgumentList "/extend"",,Hide
!Numpad1::Run, %ComSpec% /c "C:\Users\nahid\OneDrive\backup\DisplaySwitch.exe /internal",,Hide
!Numpad2::Run, %ComSpec% /c "C:\Users\nahid\OneDrive\backup\DisplaySwitch.exe /external",,Hide
!Numpad3::Run, %ComSpec% /c "C:\Users\nahid\OneDrive\backup\DisplaySwitch.exe /extend",,Hide
#2:: Run, cmd /c C:\Users\nahid\OneDrive\backup\usbmmidd_v2\2ndMonitor.bat,,Hide
!c::Center_Focused_Window()
!1::Send_to_2nd_Monitor()
#t:: WinSet, AlwaysOnTop, Toggle, A
^!b::Toggle_Screen_Blackout()
^!t::Toggle_Reset_Workspace()
^!w::Toggle_Screen_Whiteout()

; Kill Commands
; !+v::RunWait, taskkill /f /im VALORANT-Win64-Shipping.exe,,Hide
!+o::RunWait, taskkill /f /im whkd.exe,,Hide
!+p::RunWait, taskkill /f /im python.exe
; !+g::RunWait, taskkill /f /im glazewm.exe,,Hide
!+k::RunWait, taskkill /f /im komorebi.exe,,Hide
!q::KillForeground()
; ~Esc & q::KillForeground()

; Start Apps / Scripts
!e::Run, pwsh -c explorer.exe,,Hide
; !g::RunWait, C:\Users\nahid\scoop\apps\glazewm\current\GlazeWM.exe,,Hide               ;* GlazeWM
; !k::RunWait, komorebic start,,Hide                                                     ;* Komorebi
; !o::RunWait, C:\Users\nahid\scoop\apps\whkd\current\whkd.exe,,Hide                     ;* whkd
!r::RunWait, python.exe C:\ms1\running_apps.py,,Hide                                   ;* running apps
!x::RunWait, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs",,Hide ;* cmd as admin
; !y::RunWait, python.exe C:\ms1\yasb\main.py,,Hide                                      ;* yasb
#r::RunWait, "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk"
#x::RunWait, C:\ms1\mypygui.py ,,Hide                                                  ;* mypygui

; RAlt & L:: Choose_Action() ; Shortcut to open the action chooser
;; Replace & Text Related
LAlt & F::Font_Tools() ; Shortcut to open the action chooser GUI
RAlt & R::Replace_Matching_words_Selection()
RAlt & -::Replace_Dash_W_Space()
RAlt & E:: Convert_Lowercase()
RAlt & L:: Remove_Duplicate_Lines()
RAlt & P:: Remove_All_Punctuation()
RAlt & SPACE::Remove_AllSpace_Selection()
RAlt & U::Convert_Uppercase()

; Komorebic Commands
; !s::RunWait, komorebic toggle-window-container-behaviour,,Hide
; ~Esc & w::RunWait, komorebic toggle-float,,Hide
!w::RunWait, komorebic toggle-float,,Hide
; Pause & S:: RunWait, komorebic quick-save-resize,,Hide
; Pause::RunWait, komorebic quick-load-resize,,Hide


; Others
^!h::ToggleHiddenFiles()
^!m::CopyPath_File()
^!n::VScode_OpenWith()
^!o::CopyPath_DoubleSlash()
^!p::CopyPath_wsl()
^+Esc::Run pwsh -c Taskmgr.exe,,Hide
; ^+m:: Run, "C:\Program Files\Windows Media Player\wmplayer.exe" "D:\song\wwe\ww.mp3",,Return

; F1 for valorant
#IfWinActive ahk_exe VALORANT-Win64-Shipping.exe
    F1::Send, ^+{F1}
#If


;*  ██████╗██╗  ██╗ █████╗ ████████╗
;* ██╔════╝██║  ██║██╔══██╗╚══██╔══╝
;* ██║     ███████║███████║   ██║
;* ██║     ██╔══██║██╔══██║   ██║
;* ╚██████╗██║  ██║██║  ██║   ██║
;*  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝
; command shortcuts info
::;mklink::New-Item -ItemType SymbolicLink -Path FakeFile -Target RealFile -Force

; Personal Info
::;address::Vill:Munshibari, P.O-Radhapur, 9 No Ward, Dist-Lakshmipur Post Code: 3706
::;nahidbd::{U+09A8}{U+09BE}{U+09B9}{U+09BF}{U+09A6} {U+0986}{U+09B9}{U+09AE}{U+09C7}{U+09A6}
::;fatherbd::{U+09A8}{U+09C1}{U+09B0}{U+09C1}{U+09B2} {U+0986}{U+09AE}{U+09BF}{U+09A8}
::;motherbd::{U+09A8}{U+09BE}{U+099C}{U+09AE}{U+09BE} {U+09AC}{U+09C7}{U+0997}{U+09AE}

;* Valorant Trash Talk
::;vv1::u guys r so trash garbage get good..
::;vv2::trash garbage stupid noobs..
::;vv3::stupid kids get good.

;* keyboard mod buttons
::;a::ALT
::;c::CTRL
::;s::SHIFT
::;ca::CTRL{+}ALT
::;cs::CTRL{+}SHIFT
::;csa::CTRL{+}SHIFT{+}ALT
::;sa::SHIFT{+}ALT
::;ss::<SPACE>

::;;::,=:[]()

;;* Font list / need real name adjustment
::;font1::3270 nerd font
::;font2::Agency FB
::;font3::Arial
::;font4::Calibri
::;font5::Candara
::;font6::Cascadia Code PL Nerd Font
::;font7::Comic Sans MS
::;font8::Consolas
::;font9::Courier New
::;font10::DejaVu Sans Mono Nerd Font
::;font11::FiraCode Nerd Font
::;font12::Georgia
::;font13::Georgia
::;font14::Hack Nerd Font
::;font15::Helvetica
::;font16::Inconsolata Nerd Font
::;font17::Jetbrainsmono nfp
::;font18::Lucida Console
::;font19::Meslo Nerd Font
::;font20::Mononoki Nerd Font
::;font21::Palatino Linotype
::;font22::Segoe UI
::;font23::Source Code Pro Nerd Font
::;font24::SpaceMono Nerd Font
::;font25::Tahoma
::;font26::terminess Nerd Font
::;font27::Times New Roman
::;font28::Trebuchet MS
::;font29::Verdana
::;font30::Victoria

;*  ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗     ██████╗  █████╗ ████████╗██╗  ██╗
;*  ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
;*  █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝    ██████╔╝███████║   ██║   ███████║
;*  ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗    ██╔═══╝ ██╔══██║   ██║   ██╔══██║
;*  ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║    ██║     ██║  ██║   ██║   ██║  ██║
;*  ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

::;scoop::C:\Users\nahid\scoop\apps
::;user::C:\Users\nahid
::;appdata::C:\Users\nahid\AppData


;* ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗
;* ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗
;* █████╗  ██║   ██║██║     ██║  ██║█████╗  ██████╔╝
;* ██╔══╝  ██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗
;* ██║     ╚██████╔╝███████╗██████╔╝███████╗██║  ██║
;* ╚═╝      ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝

; ::;scoop::
;     Run, C:\Users\nahid\scoop
;     return
; ::;song::
;     Run, D:\song
;     return
; ::;software::
;     Run, D:\software
;     return
; ::;appdata::
;     Run, C:\Users\nahid\AppData
;     return
; ::;user::
;     Run, C:\Users\nahid
;     return

;* ███████╗██╗  ██╗ ██████╗ ██╗    ██╗        ██╗    ██╗  ██╗██╗██████╗ ███████╗
;* ██╔════╝██║  ██║██╔═══██╗██║    ██║       ██╔╝    ██║  ██║██║██╔══██╗██╔════╝
;* ███████╗███████║██║   ██║██║ █╗ ██║      ██╔╝     ███████║██║██║  ██║█████╗
;* ╚════██║██╔══██║██║   ██║██║███╗██║     ██╔╝      ██╔══██║██║██║  ██║██╔══╝
;* ███████║██║  ██║╚██████╔╝╚███╔███╔╝    ██╔╝       ██║  ██║██║██████╔╝███████╗
;* ╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝     ╚═╝        ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝

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

;;* ██████╗ ███████╗ ██████╗ ██████╗ ██╗   ██╗███╗   ██╗
;;* ██╔══██╗██╔════╝██╔════╝ ██╔══██╗██║   ██║████╗  ██║
;;* ██████╔╝█████╗  ██║  ███╗██████╔╝██║   ██║██╔██╗ ██║
;;* ██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║   ██║██║╚██╗██║
;;* ██║  ██║███████╗╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║
;;* ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

;! 🎯 open Run Path
::;run::
    Run, C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Administrative Tools\Registry Editor.lnk
    Sleep, 500
    Clipboard := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
return

;;* ██╗   ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗
;;* ██║   ██║██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝
;;* ██║   ██║███████╗██║     ██║   ██║██║  ██║█████╗
;;* ╚██╗ ██╔╝╚════██║██║     ██║   ██║██║  ██║██╔══╝
;;*  ╚████╔╝ ███████║╚██████╗╚██████╔╝██████╔╝███████╗
;;*   ╚═══╝  ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝

;! 🎯 Open-File-Using-Vscode
; VScode_OpenWith() {
;     Clipboard := ""
;     Send, ^c
;     ClipWait 1
;     if ErrorLevel
;     {
;     MsgBox, No valid file path found.
;     return
;     }
;     ClipBoardContent := Clipboard
;     IfInString, ClipBoardContent, \
;     {
;     Run, "C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe" "%ClipBoardContent%"
;     }
;     else
;     {
;     MsgBox, No valid file path found.
; }}

VScode_OpenWith() {
    ; Backup current clipboard content
    ClipboardBackup := ClipboardAll
    
    ; Clear clipboard and copy the selected file path
    Clipboard := ""
    Send, ^c
    ClipWait 1
    if ErrorLevel
    {
        MsgBox, No valid file path found.
        ; Restore original clipboard content
        Clipboard := ClipboardBackup
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
    
    ; Restore original clipboard content
    Clipboard := ClipboardBackup
}



;;*  ██████╗ ██████╗ ██████╗ ██╗   ██╗    ██████╗  █████╗ ████████╗██╗  ██╗
;;* ██╔════╝██╔═══██╗██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
;;* ██║     ██║   ██║██████╔╝ ╚████╔╝     ██████╔╝███████║   ██║   ███████║
;;* ██║     ██║   ██║██╔═══╝   ╚██╔╝      ██╔═══╝ ██╔══██║   ██║   ██╔══██║
;;* ╚██████╗╚██████╔╝██║        ██║       ██║     ██║  ██║   ██║   ██║  ██║
;;*  ╚═════╝ ╚═════╝ ╚═╝        ╚═╝       ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝

;* 🎯 Copy File Path
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
    }}

;* 🎯 Copy WSL Path
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
    }}

;* 🎯 Copy Path with '\\' double Backslashes
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
    }}

;;! ██╗  ██╗██╗██╗     ██╗         ███████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗  ██████╗ ██╗   ██╗███╗   ██╗██████╗
;;! ██║ ██╔╝██║██║     ██║         ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝ ██╔══██╗██╔═══██╗██║   ██║████╗  ██║██╔══██╗
;;! █████╔╝ ██║██║     ██║         █████╗  ██║   ██║██████╔╝█████╗  ██║  ███╗██████╔╝██║   ██║██║   ██║██╔██╗ ██║██║  ██║
;;! ██╔═██╗ ██║██║     ██║         ██╔══╝  ██║   ██║██╔══██╗██╔══╝  ██║   ██║██╔══██╗██║   ██║██║   ██║██║╚██╗██║██║  ██║
;;! ██║  ██╗██║███████╗███████╗    ██║     ╚██████╔╝██║  ██║███████╗╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝
;;! ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝

; KillForeground() {
;     WinGet, ProcessName, ProcessName, A
;     Run, taskkill /f /im %ProcessName%,, Hide
; }


; KillForeground() {
;     ; Get the process ID of the foreground window
;     WinGet, ProcessID, PID, A
;     ; Use taskkill command to forcefully terminate the process by ID
;     Run, taskkill /f /pid %ProcessID%,, Hide
; }

KillForeground() {
    ; Get the window handle of the window under the mouse cursor
    MouseGetPos, , , WinID
    
    ; Get the process ID of the window
    WinGet, ProcessID, PID, ahk_id %WinID%
    
    ; Use taskkill command to forcefully terminate the process by ID
    Run, taskkill /f /pid %ProcessID%,, Hide
}


;;* ██████╗  █████╗ ████████╗███████╗       ██╗       ████████╗██╗███╗   ███╗███████╗
;;* ██╔══██╗██╔══██╗╚══██╔══╝██╔════╝       ██║       ╚══██╔══╝██║████╗ ████║██╔════╝
;;* ██║  ██║███████║   ██║   █████╗      ████████╗       ██║   ██║██╔████╔██║█████╗
;;* ██║  ██║██╔══██║   ██║   ██╔══╝      ██╔═██╔═╝       ██║   ██║██║╚██╔╝██║██╔══╝
;;* ██████╔╝██║  ██║   ██║   ███████╗    ██████║         ██║   ██║██║ ╚═╝ ██║███████╗
;;* ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚═════╝         ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝

::;now::
FormatTime, CurrentDateTime,, yyyy-MM-dd HH-mm-ss
SendInput %CurrentDateTime%
return

;;* ██████╗ ███╗   ██╗██████╗     ███╗   ███╗ ██████╗ ███╗   ██╗██╗████████╗ ██████╗ ██████╗
;;* ╚════██╗████╗  ██║██╔══██╗    ████╗ ████║██╔═══██╗████╗  ██║██║╚══██╔══╝██╔═══██╗██╔══██╗
;;*  █████╔╝██╔██╗ ██║██║  ██║    ██╔████╔██║██║   ██║██╔██╗ ██║██║   ██║   ██║   ██║██████╔╝
;;* ██╔═══╝ ██║╚██╗██║██║  ██║    ██║╚██╔╝██║██║   ██║██║╚██╗██║██║   ██║   ██║   ██║██╔══██╗
;;* ███████╗██║ ╚████║██████╔╝    ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║██║   ██║   ╚██████╔╝██║  ██║
;;* ╚══════╝╚═╝  ╚═══╝╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝

; Send_to_2nd_Monitor() {
; ; Move all windows from the secondary monitor to the primary monitor
; ; Use Win+M to trigger the script
; #NoEnv
; SendMode Input
; SetWorkingDir %A_ScriptDir%
; ; Win + 1 hotkey to toggle window between primary and secondary monitors
; {
;     ; Get the handle of the active window
;     WinGet, hwnd, ID, A
;     ; Get the position and size of the active window
;     WinGetPos, x, y, w, h, ahk_id %hwnd%
;     ; Get the work area of the primary and secondary monitors
;     SysGet, MonitorPrimary, MonitorWorkArea, 1
;     SysGet, MonitorSecondary, MonitorWorkArea, 2
;     ; Check if the window is on the primary monitor
;     if (x >= MonitorPrimaryLeft and x < MonitorPrimaryRight and y >= MonitorPrimaryTop and y < MonitorPrimaryBottom)
;     {
;         ; Calculate the new position to center the window on the secondary monitor
;         newX := MonitorSecondaryLeft + ((MonitorSecondaryRight - MonitorSecondaryLeft - w) / 2)
;         newY := MonitorSecondaryTop + ((MonitorSecondaryBottom - MonitorSecondaryTop - h) / 2)
;     }
;     else
;     {
;         ; Calculate the new position to center the window on the primary monitor
;         newX := MonitorPrimaryLeft + ((MonitorPrimaryRight - MonitorPrimaryLeft - w) / 2)
;         newY := MonitorPrimaryTop + ((MonitorPrimaryBottom - MonitorPrimaryTop - h) / 2)
;     }
;     ; Move the window to the calculated position
;     WinMove, ahk_id %hwnd%, , newX, newY
; }}


Send_to_2nd_Monitor() {
    ; Move all windows from the secondary monitor to the primary monitor
    #NoEnv
    SendMode Input
    SetWorkingDir %A_ScriptDir%

    ; Get the handle of the active window
    WinGet, hwnd, ID, A
    
    ; Check if the window title is "LDPlayer"
    WinGetTitle, windowTitle, ahk_id %hwnd%
    if (windowTitle != "LDPlayer") {
        MsgBox, This script only works for the application with the title "LDPlayer".
        return
    }
    
    ; Get the position and size of the active window
    WinGetPos, x, y, w, h, ahk_id %hwnd%
    
    ; Get the work area of the primary and secondary monitors
    SysGet, MonitorPrimary, MonitorWorkArea, 1
    SysGet, MonitorSecondary, MonitorWorkArea, 2
    
    ; Check if the window is on the primary monitor
    if (x >= MonitorPrimaryLeft and x < MonitorPrimaryRight and y >= MonitorPrimaryTop and y < MonitorPrimaryBottom) {
        ; Calculate the new position to center the window on the secondary monitor
        newX := MonitorSecondaryLeft + ((MonitorSecondaryRight - MonitorSecondaryLeft - w) / 2)
        newY := MonitorSecondaryTop + ((MonitorSecondaryBottom - MonitorSecondaryTop - h) / 2)
    } else {
        ; Calculate the new position to center the window on the primary monitor
        newX := MonitorPrimaryLeft + ((MonitorPrimaryRight - MonitorPrimaryLeft - w) / 2)
        newY := MonitorPrimaryTop + ((MonitorPrimaryBottom - MonitorPrimaryTop - h) / 2)
    }
    
    ; Move the window to the calculated position
    WinMove, ahk_id %hwnd%, , newX, newY
}


; ██████╗ ██╗      █████╗  ██████╗██╗  ██╗     ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
; ██╔══██╗██║     ██╔══██╗██╔════╝██║ ██╔╝     ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
; ██████╔╝██║     ███████║██║     █████╔╝█████╗███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
; ██╔══██╗██║     ██╔══██║██║     ██╔═██╗╚════╝╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
; ██████╔╝███████╗██║  ██║╚██████╗██║  ██╗     ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
; ╚═════╝ ╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝     ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝

; Define a variable to track the state of the screen blackout
blackoutState := 0
; Define a function to toggle the screen blackout
Toggle_Screen_Blackout() {
    global blackoutState  ; Declare the variable as global so it can be accessed inside the function
    if (blackoutState = 0) {
        ; If the screen is not blacked out, create a black fullscreen window
        blackoutState := 1
        ; Get the height of the taskbar
        SysGet, taskbarHeight, 4, Shell_TrayWnd
        ; Create the black window to cover the entire screen
        Gui +LastFound +AlwaysOnTop -Caption +ToolWindow ; Remove caption and border
        Gui, Color, Black
        Gui, Show, w%A_ScreenWidth% h%A_ScreenHeight% x0 y0 NoActivate
    } else {
        ; If the screen is already blacked out, close the window
        blackoutState := 0
        Gui, Destroy
    }}


; ██╗    ██╗██╗  ██╗██╗████████╗███████╗    ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
; ██║    ██║██║  ██║██║╚══██╔══╝██╔════╝    ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
; ██║ █╗ ██║███████║██║   ██║   █████╗█████╗███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
; ██║███╗██║██╔══██║██║   ██║   ██╔══╝╚════╝╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
; ╚███╔███╔╝██║  ██║██║   ██║   ███████╗    ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
;  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝

; Define a variable to track the state of the screen Whiteout
whiteoutState := 0
; Define a function to toggle the screen Whiteout
Toggle_Screen_Whiteout() {
    global whiteoutState  ; Declare the variable as global so it can be accessed inside the function
    if (whiteoutState = 0) {
        ; If the screen is not Whiteed out, create a White fullscreen window
        whiteoutState := 1
        ; Get the height of the taskbar
        SysGet, taskbarHeight, 4, Shell_TrayWnd
        ; Create the White window to cover the entire screen
        Gui +LastFound +AlwaysOnTop -Caption +ToolWindow ; Remove caption and border
        
        ; Convert the RGB color #ffffff to BGR format
        color := 0xf6efb0  ; White color in RGB
        Gui, Color, %color%
        
        Gui, Show, w%A_ScreenWidth% h%A_ScreenHeight% x0 y0 NoActivate
    } else {
        ; If the screen is already Whiteed out, close the window
        whiteoutState := 0
        Gui, Destroy
    }
}


; ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗███████╗██████╗  █████╗  ██████╗███████╗    ██████╗ ███████╗███████╗███████╗████████╗
; ██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔════╝██╔════╝██╔════╝╚══██╔══╝
; ██║ █╗ ██║██║   ██║██████╔╝█████╔╝ ███████╗██████╔╝███████║██║     █████╗      ██████╔╝█████╗  ███████╗█████╗     ██║
; ██║███╗██║██║   ██║██╔══██╗██╔═██╗ ╚════██║██╔═══╝ ██╔══██║██║     ██╔══╝      ██╔══██╗██╔══╝  ╚════██║██╔══╝     ██║
; ╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗███████║██║     ██║  ██║╚██████╗███████╗    ██║  ██║███████╗███████║███████╗   ██║
;  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝╚══════╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝   ╚═╝

; Define a variable to track the state of the taskbar
taskbarVisible := 1  ; 1 for visible, 0 for hidden
Toggle_Reset_Workspace() {
    global taskbarVisible
    
    ; Get the handle of the taskbar
    WinGet, taskbarHandle, ID, ahk_class Shell_TrayWnd
    
    if (taskbarVisible) {
        ; Hide the taskbar
        WinSet, ExStyle, +0x80, ahk_id %taskbarHandle%  ; WS_EX_TOOLWINDOW
        WinSet, ExStyle, +0x20, ahk_id %taskbarHandle%  ; WS_EX_TRANSPARENT
        WinSet, Style, -0x800000, ahk_id %taskbarHandle%  ; WS_DISABLED
        taskbarVisible := 0
    } else {
        ; Unhide the taskbar
        WinSet, Style, +0x800000, ahk_id %taskbarHandle%  ; WS_DISABLED
        WinSet, ExStyle, -0x80, ahk_id %taskbarHandle%  ; WS_EX_TOOLWINDOW
        WinSet, ExStyle, -0x20, ahk_id %taskbarHandle%  ; WS_EX_TRANSPARENT
        taskbarVisible := 1
    }
}


;  ██████╗███████╗███╗   ██╗████████╗███████╗██████╗      █████╗ ██████╗ ██████╗
; ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔══██╗
; ██║     █████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝    ███████║██████╔╝██████╔╝
; ██║     ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗    ██╔══██║██╔═══╝ ██╔═══╝
; ╚██████╗███████╗██║ ╚████║   ██║   ███████╗██║  ██║    ██║  ██║██║     ██║
;  ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝     ╚═╝

Center_Focused_Window() {
    ; Get the handle of the active (focused) window
    WinGet, hwnd, ID, A
    
    ; Get the position and size of the active window
    WinGetPos, x, y, w, h, ahk_id %hwnd%
    
    ; Get the screen width and height
    SysGet, ScreenWidth, 78
    SysGet, ScreenHeight, 79
    
    ; Calculate new position to center the window
    newX := (ScreenWidth - w) / 2
    newY := (ScreenHeight - h) / 2
    
    ; Move the window to the calculated position
    WinMove, ahk_id %hwnd%, , %newX%, %newY%
}

;* ████████╗███████╗██╗  ██╗████████╗    ██████╗ ███████╗██╗      █████╗ ████████╗███████╗██████╗
;* ╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝    ██╔══██╗██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
;*    ██║   █████╗   ╚███╔╝    ██║       ██████╔╝█████╗  ██║     ███████║   ██║   █████╗  ██║  ██║
;*    ██║   ██╔══╝   ██╔██╗    ██║       ██╔══██╗██╔══╝  ██║     ██╔══██║   ██║   ██╔══╝  ██║  ██║
;*    ██║   ███████╗██╔╝ ██╗   ██║       ██║  ██║███████╗███████╗██║  ██║   ██║   ███████╗██████╔╝
;*    ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═════╝

Replace_Dash_W_Space() {
    ; Backup the clipboard
    ClipboardBackup := ClipboardAll
    ; Clear the clipboard
    Clipboard := ""
    ; Copy the selected text
    Send, ^c
    ; Wait for the clipboard to contain the copied text
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
    }
    else
    {
        ; Get the clipboard content
        ClipBoardContent := Clipboard
        ; Replace all hyphens with spaces
        StringReplace, ClipBoardContent, ClipBoardContent, -, %A_Space%, All
        ; Restore the clipboard content with the modified text
        Clipboard := ClipBoardContent
        ; Paste the modified text
        Send, ^v
    }
    ; Restore the original clipboard content
    Clipboard := ClipboardBackup
    return
    }

; Remove Spaces from Selection
Remove_AllSpace_Selection(){
;* Backup the clipboard
ClipboardBackup := ClipboardAll
;* Clear the clipboard
Clipboard := ""
;* Copy the selected text
Send, ^c
;* Wait for the clipboard to contain the copied text
ClipWait, 1
if ErrorLevel
{
MsgBox, No text selected or copying failed.
}
else
{
;* Get the clipboard content
ClipBoardContent := Clipboard
;* Replace all spaces with nothing
StringReplace, ClipBoardContent, ClipBoardContent, %A_Space%, , All
;* Restore the clipboard content with the modified text
Clipboard := ClipBoardContent
;* Paste the modified text
Send, ^v
}
;* Restore the original clipboard content
Clipboard := ClipboardBackup
return
}

; Replace Text from Selection
Replace_Matching_words_Selection(){
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ;* Wait for the clipboard to contain the copied text
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
        return
    }
    ;* Get the clipboard content
    ClipBoardContent := Clipboard
    ;* Prompt user for the word to replace
    InputBox, OldWord, Replace Word, Enter the word to replace:
    if (ErrorLevel)
    {
        ;* User canceled the input box
        Clipboard := ClipboardBackup
        return
    }
    ;* Prompt user for the replacement word
    InputBox, NewWord, Replace Word, Enter the new word:
    if (ErrorLevel)
    {
        ;* User canceled the input box
        Clipboard := ClipboardBackup
        return
    }
    ;* Replace all occurrences of the old word with the new word
    StringReplace, ClipBoardContent, ClipBoardContent, %OldWord%, %NewWord%, All
    ;* Restore the clipboard content with the modified text
    Clipboard := ClipBoardContent
    ;* Paste the modified text
    Send, ^v
    ;* Restore the original clipboard content
    Clipboard := ClipboardBackup
    return
}

; Remove All Punctuation
Remove_All_Punctuation(){
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
        return
    }
    ClipBoardContent := Clipboard
    ;* Remove punctuation
    StringReplace, ClipBoardContent, ClipBoardContent, `.,,`, All
    StringReplace, ClipBoardContent, ClipBoardContent, `;,`, All
    StringReplace, ClipBoardContent, ClipBoardContent, `:,`, All
    StringReplace, ClipBoardContent, ClipBoardContent, ``,`, All
    ;* Add more punctuation characters as needed
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}

; Convert to Lowercase
Convert_Lowercase() {
    Gui, Destroy
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel {
        MsgBox, No text selected or copying failed.
        Clipboard := ClipboardBackup
        return
    }
    ClipBoardContent := Clipboard
    ;* Convert to lowercase
    StringLower, ClipBoardContent, ClipBoardContent
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}

; Convert Text to Uppercase
Convert_Uppercase(){
    Gui, Destroy
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel
    {
        MsgBox, No text selected or copying failed.
        return
    }
    ClipBoardContent := Clipboard
    ;* Convert to uppercase
    StringUpper, ClipBoardContent, ClipBoardContent
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
    }

; Remove Duplicate Lines
Remove_Duplicate_Lines() {
    Gui, Destroy
    ClipboardBackup := ClipboardAll
    Clipboard := ""
    Send, ^c
    ClipWait, 1
    if ErrorLevel {
        MsgBox, No text selected or copying failed.
        Clipboard := ClipboardBackup
        return
    }
    ClipBoardContent := Clipboard
    ;* Remove duplicate lines
    Lines := []
    Loop, parse, ClipBoardContent, `n, `r
    {
        if !(Lines[A_LoopField]) {
            Lines[A_LoopField] := True
            Result .= A_LoopField . "`n"
        }
    }
    ClipBoardContent := Result
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}

;?  ██████╗ ██╗   ██╗██╗     ██████╗██╗  ██╗ ██████╗  ██████╗ ███████╗███████╗██████╗
;? ██╔════╝ ██║   ██║██║    ██╔════╝██║  ██║██╔═══██╗██╔═══██╗██╔════╝██╔════╝██╔══██╗
;? ██║  ███╗██║   ██║██║    ██║     ███████║██║   ██║██║   ██║███████╗█████╗  ██████╔╝
;? ██║   ██║██║   ██║██║    ██║     ██╔══██║██║   ██║██║   ██║╚════██║██╔══╝  ██╔══██╗
;? ╚██████╔╝╚██████╔╝██║    ╚██████╗██║  ██║╚██████╔╝╚██████╔╝███████║███████╗██║  ██║
;?  ╚═════╝  ╚═════╝ ╚═╝     ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝

; Shortcut to open the action chooser GUI
; Show the action chooser GUI
Font_Tools() {
    Gui, +AlwaysOnTop ; Ensure the GUI window is always on top
    Gui,Font,s12 Normal Bold,Jetbrainsmono nfp
    Gui, Add, Button, x10 y020 w290 h30 gConvert_Lowercase, Lowercase [Ralt+E]
    Gui, Add, Button, x10 y060 w290 h30 gConvert_Uppercase, UpperCase [Ralt+U]
    Gui, Add, Button, x10 y100 w290 h30 gRemove_Duplicate_Lines, rm Dup Lines [Ralt+L]
    Gui, Add, Button, x10 y140 w290 h50 , Replace Matching Text [RAlt+R]
    Gui, Show, w310 h200, Action Chooser
    return
}
{
Gui, Destroy
return
}



!h:: ; Define the shortcut Ctrl+H
Gui, New, +Resize ; Create a new GUI window with resize capability
Gui, Font, s12 Normal Bold, Jetbrainsmono nfp
Gui, Add, Button, x010 y000 w300 h50 , Font Related`nAlt+F
Gui, Add, Button, x010 y050 w300 h50 , Black Screen`nCtrl+Alt+B
Gui, Add, Button, x010 y100 w300 h50 , White Screen`nCtrl+Alt+W
Gui, Add, Button, x010 y150 w300 h50 , Reset Workspace`nCtrl+Alt+T
Gui, Add, Button, x010 y200 w300 h50 , Always On Top`nWin+T
Gui, Add, Button, x010 y250 w300 h50 , Send to 2nd Monitor`nWin+S
Gui, Add, Button, x010 y300 w300 h50 , Center Focused Apps`nWin+C

Gui, Font, s25, Segoe MDL2 Assets ; Set font size to 24 and use the Segoe MDL2 Assets font
Gui, Add, Text, x310 y000 w300 h80 +Center cBlue, VSCode
Gui, Font, s12 Normal Bold, Jetbrainsmono nfp
Gui, Add, Button, x310 y050 w300 h50 +Center cBlue, Split Right`nCtrl+\
Gui, Add, Button, x310 y100 w300 h50 +Center cBlue gTerminal_Run_File, cp Terminal Run File`nCtrl+Alt+Shift+Enter
Gui, Add, Button, x310 y150 w300 h50 +Center cBlue, Button 8
Gui, Add, Button, x310 y200 w300 h50 +Center cBlue, Button 9
Gui, Add, Button, x310 y250 w300 h50 +Center cBlue, Button 9

Gui, Show, w620 h500, Two Column GUI ; Show the GUI with a width and height
return
GuiClose:
Gui, Hide ; Hide the GUI instead of exiting the script
return

Terminal_Run_File:
    Clipboard := "workbench.action.terminal.runActiveFile"
    MsgBox, Copied `workbench.action.terminal.runActiveFile` to clipboard
return

;! ██╗  ██╗██╗██╗     ██╗         ██████╗ ██╗   ██╗██╗
;! ██║ ██╔╝██║██║     ██║        ██╔════╝ ██║   ██║██║
;! █████╔╝ ██║██║     ██║        ██║  ███╗██║   ██║██║
;! ██╔═██╗ ██║██║     ██║        ██║   ██║██║   ██║██║
;! ██║  ██╗██║███████╗███████╗   ╚██████╔╝╚██████╔╝██║
;! ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝

!k:: ; Define the shortcut Ctrl+H
Gui, New, +Resize ; Create a new GUI window with resize capability
Gui, +AlwaysOnTop
Gui, Font, s25 Normal Bold, Jetbrainsmono nfp
Gui, Add, Text, x10 y000 w300 h80 +Center cRed, Kill
Gui,Font,s12 Normal Bold,Jetbrainsmono nfp
; kill apps
Gui, Add, Button, x10 y050 w300 h50 gKill_Python    ,Python
Gui, Add, Button, x10 y100 w300 h50 gKill_Komorebi  ,Komorebi
Gui, Add, Button, x10 y150 w300 h50 gKill_PWSH      ,PWSH
Gui, Add, Button, x10 y200 w300 h50 gKill_Powershell,Powershell
Gui, Add, Button, x10 y250 w300 h50 gKill_CMD       ,cmd

Gui, Show, w320 h500, Apps (Start/Kill)
return
Gui, Hide
return
; ███████╗████████╗ █████╗ ██████╗ ████████╗     ██████╗ ██╗   ██╗██╗
; ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝    ██╔════╝ ██║   ██║██║
; ███████╗   ██║   ███████║██████╔╝   ██║       ██║  ███╗██║   ██║██║
; ╚════██║   ██║   ██╔══██║██╔══██╗   ██║       ██║   ██║██║   ██║██║
; ███████║   ██║   ██║  ██║██║  ██║   ██║       ╚██████╔╝╚██████╔╝██║
; ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═════╝  ╚═════╝ ╚═╝

!s:: ; Define the shortcut Ctrl+H
Gui, New, +Resize ; Create a new GUI window with resize capability
Gui, +AlwaysOnTop
Gui, Font, s25 Normal Bold, Jetbrainsmono nfp
Gui, Add, Text, x010 y000 w300 h80 +Center cGreen, Start
; start apps
Gui,Font,s12 Normal Bold,Jetbrainsmono nfp
Gui, Add, Button, x010 y050 w300 h50 gstart_Explorer          ,Explorer
Gui, Add, Button, x010 y100 w300 h50 gstart_Komorebic         ,Komorebic
Gui, Add, Button, x010 y150 w300 h50 gstart_RunningAppsMonitor,RunningAppsMonitor
Gui, Add, Button, x010 y200 w300 h50 gstart_cmd_asAdmin       ,cmd [Admin]
Gui, Add, Button, x010 y250 w300 h50 gstart_Run               ,Run
Gui, Add, Button, x010 y300 w300 h50 gstart_mypygui           ,mypygui

Gui, Show, w320 h500, Apps (Start/Kill)
return
Gui, Hide
return

; kill related functions
Kill_Python:
Run, taskkill /f /im python.exe,,Hide
return
Kill_Komorebi:
Run, taskkill /f /im komorebi.exe,,Hide
return
Kill_PWSH:
Run, taskkill /f /im pwsh.exe,,Hide
return
Kill_Powershell:
Run, taskkill /f /im powershell.exe,,Hide
return
Kill_CMD:
Run, taskkill /f /im cmd.exe,,Hide
return

; start related functions
start_Explorer:
Run, pwsh -c explorer.exe,,Hide
return
start_Komorebic:
Run, komorebic start,,Hide
return
start_RunningAppsMonitor:
Run, python.exe C:\ms1\running_apps.py,,Hide
return
start_cmd_asAdmin:
Run, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs",,Hide
return
start_Run:
Run, "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk"
return
start_mypygui:
Run, C:\ms1\mypygui.py ,,Hide 
return

; ██╗  ██╗ ██████╗ ███╗   ███╗ ██████╗ ██████╗ ███████╗██████╗ ██╗
; ██║ ██╔╝██╔═══██╗████╗ ████║██╔═══██╗██╔══██╗██╔════╝██╔══██╗██║
; █████╔╝ ██║   ██║██╔████╔██║██║   ██║██████╔╝█████╗  ██████╔╝██║
; ██╔═██╗ ██║   ██║██║╚██╔╝██║██║   ██║██╔══██╗██╔══╝  ██╔══██╗██║
; ██║  ██╗╚██████╔╝██║ ╚═╝ ██║╚██████╔╝██║  ██║███████╗██████╔╝██║
; ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝
Pause::
Gui, New, +Resize
Gui, +AlwaysOnTop
Gui, Font, s25 Normal Bold, Jetbrainsmono nfp
Gui, Add, Text, x010 y000 w300 h80 +Center cGreen, Komorebi
; start apps
Gui,Font,s12 Normal Bold,Jetbrainsmono nfp
Gui, Add, Button, x010 y050 w300 h50 gkomorebic_save ,Komorebic Save
Gui, Add, Button, x010 y100 w300 h50 gkomorebic_load ,Komorebic Load

Gui, Show, w320 h200, Komorebi
return
Gui, Hide
return

komorebic_save:
RunWait, komorebic quick-save-resize,,Hide
return
komorebic_load:
RunWait, komorebic quick-load-resize,,Hide
return



; ██████╗ ██╗ ██████╗      ██████╗ ██╗   ██╗██╗
; ██╔══██╗██║██╔═══██╗    ██╔════╝ ██║   ██║██║
; ██████╔╝██║██║   ██║    ██║  ███╗██║   ██║██║
; ██╔══██╗██║██║   ██║    ██║   ██║██║   ██║██║
; ██████╔╝██║╚██████╔╝    ╚██████╔╝╚██████╔╝██║
; ╚═════╝ ╚═╝ ╚═════╝      ╚═════╝  ╚═════╝ ╚═╝

!b::
Gui, New, +Resize
Gui, +AlwaysOnTop

Gui,Font,s12 Normal Bold,Jetbrainsmono nfp

Gui,Add,Button,x000 y000 w200 h50               ,Nahid Ahmed
Gui,Add,Button,x200 y000 w100 h50 gname_en_nahid,[EN]
Gui,Add,Button,x300 y000 w100 h50 gname_bd_nahid,[BD]

Gui,Add,Button,x000 y050 w200 h50               ,Father
Gui,Add,Button,x200 y050 w100 h50 gname_en_father,[EN]
Gui,Add,Button,x300 y050 w100 h50 gname_bd_father,[BD]

Gui,Add,Button,x000 y100 w200 h50               ,Mother
Gui,Add,Button,x200 y100 w100 h50 gname_en_mother,[EN]
Gui,Add,Button,x300 y100 w100 h50 gname_bd_mother,[BD]

Gui,Add,Button,x000 y150 w400 h50 gPermanentAddress,Vill:Munshibari, P.O-Radhapur, 9 No Ward, Dist-Lakshmipur Post Code: 3706

Gui, Show, w400 h500, BIO
return
Gui, Hide
return

name_bd_nahid:
    Gui, Destroy
    Send, {U+09A8}{U+09BE}{U+09B9}{U+09BF}{U+09A6} {U+0986}{U+09B9}{U+09AE}{U+09C7}{U+09A6}
return
name_en_nahid:
    Gui, Destroy
    Send, Nahid Ahmed
return
name_bd_father:
    Gui, Destroy
    Send, {U+09A8}{U+09C1}{U+09B0}{U+09C1}{U+09B2} {U+0986}{U+09AE}{U+09BF}{U+09A8}
return
name_en_father:
    Gui, Destroy
    Send, Nurul Amin
return
name_bd_mother:
    Gui, Destroy
    Send, {U+09A8}{U+09BE}{U+099C}{U+09AE}{U+09BE} {U+09AC}{U+09C7}{U+0997}{U+09AE}
return
name_en_mother:
    Gui, Destroy
    Send, Nazma Begum
return
PermanentAddress:
    Gui, Destroy
    Send, Vill:Munshibari, P.O-Radhapur, 9 No Ward, Dist-Lakshmipur Post Code: 3706
return


; !h:: ; Define the shortcut Ctrl+H
; Gui, New, +Resize ; Create a new GUI window with resize capability

; ; Use Font command to set a specific font size and style for all text controls
; Gui, Font, s10 Bold, Jetbrainsmono nfp ; Set font size to 12, make it bold, and use Arial

; ; Add text controls to the GUI
; Gui, Add, Text, x10 y10 w120 h40 +Center, Button
; Gui, Add, Text, x10 y60 w120 h40 +Center, Button
; Gui, Add, Text, x10 y110 w120 h40 +Center, Button
; Gui, Add, Text, x10 y160 w120 h40 +Center, Button
; Gui, Add, Text, x10 y210 w120 h40 +Center, Button

; Gui, Add, Text, x150 y10 w120 h40 +Center, Button
; Gui, Add, Text, x150 y60 w120 h40 +Center, Button
; Gui, Add, Text, x150 y110 w120 h40 +Center, Button
; Gui, Add, Text, x150 y160 w120 h40 +Center, Button

; Gui, Show, w300 h300, Two Column GUI ; Show the GUI with a width and height
; return

; GuiClose:
; Gui, Hide ; Hide the GUI instead of exiting the script
; return




; !h:: ; Define the shortcut Ctrl+H
; Gui, New, +Resize ; Create a new GUI window with resize capability

; ; First column
; Gui, Font, s12 Bold, Jetbrainsmono nfp
; Gui, Add, Text, x10 y10 w300 h40 +Center,  ShowActionChooser`nALT+F
; Gui, Add, Text, x10 y60 w300 h40 +Center, Button 2
; Gui, Add, Text, x10 y110 w300 h40 +Center, Button 3
; Gui, Add, Text, x10 y160 w300 h40 +Center, Button 4
; Gui, Add, Text, x10 y210 w300 h40 +Center, Button 5

; ; Second column
; Gui, Font, s12 Italic, Times New Roman
; Gui, Add, Text, x310 y10 w300 h40 +Center, Button A
; Gui, Add, Text, x310 y60 w300 h40 +Center, Button B
; Gui, Add, Text, x310 y110 w300 h40 +Center, Button C
; Gui, Add, Text, x310 y160 w300 h40 +Center, Button D

; Gui, Show, w600 h300, Two Column GUI ; Show the GUI with a width and height
; return

; GuiClose:
; Gui, Hide ; Hide the GUI instead of exiting the script
; return


#=:: ; [Win]+[=]
    WinGet, window, ID, A
    InputBox, width, Resize, Width:, , 140, 130
    InputBox, height, Resize, Height:, , 140, 130
    WinMove, ahk_id %window%, , , , width, height
    return







;  ██████╗██╗  ██╗ ██████╗ ██████╗ ██████╗
; ██╔════╝██║  ██║██╔═══██╗██╔══██╗██╔══██╗
; ██║     ███████║██║   ██║██████╔╝██║  ██║
; ██║     ██╔══██║██║   ██║██╔══██╗██║  ██║
; ╚██████╗██║  ██║╚██████╔╝██║  ██║██████╔╝
;  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝

; ChordSequence := ""
; TimerActive := False

; ; First keypress in the chord sequence
; ^f::  ; Ctrl + F
;     ChordSequence := "Ctrl+F"
;     TimerActive := True
;     SetTimer, CheckChordTimeout, -500  ; Timer to reset the chord sequence if not completed in 500ms
;     return

; ; Second keypress in the chord sequence for Explorer
; ^e::  ; Ctrl + E
;     if (ChordSequence = "Ctrl+F" && GetKeyState("Ctrl", "P")) {
;         ChordSequence := ""  ; Clear the sequence after successful match
;         TimerActive := False
;         ; Launch Windows Explorer
;         Run, explorer.exe
;     }
;     return

; ; Second keypress in the chord sequence for Terminal
; ^d::  ; Ctrl + D
;     if (ChordSequence = "Ctrl+F" && GetKeyState("Ctrl", "P")) {
;         ChordSequence := ""  ; Clear the sequence after successful match
;         TimerActive := False
;         ; Launch Windows Terminal
;         Run, wt.exe  ; Adjust path if needed
;     }
;     return

; ; Regular Ctrl + D functionality
; ^d up::  ; Ctrl + D released
;     if !(ChordSequence = "Ctrl+F") {
;         ; Perform normal Ctrl + D action here
;         Send, ^d
;     }
;     return

; ; Regular Ctrl + E functionality
; ^e up::  ; Ctrl + E released
;     if !(ChordSequence = "Ctrl+F") {
;         ; Perform normal Ctrl + E action here
;         Send, ^e
;     }
;     return

; ; Timer expirfation handler for timeout
; CheckChordTimeout:
;     if (ChordSequence = "Ctrl+F" && TimerActive) {
;         ; Send Ctrl+F if Ctrl+E or Ctrl+D is not pressed within 500ms
;         Send, ^f
;     }
;     ChordSequence := ""  ; Reset the sequence after handling timeout
;     TimerActive := False
;     return

; ; Ensure Ctrl is released if script is terminated or reset
; ^Esc::  ; Ctrl + Esc to exit the script
;     ExitApp


; Define the hotstring ;killfav
::;killme::
{
    ; Kill python.exe
    Run, taskkill /F /IM python.exe, , Hide
    ; Kill ldplayer.exe
    Run, taskkill /F /IM dnplayer.exe, , Hide
    ; Close all Chrome tabs (kills chrome.exe process)
    Run, taskkill /F /IM chrome.exe, , Hide
    ; Return to stop execution
    return
}


^!a:: ; Ctrl + Alt + A
{
    ; Get the window under the mouse
    MouseGetPos, , , winID
    
    ; Get the process path
    WinGet, processPath, ProcessPath, ahk_id %winID%
    
    ; Run the process as administrator
    if (processPath != "")
    {
        Run, %processPath%,, RunAs
    }
    else
    {
        MsgBox, Unable to retrieve the process path.
    }
}
return



;*  ███████╗███████╗██████╗
;*  ██╔════╝██╔════╝╚════██╗
;*  ███████╗█████╗   █████╔╝
;*  ╚════██║██╔══╝   ╚═══██╗
;*  ███████║██║     ██████╔╝
;*  ╚══════╝╚═╝     ╚═════╝
; Light-Attack1
; #IfWinActive ahk_exe dnplayer.exe
;     F13::
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x up}
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Sleep, 100
;         ; Send, {x up}
;     return
; #If



; ;! continue untile f14 pressed
; #IfWinActive ahk_exe dnplayer.exe
;     F13::
;         Toggle := !Toggle  ; Toggle the loop on/off
;         while (Toggle)  ; Loop while Toggle is true
;         {
;             Send, {d down}
;             Send, j
;             Send, j
;             Send, {d up}
;             Sleep, 100  ; Adjust the delay as needed
;             if (!Toggle)  ; Break the loop if Toggle is turned off
;                 break
;         }
;     return

;     F14::
;         Toggle := false  ; Stop the loop when F14 is pressed
;     return
; #If



;; only send the shortcut to dnplayer
#IfWinActive ahk_exe dnplayer.exe
    F13::
        StartTime := A_TickCount  ; Record the current time
        while (A_TickCount - StartTime < 3000)  ; Run for 3000 milliseconds (3 seconds)
        {
            Send, {l down}
            Send, {x down}
            Send, {d down}
            Send, j
            Send, j
            Send, {d up}
            Send, {x up}
            Send, {l up}
            Sleep, 100  ; Adjust the delay as needed between iterations
        }
    return
#If




; PSS
; #IfWinActive ahk_exe dnplayer.exe
;     F13::
;         Send, {x down}
;         Send, {l down}
;         Send, {i down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Send, {i up}
;         Send, {l up}
;         Send, {x up}
;     return
; #If

; #IfWinActive ahk_exe dnplayer.exe
;     F13::
;         Send, {i down}
;         Send, {d down}
;         Send, j
;         Send, j
;         Send, {d up}
;         Send, {i up}
;     return
; #If