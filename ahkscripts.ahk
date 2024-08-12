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
^!t::Toggle_Reset_Workspace()
^!b::Toggle_Screen_Blackout()
^!w::Toggle_Screen_Whiteout()
!1::Change_Monitor_Apps()
!2::Center_Focused_Window()
#t:: WinSet, AlwaysOnTop, Toggle, A

; Kill Commands
!+v::RunWait, taskkill /f /im VALORANT-Win64-Shipping.exe,,Hide
!+o::RunWait, taskkill /f /im whkd.exe,,Hide
!+p::RunWait, taskkill /f /im python.exe
!+g::RunWait, taskkill /f /im glazewm.exe,,Hide
!+k::RunWait, taskkill /f /im komorebi.exe,,Hide
!q::KillForeground()
; ~Esc & q::KillForeground()

; Start Apps / Scripts
!e::Run pwsh -c explorer.exe,,Hide
!g::RunWait, C:\Users\nahid\scoop\apps\glazewm\current\GlazeWM.exe,,Hide               ;* GlazeWM
!k::RunWait, komorebic start,,Hide                                                     ;* Komorebi
!o::RunWait, C:\Users\nahid\scoop\apps\whkd\current\whkd.exe,,Hide                     ;* whkd
!r::RunWait, python.exe C:\ms1\running_apps.py,,Hide                                   ;* running apps
!x::RunWait, pwsh -Command "cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs",,Hide ;* cmd as admin
!y::RunWait, python.exe C:\ms1\yasb\main.py,,Hide                                      ;* yasb
#r::RunWait, "C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\System Tools\Run.lnk"
#x::RunWait, C:\ms1\mypygui.py ,,Hide                                                  ;* mypygui

; Replace & Text Related
^+,:: Remove_All_Punctuation()
^+;::ReplaceDashWSpace()
^+'::Remove_AllSpace_Selection()
^+d:: Remove_Duplicate_Lines()
^+l:: Convert_Lowercase()
^+u::Convert_Uppercase()
^+y::Replace_Matching_words_Selection()

; Komorebic Commands
!s::RunWait, komorebic toggle-window-container-behaviour,,Hide
; ~Esc & w::RunWait, komorebic toggle-float,,Hide
!w::RunWait, komorebic toggle-float,,Hide
Pause::RunWait, komorebic quick-load-resize,,Hide
^l:: RunWait, komorebic quick-save-resize,,return

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
^!r::
    Run, regedit.exe
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

