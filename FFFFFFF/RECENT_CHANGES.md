# Recent Changes

## 2025-01-22

### ✅ Added Duplicate Shortcut Feature
**New Feature:** Right-click context menu now includes "Duplicate" option to quickly copy shortcuts.

**How It Works:**
- Right-click any shortcut → Select "Duplicate"
- Creates a copy with "(Copy)" appended to the name
- Clears hotkey/trigger to avoid conflicts
- Automatically selects the duplicate for easy editing
- Shows success message with instructions

**Use Cases:**
- Create variations of existing shortcuts
- Quickly set up similar shortcuts for different contexts
- Template shortcuts for common patterns

**Files Modified:**
- `ahk_gui_pyqt.py` - Added duplicate_selected() method and context menu item

### ✅ Fixed Script Execution Working Directory Issue
**Problem:** The `^!+Enter` shortcut was running scripts from a fixed directory (`C:\@delta\ms1\`) instead of the script's actual location, causing logs and output files to be created in the wrong place.

**Solution:** Modified the shortcut to extract the directory from the script file path using `SplitPath()` and pass it as the working directory parameter to `Run()`.

**Files Modified:**
- `ahk_shortcuts.json` - Updated Execute Script W/O Closing shortcut
- `generated_shortcuts.ahk` - Updated generated script

### ✅ Added Context-Aware Shortcuts Feature
**New Feature:** Added support for window-specific shortcuts that only work in certain contexts (specific window title, process name, or window class).

**How It Works:**
- New shortcut type: "Context Shortcuts"
- Shortcuts can be configured to only activate when:
  - Window title contains specific text
  - Process name matches
  - Window class matches
- Generates `#HotIf` directives in AutoHotkey script
- Similar to how `gemini.ahk` works

**Example Use Cases:**
- Terminal-specific shortcuts (Ctrl+S to save chat in Gemini terminal)
- Browser-specific shortcuts
- Editor-specific shortcuts
- File Explorer shortcuts

**Files Modified:**
- `ahk_gui_pyqt.py` - Added context shortcut support throughout
  - New dialog fields for window title, process name, window class
  - Context shortcuts display in middle column
  - Generate #HotIf directives with context check functions
- `ahk_shortcuts.json` - Added context_shortcuts array with Gemini examples
- `CONTEXT_SHORTCUTS_GUIDE.md` - Complete documentation for the feature

**GUI Changes:**
- Added "Context Shortcut" option to Add menu
- New column in display for context shortcuts
- Shows hotkey with window title in brackets
- Edit/remove support for context shortcuts

**Generated AHK Script:**
Context shortcuts generate:
1. Context check function (e.g., `IsGeminiSaveChatContext()`)
2. `#HotIf` directive to activate context
3. Hotkey definition
4. `#HotIf` to deactivate context

**Example Generated Code:**
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

**Benefits:**
- No hotkey conflicts between different contexts
- Same hotkey can do different things in different windows
- Better organization of window-specific shortcuts
- Flexible context matching (title, process, class)
