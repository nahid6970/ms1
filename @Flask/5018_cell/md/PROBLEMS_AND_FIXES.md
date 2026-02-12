# Problems & Fixes Log

This document tracks historical bugs, issues, and their solutions. Use this to:
- Understand past problems and how they were resolved
- Check if old fixes might conflict with new features
- Debug similar issues by referencing past solutions

---

## [2026-02-12 16:30] - List Formatting Not Updating in Edit Mode

**Problem:** 
When editing markdown cells with list items (e.g., `- item1`, `- item2`, `- item3`) and using backspace or delete to join multiple list lines into a single line, the visual display (list indentation styling) would not update immediately. The formatting only updated after exiting edit mode (blur event).

**Root Cause:** 
The `input` event handler in `applyMarkdownFormatting()` was intentionally not re-rendering content on every keystroke to avoid cursor jumping issues. The comment stated "DON'T re-render on every keystroke - the browser already updated the DOM." However, this prevented the `highlightSyntax()` function from being called when structural changes occurred (like line breaks being deleted), so line-based formatting like list indentation wouldn't update until blur.

**Solution:** 
1. Added smart re-rendering logic that detects when the line count changes (lines are joined or split).
2. Uses regex pattern `/^(\-{1,5})\s/m` with multiline flag to detect list formatting anywhere in the content.
3. Only triggers re-render when BOTH conditions are met:
   - Line count has changed (detected by counting `\n` characters)
   - Content contains special formatting (lists, pipe tables, or comma tables)
4. Preserves cursor position during re-render using `getCaretCharacterOffset()` before and `setCaretPosition()` after the `highlightSyntax()` call.
5. This ensures list indentation, table styling, and other line-based formatting updates immediately during editing without causing cursor jumping.

**Files Modified:**
- `static/script.js` - Updated `preview.addEventListener('input')` handler in `applyMarkdownFormatting()` function (around line 2610-2645)

**Related Issues:**
- This fix maintains the performance benefit of not re-rendering on every keystroke while solving the visual update issue for structural changes.
- The regex check is more robust than the previous string includes check.

---

## [2026-02-12 15:00] - Intelligent Scroll Memory in Single Row Mode

**Problem:** 
Moving between cells or rows in "Single Row View" would cause the scroll position to jump to previous positions or reset to 0, even with per-row state maps implemented. Focusing a cell at the bottom of a tall row would often "snap" the view back to the top.

**Root Cause:** 
1. **Wrapper Interference**: The global `renderTable` wrapper (which manages post-render height adjustments) was using global sheet scroll positions. In Single Row Mode, it would override the precise row restoration with a stale sheet-level position after a 350ms delay.
2. **Transition Overwrites**: Navigation functions were triggering state saves at moments where the browser hadn't yet updated the DOM, causing one row to "inherit" the scroll of the previous row.
3. **Natural Reflow Reset**: `adjustCellHeightForMarkdown()` temporarily cleared element heights to measure them. This caused the container height to shrink, forcing the browser to reset `scrollTop` to 0.

**Solution:** 
1. **Aware Wrapper**: Refactored the `renderTable` wrapper to be "Single Row Mode Aware." It now checks for the specific row's scroll position in the state map and uses it as the priority target for final restoration after all cells are adjusted.
2. **Atomic Navigation**: Standardized `nextSingleRow`/`prevSingleRow` to perform atomic updates: save outgoing scroll -> update index -> render with explicit flags to prevent stale data capture.
3. **Reflow Guard**: Updated `adjustCellHeightForMarkdown()` to save and restore the container scroll position around its height measurement logic, protecting the viewport from layout-induced jumps.
4. **Real-time Sync**: The global scroll listener now updates the per-row state map continuously, ensuring that any re-render always has the absolute latest coordinates.

**Files Modified:**
- `static/script.js`

---

## [2026-02-12 14:45] - Reliable Scroll Preservation in Single Row Mode (Initial Attempt)

**Problem:** 
Initial attempt to fix Single Row scroll issues.

