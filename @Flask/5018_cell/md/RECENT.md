# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-23 11:45] - F2 Nickname Search

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Implemented Nickname Search in F2 Popup
- **Feature**: Users can now search for sheets by their **Nickname** in the F2 Recent Sheets popup.
- **Implementation**:
  - Updated `populateF2RecentSheets` to attach the nickname as a `data-nickname` attribute to list items.
  - Updated `filterF2Sheets` to check against both the visible sheet name and the hidden nickname.
- **Documentation**: Updated `md/UX_NAVIGATION.md` to reflect the new capability.

**Files Modified:**
- `static/script.js` - Added dataset attribute and updated filter logic.
- `md/UX_NAVIGATION.md` - Updated F2 features list.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ F2 search now finds sheets by nickname.

---

## [2026-01-23 11:27] - Table Edit Mode Stability

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Table Shrinkage in Edit Mode
- **Problem**: Switching to edit mode on a table caused the cell to shrink and shift the sheet layout.
- **Solution**: Refined spacing strategy & Added Settings.
  - Adjusted default `line-height` to `1.6`.
  - **New Feature**: Added "Line Height Settings" in the Settings menu (`⚙️`).
    - Users can now manually adjust **Table Edit Mode** line height (Default: 1.6).
    - Users can also adjust **Markdown Preview** line height (Default: 1.5).
  - This styling is persisted via `localStorage`.

### ✅ Fixed Empty Line Above Tables & Added Distributed Formatting
- **Problem 1**: Empty lines immediately preceding a table were often consumed by the parser.
- **Solution 1**: Updated `parseMarkdown` to explicitly restore newlines if the table regex matched them.
  - *Correction*: Reverted `.join('\n')` to `.join('')` for grid tables, as this was causing large gaps *after* tables (regrssion from commit 4b2bf8). The explicit newline restoration handles the "preservation" issue correctly without adding unwanted spacing blocks.

- **Problem 2**: Formatting tags could not span across table cell delimiters.
- **Solution 2**: Implemented "Distributed Formatting" (see above).

**Files Modified:**
- `static/script.js` - Added table line styling rule to `highlightSyntax`.
- `static/style.css` - Added `.syntax-table-line` class.
- `md/PROBLEMS_AND_FIXES.md` - Logged the fix.

**Current Status:**
- ✅ Tables maintain height consistency during editing.

---

## [2026-01-20 05:43] - Separated Active Sheet State

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Decoupled Active Sheet State
- **Problem**: Changing the active sheet updated `data.json`, potentially causing unnecessary file updates.
- **Solution**: Separated persistence into two files:
  - `data.json`: Stores content (sheets, rows, columns, styles).
  - `app_state.json`: Stores application state (active sheet index).
- **Update**: Changed state file path to `C:\@delta\output\5018_output\sheet_active.json`.
- **Feature**: Added F1 Quick Navigation modal to `export_static.py`.
  - Added button to UI (magnifying glass) for mobile access.
  - Implemented responsive layout for categories and sheet grid.
  - Supports F1 hotkey and category filtering.
- **Layout**: Optimized header for mobile.
  - Moved Sheet Name and Category to a dedicated top bar.
  - combined Name and Category into a single line (`Name • Category`).
  - Reduced toolbar clutter and prevented height issues on mobile.
- **Theming**: Applied Cyberpunk styling to the Sidebar Tree View.
  - Updated both `static/style.css` (Main App) and `export_static.py` (Static Export).
  - Dark background (`#050505`) with Neon Green (`#00ff41`) and Cyan (`#00d2ff`) accents.
  - Dark background (`#050505`) with Neon Green (`#00ff41`) and Cyan (`#00d2ff`) accents.
  - High-contrast text and hover effects.
- **F1 Window Logic**: Enhanced State Persistence & Context Highlighting.
  - **State Memory**: Reopening modal restores last selected category/view.
  - **Context Highlight**: Sidebar indicates the *current sheet's category* with a green border (`current-context` class), separate from the *active selection*.
  - **Smart Defaults**: Initial open selects the current sheet's category automatically.
- **Sidebar UX**: Fixed issue where categories would collapse upon selecting a sheet.
  - Sidebar now auto-expands the category containing the active sheet during render.
  - Applied to both `export_static.py` and `static/script.js`.
- **Performance**: Optimized sheet switching.
    - Added `/api/active-sheet` endpoint to `app.py`.
    - `switchSheet` now only updates `sheet_active.json` and does **not** trigger full data save or static export.
- **Dirty Check**: Prevent unnecessary file writes.
    - `save_data` now compares incoming data with existing `data.json`.
    - Only writes to `data.json` and triggers static export if content has actually changed.
    - Uses `sort_keys=True` in `json.dump` for consistent key ordering.

**Files Modified:**
- `app.py` - Updated `STATE_FILE` path and added directory creation.
- `export_static.py` - Updated `STATE_FILE` path and added F1 modal logic.
- `dev.md` - Updated data architecture documentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Active sheet state is now isolated in `sheet_active.json`.
- ✅ Static export includes F1 navigation.

---

## [2026-01-20 03:55] - Implemented List Levels 4 & 5

**Session Duration:** 0.2 hours

**What We Accomplished:**

### ✅ Extended List Functionality to 5 Levels
- **Features**: Added support for Level 4 (`---- `) and Level 5 (`----- `) lists.
- **Visuals**: Level 4 uses `▸` (triangle), Level 5 uses `−` (minus/dash).
- **Consistency**: Implemented in both `script.js` (live preview) and `export_static.py` (static export).
- **Rule of 6**: Updated detection, stripping (static), parsing, and documentation.

**Files Modified:**
- `static/script.js` - Updated `oldParseMarkdownBody`, `checkHasMarkdown`, `calculateVisibleToRawMap`.
- `export_static.py` - Updated `oldParseMarkdownBody`, `stripMarkdown`.
- `md/MARKDOWN_SPECIAL.md` - Documented new syntax.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Lists implemented up to 5 levels.
- ✅ Documentation updated.

---

## [2026-01-18 01:25] - Default Table Border Color Update

**Session Duration:** 0.3 hours

**What We Accomplished:**

### ✅ Updated Default Table Border Color to Black
- **Problem**: Default Markdown table borders were faint grey (`#ced4da`), making them hard to see.
- **Solution**: Changed the default border color to black (`#000000`) for all Markdown-based tables (comma and pipe syntax).
- **Consistency**: Synchronized the change across the main application (`static/script.js`, `static/style.css`) and standalone exports (`export_static.py`).
- **Header Refinement**: Updated `.md-header` to use a black bottom border for better visual separation.

**Files Modified:**
- `static/script.js` - Updated `parseCommaTable` default color.
- `static/style.css` - Updated `.md-cell`, `.markdown-table`, and `.md-header` border colors.
- `export_static.py` - Updated embedded CSS for tables and cells.
- `md/PROBLEMS_AND_FIXES.md` - Documented the color update.

**Current Status:**
- ✅ Flask server running on http://127.0.0.1:5018
- ✅ Markdown tables now render with black borders by default.
- ✅ Standalone exports match the application's table styling.