# RECENT.md — AI Handoff

## 1. Project DNA
Single-file PyQt6 desktop app (`merge_gui.py`) with a Cyberpunk theme. Core purpose: prep local files into a structured prompt for AI web UIs, then merge the AI's `@@FILE/@@MODE/@@END` formatted response back to disk with optional git commit/push workflow.

## 2. Latest Implementation
**File modified: `merge_gui.py`**

### Push Button Polish
- Replaced the plain up-arrow push icon with a **upload-to-cloud SVG** (arrow + cloud path, Lucide-style) in yellow (`#FCEE0A`).
- Added a **busy variant** of the push icon (`_PUSH_BUSY_SVG`) — same cloud-upload shape with a small filled dot at top-right — shown while push is in-progress.
- Both `btn_commit` and `btn_push` now have **uniform sizing**: `setFixedHeight(32)` + `setMinimumWidth(130)` so they render as a matched pair.
- `_git_push()` now swaps to `_push_icon_busy` on start and restores `_push_icon_idle` when done (success or failure).
- Icons stored as `self._push_icon_idle` / `self._push_icon_busy` on the widget for easy access.

### Previous: COMMANDER tab
- Added **📋 COMMANDER tab** (`ProjectCommandsTab` class) — per-project saved command manager. Each command (label + cmd string) is stored in `settings.json` under `project_commands[<normalized_path>]`. Each row renders inline with **▶ RUN**, **✎ EDIT**, **✖ DEL** buttons. Running opens a real terminal window (wt.exe → `cmd /k` fallback on Windows).
- Added `load_project_commands()` / `save_project_commands()` helpers.
- Added `AddEditCommandDialog` for add/edit flow.
- Added `import shlex` (macOS terminal quoting).
- Kept existing **💻 RUNNER tab** (`CommandTab`) untouched — single ad-hoc command runner.
- Renamed tabs: `RUNNER` and `COMMANDER` (shorter = no scroll arrows in tab bar).
- Settings (`⚙`) and Restart (`⟳`) buttons are now icon-only with tooltips; Consolas font removed from them so Unicode symbols render correctly.

## 3. Critical Context
- `ProjectCommandsTab.set_project_root()` is wired via a lambda in `MainWindow._build` that wraps `merge_tab.set_root` — both fire together when project switches in PREP tab.
- Commands saved per project using `os.path.normpath` key in `settings.json['project_commands']`.
- Terminal launch: tries `wt.exe` first, falls back to `start cmd /k` — both use `DETACHED_PROCESS`.
- Push button idle/busy icons: `self._push_icon_idle` / `self._push_icon_busy` (set during `_build_merge_tab`).

## 4. Pending Task
Test COMMANDER tab end-to-end: add a command, switch projects, verify the list clears and reloads correctly per project.
