# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-23 12:45] - 3-State Markdown Mode & Clean Mode

**Session Duration:** 0.15 hours

**What We Accomplished:**

### ✅ Implemented Clean Markdown Mode (No Syntax)
- **Feature**: Added a third view mode called "Clean Mode" that renders markdown but hides all syntax markers (`**`, `##`, etc.) even during editing.
- **Cycle Logic**: The markdown toggle (📄 icon) now cycles through 3 states:
  1. **Raw Mode**: Shows raw text (0).
  2. **Standard Mode**: Shows preview, focus shows dimmed syntax (1).
  3. **Clean Mode**: Shows preview, focus hides syntax completely (2).
- **Interactions**:
  - **Left Click**: Cycles modes (Raw -> Standard -> Clean -> Raw).
  - **Right Click**: Also cycles modes (as requested).
- **Visuals**:
  - Added CSS rule to hide `.syn-marker` in `clean-markdown-mode`.
  - Added magenta glow to the toggle icon in Clean Mode.

**Files Modified:**
- `static/script.js` - Refactored `toggleMarkdownPreview`, `enableRawMode`, and initialization logic for 3 states. Added event listeners.
- `static/style.css` - Added Clean Mode CSS rules.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ 3-state toggle functional (Raw/Standard/Clean).
- ✅ Clean mode hiding syntax markers as requested.

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
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ F2 search now finds sheets by nickname.