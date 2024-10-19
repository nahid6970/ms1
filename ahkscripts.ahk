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
^!d::Toggle_Screen_Dim()()
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
    ; Clipboard := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    Clipboard := "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
return
; ::;run::
;     Send, "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
;     ; Clipboard := "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
;     ; Clipboard := "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
; return

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

; ██████╗ ██╗███╗   ███╗      ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗
; ██╔══██╗██║████╗ ████║      ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║
; ██║  ██║██║██╔████╔██║█████╗███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║
; ██║  ██║██║██║╚██╔╝██║╚════╝╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║
; ██████╔╝██║██║ ╚═╝ ██║      ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║
; ╚═════╝ ╚═╝╚═╝     ╚═╝      ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝

; Define a variable to track the state of the screen dimming
dimState := 0
; Define a function to toggle screen dimming
Toggle_Screen_Dim() {
    global dimState  ; Declare the variable as global so it can be accessed inside the function
    if (dimState = 0) {
        ; If the screen is not dimmed, create a semi-transparent black fullscreen window
        dimState := 1
        ; Create the dim window to cover the entire screen
        Gui +LastFound +AlwaysOnTop -Caption +ToolWindow -MinimizeBox -MaximizeBox ; Remove caption, border, and buttons
        Gui, Color, Black
        ; Set the window's transparency (255 is fully opaque, 0 is fully transparent)
        Gui, Add, Text, w%A_ScreenWidth% h%A_ScreenHeight% BackgroundBlack
        WinSet, Transparent, 128 ;! Adjust transparency (0-255)
        Gui, Show, w%A_ScreenWidth% h%A_ScreenHeight% x0 y0 NoActivate
        ; Allow mouse clicks and keyboard input to pass through
        WinSet, ExStyle, +0x20 ; WS_EX_TRANSPARENT
    } else {
        ; If the screen is already dimmed, close the window
        dimState := 0
        Gui, Destroy
    }
}

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
    newY := (ScreenHeight - h) / 4
    ; Move the window to the calculated position
    WinMove, ahk_id %hwnd%, , %newX%, %newY%
}

#IfWinActive ahk_exe dnplayer.exe
!v::Center_Focused_Window_modLDplayer()
#IfWinActive  ; End the condition

Center_Focused_Window_modLDplayer() {
    ; Get the handle of the active (focused) window
    WinGet, hwnd, ID, A
    ; Get the position and size of the active window
    WinGetPos, x, y, w, h, ahk_id %hwnd%
    ; Get the screen width and height
    SysGet, ScreenWidth, 78
    SysGet, ScreenHeight, 79
    ; Calculate new position to center the window (horizontal centering)
    newX := (ScreenWidth - w) / 2
    newY := (ScreenHeight - h +700)
    ; Move the window to the calculated position
    WinMove, ahk_id %hwnd%, , %newX%, %newY%
}


;* ████████╗███████╗██╗  ██╗████████╗    ██████╗ ███████╗██╗      █████╗ ████████╗███████╗██████╗
;* ╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝    ██╔══██╗██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
;*    ██║   █████╗   ╚███╔╝    ██║       ██████╔╝█████╗  ██║     ███████║   ██║   █████╗  ██║  ██║
;*    ██║   ██╔══╝   ██╔██╗    ██║       ██╔══██╗██╔══╝  ██║     ██╔══██║   ██║   ██╔══╝  ██║  ██║
;*    ██║   ███████╗██╔╝ ██╗   ██║       ██║  ██║███████╗███████╗██║  ██║   ██║   ███████╗██████╔╝
;*    ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═════╝
!Right::Send, {End}
!Left::Send, {Home}
!+Right::Send, +{End}
!+left::Send, +{home}
!BackSpace::Send, +{Delete}{Home}

; !+Right::Send, {End}+{home}
; !+left::Send, {home}+{end}


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




