# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

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