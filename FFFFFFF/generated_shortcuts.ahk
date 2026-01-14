#Requires AutoHotkey v2.0
#SingleInstance
Persistent

Paste(text) {
    Old := A_Clipboard
    A_Clipboard := ""  ; Clear clipboard first
    A_Clipboard := text
    if !ClipWait(1)
        return
    SendInput "^v"
    Sleep 250  ; Wait for paste to complete before restoring clipboard
    A_Clipboard := Old
}

;! === SCRIPT SHORTCUTS ===
;! Run Python Script
;! Opens run.py in the ms1 directory
ScrollLock:: {
    run_py_script()
    run_py_script()
    {
        Run("C:\Users\nahid\ms\ms1\scripts\run\Run.py", , "Show")
        ; Wait a moment for the window to appear
        Sleep(1000)
        ; Make the window always on top (assumes it's the active window)
        ;WinSetAlwaysOnTop(true, "A")
    }
}

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
#x::Run("C:\Users\nahid\ms\ms1\Testing\mypygui\script_manager_gui.py", , "Hide")

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
    Toggle_Screen_Blackout() {
        static blackoutState := 0
        static myGui := ""
        if (blackoutState = 0) {
            blackoutState := 1
            myGui := Gui()
            myGui.Opt("+LastFound +AlwaysOnTop -Caption +ToolWindow")
            myGui.BackColor := "Black"
            myGui.Show("w" . A_ScreenWidth . " h" . A_ScreenHeight . " x0 y0 NoActivate")
        } else {
            blackoutState := 0
            myGui.Destroy()
            myGui := ""
        }
    }
}

