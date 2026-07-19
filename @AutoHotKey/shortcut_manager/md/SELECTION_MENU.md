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
```

---

## Generated AutoHotkey v2 Code

For the example above, the compiler generates clean, nested Menu object initialization in the output AHK script:

```autohotkey
^d:: {
    m := Menu()
    m_1 := Menu()
    m_1.Add("App Data Folder", (ItemName, ItemPos, MyMenu) => OpenFolderInTab("C:\Users\nahid\.gemini\antigravity-cli"))
    m_1.Add("Workspace Folder", (ItemName, ItemPos, MyMenu) => OpenFolderInTab("C:\@delta\ms1\@AutoHotKey\shortcut_manager"))
    m.Add("My Name", (ItemName, ItemPos, MyMenu) => Paste("nahidahmed"))
    m.Add("My first command", (ItemName, ItemPos, MyMenu) => Paste("this is a first command"))
    m.Add("Open Folders", m_1)
    m.Show()
}
```
