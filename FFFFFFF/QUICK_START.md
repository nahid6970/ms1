# Quick Start Guide

Get up and running with AutoHotkey GUI Manager in 5 minutes!

## Installation

1. **Install Python 3** (if not already installed)
2. **Install PyQt6:**
   ```bash
   pip install PyQt6
   ```
3. **Install AutoHotkey v2** from [autohotkey.com](https://www.autohotkey.com/)

## First Launch

```bash
python ahk_gui_pyqt.py
```

The GUI will open with your existing shortcuts (if any).

## Your First Shortcut

### Example 1: Simple Script Shortcut

**Goal:** Press `Win+N` to open Notepad

1. Click **[+ Add]** → **Script Shortcut**
2. Fill in:
   - Name: `Open Notepad`
   - Category: `System`
   - Hotkey: `#n` (click ⌨ for help)
   - Action: `Run("notepad.exe")`
3. Click **OK**
4. Click **[🚀 Generate AHK]**
5. Run `generated_shortcuts.ahk`
6. Press `Win+N` → Notepad opens!

### Example 2: Text Shortcut

**Goal:** Type `;email` to expand to your email

1. Click **[+ Add]** → **Text Shortcut**
2. Fill in:
   - Name: `My Email`
   - Category: `Text`
   - Trigger: `;email`
   - Replacement: `your.email@example.com`
3. Click **OK**
4. Click **[🚀 Generate AHK]**
5. Run `generated_shortcuts.ahk`
6. Type `;email` → Expands to your email!

### Example 3: Context Shortcut (NEW!)

**Goal:** Press `Ctrl+S` in Gemini terminal to save chat

1. Click **[+ Add]** → **Context Shortcut**
2. Fill in:
   - Name: `Gemini Save`
   - Category: `Terminal`
   - Hotkey: `^s`
   - Window Title: `Gemini`
   - Process Name: `WindowsTerminal.exe`
3. Look at the **hints** in the action field
4. Copy this example: `SendText("/chat save")`
5. Click **OK**
6. Click **[🚀 Generate AHK]**
7. Run `generated_shortcuts.ahk`
8. Open Gemini terminal, press `Ctrl+S` → Saves chat!

## Using Hints & Reference

### Action Code Hints

When you open the action field, you'll see helpful examples:

```
Examples:

; Send text (for terminal commands)
SendText("/chat save")

; Send keys
Send("^c")  ; Ctrl+C

; Run programs
Run("notepad.exe")
```

Just copy and modify!

### Command Reference

Click **[📖 Command Reference]** for detailed documentation:
- All AutoHotkey v2 commands
- Parameters and syntax
- Real examples
- Common patterns

## Common Tasks

### Duplicate a Shortcut

1. Click the shortcut to select it
2. Right-click → **Duplicate**
3. Edit the duplicate
4. Generate script

**Use case:** Create variations for different windows

### Disable Temporarily

1. Click the ✅ next to the shortcut
2. It changes to ❌
3. Generate script (disabled shortcuts won't be included)

### Search Shortcuts

Type in the search box to filter by:
- Name
- Hotkey
- Description
- Category
- Window title (for context shortcuts)

### Organize with Categories

1. Click **[🎨 Colors]**
2. Set colors for each category
3. Click **[🗂]** to toggle category grouping

## Tips for Beginners

### Start Simple

Don't try to create complex shortcuts right away:
1. Start with simple `Run()` commands
2. Add `Send()` for key presses
3. Combine multiple actions
4. Use context shortcuts for advanced scenarios

### Use the Hints

The placeholder hints show you exactly what to do:
- Copy the examples
- Modify for your needs
- Test incrementally

### Check the Reference

When in doubt, click **[📖 Command Reference]**:
- Find the command you need
- See the syntax
- Copy working examples

### Test Before Committing

1. Create a test shortcut
2. Generate and run the script
3. Test it thoroughly
4. If it works, keep it
5. If not, edit and try again

### Duplicate for Variations

Instead of creating from scratch:
1. Create one working shortcut
2. Duplicate it
3. Modify the duplicate
4. Much faster!

## Common Patterns

### Terminal Command

```ahk
SendText("your command here")
Send("{Enter}")
```

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

### Multiple Actions

```ahk
{
    MsgBox("Starting...")
    Run("notepad.exe")
    Sleep(1000)
    Send("Hello World")
}
```

## Troubleshooting

### Shortcut not working?

1. Check if enabled (✅)
2. Verify hotkey syntax
3. Look for conflicts
4. Check the generated script

### Context shortcut not activating?

1. Verify window title (case-insensitive)
2. Check process name (case-sensitive)
3. Try window title only first
4. Use Window Spy to find correct values

### Syntax error?

1. Check AutoHotkey v2 syntax (not v1!)
2. Use Command Reference
3. Test commands individually
4. Add comments to track what works

## Next Steps

### Explore Features

- Try all shortcut types
- Use the shortcut builder (⌨)
- Customize category colors
- Organize with categories

### Learn AutoHotkey

- Read the Command Reference
- Check official docs
- Join the forum
- Experiment!

### Create Your Workflow

1. Identify repetitive tasks
2. Create shortcuts for them
3. Organize by category
4. Refine over time

### Advanced Usage

- Background scripts for automation
- Complex context shortcuts
- Multi-step actions
- Window management

## Resources

### Documentation

- `CONTEXT_SHORTCUTS_GUIDE.md` - Context shortcuts
- `AHK_COMMAND_REFERENCE.md` - Command reference
- `WORKFLOW_EXAMPLE.md` - Detailed examples
- `SUMMARY.md` - Complete feature list

### External

- [AutoHotkey v2 Docs](https://www.autohotkey.com/docs/v2/)
- [Tutorial](https://www.autohotkey.com/docs/v2/Tutorial.htm)
- [Forum](https://www.autohotkey.com/boards/)

## Quick Reference

### Hotkey Syntax

- `^` = Ctrl
- `!` = Alt
- `+` = Shift
- `#` = Win
- `{Enter}` = Enter key
- `{Tab}` = Tab key

### Common Commands

```ahk
SendText("text")           ; Send literal text
Send("^c")                 ; Send Ctrl+C
Run("program.exe")         ; Run program
MsgBox("message")          ; Show message
Sleep(1000)                ; Wait 1 second
WinActivate("Title")       ; Activate window
```

### GUI Shortcuts

- **Add:** Click [+ Add]
- **Edit:** Double-click shortcut
- **Duplicate:** Right-click → Duplicate
- **Remove:** Right-click → Remove
- **Toggle:** Click ✅/❌
- **Search:** Type in search box
- **Generate:** Click [🚀 Generate AHK]

## Support

If you need help:
1. Check the documentation files
2. Click [📖 Command Reference] in the GUI
3. Look at the placeholder hints
4. Check the AutoHotkey forum

## Happy Automating! 🚀
