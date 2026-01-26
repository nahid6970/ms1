# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

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
- ✅ Fixed bug in "Add to Recent Edits" context menu item (property name mismatch).

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

---

## [2026-01-23 14:45] - Title Text Font Styling

**Session Duration:** 0.15 hours

**What We Accomplished:**

### 🎯 Added Font Styling to "Title Text" (`:::Params:::Text:::`)
- Users can now control **font size** and **font color** inside Title Text bars.
- Enhanced Syntax: Supports `em`, `rem`, and `f-` parameters.

**Current Status:**
- ✅ Title Text supports full border and font customization.

---

## [2026-01-23 14:30] - Customizable Title Text Feature

**Session Duration:** 0.15 hours

**What We Accomplished:**

### 🎯 Enhanced "Title Text" Syntax (`:::Params:::Text:::`)
- **Customization**: Users can now set the **color** and **thickness** of Title Text borders.

**Current Status:**
- ✅ Title Text is customizable.
