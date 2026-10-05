# Feature Specifications

## Code Merger
**Status:** ✅ Complete
**Description:** Built-in Code Merger panel accessible from the status bar. Packages project files into structured AI prompts (PREP tab) and applies AI responses back to disk (MERGE tab) using the `@@FILE / @@MODE / @@END` format. Completely self-contained inside terminal_tui — no external tools required.
**Implementation:** `app.py` (routes: `/api/project/<project>/file-overwrite`, `/api/project/<project>/merge-apply`), `templates/index.html` (popover UI + JS)
**Usage:** Click the `⇅` cyan button in the status bar → opens Code Merger popover.
**Sub-features:**

### PREP tab
- Recursively lists all project files, skipping known junk dirs (`node_modules`, `.git`, `__pycache__`, etc.)
- Checkboxes per file — text/code files auto-checked, binary/non-text files shown dimmed and unchecked
- **All / None** selection buttons
- **⊘ Exclude** button — toggles a collapsible panel with glob pattern exclusions:
  - `folder/` syntax to exclude entire directory trees (e.g. `tests/`, `dist/`)
  - `*.ext` syntax to exclude by extension (e.g. `*.log`, `*.pyc`)
  - Substring match for anything else
  - Pre-loaded with sensible defaults (`.git/`, `node_modules/`, `__pycache__/`, `*.pyc`, `*.log`, `*.bak`, `*.tmp`, `*.lock`, `package-lock.json`, etc.)
  - Pattern tags with `×` remove button — removal immediately re-filters the list
  - File count + `⊘ N excluded` indicator (clickable to open the exclude panel)
- **↺ Refresh** button re-fetches the file list
- Task / instructions textarea for describing the AI task
- **⚡ Generate Prompt** — fetches file contents via `/api/project/<project>/file-content`, builds full prompt with format guide + task + file blocks
- **Copy** button copies the generated prompt to clipboard
- Prompt preview textarea showing char count

### MERGE tab
- Paste AI response textarea (accepts full `@@FILE/@@MODE/@@END` blocks, also strips outer markdown fences)
- **.bak backups** checkbox — saves timestamped `.bak` copy before modifying any file (on by default)
- **🔍 Parse** — previews which files will be changed and in what mode (no writes)
- **✔ Apply Changes** — sends response to backend, shows per-file `✅`/`❌` results with error messages
- Applied count + failed count summary

### Supported merge modes
| Mode | What it does |
|---|---|
| `replace_block` | Replaces a specific block; exact match first, falls back to whitespace-tolerant match |
| `replace_file` | Overwrites the entire file |
| `insert_after` | Inserts lines after a matched anchor |
| `delete_block` | Removes a matched block entirely |

---

## Global Restart and Page Refresh Controls
**Status:** ✅ Complete
**Description:** The global restart control offers separate actions for restarting the app and refreshing only the current page. F5 also refreshes the page.
**Implementation:** `templates/index.html` — restart action menu and global F5 key handler.

## Terminal Clipboard and Refresh Recovery
**Status:** ✅ Complete
**Description:** Terminal copy/paste works with standard shortcuts without duplicate insertion, and long AI/tool output is retained after browser refresh.
**Implementation:** `templates/index.html` — capture-phase Ctrl+V paste handling, Ctrl+C selection copy, Shift+Insert paste, and 20,000-row xterm scrollback. `app.py` retains up to 500,000 characters per session.

## F1 Quick Open Palette
**Status:** ✅ Complete
**Description:** F1 opens a centered command-palette-style window for selecting workspaces, searching saved commands, and creating a new workspace.
**Implementation:** `templates/index.html` — dark rounded palette layout, search/back row, Projects and Commands views, existing Add Workspace modal integration, Arrow-key/Enter navigation, and Ctrl/Cmd+1–9 project shortcuts.

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
- Duplicate the active workspace into the next available `-2`, `-3`, … sibling folder, copying workspace settings and files while omitting Git metadata and common generated folders

---

## Split Terminal Panes
**Status:** ✅ Complete
**Description:** Multiple terminal panes per workspace with a tabbed terminal bar shown by default.
**Implementation:** `splitTerminal(layout, initialCmd)` creates new PTY sessions. Layouts: `tabs` (default tabbed), `right` (vertical), `bottom` (horizontal), `stacked` (quad). Pane IDs and the active tab are stored in browser `localStorage`, not workspace JSON, so browser refresh reconnects to the same tabs. Resetting all sessions clears the saved tabs.
**Files Involved:** `templates/index.html` (JS: `splitTerminal()`, `confirmSplitLayout()`), `app.py` (session keyed as `<project>::<pane-id>`)
**Usage:** Click the `+` terminal tab to open another tab, or click split button in toolbar → select layout from card-style modal.
**Notifications:** An unfocused terminal tab plays a brief sound and shows an amber dot when PowerShell returns to its prompt after a command. Selecting the tab clears the dot.

---

## Git Integration
**Status:** ✅ Complete
**Description:** Full git workflow from the status bar — view changes, stage, commit, push, checkout, branch management, diff viewer, AI-suggested commit messages.
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
- **AI Suggest Commit Message** — `✨` button + Gemini model dropdown in commit message row; fetches git diff, calls Gemini API, fills textarea with conventional commit suggestion. Model dropdown is independent from AI copilot, respects hidden-models list, persists selection.

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

---

## AI Copilot
**Status:** ✅ Complete
**Description:** In-app AI assistant powered by Google Gemini, Groq, Morph, or OpenRouter. Supports tool use, chat history, system prompts, and model management.
**Implementation:** Backend `/api/ai-command` routes requests to the selected provider. Frontend renders a popover with chat history, model/provider selector, and tool toggles.
**Files Involved:** `app.py` (route: `/api/ai-command`), `ai_tools.py`, `templates/index.html` (AI copilot popover)
**Usage:** Click 🤖 in status bar (or Ctrl+I) → type prompt → Enter.
**Sub-features:**
- Multi-provider: Gemini, Groq, Morph, OpenRouter
- Dynamic model list fetched live from each provider's API
- Model visibility toggle (hide/show per provider)
- Bookmarked models sorted to top
- Speed tags (Fast / Medium / Slow) per model — manually set or auto-measured by batch tester
- Rate limit display per model (RPM / RPD / TPM)
- Custom system prompts (stored in `tui_config.json`)
- Chat history with re-prompt
- Tool use: shell commands, file read/write, directory listing
- Multiple API accounts per provider with label selector
- **Model Batch Tester** — sends a test prompt to every model of a provider sequentially:
  - Auto-hides failed models (adds to hidden list)
  - Auto-classifies speed from elapsed time (< 3 s Fast, 3–8 s Medium, ≥ 8 s Slow)
  - Per-model ignore toggle (skip in tests without hiding)
  - Eye toggle (hide/show globally) per card
  - Speed select override per card
  - Syncs copilot dropdown speed tags after batch completes
