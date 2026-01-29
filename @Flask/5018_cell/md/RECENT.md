# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-01-29 11:45] - F3 Formatter Link Removal Fix

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Fixed F3 Formatter Link Removal
- **Problem**: "Remove Formatting" (🧹) in F3 menu was stripping URLs from `{link:url}text{/}` syntax.
- **Solution**: 
    - Updated `stripMarkdown()` to preserve both URL and text for all link syntaxes (e.g., `url text`).
    - Reordered stripping logic to prioritize link preservation.
    - Refined general color regex to avoid accidental link matching.
- **Consistency**: Synchronized improvements to `export_static.py` for consistent search/sort and export behavior.

**Files Modified:**
- `static/script.js` - Major update to `stripMarkdown` logic.
- `export_static.py` - Updated `stripMarkdown` for consistency.
- `md/PROBLEMS_AND_FIXES.md` - Documented the fix.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Links are now correctly preserved when stripping formatting.
- ✅ Search and Sort now reliably handle all link syntaxes.

---

## [2026-01-27 23:59] - Bookmark Window Enhancements

**Session Duration:** 0.8 hours

**What We Accomplished:**

### 🚀 Enhanced Bookmark (Last Edited) Window
-   **Tabbed Interface Display**:
    -   Increased displayed bookmarks to **3 cells** (up from 2).
    -   Refactored tabs to show **Cell Reference only** (e.g., `A60`) for a compact, modern appearance.
    -   Implemented **Sheet Name on Hover**: Full sheet names now appear as tooltips (`title`) rather than taking up tab space.
-   **Right-Click Quick Removal**:
    -   Added `oncontextmenu` support to bookmark tabs.
    -   Users can now **right-click a tab to remove** that cell from the bookmark list immediately.
    -   Added visual hint "(Right-click to remove)" to tooltips.
-   **UI & Reliability Fixes**:
    -   **Scrollbar Sync**: Fixed a race condition where the scrollbar wouldn't appear on first load of a long cell. Using `setTimeout` and `overflow-y: auto` ensures immediate scroll visibility.
    -   **Layout Tightening**: Reduced excessive padding in `.recent-edit-list` and `.recent-edit-item`.
    -   **Data Structure Migration**: Fully transitioned `lastEditedCells` to an **Array-based structure** to support multiple entries per sheet and reliable sorting.
    -   **Robust Syncing**: Fixed `savePopupEdit` and `syncPopupWithMainUpdate` to reliably handle the new array-based storage.

**Files Modified:**
- `static/recent_edits.js` - Major refactor for tab logic, removal feature, and resize reliability.
- `static/script.js` - Migrated `lastEditedCells` initialization and `addToRecentEdits` to array logic.
- `static/style.css` - Updated tab styling and tightened list layout.
- `md/RECENT.md` - Logged session.
- `md/PROBLEMS_AND_FIXES.md` - Documented scroll and layout fixes.

**Current Status:**
- ✅ Bookmark window is now a powerful, multi-cell productivity tool.
- ✅ Tab management is intuitive with click-to-switch and right-click-to-remove.
- ✅ UI feels more integrated and less "empty/oversized".

---

## [2026-01-26 17:15] - UI/UX Refinements & Popup Direct Edit

**Session Duration:** 0.6 hours

**What We Accomplished:**

### 🎯 Added Lorem Ipsum Generator to F3 Formatter
- **New Feature**: Added a **📝+** button to the Quick Formatter (F3).
- **Functionality**: Replaces selected text with a standard Lorem Ipsum paragraph.
- **Support**: Works in both WYSIWYG (contentEditable) and Raw (textarea) modes.

### 🎨 Polished Notification UI
- **Change**: Moved toast notifications (status updates) from top-right to **top-center**.
- **UX**: Reduced size and padding for a more compact, modern look that doesn't obstruct content.

