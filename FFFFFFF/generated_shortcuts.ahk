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

;! Kill (dnplayer/python/) + Change Display
^!+r:: {
    {
        ; Kill dnplayer.exe
        Run("taskkill /F /IM dnplayer.exe",,"Hide")
        ; Kill python.exe
        Run("taskkill /F /IM python.exe",,"Hide")
        ; Run the command
        Run("C:\Users\nahid\ms\msBackups\Display\DisplaySwitch.exe /internal",,"Hide")
    }
}

;! mypygui
#x::Run("C:\Users\nahid\ms\ms1\mypygui.py", , "Hide")

;! Startup Setup
#s::Run("C:\Users\nahid\ms\ms1\scripts\flask\4999_startup\startup.py", , "Hide")

;! CrossHair
^+m::Run("C:\Users\nahid\ms\ms1\scripts\xy\XY_CroosHair.py", , "Hide")

;! Explorer Restart
LAlt & e::Run('pwsh -c explorer.exe', , 'Hide')

;! Replace Space with _
RAlt & Space:: {
    replacewith_()
    replacewith_()
    {
        ; Backup the clipboard
        ClipboardBackup := ClipboardAll()
        ; Clear the clipboard
        A_Clipboard := ""
        ; Copy the selected text
        Send("^c")
        ; Wait for the clipboard to contain the copied text
        if !ClipWait(1) {
            MsgBox("No text selected or copying failed.")
        } else {
            ; Get the clipboard content
            ClipboardContent := A_Clipboard
            ; Replace all spaces with underscores
            ClipboardContent := StrReplace(ClipboardContent, A_Space, "_")
            ; Put the modified text back in clipboard
            A_Clipboard := ClipboardContent
            ; Paste the modified text (this replaces the selected text)
            Send("^v")
            ; Wait a moment for the paste to complete
            Sleep(50)
        }
        ; Restore the original clipboard content
        A_Clipboard := ClipboardBackup
    }
}

;! Replace - w Space
RAlt & -:: {
    replacedashwithspace()
    replacedashwithspace()
    {
        ; Backup the clipboard
        ClipboardBackup := ClipboardAll()
        ; Clear the clipboard
        A_Clipboard := ""
        ; Copy the selected text
        Send("^c")
        ; Wait for the clipboard to contain the copied text
        if !ClipWait(1) {
            MsgBox("No text selected or copying failed.")
        } else {
            ; Get the clipboard content
            ClipboardContent := A_Clipboard
            ; Replace all dashes with spaces
            ClipboardContent := StrReplace(ClipboardContent, "-", A_Space)
            ; Put the modified text back in clipboard
            A_Clipboard := ClipboardContent
            ; Paste the modified text (this replaces the selected text)
            Send("^v")
            ; Wait a moment for the paste to complete
            Sleep(50)
        }
        ; Restore the original clipboard content
        A_Clipboard := ClipboardBackup
    }
}

;! Send Apps to 2nd Display
!1::Run("C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\display\send_to_2nd.ahk", "", "Hide")

;! Open w VScode
^!n::Run("C:\Users\nahid\ms\ms1\scripts\Autohtokey\version1\VScode_OpenWith.ahk", "", "Hide")

;! Center Apps Window
LAlt & c:: {
    Center_Focused_Window()
    Center_Focused_Window() {
        ; Get the handle of the active (focused) window
        hwnd := WinGetID("A")
        ; Get the position and size of the active window
        WinGetPos(&x, &y, &w, &h, "ahk_id " hwnd)
        ; Get the screen width and height
        ScreenWidth := SysGet(78)
        ScreenHeight := SysGet(79)
        ; Calculate new position to center the window
        newX := (ScreenWidth - w) / 2
        newY := (ScreenHeight - h) / 2
        ; Move the window to the calculated position
        WinMove(newX, newY, , , "ahk_id " hwnd)
    }
}

;! Black Screen
^!b:: {
    Toggle_Screen_Blackout()
    ; Define a variable to track the state of the screen blackout
    Toggle_Screen_Blackout() {
    blackoutState := 0
    ; Define a global variable to store the Gui object
    myGui := ""
    ; Define a function to toggle the screen blackout
        global blackoutState, myGui  ; Declare the variables as global so they can be accessed inside the function
        if (blackoutState = 0) {
            ; If the screen is not blacked out, create a black fullscreen window
            blackoutState := 1
            ; Create the black window to cover the entire screen
            myGui := Gui()
            myGui.Opt("+LastFound +AlwaysOnTop -Caption +ToolWindow") ; Remove caption and border
            myGui.BackColor := "Black"
            myGui.Show("w" . A_ScreenWidth . " h" . A_ScreenHeight . " x0 y0 NoActivate")
        } else {
            ; If the screen is already blacked out, close the window
            blackoutState := 0
            myGui.Destroy()
            myGui := ""  ; Clear the myGui object
        }
    }
}

