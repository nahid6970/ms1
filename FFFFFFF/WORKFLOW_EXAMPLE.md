# Complete Workflow Example

## Scenario: Adding Gemini Terminal Shortcuts

Let's walk through adding the shortcuts from your `gemini.ahk` file using the new GUI feature.

## Step 1: Open the GUI

```bash
python ahk_gui_pyqt.py
```

## Step 2: Add First Context Shortcut (Save Chat)

1. Click **"+ Add"** button
2. Select **"Context Shortcut"**
3. Fill in the dialog:

```
┌─────────────────────────────────────────────┐
│ Add Context Shortcut                        │
├─────────────────────────────────────────────┤
│ Name: Gemini Save Chat                      │
│ Category: Terminal                          │
│ Description: Save current Gemini chat       │
│ Enabled: [✓]                                │
│                                             │
│ Hotkey: ^s                          [⌨]    │
│                                             │
│ Window Title: Gemini                        │
│ Process Name: WindowsTerminal.exe           │
│ Window Class: (leave empty)                 │
│                                             │
│ Action Code:                                │
│ ┌─────────────────────────────────────────┐ │
│ │ SendText("/chat save")                  │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│              [OK]  [Cancel]                 │
└─────────────────────────────────────────────┘
```

4. Click **OK**

## Step 3: Add Second Context Shortcut (Resume Chat)

1. Click **"+ Add"** → **"Context Shortcut"** again
2. Fill in:

```
Name: Gemini Resume Chat
Category: Terminal
Description: Resume previous Gemini chat
Enabled: [✓]

Hotkey: ^r                          [⌨]

Window Title: Gemini
Process Name: WindowsTerminal.exe
Window Class: (leave empty)

Action Code:
┌─────────────────────────────────────────┐
│ SendText("/chat resume")                │
└─────────────────────────────────────────┘
```

3. Click **OK**

## Step 4: View Your Shortcuts

The GUI now shows:

```
┌─────────────────────────────────────────────────────────────┐
│  Script Shortcuts  │  Context Shortcuts  │  Text Shortcuts  │
├────────────────────┼─────────────────────┼──────────────────┤
│                    │ 📁 Terminal         │                  │
│  ✅ !x → Terminal  │  ✅ ^s [Gemini]     │  ✅ ;v1 → AHK v1 │
│  ✅ #x → GUI       │     → Save Chat     │  ✅ ;v2 → AHK v2 │
│  ...               │  ✅ ^r [Gemini]     │  ...             │
│                    │     → Resume Chat   │                  │
└────────────────────┴─────────────────────┴──────────────────┘
```

## Step 5: Generate AHK Script

1. Click **"🚀 Generate AHK"** button
2. Success message appears: "🚀 Success: AHK script generated as 'generated_shortcuts.ahk'"

## Step 6: Check Generated Code

Open `generated_shortcuts.ahk` and you'll see:

```ahk
#Requires AutoHotkey v2.0
#SingleInstance
Persistent

;! === CONTEXT SHORTCUTS ===
;! Gemini Save Chat
;! Save current Gemini chat
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

;! Gemini Resume Chat
;! Resume previous Gemini chat
IsGeminiResumeChatContext() {
    try {
        processName := WinGetProcessName("A")
        windowTitle := WinGetTitle("A")
        if (processName = "WindowsTerminal.exe" && InStr(windowTitle, "Gemini")) {
            return true
        }
    }
    return false
}

#HotIf IsGeminiResumeChatContext()

^r::{
    SendText("/chat resume")
}

#HotIf
```

## Step 7: Run the Script

```bash
# Run the generated script
generated_shortcuts.ahk
```

Or double-click `generated_shortcuts.ahk` in File Explorer.

## Step 8: Test It!

1. Open Windows Terminal
2. Start a Gemini session (window title contains "Gemini")
3. Press **Ctrl+S** → Sends "/chat save"
4. Press **Ctrl+R** → Sends "/chat resume"
5. Switch to another window → Ctrl+S and Ctrl+R do nothing (or their default action)

## Editing Shortcuts

### To Edit:
1. Double-click the shortcut in the GUI
2. Or: Click once to select, then right-click → Edit
3. Modify fields
4. Click OK
5. Regenerate the AHK script

### To Duplicate:
1. Click the shortcut to select it
2. Right-click → Duplicate
3. A copy is created with "(Copy)" in the name
4. Hotkey/trigger is cleared to avoid conflicts
5. Edit the duplicate to customize it
6. Regenerate the script

**Example Use Case:**
You have a Gemini shortcut for Windows Terminal. Duplicate it to create a similar shortcut for PowerShell:
```
Original: ^s [Gemini] → Save Chat
Duplicate: ^s [PowerShell] → Save History
```

### To Disable Temporarily:
1. Click the ✅ icon next to the shortcut
2. It changes to ❌
3. Regenerate the script (disabled shortcuts won't be included)

### To Remove:
1. Click the shortcut to select it
2. Right-click → Remove
3. Confirm deletion
4. Regenerate the script

## Advanced: Multiple Contexts

You can create different shortcuts for different contexts:

```
Context Shortcuts:
├─ 📁 Terminal
│  ├─ ^s [Gemini] → Save Chat
│  ├─ ^r [Gemini] → Resume Chat
│  ├─ ^s [PowerShell] → Save History
│  └─ ^r [PowerShell] → Reload Profile
├─ 📁 Browser
│  ├─ ^s [Chrome] → Save Page
│  └─ ^s [Firefox] → Save Page
└─ 📁 Editor
   ├─ ^s [VS Code] → Save All
   └─ ^s [Notepad++] → Save Session
```

Same hotkey (Ctrl+S), different actions based on context!

## Tips

- **Window Title:** Use partial matches (e.g., "Gemini" matches "Gemini - Windows Terminal")
- **Process Name:** Get exact name from Task Manager → Details tab
- **Window Class:** Use Window Spy (comes with AutoHotkey) to find class names
- **Testing:** Test in the actual window before committing
- **Organization:** Use categories to group related context shortcuts
- **Search:** Use the search box to filter shortcuts by name, hotkey, or window title

## Troubleshooting

**Shortcut not working?**
- Check if window title matches (case-insensitive)
- Verify process name is exact (case-sensitive)
- Try removing process name and using only window title
- Check if shortcut is enabled (✅)

**Wrong window activating?**
- Add more specific window title
- Add process name for precision
- Use window class for system windows

**Conflicts with other shortcuts?**
- Context shortcuts take priority in their context
- Global shortcuts work everywhere else
- Check for duplicate hotkeys in same context