### 🚀 Enhanced Recent Edits (Bookmark) Popup
- **Direct Edit Mode**: Popup now displays the editable textarea immediately (no click-to-edit required).
- **UI Fix**: Improved the **✕ close button** positioning and hit area. It is now larger, centered, and easier to click.
- **Live Synchronization**:
  - Popup now fetches the **actual live value** from `tableData` when opened, ensuring it's always in sync with main table edits.
  - Added `syncPopupWithMainUpdate()` to update the popup in real-time as the user types in the main table.
- **Scroll & Height Control**:
  - Implemented `autoResizePopupTextarea()` to grow naturally with text.
  - Capped height at ~15 lines (330px) with internal scrolling to prevent the popup from extending off-screen.
- **Fixed Input behavior**: Simplified Enter key handling to allow standard newlines without unwanted side effects.

**Files Modified:**
- `templates/index.html` - Added F3 button.
- `static/style.css` - Compact top-center toast styles.
- `static/script.js` - Implemented `generatePlaceholderText` and sync hook in `updateCell`.
- `static/recent_edits.js` - Complete refactor for direct edit, live sync, and height capping.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Bookmark workflow is much faster with direct editing and reliable sync.
- ✅ Notifications are less intrusive.
- ✅ Rapid prototyping improved with placeholder text button.

---

## [2026-01-26 16:35] - F3 Formatter Enhancements

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🎯 Added Lorem Ipsum Generator to F3 Formatter
- **New Feature**: Added a **📝+** button to the Quick Formatter (F3).
- **Functionality**: Replaces selected text with a standard Lorem Ipsum paragraph.
- **Support**: Works in both WYSIWYG (contentEditable) and Raw (textarea) modes.

### 🔧 Updated Title Text Default Value
- **Improvement**: Set the default value of the F3 Title Text prompt to `K_5px_2em_f-K`.
- **UX**: Reduces typing for the most common title style.

**Files Modified:**
- `templates/index.html` - Added 📝+ button.
- `static/script.js` - Implemented `generatePlaceholderText` and updated `applyTitleTextFormat`.
- `md/RECENT.md` - Logged session details.

**Current Status:**
- ✅ Improved rapid prototyping with placeholder text.
- ✅ Faster title formatting with optimized defaults.

---

## [2026-01-26 16:15] - Precision Search Scroll Restoration

**Session Duration:** 0.4 hours

**What We Accomplished:**

### ✅ Fixed Scroll Jump When Clearing Search
- **Problem**: When searching for terms and then clearing the search box, the table would jump back to the top of the sheet, causing users to lose their place.
- **Root Cause**: 
  - The scroll event listener was auto-saving the `scrollTop` of `0` when the table shrunken to show only search matches.
  - There was no logic to restore the scroll position to the last viewed match after showing all rows.
- **Solution**: 
  - **Pixel-Perfect Restoration**: Implemented a "visual offset" capture system. Before clearing search, it records the exact distance of the last match from the container's top.
  - **Adaptive Scrolling**: After clearing, it calculates and restores the scroll so the row remains at the identical screen position.
  - **Search Safety**: Disabled scroll-saving while the search box contains text to prevent overwriting true reading positions with shrunken views.
  - **Refined UX**: Simplified `clearSearch` to use the centralized logic in `searchTable`.

**Technical Changes:**
- `searchTable()`: Now captures `lastMatchRow` and its `visualOffset`.
- `searchTable()`: Restores scroll position by adjusting `scrollTop` based on the delta between new and old offsets.
- Scroll Event Listener: Added check to return early if search is active.
- `clearSearch()`: Refactored to call `searchTable()` for consistent cleanup.

**Files Modified:**
- `static/script.js` - Implemented precise scroll mapping and search safety.
- `md/RECENT.md` - Logged session.
- `md/PROBLEMS_AND_FIXES.md` - Documented the fix.

**Current Status:**
- ✅ Search-to-Full transition is now seamless and maintains context.
- ✅ No interference with per-sheet scroll preservation.

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
