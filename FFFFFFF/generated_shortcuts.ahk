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
        Run("C:\@delta\ms1\scripts\run\Run.py", , "Show")
        ; Wait a moment for the window to appear
        Sleep(1000)
        ; Make the window always on top (assumes it's the active window)
        ;WinSetAlwaysOnTop(true, "A")
    }
}

;! Monitor Internal
;! Switch to internal monitor only
RAlt & Numpad1::Run("C:\@delta\msBackups\Display\DisplaySwitch.exe /internal", "", "Hide")

;! Monitor External
;! Switch to external monitor only
RAlt & Numpad2::Run("C:\@delta\msBackups\Display\DisplaySwitch.exe /external", "", "Hide")

;! Monitor Extend
;! Extend display to both monitors
RAlt & Numpad3::Run("C:\@delta\msBackups\Display\DisplaySwitch.exe /extend", "", "Hide")

;! Bio GUI
;! Opens Bio.ahk GUI
!b::Run("C:\@delta\ms1\scripts\Autohtokey\version2\gui\Bio.ahk", "", "Hide")

;! Ultimate GUI
;! Opens Ultimate_Gui.py
!u::Run("C:\@delta\ms1\Ultimate_Gui.py", "", "Hide")

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
        Run("C:\@delta\msBackups\Display\DisplaySwitch.exe /internal",,"Hide")
    }
}

;! mypygui
#x::Run('pythonw "C:\@delta\ms1\Testing\mypygui\qt\script_manager_gui_qt.py"')

;! Startup Setup
#s::Run("C:\@delta\ms1\scripts\flask\4999_startup\startup.py", , "Hide")

