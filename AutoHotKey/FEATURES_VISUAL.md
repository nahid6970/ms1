# Visual Feature Overview

## GUI Layout

```
┌────────────────────────────────────────────────────────────────────┐
│  AutoHotkey Script Editor                                    [_][□][X]│
├────────────────────────────────────────────────────────────────────┤
│  [+ Add ▼] [🗂] [🎨 Colors] [🔍 Search...] [⌨] [🚀 Generate AHK]  │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┬──────────────┬──────────────┐                  │
│  │ Script       │ Context      │ Text         │                  │
│  │ Shortcuts    │ Shortcuts    │ Shortcuts    │                  │
│  ├──────────────┼──────────────┼──────────────┤                  │
│  │ 📁 System    │ 📁 Terminal  │ 📁 AHK       │                  │
│  │ ✅ !x        │ ✅ ^s        │ ✅ ;v1       │                  │
│  │   → Terminal │   [Gemini]   │   → AHK v1   │                  │
│  │              │   → Save     │              │                  │
│  │ 📁 Launch    │ ✅ ^r        │ 📁 Text      │                  │
│  │ ✅ #x        │   [Gemini]   │ ✅ ;run      │                  │
│  │   → GUI      │   → Resume   │   → Path     │                  │
│  │              │              │              │                  │
│  │ 📁 Display   │ 📁 Browser   │ 📁 General   │                  │
│  │ ✅ !1        │ ✅ ^t        │ ✅ ;cms      │                  │
│  │   → 2nd Mon  │   [Chrome]   │   → Template │                  │
│  │              │   → New Tab  │              │                  │
│  └──────────────┴──────────────┴──────────────┘                  │
│                                                                    │
│  Background Scripts                                                │
│  📁 General                                                        │
│  ❌ 🚀 Startup → Explorer Tabs Hook                               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Add Menu

```
┌─────────────────────┐
│ + Add               │
├─────────────────────┤
│ Script Shortcut     │  ← Global hotkeys
│ Text Shortcut       │  ← Text expansion
│ Context Shortcut    │  ← Window-specific (NEW!)
│ Background Script   │  ← Auto-run on startup
└─────────────────────┘
```

## Context Menu (Right-Click)

```
┌─────────────────┐
│ Edit            │  ← Open edit dialog
│ Duplicate       │  ← Copy shortcut (NEW!)
├─────────────────┤
│ Remove          │  ← Delete shortcut
└─────────────────┘
```

## Add/Edit Dialog - Context Shortcut

```
┌──────────────────────────────────────────────────────────────┐
│  Add Context Shortcut                              [_][□][X]  │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────┬────────────────────────────────┐ │
│  │ Name: _______________  │ Script/Action Code:            │ │
│  │                        │ ┌────────────────────────────┐ │ │
│  │ Category: [Terminal ▼] │ │ Examples:                  │ │ │
│  │                        │ │                            │ │ │
│  │ Description: _______   │ │ ; Send text (terminal)     │ │ │
│  │                        │ │ SendText("/chat save")     │ │ │
│  │ [✓] Enabled            │ │                            │ │ │
│  │                        │ │ ; Send keys                │ │ │
│  │ Hotkey: ^s      [⌨]   │ │ Send("^c")  ; Ctrl+C       │ │ │
│  │                        │ │ Send("{Enter}")            │ │ │
│  │ Window Title:          │ │                            │ │ │
│  │ Gemini_____________    │ │ ; Run programs             │ │ │
│  │                        │ │ Run("notepad.exe")         │ │ │
│  │ Process Name:          │ │                            │ │ │
│  │ WindowsTerminal.exe_   │ │ ; Multiple actions         │ │ │
│  │                        │ │ SendText("cd Documents")   │ │ │
│  │ Window Class:          │ │ Send("{Enter}")            │ │ │
│  │ ___________________    │ │ Sleep(100)                 │ │ │
│  │                        │ │ SendText("dir")            │ │ │
│  └────────────────────────┤ │ Send("{Enter}")            │ │ │
│                           │ │                            │ │ │
│                           │ │ ... (more examples)        │ │ │
│                           │ └────────────────────────────┘ │ │
│                           │                                │ │
│                           │ [📖 Command Reference]         │ │
│                           └────────────────────────────────┘ │
│                                                              │
│                                    [OK]  [Cancel]            │
└──────────────────────────────────────────────────────────────┘
```

## Shortcut Builder (⌨ Button)

```
┌────────────────────────────────────┐
│  Shortcut Builder        [_][□][X] │
├────────────────────────────────────┤
│                                    │
│  Preview: Ctrl+Shift+S             │
│                                    │
│  Modifiers:                        │
│  [✓ Ctrl] [✓ Shift] [ Alt] [ Win] │
│                                    │
│  Select Main Key:                  │
│  [s                            ▼]  │
│                                    │
│  Search: s___________________      │
│                                    │
│  Quick Keys:                       │
│  [Space] [Enter] [Tab] [Esc]       │
│  [Up] [Down]                       │
│                                    │
│                    [OK]  [Cancel]  │
└────────────────────────────────────┘
```

## Command Reference Dialog

```
┌────────────────────────────────────────────────────────────┐
│  AutoHotkey Command Reference                    [_][□][X] │
├────────────────────────────────────────────────────────────┤
│  # AutoHotkey v2 Command Reference                         │
│                                                            │
│  ## Sending Text & Keys                                    │
│                                                            │
│  ### SendText()                                            │
│  Sends text literally (no special key interpretation)      │
│  ```ahk                                                    │
│  SendText("Hello World")                                   │
│  SendText("/chat save")                                    │
│  ```                                                       │
│                                                            │
│  ### Send()                                                │
│  Sends keys with special key support                       │
│  ```ahk                                                    │
│  Send("^c")           ; Ctrl+C                             │
│  Send("{Enter}")      ; Enter key                          │
│  ```                                                       │
│                                                            │
│  ... (scrollable content)                                  │
│                                                            │
│                                              [Close]       │
└────────────────────────────────────────────────────────────┘
```

## Feature Comparison

### Before vs After

#### Before (Basic)
```
Features:
✓ Script shortcuts
✓ Text shortcuts
✓ Background scripts
✓ Basic editing
✓ Generate AHK script
```

#### After (Enhanced)
```
Features:
✓ Script shortcuts
✓ Text shortcuts
✓ Background scripts
✓ Context shortcuts        ← NEW!
✓ Basic editing
✓ Duplicate shortcuts      ← NEW!
✓ Action code hints        ← NEW!
✓ Command reference        ← NEW!
✓ Generate AHK script
✓ Working directory fix    ← NEW!
```

## Workflow Visualization

### Creating Context Shortcuts

```
Step 1: Add Context Shortcut
   ↓
