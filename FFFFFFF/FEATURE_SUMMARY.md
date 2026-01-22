# Context-Aware Shortcuts Feature Summary

## What Was Added

### New Shortcut Type: Context Shortcuts
Window-specific hotkeys that only activate in certain contexts, just like your `gemini.ahk` file.

## GUI Changes

### Add Menu
```
+ Add
  ├─ Script Shortcut
  ├─ Text Shortcut
  ├─ Context Shortcut  ← NEW!
  └─ Background Script
```

### Display Layout
```
┌─────────────────┬─────────────────┬─────────────────┐
│ Script          │ Context         │ Text            │
│ Shortcuts       │ Shortcuts       │ Shortcuts       │
│                 │    ← NEW!       │                 │
│ !x → Terminal   │ ^s [Gemini]     │ ;v1 → AHK v1    │
│ #x → GUI        │ ^r [Gemini]     │ ;v2 → AHK v2    │
│ ...             │ ...             │ ...             │
└─────────────────┴─────────────────┴─────────────────┘
```

### Dialog Fields
When adding/editing a context shortcut:
```
Name: _______________
Category: [Dropdown]
Description: _______________
Enabled: [✓]

Hotkey: _____ [⌨]

Window Title: _______________  (e.g., Gemini, Visual Studio Code)
Process Name: _______________  (e.g., WindowsTerminal.exe)
Window Class: _______________  (e.g., CabinetWClass)

Action Code:
┌─────────────────────────────┐
│                             │
│  SendText("/chat save")     │
│                             │
└─────────────────────────────┘
```

## How It Works

### Input
```json
{
  "name": "Gemini Save Chat",
  "hotkey": "^s",
  "window_title": "Gemini",
  "process_name": "WindowsTerminal.exe",
  "action": "SendText(\"/chat save\")"
}
```

### Generated Output
```ahk
IsGeminiSaveChatContext() {
    try {
        processName := WinGetProcessName("A")
        windowTitle := WinGetTitle("A")
        if (processName = "WindowsTerminal.exe" && InStr(windowTitle, "Gemini")) {
            return true
        }
    }
    return false
}

#HotIf IsGeminiSaveChatContext()

^s::{
    SendText("/chat save")
}

#HotIf
```

## Example Use Cases

### Terminal Shortcuts
- **Gemini Terminal:** Ctrl+S to save, Ctrl+R to resume
- **SSH Sessions:** Context-specific commands
- **Different shells:** PowerShell vs CMD vs Bash

### Browser Shortcuts
- **Chrome:** Ctrl+Shift+T for specific actions
- **Firefox:** Different behavior for same hotkey
- **Edge:** Browser-specific automation

### Editor Shortcuts
- **VS Code:** Project-specific shortcuts
- **Notepad++:** Different actions per file type
- **Sublime:** Context-aware commands

### File Explorer
- **Specific folders:** Shortcuts that only work in certain directories
- **Network drives:** Different actions for network vs local
- **Archive files:** Context-specific operations

## Benefits

✅ **No Conflicts:** Same hotkey, different actions in different windows
✅ **Organized:** Separate context shortcuts from global ones
✅ **Flexible:** Mix window title, process, and class matching
✅ **Powerful:** Full AutoHotkey scripting in context-aware mode
✅ **Visual:** See context info directly in the GUI

## Files Added/Modified

### New Files
- `CONTEXT_SHORTCUTS_GUIDE.md` - Complete documentation
- `RECENT_CHANGES.md` - Change log
- `gemini.ahk` - Example context shortcut file

### Modified Files
- `ahk_gui_pyqt.py` - Full context shortcut support
- `ahk_shortcuts.json` - Added context_shortcuts array with examples

## Quick Start

1. Open `ahk_gui_pyqt.py`
2. Click "+ Add" → "Context Shortcut"
3. Fill in:
   - Name: "My Context Shortcut"
   - Hotkey: "^s"
   - Window Title: "Notepad"
   - Action: `MsgBox("Hello from Notepad!")`
4. Click OK
5. Click "🚀 Generate AHK"
6. Run `generated_shortcuts.ahk`
7. Open Notepad and press Ctrl+S

The shortcut only works in Notepad! 🎉