Change_Monitor_Apps() {
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


; ; Define a function to run the appropriate command based on the active window
; RunCommandBasedOnActiveWindow() {
;     ; Get the name of the active window
;     WinGetTitle, activeWindowTitle, A

;     ; Check if the active window is Visual Studio Code
;     if (InStr(activeWindowTitle, "Visual Studio Code")) {
;         Run, cmd /c "rclone config"
;     }
;     ; Check if the active window is Google Chrome
;     else if (InStr(activeWindowTitle, "Google Chrome")) {
;         Run, cmd /c "fzf"
;     }
; }
; ; Define a hotkey (Alt + 5) to trigger the function
; !5::RunCommandBasedOnActiveWindow()


; ; Define hotkey F1 to send Ctrl+Alt+F1 when Valorant is active
; #IfWinActive ahk_class UnrealWindow ahk_exe VALORANT-Win64-Shipping.exe
;     F1::Send, ^!{F1}
; #IfWinActive

; ; Define F1 to send F1 normally
; F1::Send, {F1}



; ; Define a function to check the foreground application and send the appropriate keys
; CheckForegroundAndSendKeys() {
;     ; Get the name of the active window
;     WinGetTitle, activeWindowTitle, A

;     ; Check if the active window is Valorant
;     if (InStr(activeWindowTitle, "VALORANT")) {
;         ; Send Ctrl + Alt + F1
;         Send, ^!{F1}
;     } else {
;         ; Send F1 normally
;         Send, {F1}
;     }
; }
; ; Define a hotkey (F1) to trigger the function
; F1::CheckForegroundAndSendKeys()



; ; Define hotkey F2 to run 'dir' command when Chrome is active
; #IfWinActive ahk_exe chrome.exe
;     F2::Run, cmd /c rclone ncdu d:
; #If

; ; Define hotkey F2 to run 'rclone config' when VSCode is active
; #IfWinActive ahk_exe Code.exe
;     F2::Run, cmd /c rclone config
; #If



; ; Define hotkey F1 to send Ctrl+Alt+F1 when Valorant is active
; #If (WinActive("ahk_class UnrealWindow ahk_exe VALORANT-Win64-Shipping.exe") && GetKeyState("F1", "P"))
;     F1::Send, ^!{F1}
; #If
; ; Define a hotkey (F1) to send F1 normally for all other applications
; #If !WinActive("ahk_class UnrealWindow ahk_exe VALORANT-Win64-Shipping.exe")
;     F1::Send, {F1}
; #If




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


ReplaceDashWSpace() {
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


Remove_AllSpace_Selection(){
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
; Replace all spaces with nothing
StringReplace, ClipBoardContent, ClipBoardContent, %A_Space%, , All
; Restore the clipboard content with the modified text
Clipboard := ClipBoardContent
; Paste the modified text
Send, ^v
}
; Restore the original clipboard content
Clipboard := ClipboardBackup
return
}



Replace_Matching_words_Selection(){
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
        return
    }
    ; Get the clipboard content
    ClipBoardContent := Clipboard
    ; Prompt user for the word to replace
    InputBox, OldWord, Replace Word, Enter the word to replace:
    if (ErrorLevel)
    {
        ; User canceled the input box
        Clipboard := ClipboardBackup
        return
    }
    ; Prompt user for the replacement word
    InputBox, NewWord, Replace Word, Enter the new word:
    if (ErrorLevel)
    {
        ; User canceled the input box
        Clipboard := ClipboardBackup
        return
    }
    ; Replace all occurrences of the old word with the new word
    StringReplace, ClipBoardContent, ClipBoardContent, %OldWord%, %NewWord%, All
    ; Restore the clipboard content with the modified text
    Clipboard := ClipBoardContent
    ; Paste the modified text
    Send, ^v
    ; Restore the original clipboard content
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

; Convert to Uppercase
Convert_Uppercase(){
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
    ; Convert to uppercase
    StringUpper, ClipBoardContent, ClipBoardContent
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
    }


; Convert to Lowercase
Convert_Lowercase(){
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
    ;* Convert to lowercase
    StringLower, ClipBoardContent, ClipBoardContent
    Clipboard := ClipBoardContent
    Send, ^v
    Clipboard := ClipboardBackup
    return
}


;; Trim Leading and Trailing Spaces
; ^+t:: ; Ctrl + Shift + T
;     ClipboardBackup := ClipboardAll
;     Clipboard := ""
;     Send, ^c
;     ClipWait, 1
;     if ErrorLevel
;     {
;         MsgBox, No text selected or copying failed.
;         return
;     }
;     ClipBoardContent := Clipboard
;     ; Trim leading and trailing spaces
;     StringTrimLeft, ClipBoardContent, ClipBoardContent, InStr(ClipBoardContent, A_Space)
;     StringTrimRight, ClipBoardContent, ClipBoardContent, InStr(ClipBoardContent, A_Space)
;     Clipboard := ClipBoardContent
;     Send, ^v
;     Clipboard := ClipboardBackup
;     return


; Remove Duplicate Lines
Remove_Duplicate_Lines(){
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
    ;* Remove duplicate lines
    Lines := []
    Loop, parse, ClipBoardContent, `n, `r
    {
        if !(Lines[A_LoopField])
        {
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


; ; Replace Multiple Spaces with Single Space
; ^+m:: ; Ctrl + Shift + M
;     ClipboardBackup := ClipboardAll
;     Clipboard := ""
;     Send, ^c
;     ClipWait, 1
;     if ErrorLevel
;     {
;         MsgBox, No text selected or copying failed.             
;         return
;     }
;     ClipBoardContent := Clipboard
;     ; Replace multiple spaces with a single space
;     StringReplace, ClipBoardContent, ClipBoardContent, %A_Space% %A_Space%, %A_Space%, All
;     Clipboard := ClipBoardContent
;     Send, ^v
;     Clipboard := ClipboardBackup
;     return