;  ██████╗ ████████╗██╗  ██╗███████╗██████╗ ███████╗
; ██╔═══██╗╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔════╝
; ██║   ██║   ██║   ███████║█████╗  ██████╔╝███████╗
; ██║   ██║   ██║   ██╔══██║██╔══╝  ██╔══██╗╚════██║
; ╚██████╔╝   ██║   ██║  ██║███████╗██║  ██║███████║
;  ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
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
#IfWinActive ahk_exe dnplayer.exe
    F13::
        StartTime := A_TickCount  ; Record the current time
        while (A_TickCount - StartTime < 5000)  ; Run for 5000 milliseconds (5 seconds)
        {
            if !WinActive("ahk_exe dnplayer.exe")  ; Ensure dnplayer.exe is active
            {
                break  ; Stop if dnplayer.exe is no longer active
            }
            Send, {l down}  ; Hold down 'd'
            Send, {i down}  ; Hold down 'd'
            Send, {d down}  ; Hold down 'd'
            Send, j         ; Send 'j' multiple times
            Send, j
            Send, {d up}    ; Release 'd'
            Send, {i up}    ; Release 'd'
            Send, {l up}    ; Release 'd'
            Sleep, 100      ; Adjust the delay as needed between iterations
        }
    return

    F12::
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, {l down}
            Sleep, 100
            Send, {l up}
            Sleep, 100
        }
    return

    F11::
        StartTime := A_TickCount
        while (A_TickCount - StartTime < 5000)
        {
            if !WinActive("ahk_exe dnplayer.exe")
            {
                break
            }
            Send, {x down}
            Sleep, 100
            Send, {x up}
            Sleep, 100
        }
    return
#If


;* ███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██████╗ ███████╗██████╗
;* ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝██╔══██╗
;* █████╗   ╚███╔╝ ██████╔╝██║     ██║   ██║██████╔╝█████╗  ██████╔╝
;* ██╔══╝   ██╔██╗ ██╔═══╝ ██║     ██║   ██║██╔══██╗██╔══╝  ██╔══██╗
;* ███████╗██╔╝ ██╗██║     ███████╗╚██████╔╝██║  ██║███████╗██║  ██║
;* ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
#Persistent
SetTitleMatchMode, 2  ; Match windows containing the specified text
DetectHiddenWindows, On
; Hotkey to merge all Explorer windows into one
#e::  ; Ctrl + Shift + M
    ; Array to store all File Explorer window handles and paths
    explorerWindows := []
    ; Find all open File Explorer windows
    WinGet, id, List, ahk_class CabinetWClass
    if (id = 0)
    {
        MsgBox, No File Explorer windows are open.
        return
    }
    ; Loop through all the found windows
    Loop, %id%
    {
        this_id := id%A_Index% ; Get the window ID
        WinActivate, ahk_id %this_id%  ; Activate the window
        ; Send Alt + D to focus on the address bar, then Ctrl + C to copy the path
        Send, !d
        Sleep, 100
        Send, ^c
        ClipWait, 1  ; Wait for the clipboard to contain data
        explorerWindows.Push(Clipboard)  ; Add the path to the array
    }
    ; Activate the first Explorer window and open the remaining ones in new tabs
    WinActivate, ahk_id %id1%
    Sleep, 100
    Loop, % explorerWindows.MaxIndex()
    {
        path := explorerWindows[A_Index]
        if (A_Index = 1)
            continue  ; Skip the first one since it's already in the main window
        Send, ^t  ; Open new tab
        Sleep, 200
        Send, ^l  ; Focus on the address bar
        Sleep, 200
        Send, %path%{Enter}  ; Paste the path and press Enter
        Sleep, 500  ; Wait for the new tab to load
    }
    ; Close all the extra windows
    Loop, %id%
    {
        if (A_Index = 1)
            continue  ; Skip the first window
        this_id := id%A_Index%
        WinClose, ahk_id %this_id%
    }
    return

;* ██████╗ ██╗   ██╗███╗   ██╗    ██╗███╗   ██╗    ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
;* ██╔══██╗██║   ██║████╗  ██║    ██║████╗  ██║    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║
;* ██████╔╝██║   ██║██╔██╗ ██║    ██║██╔██╗ ██║       ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
;* ██╔══██╗██║   ██║██║╚██╗██║    ██║██║╚██╗██║       ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
;* ██║  ██║╚██████╔╝██║ ╚████║    ██║██║ ╚████║       ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
;* ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═╝╚═╝  ╚═══╝       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
; AutoHotkey script to run Python, PowerShell, or batch files with specific commands
; ^!+Enter::
;     ; Save the current clipboard content (the path of the script)
;     ClipSaved := ClipboardAll
;     Clipboard := ""               ; Clear clipboard
;     ; Send Ctrl+C to copy the selected file path
;     Send, ^c
;     ClipWait, 1                   ; Wait until clipboard has content
;     if (Clipboard != "") {
;         ; Get the selected file path from the clipboard
;         FilePath := Clipboard
;         Ext := SubStr(FilePath, InStr(FilePath, ".", 0, 0) + 1)
;         ; Check the extension and prepend the appropriate command
;         if (Ext = "py") {
;             Run, cmd /k python "%FilePath%", , , PID
;         } else if (Ext = "ps1") {
;             Run, cmd /k powershell -ExecutionPolicy Bypass -File "%FilePath%", , , PID
;         } else if (Ext = "bat") {
;             Run, cmd /k "%FilePath%", , , PID
;         } else {
;             MsgBox, Unsupported file type: %Ext%
;         }
;     } else {
;         MsgBox, No file path selected or copied.
;     }
;     ; Restore original clipboard content
;     Clipboard := ClipSaved
;     return

