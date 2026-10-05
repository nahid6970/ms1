# Terminal TUI - Multi-Workspace Terminal Dashboard

A web-based terminal dashboard application that provides multiple persistent PowerShell workspace sessions with advanced git integration, customizable UI, and mobile-friendly controls.

## Architecture Overview

**Stack:**
- **Backend**: Python Flask + Flask-SocketIO
- **Frontend**: Vanilla JavaScript + Xterm.js
- **Terminal**: WinPTY for Windows PowerShell spawning
- **Real-time**: Socket.IO for bidirectional terminal I/O
- **Storage**: JSON file-based config + localStorage for UI state

**Core Components:**
1. `app.py` - Flask server with REST API and WebSocket handlers
2. `templates/index.html` - Single-page app with terminal UI
3. WinPTY - Creates persistent PowerShell sessions per workspace
4. Custom PowerShell profiles per workspace (stored in `Project_data/`)

---

## Key Features

### 1. Workspace Management
- **Multiple workspaces**: Each workspace = a project folder + persistent terminal session
- **Custom PowerShell profiles**: Each workspace has its own profile.ps1 with:
  - Custom prompt showing workspace name
  - `cd` command defaults to project root
  - Project-specific aliases and environment variables
  - Per-project command history
- **Categories**: Group workspaces by category
- **Pin/unpin**: Keep important workspaces at the top
- **Drag-to-reorder**: Custom ordering persists in `projects.json`

### 2. Terminal Features
- **Split panes**: Multiple terminal panes per workspace
- **Layouts**: Save/restore split layouts (default tabs, vertical, horizontal, quad)
- **Font customization**: Per-workspace font family and size
- **Theme customization**: Per-workspace terminal colors + workspace card colors
- **Search in terminal**: Ctrl+F to search terminal output
- **Copy/paste**: Ctrl+C copies selected terminal text; Ctrl+C with no selection remains the terminal interrupt; Ctrl+V and Shift+Insert paste clipboard text into the active pane
- **Refresh recovery**: Terminal sessions retain up to 500,000 characters server-side and xterm panes restore up to 20,000 scrollback rows after browser reconnects.
- **Paste de-duplication**: Ctrl+V is handled by one capture-phase paste listener before xterm.js; Shift+Insert uses the explicit clipboard API path.

### 2.1 Global Keyboard Shortcuts
- **F1**: Open the Quick Open palette. Capture-phase handling keeps it available while xterm has focus.
- **F5**: Refresh the current page. Capture-phase handling prevents xterm/browser focus from swallowing the shortcut.
- **Ctrl+F**: Open terminal output search when a terminal pane is focused.
- **Arrow Up/Down + Enter**: Navigate and select items in the F1 palette.

### 3. Mobile Controls (Right Side Buttons)
Buttons appear on the right side of each terminal pane:
- **× (top)**: Close pane
- **ESC**: Send escape key
- **^C**: Send Ctrl+C (interrupt)
- **▲**: Scroll up
- **▼**: Scroll down
- **◀**: Move cursor left
- **▶**: Move cursor right
- **+ (green)**: Add custom buttons
- **[Custom buttons]**: User-defined shortcuts (Tab, Enter, etc.)

Custom buttons:
- Click + to open modal
- Enter label and escape sequence (e.g., `\t` for Tab)
- Saved per project in localStorage
- Auto-restored on workspace load

### 4. Git Integration
Click git info badge in status bar to open Git modal:

**Main Features:**
- View changed files (staged/unstaged/untracked)
- Stage all changes: `git add -A` (includes moved files)
- Commit with message
- Auto-push after commit option
- Discard all uncommitted changes button

**Past Commits (collapsible section):**
- Toggle with › arrow to expand/collapse
- Shows last 10 commits (hash, time, message)
- **Rename** (✏️): Only on HEAD commit - amends commit message
- **Push** (⬆): Only on HEAD commit - pushes to remote
- **Checkout** (⏱): On older commits - time-travel to that commit
  - Puts you in detached HEAD state
  - Shows warning banner with "Return to latest" button
