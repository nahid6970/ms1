# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **[2026-10-10] Fix File Explorer Path Paste + Missing Workspace Folder Dialog** (`templates/index.html`, `app.py`):
    * File explorer click was broken on HTTP — `navigator.clipboard` is `undefined` on insecure origins, causing an uncaught `TypeError` that killed the onclick before `term.paste()` was reached. Fixed by wrapping clipboard write in `try/catch` and switching from old `socket.emit('pty-input')` to `term.paste()`.
    * Added missing-folder detection on workspace click: `GET /api/project/<project>/path-check` checks if the folder exists; if not, a dialog offers **📁 Recreate** (creates the directory) or **🗑 Delete** (removes the workspace entry). Only proceeds to connect after recreate.

# Critical Context
* Custom buttons and their order are persisted globally in `tui_config.json`.
* `refreshAllPaneCustomButtons()` handles the DOM logic by clearing existing buttons and re-restoring them, ensuring style/order updates are applied without full page reloads.
* Image paste is handled in the pane-level capture-phase handler — NOT the document-level handler — because xterm.js swallows paste events before they bubble.
* Pasted image paths are sent **without** shell quoting — raw `result.path` only. AI tools and PTY writes receive the path as a plain string.
* File explorer path paste uses `term.paste(relativePath)` — NOT direct `socket.emit`. Clipboard copy is wrapped in `try/catch` (fails silently on HTTP).
* AI copilot dynamic model list is fetched live; hidden models are excluded from the git-modal commit-suggestion dropdown.

# Pending Task
None.
