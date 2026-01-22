# AutoHotkey v2 Command Reference

Quick reference for common AutoHotkey v2 commands to use in your shortcuts.

## Sending Text & Keys

### SendText()
Sends text literally (no special key interpretation)
```ahk
SendText("Hello World")
SendText("/chat save")
SendText("cd Documents")
```

### Send()
Sends keys with special key support
```ahk
Send("^c")           ; Ctrl+C
Send("^v")           ; Ctrl+V
Send("!{F4}")        ; Alt+F4
Send("{Enter}")      ; Enter key
Send("{Tab}")        ; Tab key
Send("^+{Esc}")      ; Ctrl+Shift+Esc
Send("{Up 5}")       ; Up arrow 5 times
```

**Common Special Keys:**
- `^` = Ctrl
- `!` = Alt
- `+` = Shift
- `#` = Win
- `{Enter}` = Enter
- `{Tab}` = Tab
- `{Esc}` = Escape
- `{Space}` = Space
- `{Up}`, `{Down}`, `{Left}`, `{Right}` = Arrow keys
- `{Home}`, `{End}`, `{PgUp}`, `{PgDn}` = Navigation
- `{F1}` through `{F12}` = Function keys
- `{Delete}`, `{Backspace}` = Delete keys

### SendInput()
Faster, more reliable sending (recommended for long sequences)
```ahk
SendInput("^c")
SendInput("{Enter}")
```

## Running Programs

### Run()
Launch programs or open files
```ahk
Run("notepad.exe")
Run("C:\\Program Files\\App\\app.exe")
Run("https://google.com")  ; Opens in default browser
Run("explorer.exe C:\\Users")
Run("cmd.exe")
Run("powershell.exe")
```

**With working directory:**
```ahk
Run("python script.py", "C:\\Projects")
```

**With options:**
```ahk
Run("notepad.exe", , "Hide")      ; Hidden
Run("notepad.exe", , "Max")       ; Maximized
Run("notepad.exe", , "Min")       ; Minimized
```

### RunWait()
Run and wait for program to close
```ahk
RunWait("notepad.exe")
MsgBox("Notepad closed!")
```

## Window Operations

### WinActivate()
Bring window to front
```ahk
WinActivate("A")                    ; Active window
WinActivate("Untitled - Notepad")   ; By title
WinActivate("ahk_exe chrome.exe")   ; By process
WinActivate("ahk_class Notepad")    ; By class
```

### WinClose()
Close window
```ahk
WinClose("A")                       ; Active window
WinClose("Untitled - Notepad")
```

### WinMaximize(), WinMinimize(), WinRestore()
Change window state
```ahk
WinMaximize("A")
WinMinimize("A")
WinRestore("A")
```

### WinMove()
Move/resize window
```ahk
WinMove(100, 100, 800, 600, "A")  ; x, y, width, height
```

### WinGetTitle()
Get window title
```ahk
title := WinGetTitle("A")
MsgBox(title)
```

### WinGetProcessName()
Get process name
```ahk
process := WinGetProcessName("A")
MsgBox(process)
```

### WinExist(), WinActive()
Check if window exists or is active
```ahk
if WinExist("Notepad") {
    MsgBox("Notepad is open")
}

if WinActive("A") {
    MsgBox("Window is active")
}
```

## Clipboard Operations

### Read Clipboard
```ahk
text := A_Clipboard
MsgBox(text)
```

### Set Clipboard
```ahk
A_Clipboard := "New text"
A_Clipboard := ""  ; Clear clipboard
```

### Wait for Clipboard
```ahk
A_Clipboard := ""
Send("^c")
if ClipWait(1) {  ; Wait 1 second
    MsgBox("Copied: " A_Clipboard)
}
```

### Backup/Restore Clipboard
```ahk
saved := ClipboardAll()  ; Backup
A_Clipboard := "Temporary text"
; ... do stuff ...
A_Clipboard := saved  ; Restore
```

## Messages & Dialogs

### MsgBox()
Show message
```ahk
MsgBox("Hello!")
MsgBox("Title", "Message text")
MsgBox("Error!", "Something went wrong", "Icon!")
```

### ToolTip()
Show tooltip
```ahk
ToolTip("Processing...")
Sleep(2000)
ToolTip()  ; Hide tooltip
```

### InputBox()
Get user input
```ahk
result := InputBox("Enter your name:", "Input")
if result.Result = "OK" {
    MsgBox("Hello " result.Value)
}
```

## Timing & Delays

### Sleep()
Pause execution
```ahk
Sleep(1000)  ; 1 second
Sleep(500)   ; 0.5 seconds
```

### SetTimer()
Run function repeatedly
```ahk
SetTimer(MyFunction, 1000)  ; Every 1 second
SetTimer(MyFunction, -5000) ; Once after 5 seconds
SetTimer(MyFunction, 0)     ; Stop timer

MyFunction() {
    ToolTip("Timer fired!")
}
```