- **Return to latest** (↩): Returns to branch HEAD from detached state

**Backend Routes:**
- `GET /api/project/<project>/git/files` - Changed files
- `POST /api/project/<project>/git/commit` - Commit + push
- `GET /api/project/<project>/git/commits` - Last 10 commits
- `POST /api/project/<project>/git/commit/rename` - Amend HEAD commit
- `POST /api/project/<project>/git/checkout` - Checkout commit
- `POST /api/project/<project>/git/return-branch` - Return to branch
- `POST /api/project/<project>/git/push` - Push to remote
- `POST /api/project/<project>/git/discard` - Discard all changes (`git restore` + `git clean`)

### 5. Bookmarks
- Save frequently used commands per workspace
- Mark as global to show in all workspaces
- Reorder by dragging
- Edit command, name, window title
- Quick execute from dropdown

### 6. Status Monitor
Shows for active workspace:
- CPU usage (all PTY processes)
- Memory usage (RSS)
- Active pane count
- Git info: branch, modifications, staged/unstaged, insertions/deletions

### 7. Scratchpad
- Floating notepad for quick notes
- Auto-saved to localStorage
- Draggable
- Markdown preview

---

## File Structure

```
C:\@delta\ms1\tools\terminal_tui\
├── app.py                          # Flask server
├── templates/
│   └── index.html                  # Single-page frontend
├── static/
│   └── favicon.png
├── app.log                         # Server logs
└── Project_data/                   # Auto-created per workspace
    └── <workspace_name>/
        ├── profile.ps1             # Custom PowerShell profile
        └── history.txt             # PowerShell command history

C:\@delta\msBackups\DataBase\Terminal_Tui_workspace\
├── projects.json                   # Workspace config (name, path, theme, bookmarks, etc.)
└── Project_data/                   # Per-workspace data (same as above)
```

---

## Configuration Files

### projects.json
Stores all workspace metadata:
```json
[
  {
    "name": "MyProject",
    "path": "C:\\path\\to\\project",
    "category": "Work",
    "pinned": false,
    "theme": {
      "background": "#000000",
      "foreground": "#d1d5db",
      "cursor": "#3b82f6",
      "scrollbarColor": "#475569",
      "scrollbarIdleColor": "#2d3748"
    },
    "cardTheme": {
      "bgColor": "#161c26",
      "textColor": "#f1f5f9",
      "pathColor": "#94a3b8",
      "accentColor": "#2563eb"
    },
    "bookmarks": [
      {
        "command": "npm run dev",
        "global": false,
        "name": "Dev Server",
        "windowTitle": ""
      }
    ]
  }
]
```

Terminal pane IDs and the active tab are stored in browser `localStorage`, not `projects.json`. A browser refresh reconnects to those terminal sessions. The Reset All Sessions action clears the saved tab state along with the sessions.

### profile.ps1 (per workspace)
```powershell
# System-managed section (auto-generated)
$global:PROJECT_ROOT_PATH = "C:\path\to\project"
Import-Module PSReadLine -ErrorAction SilentlyContinue
Set-PSReadLineOption -HistorySavePath "C:\path\to\history.txt"

function cd { ... }
function prompt { ... }

# User customization section
# Add your custom aliases, functions, environment variables below:
# Set-Alias ll Get-ChildItem
```

---

## API Endpoints

### Projects
- `GET /api/projects` - List all workspaces
- `POST /api/projects` - Add new workspace
- `POST /api/projects/<project>/duplicate` - Copy workspace files/settings into the next numbered sibling
- `DELETE /api/projects/<project>` - Delete workspace
- `POST /api/projects/customize` - Update workspace settings
- `POST /api/projects/reorder` - Reorder workspace list
- `POST /api/projects/<project>/layout` - Save split layout

### Bookmarks
- `POST /api/projects/<project>/bookmarks` - Add bookmark
- `DELETE /api/projects/<project>/bookmarks/<index>` - Delete bookmark
- `POST /api/projects/<project>/bookmarks/<index>/global` - Toggle global
- `POST /api/projects/<project>/bookmarks/<index>/edit` - Edit bookmark

