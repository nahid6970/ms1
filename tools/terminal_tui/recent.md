# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **[2026-10-11] Workspace Management + Git Init + Git Status + UX Polish** (`app.py`, `templates/index.html`):
    * Sidebar search box has a `«` close button on the left (white bg, black text, 42px) — collapse sidebar without moving mouse.
    * Git init modal for non-git projects: ⎇ Init git status bar button → standalone modal → `git init` + commit + push. Push-fail shows Create on GitHub + Push now.
    * Delete workspace toolbar button (🗑): checkbox modal for entry / Project_data / project folder. `wait=True` before `rmtree`.
    * Duplicate modal: styled + Empty folder radio option. Toast during project switch.
    * Missing workspace folder dialog on click: recreate or delete.
    * Git status: 5 → 3 processes/scan, cache TTL 30s → 5s.

* **[2026-10-10] Code Merger UX Improvements** (`app.py`, `templates/index.html`):
    * Generate Prompt on empty folders. Clipboard `execCommand` fallback on HTTP. Merge error detail + Copy all errors. Removed .bak.

# Critical Context
* Sidebar close button is inside the search input (left side, `«`) — calls `toggleSidebar()`.
* Git init modal (`git-init-modal`) is a standalone overlay, NOT inside the git commit modal.
* Delete workspace uses `kill_sessions(..., wait=True)` before `rmtree` — required on Windows.
* Git status: 3 processes/scan (rev-parse+branch combined, single diff HEAD), 5s cache TTL, coalescing lock.
* File explorer paste uses `term.paste()` — clipboard write in `try/catch` (HTTP safe).
* Code merger: no `.bak`, error `detail` has `anchor_text` + `closest_match`, clipboard has `execCommand` fallback.
* AI copilot dynamic model list fetched live; hidden models excluded from git commit suggestion dropdown.

# Pending Task
None.
