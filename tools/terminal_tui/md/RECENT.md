# Recent Development Log

All sessions recorded here — no archiving, full history in one place.
Read this file only when relevant to the current task. When reading, reference the last 5 sessions max.

---

## [2026-10-04] - Remove Quote-Wrapping from Pasted Image Paths

### Problem
All four image paste code paths (pane-level capture handler, document-level paste handler, drag-drop handler, screenshot file select) wrapped the returned path in double quotes: `` `"${result.path}"` ``. This caused AI CLI tools (Kiro, Gemini, Codex) to receive literal `"` characters as part of the path string, e.g. `"C:/Users/nahid/AppData/Local/Temp/screenshot_temp/pasted_image_20261004_230001.png"`.

### Fix
Removed all quote-wrapping — paths are now sent as-is (`result.path`). The temp folder filenames never contain spaces, so shell quoting was never necessary. AI tools handle raw paths directly without shell quoting.

**Files Modified:**
- `templates/index.html` — pane capture handler, document paste handler, `uploadDroppedImage()`, `handleScreenshotFileSelect()`

---

## [2026-10-04] - Fix Image Paste Broken by Terminal Paste Refactor

### Root Cause
The 2026-09-23 "Prevent Duplicate Terminal Paste" refactor added a capture-phase `paste` listener on each `paneDiv`. This listener called `e.stopPropagation()` for text paste — but xterm.js itself also calls `stopPropagation()` internally on its textarea's paste event. The result: when a terminal pane was focused, the `document`-level image-paste handler (`document.addEventListener('paste', ...)`) never fired because the event was consumed by xterm.js before it could bubble to the document.

### Fix
Moved the image-paste detection logic into the pane-level **capture-phase** handler (which fires before xterm.js). When the clipboard contains an image type:
1. `preventDefault()` and `stopPropagation()` are called immediately.
2. The image is uploaded to `/api/session/${activeProject}/paste-image`.
3. The returned path is sent to the active terminal via `sendTerminalPasteText(pathToSend)` (uses `paneTerm.paste()`, targeting the correct pane directly).

Text paste behavior is unchanged. The global `document` paste handler remains as a fallback for non-terminal contexts (e.g., if paste happens while no pane is focused).

**Files Modified:**
- `templates/index.html` — pane-level paste listener
- `md/RECENT.md`

---

## [2026-10-03] - AI Suggest Commit Message + Model Tester Auto-Hide & Speed

### AI Suggest Commit Message Button (git modal)
- Added `✨` icon button in the git modal commit message label row (top-right of the textarea)
- Added independent Gemini model `<select>` dropdown to the left of the button — separate from the AI copilot model selector
- Dropdown populated from `DYNAMIC_AI_MODELS['gemini']` (same live list as AI copilot); falls back to 5 hardcoded models if not yet loaded
- Always fires a background fetch to Gemini models API on git modal open to keep list fresh
- Respects the hidden-models list — models toggled hidden in AI copilot are excluded from the dropdown
- Selection persisted to `localStorage['git-ai-commit-model']`; defaults to AI copilot's last selected Gemini model
- Backend route `POST /api/project/<project>/git/suggest-commit` in `app.py`:
  - Runs `git diff --staged` first, falls back to `git diff`, then `git status --short`
  - Truncates diff to 12,000 chars to stay within token limits
  - Calls Gemini REST API directly with a conventional commits prompt
  - Returns `{"suggestion": "..."}` or `{"error": "..."}`
- Button shows spinning SVG while loading, fills textarea on success, shows green status tick
- `populateGitAIModelDropdown()` also hooked into `fetchDynamicModels` completion so git modal dropdown updates live when AI copilot fetches models

### Model Tester — Auto-hide Failed Models
- After each failed model test (HTTP error or network exception), automatically toggles that model to hidden via `_toggleTesterModelVisibility()`
- Skips models already hidden (no double-toggle)
- Shows count at end: `· N failed model(s) auto-hidden` appended to status line

### Model Tester — Auto-save Speed from Elapsed Time
- After each successful model test, classifies response time and saves to `ai-model-speeds`:
  - < 3 s → **Fast**
  - 3–8 s → **Medium**
  - ≥ 8 s → **Slow**
- Speed select on the card reflects real measured speed immediately after test
- `syncAIModelDropdown()` called after batch completes to update speed tags in AI copilot dropdown

**Files Modified:**
- `app.py` — added `POST /api/project/<project>/git/suggest-commit` route
- `templates/index.html` — git modal HTML, `populateGitAIModelDropdown()`, `suggestGitCommitMessage()`, `runModelBatchTest()` auto-hide + auto-speed logic, `fetchDynamicModels` hook, `@keyframes spin` CSS
- `md/FEATURES.md`
- `md/RECENT.md`