;! White Screen
^!w:: {
    Toggle_Screen_Whiteout()
    Toggle_Screen_Whiteout() {
        static whiteState := 0
        static myGui := ""
        if (whiteState = 0) {
            whiteState := 1
            myGui := Gui()
            myGui.Opt("+LastFound +AlwaysOnTop -Caption +ToolWindow")
            myGui.BackColor := "ffffff"
            myGui.Show("w" . A_ScreenWidth . " h" . A_ScreenHeight . " x0 y0 NoActivate")
        } else {
            whiteState := 0
            myGui.Destroy()
            myGui := ""
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
        topBorder := commentStyle.prefix . " " . StrRepeat(borderChar, maxLen + 3)
        bottomBorder := topBorder
        ; Assemble output: commented borders + content with commented side borders
        output := topBorder . "`r`n"
        for line in rawLines {
            ; Calculate padding to align vertical border with horizontal border end
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
        } else if (InStr(title, ".css")) {
            return {type: "line", prefix: "/*", border: "*"}
        } else if (InStr(title, ".js") || InStr(title, ".ts") || InStr(title, ".java") || InStr(title, ".c") || InStr(title, ".cpp")) {
            return {type: "line", prefix: "//", border: "/"}
        } else if (InStr(title, ".ahk") || InStr(title, "autohotkey")) {
            return {type: "line", prefix: ";", border: "#"}
        } else if (InStr(title, ".bat") || InStr(title, ".cmd")) {
            return {type: "line", prefix: "REM", border: "="}
        } else {
            ; Default fallback
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

;! Merge all window in a single explorer
#e:: {
    MergeAllExplorerWindows()
    MergeAllExplorerWindows() {
        ; Get the target window to merge everything into
        mainWindow := WinActive("ahk_class CabinetWClass")
        if (!mainWindow)
            mainWindow := WinExist("ahk_class CabinetWClass")
        if (!mainWindow) {
            Run("explorer.exe")
            return
        }
        pathsToOpen := []
        sourceHwnds := Map()
        ; Collect all paths from all explorer tabs
        shellApp := ComObject("Shell.Application")
        for window in shellApp.Windows {
            try {
                if (window.Name != "Windows Explorer" && window.Name != "File Explorer")
                    continue
                thisHwnd := 0
                try {
                    thisHwnd := window.HWND
                } catch {
                    continue
                }
                if (!thisHwnd || thisHwnd == 0)
                    continue
                if (thisHwnd != mainWindow) {
                    path := ""
                    try {
                        path := window.Document.Folder.Self.Path
                    } catch {
                        try {
                            path := window.LocationURL
                        } catch {
                            path := window.LocationName
                        }
                    }
                    if (path != "" && path != "This PC") {
                        pathsToOpen.Push(path)
                        sourceHwnds[thisHwnd] := true
                    }
                }
            } catch {
                continue
            }
        }
        if (pathsToOpen.Length == 0 && sourceHwnds.Count == 0) {
            return
        }
        ; Backup clipboard
        clipSaved := ClipboardAll()
        WinActivate("ahk_id " . mainWindow)
        if (!WinWaitActive("ahk_id " . mainWindow, , 2)) {
            A_Clipboard := clipSaved
            return
        }
        ; --- DELIBERATE AND STABLE NAVIGATION ---
        for p in pathsToOpen {
            cleanPath := p
            if InStr(cleanPath, "file:///") {
                cleanPath := StrReplace(cleanPath, "file:///", "")
                cleanPath := StrReplace(cleanPath, "/", "\")
                cleanPath := StrReplace(cleanPath, "%20", " ")
            }
            ; 1. Create a new tab and wait for animation to complete
            Send("^t")
            Sleep(800) ; Increased for stability
            ; 2. Focus address bar
            Send("^l")
            Sleep(400)
            ; 3. Clear existing text just in case
            Send("^a") ; Select all
            Sleep(100)
            Send("{BackSpace}")
            Sleep(200)
            ; 4. Update clipboard and PASTE
            A_Clipboard := cleanPath
            Sleep(200) ; Give OS time to register clipboard change
            Send("^v")
            Sleep(400) ; Crucial: Wait for the text to actually appear in the box
            ; 5. Navigation
            Send("{Enter}")
            Sleep(1000) ; Wait for navigation to commit before moving to the next tab
        }
        ; Restore original clipboard
        A_Clipboard := clipSaved
        ; Close other windows
        for hwnd, _ in sourceHwnds {
            try {
                if WinExist("ahk_id " . hwnd) {
                    WinClose("ahk_id " . hwnd)
                    if (WinExist("ahk_id " . hwnd)) {
                        Sleep(500)
                        WinKill("ahk_id " . hwnd)
                    }
                }
            }
        }
        WinActivate("ahk_id " . mainWindow)
    }
}

;! Open With Preferred Editor
^!n:: {
    OpenWithEditor()
    OpenWithEditor() {
        ; Backup current clipboard content
        ClipboardBackup := ClipboardAll()
        ; Clear clipboard and copy the selected file path
        A_Clipboard := ""
        Send("^c")
        if !ClipWait(1) {
            MsgBox("No valid file path found.")
            A_Clipboard := ClipboardBackup
            return
        }
        ClipBoardContent := A_Clipboard
        if InStr(ClipBoardContent, "\") {
            ; Handle multiple files (split by newline)
            FilePaths := ""
            Loop Parse, ClipBoardContent, "`n", "`r"
            {
                if (A_LoopField != "")
                {
                    FilePaths .= '"' . A_LoopField . '" '
                }
            }
            if (FilePaths != "") {
                ; Call editor_chooser.py with all file paths
                Run('python "C:\Users\nahid\ms\ms1\scripts\run\editor_chooser.py" ' . FilePaths)
            }
        } else {
            MsgBox("No valid file path found.")
        }
        ; Restore original clipboard content
        A_Clipboard := ClipboardBackup
    }
}

;! komorebi stop/start
^+k:: {
    komo_start_stop()
    komo_start_stop() {
    RunWait "powershell.exe -Command Stop-Process -Name komorebi -ErrorAction SilentlyContinue", , "Hide"
    Run "komorebic.exe start", , "Hide"
    }
}

;! Quick Shortcut
;! Sleep 250 //    Send " -> "
^q:: {
    KeySequence()
    KeySequence() {
        Send "^!{Numpad2}"
        Sleep 250
        Send "{Enter}"
        Sleep 250
        Send "^!{Numpad1}"
    }
}

;! Take Screenshot
PrintScreen::Run("C:\Users\nahid\ms\ms1\scripts\Autohtokey\version2\gui\Bio.ahk", "", "Hide")

;! Open Folder gui
#f::Run("C:\Users\nahid\ms\ms1\Testing\screenshot\folder_launcher\launcher.py", "", "Hide")

;! Gallery View
#v::Run("C:\Users\nahid\ms\ms1\Testing\screenshot\gallery\gallery.py", "", "Hide")

;! DropClipboard Insert To Field
^+i:: {
    DropClipboard()
    DropClipboard() {
        ; 1. Get current text from clipboard
        clipText := A_Clipboard
        if (clipText == "") {
            ShowNotification("Clipboard is empty!", "Warning")
            return
        }
        ; 2. Create a temporary folder and file
        tempDir := A_Temp "\AutoInsert"
        if !DirExist(tempDir)
            DirCreate(tempDir)
        ; Create a unique filename using timestamp
        fileName := "clip_" A_Now "_" A_TickCount ".txt"
        filePath := tempDir "\" fileName
        try {
            ; Write clipboard content to the new file with UTF-8 encoding (supports Bangla, etc.)
            if FileExist(filePath)
                FileDelete(filePath)
            ; "UTF-8" includes the BOM (Byte Order Mark), which helps Windows apps recognize the text as Unicode.
            FileAppend(clipText, filePath, "UTF-8")
        } catch Error as err {
            MsgBox("Failed to create temporary file:`n" err.Message)
            return
        }
        ; 3. Prepare the Clipboard for "Smart Drop"
        ; We set both File (CF_HDROP) and Text (CF_UNICODETEXT) formats.
        ; This allows Windows to decide: if it's a folder, drop the file; if it's a text field, paste the path.
        if !SetClipboardSmart(filePath) {
            MsgBox("Failed to set clipboard data.")
            return
        }
        ; 4. Perform the "Drop" action
        ; Get window and position under mouse
        MouseGetPos(&mX, &mY, &hWnd)
        ; Optional: Activate the window to ensure it receives the focus/paste
        try {
            WinActivate("ahk_id " hWnd)
        }
        ; Small click to focus the exact element under the mouse
        Click(mX, mY)
        Sleep(100) ; Wait for focus to settle
        ; Send Paste command
        Send("^v")
        ShowNotification("Dropped: " fileName "`n(File & Path ready)", "Success")
    }
    ; --- Helper Functions ---
    /**
     * Sets the clipboard to contain both the file object (for dropping into folders/apps)
     * and the file path string (for pasting into text fields).
     */
    SetClipboardSmart(filePath) {
        if !DllCall("OpenClipboard", "ptr", A_ScriptHwnd)
            return false
        DllCall("EmptyClipboard")
        ; -- 1. Set CF_UNICODETEXT (Pasting path into text fields) --
        hText := DllCall("GlobalAlloc", "uint", 0x42, "ptr", (StrLen(filePath) + 1) * 2, "ptr")
        pText := DllCall("GlobalLock", "ptr", hText, "ptr")
        StrPut(filePath, pText, "UTF-16")
        DllCall("GlobalUnlock", "ptr", hText)
        DllCall("SetClipboardData", "uint", 13, "ptr", hText) ; 13 = CF_UNICODETEXT
        ; -- 2. Set CF_HDROP (Dropping file into folders/browser uploads) --
        ; DROPFILES structure is 20 bytes
        charCount := StrLen(filePath) + 2 ; +1 for null, +1 for double null (required for file lists)
        hDrop := DllCall("GlobalAlloc", "uint", 0x42, "ptr", 20 + (charCount * 2), "ptr")
        pDrop := DllCall("GlobalLock", "ptr", hDrop, "ptr")
        NumPut("uint", 20, pDrop, 0)   ; pFiles: offset to file list
        NumPut("uint", 1, pDrop, 16)  ; fWide: 1 means Unicode
        ; Copy path to the offset 20
        StrPut(filePath, pDrop + 20, "UTF-16")
        ; Double null termination (already handled by GlobalAlloc zero-init, but for safety:)
        NumPut("ushort", 0, pDrop + 20 + (StrLen(filePath) * 2), 0)
        DllCall("GlobalUnlock", "ptr", hDrop)
        DllCall("SetClipboardData", "uint", 15, "ptr", hDrop) ; 15 = CF_HDROP
        DllCall("CloseClipboard")
        return true
    }
    ShowNotification(msg, title := "") {
        ToolTip(title ? title ": " msg : msg)
        SetTimer(() => ToolTip(), -2500)
    }
}

;! Go To SleepMode
#l:: {
    GoToSleep()
    GoToSleep() {
        ; 0 = Standby (Sleep), 1 = Hibernate
        DllCall("PowrProf\SetSuspendState", "Int", 0, "Int", 0, "Int", 0)
    }
}

;! Komorebi W1
#1::Run("komorebic.exe focus-workspace 0", , "Hide")

;! Komorebi W2
#2::Run("komorebic.exe focus-workspace 1", , "Hide")

;! Komorebi Toggle Workspace
#q:: {
    {
        ; Static variables keep their value between keypresses
        static toggle := 0
        if (toggle == 0) {
            Run("komorebic.exe focus-workspace 1", , "Hide")
            toggle := 1
        } else {
            Run("komorebic.exe focus-workspace 0", , "Hide")
            toggle := 0
        }
    }
}

;! === TEXT SHORTCUTS ===
;! AutoHotkey Version 1
;! Inserts AHK v1 header requirement
:X:;v1::Paste('#Requires AutoHotkey v1.0')

;! AutoHotkey Version 2
;! Inserts AHK v2 header requirement
:X:;v2::Paste('{#}Requires AutoHotkey v2.0')

;! Registry Run Path
;! Windows startup registry path run
:X:;run::Paste('HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run')

;! PowerShell Symlink
;! PowerShell command to create symbolic link
:X:;mklink::Paste('New-Item -ItemType SymbolicLink -Path "Fake" -Target "Original" -Force')

;! Symbols
;!   󰩷  󰣉  󰁄 󰁌 󰞘 󰜴 󱞩 󱞫 󰤼
:X:;--::Paste('')

;! Star
:X:;star::Paste('')

;! Db path
:X:;db::Paste('C:\Users\nahid\ms\db')

;! Changes for Ai to know that i made on my files
:X:;change::Paste('ok i have made some changes from last time  so keep that in mind now')

;! Percentage %
:X:;%::Paste('℅')

;! not equal
:X:;notequal::Paste('≠')

;! Theta Sign
:X:;theta::Paste('θ')

;! Custom Syntex [Half]
:X:;cms::Paste("
(
make a study note for this
md syntex formet is a bit different here is how i use them

#1.5#text#/#  = extra big text
##text##  = big text
**text** = bold text
@@text@@ = italic text
__text__ = underline
- text = list 1
-- text = list 2
--- text = list 3
)")
