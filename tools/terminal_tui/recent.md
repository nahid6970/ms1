# Project DNA
A Flask/Socket.IO-based terminal TUI using Xterm.js for multi-pane workspace management. It utilizes a unified `tui_config.json` for persistent configuration and user-defined custom button shortcuts.

# Latest Implementation
* **[2026-10-10] Code Merger UX Improvements** (`app.py`, `templates/index.html`):
    * Generate Prompt now works on empty folders — no longer blocks when zero files are checked.
    * All clipboard operations (`cmCopyPrompt`, `copyFileViewerContent`) now use `execCommand('copy')` fallback on HTTP.
    * Merge errors enriched with detail: `_find_closest_line` finds nearest match in file with line number and context snippet. Error results include `anchor_text`, `anchor_lines`, `closest_match`.
    * Results display redesigned: all-pass → single ✅ summary; any failure → plain text error block with **📋 Copy all errors** button (paste into AI chat).
    * Removed `.bak` backup checkbox — no more backup files created on apply.

* **[2026-10-10] Fix File Explorer Path Paste + Missing Workspace Folder Dialog** (`templates/index.html`, `app.py`):
    * File explorer click broken on HTTP — `navigator.clipboard` undefined throws before `term.paste()`. Fixed with try/catch + switched to `term.paste()`.
    * Missing-folder dialog on workspace click: `GET /api/project/<project>/path-check` + `POST /api/project/<project>/recreate-path`. Dialog offers 📁 Recreate or 🗑 Delete.

# Critical Context
* Custom buttons and their order are persisted globally in `tui_config.json`.
* `refreshAllPaneCustomButtons()` handles the DOM logic by clearing existing buttons and re-restoring them, ensuring style/order updates are applied without full page reloads.
* Image paste is handled in the pane-level capture-phase handler — NOT the document-level handler — because xterm.js swallows paste events before they bubble.
* Pasted image paths are sent **without** shell quoting — raw `result.path` only. AI tools and PTY writes receive the path as a plain string.
* File explorer path paste uses `term.paste(relativePath)` — NOT direct `socket.emit`. Clipboard copy is wrapped in `try/catch` (fails silently on HTTP).
* Code merger: no `.bak` backups. Error results include `detail` with `anchor_text` + `closest_match`. All clipboard ops have `execCommand` fallback for HTTP.
* AI copilot dynamic model list is fetched live; hidden models are excluded from the git-modal commit-suggestion dropdown.

# Pending Task
None.