### Sessions
- `POST /api/session/<project>` - Start/connect terminal session
- `POST /api/session/<project>/stop` - Kill terminal session
- `GET /api/session/<project>/stats` - CPU/memory/git stats
- `POST /api/sessions/reset` - Kill all sessions + reset layouts

### Git (see section 4 above)

### Files
- `GET /api/project/<project>/files` - List directory contents
- `GET /api/project/<project>/file-content` - Read file content (1 MB limit)
- `POST /api/project/<project>/file-write` - Create a new file (errors if exists)
- `POST /api/project/<project>/file-overwrite` - Write file (create or overwrite)
- `POST /api/project/<project>/file-delete` - Delete file or folder
- `POST /api/project/<project>/paste-clipboard` - Paste files from Windows clipboard
- `POST /api/project/<project>/merge-apply` - Parse and apply `@@FILE/@@MODE/@@END` AI response blocks
- `POST /api/images/temp` - Upload temporary image

### Misc
- `GET /api/fonts` - List system fonts
- `POST /api/open-explorer` - Open path in Windows Explorer
- `POST /shutdown` - Shutdown server

---

## Code Merger (Status Bar Feature)

A self-contained AI prompt-prep and response-apply workflow built into the status bar popover.

### Entry point
Click the cyan `⇅` button (`#code-merger-btn`) in `#subprocess-monitor`.

### PREP flow
1. `cmLoadFiles()` — recursively fetches files via `/api/project/<project>/files`, filters through `_cmExcludePatterns` via `cmIsExcluded()`, auto-checks text/code extensions.
2. User checks/unchecks files, optionally adds exclusion patterns, writes a task description.
3. `cmGeneratePrompt()` — fetches each checked file's content via `/api/project/<project>/file-content`, assembles the `@@FILE/@@MODE/@@END` format guide + task + file blocks into `_cmPromptText`.
4. Copy to clipboard via `cmCopyPrompt()`.

### MERGE flow
1. User pastes AI response into `#cm-response-input`.
2. `cmParseResponse()` — client-side parse to preview blocks (no writes).
3. `cmApplyResponse()` — POSTs `{ response, backup }` to `/api/project/<project>/merge-apply`.
4. Backend parses blocks, applies changes with optional `.bak` backups, returns `[{file, status, mode, message}]`.
5. Results rendered as `✅`/`❌` rows with error detail.

### Exclusion pattern matching (`cmIsExcluded`)
- `folder/` → matches any path segment equal to `folder`
- `*.ext` → extension match
- otherwise → substring match on full relative path

---

## WebSocket Handlers (namespace /pty)

```javascript
// Client → Server
socket.emit('join-session', { project, paneId, useRealDirName })
socket.emit('pty-input', { project, paneId, data })
socket.emit('resize', { project, paneId, cols, rows })

// Server → Client
socket.on('pty-output', { data })
socket.on('pty-output', { eof: true })
socket.on('session-ready', { name, paneId, path })
```

---

## LocalStorage Keys

Per-workspace:
- `custom-btns-<project>` - Custom terminal button shortcuts
- `scratchpad-<project>` - Scratchpad content

Global:
- `terminal-font-family` - Font choice
- `terminal-font-size` - Font size
- `use-real-dir-prompt` - Use real dir name in prompt
- `workspaces-order` - Custom workspace order

---

## Running the App

**Requirements:**
- Python 3.x
- Flask, Flask-SocketIO, winpty
- Windows (for WinPTY)

**Start:**
```bash
python app.py
```

**Access:**
- Local: http://127.0.0.1:5577/
- Network: http://<local_ip>:5577/

**Config:**
- Set `TERMINAL_TUI_DEBUG=1` env var to enable debug mode

---

## Code Style & Patterns

### Backend (app.py)
- Flask routes follow RESTful patterns
- All git commands run in `git_root` (repo root) with `pathspec` for workspace subfolder
- `creationflags=0x08000000` on Windows to hide console windows
- Error handling returns JSON with `{"error": "message"}`

