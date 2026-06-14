# STARTUP // MANAGER — Project Overview

## What It Does
A cyberpunk-themed PyQt6 GUI for managing Windows startup items. It replaces manual registry editing and startup folder management with a unified interface that supports two launch methods, cloud backup, and live testing of startup entries.

---

## Two Modes

| Mode | How it works |
|---|---|
| **REGISTRY** | Reads/writes `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`. Items run directly when Windows starts. |
| **SCRIPT** | Generates a `.ps1` file on your Desktop. That script is run at startup and executes all enabled items sequentially. |

Toggle between modes with the **MODE** button in the toolbar. Mode is persisted across sessions.

---

## Key Features

### Item Management
- **Add / Edit / Delete** startup entries via `ItemDialog`
- Each item stores: name, type (App/Command), path, args, ps1_command, exec type, run_as_admin, show_terminal
- Two columns: **CMD_LINE_INTERFACE** (Command type) and **APPLICATION_LAYER** (App type)
- Sort by Name or Date, ASC/DESC

### Launching (Context Menu)
Right-click any item for:
- **EXECUTE PROTOCOL** — simulates actual startup behavior for the active mode
- **EXECUTE AS ADMIN** — same but forced elevated

### SHOW TERMINAL Toggle (per item)
Controls whether a console window appears — both in preview and at actual startup:
- `False` → hidden at startup (VBS window-style 0 for registry, `-WindowStyle Hidden` for script)
- `True` → terminal visible

### Scanning
| Button | What it scans |
|---|---|
| SCAN_SYS | Startup folders (`%APPDATA%` + `%ProgramData%`) |
| SCAN_REG | All registry Run/RunOnce keys (HKCU + HKLM) |
| SCAN_TASKS | Task Scheduler logon/boot triggers |
| SCAN_UWP | Windows Store app startup tasks |

All scans show a filterable checklist — select which items to import.

### PRUNE_LNK
Finds `.lnk` shortcuts in startup folders that match items already in your list and deletes them (prevents double-launching).

### Cloud Backup (Convex)
- **Backup** — saves current config to Convex cloud with a label
- **Restore** — pick any previous backup to restore from
- **CHECK** — compares current config against latest backup
- **SHOW DIFF** — GitHub-style color diff between local and remote

---

## Data Files
| File | Purpose |
|---|---|
| `C:\@delta\output\startup\startup_items.json` | All startup item definitions |
| `C:\@delta\output\startup\settings.json` | Mode, sort, PS1 path |
| `C:\@delta\output\startup\vbs\*.vbs` | Auto-generated VBS launchers (admin/hidden) |
| `~/Desktop/myStartup.ps1` | Generated PS1 startup script (default path) |

---

## Important Classes

### `MainWindow`
The main application window. Owns all state and orchestrates everything.

| Method | Purpose |
|---|---|
| `handle_toggle` | Enables/disables an item in registry or PS1 script |
| `handle_launch` | Executes an item from the context menu, simulating startup behavior |
| `generate_ps1` | Rebuilds the `.ps1` startup script from all `script_enabled` items |
| `_make_vbs` | Creates a VBS launcher — `window_style=1` for runas, `0` for hidden |
| `check_registry` | Returns whether an item is currently in the registry Run key |
| `populate_lists` | Rebuilds both columns from `self.items` |
| `scan_registry` | Scrapes all Run/RunOnce registry keys for new entries |
| `scan_tasks` | Uses PowerShell to find logon/boot scheduled tasks |
| `scan_uwp` | Finds UWP/Store app startup tasks via registry + AppX manifests |
| `backup_to_convex` / `restore_from_convex` | Cloud sync via Convex HTTP API |

### `ItemDialog`
Add/edit dialog for a single startup entry. Fields: name, type, exec type, path, args, ps1_command, RUN AS ADMIN, SHOW TERMINAL.

### `StartupItemWidget`
A row widget representing one startup item. Shows status (ON/OFF), name, path, date. Emits signals for toggle, launch, edit, delete. Right-click opens context menu.

### `ScanResultsDialog`
Filterable checklist dialog used by all scan operations to select which found items to import.

### `DiffDialog`
Color-coded unified diff view (GitHub style) comparing two JSON configs.

### `ConvexLabelDialog`
Backup dialog with inline CHECK and SHOW DIFF against the latest cloud backup.

### `RestoreDialog`
Lists all cloud backups with restore, diff, and delete per entry.

---

## UI Components

| Class | Purpose |
|---|---|
| `CyberButton` | Styled QPushButton with optional SVG icon, outlined/filled variants |
| `CyberInput` | Styled QLineEdit with cyberpunk theme |
