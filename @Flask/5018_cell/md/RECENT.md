# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

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

**Files Modified:**
- `static/script.js` - Updated core logic (6 locations).
- `export_static.py` - Updated export logic (3 locations).
- `templates/index.html` - Enhanced guide entry.
- `md/MARKDOWN_SPECIAL.md` - Updated feature documentation.
- `md/RECENT.md` - Logged session.

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

---

## [2026-01-23 13:45] - Fixed Empty Lines Above Separators

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Empty Line Consumption Above/Below Separators
- **Problem**: Empty lines above/below horizontal separators were being "swallowed."
- **Solution**: Refined the joiner to only skip the newline if **both** lines have content.

**Current Status:**
- ✅ Separators respect empty lines.