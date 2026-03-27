# AutoHotkey (AHK) GUI Manager - Consolidated Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Quick Start Guide](#quick-start-guide)
3. [AHK v2 Command Reference](#ahk-v2-command-reference)
4. [Context Shortcuts Guide](#context-shortcuts-guide)
5. [Context Menu Guide](#context-menu-guide)
6. [Feature Summary](#feature-summary)
7. [Visual Feature Overview](#visual-feature-overview)
8. [Action Code Hints Feature](#action-code-hints-feature)
9. [Duplicate Feature Summary](#duplicate-feature-summary)
10. [Context-Aware Shortcuts Feature Summary](#context-aware-shortcuts-feature-summary)
11. [Workflow Example](#workflow-example)
12. [Recent Changes](#recent-changes)

---

<a name="introduction"></a>
# Introduction (Original README)

A powerful PyQt6 application for visually managing, searching, and generating AutoHotkey v2 scripts. This tool eliminates the need for manual script editing and provides a "Shortcut Builder" to avoid system-level hotkey conflicts during setup.

## 🚀 Key Features

- **Visual Shortcut Builder (⌨)**: Construct complex hotkeys (like `Ctrl+Alt+T`) by clicking modifier buttons and searching for keys. No more system-level shortcuts triggering while you try to assign them!
- **Searchable Interface**: Instantly find shortcuts by name, key, description, or category.
- **Category Organization**: Group shortcuts into categories (System, Navigation, Media, etc.) with custom color coding.
- **Two Shortcut Types**:
    - **Script Shortcuts**: Runs AutoHotkey v2 code when a hotkey is pressed.
    - **Background Scripts**: Code that runs automatically as soon as the script starts (perfect for timers, setup, or persistent background tasks). No hotkey required.
    - **Text Shortcuts (Hotstrings)**: Replaces a typed trigger (e.g., `;v2`) with replacement text. **Automatically handles special characters (#, !, etc.) and multiline text literally.**

---

## 🛠 How to Add New Scripts

To add a new script to the GUI, follow these steps:

1. **Launch the App**: Run `ahk_gui_pyqt.py`.
2. **Add Shortcut**: Click the **+ Add** button and select **Script Shortcut**.
3. **Set Hotkey**: Use the keyboard icon (**⌨**) next to the Hotkey field to open the **Shortcut Builder**. Click Ctrl/Alt/Shift and select your main key.
4. **Input Action**: Paste your AHK v2 code into the **Action** text box.

### Important: Multi-line Logic
- If your script is a **single line** (e.g., `Run "notepad.exe"`), the GUI will generate it as `Hotkey::Action`.
- If your script has **multiple lines**, the GUI **automatically wraps** it in `{ }` braces. You don't need to add them yourself unless you are defining internal functions or blocks.

### 💡 Best Practice: Use Functions for Everything
For the best experience when sharing code with AI (like me!) or writing your own, **always wrap your logic inside a function**.

**Why?**
1. It avoids "variable name conflicts" between different shortcuts.
2. It makes the code much cleaner when pasted into the GUI.
3. It ensures that variables defined inside the function don't accidentally "leak" into other parts of your AHK script.

**The "Clean Format" to use:**
```autohotkey
; Give your function a unique name
MyAwesomeAction() {
    ; All your script logic goes here
    MsgBox("Action complete!")
}

; Then just call it inside the Hotkey in the GUI:
MyAwesomeAction()
```

---

## 📝 AHK v2 Script Examples

Here are some common snippets you can copy and paste into the **Action** box:

### Open a Website
```autohotkey
Run "https://www.google.com"
```

### Launch an App (with specific working directory)
```autohotkey
Run "C:\Path\To\YourApp.exe", "C:\Path\To\"
```

### Type Custom Text (using Send)
```autohotkey
Send "Best regards,{Enter}Nahid Ahmed"
```

### Move/Resize Window
```autohotkey
WinMove(0, 0, 800, 600, "A") ; Moves the Active window to top-left and resizes
```

### Toggle Volume
```autohotkey
Send "{Volume_Mute}"
```

### Multi-line Power Script
```autohotkey
if WinExist("ahk_class Notepad")
    WinActivate
else
    Run "notepad.exe"
```

---

## 📂 Project Structure

- `ahk_gui_pyqt.py`: The main Python application logic and UI.
- `ahk_shortcuts.json`: Your database of saved shortcuts (automatically managed).
- `generated_shortcuts.ahk`: The output file you run with AutoHotkey v2.

## ⚠️ Requirements

- **Python 3.10+**
- **PyQt6**: `pip install PyQt6`
- **AutoHotkey v2**: Required to run the generated `.ahk` file.

---

<a name="quick-start-guide"></a>
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

- [Introduction](#introduction)
- [Quick Start Guide](#quick-start-guide)
- [AHK v2 Command Reference](#ahk-v2-command-reference)
- [Context Shortcuts Guide](#context-shortcuts-guide)
- [Context Menu Guide](#context-menu-guide)
- [Feature Summary](#feature-summary)
- [Visual Feature Overview](#visual-feature-overview)
- [Action Code Hints Feature](#action-code-hints-feature)
- [Duplicate Feature Summary](#duplicate-feature-summary)
- [Context-Aware Shortcuts Feature Summary](#context-aware-shortcuts-feature-summary)
- [Workflow Example](#workflow-example)
- [Recent Changes](#recent-changes)

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

---

<a name="ahk-v2-command-reference"></a>
# AutoHotkey v2 Command Reference

Quick reference for common AutoHotkey v2 commands to use in your shortcuts.

## Sending Text & Keys

### SendText()
Sends text literally (no special key interpretation)
```ahk
SendText("Hello World")
SendText("/chat save")
SendText("cd Documents")
```

### Send()
Sends keys with special key support
```ahk
Send("^c")           ; Ctrl+C
Send("^v")           ; Ctrl+V
Send("!{F4}")        ; Alt+F4
Send("{Enter}")      ; Enter key
Send("{Tab}")        ; Tab key
Send("^+{Esc}")      ; Ctrl+Shift+Esc
Send("{Up 5}")       ; Up arrow 5 times
```

**Common Special Keys:**
- `^` = Ctrl
- `!` = Alt
- `+` = Shift
- `#` = Win
- `{Enter}` = Enter
- `{Tab}` = Tab
- `{Esc}` = Escape
- `{Space}` = Space
- `{Up}`, `{Down}`, `{Left}`, `{Right}` = Arrow keys
- `{Home}`, `{End}`, `{PgUp}`, `{PgDn}` = Navigation
- `{F1}` through `{F12}` = Function keys
- `{Delete}`, `{Backspace}` = Delete keys

### SendInput()
Faster, more reliable sending (recommended for long sequences)
```ahk
SendInput("^c")
SendInput("{Enter}")
```

## Running Programs

### Run()
Launch programs or open files
```ahk
Run("notepad.exe")
Run("C:\\Program Files\\App\\app.exe")
Run("https://google.com")  ; Opens in default browser
Run("explorer.exe C:\\Users")
Run("cmd.exe")
Run("powershell.exe")
```

**With working directory:**
```ahk
Run("python script.py", "C:\\Projects")
```

**With options:**
```ahk
Run("notepad.exe", , "Hide")      ; Hidden
Run("notepad.exe", , "Max")       ; Maximized
Run("notepad.exe", , "Min")       ; Minimized
```

### RunWait()
Run and wait for program to close
```ahk
RunWait("notepad.exe")
MsgBox("Notepad closed!")
```

## Window Operations

### WinActivate()
Bring window to front
```ahk
WinActivate("A")                    ; Active window
WinActivate("Untitled - Notepad")   ; By title
WinActivate("ahk_exe chrome.exe")   ; By process
WinActivate("ahk_class Notepad")    ; By class
```

### WinClose()
Close window
```ahk
WinClose("A")                       ; Active window
WinClose("Untitled - Notepad")
```

### WinMaximize(), WinMinimize(), WinRestore()
Change window state
```ahk
WinMaximize("A")
WinMinimize("A")
WinRestore("A")
```

### WinMove()
Move/resize window
```ahk
WinMove(100, 100, 800, 600, "A")  ; x, y, width, height
```

### WinGetTitle()
Get window title
```ahk
title := WinGetTitle("A")
MsgBox(title)
```

### WinGetProcessName()
Get process name
```ahk
process := WinGetProcessName("A")
MsgBox(process)
```

### WinExist(), WinActive()
Check if window exists or is active
```ahk
if WinExist("Notepad") {
    MsgBox("Notepad is open")
}

if WinActive("A") {
    MsgBox("Window is active")
}
```

## Clipboard Operations

### Read Clipboard
```ahk
text := A_Clipboard
MsgBox(text)
```

### Set Clipboard
```ahk
A_Clipboard := "New text"
A_Clipboard := ""  ; Clear clipboard
```

### Wait for Clipboard
```ahk
A_Clipboard := ""
Send("^c")
if ClipWait(1) {  ; Wait 1 second
    MsgBox("Copied: " A_Clipboard)
}
```

### Backup/Restore Clipboard
```ahk
saved := ClipboardAll()  ; Backup
A_Clipboard := "Temporary text"
; ... do stuff ...
A_Clipboard := saved  ; Restore
```

## Messages & Dialogs

### MsgBox()
Show message
```ahk
MsgBox("Hello!")
MsgBox("Title", "Message text")
MsgBox("Error!", "Something went wrong", "Icon!")
```

### ToolTip()
Show tooltip
```ahk
ToolTip("Processing...")
Sleep(2000)
ToolTip()  ; Hide tooltip
```

### InputBox()
Get user input
```ahk
result := InputBox("Enter your name:", "Input")
if result.Result = "OK" {
    MsgBox("Hello " result.Value)
}
```

## Timing & Delays

### Sleep()
Pause execution
```ahk
Sleep(1000)  ; 1 second
Sleep(500)   ; 0.5 seconds
```

### SetTimer()
Run function repeatedly
```ahk
SetTimer(MyFunction, 1000)  ; Every 1 second
SetTimer(MyFunction, -5000) ; Once after 5 seconds
SetTimer(MyFunction, 0)     ; Stop timer

MyFunction() {
    ToolTip("Timer fired!")
}
```

## Variables & Strings

### Variables
```ahk
myVar := "Hello"
number := 42
result := 10 + 20
```

### String Operations
```ahk
; Concatenation
fullName := firstName " " lastName

; Length
len := StrLen("Hello")

; Replace
newStr := StrReplace("Hello World", "World", "AHK")

; Upper/Lower case
upper := StrUpper("hello")
lower := StrLower("HELLO")

; Contains
if InStr("Hello World", "World") {
    MsgBox("Found!")
}

; Split
parts := StrSplit("a,b,c", ",")
```

## Control Flow

### If/Else
```ahk
if (condition) {
    ; do something
} else if (other) {
    ; do other
} else {
    ; default
}
```

### Loop
```ahk
Loop 5 {
    MsgBox("Iteration " A_Index)
}

Loop Files, "C:\\*.txt" {
    MsgBox(A_LoopFileName)
}
```

### While
```ahk
count := 0
while (count < 5) {
    count++
    MsgBox(count)
}
```

## File Operations

### FileRead()
Read file content
```ahk
content := FileRead("C:\\file.txt")
MsgBox(content)
```

### FileAppend()
Append to file
```ahk
FileAppend("New line`n", "C:\\file.txt")
```

### FileDelete()
Delete file
```ahk
FileDelete("C:\\file.txt")
```

### FileExist()
Check if file exists
```ahk
if FileExist("C:\\file.txt") {
    MsgBox("File exists")
}
```

## Mouse Operations

### Click()
Click mouse
```ahk
Click()              ; Left click at current position
Click(100, 200)      ; Click at coordinates
Click("Right")       ; Right click
Click(2)             ; Double click
```

### MouseMove()
Move mouse
```ahk
MouseMove(100, 200)
MouseMove(100, 200, 50)  ; Speed 50 (0-100)
```

### MouseGetPos()
Get mouse position
```ahk
MouseGetPos(&x, &y)
MsgBox("X: " x " Y: " y)
```

## System Information

### A_ScriptDir
Script directory
```ahk
MsgBox(A_ScriptDir)
```

### A_WorkingDir
Current working directory
```ahk
MsgBox(A_WorkingDir)
```

### A_UserName
Current user
```ahk
MsgBox(A_UserName)
```

### A_ComputerName
Computer name
```ahk
MsgBox(A_ComputerName)
```

### A_Now
Current date/time
```ahk
MsgBox(A_Now)  ; Format: YYYYMMDDHH24MISS
```

## Common Patterns

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

### Toggle Window State
```ahk
if WinActive("Notepad") {
    WinMinimize("A")
} else {
    WinActivate("Notepad")
}
```

### Send Command to Terminal
```ahk
SendText("cd Documents")
Send("{Enter}")
Sleep(100)
SendText("dir")
Send("{Enter}")
```

### Conditional Action
```ahk
if WinActive("ahk_exe chrome.exe") {
    Send("^t")  ; New tab in Chrome
} else {
    Run("chrome.exe")
}
```

## Context Shortcut Examples

### Terminal Commands
```ahk
; Save chat in Gemini
SendText("/chat save")

; Git commands
SendText("git status")
Send("{Enter}")

; SSH commands
SendText("ssh user@server")
Send("{Enter}")
```

### Browser Automation
```ahk
; New tab
Send("^t")

; Close tab
Send("^w")

; Refresh
Send("{F5}")

; Developer tools
Send("{F12}")
```

### Editor Shortcuts
```ahk
; Save all
Send("^+s")

; Format document
Send("!+f")

; Comment line
Send("^/")
```

### Window Management
```ahk
; Maximize
WinMaximize("A")

; Move to second monitor
WinMove(1920, 0, , , "A")

; Always on top toggle
WinSetAlwaysOnTop(-1, "A")
```

## Tips

1. **Use SendText() for literal text** (terminal commands, chat messages)
2. **Use Send() for key combinations** (Ctrl+C, Alt+F4)
3. **Add Sleep() between actions** to ensure they complete
4. **Backup clipboard** before modifying it
5. **Check window state** before acting on it
6. **Use WinWait()** to wait for windows to appear
7. **Test incrementally** - add one command at a time

## Resources

- [Official AHK v2 Documentation](https://www.autohotkey.com/docs/v2/)
- [Command List](https://www.autohotkey.com/docs/v2/lib/)
- [Tutorial](https://www.autohotkey.com/docs/v2/Tutorial.htm)

---

<a name="context-shortcuts-guide"></a>
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

---

<a name="context-menu-guide"></a>
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

---

<a name="feature-summary"></a>
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

## Recent Additions

### 1. Open Focused App Directory (2026-02-15) ✅

**What:** Global shortcut (Alt+f) to open the containing folder of the active application.

**Features:**
- Works with any focused window
- Automatically identifies the executable path
- Opens the directory in File Explorer
- Robust error handling for system processes

**Use Case:**
- Quickly find where an app is installed
- Access configuration files or logs for the current app
- Open the script directory for a running script

### 2. Context-Aware Shortcuts (2025-01-22) ✅

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
└── README.md                    # Consolidated documentation
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

---

<a name="visual-feature-overview"></a>
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

---

<a name="action-code-hints-feature"></a>
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

---

<a name="duplicate-feature-summary"></a>
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
├─────────────────┤
│ Remove          │
└─────────────────┘
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

---

<a name="context-aware-shortcuts-feature-summary"></a>
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

---

<a name="workflow-example"></a>
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

---

<a name="recent-changes"></a>
# Recent Changes

## 2026-02-15

### ✅ Added "Open Focused App Directory" Shortcut
**New Feature:** Added a global shortcut (Alt+f) that opens the folder containing the executable of the currently focused window.

**How It Works:**
- Press `Alt+f` while any application is focused
- The script identifies the process path of the active window
- Opens the containing directory in File Explorer
- Uses `WinGetProcessPath` and `SplitPath` for reliable path extraction

**Files Modified:**
- `ahk_shortcuts.json` - Added the new shortcut to database
- `generated_shortcuts.ahk` - Updated the generated script with the new functionality

## 2025-01-22

### ✅ Added Action Code Hints & Command Reference
**New Feature:** Action code fields now show helpful placeholder hints with examples, plus a Command Reference button for detailed documentation.

**What's Included:**
- **Context-aware hints:** Different examples for script/context/startup shortcuts
- **Command Reference button:** Opens comprehensive AutoHotkey v2 command guide
- **Common patterns:** Terminal commands, key sending, window operations, clipboard, etc.

**Hints Include:**
- SendText() for terminal commands
- Send() for key combinations
- Run() for launching programs
- Window operations (WinMaximize, WinClose, etc.)
- Clipboard operations
- Multiple action examples
- Comments explaining each command

**Command Reference Covers:**
- Sending text & keys
- Running programs
- Window operations
- Clipboard operations
- Messages & dialogs
- Timing & delays
- Variables & strings
- Control flow
- File operations
- Mouse operations
- System information
- Common patterns
- Context shortcut examples

**Files Added:**
- `AHK_COMMAND_REFERENCE.md` - Comprehensive AutoHotkey v2 command reference

**Files Modified:**
- `ahk_gui_pyqt.py` - Added placeholder hints and command reference dialog

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
