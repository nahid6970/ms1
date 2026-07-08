# Problems & Fixes Log

---

## [2026-07-06 15:24] - PowerShell Command Parsing Error with `$?`
**Problem:** Running debug scripts via PowerShell wrapper `& { script } ; if (-not $?) { ... }` failed with parser errors:
```
Missing expression after unary operator '-not'.
Unexpected token 'True' in expression or statement.
```
**Root Cause:** The outer shell was interpreting `$?` and other PowerShell syntax before the inner command could process it, causing token parsing failures.
**Solution:** Switched to PowerShell `-EncodedCommand` with Base64 encoding. The script is converted to UTF-16LE bytes, Base64-encoded, and passed as `-EncodedCommand` so no shell interpolation occurs.
**Files Modified:** `templates/index.html` — `handleRunDebugScript()` / `executeExplorerRun()`

---

## [2026-07-06 15:40] - File Delete Shows "Error deleting file" Despite Success
**Problem:** After successfully deleting a file, the UI displayed an alert saying "Error deleting file."
**Root Cause:** The success handler called `refreshFileTree()` which **did not exist** as a function. This threw a `ReferenceError`, which was caught by the surrounding `try/catch` block and displayed the error alert.
**Solution:** Replaced `refreshFileTree()` with `loadExplorerRoot()` — the actual function that reloads the file explorer tree.
**Files Modified:** `templates/index.html` — `deleteExplorerFile()`

---

## [2026-07-06 15:28] - Debug Script Runner Interfering with Agent CLIs
**Problem:** Running a debug script executed it in the current terminal pane, which disrupted any running agent CLI session.
**Root Cause:** The original implementation wrote the command directly to the active terminal pane.
**Solution:** Changed to open a new tab via `splitTerminal('tabs', cmd + '\r')` so the debug script runs in an isolated pane.
**Files Modified:** `templates/index.html` — `handleRunDebugScript()` → `executeExplorerRun()`

---

## [2026-07-06 ~15:25] - Autocomplete Dropdown Showing `python script.py` Instead of `script.py`
**Problem:** The debug script autocomplete dropdown was displaying command-prefixed strings (e.g., `python myscript.py`) instead of just the filename.
**Root Cause:** The dropdown options were being formatted with the runner prefix before being displayed.
**Solution:** Changed to show raw filenames only (e.g., `myscript.py`, `.\\test.ps1`). The runner prefix is added only at execution time based on the selected mode.
**Files Modified:** `templates/index.html` — `filterDebugScripts()` / `openDebugScriptModal()`

---

## [2026-07-08 21:00] - Mobile Layout Disappears / Covered by Black UI Overlay
**Problem:** On mobile browsers (Safari/Chrome), the top header and bottom status bar completely disappeared or were covered by a black/blurry layer after recent commits.
**Root Cause:** Hidden modal overlays (`.modal-overlay`) with high z-index (like `ai-model-tester-modal` and `ai-system-prompt-modal` at `z-index: 3000`) had `display: flex` and were only hidden via `opacity: 0; pointer-events: none;`. A rendering/compositing bug on mobile GPUs causes the `backdrop-filter: blur(8px)` and/or the background overlay to still render and composite on top of all other page elements, blocking the entire screen.
**Solution:** Added `visibility: hidden;` to `.modal-overlay` and transitioned it in CSS (`transition: opacity 0.25s ease, visibility 0.25s ease;`), toggling it to `visibility: visible;` in `.modal-overlay.show`. This completely excludes the hidden overlays from the render tree, resolving the GPU compositing bug.
**Files Modified:** `templates/index.html` — `.modal-overlay` / `.modal-overlay.show` styles

---

## [2026-07-08 21:05] - Upload Button Only Allows Selecting One Image at a Time
**Problem:** The screenshot/image upload button (`#screenshot-upload-btn`) only allowed selecting and uploading a single image at a time.
**Root Cause:** The underlying `<input type="file" id="screenshot-file-input">` element lacked the `multiple` HTML attribute, and the `handleScreenshotFileSelect(event)` javascript handler only processed `event.target.files[0]`.
**Solution:** Added the `multiple` attribute to the input file element, and updated `handleScreenshotFileSelect` to map files to concurrent upload promises, await them with `Promise.all`, and write the resulting space-separated, quoted paths to the active terminal input.
**Files Modified:** `templates/index.html` — screenshot-file-input element & handleScreenshotFileSelect JS function

---

## [2026-07-08 23:57] - Performance Overhead from Loading Multiple JSON Configuration Files
**Problem:** The application had to load and parse six separate JSON configuration files (projects, extension icons, subcommands, starred ports, custom buttons, snippets), causing unnecessary disk I/O and potential performance bottlenecks.
**Root Cause:** The configuration system was fragmented across multiple files, each read and written independently on demand.
**Solution:** Consolidated all six JSON configuration files into a single unified config file (`tui_config.json`). Added automated backward-compatible migration logic on startup to merge existing old configuration files if `tui_config.json` doesn't exist, and implemented thread-safe in-memory configuration caching to make subsequent reads near-instantaneous.
**Files Modified:** `app.py` — Config variables, helpers, and endpoints refactored

---

## [2026-07-09 00:02] - Relocation of Unified Configuration to Main Project Directory
**Problem:** The consolidated config file `tui_config.json` was originally saved in the external backup database directory (`C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\`), which separates config from the project root.
**Root Cause:** Initial design placed it alongside original backups, but placing it in the main project directory makes the app more self-contained.
**Solution:** Changed `CONFIG_FILE` path to point to the local project root (`tui_config.json`). Enhanced startup migration logic to: (1) check for the backup folder's `tui_config.json` and copy/migrate it locally, or (2) fallback to migrating from the original 6 separate JSON files. Added `tui_config.json` to `.gitignore` to prevent committing local workspace state.
**Files Modified:** `app.py` — Updated CONFIG_FILE path and migrate_existing_configs, `.gitignore` — added tui_config.json

---

## [2026-07-09 00:04] - Relocation of Project_data to Main Project Directory
**Problem:** Project-specific workspace metadata (PowerShell profiles, command history) was stored externally inside the backup directory (`C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\Project_data\`).
**Root Cause:** Initial layout path placed `Project_data` inside the database backup location, making it dependent on an external directory path structure.
**Solution:** Relocated `Project_data` directory to the local main project root. Added copy-on-initialization migration logic in the backend to check for the backup folder's existing project data folder and migrate it locally if it doesn't already exist.
**Files Modified:** `app.py` — Updated `project_data_dir` path and added copy-on-init migration logic

---

## [2026-07-09 00:20] - Git Constantly Shows `tui_config.json` Modified
**Problem:** Whenever the user works on the project, Git shows `tui_config.json` as modified even when the user hasn't made any manual configuration changes.
**Root Cause:** On page load or session init, the frontend called `saveTerminalLayoutState()` which unconditionally sent a POST request to `/api/projects/<project>/layout` with the current layout (even if it was the default layout). The backend then wrote the configuration file back to disk on every layout POST request, even if there was no actual change, causing the modification timestamp and formatting to trigger a Git diff.
**Solution:** 
1. Updated `saveTerminalLayoutState` in `templates/index.html` to skip the REST API request if the active project's layout already matches the new state, or if no layout is saved yet and the new state is the default layout.
2. Updated `set_config_val` in `app.py` to check if the new configuration value is identical to the cached version, skipping file write operations if no data changes have occurred.
**Files Modified:** `templates/index.html` — `saveTerminalLayoutState` function; `app.py` — `set_config_val` function.


