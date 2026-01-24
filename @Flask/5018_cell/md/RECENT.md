# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-23 15:00] - 2-Button Markdown Mode Toggle

**Session Duration:** 0.2 hours

**What We Accomplished:**

### ✅ Split Markdown Toggle into 2 Buttons
- **Feature**: Refactored the view mode controls for better UX. Instead of a single cycle button, there are now two dedicated toggles:
  1. **📝 (Raw Mode)**: Dedicated button to switch to source code view.
  2. **👁️ (Visual Mode)**: Dedicated button to toggle between **Standard** (dimmed syntax) and **Clean** (pure WYSIWYG) modes.
- **Interactions**:
  - Clicking 📝 instantly enters/exits Raw mode.
  - Clicking 👁️ cycles between Standard <-> Clean modes.
  - Right-clicking either icon also cycles its respective state.
- **Visuals**:
  - Clean Mode still features the magenta glow on the 👁️ icon.
  - Refined CSS for active/inactive toggle states.
- **Technical**:
  - Refactored `static/script.js` to use a central `setMode(mode)` function.
  - Removed redundant `enableRawMode` logic.
  - Synchronized across initialization, event listeners, and documentation.

**Files Modified:**
- `templates/index.html` - Added the new button structure.
- `static/script.js` - Refactored mode logic and listeners.
- `static/style.css` - Updated active/clean mode styles.
- `md/MARKDOWN_MODES.md` - Updated documentation for the new UI.
- `md/UX_NAVIGATION.md` - Updated UI documentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Improved 2-button control system for markdown viewing.

---

## [2026-01-23 14:45] - Title Text Font Styling

**Session Duration:** 0.15 hours

**What We Accomplished:**

### 🎯 Added Font Styling to "Title Text" (`:::Params:::Text:::`)
- **Advanced Customization**: Users can now control the **font size** and **font color** inside Title Text bars.
- **Enhanced Syntax**: 
  - `:::1.5em:::Title:::` (Change font size)
  - `:::f-R:::Title:::` (Change font color to red - use `f-` prefix)
  - `:::B_2px_1.2em_f-#fff:::Title:::` (Full styling: Blue 2px border, 1.2em white text)
- **Implementation**:
  - Updated parsing logic in `static/script.js` and `export_static.py` to handle `em`, `rem`, and `f-` parameters.
  - Corrected detection and stripping regexes to allow `#`, `.`, and `-` in parameter blocks.
- **Documentation**: Updated Formatting Guide and `md/MARKDOWN_SPECIAL.md` with new styling examples.

**Current Status:**
- ✅ Title Text supports full border and font customization.

---

## [2026-01-23 14:30] - Customizable Title Text Feature

**Session Duration:** 0.15 hours

**What We Accomplished:**

### 🎯 Enhanced "Title Text" Syntax (`:::Params:::Text:::`)
- **Customization**: Users can now set the **color** and **thickness** of Title Text borders.
- **New Syntax**: 
  - `:::Title:::` (Default: Black, 1px)
  - `:::R_3px:::Title:::` (Red, 3px borders)
- **Implementation**: Added parameter parsing logic to `highlightSyntax` and `oldParseMarkdownBody`.

**Current Status:**
- ✅ Title Text is customizable.

---

## [2026-01-23 14:15] - Resolved Title Text Syntax Conflict

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 Updated "Title Text" Syntax to `:::Text:::`
- **Conflict Resolution**: Changed the marker from `===` to `:::` because `===` was partially matched by the existing `==` (black highlight) rule.
- **New Syntax**: Users now use `:::Title:::`.

**Current Status:**
- ✅ `:::Title Text:::` is safe from syntax conflicts.

---

## [2026-01-23 14:00] - New "Title Text" Feature & Separator Fixes

**Session Duration:** 0.25 hours

**What We Accomplished:**

### 🎯 Added "Title Text" Syntax
- **New Feature**: Users can now create prominent section titles.
- **Visuals**: Renders text as a bold, centered block with solid 1px top and bottom borders.

### ✅ Refined Separator (`-----`) Line Joining
- **Fix**: Updated the line-joining logic to preserve newlines if either adjacent line is empty.

**Current Status:**
- ✅ Spacing issues resolved.
