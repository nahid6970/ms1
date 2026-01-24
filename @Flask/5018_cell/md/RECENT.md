# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-23 14:15] - Resolved Title Text Syntax Conflict

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 Updated "Title Text" Syntax to `:::Text:::`
- **Conflict Resolution**: Changed the marker from `===` to `:::` because `===` was partially matched by the existing `==` (black highlight) rule, causing rendering errors.
- **New Syntax**: Users now use `:::Title:::`.
- **Implementation**: Updated all parsing, stripping, and detection logic in `static/script.js`, `export_static.py`, and the documentation.

**Files Modified:**
- `static/script.js` - Updated core logic.
- `export_static.py` - Updated export logic.
- `templates/index.html` - Updated formatting guide.
- `md/MARKDOWN_SPECIAL.md` - Updated documentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ `:::Title Text:::` is now safe from syntax conflicts.

---

## [2026-01-23 14:00] - New "Title Text" Feature & Separator Fixes

**Session Duration:** 0.25 hours

**What We Accomplished:**

### 🎯 Added "Title Text" Syntax
- **New Feature**: Users can now create prominent section titles using `===` delimiters.
- **Visuals**: Renders text as a bold, centered block with solid 1px top and bottom borders.
- **Implementation**:
  - Added to `highlightSyntax` for real-time edit mode (with hidden markers).
  - Added to `oldParseMarkdownBody` for standard preview mode.
  - Implemented in `export_static.py` for standalone HTML consistency.
  - Added to `checkHasMarkdown` and `stripMarkdown` for proper detection and searching.
- **Documentation**: Updated "Markdown Formatting Guide" modal and `md/MARKDOWN_SPECIAL.md`.

### ✅ Refined Separator (`-----`) Line Joining
- **Problem**: Explicit empty lines above/below horizontal separators were being removed.
- **Fix**: Updated the line-joining logic to preserve newlines if either adjacent line is empty, matching the fix previously applied to tables.

**Current Status:**
- ✅ Spacing issues for tables and separators are resolved.

---

## [2026-01-23 13:45] - Fixed Empty Lines Above Separators

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Empty Line Consumption Above/Below Separators
- **Problem**: Just like with tables, empty lines placed immediately above or below horizontal separators (`-----`) were being "swallowed," causing the separator to touch the text.
- **Root Cause**: The line-joining logic in `oldParseMarkdownBody` was aggressively skipping newlines when a separator was detected to avoid double-spacing from block margins. However, it did this even when the user intended to have an explicit empty line.
- **Solution**: Refined the joiner to only skip the newline if **both** the current line and the previous line have content. If either is empty, the newline/break is preserved to maintain the user's intended spacing.
- **Consistency**: Applied the fix to both `static/script.js` and `export_static.py`.

**Current Status:**
- ✅ Separators now respect empty lines above/below them.

---

## [2026-01-23 13:30] - Refined Table Spacing & Joining

**Session Duration:** 0.15 hours

**What We Accomplished:**

### ✅ Refined Spacing Strategy Around Tables
- **Problem**: The previous fix for preserving empty lines introduced "double spacing" below tables, making subsequent text appear too far away.
- **Root Cause**: Tables have their own CSS margins (`margin: 4px 0` for `.md-grid`). Adding a newline (`\n`) in a `pre-wrap` container creates a full line break on top of that margin.
- **Solution**: 
  - Updated `parseMarkdown` to use a "smart joiner". 
  - It now only adds a newline if it's transitioning between text blocks or if there's an explicit empty line.
  - If a block is a table and the next block is text, it skips the newline to rely on the table's built-in margin.
- **Comma Tables**: Applied similar refined logic to `Table*N` syntax, adding a newline only if the remaining content doesn't already start with one.
- **Consistency**: Synchronized the logic across `static/script.js` and `export_static.py`.

**Current Status:**
- ✅ Empty lines are preserved above/below tables when explicitly typed.
- ✅ Normal spacing is maintained when text immediately follows a table.

---

## [2026-01-23 13:15] - Fixed Empty Line Above Tables

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Empty Line Consumption Before Grid Tables
- **Problem**: When a user added an empty line between text and a Pipe table (`|...|`), the empty line was ignored in the preview, causing the text to merge with the table.
- **Root Cause**: The block-joining logic in `parseMarkdown` was using an over-aggressive strategy that skipped separators if one of the blocks was a table.
- **Solution**: Simplified the block-joining logic to always use a newline (`\n`) as a separator between blocks. This preserves the natural document structure and ensures that explicit empty lines are rendered in the `pre-wrap` preview.
- **Consistency**: Applied the fix to both the live application (`static/script.js`) and the standalone export logic (`export_static.py`).

**Current Status:**
- ✅ Empty lines above/below tables are now correctly preserved in all modes.