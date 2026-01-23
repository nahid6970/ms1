# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-23 12:25] - Fix Custom Color Syntax in Edit Mode

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Custom Color Syntax Rendering in Edit Mode
- **Problem**: Custom color syntaxes (e.g., `++text++`) were not displaying their colors or styles when editing a cell (WYSIWYG mode).
- **Root Cause**: The `highlightSyntax` function was using incorrect property names (`backgroundColor` instead of `bgColor`) and missing style logic.
- **Solution**: Updated `highlightSyntax` to use correct properties and apply bold, italic, and underline styles defined in the custom syntax.

**Files Modified:**
- `static/script.js` - Corrected property mapping in `highlightSyntax`.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Custom syntaxes now render correctly in both Preview and Edit modes.

---

## [2026-01-23 12:10] - Markdown Preview Line Height Fix

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Markdown Preview Line Height Setting
- **Problem**: The "Markdown Preview" line height setting was not updating the preview or table rows because the CSS was hardcoded to `1.4`.
- **Solution**:
  - Updated `.markdown-preview` class in `static/style.css` to use `var(--markdown-preview-line-height)`.
  - Explicitly applied the variable to `.markdown-table td` and `.markdown-table th` to ensure tables inside the preview respect the setting.

**Files Modified:**
- `static/style.css` - Replaced hardcoded line-height with CSS variable.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Markdown Preview line height now dynamically updates when changed in Settings.

---

## [2026-01-23 12:00] - Server-Side Settings Persistence

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Migrated Line Height Settings to JSON File
- **Problem**: Settings were only stored in `localStorage`, limiting portability.
- **Solution**: Implemented server-side persistence for application settings.
  - Created `C:\@delta\db\5018_cell\setting.json` as the storage file.
  - Added `/api/settings` GET/POST endpoints to `app.py`.
  - Updated `static/script.js` to fetch/save settings via API instead of `localStorage`.
- **Impact**: "Table Edit Mode" and "Markdown Preview" line heights are now saved globally to the filesystem.

**Files Modified:**
- `app.py` - Added settings API and file constants.
- `static/script.js` - Switched `loadLineHeightSettings` and `updateLineHeightSettings` to use the API.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Settings are now persisted to `setting.json`.

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