;! White Screen
^!w:: {
    Toggle_Screen_Whiteout()
    ; Define a variable to track the state of the screen blackout
    Toggle_Screen_Whiteout() {
    whiteState := 0
    ; Define a global variable to store the Gui object
    myGui := ""
    ; Define a function to toggle the screen blackout
        global whiteState, myGui  ; Declare the variables as global so they can be accessed inside the function
        if (whiteState = 0) {
            ; If the screen is not blacked out, create a black fullscreen window
            whiteState := 1
            ; Create the black window to cover the entire screen
            myGui := Gui()
            myGui.Opt("+LastFound +AlwaysOnTop -Caption +ToolWindow") ; Remove caption and border
            myGui.BackColor := "ffffff"
            myGui.Show("w" . A_ScreenWidth . " h" . A_ScreenHeight . " x0 y0 NoActivate")
        } else {
            ; If the screen is already blacked out, close the window
            whiteState := 0
            myGui.Destroy()
            myGui := ""  ; Clear the myGui object
        }
    }
}

;! Execute Script W/O Closing
^!+Enter:: {
    {
        ClipSaved := ClipboardAll()
        A_Clipboard := ""               ; Clear clipboard
        ; Get the active window title
        ActiveTitle := WinGetTitle("A")
        ; If the active window is VSCode, simulate the shortcut to copy the file path
        if InStr(ActiveTitle, "Visual Studio Code") {
            ; Simulate VSCode's shortcut to copy the current file path (Shift + Alt + C)
            Send("+!c")
            Errorlevel := !ClipWait(1)               ; Wait until clipboard has content
        } else {
            ; Send Ctrl+C to copy the selected file path in other environments
            Send("^c")
            Errorlevel := !ClipWait(1)               ; Wait until clipboard has content
        }
        if (A_Clipboard != "") {
            ; Get the selected file path from the clipboard
            FilePath := A_Clipboard
            Ext := SubStr(FilePath, (InStr(FilePath, ".", 0, -1) + 1)<1 ? (InStr(FilePath, ".", 0, -1) + 1)-1 : (InStr(FilePath, ".", 0, -1) + 1))
            ; Check the extension and run the appropriate command
            if (Ext = "py") {
                Run("cmd /k python `"" FilePath "`"", , , &PID)
            } else if (Ext = "ps1") {
                Run("cmd /k powershell -ExecutionPolicy Bypass -File `"" FilePath "`"", , , &PID)
            } else if (Ext = "bat") {
                Run("cmd /k `"" FilePath "`"", , , &PID)
            } else if (Ext = "ahk") {
                Run("cmd /k `"" FilePath "`"", , , &PID)
            } else {
                MsgBox("Unsupported file type: " Ext)
            }
        } else {
            MsgBox("No file path selected or copied.")
        }
        ; Restore original clipboard content
        A_Clipboard := ClipSaved
        return
    }
}

;! Border
^+b:: {
    AddSmartBorder()
    AddSmartBorder()
    {
        ; Copy selected text
        A_Clipboard := ""
        Send("^c")
        ClipWait(1)
        if !A_Clipboard {
            MsgBox "Nothing selected!"
            return
        }
        ; Detect language/file type from window title
        activeTitle := WinGetTitle("A")
        commentStyle := DetectCommentStyle(activeTitle)
        ; Split into lines and normalize tabs → spaces
        rawLines := StrSplit(A_Clipboard, "`n", "`r")
        maxLen := 0
        for i, line in rawLines {
            clean := StrReplace(line, "`t", "    ")
            rawLines[i] := clean
            if (StrLen(clean) > maxLen)
                maxLen := StrLen(clean)
        }
        ; Build borders (only borders are commented, content stays as-is)
        borderChar := commentStyle.border
        topBorder := commentStyle.prefix . " " . StrRepeat(borderChar, maxLen + 4)
        bottomBorder := topBorder
        ; Assemble output: commented borders + content with commented side borders
        output := topBorder . "`r`n"
        for line in rawLines {
            ; Add commented vertical border on right side
            padding := StrRepeat(" ", maxLen + 4 - StrLen(line))
            output .= line . padding . commentStyle.prefix . "`r`n"
        }
        output .= bottomBorder
        ; Replace selection with bordered text
        A_Clipboard := output
        Sleep 50
        Send("^v")
    }
    DetectCommentStyle(windowTitle) {
        ; Convert to lowercase for easier matching
        title := StrLower(windowTitle)
        ; Detect based on file extension or application
        if (InStr(title, ".py") || InStr(title, "python") || InStr(title, "pycharm")) {
            return {type: "line", prefix: "#", border: "#"}
        } else if (InStr(title, ".ps1") || InStr(title, "powershell") || InStr(title, "ise")) {
            return {type: "line", prefix: "#", border: "#"}
        } else if (InStr(title, ".html") || InStr(title, ".htm") || InStr(title, ".xml")) {
            return {type: "html", prefix: "<!--", suffix: "-->"}
        } else if (InStr(title, ".css")) {
            return {type: "block", prefix: "/*", suffix: "*/"}
        } else if (InStr(title, ".js") || InStr(title, ".ts") || InStr(title, ".java") || InStr(title, ".c") || InStr(title, ".cpp")) {
            return {type: "block", prefix: "/*", suffix: "*/"}
        } else if (InStr(title, ".ahk") || InStr(title, "autohotkey")) {
            return {type: "line", prefix: ";", border: "#"}
        } else if (InStr(title, ".bat") || InStr(title, ".cmd")) {
            return {type: "line", prefix: "REM", border: "="}
        } else {
            ; Default fallback - could add input box here to ask user
            return {type: "line", prefix: "#", border: "#"}
        }
    }
    StrRepeat(char, count) {
        result := ""
        Loop count
            result .= char
        return result
    }
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

;! Star
::;star::
