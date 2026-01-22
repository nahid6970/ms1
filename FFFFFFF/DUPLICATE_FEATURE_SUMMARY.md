# Duplicate Feature Summary

## What's New

Added a **Duplicate** option to the right-click context menu for quickly copying shortcuts.

## Visual Guide

### Before
```
Right-click menu:
┌─────────────┐
│ Edit        │
│ Remove      │
└─────────────┘
```

### After
```
Right-click menu:
┌─────────────┐
│ Edit        │
│ Duplicate   │ ← NEW!
├─────────────┤
│ Remove      │
└─────────────┘
```

## How It Works

### Step 1: Select a Shortcut
```
Context Shortcuts:
  ✅ ^s [Gemini] → Save Chat  ← Click to select
  ✅ ^r [Gemini] → Resume Chat
```

### Step 2: Right-Click → Duplicate
```
┌─────────────────────────────┐
│ Edit                        │
│ Duplicate      ← Click this │
├─────────────────────────────┤
│ Remove                      │
└─────────────────────────────┘
```

### Step 3: Duplicate Created
```
Context Shortcuts:
  ✅ ^s [Gemini] → Save Chat
  ✅ ^r [Gemini] → Resume Chat
  ✅    [Gemini] → Save Chat (Copy)  ← New duplicate!
                   ↑ Hotkey cleared to avoid conflict
```

### Step 4: Success Message
```
┌────────────────────────────────────────────┐
│ Success                                    │
├────────────────────────────────────────────┤
│ Duplicated 'Save Chat' as                 │
│ 'Save Chat (Copy)'.                        │
│                                            │
│ Please edit the duplicate to set a        │
│ unique hotkey/trigger.                     │
│                                            │
│                    [OK]                    │
└────────────────────────────────────────────┘
```

### Step 5: Edit the Duplicate
Double-click or right-click → Edit to customize:
```
Name: PowerShell Save  ← Changed from "Save Chat (Copy)"
Hotkey: ^s             ← Set the hotkey
Window Title: PowerShell  ← Changed from "Gemini"
```

## What Gets Copied

### Copied Exactly:
- ✅ Name (with "(Copy)" appended)
- ✅ Category
- ✅ Description
- ✅ Action/Replacement code
- ✅ Enabled status
- ✅ Context conditions (window title, process, class)

### Cleared to Avoid Conflicts:
- ❌ Hotkey (for script/context shortcuts)
- ❌ Trigger (for text shortcuts)

## Use Cases

### 1. Context Variations
Create similar shortcuts for different windows:
```
Original:  ^s [Gemini] → Save Chat
Duplicate: ^s [PowerShell] → Save History
Duplicate: ^s [CMD] → Save Session
```

### 2. Template Shortcuts
Use one shortcut as a template:
```
Template: [Template] → Common boilerplate code
Duplicate → Customize for specific use
Duplicate → Customize for another use
```

### 3. Testing Changes
Test modifications without losing the original:
```
Original: ^s → Working version
Duplicate: ^s → Test version (disable original)
If works: Remove original
If fails: Remove duplicate
```

### 4. Quick Variations
Create slight variations quickly:
```
Original: ;v1 → #Requires AutoHotkey v1.0
Duplicate: ;v2 → #Requires AutoHotkey v2.0
```

## Workflow Example

**Goal:** Create Ctrl+S shortcuts for 3 different terminals

1. **Create the first one:**
   - Add Context Shortcut
   - Name: "Gemini Save"
   - Hotkey: ^s
   - Window Title: Gemini
   - Action: `SendText("/chat save")`

2. **Duplicate for PowerShell:**
   - Select "Gemini Save"
   - Right-click → Duplicate
   - Edit duplicate:
     - Name: "PowerShell Save"
     - Hotkey: ^s
     - Window Title: PowerShell
     - Action: `SendText("history > history.txt")`

3. **Duplicate for CMD:**
   - Select "PowerShell Save"
   - Right-click → Duplicate
   - Edit duplicate:
     - Name: "CMD Save"
     - Hotkey: ^s
     - Window Title: Command Prompt
     - Action: `SendText("doskey /history > history.txt")`

**Result:** Same hotkey (Ctrl+S) does different things in each terminal!

## Benefits

⚡ **Fast:** Create variations in seconds
🎯 **Accurate:** No typos from manual recreation
🔄 **Flexible:** Duplicate any shortcut type
🛡️ **Safe:** Original remains unchanged
📝 **Smart:** Clears conflicts automatically

## Tips

- **Duplicate before experimenting:** Keep the working version safe
- **Use meaningful names:** Change "(Copy)" to something descriptive
- **Check for conflicts:** Make sure hotkeys/triggers are unique
- **Organize with categories:** Group related duplicates together
- **Test incrementally:** Duplicate, change one thing, test

## Technical Details

**Implementation:**
- Uses Python's `copy.deepcopy()` for complete copy
- Automatically appends "(Copy)" to name
- Clears hotkey/trigger fields
- Adds to appropriate list (script/text/context/startup)
- Saves to JSON automatically
- Selects the duplicate for easy editing

**Files Modified:**
- `ahk_gui_pyqt.py` - Added `duplicate_selected()` method

## Future Enhancements

Potential improvements:
- Duplicate multiple shortcuts at once
- Auto-open edit dialog after duplicate
- Find/replace in duplicated code
- Duplicate across categories
- Undo/redo support