Step 2: Fill in details
   ├─ Name: "Gemini Save"
   ├─ Hotkey: ^s
   ├─ Window Title: Gemini
   └─ Process: WindowsTerminal.exe
   ↓
Step 3: Look at hints
   ├─ See examples in placeholder
   └─ Click 📖 for more details
   ↓
Step 4: Copy example
   └─ SendText("/chat save")
   ↓
Step 5: Generate & Test
   ├─ Click 🚀 Generate AHK
   ├─ Run generated_shortcuts.ahk
   └─ Test in Gemini terminal
```

### Duplicating for Variations

```
Original Shortcut
   ↓
Right-click → Duplicate
   ↓
Edit Duplicate
   ├─ Change name
   ├─ Change window title
   └─ Modify action
   ↓
Generate Script
   ↓
Same hotkey, different contexts!
```

## Generated Script Structure

```ahk
#Requires AutoHotkey v2.0
#SingleInstance
Persistent

Paste(text) { ... }  ; Helper function

;! === BACKGROUND / STARTUP SCRIPTS ===
; Auto-execute section
SetTimer(MyFunc, 1000)

;! === SCRIPT SHORTCUTS ===
; Global hotkeys
!x::Run("pwsh", , "Hide")
#x::Run("gui.py", , "Hide")

;! === CONTEXT SHORTCUTS ===
; Window-specific hotkeys
IsGeminiSaveContext() {
    try {
        processName := WinGetProcessName("A")
        windowTitle := WinGetTitle("A")
        if (processName = "WindowsTerminal.exe" && InStr(windowTitle, "Gemini")) {
            return true
        }
    }
    return false
}

#HotIf IsGeminiSaveContext()
^s::{
    SendText("/chat save")
}
#HotIf

;! === TEXT SHORTCUTS ===
; Text expansion
:X:;v1::Paste('#Requires AutoHotkey v1.0')
:X:;v2::Paste('#Requires AutoHotkey v2.0')
```

## Feature Matrix

| Feature | Script | Text | Context | Startup |
|---------|--------|------|---------|---------|
| Hotkey | ✅ | ❌ | ✅ | ❌ |
| Trigger | ❌ | ✅ | ❌ | ❌ |
| Action Code | ✅ | ❌ | ✅ | ✅ |
| Replacement | ❌ | ✅ | ❌ | ❌ |
| Window Context | ❌ | ❌ | ✅ | ❌ |
| Auto-run | ❌ | ❌ | ❌ | ✅ |
| Code Hints | ✅ | ❌ | ✅ | ✅ |
| Duplicate | ✅ | ✅ | ✅ | ✅ |
| Enable/Disable | ✅ | ✅ | ✅ | ✅ |

## Icon Legend

- ✅ = Enabled
- ❌ = Disabled
- 📁 = Category
- 🚀 = Startup/Background
- 🔍 = Search
- ⌨ = Shortcut Builder
- 📖 = Command Reference
- 🎨 = Colors
- 🗂 = Category Toggle
- [▼] = Dropdown
- [_][□][X] = Window Controls

## Color Coding

```
Categories (customizable):
├─ System:     #FF6B6B (Red)
├─ Navigation: #4ECDC4 (Cyan)
├─ Text:       #45B7D1 (Blue)
├─ Media:      #96CEB4 (Green)
├─ AutoHotkey: #FFEAA7 (Yellow)
├─ General:    #DDA0DD (Purple)
├─ Terminal:   #FFA07A (Orange)
└─ Custom:     (Your choice)

Status:
├─ Enabled:    #27ae60 (Green) ✅
├─ Disabled:   #ff5555 (Red) ❌
└─ Selected:   #4a5b6e (Blue highlight)
```

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│ QUICK REFERENCE                         │
├─────────────────────────────────────────┤
│ Add Shortcut:     [+ Add] button        │
│ Edit:             Double-click          │
│ Duplicate:        Right-click → Dup     │
│ Remove:           Right-click → Remove  │
│ Toggle Enable:    Click ✅/❌           │
│ Search:           Type in search box    │
│ Category Toggle:  Click 🗂 icon         │
│ Generate Script:  [🚀 Generate AHK]     │
│ Command Help:     [📖] in dialog        │
│ Shortcut Builder: [⌨] in dialog        │
└─────────────────────────────────────────┘
```
