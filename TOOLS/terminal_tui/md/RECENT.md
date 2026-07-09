# Recent Development Log

All sessions recorded here — no archiving, full history in one place.
Read this file only when relevant to the current task. When reading, reference the last 5 sessions max.

---

## [2026-07-03] - Git Integration & Mobile Controls Overhaul
**What We Accomplished:**
- Changed `git add .` to `git add -A` to handle moved files
- Added collapsible past commits section (last 10 commits)
- Added commit rename (amend HEAD only)
- Added checkout for time-travel to past commits with detached HEAD warning
- Added discard all changes (`git restore` + `git clean`)
- Added mobile ESC, Ctrl+C, ← → buttons
- Added custom button shortcuts per project (+ button → modal)
- UI polish: compact git modal, single-line commit rows, chevron toggle

**Files Modified:**
- `app.py` — git routes, session stats
- `templates/index.html` — git modal UI, mobile controls

---

## [2026-07-06 ~14:00] - Mobile Input Tray & Status Bar Updates
**What We Accomplished:**
- Implemented persistent mobile input tray for Gboard spacebar-slide cursor control
- Text is inserted into terminal without auto-enter (user explicitly sends Enter when ready)
- Updated status bar icons: CPU/RAM use SVG icons instead of text labels
- RAM displayed as integer only (no "MB" suffix)
- Status bar button styling with `.sbicon-btn` class

**Files Modified:**
- `templates/index.html` — mobile input tray, status bar icons

---

## [2026-07-06 ~15:00] - Debug Script Runner → Explorer Run Integration
**What We Accomplished:**
- Originally added a Debug Script Runner modal with custom dropdown for script selection
- User didn't like the dropdown UI — replaced with Quick Select pills
- User wanted it integrated into the File Explorer instead of a separate button
- **Final implementation:** Removed standalone Run Debug Script button from toolbar
- Added ▶ (play) icon on each file in the File Explorer (shows on hover, before the 👁 eye icon)
- Clicking play opens a card-style modal (like split-select-modal) with 3 options:
  - **PowerShell** — wraps with `-EncodedCommand` + error pause
  - **Command Prompt** — wraps with `cmd /c "... || pause"`
  - **Raw Execution** — sends directly to new tab
- All run in a new tab (`splitTerminal('tabs')`) to avoid interrupting agent CLIs
- Click-outside-to-close on the modal overlay

**Files Modified:**
- `templates/index.html` — explorer-run-modal HTML, JS functions
- `app.py` — no backend changes for this feature

**Known Issues:**
- PowerShell `-EncodedCommand` is needed because wrapping `$?` in a command string causes parser errors

---

## [2026-07-06 ~15:35] - File Explorer Delete, Paste & Folder Actions
**What We Accomplished:**
- Added 🗑 (trash) delete button in file explorer — appears on hover after the eye icon
- Delete button now shows for **both files and folders** (originally files-only)
- Added `POST /api/project/<project>/file-delete` backend endpoint (handles files + recursive folder delete via `shutil.rmtree`)
- Fixed false "Error deleting file" alert — was caused by calling non-existent `refreshFileTree()` instead of `loadExplorerRoot()`
- Added "Paste Files" button at bottom of explorer panel
- Paste uses PowerShell `[System.Windows.Forms.Clipboard]::GetFileDropList()` to read copied files from Windows clipboard
- Backend `POST /api/project/<project>/paste-clipboard` copies files/folders into project root via `shutil.copy2`/`copytree`
- Added `POST /api/project/<project>/file-write` endpoint for creating files with content

**Files Modified:**
- `app.py` — `file-delete`, `file-write`, `paste-clipboard` routes
- `templates/index.html` — explorer action buttons, paste bar, JS functions

---

## [2026-07-06 ~15:56] - Documentation Restructure
**What We Accomplished:**
- Created proper `md/` documentation folder per project template guide
- Created `md/AI_CONTEXT.md` — stable project brief for AI handoff
- Created `md/FEATURES.md` — all feature specifications with status
- Created `md/UI_UX.md` — design system, color palette, component patterns
- Created `md/RECENT.md` — this development session log
- Created `md/PROBLEMS_AND_FIXES.md` — bug tracking
- Created `dev.md` — main development guide linking to all docs
- Renamed `PROJECT.md` → `md/ARCHITECTURE.md` as the detailed architecture reference

