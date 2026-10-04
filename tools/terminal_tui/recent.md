# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **[2026-10-04] Fix Image Paste Broken by Terminal Paste Refactor** (`templates/index.html`):
    * Moved image-paste detection into the pane-level capture-phase `paste` handler (fires before xterm.js).
    * Root cause: xterm.js calls `stopPropagation()` internally, preventing the `document`-level image-paste handler from firing when a terminal pane was focused.
    * Fix: capture-phase handler now checks for image clipboard items first — calls `preventDefault()`/`stopPropagation()`, uploads to `/api/session/${activeProject}/paste-image`, sends path via `sendTerminalPasteText()`.
    * Text paste behavior and global `document` paste fallback remain unchanged.

* **[2026-10-03] AI Suggest Commit Message + Model Tester Improvements** (`app.py`, `templates/index.html`):
    * Added `✨` button in git modal to auto-generate a conventional commit message via Gemini.
    * Separate Gemini model dropdown in git modal, persisted to `localStorage['git-ai-commit-model']`.
    * Backend `POST /api/project/<project>/git/suggest-commit` — diffs staged → unstaged → status, truncates to 12 000 chars, calls Gemini REST.
    * Model Batch Tester: auto-hides failed models after test; auto-classifies speed from elapsed time (< 3 s Fast, 3–8 s Medium, ≥ 8 s Slow); syncs speed tags to AI copilot dropdown after batch.

# Critical Context
* Custom buttons and their order are persisted globally in `tui_config.json`.
* `refreshAllPaneCustomButtons()` handles the DOM logic by clearing existing buttons and re-restoring them, ensuring style/order updates are applied without full page reloads.
* Image paste is handled in the pane-level capture-phase handler — NOT the document-level handler — because xterm.js swallows paste events before they bubble.
* AI copilot dynamic model list is fetched live; hidden models are excluded from the git-modal commit-suggestion dropdown.

# Pending Task
None.
