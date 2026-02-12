# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

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

**Files Modified:**
- `static/script.js` - Updated `extractRawText`, `extractRawTextBeforeCaret`, and `focus` listener.
- `md/PROBLEMS_AND_FIXES.md` - Documented the fix.
- `md/RECENT.md` - Logged session and archived 1 older session.

**Current Status:**
- ✅ Visual Mode editing is now bulletproof against fast-typing race conditions.
- ✅ Fail-safe logic prevents literal icons from entering the database.

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

## [2026-02-08 16:15] - #R# Border Box Refinement and Alignment Fixes

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🎨 Refined Multi-line Border Box Styling
- **Solution**: Switched from `border` to `outline` for cleaner rendering.

---

*Older sessions archived in md/ARCHIVE_RECENT.md*
