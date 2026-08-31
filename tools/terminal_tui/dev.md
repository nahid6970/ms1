# Terminal TUI - Developer Guide

> Multi-Workspace Terminal Dashboard — a web-based terminal app with split panes, git integration, file explorer, and mobile controls.

---

## Quick Start

```bash
# Requirements: Python 3.x, Windows (WinPTY)
pip install flask flask-socketio winpty

# Run
python app.py

# Access
# Local:   http://127.0.0.1:5577/
# Network: http://<local_ip>:5577/
```

---

## Project Structure

```
terminal_tui/
├── app.py                          # Flask server — all REST API + WebSocket handlers
├── templates/
│   └── index.html                  # Single-page frontend (HTML + CSS + JS inline)
├── static/
│   └── favicon.png
├── Project_data/                   # Auto-created per workspace
│   └── <workspace_name>/
│       ├── profile.ps1             # Custom PowerShell profile
│       └── history.txt             # Command history
├── dev.md                          # ← You are here
├── md/
│   ├── AI_CONTEXT.md               # Stable project brief for AI handoff
│   ├── RECENT.md                   # Development session log (full history)
│   ├── FEATURES.md                 # Feature specifications & status
│   ├── PROBLEMS_AND_FIXES.md       # Bug tracking & solutions
│   ├── UI_UX.md                    # Design system & component patterns
│   └── ARCHITECTURE.md             # Detailed architecture (API, config, WebSocket)
├── app.log                         # Server logs
└── .gitignore
```

**External config:** `C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\projects.json`

---

## Documentation Index

| File | Purpose | When to Read |
|------|---------|-------------|
| [AI_CONTEXT.md](md/AI_CONTEXT.md) | Quick project brief for AI agents | Start of any AI session |
| [RECENT.md](md/RECENT.md) | Full development history | Continuing previous work |
| [FEATURES.md](md/FEATURES.md) | All features with status & implementation details | Adding/modifying features |
| [PROBLEMS_AND_FIXES.md](md/PROBLEMS_AND_FIXES.md) | Bug log with root causes | Debugging similar issues |
| [UI_UX.md](md/UI_UX.md) | Design system, colors, component patterns | UI work |
| [ARCHITECTURE.md](md/ARCHITECTURE.md) | Full API reference, config format, WebSocket protocol | Backend/integration work |

---

## Architecture Overview

**Stack:** Python Flask + Vanilla JS + Xterm.js + WinPTY + Socket.IO

- **Backend** (`app.py`): REST API for workspace/git/file management + Socket.IO for terminal I/O
- **Frontend** (`index.html`): ~8700-line single-page app, no build step. All CSS/JS inline.
- **Terminal**: WinPTY spawns PowerShell per pane. Socket.IO namespace `/pty` handles bidirectional I/O.
- **Storage**: `projects.json` (server-side) + `localStorage` (client-side UI state)

---

## Development Workflow

### Adding a Feature
1. Add HTML (modal/panel/button) to `templates/index.html`
2. Add JS functions in the `<script>` section
3. Add backend API route in `app.py` if needed
4. Reload browser — no build step
5. Update `md/FEATURES.md` with the new feature
6. Log the session in `md/RECENT.md`

### Fixing a Bug
1. Identify and fix the issue
2. Document in `md/PROBLEMS_AND_FIXES.md` with root cause
3. Log in `md/RECENT.md`

### Code Patterns
- **Modals**: `.modal-overlay` + `.modal-content` + `.show` class toggle
- **Card selections**: Grid of clickable cards (see split-select-modal pattern)
- **Status bar buttons**: `.sbicon-btn` class with SVG icons
- **Explorer actions**: Hover-reveal with `opacity` toggle on `actionsContainer`
- **Git commands**: Always resolve `git_root` first, use `creationflags=0x08000000` on Windows
- **PowerShell wrapping**: Use `-EncodedCommand` with Base64 for complex commands

---

## Environment

| Setting | Value |
|---------|-------|
| Port | `5577` (hardcoded in `app.py`) |
| Debug mode | Set `TERMINAL_TUI_DEBUG=1` env var |
| Config file | `C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\projects.json` |
| Temp images | `C:\Users\nahid\AppData\Local\Temp\screenshot_temp` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Terminal not connecting | Check PowerShell in PATH, check `app.log` for PTY errors |
| Git commands fail | Ensure folder is in a git repo, check git in PATH |
| Layout not saving | Check `projects.json` is writable |
| Custom buttons missing | Check localStorage quota, key format: `custom-btns-<name>` |
| PowerShell syntax errors | Use `-EncodedCommand` with Base64 — see PROBLEMS_AND_FIXES.md |