*Next session: Consider adding keyboard shortcuts doc, further UI polish*

---

## [2026-07-08] - Mobile Overlay Bug Fix, Multiple Screenshot Upload & Config Consolidation
**What We Accomplished:**
- Identified and fixed mobile layout rendering bug where the top header and bottom status bar disappeared or were covered by a black/blurry layer.
- Root Cause: Multiple hidden `.modal-overlay` elements with high z-index (3000) and `backdrop-filter: blur(8px)` remained in the layout (`display: flex`) and triggered mobile GPU rendering/compositing bugs, rendering them opaque.
- Solution: Updated `.modal-overlay` CSS to use `visibility: hidden;` and transitioned it along with `opacity` to completely exclude inactive modals from the rendering tree.
- Resolved screenshot upload limitation where only one image could be selected/uploaded at a time.
- Added `multiple` attribute to `screenshot-file-input` and updated JS handler to upload files concurrently using `Promise.all` and join the resulting paths with spaces.
- Consolidated six individual JSON configuration files (`projects.json`, `extension_icons.json`, `subcommands.json`, `starred_ports.json`, `custom_buttons.json`, `snippets.json`) into a single unified configuration file `tui_config.json`.
- Implemented backward-compatible startup migration logic in the backend to merge existing JSON configurations into `tui_config.json`.
- Relocated the unified `tui_config.json` configuration file and the `Project_data` workspace folder to the local main project directory.
- Added `tui_config.json` to `.gitignore` to prevent tracking local configurations in git (note: `Project_data` was already ignored).
- Updated migration logic to check for both the database backup unified configuration or the original six JSON files to perform a seamless transition.
- Implemented copy-on-init migration for `Project_data` workspaces to seamlessly transfer existing profiles and histories to the local project root.
- Added thread-safe, in-memory caching for the unified configuration values to minimize disk reads and optimize TUI responsiveness.
- Updated documentation (`md/PROBLEMS_AND_FIXES.md` and `md/RECENT.md`).

**Files Modified:**
- `templates/index.html` — updated modal-overlay transition/visibility and added multiple screenshot upload support
- `app.py` — refactored config paths, helpers, Project_data location, and endpoints to use local project root
- `.gitignore` — added tui_config.json to ignored files
- `md/PROBLEMS_AND_FIXES.md` — logged bugs and solutions
- `md/RECENT.md` — logged development session

---

## [2026-07-09] - Prevent Redundant Config Saves & Relocate System Prompts to Config File
**What We Accomplished:**
- Prevented `tui_config.json` from showing as modified in Git when working on the project without changing settings.
- Added a layout validation check in `saveTerminalLayoutState` in `templates/index.html` to avoid POSTing layout changes if the active project's layout is identical to the current configuration.
- Updated `set_config_val` in `app.py` to compare new configurations with the cached values (`_CONFIG_CACHE`), skipping disk I/O when configuration contents are unchanged.
- Untracked `tui_config.json` globally in Git using `git rm --cached` so that local updates are completely ignored by Git while retaining the local configuration file.
- Relocated AI system prompts, the active system prompt ID selection, and system prompt button styles from browser `localStorage` to the consolidated `tui_config.json` configuration file.
- Created GET/POST backend endpoints in `app.py` (`/api/system-prompts`, `/api/active-system-prompt-id`, and `/api/system-prompt-btn-style`) to read and write these settings.
- Updated the frontend JavaScript in `templates/index.html` to fetch configuration state from the server on page load and maintain the state in memory, with auto-migration from `localStorage` to `tui_config.json` if the server config is empty.

**Files Modified:**
- `templates/index.html` — updated `saveTerminalLayoutState()`, prompt storage helpers, dropdown population, and Copilot submission logic
- `app.py` — updated `set_config_val()` and added prompt config API endpoints
- `md/PROBLEMS_AND_FIXES.md` — documented problem and fix details
- `md/RECENT.md` — updated recent development logs

