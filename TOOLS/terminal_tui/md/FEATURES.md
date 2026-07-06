# Feature Specifications

## Workspace Management
**Status:** ✅ Complete
**Description:** Multi-workspace terminal sessions. Each workspace = project folder + persistent PowerShell session with custom profile.
**Implementation:** `projects.json` stores all workspace metadata. `Project_data/<name>/profile.ps1` is auto-generated per workspace.
**Files Involved:** `app.py` (routes: `/api/projects/*`), `templates/index.html` (sidebar UI)
**Usage:** Click `+` in sidebar → enter name + folder path → click workspace card to spawn terminal.
**Sub-features:**
- Categories — group workspaces
- Pin/unpin — keep important workspaces at top
- Drag-to-reorder — custom ordering persisted
- Custom PowerShell profiles with project-specific prompt, aliases, history

---

## Split Terminal Panes
**Status:** ✅ Complete
**Description:** Multiple terminal panes per workspace with various layouts.
**Implementation:** `splitTerminal(layout, initialCmd)` creates new PTY sessions. Layouts: `right` (vertical), `bottom` (horizontal), `stacked` (quad), `tabs` (tabbed).
**Files Involved:** `templates/index.html` (JS: `splitTerminal()`, `confirmSplitLayout()`), `app.py` (session keyed as `<project>::<pane-id>`)
**Usage:** Click split button in toolbar → select layout from card-style modal.

---

## Git Integration
**Status:** ✅ Complete
**Description:** Full git workflow from the status bar — view changes, stage, commit, push, checkout, branch management, diff viewer.
**Implementation:** Backend runs git CLI commands via `subprocess`. Frontend renders in modals.
**Files Involved:** `app.py` (routes: `/api/project/<project>/git/*`), `templates/index.html` (git modal UI)
**Usage:** Click git badge in status bar → review files → commit → push.
**Sub-features:**
- Stage all (`git add -A`)
- Commit + auto-push
- Past commits (last 10) with rename, checkout, push
- Detached HEAD warning with "Return to latest"
- Discard all changes (`git restore` + `git clean`)
- Branch management (create, switch, merge, delete)
- Diff viewer with line-by-line changes
- Git graph visualization

---

## Bookmarks
**Status:** ✅ Complete
**Description:** Save frequently used commands per workspace with global option.
**Implementation:** Stored in `projects.json` per workspace. Dropdown in toolbar.
**Files Involved:** `app.py` (routes: `/api/projects/<project>/bookmarks/*`), `templates/index.html` (bookmark dropdown + edit modal)
**Usage:** Click 🔖 dropdown → select command → auto-executes. Click ⭐ to bookmark current command.
**Sub-features:**
- Global bookmarks (appear in all workspaces)
- Edit command, name, window title
- Reorder by drag or position select

---

## File Explorer
**Status:** ✅ Complete
**Description:** Slide-out file explorer panel with recursive directory browsing.
**Implementation:** Backend serves directory listings. Frontend renders tree with lazy-loading subdirectories.
**Files Involved:** `app.py` (routes: `/api/project/<project>/files`, `file-content`, `file-delete`, `file-write`, `paste-clipboard`), `templates/index.html` (explorer panel + file viewer modal)
**Usage:** Click folder icon in toolbar → browse files → hover for action buttons.
**Sub-features:**
- View file content with syntax highlighting and line numbers
- Run scripts (opens card-style modal: PowerShell / CMD / Raw)
- Delete files and folders
- Paste files from Windows clipboard

---

## Status Monitor
**Status:** ✅ Complete
**Description:** Real-time status bar showing system and git info.
**Implementation:** Polls `/api/session/<project>/stats` periodically.
**Files Involved:** `app.py` (route: `/api/session/<project>/stats`), `templates/index.html` (status bar)
**Usage:** Visible at bottom of screen when a workspace is active.
**Sub-features:**
- CPU usage (SVG icon)
- RAM usage (integer, SVG icon)
- Active pane count
- Git branch, modifications count, insertions/deletions

---

## Mobile Controls
**Status:** ✅ Complete
**Description:** Touch-friendly buttons on terminal panes + persistent input tray for Gboard text editing.
**Implementation:** Buttons positioned on right side of each pane. Input tray is a slide-out panel in status bar.
**Files Involved:** `templates/index.html` (mobile button rendering, input tray)
**Sub-features:**
- Close pane (×), ESC, Ctrl+C, scroll up/down, cursor left/right
- Custom button shortcuts (+ button → modal → saved per project in localStorage)
- Mobile Input Helper tray — type/edit with native cursor features, insert to terminal without auto-enter

---

## Scheduled Commands
**Status:** ✅ Complete
**Description:** Schedule commands to run after a delay.
**Implementation:** Backend uses threading timers. Frontend popover with quick-set buttons.
**Files Involved:** `app.py` (routes: `/api/project/<project>/schedule/*`), `templates/index.html` (sched popover)
**Usage:** Click ⏰ in status bar → enter command + delay → schedule.

---

## Quick Tools
**Status:** ✅ Complete
**Description:** Built-in utilities: grep search, file stats, process killer, port checker.
**Implementation:** Backend runs system commands. Frontend renders in tabbed popover.
**Files Involved:** `app.py` (routes: `/api/project/<project>/tools/*`, `/api/tools/*`), `templates/index.html` (qtools popover)
**Usage:** Click 🔧 in status bar → select tab → run tool.

---

## Snippets
**Status:** ✅ Complete
**Description:** Save and send text snippets to the active terminal.
**Implementation:** Stored via backend API. Frontend popover.
**Files Involved:** `app.py` (routes: `/api/snippets`), `templates/index.html` (snippets popover)
**Usage:** Click snippets button in status bar → add/send snippets.

---

## Scratchpad
**Status:** ✅ Complete
**Description:** Floating notepad per workspace for quick notes.
**Implementation:** Saved to localStorage per project. Draggable panel.
**Files Involved:** `templates/index.html` (scratchpad panel)
**Usage:** Click 📝 in toolbar → type notes → auto-saved.

---

## Theme Customization
**Status:** ✅ Complete
**Description:** Per-workspace terminal and card theming.
**Implementation:** Stored in `projects.json`. Applied via CSS custom properties and Xterm.js theme options.
**Files Involved:** `app.py` (route: `/api/projects/customize`), `templates/index.html` (theme modal)
**Sub-features:**
- Terminal colors (background, foreground, cursor, scrollbar)
- Workspace card colors (bg, text, path, accent)
- Font family and size selection
- Global app font override

---

## Screenshot / Image Upload
**Status:** ✅ Complete
**Description:** Upload or paste images, saved to temp directory with path copied to clipboard.
**Implementation:** Backend saves to `C:\Users\nahid\AppData\Local\Temp\screenshot_temp`.
**Files Involved:** `app.py` (routes: `/api/images/temp`, `/api/session/<project>/paste-image`), `templates/index.html` (file input + paste handler)
**Usage:** Click 📷 button or paste image → path auto-copied.