;! CrossHair
^+m::Run("C:\@delta\ms1\scripts\xy\XY_CroosHair.py", , "Hide")

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
!1::Run("C:\@delta\ms1\scripts\Autohtokey\version2\display\send_to_2nd.ahk", "", "Hide")

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
            ; Extract the directory from the file path
            SplitPath(FilePath, , &FileDir)
            Ext := SubStr(FilePath, (InStr(FilePath, ".", 0, -1) + 1)<1 ? (InStr(FilePath, ".", 0, -1) + 1)-1 : (InStr(FilePath, ".", 0, -1) + 1))
            ; Check the extension and run the appropriate command with working directory
            if (Ext = "py") {
                Run("cmd /k python `"" FilePath "`"", FileDir, , &PID)
            } else if (Ext = "ps1") {
                Run("cmd /k powershell -ExecutionPolicy Bypass -File `"" FilePath "`"", FileDir, , &PID)
            } else if (Ext = "bat") {
                Run("cmd /k `"" FilePath "`"", FileDir, , &PID)
            } else if (Ext = "ahk") {
                Run("cmd /k `"" FilePath "`"", FileDir, , &PID)
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
            Loop Parse, ClipBoardContent, "`n", "`r" {
                if (A_LoopField != "") {
                    FilePaths .= '"' . A_LoopField . '" '
                }
            }
            if (FilePaths != "") {
                ; Use pythonw to run without console window
                Run('pythonw "C:\@delta\ms1\scripts\run\editor_chooser.py" ' . FilePaths, , "Hide")
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
PrintScreen::Run("C:\@delta\ms1\scripts\Autohtokey\version2\gui\Bio.ahk", "", "Hide")

;! Open Folder gui
#f::Run("C:\@delta\ms1\Testing\screenshot\folder_launcher\launcher.py", "", "Hide")

;! Gallery View
#v::Run("C:\@delta\ms1\Testing\screenshot\gallery\gallery.py", "", "Hide")

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
:X:;db::Paste('C:\@delta\db')

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
Dont add unnecessary extra lines between heading and its content
dont use --- or dash to add separator just keep single empty line for spacing
)")

;! Cyberpunk styling with pyqt
:X:;cyberpunk::Paste("
(
# Cyberpunk UI Theme Guide


A reusable styling reference for PyQt6 applications with a dark, neon-accented cyberpunk aesthetic.


---


## Color Palette


```python
# Core Colors
CP_BG = ""#050505""           # Main Background (almost black)
CP_PANEL = ""#111111""        # Panel/Card Background
CP_DIM = ""#3a3a3a""          # Dimmed/Inactive elements, borders


# Text Colors
CP_TEXT = ""#E0E0E0""         # Primary text
CP_SUBTEXT = ""#808080""      # Secondary/muted text


# Accent Colors
CP_YELLOW = ""#FCEE0A""       # Primary accent (Cyber Yellow)
CP_CYAN = ""#00F0FF""         # Secondary accent (Neon Cyan)
CP_RED = ""#FF003C""          # Error/Delete/Danger
CP_GREEN = ""#00FF00""        # Success/Confirm
CP_MAGENTA = ""#FF00FF""      # Alternate accent
CP_ORANGE = ""#FFA500""       # Warning/Highlight
```


---


## Typography


- **Primary Font:** `Consolas` (monospace)
- **Fallback:** Any monospace font
- **Weights:** Normal (400), Bold (700)
- **Sizes:**
  - Headers: 16px bold
  - Section titles: 11-12px bold
  - Body text: 10-11px
  - Labels/Status: 8-9px
  - Timestamps: 7px


```python
from PyQt6.QtGui import QFont


# Header
QFont(""Consolas"", 16, QFont.Weight.Bold)


# Section Title
QFont(""Consolas"", 11, QFont.Weight.Bold)


# Body/Button
QFont(""Consolas"", 10, QFont.Weight.Bold)


# Small Labels
QFont(""Consolas"", 8)
```


---


## Button Styles


### Solid Button (Primary Action)
```python
QPushButton {
    background-color: #FCEE0A;
    color: #050505;
    border: none;
    padding: 5px 15px;
    font-family: 'Consolas';
    font-weight: bold;
}
QPushButton:hover {
    background-color: #050505;
    color: #FCEE0A;
    border: 1px solid #FCEE0A;
}
```


### Outlined Button (Secondary Action)
```python
QPushButton {
    background-color: transparent;
    color: #FCEE0A;
    border: 2px solid #FCEE0A;
    padding: 5px 15px;
    font-family: 'Consolas';
    font-weight: bold;
}
QPushButton:hover {
    background-color: #FCEE0A;
    color: #050505;
}
```


### Danger Button
```python
QPushButton {
    background-color: transparent;
    color: #FF003C;
    border: 2px solid #FF003C;
    padding: 5px 15px;
    font-family: 'Consolas';
}
QPushButton:hover {
    background-color: #FF003C;
    color: #050505;
}
```


---


## Input Fields


```python
QLineEdit {
    background-color: #111111;
    color: #FCEE0A;
    border: 1px solid #3a3a3a;
    padding: 8px;
    font-family: 'Consolas';
}
QLineEdit:focus {
    border: 1px solid #00F0FF;
}
QLineEdit::placeholder {
    color: #808080;
}
```


---


## Dropdown / ComboBox


```python
QComboBox {
    background-color: transparent;
    color: #00F0FF;
    border: 1px solid #00F0FF;
    padding: 5px 15px;
    font-family: 'Consolas';
    font-weight: bold;
}
QComboBox:hover {
    background-color: #00F0FF;
    color: #050505;
}
QComboBox::drop-down {
    border: 0px;
    width: 0px;
}
QComboBox QAbstractItemView {
    background-color: #111111;
    color: #E0E0E0;
    selection-background-color: #00F0FF;
    selection-color: #050505;
    border: 1px solid #00F0FF;
    outline: none;
}
```


---


## Checkbox


```python
QCheckBox {
    color: #E0E0E0;
    font-family: 'Consolas';
    font-size: 11px;
    spacing: 10px;
    padding: 10px;
    border: 1px solid #111111;
    background: #111111;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #3a3a3a;
    background: #050505;
}
QCheckBox::indicator:checked {
    background: #FCEE0A;
    border: 1px solid #FCEE0A;
}
QCheckBox::indicator:hover {
    border: 1px solid #00F0FF;
}
QCheckBox:hover {
    border: 1px solid #3a3a3a;
    background: #1a1a25;
}
```


---


## Context Menu


```python
QMenu {
    background-color: #050505;
    color: #E0E0E0;
    border: 1px solid #00F0FF;
    font-family: 'Consolas';
}
QMenu::item {
    padding: 6px 25px;
    background-color: transparent;
}
QMenu::item:selected {
    background-color: #00F0FF;
    color: #050505;
}
```


---


## Scrollbar


```python
QScrollBar:vertical {
    background: #050505;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #3a3a3a;
}
QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}
```


---


## Cards / List Items


```python
/* Item card with left accent border */
QFrame {
    background-color: #0f0f15;
    border-left: 3px solid #FCEE0A;  /* Active state */
    border-bottom: 1px solid #111111;
}
QFrame:hover {
    background-color: #1a1a25;
}


/* Inactive state: change border-left to #3a3a3a */
```


---


## Status Toggle Button


```python
/* Active State */
QPushButton {
    background-color: #FCEE0A;
    color: #050505;
    border: 1px solid #FCEE0A;
    border-radius: 0px;
}


/* Inactive State */
QPushButton {
    background-color: transparent;
    color: #808080;
    border: 1px solid #3a3a3a;
    border-radius: 0px;
}
QPushButton:hover {
    border: 1px solid #00F0FF;
    color: #00F0FF;
}
```


---


## Dialog Windows


```python
QDialog {
    background-color: #050505;
    border: 1px solid #3a3a3a;
}
QDialog QLabel {
    color: #00F0FF;
    font-family: 'Consolas';
    font-weight: bold;
    font-size: 12px;
}
```


---


## Headers & Labels


```python
/* Main Title */
QLabel {
    color: #FCEE0A;
    font-family: 'Consolas';
    font-size: 16px;
    font-weight: bold;
    letter-spacing: 2px;
}


/* Section Header */
QLabel {
    color: #808080;
    font-family: 'Consolas';
    font-size: 11px;
    font-weight: bold;
    padding-bottom: 5px;
    border-bottom: 2px solid #3a3a3a;
}


/* Status Text */
QLabel {
    color: #00F0FF;
    font-family: 'Consolas';
    font-size: 10px;
}
```


---


## Splitter


```python
QSplitter::handle {
    background-color: #3a3a3a;
}
QSplitter::handle:hover {
    background-color: #00F0FF;
}
```


---


## Design Principles


1. **Dark Foundation:** Near-black backgrounds (#050505, #111111)
2. **Neon Accents:** Yellow for primary, Cyan for secondary, Red for danger
3. **Monospace Typography:** Consolas throughout for that terminal/hacker feel
4. **Sharp Edges:** No border-radius (0px) for that angular cyberpunk look
5. **Hover States:** Invert colors on hover (bg becomes text color, text becomes bg)
6. **Left Border Accents:** Use colored left borders to indicate state/importance
7. **Uppercase Text:** Headers and labels in uppercase for impact
8. **Minimal Padding:** Tight, efficient layouts
9. **Status Indicators:** Text-based (""ON""/""OFF"", ""ACTV"") rather than icons


---


## Naming Conventions


Use tech/system-inspired terminology:
- ""EXECUTE PROTOCOL"" instead of ""Run""
- ""PURGE ENTRY"" instead of ""Delete""
- ""EDIT CONFIG"" instead of ""Edit""
- ""SCAN_SYS"" instead of ""Scan System""
- ""UPLOAD"" instead of ""Save""
- ""ABORT"" instead of ""Cancel""
- ""IDENTITY // NAME"" instead of ""Name""
- ""SOURCE // PATH"" instead of ""Path""


---


## Quick Start Template


```python
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QFont


# Palette
CP_BG = ""#050505""
CP_PANEL = ""#111111""
CP_YELLOW = ""#FCEE0A""
CP_CYAN = ""#00F0FF""
CP_RED = ""#FF003C""
CP_DIM = ""#3a3a3a""
CP_TEXT = ""#E0E0E0""
CP_SUBTEXT = ""#808080""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f""QMainWindow {{ background-color: {CP_BG}; }}"")
        # ... your UI setup


if __name__ == ""__main__"":
    app = QApplication([])
    app.setStyle(""Fusion"")  # Important for consistent styling
    window = MainWindow()
    window.show()
    app.exec()
```


---


*Generated from startup.py cyberpunk theme implementation*
)")

;! Check summary and unorganized data in ai
:X:;check::Paste('here is everything added to summary or it missed something')

;! AI Instruction Prompt 1
:X:;commit::Paste("
(
IMPORTANT:
- here when i say commit then commit the current changes in my github and then push
- only commit when i type ""commit""
- use emoji ✅when resolved any bug and ⚠️ when facing any issue etc to make the commit message more attractive
- also first update the md files then commit [update whatever md files needs update like recent changes, problem solving md, new feature md etc]
- use only 1 line for commit message
)")

;! AI - Instruction For md file
:X:;ai1::Paste("
(
For Projects Always create a Dev.md file and discuss important thing about the project general idea important things etc and also make a md directory where u will add Provlems_Solution.md where u will update  problems and how we resolved them in this structure

## Template for New Entries
## [YYYY-MM-DD HH:MM] - Brief Problem Title

**Problem:** 
Description of the issue observed

**Root Cause:** 
What was actually causing the problem

**Solution:** 
How it was fixed (include key code changes)

**Files Modified:**
- `file1.js` - Brief description of change
- `file2.css` - Brief description of change

**Related Issues:** Links to related problems or ""None""
)")

;! Unresolved ai orompt
:X:;unresolved::Paste('still shows as power in both checked and unchecked situatin ok add it to problem & talk about how u tried to reslove it i will use another ai')