^!+Enter::
    ; Save the current clipboard content (the path of the script)
    ClipSaved := ClipboardAll
    Clipboard := ""               ; Clear clipboard
    ; Get the active window title
    WinGetActiveTitle, ActiveTitle
    ; If the active window is VSCode, simulate the shortcut to copy the file path
    if InStr(ActiveTitle, "Visual Studio Code") {
        ; Simulate VSCode's shortcut to copy the current file path (Shift + Alt + C)
        Send, +!c
        ClipWait, 1               ; Wait until clipboard has content
    } else {
        ; Send Ctrl+C to copy the selected file path in other environments
        Send, ^c
        ClipWait, 1               ; Wait until clipboard has content
    }
    if (Clipboard != "") {
        ; Get the selected file path from the clipboard
        FilePath := Clipboard
        Ext := SubStr(FilePath, InStr(FilePath, ".", 0, 0) + 1)
        ; Check the extension and run the appropriate command
        if (Ext = "py") {
            Run, cmd /k python "%FilePath%", , , PID
        } else if (Ext = "ps1") {
            Run, cmd /k powershell -ExecutionPolicy Bypass -File "%FilePath%", , , PID
        } else if (Ext = "bat") {
            Run, cmd /k "%FilePath%", , , PID
        } else {
            MsgBox, Unsupported file type: %Ext%
        }
    } else {
        MsgBox, No file path selected or copied.
    }
    ; Restore original clipboard content
    Clipboard := ClipSaved
    return


