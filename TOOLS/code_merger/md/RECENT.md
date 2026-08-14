# RECENT.md — AI Handoff

## 1. Project DNA
Single-file PyQt6 desktop app (`merge_gui.py`) with a Cyberpunk theme. Core purpose: prep local files into a structured prompt for AI web UIs, then merge the AI's `@@FILE/@@MODE/@@END` formatted response back to disk with optional git commit/push workflow.

## 2. Latest Implementation
**File modified: `merge_gui.py`**

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

## 4. Pending Task
Test COMMANDER tab end-to-end: add a command, switch projects, verify the list clears and reloads correctly per project.
