# Action Code Hints Feature

## What's New

Added helpful placeholder hints in the Script/Action Code field to guide you on what commands to use.

## Visual Guide

### Before
```
┌─────────────────────────────────────┐
│ Script/Action Code:                 │
│ ┌─────────────────────────────────┐ │
│ │                                 │ │
│ │  (empty field)                  │ │
│ │                                 │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### After - Context Shortcuts
```
┌─────────────────────────────────────────────────┐
│ Script/Action Code:                             │
│ ┌─────────────────────────────────────────────┐ │
│ │ Examples:                                   │ │
│ │                                             │ │
│ │ ; Send text (for terminal commands)        │ │
│ │ SendText("/chat save")                     │ │
│ │ SendText("ls -la")                         │ │
│ │                                             │ │
│ │ ; Send keys                                │ │
│ │ Send("^c")  ; Ctrl+C                       │ │
│ │ Send("{Enter}")                            │ │
│ │                                             │ │
│ │ ; Run programs                             │ │
│ │ Run("notepad.exe")                         │ │
│ │                                             │ │
│ │ ; Show message                             │ │
│ │ MsgBox("Hello!")                           │ │
│ │                                             │ │
│ │ ... (more examples)                        │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [📖 Command Reference]  ← NEW BUTTON!          │
└─────────────────────────────────────────────────┘
```

### After - Script Shortcuts
```
┌─────────────────────────────────────────────────┐
│ Script/Action Code:                             │
│ ┌─────────────────────────────────────────────┐ │
│ │ Examples:                                   │ │
│ │                                             │ │
│ │ ; Simple action                            │ │
│ │ Run("notepad.exe")                         │ │
│ │                                             │ │
│ │ ; Multiple lines                           │ │
│ │ {                                          │ │
│ │     MsgBox("Starting...")                  │ │
│ │     Run("notepad.exe")                     │ │
│ │ }                                          │ │
│ │                                             │ │
│ │ ; Send keys                                │ │
│ │ Send("^c")  ; Ctrl+C                       │ │
│ │                                             │ │
│ │ ... (more examples)                        │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [📖 Command Reference]                          │
└─────────────────────────────────────────────────┘
```

### After - Startup Scripts
```
┌─────────────────────────────────────────────────┐
│ Script/Action Code:                             │
│ ┌─────────────────────────────────────────────┐ │
│ │ Examples:                                   │ │
│ │                                             │ │
│ │ ; Background script that runs on startup   │ │
│ │ ; No hotkey needed - runs automatically    │ │
│ │                                             │ │
│ │ ; Register shell hook                      │ │
│ │ DllCall("RegisterShellHookWindow", ...)    │ │
│ │                                             │ │
│ │ ; Set timer                                │ │
│ │ SetTimer(MyFunction, 1000)                 │ │
│ │                                             │ │
│ │ ... (more examples)                        │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ [📖 Command Reference]                          │
└─────────────────────────────────────────────────┘
```

## Command Reference Button

Click the **📖 Command Reference** button to open a comprehensive guide with:

- **Sending Text & Keys** - SendText(), Send(), SendInput()
- **Running Programs** - Run(), RunWait()
- **Window Operations** - WinActivate(), WinClose(), WinMaximize()
- **Clipboard Operations** - Read, write, backup/restore
- **Messages & Dialogs** - MsgBox(), ToolTip(), InputBox()
- **Timing & Delays** - Sleep(), SetTimer()
- **Variables & Strings** - String operations, concatenation
- **Control Flow** - If/Else, Loop, While
- **File Operations** - FileRead(), FileAppend(), FileDelete()
- **Mouse Operations** - Click(), MouseMove(), MouseGetPos()
- **System Information** - A_ScriptDir, A_UserName, A_Now
- **Common Patterns** - Copy/modify/paste, run and activate, etc.
- **Context Shortcut Examples** - Terminal, browser, editor, window management

## Context Shortcut Hints

When creating a **Context Shortcut**, you'll see examples for:

### Terminal Commands
```ahk
SendText("/chat save")
SendText("ls -la")
```

### Sending Keys
```ahk
Send("^c")        ; Ctrl+C
Send("{Enter}")   ; Enter key
Send("!{F4}")     ; Alt+F4
```

### Running Programs
```ahk
Run("notepad.exe")
Run("C:\\path\\to\\program.exe")
```

### Multiple Actions
```ahk
SendText("cd Documents")
Send("{Enter}")
Sleep(100)
SendText("dir")
Send("{Enter}")
```

### Clipboard Operations
```ahk
text := A_Clipboard
MsgBox(text)

A_Clipboard := "New text"
```

### Window Operations
```ahk
WinMaximize("A")   ; Maximize active window
WinMinimize("A")   ; Minimize active window
WinClose("A")      ; Close active window
```

## How to Use

1. **Open Add/Edit Dialog** for any shortcut type
2. **Look at the placeholder hints** in the action field
3. **Click 📖 Command Reference** for detailed documentation
4. **Copy examples** and modify them for your needs
5. **Test incrementally** - start simple, add complexity

## Example Workflow

### Creating a Gemini Save Shortcut

1. Add Context Shortcut
2. See the hints:
   ```
   ; Send text (for terminal commands)
   SendText("/chat save")
   ```
3. Copy the example: `SendText("/chat save")`
4. Paste into action field
5. Done! No need to remember syntax

### Creating a Complex Script

1. Add Script Shortcut
2. Click **📖 Command Reference**
3. Browse to "Common Patterns" section
4. Find "Copy, Modify, Paste" example
5. Copy the code
6. Modify for your needs
7. Test it

## Benefits

✅ **No memorization needed** - Examples right there
✅ **Learn by example** - See real working code
✅ **Quick reference** - Command reference button
✅ **Context-aware** - Different hints for different shortcut types
✅ **Comprehensive** - Covers most common use cases

## Tips

- **Start with examples** - Copy and modify rather than writing from scratch
- **Use Command Reference** - Detailed documentation with all parameters
- **Test incrementally** - Add one command at a time
- **Check syntax** - AutoHotkey v2 syntax is different from v1
- **Read comments** - Hints include helpful comments

## Common Commands Quick Reference

### Most Used for Context Shortcuts

```ahk
SendText("text")           ; Send literal text
Send("^c")                 ; Send Ctrl+C
Send("{Enter}")            ; Send Enter
Run("program.exe")         ; Run program
MsgBox("message")          ; Show message
Sleep(1000)                ; Wait 1 second
A_Clipboard := "text"      ; Set clipboard
text := A_Clipboard        ; Get clipboard
```

### Most Used for Script Shortcuts

```ahk
Run("notepad.exe")         ; Launch program
Send("^c")                 ; Copy
Send("^v")                 ; Paste
WinActivate("Title")       ; Activate window
WinMaximize("A")           ; Maximize active
MsgBox("Hello")            ; Show message
```

### Most Used for Startup Scripts

```ahk
SetTimer(Func, 1000)       ; Run every 1 sec
DllCall("Function", ...)   ; Call Windows API
OnClipboardChange(Func)    ; Monitor clipboard
```

## Files

- **AHK_COMMAND_REFERENCE.md** - Complete command reference (opens when you click the button)
- **ahk_gui_pyqt.py** - Updated with placeholder hints and reference button

## Future Enhancements

Potential improvements:
- Syntax highlighting in action field
- Auto-completion for commands
- Inline documentation tooltips
- Code snippets library
- Template shortcuts
