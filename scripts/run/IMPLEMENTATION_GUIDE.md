# FZF Project Implementation Guide

This document outlines the standard architecture, visual style, and shortcut conventions for the `@delta` script ecosystem. Follow these rules to ensure consistency and avoid common implementation pitfalls.

## 1. Directory & Data Standards
- **Database Location**: All JSON history, bookmarks, and settings must be stored in `C:\@delta\db\FZF_launcher`.
- **Script Location**: Place related scripts in their own subfolder under `C:\@delta\ms1\scriptsun`.
- **Unicode**: Always include the following in Python feeders:
  ```python
  if hasattr(sys.stdout, "reconfigure"):
      sys.stdout.reconfigure(encoding="utf-8", errors="replace")
  ```

## 2. Visual Aesthetic (Cyberpunk)
- **FZF Colors**:
  ```bash
  --color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff
  ```
- **Markers**: 
  - Use `* ` (star + space) for bookmarked items.
  - Use `  ` (two spaces) for normal items to maintain alignment.
- **Layout**: Always use `--layout=reverse --border --header-first`.

## 3. Shortcut Conventions
To match existing tools, key bindings must be implemented as follows:

| Key | Action | Implementation Detail |
| :--- | :--- | :--- |
| **Enter** | Primary Action | Use `execute-silent(...) + reload(feeder)` to prevent terminal clearing AND maintain responsiveness on Windows. |
| **?** | Toggle Header | Use `--no-header` + `--bind=start:toggle-header` + `--bind=?:toggle-header`. |
| **F1** | Help Window | `execute-silent(cmd /c start cmd /k type "{help_path}" ^& pause)` |
| **F5** | Bookmark | `execute-silent(python add_script.py {selection}) + reload(feeder)` |
| **Del** | Remove | `execute-silent(python remove_script.py {selection}) + reload(feeder)` |
| **Ctrl-R** | Refresh | `reload(python feeder.py)` |

## 4. Handling the "Black Window" Issue
When launching a PyQt6 GUI (like a chooser) from within `fzf`:
- **Problem**: `execute(...)` clears the terminal buffer, leaving the user looking at a black screen while the GUI is open.
- **Solution**: Use `execute-silent(...)`. This keeps the `fzf` interface visible in the background while the GUI pops up on top.

## 5. Header Toggling (The "Run.py" Style)
To start with the help header hidden but allow toggling:
1. Define your `help_header` string.
2. Add these flags to `fzf_args`:
   ```python
   "--header-first",
   "--no-header",
   f"--header={help_header}",
   "--bind=?:toggle-header",
   "--bind=start:toggle-header"
   ```

## 6. Multi-Argument Passing
When passing selections to helper scripts, always quote the placeholders to handle spaces:
`python script.py "{1}" "{q}" "{2}"`

## 7. PyQt6 GUI Standards
- **Style**: Use the `CP_` palette (Cyberpunk Yellow: `#FCEE0A`, Cyan: `#00F0FF`, Red: `#FF003C`).
- **Behavior**: Set `Qt.WindowType.WindowStaysOnTopHint` and close the window on `focusOutEvent` or `ActivationChange` for a "popup" feel.
