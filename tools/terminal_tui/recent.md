# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **[2026-10-11] Workspace Management + Git Init + Git Status Optimization** (`app.py`, `templates/index.html`):
    * Missing workspace folder dialog on click: path-check API + recreate/delete options.
    * Git init modal for non-git projects: ⎇ Init git status bar button, standalone modal, `git init` + initial commit + remote + push. Push-fail shows Create on GitHub link + Push now button.
    * Delete workspace button (🗑) in toolbar: styled checkbox modal — remove entry, delete Project_data, optionally delete project folder. Uses `wait=True` before `rmtree` to avoid Windows file handle issues.
    * Duplicate workspace modal: replaced `confirm()` with styled modal + Empty folder radio option.
    * Git status optimized: 5 → 3 git processes per scan, cache TTL 30s → 5s.

* **[2026-10-10] Code Merger UX Improvements** (`app.py`, `templates/index.html`):
    * Generate Prompt works on empty folders. All clipboard ops use `execCommand` fallback on HTTP.
    * Merge errors enriched with closest-match detail. Results: all-pass summary vs error text block + Copy all errors. Removed .bak backups.

# Critical Context
* Custom buttons persisted in `tui_config.json`. `refreshAllPaneCustomButtons()` handles DOM updates.
* Image paste in pane-level capture-phase handler (xterm.js swallows bubble). Paths sent without shell quoting.
* File explorer paste uses `term.paste(relativePath)` — clipboard write wrapped in `try/catch` (HTTP safe).
* Code merger: no `.bak` backups. Error `detail` includes `anchor_text` + `closest_match`. Clipboard has `execCommand` fallback.
* Git status: 3 processes per scan, 5s cache TTL, coalescing lock prevents process buildup. `invalidate_git_status_cache` called after all git modal actions.
* Git init modal (`git-init-modal`) is a standalone overlay — NOT embedded in the git commit modal.
* Delete workspace uses `kill_sessions(..., wait=True)` before `rmtree` to avoid Windows holding folder handles.
* AI copilot dynamic model list fetched live; hidden models excluded from git commit suggestion dropdown.

# Pending Task
None.
