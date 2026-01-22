# AutoHotkey GUI Manager - Feature Summary

Complete overview of all features and recent additions.

## Core Features

### Shortcut Types

1. **Script Shortcuts** - Global hotkeys that work everywhere
2. **Text Shortcuts** - Text expansion/replacement
3. **Context Shortcuts** - Window-specific hotkeys (NEW!)
4. **Background Scripts** - Auto-run scripts on startup

### GUI Features

- **Visual Organization** - Three-column layout with categories
- **Search** - Filter shortcuts by name, hotkey, description, category
- **Category Grouping** - Toggle to group by category or flat list
- **Enable/Disable** - Click ✅/❌ to toggle shortcuts
- **Color Coding** - Customizable category colors
- **Selection** - Click to select, double-click to edit
- **Context Menu** - Right-click for Edit/Duplicate/Remove

### Editing Features

- **Add/Edit Dialog** - Full-featured dialog for all shortcut types
- **Shortcut Builder** - Visual hotkey builder (⌨ button)
- **Action Hints** - Placeholder examples in action fields (NEW!)
- **Command Reference** - Built-in AutoHotkey command guide (NEW!)
- **Duplicate** - Copy shortcuts with one click (NEW!)

## Recent Additions (2025-01-22)

### 1. Context-Aware Shortcuts ✅

**What:** Window-specific hotkeys that only work in certain contexts

**Features:**
- Match by window title, process name, or window class
- Same hotkey can do different things in different windows
- Generates `#HotIf` directives automatically
- Visual display shows context info

**Example:**
```
^s [Gemini] → Save chat
^s [PowerShell] → Save history
^s [Chrome] → Save page
```

**Use Cases:**
- Terminal-specific commands
- Browser automation
- Editor shortcuts
- File Explorer actions

### 2. Duplicate Shortcuts ✅

**What:** Copy any shortcut with one right-click

**Features:**
- Creates exact copy with "(Copy)" in name
- Clears hotkey/trigger to avoid conflicts
- Automatically selects duplicate for editing
- Works with all shortcut types

**Workflow:**
1. Select shortcut
2. Right-click → Duplicate
3. Edit the duplicate
4. Done!

**Use Cases:**
- Create variations for different contexts
- Use shortcuts as templates
- Test modifications safely
- Quick setup of similar shortcuts

### 3. Action Code Hints ✅

**What:** Helpful placeholder examples in action code fields

**Features:**
- Context-aware hints (different for each shortcut type)
- Common commands with comments
- Real working examples
- Copy-paste ready

**Context Shortcut Hints:**
```ahk
; Send text (for terminal commands)
SendText("/chat save")

; Send keys
Send("^c")  ; Ctrl+C

; Run programs
Run("notepad.exe")

; Multiple actions
SendText("cd Documents")
Send("{Enter}")
```

**Script Shortcut Hints:**
```ahk
; Simple action
Run("notepad.exe")

; Multiple lines
{
    MsgBox("Starting...")
    Run("notepad.exe")
}
```

### 4. Command Reference ✅

**What:** Comprehensive AutoHotkey v2 command guide

**Access:** Click 📖 Command Reference button in any action field

**Includes:**
- Sending text & keys (SendText, Send, SendInput)
- Running programs (Run, RunWait)
- Window operations (WinActivate, WinClose, WinMaximize)
- Clipboard operations (read, write, backup/restore)
- Messages & dialogs (MsgBox, ToolTip, InputBox)
- Timing & delays (Sleep, SetTimer)
- Variables & strings (concatenation, replace, split)
- Control flow (if/else, loop, while)
- File operations (FileRead, FileAppend, FileDelete)
- Mouse operations (Click, MouseMove, MouseGetPos)
- System information (A_ScriptDir, A_UserName, A_Now)
- Common patterns (copy/modify/paste, run and activate)
- Context shortcut examples

### 5. Script Working Directory Fix ✅

**What:** Scripts now run from their own directories

