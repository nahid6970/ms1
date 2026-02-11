# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

---

## [2026-02-11 10:30] - Single Row Mode Per-Sheet State

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Per-Sheet Single Row Mode
- **Problem**: Toggling "Single Row Mode" or changing the focused row in one sheet would affect other sheets when switching back and forth. The state was global.
- **Solution**: 
  - Implemented `saveSingleRowState()` and `loadSingleRowState(index)` to persist `singleRowMode` (on/off) and `singleRowIndex` (row number) for each sheet individually in `localStorage`.
  - Updated `switchSheet`, `loadData`, `toggleSingleRowMode`, `prevSingleRow`, and `nextSingleRow` to use this per-sheet state.
  - Added clamping logic in `renderTable` to ensure the index stays valid if rows are deleted, saving the corrected state.

**Files Modified:**
- `static/script.js` - Added state management functions and updated navigation logic.
- `md/CELL_FEATURES.md` - Updated feature documentation.
- `md/PROBLEMS_AND_FIXES.md` - Documented the fix.
- `md/RECENT.md` - Logged session.

**Current Status:**
- ✅ Users can have different sheets in different modes (Table vs Single Row).
- ✅ Row focus is preserved individually for each sheet.

---

## [2026-02-08 16:15] - #R# Border Box Refinement and Alignment Fixes

**Session Duration:** 1.0 hours

**What We Accomplished:**

### 🎨 Refined Multi-line Border Box Styling
- **Problem**: Multi-line `#R#` border boxes showed horizontal lines between every wrapped row of text, and the borders were too close to the text on wrapped lines.
- **Solution**: 
  - Switched from `border` to `outline: 2px solid [color]`. Browsers render `outline` as a single, continuous outer path around the collective shape of wrapped text fragments, removing internal horizontal lines.
  - Used `outline-offset: 4px` instead of `padding` to provide consistent spacing from text across all lines.
  - Added `line-height: 1.5` to the span to ensure vertical spacing between rows within the border block.

### 📐 Vertical Alignment and Padding Fixes
- **Problem**: The initial line of a multi-line border box was slightly indented compared to subsequent lines.
- **Root Cause**: An asymmetrical horizontal `margin` was applied to the `inline` span, which only affected the start/end fragments of the wrapped text.
- **Solution**: Removed horizontal margins and padding, relying entirely on `outline-offset` for spacing. This ensures that every line of text in a wrapped block starts at the exact same horizontal offset, fixing vertical alignment.

### 🔧 Consistency and Export Sync
- **Live Sync**: Successfully implemented and verified these changes in the main application's markdown parser.
- **Export Parity**: Synchronized all styling refinements (outline, offset, line-height) to the `export_static.py` script to ensure exported HTML files match the application exactly.

**Files Modified:**
- `static/script.js` - Updated `parseMarkdownInline` and `oldParseMarkdownBody` with refined CSS.
- `export_static.py` - Synced CSS refinements to both JS-embedded logic sections.
- `md/PROBLEMS_AND_FIXES.md` - Documented the styling refinement and alignment fix.
- `md/RECENT.md` - Logged today's session and archived 11 older sessions.

**Current Status:**
- ✅ Multi-line border boxes are visually clean and professional.
- ✅ Left-alignment of wrapped text is perfectly consistent.
- ✅ Static exports are bit-for-bit visually identical to the live app for these features.

---

## [2026-02-06 16:15] - Table Formatting and UI Refinements

**Session Duration:** 0.5 hours

**What We Accomplished:**

### ✅ Final Fix for Nested Table Formatting (Stars and Punctuation)
- **Problem**: Mixing row-wrapped formatting with cell-specific styles caused rendering artifacts. Additionally, the `inline-block` border box implementation broke the "hanging indent" in table cells and sometimes misaligned text.
- **Solution**: 
  - **Indentation Flow Fix**: Reverted Border Box (`#R#`) to `display: inline` but removed `box-decoration-break: clone`. This allows the text to flow naturally with the cell's hanging indent while maintaining a single continuous border that doesn't "re-box" every line.
  - **Clipping Fix**: Maintained `overflow: visible` for `.md-cell` to ensure borders remain fully visible in all modes.
  - **Smart Detection**: Refined `distributeTableFormatting` with a "Local Closure Check" to accurately handle complex nested tags and trailing punctuation like `।`.
- **Consistency**: Synchronized all improvements across the live app and `export_static.py`.

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

*Sessions are moved to ARCHIVE_RECENT.md when this log exceeds 5 entries (excluding today's active work).*
