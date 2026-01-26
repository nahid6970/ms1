# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-26 15:30] - Fixed Per-Sheet Scroll Position Preservation

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🐛 Fixed Scroll Position Not Preserving for Specific Sheets
- **Problem**: Scroll position was not being preserved for certain sheets (e.g., "GK" sheet) when switching between sheets.
- **Root Cause**: Scroll positions were stored by **sheet index** instead of **sheet name**, so when sheets were reordered (moved up/down), the scroll positions became mismatched.
- **Solution**: 
  - Changed scroll position storage to use **sheet name** as the key instead of index.
  - Added migration function to convert old index-based positions to name-based.
  - Fixed `renderTable` wrapper that was overriding scroll positions after 350ms delay.
  - Added `preserveScroll` parameter to `renderTable()` to distinguish between re-renders and sheet switches.

**Technical Changes:**
- `switchSheet()`: Now saves/restores scroll using sheet name as key.
- `renderTable()`: Added `preserveScroll` parameter (default `true`).
- `renderTable` wrapper: Respects `preserveScroll` flag to avoid overriding scroll on sheet switch.
- Scroll event listener: Saves scroll position using sheet name.
- Added `migrateScrollPositions()`: One-time migration from index-based to name-based storage.

**Files Modified:**
- `static/script.js` - Fixed scroll position logic throughout.
- `md/RECENT.md` - Logged session.
- `md/PROBLEMS_AND_FIXES.md` - Documented the bug and fix.

**Current Status:**
- ✅ Scroll positions now persist correctly across all sheets, even after reordering.
- ✅ Added comprehensive logging for debugging scroll issues.

---

## [2026-01-26 10:55] - Recent Sheet Edits Feature

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🎯 Added "Recent Edits" Popup (Manual)
- **New Feature**: Added a **🕒** button for viewing pinned/recent edits.
- **Changed Functionality**:
  - **Manual Tracking**: Users now manually add cells to the list using "📌 Add to Recent Edits" in the context menu.
  - **Automatic tracking removed** to prevent noise.
  - Clicking the clock button shows these manually pinned cells from *other* sheets.
  - Users can **edit** these cells directly from the popup.
  - Updates are synced to the respective sheet immediately.
- **Implementation**:
  - Context Menu: Added "Add to Recent Edits" option.
  - JS: Removed auto-tracking from `updateCell`, added `addToRecentEdits()`.
  - Persistence: Uses `localStorage`.

**Files Modified:**
- `templates/index.html` - Added button and script inclusion. Moved popup to body.
- `static/style.css` - Added popup styles.
- `static/script.js` - Added tracking logic.
- `static/recent_edits.js` - New file for popup logic.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Feature implemented.
- ✅ Fixed popup clipping issue by using fixed positioning.
- ✅ Added persistence via localStorage.
- ✅ Fixed bug in "Add to Recent Edits" context menu item.
- ✅ Made popup persistent (does not close when clicking outside), allowing interaction with other sheets while viewing.

---

## [2026-01-23 15:30] - F3 Title Text Button & UX Polish

**Session Duration:** 0.15 hours

**What We Accomplished:**

### 🎯 Added Title Text Button to F3 Formatter
- **New Feature**: Added a **T** button to the Quick Formatter (F3) for the Title Text syntax.
- **Workflow**:
  - Select text and press **F3**.
  - Click the **T** button (between Border Box and Code).
  - A prompt allows entering optional parameters (e.g., `R_3px_1.5em_f-K`).
  - Automatically wraps selection in `:::Params:::Text:::`.
- **Implementation**:
  - Added `applyTitleTextFormat(event)` to `static/script.js`.
  - Added button UI to `templates/index.html`.
  - Supports both WYSIWYG (contentEditable) and Raw (textarea) modes.

### ✅ Refined Visual Mode Indication
- **Dynamic Feedback**: Visual mode button icon now switches between **👁️** (Standard) and **✨** (Clean).
- **Mode Tooltips**: Added explicit "Visual Mode: Standard" and "Visual Mode: Clean" titles to the button.

**Files Modified:**
- `templates/index.html` - Added F3 button.
- `static/script.js` - Implemented `applyTitleTextFormat`.
- `md/UX_NAVIGATION.md` - Updated F3 layout documentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Improved workflow for creating section titles.
- ✅ Better visual feedback for view modes.

---

## [2026-01-23 15:15] - Improved Visual Mode Indication

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Enhanced Visual Mode UI Feedback
- **Problem**: It was difficult to distinguish between "Standard" and "Clean" modes using only the 👁️ button's glow.
- **Solution**: 
  - **Dynamic Icons**: Icon changes between **👁️** and **✨**.
  - **Dynamic Tooltips**: Updated `title` attribute.

**Current Status:**
- ✅ Clear visual distinction between all 3 markdown modes.

---

## [2026-01-23 15:00] - 2-Button Markdown Mode Toggle

**Session Duration:** 0.2 hours

**What We Accomplished:**

### ✅ Split Markdown Toggle into 2 Buttons
- Refactored controls into **📝 (Raw)** and **👁️ (Visual)** buttons.
- Refactored `static/script.js` to use a central `setMode(mode)` function.

**Current Status:**
- ✅ Improved 2-button control system for markdown viewing.
