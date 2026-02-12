# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-02-12 14:00] - List Support in Table Cells

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 📊 Lists Inside Table Cells
- **New Feature**: Added support for markdown lists (bullet and numbered) inside table cells for both Pipe and Comma tables.
- **Implementation**: 
  - Updated `parseMarkdownInline` to split cell content by `<br>` or `\n` and process each line for list markers.
  - Supports standard bullet markers (`-`, `--`, `---`, etc.) and numbered markers (`1.`, `2.`, etc.).
  - Preserves hanging indents and tab alignment using the same styling logic as main-sheet lists.
- **Rule of 6 Compliance**:
  - Synchronized the logic to `export_static.py` for correct rendering in standalone exports.
  - Updated the "Markdown Formatting Guide" in `templates/index.html` with examples and instructions.

### 🛡️ Robust Syntax Protection in Visual Mode
- **Problem**: Users reported rare cases where markdown syntax was stripped during editing.
- **Solution**: Removed `requestAnimationFrame` from focus handler and added "Bullet Recovery" logic to `extractRawText`.

**Files Modified:**
- `static/script.js` - Updated `parseMarkdownInline` with list parsing.
- `export_static.py` - Synced `parseMarkdownInline` improvements.
- `templates/index.html` - Updated Formatting Guide.
- `md/RECENT.md` - Logged session and archived 1 older session.

**Current Status:**
- ✅ Tables now support rich multiline content including nested lists.
- ✅ Consistent rendering between live app and static exports.

---

## [2026-02-12 13:30] - Visual Mode Syntax Corruption Fix

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🛡️ Robust Syntax Protection in Visual Mode
- **Problem**: Users reported rare cases where all markdown syntax was stripped from a cell during editing, leaving only rendered list bullets (•, ◦, etc.) in the raw data.
- **Root Cause**: A race condition in the `focus` event listener. Highlighting was deferred via `requestAnimationFrame`. If a user typed instantly, the `input` event would trigger `extractRawText` on the *already rendered* preview (with bullets) before it switched to *highlighted syntax* (with markers).
- **Solution**: 
  - **Immediate Highlighting**: Removed `requestAnimationFrame` from the `focus` handler. The transition from rendered preview to syntax-highlighted editor now happens synchronously, ensuring the DOM always contains markers when the user types.
  - **Fail-safe Recovery**: Updated `extractRawText` and `extractRawTextBeforeCaret` with a "Bullet Recovery" map. If it ever encounters rendered bullets (•, ◦, ▪, ▸, −) at the start of a line, it automatically converts them back to markdown syntax (- , -- , --- , etc.), preventing data corruption.

---

## [2026-02-12 12:00] - Script Crash and Hiding Sheet Content

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🔧 Bug Fixes & Robustness
- **Fixed Script Crash**: Resolved a critical error where duplicated code in `showSyntaxInspector` was executing in the global scope.
- **Rendering Safeguards**: Added checks in `renderTable` to handle empty sheets.

---

## [2026-02-12 11:30] - Syntax Inspector & Single Row Mode Per-Sheet State

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🔍📜 Syntax Inspector Feature
- **New Feature**: Added a "Syntax Inspector" button (🔍📜) to the F3 Quick Formatter.
- **UI Refinements**: Centered modal and auto-close F3.

### ✅ Per-Sheet Single Row Mode & Scroll Fix
- **Solution**: Per-sheet state for Single Row Mode and scroll restoration fix.

---

## [2026-02-11 10:30] - Single Row Mode Per-Sheet State

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Per-Sheet Single Row Mode
- **Problem**: Toggling "Single Row Mode" affected other sheets.
- **Solution**: Implemented per-sheet state.

---

*Older sessions archived in md/ARCHIVE_RECENT.md*
