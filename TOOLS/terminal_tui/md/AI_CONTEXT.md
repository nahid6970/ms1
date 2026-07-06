# Terminal TUI - AI Context / Project Brief

> Short, stable summary for AI handoff. Update only when the project shape changes.

## What It Is
A **web-based multi-workspace terminal dashboard** for Windows. Each workspace maps to a project folder with a persistent PowerShell session, advanced git integration, split panes, mobile controls, and a full-featured file explorer.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Python 3 — Flask + Flask-SocketIO |
| Frontend | Vanilla JS — Single-page `templates/index.html` |
| Terminal | Xterm.js (rendering) + WinPTY (Windows PTY) |
| Real-time | Socket.IO (namespace `/pty`) |
| Storage | `projects.json` (server) + `localStorage` (client) |

## Entry Points
- **`app.py`** — Flask server, all REST API routes, WebSocket handlers, terminal session management. Runs on port `5577`.
- **`templates/index.html`** — Entire frontend SPA (~8700 lines). All JS/CSS is inline. No build step.
- **`projects.json`** — Located at `C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\projects.json`. Stores workspace configs, bookmarks, themes, layouts.
- **`Project_data/<workspace>/`** — Per-workspace PowerShell profile (`profile.ps1`) and command history (`history.txt`).

## Critical Invariants
1. **Terminal sessions** are keyed as `<project>` (main) or `<project>::<pane-id>` (splits) in the `active_sessions` dict.
2. **PowerShell profiles** are auto-regenerated on session start. User customizations are preserved below the `# Add your custom project aliases...` marker.
3. **Git commands** resolve `git_root` via `git rev-parse --show-toplevel` and use `pathspec` for the workspace subfolder. Always use `creationflags=0x08000000` on Windows to hide console windows.
4. **All modals** use `.modal-overlay` + `.modal-content` + `.classList.add('show')` / `.remove('show')` pattern.
5. **Status bar buttons** use the `.sbicon-btn` class with inline SVG icons.
6. **File explorer** actions (run, view, delete) show on hover via an `actionsContainer` with `opacity` toggle.

## What Not to Break
- The PowerShell profile regeneration logic (system section + user customization marker).
- The `splitTerminal()` function — it handles all pane creation/layout management.
- The `projects.json` read/write cycle — many routes read, modify, and write back.
- Socket.IO namespace `/pty` — terminal I/O depends on this.

## Common Gotchas
- **PowerShell special characters**: When wrapping commands for execution, use `-EncodedCommand` with Base64 to avoid parsing issues with `$?`, quotes, etc.
- **File paths**: Always use `os.path.normpath()` and validate with `.startswith(base_path)` to prevent path traversal.
- **Frontend is one huge file**: `index.html` contains all HTML, CSS, and JS inline. Search by function name or HTML ID, not by file.
- **Port 5577** is hardcoded in `app.py`.

## Preferred Workflow
1. **New features**: Add HTML (modal/UI) → Add JS functions → Add backend API route if needed.
2. **Bug fixes**: Document in `md/PROBLEMS_AND_FIXES.md` with root cause.
3. **Always test** by reloading the browser — no build step needed.