**Solution:** Refactored `saveSingleRowState` and navigation functions. Superseded by 15:00 fix.

---

## [2026-02-12 14:30] - Scroll Position Resets in Cells and Single Row Mode (Initial Logic)

**Problem 1: Cell Internal Scroll Reset**
When editing a large cell in Visual Mode, clicking another cell (blur) caused the first cell to re-render its preview. This process reset the element's `scrollTop` to 0.

**Problem 2: Row Scroll Loss in Single Row Mode**
Navigating between rows lost the vertical place.

**Solution:** Initial implementation of `rowScrolls` map and blur scroll cache. (Superseded by 15:00 fix).

---

## [2026-02-12 14:00] - List Support in Table Cells

**Feature:** Added ability to use markdown lists (bullet and numbered) inside table cells.

**Solution:** Updated `parseMarkdownInline` (the specialized parser for cells) to detect `<br>` or `\n` and process lines individually. It now recognizes list markers like `- ` and `1. ` and applies the same rich formatting (hanging indents, icons) used in the main sheet.

**Files Modified:**
- `static/script.js`
- `export_static.py`
- `templates/index.html`

---

## [2026-02-12 13:30] - Syntax Corruption in Visual Mode

**Problem:** 
Occasionally, while editing a cell in Visual Mode (ContentEditable), all markdown syntax (like `**`, `__`) would be stripped, leaving only rendered icons like bullets (`•`) in the raw data.

**Root Cause:** 
A race condition in the `focus` event listener for the markdown preview.

**Solution:** Synchronous transition and fail-safe recovery logic in `extractRawText`.

**Files Modified:**
- `static/script.js`

---

## [2026-02-12 12:00] - Script Crash and Hiding Sheet Content

**Problem:** 
Application unresponsive after Syntax Inspector implementation.

**Solution:** Code cleanup and rendering safeguards in `renderTable`.

---

## [2026-02-12 11:30] - Syntax Reordering and Single Row Mode Scroll Fix

**Problem:** Formatting nesting control and scroll jump on untoggle.

**Solution:** Syntax Inspector feature and precise scroll restoration on untoggle.

---

## [2026-02-11 10:30] - Single Row Mode State Leaking Between Sheets

**Problem:** 
Global Single Row state affected all sheets.

**Solution:** Per-Sheet Persistence using `sheetSingleRowStates`.

---

## [2026-02-08 16:05] - Multi-line #R# Border Box Styling Refinement

**Problem:** 
Visual artifacts in multi-line border boxes.

**Solution:** Switched from `border` to `outline` with offset.

---

## [2026-02-06 16:45] - Text Overflow in #R# Border Boxes

**Problem:** 
Long unbroken text overflowing border boxes.

**Solution:** Changed style to `word-break: break-word`.

---

## [2026-02-06 16:15] - Sub-sheet Colors Not Working and Duplicate Context Menus

**Problem:** 
Custom colors and context menu options missing for sub-sheets.

**Solution:** Code consolidation and robust styling.

---

## [2026-02-06 15:45] - Sort Rank Gaps and Duplicate Numbers in Old Sheets

**Problem:** 
Stale sort rank data causing logic failures.

**Solution:** Global normalization on load and action.

---

## [2026-02-06 16:15] - Extra Stars and Detection Failures in Table Formatting

**Problem:** 
Table rendering artifacts with complex nested tags.

**Solution:** distribution logic refinement and punctuation support.

---

## [2026-02-06 14:55] - Sort Rank Gaps and Non-Contiguous Numbers

**Problem:** 
Missing numbers in sort rank sequences.

**Solution:** Normalization strategy.

---

## [2026-02-06 14:30] - Popup Management and Click-Outside Behavior

**Problem:** 
Overlapping popups and no click-outside dismissal.

**Solution:** Exclusive toggling and global click listeners.

---

## [2026-01-29 11:30] - F3 Formatter Link Removal Issue

**Problem:** 
Link stripping discarding URLs.

**Solution:** Preserved URL and text for all link syntaxes.

