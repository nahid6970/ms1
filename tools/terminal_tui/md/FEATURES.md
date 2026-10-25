# Feature Specifications

## Restart and Refresh Requirements

When reporting completed work, end the response with the required next action:

- **Python server/backend changes** (for example, `app.py` routes or session handling): restart the Flask app; refresh the browser too if the page needs updated frontend code.
- **Frontend-only changes** (`templates/index.html`, CSS, or browser JavaScript): refresh the browser; restarting the app is not needed.
- **Configuration/data-only changes:** normally neither. Mention a new terminal session or other action when the feature requires it.

Always state one clear outcome at the end of the response. Do not say “restart required” without naming what must be restarted.

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

**Local path picker:** In the Add Workspace modal, focus Local Directory Path and press Tab to browse local drives and folders. Select the current folder to fill the path; if Workspace Name is empty, it is filled from the selected folder name. The picker can create a new folder in the current directory.

**Duplicate path warning:** Adding a workspace whose folder path is already registered is rejected with a warning naming the existing workspace. Path comparison ignores case and separator differences and resolves equivalent filesystem paths.

**Closing the last terminal tab:** Closing the last pane stops that workspace session, clears its saved tab layout, and returns to Home. Home selection is persisted so a page refresh does not reopen the previously active workspace.

### Workspace List Filters
**Status:** ✅ Complete
**Description:** A synchronized connected three-option icon control filters projects in both the sidebar and workspace dropdown. The provided All layers, GitHub, and Rclone SVGs are embedded inline; each icon can be selected directly and includes an accessible name and tooltip.
**Implementation:** `templates/index.html` stores the selected filter in `localStorage` and applies it to both project renderers. `app.py` includes a `hasRcloneDestination` flag in the projects response; successful Rclone destination saves update the current client-side project data immediately.

**Per-workspace Git remote recovery:** Save a Git remote URL under Customize Workspace. The missing-folder dialog can clone that remote into the saved workspace path. The same settings action runs `git fetch --prune origin` when the folder already contains a Git repository; this updates remote refs without changing the checked-out files. The URL is stored in the workspace record in `tui_config.json`.
**Restore a folder to a past commit:** Each past commit has a second restore action beside Checkout. It restores the workspace subtree snapshot into the index and working tree, removes untracked files under that subtree, preserves ignored files, and leaves paths outside the workspace untouched. A confirmation explains the discarded changes before it runs.
**Sub-features:**
- Categories — group workspaces
- Pin/unpin — keep important workspaces at top
- Drag-to-reorder — custom ordering persisted
- Custom PowerShell profiles with project-specific prompt, aliases, history
- Duplicate the active workspace into the next available `-2`, `-3`, … sibling folder, copying workspace settings and files while omitting Git metadata and common generated folders
- **Workspace bar** (top of terminal area) shows running workspace chips for quick switching — auto-hides when only one workspace is running, reappears as soon as a second one opens

---

## Rclone Workspace Sync
**Status:** ✅ Complete
**Description:** Compare or sync the active workspace with a local folder or rclone remote. Commands open in a new terminal tab. The centered Rclone dialog fits its content, grows when filter previews appear, and keeps its action buttons visible while long content scrolls. The configured button foreground and background colors can be changed in Global Settings with presets or custom colors.
**Implementation:** `templates/index.html` builds `rclone check` or directional `rclone sync` commands; `app.py` provides workspace scanning and Gemini ignore suggestions.
**Usage:** Open the Rclone button in the workspace header (before Delete), set Destination and optional ignorelist, then use Check, SRC → DST, or DST → SRC. Press Tab in Destination to browse local folders and configured Rclone remotes; the browser starts at the entered path or lists available drives/remotes when empty. Configure button colors in Global Settings → General. Ignorelist patterns are read from the configured file and passed as individual `--exclude` flags.
**AI ignore suggestions:** The ✨ action scans folder names at all depths and immediate file/subfolder counts, plus up to 40 top-level filenames, up to 200 extensions, and up to 12,000 characters of `.gitignore`. Known heavy and hidden folders are reported as pruned and not recursively scanned. The AI receives at most 500 directory records (favoring folders with more immediate files), never individual file paths. Suggestions appear in the preview before the user saves them. The modal expands to fit the preview when possible; on smaller screens, its content scrolls while the action buttons stay visible. The Gemini model is selectable and remembered locally. An absolute ignorelist path outside the workspace falls back to `<workspace>/ignorelist.txt` and updates the field.
**Files Involved:** `app.py` (`/api/project/<project>/rclone/scan`, `/api/project/<project>/rclone/suggest-ignore`, `/api/rclone/destination-directories`, `/api/local/directories`, `/api/local/directories/create`), `templates/index.html` (Rclone modal, color settings, and local folder pickers)

## Git .gitignore AI Suggestion
**Status:** ✅ Complete
**Description:** An AI action beside the Git modal heading scans the workspace file and folder paths, then suggests a project-specific `.gitignore` or updates the existing one.
**Implementation:** `POST /api/project/<project>/git/suggest-ignore` scans paths locally while skipping `.git` internals and symlink traversal. Gemini receives the existing root `.gitignore` (if present) and a compact bounded inventory of extensions, directory names, busy directories, and sampled paths; file contents are not read. The prompt favors concise, evidence-based rules and rejects generic boilerplate for ecosystems or tools absent from the inventory. The result opens in an editable preview. `POST /api/project/<project>/git/gitignore` atomically writes the reviewed contents to the workspace root and invalidates Git status cache.
**Usage:** Open the Git modal, select the `.gitignore` AI button beside its heading, review and edit the proposal, then choose Create or Update to save. The changed-file list refreshes after saving.
**Files Involved:** `app.py` (Git suggestion and save endpoints), `templates/index.html` (Git modal action, editable preview, and refresh), `md/ARCHITECTURE.md`, `md/FEATURES.md`, `md/RECENT.md`

---

## Bangla (Complex Script) Rendering in Terminal
**Status:** ✅ Complete
**Description:** Bangla text displays correctly shaped in the main terminal. Matras, hasants, and conjuncts combine properly instead of appearing as broken isolated cells.
**Implementation:** `templates/index.html` — after each `pty-output` write, scroll, and resize, `renderBanglaRows()` scans the visible xterm buffer rows and places absolutely-positioned `<div class="bangla-row-overlay">` elements inside `.xterm-screen` at the exact pixel position of any row containing Bangla characters (U+0980–U+09FF). The overlays use `Nirmala UI`/`Vrinda` fonts so the browser shapes the text correctly. Non-Bangla rows are untouched. Overlays are `pointer-events: none` so all input passes through to xterm.
**Key functions:** `renderBanglaRows(term, paneDiv)`, `_banglaRowHtml(term, bufferRow)`

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
- HEAD is marked in the commit list only when that commit actually touched files in the active workspace folder — foreign commits from other workspaces sharing the same repo are not injected
- Preview a past commit's own changes scoped to the workspace folder (parent → commit diff, not HEAD → commit)
- Global setting to hide or show commit hashes in the past-commits list
- Compact relative commit times (`35s`, `15h`, `11d`) without an “ago” suffix
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
