# Advanced Text Selection Menus

This document describes the syntax, structure, and behavior of the advanced selection menu compiler for **Text Shortcuts**.

## Overview

When **Show multi-line text as a selection menu** is enabled on a Text Shortcut, the replacement text is parsed to build an interactive, hierarchical menu system in AutoHotkey v2. 

The menu system supports:
1. **Nesting (Submenus)**: Grouping actions under hoverable sub-items.
2. **Modular Actions**: Setting custom display names, inserting text, or opening directories in Windows File Explorer.
3. **Hotkey Triggers**: Using keyboard shortcuts like `Ctrl+D` (`^d`) as triggers.

---

## Formatting Syntax

The parser scans each line of the replacement text for **submenu dashes** and **bracketed modular tags**.

### 1. Hierarchy & Submenus (Dashes)

Use leading dashes (`-`) to represent nesting levels. 

- **0 dashes**: Root menu item (e.g. `[name:Root Item]`)
- **1 dash (`-`)**: Submenu Level 1 (e.g. `-[name:Level 1 Sub-item]`)
- **2 dashes (`--`)**: Submenu Level 2
- **3 dashes (`---`)**: Submenu Level 3
- **4 dashes (`----`)**: Submenu Level 4
- **5 dashes (`-----`)**: Submenu Level 5 (Maximum clamped level)

If an item contains children (items declared directly below it with more dashes), clicking that item will expand the submenu rather than executing a direct action.

### 2. Modular Action Tags (Brackets)

Each line can contain key-value pairs formatted as `[key:value]`.

| Tag | Purpose | Example |
| :--- | :--- | :--- |
| `name` | Dictates the display name in the menu. Defaults to the action value if omitted. | `[name:My Command]` |
| `text` | Inserts the text using the shortcut's delivery method. | `[text:print("Hello")]` |
| `folder` | Opens the specified directory in Windows File Explorer. | `[folder:C:\Users]` |
| `cmd` | Runs a shell command (CMD by default, hidden window). | `[cmd:ping google.com]` |
| `shell` | Selects the shell for `cmd:`. Values: `cmd` (default), `pwsh` or `powershell`. | `[cmd:Get-Process][shell:pwsh]` |
| `show` | Controls window visibility for `cmd:`. Values: `hidden` (default), `visible`. | `[cmd:dir][show:visible]` |

#### Default / Fallback Rules:
- If a bracketed block has no colon (e.g., `[this is a first command]`), it defaults to the `text:` tag.
- If no tags are provided (e.g., just plain text `Insert Item`), it treats the entire line as both `name` and `text` for backward compatibility.
- Future action tags (e.g., `[url:...]`) can be easily added to the modular compiler loop.

---

## Configuration Example

Below is a complete replacement configuration (as defined in `example.txt`):

```text
[name:Main menu options]
-[name:My Name][text:nahidahmed]
-[name:My first command][this is a first command]
-[name:Open Folders]
--[name:App Data Folder][folder:C:\Users\nahid\.gemini\antigravity-cli]
--[name:Workspace Folder][folder:C:\@delta\ms1\@AutoHotKey\shortcut_manager]
-[name:Commands]
--[name:Flush DNS][cmd:ipconfig /flushdns][show:visible]
--[name:List Processes][cmd:Get-Process][shell:pwsh][show:visible]
--[name:Clear Temp][cmd:Remove-Item $env:TEMP\* -Recurse -Force][shell:pwsh]
```

---

## Generated AutoHotkey v2 Code

For the example above, the compiler generates clean, nested Menu object initialization in the output AHK script:

```autohotkey
^d:: {
    m := CustomMenu()
    m_1 := CustomMenu()
    m_1.Add("App Data Folder", (ItemName, ItemPos, MyMenu) => OpenFolderInTab("C:\Users\nahid\.gemini\antigravity-cli"))
    m_1.Add("Workspace Folder", (ItemName, ItemPos, MyMenu) => OpenFolderInTab("C:\@delta\ms1\@AutoHotKey\shortcut_manager"))
    m_2 := CustomMenu()
    m_2.Add("Flush DNS", (ItemName, ItemPos, MyMenu) => RunCmdVisible("ipconfig /flushdns"))
    m_2.Add("List Processes", (ItemName, ItemPos, MyMenu) => RunPwshVisible("Get-Process"))
    m_2.Add("Clear Temp", (ItemName, ItemPos, MyMenu) => RunPwsh("Remove-Item $env:TEMP\* -Recurse -Force"))
    m.Add("My Name", (ItemName, ItemPos, MyMenu) => Paste("nahidahmed"))
    m.Add("My first command", (ItemName, ItemPos, MyMenu) => Paste("this is a first command"))
    m.Add("Open Folders", m_1)
    m.Add("Commands", m_2)
    m.Show()
}
```


## GUI Interaction & Navigation Behavior

Instead of standard native context menus, the compiler implements a custom side-by-side cascading menu system with advanced mouse and window behaviors:

1. **Cascading Side-by-Side Submenus**: Submenus open adjacent to their parent menu (expanding to the right by default) instead of replacing the parent window or requiring a back button.
2. **Hover Auto-Expansion & Debouncing**: Hovering the mouse pointer over a submenu item automatically opens it. A 400ms debouncing delay is enforced, and mouse-position verification is performed when the timer fires to prevent accidental triggers when moving the pointer across items.
3. **Boundary-Aware Flipping & Clamping**: Menu placement is calculated using screen coordinates (`CoordMode "Mouse", "Screen"`) and is aware of multi-monitor work areas (`MonitorGetWorkArea`).
   - **Horizontal Flipping**: If a submenu would extend beyond the right boundary of the current monitor, it automatically flips to open on the opposite (left) side of the parent menu.
   - **Vertical Clamping**: If a menu would extend below the bottom boundary of the monitor, it is shifted upward to stay fully visible on the screen.
4. **Mouse Back-tracking**: Moving the mouse pointer back onto a parent menu automatically hides and destroys all active submenus down the stack. The parent GUI window is explicitly reactivated to maintain focus.
5. **Loss-of-Focus Auto-Closing**: Focus is monitored globally using the `WM_ACTIVATE` message hook. When any menu window is deactivated, the script checks if the newly activated window (`lParam`) belongs to the menu stack. If focus shifts to any window outside the stack (e.g. desktop, code editor), the entire menu cascade is instantly closed and cleaned up.

## Native Menu vs. Custom GUI Menu

By default, selection menus are compiled using a custom AHK GUI window (`CustomMenu` and `CustomMenuGUI`) which supports custom styling, side-by-side cascading submenus, and mouse-hover expansion.

However, if you prefer the standard Windows native context menu style, you can toggle this behavior.

### Configuration
Open the **Settings** dialog in the AutoHotkey Shortcut Editor GUI. You will find:
1. **Selection Menu Font**: Select any font family installed on your system (e.g. `Segoe UI`, `Consolas`, `Arial`, or `Segoe UI Semibold`).
2. **Selection Menu Font Size**: Adjust the font size from `8` up to `36`.
3. **Use standard Windows native context menu**: Check this box to bypass the custom side-by-side GUI menu stack entirely and compile selection menus to run using standard AHK v2 `Menu` objects.

These values are saved to `ahk_shortcuts.json` under `selection_menu_font_family`, `selection_menu_font_size`, and `use_native_menu` and automatically compiled into `generated_shortcuts.ahk`.


