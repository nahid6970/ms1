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

## [2026-07-08] - Mobile Overlay Bug Fix & Multiple Screenshot Upload
**What We Accomplished:**
- Identified and fixed mobile layout rendering bug where the top header and bottom status bar disappeared or were covered by a black/blurry layer.
- Root Cause: Multiple hidden `.modal-overlay` elements with high z-index (3000) and `backdrop-filter: blur(8px)` remained in the layout (`display: flex`) and triggered mobile GPU rendering/compositing bugs, rendering them opaque.
- Solution: Updated `.modal-overlay` CSS to use `visibility: hidden;` and transitioned it along with `opacity` to completely exclude inactive modals from the rendering tree.
- Resolved screenshot upload limitation where only one image could be selected/uploaded at a time.
- Added `multiple` attribute to `screenshot-file-input` and updated JS handler to upload files concurrently using `Promise.all` and join the resulting paths with spaces.
- Updated documentation (`md/PROBLEMS_AND_FIXES.md` and `md/RECENT.md`).

**Files Modified:**
- `templates/index.html` — updated modal-overlay transition/visibility and added multiple screenshot upload support
- `md/PROBLEMS_AND_FIXES.md` — logged bugs and solutions
- `md/RECENT.md` — logged development session