;* ███████╗ ██████╗ ██████╗  ██████╗███████╗    ██████╗ ███████╗██╗     ███████╗████████╗███████╗
;* ██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝    ██╔══██╗██╔════╝██║     ██╔════╝╚══██╔══╝██╔════╝
;* █████╗  ██║   ██║██████╔╝██║     █████╗      ██║  ██║█████╗  ██║     █████╗     ██║   █████╗
;* ██╔══╝  ██║   ██║██╔══██╗██║     ██╔══╝      ██║  ██║██╔══╝  ██║     ██╔══╝     ██║   ██╔══╝
;* ██║     ╚██████╔╝██║  ██║╚██████╗███████╗    ██████╔╝███████╗███████╗███████╗   ██║   ███████╗
;* ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚══════╝    ╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝   ╚══════╝
RAlt & Del::
{
    ; Prompt for the folder path
    InputBox, folderPath, Folder Deletion, Enter the path of the folder to delete:
    if (folderPath = "")
        return  ; Exit if no folder is provided
    ; Check if the folder exists
    if !FileExist(folderPath)
    {
        MsgBox, Folder does not exist!
        return
    }
    ; Path to handle64.exe
    handlePath := "C:\Users\nahid\OneDrive\backup\Handle\handle64.exe"
    ; Run handle64.exe to find the processes using the folder
    RunWait, %handlePath% "%folderPath%" /accepteula > "%A_Temp%\handle_output.txt"
    ; Read the output of handle.exe
    FileRead, handleOutput, %A_Temp%\handle_output.txt
    ; Kill the processes that are using the folder
    Loop, Parse, handleOutput, `n
    {
        if (RegExMatch(A_LoopField, "PID: (\d+)", process))
        {
            ; Extract the process ID
            pid := process1
            ; Kill the process
            RunWait, TaskKill /F /PID %pid%
        }
    }
    ; Attempt to delete the folder after killing processes
    FileRemoveDir, %folderPath%, 1
    if !ErrorLevel
        MsgBox, Folder deleted successfully!
    else
        MsgBox, Failed to delete the folder. It may still be in use by other processes.
    
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

;* ██╗   ██╗██╗  ████████╗██╗███╗   ███╗ █████╗ ████████╗███████╗     ██████╗ ██╗   ██╗██╗
;* ██║   ██║██║  ╚══██╔══╝██║████╗ ████║██╔══██╗╚══██╔══╝██╔════╝    ██╔════╝ ██║   ██║██║
;* ██║   ██║██║     ██║   ██║██╔████╔██║███████║   ██║   █████╗      ██║  ███╗██║   ██║██║
;* ██║   ██║██║     ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██╔══╝      ██║   ██║██║   ██║██║
;* ╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║██║  ██║   ██║   ███████╗    ╚██████╔╝╚██████╔╝██║
;*  ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝     ╚═════╝  ╚═════╝ ╚═╝

#Include C:\ms1\scripts\AHK_BT\V1_4\Class_ImageButton.ahk
!u::
Gui, Margin, 20, 20
; Gui, Font, s11 normal, Segoe UI
Gui,Font,s12 Normal Bold,Jetbrainsmono nfp

Gui, Add, Button, xm ym h30 gmybio, Bio
Gui, Add, Button, x+5 yp h30 gkomorebic_save ,Komorebic Save
Gui, Add, Button, x+5 yp h30 gkomorebic_load ,Komorebic Load

Gui, Add, Button, xm y+5 w250 h30, Komorebic
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_Komorebi, % "Kill"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gStart_Komorebi, % "Start"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)

Gui, Add, Button, xm y+5 w250 h30, Explorer
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gkill_Explorer, % "Kill"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gstart_Explorer, % "Start"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)

Gui, Add, Button, xm y+5 w250 h30, Powershell
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_PWSH, % "PWSH 7"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_Powershell, % "PWSH 1"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)

Gui, Add, Button, xm y+5 w250 h30, Python
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn61 gKill_Python, % "Kill"
IBBtnStyles := [ [0, 0x80F0B9B8, , , 0, , 0x80D43F3A, 2]      ; normal
			   , [0, 0x80E27C79, , , 0, , 0x80D43F3A, 2]      ; hover
			   , [0, 0x80D43F3A, , , 0, , 0x80D43F3A, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x80D43F3A, 2] ]
ImageButton.Create(hBtn61, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gStart_Python_mypygui_showT, % "mypygui-S"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)
Gui, Add, Button, x+5 yp w100 h30 hWndhBtn63 gStart_Python_mypygui_hideT, % "mypygui-H"
IBBtnStyles := [ [0, 0x80C6E6C6, , , 0, , 0x805CB85C, 2]      ; normal
			   , [0, 0x8091CF91, , , 0, , 0x805CB85C, 2]      ; hover
			   , [0, 0x805CB85C, , , 0, , 0x805CB85C, 2]      ; pressed
			   , [0, 0x80F0F0F0, , , 0, , 0x805CB85C, 2] ]
ImageButton.Create(hBtn63, IBBtnStyles*)

Gui, Show,, Image Buttons
return

komorebic_save:
RunWait, komorebic quick-save-resize,,Hide
return
komorebic_load:
RunWait, komorebic quick-load-resize,,Hide
return
Kill_Komorebi:
Run, taskkill /f /im komorebi.exe,,Hide
return
Start_Komorebi:
Run, komorebi.exe,,Hide
return

Kill_Python:
Run, taskkill /f /im python.exe,,Hide
return
Start_Python_mypygui_hideT:
Run, C:\ms1\mypygui.py,,Hide
return
Start_Python_mypygui_showT:
    Run, cmd /k python "C:\ms1\mypygui.py", , UseErrorLevel
    if (ErrorLevel)
    {
        MsgBox, Script failed to execute. Error code: %ErrorLevel%
    }
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

start_Explorer:
Run, pwsh -c explorer.exe,,Hide
return
kill_Explorer:
Run, taskkill /f /im explorer.exe,,Hide
return

; extra unused
start_RunningAppsMonitor:
Run, python.exe C:\ms1\running_apps.py,,Hide
return
start_cmd_asAdmin:
Run, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs",,Hide
return
start_Run:
Run, "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk"
return

;* ██████╗ ██╗ ██████╗      ██████╗ ██╗   ██╗██╗
;* ██╔══██╗██║██╔═══██╗    ██╔════╝ ██║   ██║██║
;* ██████╔╝██║██║   ██║    ██║  ███╗██║   ██║██║
;* ██╔══██╗██║██║   ██║    ██║   ██║██║   ██║██║
;* ██████╔╝██║╚██████╔╝    ╚██████╔╝╚██████╔╝██║
;* ╚═════╝ ╚═╝ ╚═════╝      ╚═════╝  ╚═════╝ ╚═╝

mybio:
Gui, Destroy
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
