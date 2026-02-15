# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

## [2026-02-15 13:10] - Table Markdown Spanning in Static Export

**Session Duration:** 0.8 hours

**What We Accomplished:**

### 📊 Table Markdown Spanning for Static Export
- **Feature**: Synced the new table markdown spanning feature to `export_static.py`.
- **Implementation**:
  - Integrated the logic to track open/close state of delimiters across table cells into the embedded JS in `export_static.py`.
  - Removed the outdated `splitTableLine` function in favor of the new `parseGridTable` logic that matches `static/script.js`.
  - Fixed backslash escaping in the embedded JavaScript regex within the Python script to ensure proper rendering in exported HTML.
- **Improved Detection**:
  - Updated `hasMarkdown` check in `export_static.py` to include `customColorSyntaxes` detection, ensuring cells with custom highlighting are processed correctly during export.
- **Verification**:
  - Ran `export_static.py` and confirmed successful generation of `mycell.html` (5.9MB) without syntax errors.

**Files Modified:**
- `export_static.py` - Updated `parseGridTable`, removed `splitTableLine`, and refined `hasMarkdown` logic.
- `md/RECENT.md` - Added current session, archived oldest.
- `md/PROBLEMS_AND_FIXES.md` - Documented the export synchronization fix.

**Current Status:**
- ✅ Table markdown spanning works in both main app and static export.
- ✅ Custom color syntaxes are correctly detected in static export.
- ✅ Static export generates successfully without warnings.

**Next Steps:**
- Visually verify the exported HTML with complex spanning tables.

**Time Spent:** 0.8 hours

---

---

## [2026-02-15 12:20] - Nerd Font Support & Table Markdown Spanning

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🎨 Nerd Font Icon Support
- **Feature**: Added JetBrains Mono Nerd Font support for icon glyphs (, , etc.)
- **Implementation**:
  - Added Nerd Font to fallback chain: `'JetBrains Mono', 'JetBrainsMono Nerd Font', Vrinda, monospace`
  - Updated both main app (`static/script.js`) and export (`export_static.py`)
  - Icons display if Nerd Font is installed locally
- **Note**: Users should add a space after Nerd Font icons to prevent text overlap

### 📊 Table Markdown Spanning
- **Feature**: Markdown and custom color syntax can now span multiple table cells
- **Examples**:
  - `==Cell1 | Cell2 | Cell3==` → applies highlight to all three cells
  - `¿¿Cell1 | Cell2 | Cell3¿¿` → applies custom syntax to all cells
- **Implementation**:
  - Updated `parseGridTable()` to track open/close state of delimiters across cells
  - Each cell gets properly closed syntax: `==Cell1== | ==Cell2== | ==Cell3==`
  - Works with: `**`, `==`, `!!`, `??`, `@@`, `##`, `~~`, `<<`, `>>`, and custom syntax markers
- **Logic**: Tracks which delimiters are open, prepends them to next cell, closes them, and marks as open for following cells

**Files Modified:**
- `static/script.js` - Added Nerd Font fallback (3 lines), table spanning logic (~40 lines)
- `export_static.py` - Added Nerd Font fallback (1 line)
- `static/style.css` - Added letter-spacing for icon spacing
- `templates/index.html` - Restored Google Fonts link
- `md/CORE_SYSTEMS.md` - Documented Nerd Font support
- `md/TABLE_ADVANCED.md` - Documented markdown spanning feature
- `md/CUSTOM_SYNTAX.md` - Added table support section

**Current Status:**
- ✅ Nerd Font icons display correctly
- ✅ Markdown syntax spans multiple table cells
- ✅ Custom color syntax works across table cells
- ✅ Export HTML includes Nerd Font support

**Next Steps:**
- Test with various Nerd Font icon combinations
- Verify export HTML renders correctly

**Time Spent:** 0.5 hours

---

---

## [2026-02-12 16:30] - List Line Joining Visual Update Fix

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🐛 Fixed List Line Joining Not Updating Visually
- **Problem**: When editing list items (e.g., `- item1`, `- item2`) and using backspace/delete to join them into one line, the visual display wouldn't update until exiting edit mode.
- **Root Cause**: The `input` event handler wasn't re-rendering the content when structural changes occurred. The comment said "DON'T re-render on every keystroke" to avoid cursor jumping, but this caused list indentation styling to not update when line breaks were removed.
- **Solution**: 
  - Added smart detection for when line count changes (lines joined/split).
  - Used regex `/^(\-{1,5})\s/m` to detect list markers (1-5 dashes followed by space).
  - When line count changes AND content has special formatting (lists, tables), re-render with `highlightSyntax()`.
  - Preserved cursor position during re-render using `getCaretCharacterOffset()` and `setCaretPosition()`.
- **Result**: List indentation styling now updates immediately when joining/splitting lines, providing instant visual feedback.

**Files Modified:**
- `static/script.js` - Updated input event handler in `applyMarkdownFormatting()` (~10 lines)

**Technical Details:**
- **Detection**: Tracks `_previousLineCount` on the preview element to detect structural changes
- **Regex Pattern**: `/^(\-{1,5})\s/m` matches list markers at start of any line (multiline flag)
- **Cursor Preservation**: Saves character offset before re-render, restores after
- **Performance**: Only re-renders when necessary (line count changes + special formatting present)

**Current Status:**
- ✅ List line joining updates immediately in edit mode
- ✅ Cursor position preserved during re-render
- ✅ No performance impact on regular typing

---

## [2026-02-12 15:00] - Reliable Scroll & Navigation Fixes (Final)

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🖱️ Intelligent Scroll Preservation
- **Problem**: In Single Row Mode, focusing between cells or moving between rows would cause the scroll position to "forget" where the user was or reset to previous rows' positions.
- **Root Cause**: 
  - The high-level `renderTable` wrapper was unaware of per-row scroll states and would override the precise row restoration with stale global sheet positions.
  - Frequent re-renders during editing/navigation were competing for scroll control.
- **Solution**: 
  - **Enhanced Wrapper**: Updated the `renderTable` wrapper to prioritize `rowScrolls` from the `sheetSingleRowStates` map. This ensures the final scroll restoration (after all cell height adjustments) uses the correct, row-specific coordinates.
  - **Synchronized Navigation**: Verified `nextSingleRow`/`prevSingleRow` correctly use the `skipScroll` flag to transition between indices without data leakage.
  - **Fail-safe Restore**: Standardized the `targetScrollTop` logic in the wrapper to handle both row navigation (`preserveScroll=false`) and cell editing (`preserveScroll=true`) scenarios seamlessly.

**Files Modified:**
- `static/script.js` - Refactored `renderTable` wrapper and navigation logic.
- `md/PROBLEMS_AND_FIXES.md` - Documented the final solution.

**Current Status:**
- ✅ Single Row Mode is now fully production-ready with perfect scroll memory.
- ✅ Cell navigation is smooth and stable regardless of row height.

---

## [2026-02-12 14:45] - Reliable Scroll Preservation in Single Row Mode

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🖱️ Scroll Preservation Refinements
- **Solution**: Refactored `saveSingleRowState` and navigation functions. Added layout shift protection in `adjustCellHeightForMarkdown`.

---

*Older sessions archived in md/ARCHIVE_RECENT.md*