### Frontend (index.html)
- No build step - pure vanilla JS
- Xterm.js for terminal rendering
- Socket.IO for real-time communication
- All modals use `.modal-overlay` + `.modal-content` classes
- Mobile controls use absolute positioning with `right: 6px`
- CSS custom properties for theming (`var(--bg-main)`, etc.)

### Terminal Sessions
- Each session = TerminalSession instance in `active_sessions` dict
- Key format: `<project>` (main pane) or `<project>::<pane-id>` (split panes)
- PTY process spawns PowerShell with custom profile
- Background thread reads PTY output and broadcasts via Socket.IO
- Session cleanup on disconnect/close

---

## Common Workflows

### Adding a New Workspace
1. Click + in sidebar
2. Enter name + folder path
3. Creates entry in projects.json
4. Creates profile.ps1 in Project_data/<name>/
5. Click workspace card to spawn terminal

### Duplicating a Workspace
1. Select a workspace and use the duplicate icon beside the workspace controls.
2. The backend copies files into the next available numbered sibling folder (`name-2`, `name-3`, …), omitting `.git`, virtual environments, dependency folders, caches, and common build output.
3. A separate workspace is registered with the source category, theme, and bookmarks; its terminal layout starts fresh.
4. The new workspace is selected and gets a new per-workspace profile when its terminal starts.

### Customizing Workspace
1. Right-click workspace card → Customize
2. Change name, path, category, theme, card colors
3. Pin to top if desired
4. Name/path changes kill active session (clean restart)

### Using Git Integration
1. Click git badge in status bar
2. Review changed files
3. Write commit message
4. Check "Stage all changes" (uses `git add -A`)
5. Check "Push after commit" if desired
6. Click Commit button
7. Expand "Past Commits ›" to manage history

### Adding Custom Mobile Buttons
1. Click green + button on terminal right side
2. Enter label (e.g., "Tab")
3. Enter key code (e.g., `\t`)
4. Click Add Button
5. New button appears below + button
6. Saved in localStorage per project

---

## Troubleshooting

**Terminal not connecting:**
- Check if PowerShell is in PATH
- Check app.log for PTY errors
- Verify workspace path exists

**Git commands fail:**
- Ensure workspace folder is inside a git repo
- Check git is in PATH
- Run `git rev-parse --show-toplevel` in workspace folder manually

**Layout not saving:**
- Check projects.json is writable
- Verify `POST /api/projects/<project>/layout` succeeds

**Custom buttons not restoring:**
- Check localStorage quota
- Verify key format: `custom-btns-<project_name>`
- Check console for errors

---

## Recent Changes (2026-07-03)

1. **Git add -A**: Changed from `git add .` to `git add -A` to handle moved files
2. **Past commits section**: Added collapsible section with last 10 commits
3. **Commit rename**: Only HEAD commit can be renamed (git commit --amend)
4. **Checkout commits**: Time-travel to any past commit with detached HEAD warning
5. **Discard changes**: Added button to run `git restore` + `git clean`
6. **Mobile controls**: Added ESC, Ctrl+C, ← →, and + buttons
7. **Custom buttons**: Modal to add user-defined shortcuts per project
8. **UI polish**: Compact git modal, single-line commit rows, chevron toggle arrow

---

## Future Enhancements

- [ ] Multi-user support (auth)
- [ ] Remote SSH connections
- [ ] Terminal tabs within panes
- [ ] More git operations (stash, branch switching, merge)
- [ ] File explorer sidebar
- [ ] Code editor integration
- [ ] Theme marketplace
- [ ] Export/import workspace configs
- [ ] Linux/Mac support (replace WinPTY with node-pty)

---

## License & Credits

**Author**: Built with Kiro AI assistance  
**Created**: 2026  
**Dependencies**:
- [Xterm.js](https://xtermjs.org/) - Terminal emulator
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Socket.IO](https://socket.io/) - Real-time communication
- [WinPTY](https://github.com/rprichard/winpty) - Windows PTY wrapper