---

## [2026-10-02] - Fix Git Status Stale After Commit
**What We Accomplished:**
- After committing, the git status badge in the status bar kept showing the old "dirty" state for several seconds (up to the 30-second cache window).
- Root cause: the git status cache was never invalidated after a successful commit, so `updateStatsMonitor()` (called immediately after commit) returned the stale cached result.
- Added `invalidate_git_status_cache(path)` helper and called it in `api_git_commit` right after a successful `git commit`. The next stats poll now runs a fresh scan and returns the clean state immediately.

**Files Modified:**
- `app.py`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---


## [2026-10-01] - Preserve Multiline Paste Semantics in Terminal
**What We Accomplished:**
- Routed clipboard text through xterm.js `Terminal.paste()` instead of writing raw text directly to the PTY.
- Retained the existing Ctrl+V, Shift+Insert, image-paste, and duplicate-paste handling while allowing xterm.js to apply paste transformations.

**Files Modified:**
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`

---

## [2026-09-26] - Duplicate Workspace into Numbered Copy
**What We Accomplished:**
- Added an active-workspace duplicate button that creates the next available `-2`, `-3`, … sibling copy.
- Copies files while excluding `.git`, virtual environments, dependency folders, caches, and common build output.
- Carries over category, theme, and bookmarks, starts with a fresh terminal layout, and switches to the copy.

**Files Modified:**
- `app.py`
- `templates/index.html`
- `md/FEATURES.md`
- `md/ARCHITECTURE.md`
- `md/UI_UX.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-25] - Make Git Monitor Path Matching Case-Insensitive
**What We Accomplished:**
- Made workspace Git status, diff counts, and changed-file listing match project pathspecs without depending on directory-name casing.
- Covered the `Testing` to `testing` path case for the `mypygui` workspace.

**Files Modified:**
- `app.py`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-24] - Add Bookmark Command Colors
**What We Accomplished:**
- Added an optional color picker to the bookmark edit/add dialog.
- Kept the controls on one line and added direct hex input such as `#ff55ff`.
- Persisted validated six-digit hex colors with bookmark records.
- Applied custom colors to bookmark display names while retaining the default theme color when disabled.

**Files Modified:**
- `app.py`
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-24] - Allow Dragging Global Bookmarks
**What We Accomplished:**
- Added drag handles to global bookmarks in the merged bookmark list.
- Added a persisted merged display order so global and local bookmarks can be dragged across workspace boundaries.
- Kept each bookmark's source workspace and ownership unchanged.

**Files Modified:**
- `templates/index.html`
- `app.py`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-24] - Default Terminal Tabs With Plus Button
**What We Accomplished:**
- Made the tabbed terminal layout the default, including the single-terminal state.
- Added a `+` tab that opens another terminal tab through the existing tabbed split flow.
- Normalized old one-pane `split-right` layouts so they show the tab bar.

**Files Modified:**
- `templates/index.html`
- `md/FEATURES.md`
- `md/UI_UX.md`
- `md/ARCHITECTURE.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-24] - Stop Duplicate Ctrl+V Paste
**What We Accomplished:**
- Routed Ctrl+V terminal paste through the browser paste event with a delayed plain-text fallback.
- Added a short same-text dedupe guard shared by Ctrl+V, fallback, and Shift+Insert paste paths.

**Files Modified:**
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-22] - Add Restart Menu and F5 Page Refresh
**What We Accomplished:**
- Changed the global restart icon to open separate “Restart app” and “Refresh page” actions.
- Added a global F5 keyboard handler that refreshes the current page.
- Kept the existing session reset and backend restart flow unchanged.

**Files Modified:**
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-24] - Fix Text Paste in AI CLI Terminals
**What We Accomplished:**
- Prevented Ctrl+V from reaching AI CLI tools as their image-paste shortcut.
- Restored single plain-text clipboard insertion through the frontend PTY handler.

**Files Modified:**
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-23] - Document Clipboard and Refresh Behavior
**What We Accomplished:**
- Documented the single-event terminal paste path that prevents duplicate Ctrl+V insertion.
- Documented Shift+Insert paste and the larger server/xterm scrollback limits used after refresh.

**Files Modified:**
- `md/FEATURES.md`
- `md/ARCHITECTURE.md`
- `md/UI_UX.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-23] - Prevent Duplicate Terminal Paste
**What We Accomplished:**
- Routed Ctrl+V through a single capture-phase paste handler before xterm.js.
- Kept Shift+Insert clipboard support and prevented duplicate terminal input.

