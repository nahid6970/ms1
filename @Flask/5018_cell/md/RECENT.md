# Recent Development Log

## [2026-06-17 18:45] - JSON UTF-8, Subsheet Drag Reorder, F9 Reorder GUI

**Session Duration:** 1.2 hours

**What We Accomplished:**

### 🔧 JSON UTF-8 encoding fix
- All `json.dump` / `open()` calls in `app.py` now use `encoding='utf-8'` and `ensure_ascii=False`.
- Bangla text is now stored as real characters in JSON files instead of `\u09xx` escape sequences.
- GitHub diffs will now show readable text changes instead of walls of escape codes.
- `quick_texts.json` already had this — fixed `data.json`, `custom_syntaxes.json`, `setting.json`, `sheet_active.json`.

### 🎯 Subsheet drag-to-reorder in dropdown
- Each subsheet item in the `⋮` dropdown now has a `⠿` drag handle on the left.
- Dragging inserts at the target position (shifts others), not swaps.
- Saves and re-renders immediately. Parent sheet row has no handle.

### 🎯 F9 upgraded to multi-part reorder GUI
- **2 parts**: still swaps directly (instant, no GUI).
- **3+ parts**: opens a modal GUI with:
  - Separator input with preset buttons: `,` `|` `&` `→`
  - Drag-to-reorder list
  - A→Z / Z→A sort buttons
  - Confirm / Cancel
- Separator spacing auto-detected from original text (e.g. ` | ` preserved as ` | `).
- Applies by writing directly to the hidden textarea (source of truth), avoiding contentEditable duplication bugs.

**Files Modified:**
- `app.py` — UTF-8 encoding + `ensure_ascii=False` on all JSON reads/writes.
- `static/script.js` — Subsheet drag reorder (insert logic), F9 reorder GUI (`showReorderGui`).
- `static/style.css` — `.subsheet-drag-handle` style.

**Current Status:**
- ✅ JSON files now store Bangla as readable text.
- ✅ Subsheets can be drag-reordered in the dropdown.
- ✅ F9 reorder GUI works with drag, sort, and preset separators.

---

## [2026-06-17 12:16] - Table Styling Overhaul

**Session Duration:** 0.6 hours

**What We Accomplished:**

### 🎨 Fix double border in rowspan tables (bolder middle row bug)
- Root cause: each `md-rowspan-row` cell had `border-top` + `border-bottom`, so adjacent rowspan rows doubled the border between them (2px instead of 1px).
- Fix: `md-rowspan-row` now only has `border-bottom`. Added new `md-rowspan-top` class (applied when previous row is NOT in the rowspan set) for the top border of each rowspan block.

### 🎨 Ruled table syntax `|━━━|━━━|━━━|`
- New separator row syntax using `━` (U+2501).
- Works like `|---|` (skipped from rendering, first row gets header style) but also adds `md-ruled` class to the grid → 1px `border-bottom` on every cell row.
- Header bottom border is 2px (bolder) to distinguish it from row separators.

### 🎨 Outer frame borders for all tables
- All `.md-grid` tables now have `border-top: 2px` and `border-bottom: 2px` on the container.
- First cell of every row gets `md-first-col` class → `border-left: 3px` (matching right column dividers).

**Files Modified:**
- `static/style.css` — `md-rowspan-row` border fix, new `md-rowspan-top`, `md-first-col`, `md-ruled`, `md-grid` outer borders.
- `static/script.js` — Added `isRuled` detection, `md-ruled` class on grid, `md-rowspan-top`, `md-first-col`, `md-first-row` classes in cell rendering.
- `export_static.py` — All above changes mirrored.

**Current Status:**
- ✅ Rowspan tables no longer have a bolder middle row.
- ✅ `|━━━|` ruled tables show row separators with header styling.
- ✅ All tables have a complete outer frame (top, bottom, left, right borders).

---

## [2026-06-16 14:35] - Sheet Index Copy Format

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 Sheet index copied in `[[I:index:sheetname]]` format
- `setAndCopySheetIndex` now copies `[[I:indexvalue:sheetname]]` instead of bare index value.
- Works in both cases: newly set index and already-existing index.

**Files Modified:**
- `static/script.js` — updated `setAndCopySheetIndex` copy text format.

**Current Status:**
- ✅ Clicking `#` copies `[[I:20260616143000:SheetName]]` to clipboard.

---

## [2026-06-16 14:21] - Fix Sheet Index Copy & Variable Font Size Default

**Session Duration:** 0.1 hours

**What We Accomplished:**

### ✅ Sheet index copy when already set
- Clicking `#` (Set & Copy Sheet Index) now copies the index even when it's already set.
- Root cause: `navigator.clipboard.writeText()` silently fails when index already exists (no fetch delay = no active user gesture context). Fixed by adding `execCommand('copy')` fallback via a temporary textarea.
- Warning toast still shows unchanged.

### 🎨 Variable font size default changed to 1.5
- Both prompts in `applyVariableFontSize` (contentEditable and legacy input paths) now default to `1.5` instead of `2`.

**Files Modified:**
- `static/script.js` — `setAndCopySheetIndex` with execCommand fallback; `applyVariableFontSize` default prompt value.

**Current Status:**
- ✅ `#` button always copies index (new or existing).
- ✅ Font size prompt defaults to 1.5×.

---

## [2026-06-16 12:08] - Custom Syntax Font Size Unit Changed to em

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎨 Font size in Custom Color Syntax now uses `em` (relative)
- Changed from `px` to `em` to match the existing `#2#text#/#` variable font size syntax.
- Input field updated: placeholder `em`, min `0.5`, max `5`, step `0.1`, value parsed as `float`.
- Updated all 5 locations where `fontSize` is applied in style strings (`customColorSyntaxesCache` builder, `rebuildCustomSyntaxCache`, `applyCustomColorSyntaxes` ×2, preview box in settings row).

**Files Modified:**
- `static/script.js` — all `fontSize` style outputs changed from `px` to `em`, input field attributes updated.

**Current Status:**
- ✅ Custom syntax font size is relative (e.g. `1.5` = 1.5× cell font size).

---

## [2026-06-16 11:49] - UI Polish & Custom Syntax Font Size

**Session Duration:** 0.3 hours

**What We Accomplished:**

### 🎨 UI: Border-radius removed from all popups
- Added CSS overrides to set `border-radius: 0` on `.quick-formatter`, `.f1-popup`, `.modal-content`, `.recent-edits-popup`, `#quickTextPopup`.

### 🎨 F3 grid changed to 10 items per row
- Changed `.quick-formatter-options` grid from `repeat(8, 1fr)` to `repeat(10, 1fr)`.
- Updated `min-width` from `480px` to `600px` to fit 10 buttons.

### 🎯 Custom Color Syntax: Font Size option
- Added `fontSize` field to each custom syntax object (default empty = inherit).
- Added a number input (px) in the Format column of the custom syntax settings table.
- Preview box updates live with chosen font size.
- Added `rebuildCustomSyntaxCache()` helper — called on every `updateCustomSyntax` so changes apply immediately without reload.
- Fixed font size not applying in preview (non-edit) mode: added `fontSize` to `applyCustomColorSyntaxes()` and `applyCustomColorSyntaxesRaw()` (both occurrences).
- Font size also applied in edit/highlight mode via `customColorSyntaxesCache`.

