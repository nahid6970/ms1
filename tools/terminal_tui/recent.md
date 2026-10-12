# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

## [2026-10-11] Sidebar Flash on Refresh
- The saved collapsed state and sidebar width are now applied before first paint, preventing the sidebar from flashing open during refresh.
- `templates/index.html`

# Latest Implementation

* **[2026-10-12] Workspace Bar** (`templates/index.html`):
    * Slim `#workspace-bar` (34px, `#080c14`) sits between the toolbar and `#terminal-parent` inside `.terminal-container-wrapper`.
    * Shows only running workspaces (`p.is_active`) as chips with colored dot (uses `cardTheme.accentColor`). Active chip is highlighted in blue.
    * Single-click on inactive chip → `selectProject()`. Double-click → `stopProjectSession(name, { silent: true })` (no confirm dialog).
    * After killing a session, automatically focuses the last previously visited running workspace via `wsfocusHistory[]` stack, or falls back to homepage.
    * `updateWorkspaceBar()` is called from `restoreTerminalLayout` and `stopProjectSession`.
    * Togglable via Settings → Layout tab → "Show Workspace Bar" checkbox (`localStorage` key `show-workspace-bar`, default `true`).

* **[2026-10-12] Create Folder on Add Workspace** (`app.py`, `templates/index.html`):
    * New `/api/mkdir` endpoint: calls `os.makedirs(path, exist_ok=True)`.
    * When "Add Workspace" fails with "does not exist" error, a dashed "📁 Create Folder & Add Workspace" button appears below the error.
    * Clicking it calls `/api/mkdir`, shows a spinner, then auto-submits the form on success.
    * `#create-folder-hint` div hidden by default, reset on `openAddModal()`.

* **[2026-10-11] Switch Terminal to pwsh (PowerShell Core)** (`app.py`):
    * Changed `TerminalSession` from `powershell.exe` to `pwsh.exe`.
    * Uses `-EncodedCommand` (Base64 UTF-16LE) to dot-source the workspace profile — avoids all quoting/path issues.
    * Removed `-NoProfile` so the user's default `$PROFILE` loads first, then the workspace profile runs on top (overrides `cd`, history path, prompt).
    * Startup order: `$PROFILE` (aliases, oh-my-posh, etc.) → workspace profile (PROJECT_ROOT_PATH, cd, history, prompt marker).

* **[2026-10-11] Workspace Management + Git Init + Git Status + UX Polish** (`app.py`, `templates/index.html`):
    * Sidebar search box `«` close button (left side, white bg, 42px).
    * Git init modal for non-git projects. Delete workspace toolbar button. Duplicate modal + Empty folder option.
    * Missing workspace folder dialog. Git status 5→3 processes/scan, cache TTL 30s→5s.

* **[2026-10-10] Code Merger UX Improvements** (`app.py`, `templates/index.html`):
    * Generate Prompt on empty folders. Clipboard `execCommand` fallback. Merge error detail + Copy all errors. Removed .bak.

# Critical Context
* Terminal uses `pwsh.exe` with `-EncodedCommand` (no `-NoProfile`). Default `$PROFILE` loads first, workspace profile second.
* Workspace profile sets: `$PROJECT_ROOT_PATH`, custom `cd` (bare cd → project root), `HistorySavePath` per workspace, custom prompt + ttui prompt marker.
* Sidebar close button is inside the search input (left, `«`) — calls `toggleSidebar()`.
* Git init modal (`git-init-modal`) is a standalone overlay, NOT inside the git commit modal.
* Delete workspace uses `kill_sessions(..., wait=True)` before `rmtree`.
* Git status: 3 processes/scan, 5s cache TTL, coalescing lock.
* File explorer paste uses `term.paste()` — clipboard write in `try/catch` (HTTP safe).
* Code merger: no `.bak`, error `detail` has `anchor_text` + `closest_match`, clipboard has `execCommand` fallback.
* `stopProjectSession(name, options={})` — pass `{ silent: true }` to skip the confirm dialog.
* `wsfocusHistory[]` — array tracking workspace focus order; used to auto-focus last visited workspace after a session is killed.
* Workspace bar chips: single-click = switch, double-click = kill (silent). Bar hidden when `localStorage['show-workspace-bar'] === 'false'`.
* `/api/mkdir` endpoint creates directories via `os.makedirs(path, exist_ok=True)`. Requires server restart to activate.

# Pending Task
None.
