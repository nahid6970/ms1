# RECENT.md — AI Handoff

## 1. Project DNA
Single-file PyQt6 desktop app (`merge_gui.py`) with a Cyberpunk theme. Core purpose: prep local files into a structured prompt for AI web UIs, then merge the AI's `@@FILE/@@MODE/@@END` formatted response back to disk with optional git commit/push workflow.

## 2. Latest Implementation
**File modified: `merge_gui.py`**

### Merge Tab Button Row — Final State
Button row order (left → right):
```
[ 🔍 PARSE CHANGES ]  [ ✔ APPLY CHANGES ]  [ ⊕ COMMIT ]  [ ↑ PUSH ]  <stretch>  [ RUN ▾ ]
```

- **PARSE / APPLY** — cyan / green styled QPushButtons (existing, unchanged).
- **COMMIT** — cyan border/text, SVG git-commit icon, `setFixedHeight(32)`, `setMinimumWidth(130)`, disabled state `color: #666 / border: #555`.
- **PUSH** — yellow border/text, upload-to-cloud SVG icon (idle + busy variants stored as `self._push_icon_idle` / `self._push_icon_busy`), same sizing as COMMIT. Icon swaps to busy during `_git_push()` and restores on finish.
- **RUN ▾** — plain unstyled default `QPushButton("RUN ▾")`, no custom stylesheet, floats right via `addStretch()` before it. Opens `self._run_menu` (QMenu) anchored below the button via `_open_run_menu()`.

### Quick-Run Dropdown
- `self._run_menu` is a `QMenu` with no custom styling (inherits app defaults).
- `_run_menu.aboutToShow` → `_refresh_run_menu()` — always re-reads `settings.json` on open.
- `_refresh_run_menu()` — loads commands via `load_project_commands(root)`, adds a `QAction` per entry (`▶  <label>`), or a disabled placeholder if none exist.
- `_open_run_menu()` — positions menu at `btn_run_menu.rect().bottomLeft()` mapped to global coords.
- `_launch_command(cmd, label)` — launches in terminal: wt.exe → `cmd /k` fallback on Windows, osascript on macOS, gnome-terminal/xterm on Linux.
- `set_root()` also calls `_refresh_run_menu()` on project switch.

### Imports added
- `QAction` added to `from PyQt6.QtGui import ...`

### Previous: COMMANDER tab
- Per-project saved command manager (`ProjectCommandsTab`). Each row has ▶ RUN / ✎ EDIT / ✖ DEL.
- Commands stored in `settings.json['project_commands'][<normalized_path>]`.
- Terminal: tries `wt.exe` first, falls back to `start cmd /k`.

## 3. Critical Context
- `load_project_commands(root)` is the shared reader used by both COMMANDER tab and the RUN dropdown.
- `_combined_set_root` in `MainWindow` chains: `merge_tab.set_root` → `project_commands_tab.set_project_root` → header update.
- `_BTN_H = 32`, `_BTN_W = 130` are local constants inside `_build_merge_tab` used for COMMIT and PUSH sizing only (RUN uses default sizing).

## 4. Pending Task
Test end-to-end: add a command in COMMANDER tab, open Merge tab, click RUN ▾ — verify the command appears and launches correctly.
