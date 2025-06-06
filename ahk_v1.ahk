#Requires AutoHotkey v1.0

#Persistent ; Keeps the script running
Menu, Tray, Icon, C:\msBackups\icon\shutdown3.png ; Set the tray icon
Menu, Tray, NoStandard ; Disable default tray menu items (Restore, Pause, etc.)

; Create a tray icon with a right-click menu
Menu, Tray, Add, Reset WorkSpace, Toggle_Reset_Workspace
Menu, Tray, Add, Exit, ExitScript

; Menu, Tray, Default, Exit ; Sets default menu item for left-click on tray icon

; Detect double-click on the tray icon
OnMessage(0x404, "TrayIconClick")
; what happens when double click Detected

TrayIconClick(wParam, lParam) {
    if (lParam = 0x201) { ; Double-click detected
        Run, "C:\Users\nahid\AppData\Local\Programs\Microsoft VS Code\Code.exe" "%A_ScriptFullPath%" ; Open the script in VSCode
    }
}

; Optional: Right-click on tray icon for menu
TrayIconShortcut:
    Return
; Function to exit the script when selected from tray menu
ExitScript:
    ExitApp



#Include, C:\ms1\scripts\Autohtokey\version1\text\Text_Related.ahk
#Include, C:\ms1\scripts\Autohtokey\version1\Windows_Screen_related.ahk
; #Include, C:\ms1\scripts\ahk\shadowFight3.ahk

;;* AHK Related
^+p::Pause    ; Pause script with Ctrl+Alt+P
^+s::Suspend  ; Suspend script with Ctrl+Alt+S
^+r::Reload   ; Reload script with Ctrl+Alt+R

; Display Related
; !Numpad1::Run, pwsh -c "Start-Process "C:\Windows\System32\DisplaySwitch.exe" -ArgumentList "/internal"",,Hide
; !Numpad2::Run, pwsh -c "Start-Process "C:\Windows\System32\DisplaySwitch.exe" -ArgumentList "/external"",,Hide
; !Numpad3::Run, pwsh -c "Start-Process "C:\Windows\System32\DisplaySwitch.exe" -ArgumentList "/extend"",,Hide
RAlt & Numpad1::Run, %ComSpec% /c "C:\msBackups\Display\DisplaySwitch.exe /internal",,Hide
RAlt & Numpad2::Run, %ComSpec% /c "C:\msBackups\Display\DisplaySwitch.exe /external",,Hide
RAlt & Numpad3::Run, %ComSpec% /c "C:\msBackups\Display\DisplaySwitch.exe /extend",,Hide
#2:: Run, cmd /c C:\Users\nahid\OneDrive\backup\usbmmidd_v2\2ndMonitor.bat,,Hide
!c::Center_Focused_Window()
!1::Send_to_2nd_Monitor()
#t:: WinSet, AlwaysOnTop, Toggle, A
^!b::Toggle_Screen_Blackout()
^!d::Toggle_Screen_Dim()()
^!t::Toggle_Reset_Workspace()
^!w::Toggle_Screen_Whiteout()

; gui
!b::Run, %ComSpec% /c "C:\ms1\scripts\ahk\Bio.ahk",,Hide
!u::Run, %ComSpec% /c "C:\ms1\scripts\ahk\Ultimate_Gui.ahk",,Hide


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
LAlt & F::Font_Tools()
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

#IfWinActive ahk_exe dnplayer.exe
!v::Center_Focused_Window_modLDplayer()
#IfWinActive  ; End the condition
; Initialize a variable to keep track of the toggle state
isFirstPosition := true
Center_Focused_Window_modLDplayer() {
    global isFirstPosition  ; Access the toggle variable
    ; Get the handle of the dnplayer.exe window
    WinGet, hwnd, ID, A
    ; Toggle between the two positions
    if (isFirstPosition) {
        ; Set the window to x=1250, y=120
        WinMove, ahk_id %hwnd%, , 159, 49
    } else {
        ; Set the window to x=1150, y=550
        WinMove, ahk_id %hwnd%, , 159, 865
    }
    ; Toggle the position state for the next activation
    isFirstPosition := !isFirstPosition
}

#IfWinActive  ; Remove window-specific condition for general usage
; Define a shortcut to show the position of the foreground window under the mouse
^!v::ShowWindowPositionUnderMouse()
ShowWindowPositionUnderMouse() {
    ; Get the handle of the active (foreground) window
    WinGet, hwnd, ID, A
    ; Get the position of the active window
    WinGetPos, x, y, w, h, ahk_id %hwnd%
    ; Display the starting x and y coordinates as a tooltip under the mouse
    MouseGetPos, mouseX, mouseY  ; Get the current mouse position
    ToolTip, Starting Position: `nX: %x%`nY: %y%, %mouseX%, %mouseY%
    ; Hide the tooltip after 2 seconds
    SetTimer, HideToolTip, -2000
}
HideToolTip:
    ToolTip  ; Clear the tooltip
return



;* ████████╗███████╗██╗  ██╗████████╗    ██████╗ ███████╗██╗      █████╗ ████████╗███████╗██████╗
;* ╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝    ██╔══██╗██╔════╝██║     ██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
;*    ██║   █████╗   ╚███╔╝    ██║       ██████╔╝█████╗  ██║     ███████║   ██║   █████╗  ██║  ██║
;*    ██║   ██╔══╝   ██╔██╗    ██║       ██╔══██╗██╔══╝  ██║     ██╔══██║   ██║   ██╔══╝  ██║  ██║
;*    ██║   ███████╗██╔╝ ██╗   ██║       ██║  ██║███████╗███████╗██║  ██║   ██║   ███████╗██████╔╝
;*    ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═════╝
; !Right::Send, {End}
; !Left::Send, {Home}
; !+Right::Send, +{End}
; !+left::Send, +{home}
; !BackSpace::Send, +{Delete}{Home}

; !+Right::Send, {End}+{home}
; !+left::Send, {home}+{end}

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
        } else if (Ext = "ahk") {
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
