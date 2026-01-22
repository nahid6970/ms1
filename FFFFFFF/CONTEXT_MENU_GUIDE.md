# Context Menu Guide

## Right-Click Actions

When you right-click on any shortcut in the GUI, you get these options:

```
┌─────────────────┐
│ Edit            │
│ Duplicate       │
├─────────────────┤
│ Remove          │
└─────────────────┘
```

## Edit

**What it does:** Opens the edit dialog for the selected shortcut

**How to use:**
1. Click a shortcut to select it
2. Right-click → Edit
3. Modify any fields
4. Click OK

**Alternative:** Double-click the shortcut

**Use when:**
- Changing hotkey/trigger
- Updating action code
- Modifying description
- Changing category
- Adjusting context conditions

## Duplicate

**What it does:** Creates a copy of the selected shortcut

**How it works:**
1. Click a shortcut to select it
2. Right-click → Duplicate
3. A copy is created with:
   - Name: `Original Name (Copy)`
   - Hotkey/Trigger: Cleared (to avoid conflicts)
   - All other fields: Copied exactly
4. The duplicate is automatically selected
5. Success message appears with instructions

**Use when:**
- Creating variations of existing shortcuts
- Setting up similar shortcuts for different contexts
- Using a shortcut as a template
- Testing modifications without losing the original

## Remove

**What it does:** Deletes the selected shortcut permanently

**How it works:**
1. Click a shortcut to select it
2. Right-click → Remove
3. Confirmation dialog appears
4. Click Yes to confirm deletion
5. Shortcut is removed from the list

**Warning:** This action cannot be undone (unless you have a backup of `ahk_shortcuts.json`)

**Use when:**
- Removing obsolete shortcuts
- Cleaning up duplicates
- Deleting test shortcuts

## Common Workflows

### Creating Variations

**Scenario:** You have a Gemini terminal shortcut and want similar ones for PowerShell and CMD.

1. Select the Gemini shortcut
2. Right-click → Duplicate
3. Edit the duplicate:
   - Change name to "PowerShell Save"
   - Change window title to "PowerShell"
   - Set hotkey to `^s`
4. Duplicate again for CMD
5. Edit that duplicate:
   - Change name to "CMD Save"
   - Change window title to "Command Prompt"
   - Set hotkey to `^s`

Result: Same hotkey (Ctrl+S) does different things in different terminals!

### Template Shortcuts

**Scenario:** You frequently create shortcuts with similar structure.

1. Create a "template" shortcut with common settings:
   - Category: "Templates"
   - Description: "Template for X type shortcuts"
   - Action: Basic structure/boilerplate code
2. When you need a new similar shortcut:
   - Select the template
   - Right-click → Duplicate
   - Edit the duplicate with specific details
   - Change category from "Templates" to actual category

### Testing Changes

**Scenario:** You want to test a modification without losing the working version.

1. Select the working shortcut
2. Right-click → Duplicate
3. Edit the duplicate with your test changes
4. Disable the original (click ✅ to make it ❌)
5. Generate and test the script
6. If it works: Remove the original
7. If it doesn't: Remove the duplicate, re-enable the original

### Quick Context Variations

**Scenario:** Same action, different windows.

1. Create one context shortcut (e.g., for Chrome)
2. Duplicate it
3. Edit duplicate: Change only the window title/process
4. Repeat for each window type

Example:
```
^s [Chrome] → Save Page
^s [Firefox] → Save Page  (duplicated from Chrome)
^s [Edge] → Save Page     (duplicated from Chrome)
```

## Keyboard Shortcuts

While the GUI doesn't have keyboard shortcuts for the context menu yet, you can:

- **Select:** Click once
- **Edit:** Double-click
- **Context Menu:** Right-click

## Tips

- **Duplicate before editing:** If you're unsure about changes, duplicate first
- **Use descriptive names:** When duplicating, give meaningful names
- **Clear conflicts:** Duplicate clears hotkeys/triggers to prevent conflicts
- **Organize with categories:** Use categories to group related duplicates
- **Test incrementally:** Duplicate, modify one thing, test, repeat

## Limitations

- Cannot duplicate multiple shortcuts at once (select and duplicate one at a time)
- Cannot undo duplication (but you can remove the duplicate)
- Duplicate doesn't automatically open edit dialog (you need to edit manually)

## Future Enhancements

Potential future features:
- Duplicate multiple shortcuts
- Duplicate with automatic edit dialog
- Duplicate to different category
- Duplicate with find/replace in action code
- Undo/redo support