---

## [2026-01-26 17:15] - Recent Edits Popup Out-of-Sync and Layout Issues

**Problem:** 
Stale data and uncontrollable layout shifts in bookmarks.

**Solution:** Live fetching and height capping.

---

## [2026-01-26 16:15] - Scroll Position Lost After Clearing Search

**Problem:** 
Clearing search resetting scroll to top.

**Solution:** Visual offset capture and precision restoration.

---

## [2026-01-26 15:30] - Sheet Scroll Position Not Preserved After Reordering

**Problem:** 
Reordering sheets caused scroll positions to mismatch.

**Solution:** Switched storage key from index to name.

---

## [2026-01-23 13:30] - Excessive Spacing Below Tables (Smart Joiner)

**Problem:** 
Redundant vertical space after markdown tables.

**Solution:** "Smart Joiner" logic in parser.

---

## [2026-01-23 13:20] - Export Script Blank Page (JS Syntax Error)

**Problem:** 
Static export displaying blank page.

**Solution:** Escaped newlines in Python template.

---

## [2026-01-23 13:15] - Empty Lines Before/After Tables Not Showing

**Problem:** 
Empty lines disappearing around tables.

**Solution:** Simplified block-joining logic.

---

## [2026-01-23 12:25] - Custom Color Syntax Not Showing in Edit Mode

**Problem:** 
Styles lost when editing cells with custom colors.

**Solution:** Property mapping fix in highlightSyntax.

---

## [2026-01-23 12:10] - Markdown Preview Line Height Ignoring Tables

**Problem:** 
Settings not applying to table cells.

**Solution:** Variable-based line height in CSS.

---

## [2026-01-23 11:45] - F2 Popup Nickname Search Missing

**Problem:** 
Could not search by nickname in F2.

**Solution:** Added data-nickname attribute and search logic.

---

## [2026-01-23 11:27] - Table Shrinkage in Edit Mode

**Problem:** 
Table rows shrinking in WYSIWYG mode.

**Solution:** Span wrapping and line-height matching.

---

## [2026-01-18 01:25] - Table Border Color Defaulting to Faint Grey

**Problem:** 
Borders hard to see.

**Solution:** Defaulted to black borders.

---

## [2026-01-18 01:07] - Bold/Italic Not Rendering When KaTeX Present

**Problem:** 
Parsing conflict between KaTeX and markers.

**Solution:** Reordered parsing sequence.

---

## [2026-01-18 01:00] - List Detection Failed with KaTeX Math

**Problem:** 
List check failing after KaTeX transformation.

**Solution:** Used original line for detection.

---

## [2026-01-18 00:40] - Cursor Offset Mismatch in List Items

**Problem:** 
Inaccurate click-to-edit mapping in lists.

**Solution:** Preserved first character of list marker in map.

---

## [2026-01-18 00:30] - Cell Height Overflow in Edit Mode

**Problem:** 
Height not adjusting for raw syntax.

**Solution:** td height adjustment and focus/blur integration.

---

## [2026-01-17 23:55] - Bangla Text Overflow and Border Box Fixes

**Problem:** 
Glyphs cutting off in complex scripts.

**Solution:** Unified font (Vrinda) and increased preview padding.

---

## [2026-01-17 22:45] - Math Category Refinement and Git Workflow Setup

**Problem:** 
Cluttered F3 math section.

**Solution:** Simplified to 4 essential buttons.

---

## [2026-01-17 22:50] - Project Template Creation and Math Category Optimization

**Problem:** 
Inconsistent project setup.

**Solution:** Standardized guide and reordered buttons.

---

## [2026-01-17 22:55] - Header Z-Index Fix for Edit Mode Scrolling

**Problem:** 
Edit box covering headers.

**Solution:** Increased th z-index.

---

## [2026-01-17 23:00] - Code Formatting Bug Fix in Edit Mode

**Problem:** 
Malformed HTML breaking syntax highlighting.

**Solution:** Fixed closing tag in regex.

---