## Variables & Strings

### Variables
```ahk
myVar := "Hello"
number := 42
result := 10 + 20
```

### String Operations
```ahk
; Concatenation
fullName := firstName " " lastName

; Length
len := StrLen("Hello")

; Replace
newStr := StrReplace("Hello World", "World", "AHK")

; Upper/Lower case
upper := StrUpper("hello")
lower := StrLower("HELLO")

; Contains
if InStr("Hello World", "World") {
    MsgBox("Found!")
}

; Split
parts := StrSplit("a,b,c", ",")
```

## Control Flow

### If/Else
```ahk
if (condition) {
    ; do something
} else if (other) {
    ; do other
} else {
    ; default
}
```

### Loop
```ahk
Loop 5 {
    MsgBox("Iteration " A_Index)
}

Loop Files, "C:\\*.txt" {
    MsgBox(A_LoopFileName)
}
```

### While
```ahk
count := 0
while (count < 5) {
    count++
    MsgBox(count)
}
```

## File Operations

### FileRead()
Read file content
```ahk
content := FileRead("C:\\file.txt")
MsgBox(content)
```

### FileAppend()
Append to file
```ahk
FileAppend("New line`n", "C:\\file.txt")
```

### FileDelete()
Delete file
```ahk
FileDelete("C:\\file.txt")
```

### FileExist()
Check if file exists
```ahk
if FileExist("C:\\file.txt") {
    MsgBox("File exists")
}
```

## Mouse Operations

### Click()
Click mouse
```ahk
Click()              ; Left click at current position
Click(100, 200)      ; Click at coordinates
Click("Right")       ; Right click
Click(2)             ; Double click
```

### MouseMove()
Move mouse
```ahk
MouseMove(100, 200)
MouseMove(100, 200, 50)  ; Speed 50 (0-100)
```

### MouseGetPos()
Get mouse position
```ahk
MouseGetPos(&x, &y)
MsgBox("X: " x " Y: " y)
```

## System Information

### A_ScriptDir
Script directory
```ahk
MsgBox(A_ScriptDir)
```

### A_WorkingDir
Current working directory
```ahk
MsgBox(A_WorkingDir)
```

### A_UserName
Current user
```ahk
MsgBox(A_UserName)
```

### A_ComputerName
Computer name
```ahk
MsgBox(A_ComputerName)
```

### A_Now
Current date/time
```ahk
MsgBox(A_Now)  ; Format: YYYYMMDDHH24MISS
```

## Common Patterns

### Copy, Modify, Paste
```ahk
saved := ClipboardAll()
A_Clipboard := ""
Send("^c")
ClipWait(1)
text := A_Clipboard
text := StrReplace(text, "old", "new")
A_Clipboard := text
Send("^v")
Sleep(100)
A_Clipboard := saved
```

### Run and Activate
```ahk
Run("notepad.exe")
Sleep(500)
WinActivate("Untitled - Notepad")
```

### Toggle Window State
```ahk
if WinActive("Notepad") {
    WinMinimize("A")
} else {
    WinActivate("Notepad")
}
```

### Send Command to Terminal
```ahk
SendText("cd Documents")
Send("{Enter}")
Sleep(100)
SendText("dir")
Send("{Enter}")
```

### Conditional Action
```ahk
if WinActive("ahk_exe chrome.exe") {
    Send("^t")  ; New tab in Chrome
} else {
    Run("chrome.exe")
}
```

## Context Shortcut Examples

### Terminal Commands
```ahk
; Save chat in Gemini
SendText("/chat save")

; Git commands
SendText("git status")
Send("{Enter}")

; SSH commands
SendText("ssh user@server")
Send("{Enter}")
```

### Browser Automation
```ahk
; New tab
Send("^t")

; Close tab
Send("^w")

; Refresh
Send("{F5}")

; Developer tools
Send("{F12}")
```

### Editor Shortcuts
```ahk
; Save all
Send("^+s")

; Format document
Send("!+f")

; Comment line
Send("^/")
```

### Window Management
```ahk
; Maximize
WinMaximize("A")

; Move to second monitor
WinMove(1920, 0, , , "A")

; Always on top toggle
WinSetAlwaysOnTop(-1, "A")
```

## Tips

1. **Use SendText() for literal text** (terminal commands, chat messages)
2. **Use Send() for key combinations** (Ctrl+C, Alt+F4)
3. **Add Sleep() between actions** to ensure they complete
4. **Backup clipboard** before modifying it
5. **Check window state** before acting on it
6. **Use WinWait()** to wait for windows to appear
7. **Test incrementally** - add one command at a time

## Resources

- [Official AHK v2 Documentation](https://www.autohotkey.com/docs/v2/)
- [Command List](https://www.autohotkey.com/docs/v2/lib/)
- [Tutorial](https://www.autohotkey.com/docs/v2/Tutorial.htm)
