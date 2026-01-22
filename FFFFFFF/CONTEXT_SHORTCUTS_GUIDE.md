# Context Shortcuts Guide

## What are Context Shortcuts?

Context shortcuts are window-specific hotkeys that only work when certain conditions are met (specific window title, process, or window class). This is similar to how `gemini.ahk` works.

## How to Create Context Shortcuts

**Using the GUI:**
1. Click "+ Add" button
2. Select "Context Shortcut"
3. Fill in the fields:
   - **Name:** Descriptive name for the shortcut
   - **Category:** Organize your shortcuts
   - **Description:** Optional description
   - **Hotkey:** The key combination (e.g., ^s, ^r)
   - **Window Title:** Text that must appear in the window title
   - **Process Name:** (Optional) Specific process name (e.g., WindowsTerminal.exe)
   - **Window Class:** (Optional) Window class name (e.g., CabinetWClass)
   - **Action Code:** The AutoHotkey code to execute

**At least one context field (Window Title, Process Name, or Window Class) is required.**

## Example: Gemini Terminal Shortcuts

**Save Chat Shortcut:**
- Name: Gemini Save Chat
- Hotkey: ^s
- Window Title: Gemini
- Process Name: WindowsTerminal.exe
- Action: `SendText("/chat save")`

**Resume Chat Shortcut:**
- Name: Gemini Resume Chat
- Hotkey: ^r
- Window Title: Gemini
- Process Name: WindowsTerminal.exe
- Action: `SendText("/chat resume")`

## How It Works

When you generate the AHK script, context shortcuts create:

1. **Context Check Function:** Verifies if the active window matches your criteria
2. **#HotIf Directive:** Activates the hotkey only when the context matches
3. **Hotkey Definition:** The actual shortcut action

**Generated Code Example:**
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

## Use Cases

**Browser-Specific Shortcuts:**
- Window Title: "Chrome"
- Process Name: chrome.exe

**Editor-Specific Shortcuts:**
- Window Title: "Visual Studio Code"
- Process Name: Code.exe

**File Explorer Shortcuts:**
- Window Class: CabinetWClass

**Terminal Shortcuts:**
- Process Name: WindowsTerminal.exe
- Window Title: (specific terminal tab name)

## Tips

- Use **Window Title** for general matching (most flexible)
- Add **Process Name** for more precise targeting
- Use **Window Class** for system windows (use Window Spy to find class names)
- Combine multiple conditions for maximum specificity
- Test your shortcuts after generating the AHK script

## Display in GUI

Context shortcuts appear in the middle column labeled "Context Shortcuts". They show:
- The hotkey
- The window title (truncated if long) in brackets
- The shortcut name
- Enable/disable toggle (✅/❌)

## Benefits

- **No Conflicts:** Same hotkey can do different things in different windows
- **Context-Aware:** Shortcuts only work where they make sense
- **Organized:** Keep window-specific shortcuts separate from global ones
- **Flexible:** Mix and match window title, process, and class conditions