## [2026-01-17 23:10] - Superscript Mode Toggle Implementation

**Problem:** 
Conflict between math notation and markers.

**Solution:** Per-cell mode toggle.

---

## [2026-01-17 23:12] - Set Superscript Mode Default to Enabled

**Problem:** 
Manual configuration required for every cell.

**Solution:** Enabled by default for new styles.

---

## [2026-01-17 23:20] - LaTeX Math Syntax Support Implementation

**Problem:** 
AI-generated math not rendering.

**Solution:** LaTeX to KaTeX conversion across all parsers.

---

## [2026-01-17 23:35] - Superscript Toggle Fixed in Static Export (RESOLVED)

**Problem:** 
Toggle setting ignored in HTML files.

**Solution:** Synced cellStyle parameter to export parsers.

---

## [2026-01-17 22:15] - Square Root and Fraction Buttons Not Working in ContentEditable

**Problem:** 
F3 math buttons failed in Visual Mode.

**Solution:** Dual-mode support using Range API.

---

## [2026-01-17 21:30] - Double-Click Word Selection Includes Trailing Space

**Problem:** 
Messy word selection.

**Solution:** Custom double-click handler with range adjustment.

---

## [2026-01-17 21:00] - F3 Multi-Format Selection Issues

**Problem:** 
Multiple formats not applying correctly in Visual Mode.

**Solution:** Dual-mode applyMultipleFormats.

---

## [2026-01-17 20:30] - Link Syntax and Clear Format Behavior

**Problem:** 
Links using old syntax or being stripped entirely.

**Solution:** Updated Link format and stripMarkdown consistency.

---

## [2026-01-17 20:00] - Auto-Switch to Raw Mode for Multi-Cursor Features

**Problem:** 
Multi-cursor directing users to switch modes manually.

**Solution:** Automatic mode switching logic.

---

## [2026-01-17 19:00] - F3 Formatter Functions Not Working in ContentEditable

**Problem:** 
H+, Border Box, Sort, Lines/Comma failed in Visual Mode.

**Solution:** Dual-mode implementation for all 5 functions.

---

## [2026-01-17 18:30] - Alt+Up/Down Exits Edit Mode

**Problem:** 
Line movement triggering focus loss.

**Solution:** Silent tableData update and manual highlights.

---

## [2026-01-16 20:00] - Click-to-Edit Cursor Positioning Incorrect (RESOLVED)

**Problem:** 
Markers making visible offsets inaccurate.

**Solution:** Robust mapping via calculateVisibleToRawMap.

---

## [2026-01-16 18:15] - Multi-Line Cursor Selection Support

**Problem:** 
Cursors could only insert/delete, no selection.

**Solution:** Selection tracking and Shift+arrow support.

---

## [2026-01-16 18:00] - Multi-Line Cursor Visual Markers Not Updating

**Problem:** 
No visual feedback for multi-cursors.

**Solution:** Re-enabled markers and added arrow handling.

---

## [2026-01-16 17:45] - Multi-Cursor Home/End Not Consolidating Cursors Per Line

**Problem:** 
Duplicate cursors on same line.

**Solution:** Set-based consolidation.

---

## [2026-01-16 17:30] - Keyboard Shortcuts Not Working (F9, Ctrl+Shift+D, Ctrl+Alt+Arrows)

**Problem:** 
Conflict with browser defaults.

**Solution:** Capture phase listeners and preventDefault.

---

## [2026-01-16 17:00] - F3 Formatting Not Persisting After Refresh

**Problem:** 
Visual changes not saving to database.

**Solution:** Simplified sync to underlying hidden inputs.

---

## [2026-01-16 16:45] - F3 Quick Formatter Additional Functions Not Working

**Problem:** 
Case conversion and scroll jumping.

**Solution:** Dual-mode case change and scroll position caching.

---

## [2026-01-16 16:30] - Markdown Links Not Opening in Browser

**Problem:** 
Clicking links entered edit mode.

**Solution:** Intercepted mousedown/click on links.

---

