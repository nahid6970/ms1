# startup.py — Changes (2026-06-14)

## 1. SHOW TERMINAL Toggle
- Added **SHOW TERMINAL** checkbox in `ItemDialog` next to **RUN AS ADMIN**
- Stored as `show_terminal` (bool) in the item JSON
- Controls whether a terminal/console window appears when launching an item

## 2. Execute Protocol — Mode-Aware Launch
"Execute Protocol" (right-click context menu) now simulates the actual startup mechanism based on the active mode:

### REGISTRY Mode
| Condition | Behavior |
|---|---|
| `run_as_admin=True` | Runs `wscript.exe _admin.vbs` — same as what's written to the registry |
| `show_terminal=False` + script path (`.py/.ps1/.bat/.cmd`) | Runs `wscript.exe _hidden.vbs` with window style `0` (hidden) |
| `show_terminal=True` or `.exe` | Runs `"path" args` via shell (normal window) |

### SCRIPT Mode
| Condition | Behavior |
|---|---|
| Normal | Runs `ps1_command` via `powershell -NoProfile -Command` — identical to the generated PS1 |
| `run_as_admin=True` | Same + appends `-Verb RunAs` |

## 3. Execute As Admin — Mode-Aware
- **REGISTRY mode**: always uses the VBS/wscript elevation path (window style `1`)
- **SCRIPT mode**: runs `ps1_command` with `-Verb RunAs` appended

## 4. Hidden Terminal at Actual Startup
`show_terminal=False` now suppresses the terminal at real startup too:

### REGISTRY Mode
- When toggling ON: writes `wscript.exe "_hidden.vbs"` to the registry key instead of the raw path
- VBS uses `ShellExecute` with window style `0` (SW_HIDE)

### SCRIPT Mode
- `generate_ps1` appends `-WindowStyle Hidden` to the command when `show_terminal=False`

> **Note:** If an item was already toggled ON before these changes, toggle it OFF and back ON to re-write the registry/PS1 with the new hidden behavior.

## 5. `_make_vbs` — Window Style Parameter
- Added `window_style=1` parameter (1=normal/runas, 0=hidden)
- Generates `_admin.vbs` for elevation, `_hidden.vbs` for hidden launch
- VBS verb is `""` (empty) for hidden, `"runas"` for admin
