# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-23 13:45] - Fixed Empty Lines Above Separators

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Fixed Empty Line Consumption Above/Below Separators
- **Problem**: Just like with tables, empty lines placed immediately above or below horizontal separators (`-----`) were being "swallowed," causing the separator to touch the text.
- **Root Cause**: The line-joining logic in `oldParseMarkdownBody` was aggressively skipping newlines when a separator was detected to avoid double-spacing from block margins. However, it did this even when the user intended to have an explicit empty line.
- **Solution**: Refined the joiner to only skip the newline if **both** the current line and the previous line have content. If either is empty, the newline/break is preserved to maintain the user's intended spacing.
- **Consistency**: Applied the fix to both `static/script.js` and `export_static.py`.

**Files Modified:**
- `static/script.js` - Refined separator joiner.
- `export_static.py` - Refined separator joiner in embedded JS.
- `md/RECENT.md` - Logged session.

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

**Files Modified:**
- `static/script.js` - Refined joiner in `parseMarkdown`.
- `export_static.py` - Refined joiner in `parseMarkdown`.
- `md/RECENT.md` - Logged session.

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

**Files Modified:**
- `static/script.js` - Updated `parseMarkdown` block joiner.
- `export_static.py` - Updated `parseMarkdown` block joiner.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Empty lines above/below tables are now correctly preserved in all modes.

---

## [2026-01-23 13:00] - List Indentation Fix & Markdown Mode Polish

**Session Duration:** 0.15 hours

**What We Accomplished:**

### ✅ Implemented Hanging Indents for Lists in Edit Mode
- **Feature**: List items (`-`, `--`, `---`, `----`, `-----`) now maintain a consistent hanging indent in Edit Mode (Standard and Clean modes).
- **Implementation**: Updated `highlightSyntax` to detect list patterns and apply `text-indent: -1em` with appropriate `padding-left`.
- **Consistency**: This ensures that when a list line wraps, the second line is indented, matching the Preview Mode behavior exactly.

### ✅ Refined 3-State Markdown Toggle
- **Interaction**: Added support for cycling modes via the Page Icon (📄) button.
- **States**: 0 (Raw), 1 (Standard), 2 (Clean).
- **UI**: Clean mode now hides syntax markers while maintaining the correct list indentation.

**Files Modified:**
- `static/script.js` - Updated `highlightSyntax` for list indentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ List indentation follows preview behavior in all markdown modes.
- ✅ 3-state toggle functional and documented.

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