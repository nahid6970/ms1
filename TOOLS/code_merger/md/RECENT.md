# RECENT.md — AI Handoff

## 1. Project DNA
Single-file PyQt6 desktop app (`merge_gui.py`) with a Cyberpunk theme. Core purpose: prep local files into a structured prompt for AI web UIs, then merge the AI's `@@FILE/@@MODE/@@END` formatted response back to disk with optional git commit/push workflow.

## 2. Latest Implementation
**File modified: `merge_gui.py`**

### Quick-Run Dropdown Button in Merge Tab
- Added a **▶ RUN** `QToolButton` (purple `#B060FF`) to the Merge tab button row, right after PUSH.
- Uses `MenuButtonPopup` mode: clicking either the main area or the dropdown arrow opens a `QMenu`.
- The menu lists all saved commands for the current project (from `settings.json['project_commands']`).
- Shows a disabled placeholder `"(no commands — add them in COMMANDER tab)"` when none exist.
- Wired `_run_menu.aboutToShow` → `_refresh_run_menu()` so the list always reflects latest saves.
- `_launch_command()` added to `MergeTab` — same wt.exe / cmd /k / osascript logic as COMMANDER tab.
- `set_root()` also calls `_refresh_run_menu()` when project switches.
- New imports: `QToolButton` (QtWidgets), `QAction` (QtGui).

### Push Button Polish
- Replaced plain up-arrow push icon with **upload-to-cloud SVG** (arrow + cloud path, Lucide-style) in yellow.
- Added busy-state icon variant (`_PUSH_BUSY_SVG`) shown while push is in-progress.
- `btn_commit` and `btn_push` now have `setFixedHeight(32)` + `setMinimumWidth(130)` — matched pair.
- `_git_push()` swaps to busy icon on start, restores idle icon when done.

### Disabled Button Visibility Fix
- `btn_commit` and `btn_push` disabled state changed from `color: CP_DIM (#3a3a3a)` → `color: #666; border: 1.5px solid #555` so text is readable when inactive.

### Previous: COMMANDER tab
- Per-project saved command manager (`ProjectCommandsTab`). Each row has ▶ RUN / ✎ EDIT / ✖ DEL buttons.
- Commands stored in `settings.json['project_commands'][<normalized_path>]`.
- Terminal: tries `wt.exe` first, falls back to `start cmd /k`.

## 3. Critical Context
- `load_project_commands(root)` reads from `settings.json` — used by both COMMANDER tab and the new RUN dropdown.
- `_run_menu.aboutToShow` re-reads disk on every open — always fresh.
- `_combined_set_root` in MainWindow chains: `merge_tab.set_root` → `project_commands_tab.set_project_root` → header update.

## 4. Pending Task
Test COMMANDER tab end-to-end: add a command, verify it appears in the RUN dropdown on the Merge tab without switching projects.
