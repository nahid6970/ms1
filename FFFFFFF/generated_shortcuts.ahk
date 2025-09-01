#Requires AutoHotkey v2.0
#SingleInstance
Persistent

;! === SCRIPT SHORTCUTS ===
;! Open Terminal Admin
;! Opens PowerShell as administrator
!x::RunWait("pwsh -Command `"cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs`"", , "Hide")

;! Run Python Script
;! Opens run.py in the ms1 directory
!Space::Run("C:\Users\nahid\ms\ms1\run.py", , "Show")

;! Monitor Internal
;! Switch to internal monitor only
RAlt & Numpad1::Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")

;! Monitor External
;! Switch to external monitor only
RAlt & Numpad2::Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")

;! Monitor Extend
;! Extend display to both monitors
RAlt & Numpad3::Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")

;! Bio GUI
;! Opens Bio.ahk GUI
!b::Run("C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\gui\Bio.ahk", "", "Hide")

;! Ultimate GUI
;! Opens Ultimate_Gui.py
!u::Run("C:\Users\nahid\ms\ms1\Ultimate_Gui.py", "", "Hide")

;! Always On Top Toggle
;! Toggles always on top for active window
#t:: {
    Always_on_Top()
    Always_on_Top(){
        static alwaysOnTop := false
        if (alwaysOnTop) {
            WinSetAlwaysOnTop(false, "A")
        } else {
            WinSetAlwaysOnTop(true, "A")
        }
        alwaysOnTop := !alwaysOnTop
    }
}

;! Kill Foreground Process
;! Forcefully kills the process under mouse cursor
!q:: {
    KillForeground()
    KillForeground() {
        MouseGetPos(, , &WinID)
        ProcessID := WinGetPID("ahk_id " WinID)
        Run("taskkill /f /pid " ProcessID, , "Hide")
    }
}

;! Copy Path
^!m:: {
    CopyPath_File()
    CopyPath_File() {
        ClipboardBackup := ClipboardAll()
        A_Clipboard := "" 
        Send("^c")
        Errorlevel := !ClipWait(1)
        if ErrorLevel
        {
        MsgBox("No valid file path found.")
        }
        else
        {
        ClipBoardContent := A_Clipboard
        ; V1toV2: StrReplace() is not case sensitive
        ; check for StringCaseSense in v1 source script
        ; and change the CaseSense param in StrReplace() if necessary
        ClipBoardContent := StrReplace(ClipBoardContent, "`n", "`t")
        A_Clipboard := ClipboardBackup
        A_Clipboard := ClipBoardContent
        TrayTip("Copy as Path", "Copied `"" ClipBoardContent "`" to clipboard.")
        }}
}

;! === TEXT SHORTCUTS ===
;! AutoHotkey Version 1
;! Inserts AHK v1 header requirement
::;v1::#Requires AutoHotkey v1.0

;! AutoHotkey Version 2
;! Inserts AHK v2 header requirement
::;v2::#Requires AutoHotkey v2.0

;! Registry Run Path
;! Windows startup registry path run
::;run::HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run

;! PowerShell Symlink
;! PowerShell command to create symbolic link
::;mklink::New-Item -ItemType SymbolicLink -Path "Fake" -Target "Original" -Force

;! Arrow Symbol
;! Right-pointing arrow symbol
::;--::➔

;! Writers list of writings
::;list::x
(

কাব্যগ্রন্থ/গদ্যকাব্য:
কবিতা:
উপন্যাস:
নাটক:
সনেট:
ছোটগল্প/গল্প:
গদ্যগ্রন্থ-প্রবন্ধ:
অনুবাদ গ্রন্থ:
বই:
অন্যান্য:
পংক্তি এবং উদ্ধৃতি:
)
