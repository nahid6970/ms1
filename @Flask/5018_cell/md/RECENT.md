# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-02-12 11:30] - Syntax Inspector & Single Row Mode Per-Sheet State

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🔧 Bug Fixes & Robustness
- **Fixed Script Crash**: Resolved a critical error where duplicated code in `showSyntaxInspector` was executing in the global scope, breaking the entire application.
- **Rendering Safeguards**: Added checks in `renderTable` to handle empty sheets and invalid indices gracefully, preventing "Cannot read properties of undefined" errors that were hiding sheet content.

### 🔍📜 Syntax Inspector Feature
- **New Feature**: Added a "Syntax Inspector" button (🔍📜) to the F3 Quick Formatter.
- **Functionality**:
  - Analyzes selected text to identify all nested markdown syntaxes (e.g., in `**__text__**` it finds Bold and Underline).
  - Opens a modal listing all found syntaxes in their current nesting order.
  - Clicking any syntax in the list automatically re-wraps the text to move that syntax to the **outermost** position.
  - Supports both `contentEditable` and legacy `input/textarea` modes.
  - Handles 15+ standard syntaxes and complex regex-based syntaxes (Border Box, Font Size, Custom Colors, Titles).
- **UI Refinements**:
  - Automatically closes the F3 Quick Formatter window when the inspector opens to reduce clutter.
  - Centered the Syntax Inspector modal perfectly on the screen using flexbox for better UX.

### ✅ Per-Sheet Single Row Mode & Scroll Fix
- **Problem**: Toggling "Single Row Mode" or changing the focused row in one sheet would affect other sheets.
- **Problem 2**: Untoggling "Single Row Mode" would cause the sheet to scroll to the top.
- **Solution**: 
  - Implemented `saveSingleRowState()` and `loadSingleRowState(index)` to persist state for each sheet individually.
  - **Scroll Fix**: Added `scrollToRow(index)` helper and updated `toggleSingleRowMode` to precisely scroll back to the active row when disabling Single Row Mode.

**Files Modified:**
- `static/script.js` - Added state management, scroll fix, and Syntax Inspector logic.
- `static/style.css` - Added Syntax Inspector list styling.
- `templates/index.html` - Added Syntax Inspector button and modal.
- `md/CELL_FEATURES.md` - Updated feature documentation.
- `md/PROBLEMS_AND_FIXES.md` - Documented fixes and new feature.
- `md/KEYBOARD_SHORTCUTS.md` - Added Syntax Inspector to F3 list.

**Current Status:**
- ✅ Users can inspect and reorder complex nested formatting easily.
- ✅ Single Row Mode is fully independent per sheet.
- ✅ Navigation between modes is smooth with no scroll jumps.

---

## [2026-02-11 10:30] - Single Row Mode Per-Sheet State

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Per-Sheet Single Row Mode
- **Problem**: Toggling "Single Row Mode" or changing the focused row in one sheet would affect other sheets when switching back and forth. The state was global.
- **Problem 2**: Untoggling "Single Row Mode" would cause the sheet to scroll to the top.
- **Solution**: Implemented per-sheet state for `singleRowMode` and `singleRowIndex`.

---

## [2026-02-08 16:15] - #R# Border Box Refinement and Alignment Fixes

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🎨 Refined Multi-line Border Box Styling
- **Problem**: Multi-line `#R#` border boxes showed horizontal lines between every wrapped row of text.
- **Solution**: Switched from `border` to `outline: 2px solid [color]` with `outline-offset: 4px`.

---

## [2026-02-06 16:15] - Table Formatting and UI Refinements

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Final Fix for Nested Table Formatting (Stars and Punctuation)
- **Problem**: Mixing row-wrapped formatting with cell-specific styles caused rendering artifacts.
- **Solution**: Reverted Border Box (`#R#`) to `display: inline`.

---

## [2026-02-06 15:45] - Square Borders and Sub-sheet Tab Colorization

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🎯 Square UI Borders
- **Visual Update**: Removed all rounded corners (`border-radius: 0`) from the entire application interface.

---

*Older sessions archived in md/ARCHIVE_RECENT.md*
