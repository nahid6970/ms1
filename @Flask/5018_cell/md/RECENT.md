# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-02-06 16:15] - Table Formatting and UI Refinements

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Final Fix for Nested Table Formatting (Stars and Punctuation)
- **Problem**: Table rows with trailing punctuation failed to distribute formatting tags. Additionally, border boxes (`#R#`) were being clipped in exports.
- **Solution**: 
  - **Clipping Fix**: Changed `overflow` from `hidden` to `visible` for `.md-cell`. This ensures that even with a compact layout, the 2px borders are fully visible and not cut off by the cell edges.
  - **Smart Detection**: Refined `distributeTableFormatting` to correctly handle punctuation and local tag pairs.
- **Compact UI**: Reverted extra padding/line-height to maintain the original compact spreadsheet look while keeping the border fix.
- **Consistency**: Synchronized these improvements to `export_static.py`.

### 🎨 UI Consistency Improvements
- **Sub-sheet Fix**: Resolved a duplicate function issue that was preventing "Set Colors" from appearing in the sub-sheet menu.
- **Dynamic Colors**: Improved the `important` flags and inheritance for category/sheet colors to ensure they apply reliably across all bars and sidebars.

**Files Modified:**
- `static/script.js` - Major rewrite of `distributeTableFormatting` and cleanup of `parseGridTable`.
- `export_static.py` - Updated to match new formatting logic.
- `md/RECENT.md` - Logged session.
- `md/PROBLEMS_AND_FIXES.md` - Documented the "stars" fix.

**Current Status:**
- ✅ Complex table rows like `**__A | B__**` now render perfectly.
- ✅ Navigation bars are fully customizable and professional.

---

## [2026-02-06 15:45] - Square Borders and Sub-sheet Tab Colorization

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🎯 Square UI Borders
- **Visual Update**: Removed all rounded corners (`border-radius: 0`) from the main container, sheet tabs, subsheet bar, toolbar buttons, and search boxes for a sharper, professional look.

### 🎨 Sub-sheet Tab Colorization
- **Customizable Sub-sheets**: Added "Set Colors" to the right-click menu of sub-sheet tabs.
- **Dynamic Styling**:
  - Sub-sheet tabs now use their own `bgColor` and `fgColor` metadata.
  - Active tabs are highlighted with a white inner border (`box-shadow`) to maintain visibility against custom backgrounds.
  - Sub-sheet bar automatically adopts the parent sheet's background color.
- **Real-time Sync**: Color changes now reflect immediately in the main view, subsheet bar, and sidebar tree.
- **Fix**: Removed a duplicate `showSubSheetContextMenu` function that was overwriting the version containing the "Set Colors" option.

**Files Modified:**
- `static/style.css` - Removed border-radii across the UI.
- `static/script.js` - Added "Set Colors" to subsheet menu, improved `applyTabColors`, and synchronized color updates.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ UI has a consistent square aesthetic.
- ✅ Sub-sheets are fully color-customizable from their own bar.

---

## [2026-02-06 16:15] - UI/UX Refinements and Sub-sheet Customization

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🎨 Advanced Color Customization & Inheritance
- **Sub-sheet Styling**: Added "Set Colors" to the sub-sheet tab context menu. Sub-sheets now support unique background and text colors.
- **Category Inheritance**: Implemented logic where sheets and sub-sheets automatically inherit the background/text colors of their parent Category if no explicit colors are set.
- **Visual Sync**: Enhanced color application to be more robust using `!important` flags, ensuring custom themes correctly override default styles across the F1 window, Sidebar tree, and Navigation bars.
- **Smarter Input**: Added auto-correction for hex codes (prepends `#` if missing) in prompt dialogs.

### 📐 Square Professional UI
- **Modern Aesthetic**: Replaced all rounded corners (`border-radius: 0`) across the entire application interface, including the main container, sheet tabs, subsheet bar, toolbar buttons, search boxes, and context menus.

### 🎯 Bulletproof Sort Ranking
- **Global Normalization**: Added a proactive cleanup step during app load that automatically resolves duplicate ranks or gaps in old sheets.
- **Contiguous Sequencing**: Refined the re-ranking logic to ensure a perfect 1, 2, 3... sequence is maintained even during complex moves or deletions.

### 🔧 Code Cleanup & Bug Fixes
- **Duplicate Function Removal**: Identified and removed a duplicate `showSubSheetContextMenu` function that was preventing color options from appearing.
- **Sync Fixes**: Integrated `renderSidebar()` and `renderTable()` updates into the sheet color picker to ensure changes reflect instantly without page refresh.

