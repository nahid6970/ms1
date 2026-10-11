# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

## [2026-10-11] Sidebar Flash on Refresh
- The saved collapsed state and sidebar width are now applied before first paint, preventing the sidebar from flashing open during refresh.
- `templates/index.html`

# Latest Implementation
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

# Pending Task
None.