## [2026-01-16 16:15] - F3 Quick Formatter Functions Not Working with ContentEditable

**Problem:** 
Table formatter and Clear buttons failed.

**Solution:** Dual-mode implementation and Range API integration.

---

## [2026-01-16 15:30] - Multiple Shortcut and Feature Fixes

**Problem:** 
Persistence and shortcut interference issues.

**Solution:** saveData in clear, prevented bookmark/rotation defaults.

---

## [2026-01-16 01:20] - F3 Quick Formatter Blur Handler Fix

**Problem:** 
Formatting disappearing briefly.

**Solution:** Added visibility check in blur listener.

---

## [2026-01-16 01:00] - F3 Quick Formatter Duplicate Functions Removed

**Problem:** 
Duplicate code overwriting fixes.

**Solution:** Deleted 785 redundant lines.

---

## [2026-01-16 00:45] - F3 Quick Formatter Contenteditable Support

**Problem:** 
F3 didn't open in Visual Mode.

**Solution:** Updated detection and selection logic.

---

## [2026-01-16 00:40] - WYSIWYG Enter Key Cell Expansion Fix

**Problem:** 
Cursor becoming invisible on Enter.

**Solution:** scrollIntoView and padding adjustments.

---

## [2026-01-16 00:30] - WYSIWYG Backspace/Delete Double-Press Fix

**Problem:** 
Invisible ZWS requiring double backspace.

**Solution:** Manual ZWS skip in keydown.

---

## [2026-01-16 00:25] - WYSIWYG Focus Scroll Prevention

**Problem:** 
Jumping to top on cell focus.

**Solution:** preventScroll and scroll-margin CSS.

---

## [2026-01-16 00:20] - WYSIWYG Data Save and Cell Height Fix

**Problem:** 
Data not saving and overflow in edit mode.

**Solution:** Direct tableData sync and maxHeight TD logic.

---

## [2026-01-16 00:15] - WYSIWYG Cursor Jump on Input

**Problem:** 
Re-rendering on every key jumpy.

**Solution:** Restricted re-render to focus/blur.

---

## [2026-01-15 23:45] - WYSIWYG Markdown Editing Implementation

**Problem:** 
Edit experience disconnected from preview.

**Solution:** contentEditable architecture with dual-rendering.

---

## [2026-01-15 23:30] - Reverted Forced Sheet Scrolling to Top

**Problem:** 
Disorienting jumping behavior.

**Solution:** Reverted to natural browser behavior.

---

## [2026-01-12 23:45] - PENDING: Markdown Edit to Raw Mode Scroll Jump

**Problem:** 
Switching modes while editing jumps to end.

**Status:** PENDING

---

## [2026-01-12 23:30] - F8 Word Pick Now Copies to Clipboard

**Problem:** 
User convenience.

**Solution:** Added clipboard copy to pick handler.

---

## [2026-01-12 23:00] - Click-to-Edit Cursor Visibility and Scroll Restore

**Problem:** 
Loss of vertical place after editing.

**Solution:** Scroll position caching around edit sessions.

---

## [2026-01-12 22:30] - Raw Mode Visual Indicator

**Problem:** 
Hard to tell active mode.

**Solution:** Color-coded toggle label.

---

## [2026-01-12 22:00] - Scroll Position Lost on Refresh and Raw Mode Toggle

**Problem:** 
Scroll jumps to top on mode changes.

**Solution:** 1s initialization delay and safe-adjust logic.

---

## [2026-01-12 21:30] - List Item Tab Alignment & Hanging Indent Issues

**Problem:** 
Misaligned lists.

**Solution:** inline-block lists with text-indent CSS.

---

## [2026-01-12 21:00] - Raw Mode Showing Text Twice

**Problem:** 
Visual artifacts in raw mode.

**Solution:** Restricted formatting to markdown-enabled state.

---

## [2026-01-12 20:30] - Raw Mode Cell Height Not Adjusting

**Problem:** 
Cut-off text in raw mode.

**Solution:** Direct scrollHeight measurement for textareas.