**Files Modified:**
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-23] - Preserve More Terminal Output Across Refresh
**What We Accomplished:**
- Increased server-side PTY history retention from 100,000 to 500,000 characters.
- Increased xterm.js scrollback to 20,000 rows so long AI/tool transcripts remain available after browser refresh.

**Files Modified:**
- `app.py`
- `templates/index.html`
- `md/ARCHITECTURE.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-23] - Fix Quick Open Category Tag Alignment
**What We Accomplished:**
- Fixed F1 palette category tags so they stay beside project names consistently.
- Kept `⌘ 1–9` shortcut labels aligned to the right without affecting tag placement.

**Files Modified:**
- `templates/index.html`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-23] - Refresh Documentation for F1 Palette
**What We Accomplished:**
- Updated feature, UI/UX, and problem/fix documentation to describe the reference-style F1 command palette.
- Documented project shortcut selection and the compact search/back/result/footer layout.

**Files Modified:**
- `md/FEATURES.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/UI_UX.md`
- `md/RECENT.md`

---

## [2026-09-22] - Match F1 Palette to Quick-Open Reference
**What We Accomplished:**
- Restyled the F1 palette as a compact centered command panel with a dark rounded surface, search/back row, grouped results, and keyboard footer.
- Added compact project rows, shortcut labels, project/command switching, and Ctrl/Cmd+number project selection.

**Files Modified:**
- `templates/index.html`
- `md/UI_UX.md`
- `md/RECENT.md`

---

## [2026-09-22] - Synchronize Keyboard and Quick Open Documentation
**What We Accomplished:**
- Documented F1 Quick Open, F5 refresh, terminal copy/paste behavior, and terminal-focus capture handling.
- Updated architecture, UI/UX, AI context, feature, problem/fix, and recent-session documentation.

**Files Modified:**
- `md/ARCHITECTURE.md`
- `md/UI_UX.md`
- `md/AI_CONTEXT.md`
- `md/FEATURES.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-09-22] - Fix Terminal-Focused Shortcuts and Clipboard Paste
**What We Accomplished:**
- Captured F1 and F5 before xterm.js so the Quick Open palette and page refresh work with terminal focus.
- Added Ctrl+C copy for selected terminal text while preserving Ctrl+C interrupt behavior with no selection.
- Added Ctrl+V and Shift+Insert clipboard paste into the active terminal pane.

**Files Modified:**
- `templates/index.html`
- `md/FEATURES.md`
- `md/PROBLEMS_AND_FIXES.md`
- `md/RECENT.md`

---

## [2026-08-31] - Remove Backend Health Check Auto-Close Feature
**What We Accomplished:**
- Identified a bug where pressing Ctrl+C in a workspace terminal pane (to cancel an AI agent or command) could accidentally close the browser tab.
- Root cause: `startBackendHealthCheck()` polled `/api/projects` every second with an 800ms timeout and only needed 2 consecutive failures to trigger the auto-close. A brief Flask event loop spike from PTY/subprocess cleanup was enough to fire false positives.
- Removed `showConnectionLostOverlay()` and `startBackendHealthCheck()` functions entirely.
- Removed the `startBackendHealthCheck()` call from `window.onload`.
- The tab will no longer auto-close when the server stops or restarts — users must close it manually.

**Files Modified:**
- `templates/index.html` — removed both functions and the `window.onload` call

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

# [2026-09-30] - Keep Terminal Tabs Session-Only
- Stopped writing terminal layout and pane IDs to workspace JSON.
- Workspace startup now always creates one default terminal tab, avoiding restoration of empty tabs after an app restart.
- Updated architecture and feature documentation to describe session-only tabs.
# [2026-09-30] - Notify When a Background Tab Finishes a Command
- Added a hidden PowerShell prompt marker and use it to detect command completion in terminal output.
- Show an amber indicator on unfocused terminal tabs after command completion; selecting the tab clears it.
- Filter the marker from terminal display output.

# [2026-09-30] - Restore Terminal Tabs After Browser Refresh
- Save workspace pane IDs and the selected pane in browser `localStorage`, not workspace JSON.
- Reconnect to the same sessions after a browser refresh and clear the saved state from Reset All Sessions.
- Play a brief notification sound when an unfocused tab first receives its completion indicator.

# [2026-10-01] - Stop Closed Pane Processes and Throttle Git Status
- Cache and coalesce Git status scans to reduce repeated Git process creation.
- Closing a tab now removes its PTY session and child process tree; bound process termination and avoid holding the session registry lock during cleanup.
- Prevent overlapping stats polls and stale workspace restores from overwriting the active workspace.