**Problem:** All scripts were running from `C:\@delta\ms1\`

**Solution:** Extract directory from file path and use as working directory

**Impact:** Logs and output files now created in correct location

## Workflow Examples

### Creating Context Shortcuts

1. Click "+ Add" → "Context Shortcut"
2. Fill in:
   - Name: "Gemini Save"
   - Hotkey: ^s
   - Window Title: Gemini
   - Process: WindowsTerminal.exe
3. Look at hints in action field
4. Copy example: `SendText("/chat save")`
5. Click OK
6. Generate AHK script
7. Test in Gemini terminal

### Duplicating for Variations

1. Create first shortcut (e.g., Gemini save)
2. Select it
3. Right-click → Duplicate
4. Edit duplicate:
   - Change name to "PowerShell Save"
   - Change window title to "PowerShell"
   - Change action to `SendText("history > history.txt")`
5. Repeat for other terminals
6. Generate script
7. Same hotkey works differently in each terminal!

### Using Command Reference

1. Open Add/Edit dialog
2. Click 📖 Command Reference
3. Browse to relevant section
4. Find command you need
5. Copy example code
6. Paste into action field
7. Modify for your needs
8. Test it

## File Structure

```
.
├── ahk_gui_pyqt.py              # Main GUI application
├── ahk_shortcuts.json           # Shortcuts database
├── generated_shortcuts.ahk      # Generated AutoHotkey script
├── gemini.ahk                   # Example context shortcut
│
├── Documentation/
│   ├── README.md                # Main documentation
│   ├── CONTEXT_SHORTCUTS_GUIDE.md
│   ├── CONTEXT_MENU_GUIDE.md
│   ├── DUPLICATE_FEATURE_SUMMARY.md
│   ├── HINTS_FEATURE.md
│   ├── AHK_COMMAND_REFERENCE.md
│   ├── WORKFLOW_EXAMPLE.md
│   ├── FEATURE_SUMMARY.md
│   ├── RECENT_CHANGES.md
│   └── SUMMARY.md (this file)
```

## Quick Start

1. **Run GUI:** `python ahk_gui_pyqt.py`
2. **Add Shortcuts:** Click "+ Add" and choose type
3. **Use Hints:** Look at placeholder examples
4. **Check Reference:** Click 📖 for detailed docs
5. **Generate Script:** Click "🚀 Generate AHK"
6. **Run Script:** Double-click `generated_shortcuts.ahk`

## Tips & Best Practices

### General
- Use categories to organize shortcuts
- Enable/disable instead of deleting (for testing)
- Use search to find shortcuts quickly
- Group by category for better organization

### Context Shortcuts
- Start with window title only (most flexible)
- Add process name for precision
- Use window class for system windows
- Test in actual window before committing

### Duplicating
- Duplicate before experimenting
- Use meaningful names (not just "Copy")
- Check for hotkey conflicts
- Organize duplicates with categories

### Action Code
- Start with hints/examples
- Use Command Reference for details
- Test incrementally (one command at a time)
- Add comments for complex code
- Use SendText() for literal text
- Use Send() for key combinations

### Workflow
- Create template shortcuts
- Duplicate for variations
- Test before generating
- Keep backups of working shortcuts

## Keyboard Shortcuts

- **Select:** Click once
- **Edit:** Double-click
- **Context Menu:** Right-click
- **Search:** Type in search box
- **Toggle Enable:** Click ✅/❌

## Common Issues & Solutions

### Shortcut not working?
- Check if enabled (✅)
- Verify hotkey syntax
- Test in correct window (for context shortcuts)
- Check for conflicts with other shortcuts

### Context shortcut not activating?
- Verify window title matches (case-insensitive)
- Check process name is exact (case-sensitive)
- Try window title only first
- Use Window Spy to find correct values

### Action code not working?
- Check AutoHotkey v2 syntax (not v1!)
- Add Sleep() between actions
- Test commands individually
- Check Command Reference for correct usage

### Duplicate has conflicts?
- Edit hotkey/trigger immediately
- Check for existing shortcuts with same key
- Use different context for same hotkey

## Future Enhancements

Potential features:
- Syntax highlighting in action fields
- Auto-completion for commands
- Inline documentation tooltips
- Code snippets library
- Import/export shortcuts
- Backup/restore functionality
- Undo/redo support
- Keyboard shortcuts for GUI
- Batch operations (enable/disable multiple)
- Shortcut testing without generating

## Resources

- [AutoHotkey v2 Documentation](https://www.autohotkey.com/docs/v2/)
- [Command List](https://www.autohotkey.com/docs/v2/lib/)
- [Tutorial](https://www.autohotkey.com/docs/v2/Tutorial.htm)
- [Forum](https://www.autohotkey.com/boards/)

## Credits

Built with:
- Python 3
- PyQt6
- AutoHotkey v2

## Version History

- **v2.0** (2025-01-22) - Context shortcuts, duplicate, hints, command reference
- **v1.0** - Initial release with script/text/startup shortcuts