### 🎨 Removed number input spinner arrows globally via CSS.

**Files Modified:**
- `static/style.css` — border-radius overrides, 10-col grid, spinner arrow removal.
- `static/script.js` — `rebuildCustomSyntaxCache()`, `fontSize` in cache build, `applyCustomColorSyntaxes`, `applyCustomColorSyntaxesRaw`, settings row UI, default object.

**Current Status:**
- ✅ All popup windows have square corners.
- ✅ F3 shows 10 buttons per row.
- ✅ Custom syntax font size works in both preview and edit mode.

---

## [2026-06-16 11:27] - Quick Texts Section in F3 Formatter

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🎯 Quick Texts Feature
- Added a new **"Quick Texts"** section in the F3 Quick Formatter, placed after the "Text Case" section.
- Section header matches the style of other F3 headers (centered, uppercase, blue) with an inline green `+` circle button.
- Clicking `+` opens a floating popup (not inline — doesn't expand the F3 panel) with a Name field and a Text textarea.
- Clicking **Save** adds the snippet to the section as a button. Each button has a red `×` dot at top-right to delete it.
- Clicking a saved text button inserts its text at the cursor position in the active cell (supports both contentEditable WYSIWYG mode and legacy input/textarea mode).
- Snippets persist across sessions via a new `quick_texts.json` file, saved/loaded through new API endpoints.

**Files Modified:**
- `app.py` — Added `QUICK_TEXTS_FILE` path constant and `/api/quick-texts` GET + POST endpoints.
- `templates/index.html` — Added Quick Texts section header (with `+` button), `#quickTextButtons` container, and `#quickTextPopup` floating form modal.
- `static/script.js` — Added `loadQuickTexts`, `saveQuickTextsToServer`, `renderQuickTextButtons`, `insertQuickText`, `showQuickTextForm`, `cancelQuickTextForm`, `saveQuickText` functions; added `loadQuickTexts()` call to init IIFE.

**Current Status:**
- ✅ Quick Texts section visible in F3 after Text Case.
- ✅ Add/save/delete snippets with JSON persistence.
- ✅ Inserting text works in both WYSIWYG and raw mode.

---

## [2026-06-14 21:06] - English to Bangla Number Conversion in F3 Formatter

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 F3 Number Conversion Button (১২৩)
- Added a new `১২৩` button in the F3 Quick Formatter, placed right after the existing `বাং` (Bangla Phonetic) button in the Text Case section.
- The button converts only English digits (0–9) in the selected text to Bangla digits (০–৯), leaving all other characters unchanged.
- Works in both contentEditable (WYSIWYG) mode and legacy input/textarea mode — mirrors the same dual-mode pattern as `changeTextCase`.
- New function: `convertNumbersToBangla(event)` in `static/script.js`.

**Files Modified:**
- `templates/index.html` — Added `১২৩` button after the `বাং` button in the F3 formatter.
- `static/script.js` — Added `convertNumbersToBangla()` function after `changeTextCase()`.

**Current Status:**
- ✅ Selecting any text and pressing F3 → `১২৩` converts all English numbers in selection to Bangla digits.

---

## [2026-06-13 15:11] - Fix Ctrl+Alt+Up/Down Not Persisting in Visual Mode

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 Ctrl+Alt Multi-Cursor Persistence in Visual Mode
- Fixed `Ctrl+Alt+Up` / `Ctrl+Alt+Down` edits resetting after page refresh in Visual Mode.
- Root cause: `syncMultiCursorValue` was reading `cell.parentElement.dataset.row` (the `<tr>`) to get the row index, but `data-row` is set on the `<td>` itself. This made `rowIndex` always `NaN`, so the `tableData` in-memory update was skipped and `saveData()` saved stale data.
- Fix: one-line change — `cell.parentElement.dataset.row` → `cell.dataset.row`.

**Files Modified:**
- `static/script.js` — Fixed `rowIndex` lookup in `syncMultiCursorValue`.

**Current Status:**
- ✅ `Ctrl+Alt+Up/Down` edits now persist after refresh in Visual Mode.

---

## [2026-06-13 00:10] - Visual Mode Ctrl+Alt Cursor Support

**Session Duration:** 0.0 hours

**What We Accomplished:**

### 🎯 Visual Mode Multi-Cursor Support
- Added contentEditable-aware multi-line cursor handling so `Ctrl+Alt+Up` / `Ctrl+Alt+Down` now work directly in Visual Mode.
- The visual editor now uses the same line/column cursor model as raw mode, but writes back through the preview instead of forcing a mode switch.
- Raw-mode helper fallback remains only for the other shortcut paths that still need it.

**Files Modified:**
- `static/script.js` — Added contentEditable-aware multi-line cursor handling and sync helpers.

**Current Status:**
- ✅ `Ctrl+Alt+Up/Down` now work in Visual Mode.

---

## [2026-06-13 00:00] - Visual Mode Line-Move Shortcut Persistence Fix

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 Visual Mode Shortcut Persistence
- Fixed `Alt+Up` / `Alt+Down` so moving selected lines in Visual Mode now updates the underlying cell value, not just the rendered editor DOM.
- Consolidated line-move logic so raw mode and visual mode share the same line reordering math.

**Files Modified:**
- `static/script.js` — Visual-mode line move persistence and Ctrl+Alt arrow behavior.

**Current Status:**
- ✅ Alt-based line moves persist after refresh in Visual Mode.
- ✅ Ctrl+Alt arrow shortcuts now work from Visual Mode by switching into Raw Mode correctly.

---

## [2026-06-12 18:10] - AI API Endpoints for Sheet/Cell Access

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🎯 AI-Accessible REST API (`/ai/*`)
- Added 6 new endpoints to `app.py` so any AI agent can read and modify sheet/cell data over HTTP.
- `GET /ai/schema` — returns all sheets with arrayIndex, customIndex, name, category, colCount, rowCount.
- `GET /ai/sheet/<id>` — returns full sheet (all rows, columns, cellStyles).
- `GET /ai/cell/<id>/<row>/<col>` — reads a single cell value + style.
- `POST /ai/cell/<id>/<row>/<col>` — updates a single cell `{"value": "..."}`.
- `POST /ai/cells` — batch update multiple cells across any sheets.
- `GET /ai/find?sheet=<id>&q=<text>` — case-insensitive cell search, returns row/col indexes.
- `<id>` accepts both **arrayIndex** (integer) and **customIndex** (14-digit timestamp string).
- Added `AI_API.md` to project root as a reference doc for AI agents.

**Files Modified:**
- `app.py` — Added `resolve_sheet()` helper and all 6 `/ai/*` endpoints.
- `AI_API.md` — New file at project root with full usage guide and examples.

**Current Status:**
- ✅ All AI endpoints live and functional after Flask restart.
- ✅ customIndex lookup works alongside arrayIndex.
- ✅ Writes save to disk and auto-export static HTML.

---

## [2026-05-20 00:05] - F1 UI Compacting, Drag Indicator & Export Sheet Links

**Session Duration:** 0.4 hours

**What We Accomplished:**

### 🎨 F1 Popup Compacting
- Removed "Categories" label text; centered action buttons (➕ ⬆️ ⬇️) in the title bar.
- Reduced category panel width (250→180px), item padding, font sizes, sheet item padding, sheet list gap, separator margins.

### 🎯 F1 Drag & Drop Indicator
- Replaced blue border highlight on hovered sheets with an orange glowing dot (`#ff9d00`) on the left/right edge of the target sheet.
- Dragged sheet fades to 30% opacity; custom compact drag ghost shows just the sheet name.
- Dot uses `drop-before`/`drop-after` CSS classes with padding shift so it doesn't overlap text.

### ✅ Static Export Sheet Link Navigation
- `[[I:index]]` and `[[S:name]]` links in static export were not navigating — the click handler was missing entirely.
- Added `sheet-link` click handler to the document click listener in `export_static.py`.
- Also synced `customIndex` lookup to both `[[I:]]` parse locations in `export_static.py` (regex `\d+` → `\w+`).

**Files Modified:**
- `static/style.css` — F1 compact styles, drop indicator, dragging opacity.
- `static/script.js` — Drag indicator logic (classes instead of DOM element), custom drag ghost, clientX axis fix.
- `templates/index.html` — Removed Categories label, centered buttons.
- `export_static.py` — Added sheet-link click handler, synced customIndex `[[I:]]` parsing.

**Current Status:**
- ✅ F1 popup is more compact and readable.
- ✅ Drag indicator shows correctly as an orange dot.
- ✅ `[[I:]]` and `[[S:]]` links work in static export.

---

## [2026-05-19 23:33] - Datetime-Based Custom Sheet Index

**Session Duration:** 0.3 hours

**What We Accomplished:**

### 🎯 Custom Sheet Index Feature
- **`#` Button**: Added a `#` button to the header action pill (beside `⋮` and `+`) that sets a datetime-based custom index on the current sheet and copies it to clipboard.
- **Index Format**: `YYYYMMDDHHmmss` (e.g. `20260519232412`) — unique per second, no duplication possible.
- **No Overwrite**: If an index is already set, clicking `#` shows a red toast and does nothing.
- **`[[I:Index]]` Links**: Updated both parsing locations to resolve `customIndex` first (by scanning `sheet.customIndex`), then fall back to array position. Regex updated from `\d+` to `\w+` to support the longer timestamp format.
- **Copy Sheet Index**: `copySheetIndex()` now copies `customIndex` if set, otherwise falls back to array position.
- **Context Menus**: "Set Index" was added then removed from all right-click menus (F1, subsheet bar, tree) — only the `#` header button remains.

**Files Modified:**
- `app.py` — Added `POST /api/sheets/<index>/set-custom-index` endpoint.
- `static/script.js` — Added `setSheetCustomIndex()`, `setAndCopySheetIndex()`, updated `[[I:Index]]` parsing (×2), updated `copySheetIndex()`.
- `templates/index.html` — Added `#` button to header action pill.

**Current Status:**
- ✅ `#` button sets and copies a unique datetime index in one click.
- ✅ Index is permanent — cannot be overwritten accidentally.
- ✅ `[[I:20260519232412]]` links resolve correctly.

---

## [2026-05-17 11:15] - Syntax Template Engine & Multi-Level List Sorting

**Session Duration:** 2.5 hours

**What We Accomplished:**

### 🚀 Syntax Template Engine Upgrade
- **Numbered Placeholders**: Upgraded Syntax Replacer to support up to 9 capture groups (`text1`...`text9`).
- **Template Replacement**: Users can now define complex transformation templates (e.g., `text1 -> text2` converted to `text1 (text2)`).
- **Smart Regex Generation**: 
  - Implemented **Greedy matching** (`(.*)`) for placeholders at the end of a find pattern to ensure full line capture.
  - Retained **Non-greedy matching** (`(.*?)`) for middle placeholders to ensure precise delimiter detection.
- **Side-Specific Toggles**: Added "Both", "Left", and "Right" modes with exclusive side removal.
- **Recent History**: Persistent storage for the last 5 successful templates with quick re-apply functionality.

### 🔢 Multi-Level List Sorting Fix
- **Deep Nesting Support**: Updated `sortLines` and `sortLinesBanglaDate` to recognize nested lists beyond 2 levels.
- **Regex Detection**: Replaced explicit double-dash checks with a regex (`/^--+\s/`) that handles `---`, `----`, and deeper levels.
- **Structural Integrity**: Ensured that deep-nested sub-items correctly "stick" to their parent items during sorting rather than jumping to the top of the cell.

### 🎨 UI/UX and Documentation
- **UI Placeholders**: Updated Syntax Replacer modal with examples for template usage and numbered placeholders.
- **Feature Docs**: Fully updated `md/FIND_REPLACE_SYNTAX.md` with template engine logic, examples, and side-specific rules.

**Files Modified:**
- `static/script.js` — Core logic for Template Engine, Greedy matching, and Multi-dash sorting.
- `templates/index.html` — UI for history, side toggles, and template instructions.
- `md/FIND_REPLACE_SYNTAX.md` — Comprehensive feature update.
- `md/RECENT.md` — Development logging.

**Current Status:**
- ✅ Template Engine is robust and handles trailing text correctly.
- ✅ Complex list structures (3+ dashes) now sort correctly.
- ✅ History and UI provide a smooth workflow for repetitive tasks.

---

## [2026-05-09 23:23] - Move Single Row Controls to TH Header Toggle Container

**Session Duration:** 0.4 hours

**What We Accomplished:**

### 🎨 Header Toggle Container Refactor
- **Moved Single Row Controls**: Removed `prevSingleRow`, `toggleSingleRowMode`, and `nextSingleRow` buttons from the toolbar in `index.html` and added them into the `header-toggle-container` span rendered inside the first `<th>` column header in `script.js`.
- **Grouped with Border**: Wrapped the three single-row buttons in a `<span class="header-toggle-group">` with a visible blue border to visually separate them from the toolbar/tabs/subsheet toggles.
- **SVG Icons**: Replaced all emoji buttons in the header toggle container with clean SVG icons (hamburger, tab, folder, chevron-left, row-focus, chevron-right).
- **Reordered**: Moved Sheet Tabs toggle to first position in the container.
- **Vertical Alignment**: Added `align-items: center` to both `.header-toggle-container` and `.header-toggle-group`.
- **Arrow Disabled State Fix**: Fixed `prevDisabled`/`nextDisabled` in `renderTable()` to use actual `singleRowIndex` position (first/last row) instead of just `!singleRowMode`, so arrows correctly disable on refresh.
- **Null Guard Fix**: Added null checks in `updateSingleRowButtons()` and `toggleSingleRowMode()` to prevent crash before `renderTable()` creates the header buttons.
- **Arrow Color**: Gave `#btnPrevRow` and `#btnNextRow` a solid blue background with white SVG strokes, distinct from the center toggle button's light blue style.

**Files Modified:**
- `static/script.js` — Moved single row buttons into `header-toggle-container`, added SVG icons, fixed disabled state logic, added null guards.
- `static/style.css` — Added `.header-toggle-group`, `.btn-header-toggle svg`, arrow button color rules, `align-items: center` fixes.
- `templates/index.html` — Removed single row buttons and separator from toolbar.

**Current Status:**
- ✅ Single row controls live in the TH header alongside toolbar/tabs/subsheet toggles.
- ✅ Arrow buttons correctly disabled at first/last row on refresh.
- ✅ All buttons use clean SVG icons.
- ✅ Arrow buttons visually distinct with solid blue bg + white icon.

**Known Issues:**
- None

---

## [2026-05-07 11:15] - Sub-Sheet Search Bar & Filtering

**Session Duration:** 0.4 hours

**What We Accomplished:**

### 🔍 Sub-Sheet Search
- **Search Bar**: Added a search input at the top of the sub-sheet dropdown menu.
- **Real-time Filtering**: Sub-sheets are filtered dynamically as the user types, matching against the sheet name.
- **Auto-Focus**: The search input automatically receives focus when the dropdown is opened for immediate searching.
- **Visual Feedback**: Added a "No results" message when no sub-sheets match the filter.
- **Static Export Parity**: Fully implemented the search functionality in the `export_static.py` script to ensure standalone files have the same capabilities.

### 🎨 UI/UX Refinement
- **Improved Visibility**: Added subtle borders to the sub-sheet "Add" (+) and "Dropdown" (⋮) buttons.
- **Compact Layout**: Reduced padding, gaps, and font sizes within the sub-sheet dropdown to allow more items to be visible simultaneously.
- **Cyberpunk Styling**: Styled the search bar to match the dark green/black cyberpunk aesthetic.
- **Layout Adjustments**: Reorganized the dropdown to use a flex-column layout with a scrollable items container below the fixed search bar.

**Files Modified:**
- `static/script.js` — Refactored `renderSubSheetDropdown` and added `renderSubSheetList` with filtering logic.
- `static/style.css` — Added styles for `.subsheet-search-wrapper`, `#subsheetSearchInput`, and `.subsheet-items-container`.
- `export_static.py` — Synchronized search logic and styling for static exports.
- `md/UX_NAVIGATION.md` — Updated documentation to include the Search Bar feature.
- `md/RECENT.md` — Added this log.

**Current Status:**
- ✅ Sub-sheets can be quickly found via search.
- ✅ Search works in both main app and static exports.
- ✅ Flexible height remains functional with the new search bar.
- ✅ Horizontal scrollbar issue on hover fixed.

**Known Issues:**
- None

### 🐛 Bug Fixes
- **Layout Fix**: Fixed an issue where a horizontal scrollbar would appear in the sub-sheet dropdown when hovering over items. This was caused by the hover "nudge" effect (`translateX`) pushing content beyond the container's width.
- **Border Visibility**: Fixed clipping of the right border on hover by adding a small `margin-right` to the items, providing enough buffer for the `translateX` animation within the hidden-overflow container.

---

## [2026-05-07 10:45] - Flexible Sub-Sheet Window Height

**Session Duration:** 0.3 hours

**What We Accomplished:**

### ↔️ Flexible Sub-Sheet Window
- **Dynamic Sizing**: The sub-sheet dropdown menu (both in-app and static export) now dynamically calculates available window height.
- **Scrollbar Implementation**: Removed fixed `400px` height constraint. The window now expands to the bottom of the viewport and displays a scrollbar only when content overflows.
- **Improved UX**: Users with many sub-sheets can now view more items simultaneously without being restricted by a small fixed window size.
- **Consistency**: Applied the same logic to the `subsheet-more-dropdown` (overflow tabs) to ensure consistent behavior across all sub-sheet navigation elements.

**Files Modified:**
- `static/script.js` — Updated `toggleSubSheetDropdown` to calculate `maxHeight` dynamically.
- `static/style.css` — Removed fixed `400px` height and replaced with flexible `vh` units for `.subsheet-dropdown-menu` and `.subsheet-more-dropdown`.
- `export_static.py` — Synchronized dynamic height logic and CSS updates for the static export version.
- `md/UX_NAVIGATION.md` — Updated documentation to reflect flexible height behavior.
- `md/RECENT.md` — Added this log.

**Current Status:**
- ✅ Sub-sheet dropdown adapts to window height.
- ✅ Scrollbars appear correctly when content overflows.
- ✅ Static export maintains functional parity with the main app.

**Known Issues:**
- None

---

## [2026-04-28 13:47] - Move Subsheet to Main Sheet via Context Menu

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🎯 Promote Subsheet to Main Sheet
- **Feature**: Right-clicking a subsheet tab in the subsheet bar now shows a ⬆️ **Move to Main Sheet** option.
- **Logic**: Added `promoteToMainSheet(sheetIndex)` which deletes the `parentSheet` property from the sheet, making it a top-level sheet.
- **Category Safety**: The promoted sheet inherits its parent's category so it appears in the correct category group — no cross-category bleed.
- **Index Safety**: No sheets are reordered or spliced, so all `sheetCategories` indices remain intact.
- **Visibility**: The menu item only appears for actual subsheets (those with `parentSheet` set), not for the parent tab.

**Files Modified:**
- `static/script.js` — Added `promoteToMainSheet()` function and conditional menu item in `showSubSheetContextMenu`.

**Current Status:**
- ✅ Right-click on subsheet tab shows "Move to Main Sheet" option.
- ✅ Promoted sheet becomes a top-level sheet in the same category.
- ✅ File indexing and category assignments remain consistent.

**Known Issues:**
- None

---

## [2026-04-27 16:15] - Isolated Category Colors & Documentation Update

**Session Duration:** 0.6 hours

**What We Accomplished:**

### 🎨 Color System Refinement
- **Category Isolation**: Removed aggressive color inheritance where category styles (bg/fg) were leaking into the main sheet header and sub-sheets.
- **Header Cleanup**: Standardized the main sheet title and action pill to use theme-default colors (cyberpunk green/black) instead of inheriting category colors.
- **Sub-sheet Consistency**: Sub-sheets (both in the bar and the new dropdown) now only use their own specific colors or the default theme.
- **F1/Sidebar Focus**: Category colors are now strictly visual aids for the F1 navigation window and the sidebar tree view.

### 🚀 Toolbar & Header Enhancements
- **Search Box Relocation**: Moved the search box from the secondary toolbar to the main header, positioned conveniently to the left of the Bookmark button.
- **Improved Header Compactness**: Integrated search into the `.sheet-controls` group, freeing up vertical space in the secondary toolbar.
- **Ribbon Toggle Sync**: Search box now toggles visibility along with the main sheet header (F4).
- **Refined Event Handlers**: Cleaned up `static/script.js` to prevent redundant style applications during `renderSidebar` and `renderSubSheetBar`.
- **Documentation Sync**: Updated `UX_NAVIGATION.md` and `RECENT.md` to reflect these behavioral changes.

**Files Modified:**
- `static/script.js` - Removed inheritance logic from `renderSubSheetBar`, `renderSubSheetDropdown`, and `renderSidebar`.
- `md/RECENT.md` - Added this log.
- `md/UX_NAVIGATION.md` - Updated category color behavior description.

**Current Status:**
- ✅ Category colors no longer clash with sheet-level styling.
- ✅ Header UI remains clean and consistent across different categories.
- ✅ Documentation accurately reflects current behavior.

**Known Issues:**
- None

---

## [2026-04-27 15:30] - Enhanced Sub-sheet UI & Action Header

**Session Duration:** 0.8 hours

**What We Accomplished:**

### 🎨 Modernized Sub-sheet Navigation
- **Action Pill**: Grouped subsheet actions into a subtle "pill" container next to the main sheet name.
- **Improved Icons**: Replaced the hover dropdown with a vertical ellipsis (⋮) for the menu and a (+) button for quick adding.
- **Compact Dropdown**: Redesigned the subsheet dropdown to match the F2 cyberpunk aesthetic (dark green/black theme).
- **Alignment**: Standardized icons using flexbox and JetBrains Mono for perfect visual balance.

### 🔧 UI Logic Refinements
- **Conditional Visibility**: The ⋮ menu button now automatically hides if a sheet has no subsheets, reducing UI clutter.
- **Clean Titles**: Removed the dropdown arrow and functionality from the main sheet name to prevent accidental clicks.
- **Context Preservation**: Full right-click functionality (Rename, Delete, Colors) maintained in the new dropdown menu.
- **Positioning**: Dropdown now anchors precisely to the action pill.

**Files Modified:**
- `templates/index.html` - Restructured `current-sheet-info` and added the action pill.
- `static/style.css` - Overhauled dropdown, action buttons, and header layout styles.
- `static/script.js` - Updated `toggleSubSheetDropdown`, `renderSubSheetDropdown`, and `updateTreeUI` logic.

**Current Status:**
- ✅ Modernized, compact navigation for hierarchical sheets.
- ✅ Balanced and aligned header icons.
- ✅ Cleaner UI for sheets without children.

**Known Issues:**
- None

---

## [2026-04-18 23:49] - Fixed Image Markdown Bugs

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🐛 Fixed Image Regex in Static Export
- **Problem**: Images (`![alt](url)`) rendered as empty/nothing in static export HTML.
- **Root Cause**: Over-escaped regex in `export_static.py` — `!\\\[` produced `!\\[` in JS output, which matched a literal backslash instead of `![`.
- **Solution**: Corrected to `!\[([^\]]+)\]\(([^)]+)\)` (matching `script.js`) in both `parseMarkdownInline` and `oldParseMarkdownBody`.

### 🐛 Fixed Image Gap in Main App Preview
- **Problem**: Text after an image had an unwanted vertical gap.
- **Root Cause**: `.markdown-preview img` had `display: block` and `margin: 5px 0`.
- **Solution**: Changed to `display: inline; vertical-align: middle;`.

**Files Modified:**
- `export_static.py` - Fixed image regex escaping in `parseMarkdownInline` and `oldParseMarkdownBody`
- `static/style.css` - Fixed `.markdown-preview img` display/margin

**Current Status:**
- ✅ Images render correctly in static export
- ✅ No gap after images in main app preview

**Known Issues:**
- None

---

## [2026-04-18 11:45] - Image Markdown Support

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🖼️ New Image Markdown Support
- **Feature**: Added standard markdown image support `![alt](url)` with dimension extensions.
- **Extended Syntax**:
  - `![alt;width](url)`
  - `![alt;width;height](url)`
- **Styling**: 
  - Images automatically fit cell width (`max-width: 100%`).
  - Added specific `.markdown-preview img` styles in `static/style.css`.
- **Integration**:
  - **Live Preview**: Updated `static/script.js` (detection, parsing, and stripping).
  - **Static Export**: Updated `export_static.py` for consistent offline rendering.
  - **Documentation**: Added "Images" section to the Markdown Formatting Guide modal in `templates/index.html`.

**Files Modified:**
- `static/script.js` - Updated `checkHasMarkdown`, `parseMarkdownInline`, `oldParseMarkdownBody`, `stripMarkdown`.
- `export_static.py` - Updated `hasMarkdown` check and parsing functions.
- `static/style.css` - Added image-specific preview styles.
- `templates/index.html` - Updated Markdown Guide modal.
- `md/IMAGE_MARKDOWN.md` - Created new feature documentation.
- `md/RECENT.md`, `md/IMPLEMENTATION_SUMMARY.md`, `md/MARKDOWN_SPECIAL.md` - Updated references.

**Current Status:**
- ✅ Images render correctly in preview and static export.
- ✅ Custom sizing (width/height) supported.
- ✅ Accessibility (alt text) preserved.

**Known Issues:**
- None

---

## [2026-04-05 10:50] - Fixed Scrollbar Drag Lag in Visual Mode

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🐛 Fixed Intermittent Scrollbar Drag Lag
- **Problem**: Manually dragging the scrollbar in Visual Mode caused intermittent lag/stuttering. Mouse wheel scrolling was unaffected.
- **Root Cause**:
  - `position: sticky` on `th` headers forced layout recalculation on every scroll event (main thread).
  - No GPU layer promotion meant sticky headers were repainted from scratch each frame.
  - The scroll listener lacked `{ passive: true }`, blocking the compositor thread.
- **Solution**:
  - Added `will-change: scroll-position` + `contain: strict` to `.table-container` for GPU layer isolation.
  - Added `transform: translateZ(0)` + `will-change: transform` to `th` to promote sticky headers to their own compositor layers.
  - Added `{ passive: true }` to the scroll event listener so the browser can handle scroll on the compositor thread.

**Files Modified:**
- `static/style.css` - GPU promotion hints on `.table-container` and `th`
- `static/script.js` - `{ passive: true }` on scroll listener
- `SCROLL_LAG_BUG.md` - Marked as fixed with full root cause summary
- `md/PROBLEMS_AND_FIXES.md` - Logged fix
- `md/RECENT.md` - This entry

**Current Status:**
- ✅ Scrollbar drag is smooth in Visual Mode

**Known Issues:**
- None

---

## [2026-04-02 11:30] - Find & Replace Text & Searchable PDF Export

**Session Duration:** 1.2 hours

**What We Accomplished:**

### 🔍 New Find & Replace Text Feature
- **Feature**: Added a literal text search and replace tool in the F3 Quick Formatter.
- **UI**: Added a new SVG icon button (Magnifying glass with arrow 🔍➡️) to the F3 menu.
- **Modal**: Implemented a dedicated modal with:
  - **Find Text** and **Replace With** input boxes.
  - **Case Sensitive** toggle checkbox.
  - **Live Preview**: Shows occurrence count and a before/after snippet of the first match as you type.
- **Logic**: Uses regex (with automatic escaping of special characters) to perform global replaces while preserving cell state and triggering necessary input events.

### 📄 Professional PDF Export Enhancements
- **Custom Width**: Both PDF export methods now prompt for a layout width (default 800px) before generation.
- **🖨️ Print Cell (Selectable PDF)**: 
  - Added a second export option to the right-click context menu.
  - Uses a hidden iframe and the browser's native print dialog (`window.print()`).
  - Produces high-quality, **searchable and selectable** PDFs.
  - **Table Fix**: Included comprehensive CSS in the print view to prevent complex markdown tables from collapsing "line-by-line".
  - **Custom Color Syntax Fix**: Dynamically injects CSS for user-defined custom color syntaxes (like `¿¿text¿¿`) into the print view to ensure colors are preserved in the PDF.
  - **Font Support**: Injects JetBrains Mono, Vrinda, and KaTeX styles for consistent rendering.
- **Icon Update**: Replaced dual-emoji icons (🔍🔄, 🔍📜) with professional SVG icons in the F3 menu for a cleaner look.

**Files Modified:**
- `templates/index.html` - Added F3 button, Text Replacer modal, and new context menu option.
- `static/script.js` - Implemented `showTextReplacer()`, `applyTextReplace()`, `printCellToPDF()`, and updated `exportCellToPDF()`.
- `md/FIND_REPLACE_TEXT.md` - Created new feature documentation.
- `md/CELL_PDF_EXPORT_FEATURE.md` - Updated with custom width and searchable PDF details.
- `dev.md`, `md/KEYBOARD_SHORTCUTS.md`, `md/EDITING_EXTENSIONS.md`, `md/CELL_FEATURES.md` - Updated references.

**Current Status:**
- ✅ Find & Replace Text working with live preview.
- ✅ Professional selectable PDFs now support complex tables.
- ✅ UI icons modernized with SVGs.

**Known Issues:**
- None

---

## [2026-03-30 20:12] - Fixed Bengali Search Highlight & Scroll

**Session Duration:** 0.05 hours

**What We Accomplished:**
- Fixed highlight and scroll-to-match not working when searching Bengali vowel variants
- Root cause: `highlightMultipleTermsInHtml` compared raw cell text (e.g. `ী`) against normalized search term (`ি`), so no highlight spans were created and `searchMatches` stayed empty
- Fix: applied `normalizeBengali()` to `lowerText` inside `highlightMultipleTermsInHtml` (line 7817)

**Files Modified:**
- `static/script.js` — `normalizeBengali()` applied to `lowerText` in `highlightMultipleTermsInHtml`

**Current Status:**
- ✅ Bengali vowel variants now highlight and scroll correctly in sheet search

**Known Issues:**
- None

---

## [2026-03-30 20:08] - Bengali Vowel Sign Search Normalization

**Session Duration:** 0.1 hours

**What We Accomplished:**
- Added `normalizeBengali()` helper in `static/script.js` (near `stripMarkdown`)
- Maps `ী` (U+09C0) → `ি` (U+09BF) and `ূ` (U+09C2) → `ু` (U+09C1) so both forms match in search
- Applied to all search paths: sheet search (`searchTable`) and F1 window search (`filterF1Sheets`) — all 3 modes (`*`, `#`, normal)

**Files Modified:**
- `static/script.js` — Added `normalizeBengali()`, applied at 10 locations across both search functions

**Current Status:**
- ✅ Searching `ি` matches cells/sheets with `ী` and vice versa
- ✅ Searching `ু` matches cells/sheets with `ূ` and vice versa

**Known Issues:**
- None

---

## [2026-03-11 12:42] - Find & Replace Syntax Feature in F3 Formatter

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🔄 New Find & Replace Syntax Feature
- **Feature**: Added a powerful syntax replacement tool in F3 Quick Formatter
- **Button**: 🔄 icon button opens a modal for finding and replacing syntax patterns
- **Smart Detection**: 
  - Automatically scans entire cell and lists all found syntaxes
  - Groups custom colors by exact color values (e.g., `{fg:#ff0000}` separate from `{fg:#ffffff;bg:#000000}`)
  - Detects all standard syntaxes (bold, italic, highlights, etc.)
  - Detects user-defined custom syntax markers
- **Quick Replace Buttons**: 
  - One-click buttons for common replacements (Black, Red, Blue, Bold, Italic, Underline)
  - Dynamically shows all custom syntax markers with their colors
- **Live Preview**: Shows occurrence count and before/after example
- **Pattern Matching**: Uses `text` as placeholder to preserve content while changing syntax

**Files Modified:**
- `templates/index.html` - Added 🔄 button and Syntax Replacer modal
- `static/script.js` - Added `showSyntaxReplacer()`, `findAllSyntaxesInCell()`, `applySyntaxReplace()`, and helper functions
- `md/KEYBOARD_SHORTCUTS.md` - Added feature to F3 shortcuts list
- `md/FIND_REPLACE_SYNTAX.md` - Created comprehensive feature documentation

**Current Status:**
- ✅ Find & Replace Syntax feature working
- ✅ Detects all syntax types including custom ones
- ✅ Live preview shows changes before applying
- ✅ Custom syntax buttons appear dynamically

**Known Issues:**
- None
## [2026-03-10 14:15] - Fixed Title Spacing & Table Merging Issues

**Session Duration:** 0.4 hours

**What We Accomplished:**

### 🔧 Fixed Title Syntax Extra Line & Table Merging
- **Problem**: 
  1. Title syntax `:::K_5px_1em_f-K:::text:::` was creating an extra empty line after it.
  2. Attempting to fix the gap often caused tables to merge with the preceding line incorrectly.
- **Root Cause**: 
  - Redundant newlines were being added during the joining of block-level elements (titles, tables, etc.) in the Markdown renderer.
  - Since these elements already force a new line, the additional `\n` character in a `white-space: pre-wrap` container created an unwanted gap.
- **Solution**: 
  - **md-title Class**: Added the `md-title` class to title `div`s for reliable identification.
  - **Smart Block Joiner**: Updated `oldParseMarkdownBody` and `parseMarkdown` with a block-aware reducer that skips redundant newlines when joining block elements (titles, tables, separators, timelines, and lists).
  - **Table Refinement**: Refactored `Table*N` recursive parsing to prevent gaps before and after tables while maintaining user-intended spacing.
- **Result**: 
  - Clean layout with consistent spacing.
  - No more extra gaps after titles.
  - Tables remain distinct and don't merge with surrounding text.

**Files Modified:**
- `static/script.js` - Updated `highlightSyntax`, `oldParseMarkdownBody`, and `parseMarkdown` with smart joiner logic.

**Current Status:**
- ✅ Title syntax works without extra gaps
- ✅ Tables render correctly without merging
- ✅ User-intended empty lines are preserved

---

## [2026-03-10 00:31] - Fixed Title Syntax Extra Line Issue (Superseded)


## [2026-03-09 20:46] - Search Highlights in Edit Mode & F2 Scrollbar Fix

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🔍 Search Highlights Now Visible in Edit Mode
- **Problem**: When searching for text and clicking to edit a cell, the search highlights disappeared, making it hard to find the searched items.
- **Solution**: 
  - Modified focus event handler to preserve search highlights when entering edit mode
  - Added search highlight preservation during typing (when re-rendering for special formatting)
  - Search terms are re-applied using `highlightMultipleTermsInHtml()` after `highlightSyntax()`
- **Result**: Yellow search highlights remain visible while editing cells

### 🎨 Fixed F2 Horizontal Scrollbar
- **Problem**: F2 recent sheets popup showed an unwanted horizontal scrollbar at the bottom
- **Solution**: Added `overflow-x: hidden` to `.f2-sheets-list`
- **Result**: Clean popup without horizontal scrollbar

**Files Modified:**
- `static/script.js` - Updated preview focus and input event handlers to preserve search highlights
- `static/style.css` - Added overflow-x: hidden to F2 sheets list

**Current Status:**
- ✅ Search highlights visible in edit mode
- ✅ Highlights persist while typing
- ✅ F2 popup clean without horizontal scroll

---


## [2026-03-05 22:26] - Added Sub-sheet Dropdown to Current Sheet Title

**Session Duration:** 0.2 hours

**What We Accomplished:**

### 🎯 Added Quick Sub-sheet Access Dropdown
- **Feature**: Click on current sheet title (top-left) to show dropdown with all sub-sheets
- **Implementation**:
  - Dropdown shows parent sheet + all sub-sheets
  - Active sheet highlighted in blue
  - Custom colors from sheet/category settings applied
  - Right-click context menu (Rename, Set Colors, Delete)
  - "+ Add Sub-sheet" button at bottom
  - Click outside to close
  - Positioned directly below the sheet title text
  - Added ▼ indicator arrow that appears on hover

**Files Modified:**
- `templates/index.html` - Added dropdown container to current-sheet-info
- `static/style.css` - Added .subsheet-dropdown-menu styles and dropdown indicator
- `static/script.js` - Added toggleSubSheetDropdown() and renderSubSheetDropdown()

**Current Status:**
- ✅ Quick access to all sub-sheets from title
- ✅ Visual indicator shows it's clickable
- ✅ All customization features work (colors, context menu)
- ✅ Subsheet bar remains unchanged
- ✅ Dropdown positioned at sheet title location

---


## [2026-03-02 18:54] - Fixed Trailing Newlines and List Inline Display

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🐛 Fixed Accumulating Empty Lines at Cell End
- **Problem**: When editing cells, unnecessary empty lines kept accumulating at the end, eventually becoming huge and annoying.
- **Root Cause**: `extractRawText()` was adding newlines after DIV/P elements without trimming excessive trailing newlines.
- **Solution**: Added logic to trim multiple trailing newlines, keeping at most one.
- **Result**: No more accumulating empty lines during editing.

### 🐛 Fixed List Items Going to Second Line
- **Problem**: When typing multiple list items on the same line (e.g., `- item1 -- item2`), the second list would jump to a new line.
- **Root Cause**: `highlightSyntax()` wrapped list items in `<div>` with `display: block`, forcing them onto separate lines.
- **Solution**: Changed to `display: inline-block` to keep list items inline while maintaining hanging indent styling.
- **Result**: Multiple list items can now stay on the same line.

**Files Modified:**
- `static/script.js` - Updated `extractRawText()` and `highlightSyntax()` (~5 lines)

**Current Status:**
- ✅ No more trailing newline accumulation
- ✅ List items stay inline as expected

---


## [2026-02-28 10:30] - Fixed Cursor Navigation and Bengali Search Inconsistency

**Session Duration:** 0.7 hours

**What We Accomplished:**

### 🐛 Fixed Cursor Jump, Drift, and Arrow Navigation
- **Problem**: 
  1. Multi-line delete caused jumps to top.
  2. Editing caused drift in "wrong direction".
  3. ArrowUp/Down jumped to top/bottom instead of moving line-by-line.
- **Solution**: 
  - **Block Architecture**: Converted syntax-highlighted lines (tables, lists) from `inline-block` to `block` (DIV).
  - **Caret Optimization**: Removed redundant `<br>` tags following block elements in `highlightSyntax()`.
  - **Recursive Offsets**: Updated `extractRawTextBeforeCaret` and `setCaretPosition` to correctly handle element nodes and block newlines.
- **Result**: Smooth, reliable typing and navigation in Visual Mode.

### 🔍 Fixed Bengali Search Inconsistencies
- **Problem**: Bengali text was sometimes visible in cells but couldn't be found by the searchbox.
- **Root Cause**: Bengali characters can have multiple Unicode representations (e.g., combining characters vs. precomposed ones). Searching for one form while the sheet uses another leads to mismatch.
- **Solution**: 
  - **Unicode Normalization**: Implemented `NFC` (Canonical Composition) normalization in `searchTable()` for both the search query and the cell content.
  - **Consistency**: Applied normalization to both the main application (`static/script.js`) and the static export script (`export_static.py`).
- **Result**: Bengali search is now significantly more robust and reliable.

**Files Modified:**
- `static/script.js` - Updated `extractRawTextBeforeCaret`, `setCaretPosition`, `beforeinput`, `highlightSyntax`, and `searchTable` (~60 lines)
- `static/style.css` - Updated `.syntax-table-line` (~10 lines)
- `export_static.py` - Updated `searchTable` in embedded JS (~15 lines)

**Current Status:**
- ✅ Navigation is smooth.
- ✅ Bengali search is reliable.
- ✅ Export consistency maintained.

---

## [2026-02-25 16:13] - Fixed Cursor Jump on Multi-line Delete in Visual Mode

**Session Duration:** 0.1 hours

**What We Accomplished:**

### 🐛 Fixed Cursor Position Jump on Backspace
- **Problem**: When selecting multiple lines in visual mode (contentEditable) and pressing backspace, the cursor would jump to the top of the cell, requiring scrolling back to the edit location.
- **Root Cause**: The `beforeinput` event handler only prevented scroll jumps for `TEXTAREA` elements, not `contentEditable` divs used in visual/markdown mode. Additionally, cursor position wasn't preserved during delete operations.
- **Solution**: 
  - Extended scroll prevention to check for both `TEXTAREA` and `contentEditable` elements
  - Added cursor position preservation using `getCaretCharacterOffset()` before operation
  - Restored cursor position using `setCaretPosition()` after operation
  - Maintained scroll lock through multiple `requestAnimationFrame` calls
- **Result**: Cursor now stays at the deletion point when removing multi-line selections in visual mode.

**Files Modified:**
- `static/script.js` - Updated `beforeinput` event handler (~10 lines modified)

**Technical Details:**
- **Detection**: Added `isContentEditable` check alongside `isTextarea`
- **Cursor Preservation**: Saved offset before operation, restored in `setTimeout` after DOM update
- **Scroll Lock**: Existing triple `requestAnimationFrame` pattern now applies to contentEditable

**Current Status:**
- ✅ No scroll jump when deleting multi-line selection in visual mode
- ✅ Cursor stays at deletion point
- ✅ Works for backspace, delete, cut operations

**Time Spent:** 0.1 hours

---

## [2026-02-24 14:21] - Voice Search for Sheet Searchbox

**Session Duration:** 0.3 hours

**What We Accomplished:**

### 🎤 Voice Search Feature
- **Feature**: Added voice input to sheet searchbox with language toggle
- **Implementation**:
  - Added microphone button (CSS circle) next to search input
  - Web Speech API integration with `webkitSpeechRecognition`
  - Left-click: Start/stop voice recording
  - Right-click: Toggle English ↔ Bengali language
  - Visual indicators: Gray (English), Green (Bengali), Red pulsing (Recording)
  - Language preference saved to `localStorage` (persists across reloads)
- **Features**:
  - Interim results show as you speak
  - Final transcript triggers search automatically
  - Works with existing search features (comma-separated terms, markdown stripping)
  - `initVoiceLang()` restores language state on page load

**Files Modified:**
- `templates/index.html` - Added voice button with right-click handler
- `static/style.css` - Added `.btn-voice-search` styling with `.bengali` and `.listening` states, pulse animation
- `static/script.js` - Added voice search functions (~70 lines): `initVoiceLang()`, `toggleVoiceLang()`, `toggleVoiceSearch()`, `startVoiceSearch()`, `stopVoiceSearch()`

**Technical Details:**
- **API**: `webkitSpeechRecognition` (Chrome/Edge)
- **Languages**: `en-US` (English), `bn-BD` (Bengali)
- **Storage**: `localStorage.getItem/setItem('voiceLang')`
- **Permissions**: Requires microphone access (use `chrome://flags/#unsafely-treat-insecure-origin-as-secure` for localhost)

**Current Status:**
- ✅ Voice search works in both English and Bengali
- ✅ Language preference persists across page reloads
- ✅ Visual feedback for recording state
- ✅ Integrates seamlessly with existing search

**Time Spent:** 0.3 hours

---

## [2026-02-15 13:10] - Table Markdown Spanning in Static Export

**Session Duration:** 0.8 hours

**What We Accomplished:**

### 📊 Table Markdown Spanning for Static Export
- **Feature**: Synced the new table markdown spanning feature to `export_static.py`.
- **Implementation**:
  - Integrated the logic to track open/close state of delimiters across table cells into the embedded JS in `export_static.py`.
  - Removed the outdated `splitTableLine` function in favor of the new `parseGridTable` logic that matches `static/script.js`.
  - Fixed backslash escaping in the embedded JavaScript regex within the Python script to ensure proper rendering in exported HTML.
- **Improved Detection**:
  - Updated `hasMarkdown` check in `export_static.py` to include `customColorSyntaxes` detection, ensuring cells with custom highlighting are processed correctly during export.
- **Verification**:
  - Ran `export_static.py` and confirmed successful generation of `mycell.html` (5.9MB) without syntax errors.

**Files Modified:**
- `export_static.py` - Updated `parseGridTable`, removed `splitTableLine`, and refined `hasMarkdown` logic.
- `md/RECENT.md` - Added current session, archived oldest.
- `md/PROBLEMS_AND_FIXES.md` - Documented the export synchronization fix.

**Current Status:**
- ✅ Table markdown spanning works in both main app and static export.
- ✅ Custom color syntaxes are correctly detected in static export.
- ✅ Static export generates successfully without warnings.

**Next Steps:**
- Visually verify the exported HTML with complex spanning tables.

**Time Spent:** 0.8 hours

---

## [2026-02-15 12:20] - Nerd Font Support & Table Markdown Spanning

**Session Duration:** 0.5 hours

**What We Accomplished:**

### 🎨 Nerd Font Icon Support
- **Feature**: Added JetBrains Mono Nerd Font support for icon glyphs (, , etc.)
- **Implementation**:
  - Added Nerd Font to fallback chain: `'JetBrains Mono', 'JetBrainsMono Nerd Font', Vrinda, monospace`
  - Updated both main app (`static/script.js`) and export (`export_static.py`)
  - Icons display if Nerd Font is installed locally
- **Note**: Users should add a space after Nerd Font icons to prevent text overlap

### 📊 Table Markdown Spanning
- **Feature**: Markdown and custom color syntax can now span multiple table cells
- **Examples**:
  - `==Cell1 | Cell2 | Cell3==` → applies highlight to all three cells
  - `¿¿Cell1 | Cell2 | Cell3¿¿` → applies custom syntax to all cells
- **Implementation**:
  - Updated `parseGridTable()` to track open/close state of delimiters across cells
  - Each cell gets properly closed syntax: `==Cell1== | ==Cell2== | ==Cell3==`
  - Works with: `**`, `==`, `!!`, `??`, `@@`, `##`, `~~`, `<<`, `>>`, and custom syntax markers
- **Logic**: Tracks which delimiters are open, prepends them to next cell, closes them, and marks as open for following cells

**Files Modified:**
- `static/script.js` - Added Nerd Font fallback (3 lines), table spanning logic (~40 lines)
- `export_static.py` - Added Nerd Font fallback (1 line)
- `static/style.css` - Added letter-spacing for icon spacing
- `templates/index.html` - Restored Google Fonts link
- `md/CORE_SYSTEMS.md` - Documented Nerd Font support
- `md/TABLE_ADVANCED.md` - Documented markdown spanning feature
- `md/CUSTOM_SYNTAX.md` - Added table support section

**Current Status:**
- ✅ Nerd Font icons display correctly
- ✅ Markdown syntax spans multiple table cells
- ✅ Custom color syntax works across table cells
- ✅ Export HTML includes Nerd Font support

- ✅ Added **Use Last** button to the modal to reuse previous search/replace values.
- ✅ Persisted last used values using `localStorage` for cross-session use.
- ✅ Automatically triggers replacement preview when using last values.

### 🛠️ Sticky Edit Mode
- ✅ Added **Sticky Edit Mode** (📌 toggle) to prevent cells from exiting edit mode on blur.
- ✅ Persisted sticky mode state in `localStorage`.
- ✅ Implemented **Escape** key override to force-exit edit mode when sticky mode is active.
- ✅ Fixed **Sticky Edit Mode** exiting when using F3 Quick Formatter tools (added action cooldown check).
- ✅ Enhanced **Sticky Edit Mode** to persist state across cell re-renders (preserves `editing` class and focus when formatting is applied).
- ✅ Documentation updated in `md/WYSIWYG_EDIT_MODE.md`.

**Next Steps:**
- Test with various Nerd Font icon combinations
- Verify export HTML renders correctly

**Time Spent:** 0.5 hours

---

## [2026-05-18 09:00] - Internal Navigation & Sheet TOC
- **Feature**: Added internal sheet navigation using markdown syntax.
- **Syntaxes**:
  - `[[S:Sheet Name:Label]]`: Link by name with optional custom label.
  - `[[I:Index:Label]]`: Link by index with optional custom label.
  - `[[TOC]]`: Automatically generates a clickable Table of Contents.
- **Context Menu**: 
  - Added **"Copy Sheet Index"** to the cell context menu.
- **Styling**: Removed default underline from sheet links and added color inheritance.

---

## [2026-05-18 11:15] - F2 Popup Pinning & UI Refinement
- **Feature**: Added sheet pinning to F2 popup and compacted the UI.
- **Implementation**: Pinned sheets stay at the top; removed unnecessary "Recent Sheets" header; reduced padding/font sizes.

---

## [2026-05-18 13:45] - Single Row View Counter
- **Feature**: Added a row counter (e.g., "6/29") to Single Row View.
- **Interactivity**: The counter is now clickable to quickly disable Single Row Mode.
- **Styling**: Added hover effects and pointer cursor to the counter.

$content
$content
$content
