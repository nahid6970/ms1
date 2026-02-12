# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-02-12 14:45] - Final Scroll & Navigation Refinements

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🖱️ Reliable Scroll Preservation
- **Problem**: Moving between cells in Single Row Mode caused the view to "reset" to previous positions.
- **Root Cause**: 
  - `saveSingleRowState` was being called during row transitions *after* the index changed but *before* rendering, causing the new row to inherit the old row's scroll.
  - Manual scroll restorations in `focus`/`blur` handlers were interfering with natural browser behavior and capturing stale positions.
- **Solution**: 
  - **Auto-Save on Scroll**: Updated the global scroll listener to call `saveSingleRowState()` continuously, ensuring `rowScrolls` are always up to date.
  - **Smart Navigation**: Refactored `nextSingleRow` and `prevSingleRow` to explicitly save the old row's scroll, then update index, then save the index *without* overwriting the scroll map.
  - **Clean Handlers**: Removed manual `scrollTop` overrides from `focus` and `blur` listeners in `applyMarkdownFormatting`, allowing the browser to manage focus positions naturally.

**Files Modified:**
- `static/script.js` - Refactored `saveSingleRowState`, navigation functions, and event listeners.
- `md/PROBLEMS_AND_FIXES.md` - Updated with final resolution details.
- `md/RECENT.md` - Logged session and archived 1 older session.

**Current Status:**
- ✅ Scroll positions are perfectly preserved within and between rows in Single Row Mode.
- ✅ Cell focus is smooth and no longer jumps to "last cell" positions.

---

## [2026-02-12 14:00] - List Support in Table Cells

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 📊 Lists Inside Table Cells
- **New Feature**: Added support for markdown lists (bullet and numbered) inside table cells.
- **Implementation**: Updated `parseMarkdownInline` to split content by `<br>` or `\n`.

---

## [2026-02-12 13:30] - Visual Mode Syntax Corruption Fix

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🛡️ Robust Syntax Protection in Visual Mode
- **Problem**: Rare markdown syntax stripping during editing.
- **Solution**: Immediate highlighting on focus and fail-safe bullet recovery.

---

## [2026-02-12 12:00] - Script Crash and Hiding Sheet Content

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🔧 Bug Fixes & Robustness
- **Fixed Script Crash**: Resolved duplicated code error in global scope.
- **Rendering Safeguards**: Added checks for empty sheets in `renderTable`.

---

## [2026-02-12 11:30] - Syntax Inspector & Single Row Mode Per-Sheet State

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🔍📜 Syntax Inspector Feature
- **New Feature**: Added a "Syntax Inspector" button (🔍📜) to the F3 Quick Formatter.

### ✅ Per-Sheet Single Row Mode & Scroll Fix
- **Solution**: Per-sheet state for Single Row Mode and scroll restoration fix.

---

*Older sessions archived in md/ARCHIVE_RECENT.md*