**Files Modified:**
- `static/script.js` - Major logic updates for colors, inheritance, and ranking.
- `static/style.css` - UI-wide square border updates and background-color optimizations.
- `md/RECENT.md` - Logged session.
- `md/PROBLEMS_AND_FIXES.md` - Documented fixes.
- `md/UX_NAVIGATION.md` - Updated navigation features.

**Current Status:**
- ✅ Navigation bars dynamically adapt to Category/Sheet themes.
- ✅ Professional square-edge design implemented.
- ✅ Sort ranks are consistently contiguous and gapless.

---

## [2026-02-06 15:15] - Category Colors and Sort Rank Refinements

**Session Duration:** 0.6 hours

**What We Accomplished:**

### 🎯 Added Category Colors in F1 and Sidebar
- **New Feature**: Categories in the F1 Quick Navigation window can now have custom background and text colors.
- **Implementation**:
  - Added "Set Colors" to the Category context menu in F1.
  - Colors are applied to both the F1 category list and the Sidebar tree headers.
  - Supports "Uncategorized" as a colorable category.
  - Data is stored in `tableData.categoryStyles`.

### ✅ Enhanced Sort Ranking Logic
- **Normalization**: Ranks are now automatically normalized to a contiguous sequence (1, 2, 3...) upon any change or app load.
- **Improved Movement**: Setting a rank now properly shifts existing items and fills gaps, ensuring a consistent user experience.

**Files Modified:**
- `static/script.js` - Implemented `showCategoryColorPicker`, updated `populateF1Categories`, `renderSidebar`, and `initializeCategories`.
- `md/UX_NAVIGATION.md` - Updated documentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Categories are now as customizable as sheets.
- ✅ Sort ranking is bulletproof.

---

## [2026-02-06 14:45] - Cell Sort Ranking Enhancements

**Session Duration:** 0.3 hours

**What We Accomplished:**

### 🎯 Added Auto-Reranking and Normalization for Sort Ranks
- **New Logic**: When setting a rank (e.g., rank 1), the system now automatically shifts all existing ranks that are equal to or higher than the new rank (+1).
- **Contiguous Sequencing**: Implemented a **Normalization** step (`normalizeSheetRanks`) that runs after every ranking change. This ensures ranks are always a gapless sequence (1, 2, 3...), even if an item is moved to a high number or a rank is deleted.
- **Improved Moving Logic**: Moving a ranked cell now properly swaps positions by temporarily removing the cell from the list, compacting the rest, and then re-inserting at the target rank.
- **Batch Support**: The feature now correctly handles multiple selected cells, processing them in sheet order (top-to-bottom).
- **Reliability Fix**: Added missing `saveData()` call to the ranking function to ensure persistence.

**Files Modified:**
- `static/script.js` - Updated `setCellRank()` with reranking logic and `saveData()`.
- `md/CELL_FEATURES.md` - Updated documentation.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Sort ranking is more dynamic and user-friendly.

---

## [2026-02-06 14:30] - Temporary Notepad Feature

**Session Duration:** 0.4 hours

**What We Accomplished:**

### 🎯 Added Temporary Notepad
- **New Feature**: Added a **📝** button to the toolbar that opens a persistent scratchpad.
- **Functionality**:
  - **Independent Storage**: content is saved to `localStorage` (`temp_notepad_content`), persisting across refreshes but remaining separate from sheet data.
  - **UI/UX**: dedicated 400px wide popup with a resizeable textarea.
  - **Interaction**: auto-focuses on open; closes automatically when clicking outside.
- **Refinement**:
  - **Exclusive Popups**: implemented logic to ensure opening the Notepad closes the Bookmark popup, and vice versa.
  - **Click-Outside Fix**: added robust "click outside to close" handlers for both the Notepad and the Bookmark popup.

**Files Modified:**
- `templates/index.html` - Added button and popup container.
- `static/style.css` - Added styling for `.temp-notepad-popup`.
- `static/temp_notepad.js` - Created feature logic.
- `static/recent_edits.js` - Added coordination logic and click-outside handler.
- `md/TEMP_NOTEPAD_FEATURE.md` - Created feature documentation.
- `md/RECENT.md` - Logged session.
- `md/PROBLEMS_AND_FIXES.md` - Documented UI behavior fixes.

**Current Status:**
- ✅ Users have a dedicated space for temporary notes.
- ✅ Popup management is cleaner (no overlapping windows).

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
