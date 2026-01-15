# Problems & Fixes Log

This document tracks historical bugs, issues, and their solutions. Use this to:
- Understand past problems and how they were resolved
- Check if old fixes might conflict with new features
- Debug similar issues by referencing past solutions

---

## [2026-01-16 00:30] - WYSIWYG Backspace/Delete Double-Press Fix
**Problem:** 
In the contenteditable WYSIWYG editor, pressing Backspace or Delete required two presses to delete one character.

**Root Cause:** 
Zero-width spaces (`\u200B`) were inserted after `<br>` tags to make empty lines clickable. Backspace/Delete would first delete the invisible ZWS (no visible change), then the actual character.

**Solution:** 
Added keydown handlers for Backspace and Delete that detect if the adjacent character is a ZWS and automatically remove it before letting the default action continue.

**Files Modified:**
- `static/script.js` - Added ZWS skip logic in the keydown handler.

**Related Issues:** Enter key handling, empty line clicking.

---

## [2026-01-16 00:25] - WYSIWYG Focus Scroll Prevention
**Problem:** 
When clicking on a cell to edit, especially if scrolled far into a tall cell, the sheet would jump to position the cell's top border at the top of the viewport.

**Root Cause:** 
Browser default behavior scrolls focused elements into view. The `focus()` call on contenteditable elements triggered this.

**Solution:** 
Multiple fixes applied:
- Used `focus({ preventScroll: true })` when focusing the preview.
- Save and restore `tableContainer.scrollTop/scrollLeft` around focus events.
- Added CSS `scroll-margin: 0` to prevent browser scroll adjustments.

**Files Modified:**
- `static/script.js` - `handlePreviewMouseDown` and focus event listener.
- `static/style.css` - Added scroll-margin rules for `.markdown-preview`.

**Related Issues:** Click-to-Edit positioning.

---

## [2026-01-16 00:20] - WYSIWYG Data Save and Cell Height Fix
**Problem:** 
1. Data wasn't saving while typing in the WYSIWYG editor.
2. As content grew, text would overflow the cell border instead of expanding.
3. Calling `updateCell()` during input caused focus loss.

**Root Cause:** 
`updateCell()` calls `applyMarkdownFormatting()` which recreates the preview element, destroying the focused element. Height adjustment was based on the hidden input, not the visible preview.

**Solution:** 
- Save data directly to `tableData.sheets[currentSheet].rows[rowIndex][colIndex]` without calling `updateCell()`.
- Use debounced `saveData()` for backend persistence.
- Measure `preview.scrollHeight` directly and apply height to preview, input, and cell.

**Files Modified:**
- `static/script.js` - Refactored `input` event handler in `applyMarkdownFormatting`.

**Related Issues:** Focus loss during editing.

---

## [2026-01-16 00:15] - WYSIWYG Cursor Jump on Input
**Problem:** 
While typing, the cursor would jump around, sometimes to previous lines or the top of the cell.

**Root Cause:** 
The `input` event handler was re-rendering the entire content with `highlightSyntax()` on every keystroke, then attempting to restore the caret position. Offset calculation inconsistencies (especially with ZWS characters) caused mismatches.

**Solution:** 
Removed real-time re-rendering from the input handler. Now:
- Browser handles DOM updates natively (typing, deletion).
- Input handler only syncs data and adjusts height.
- Full re-render only happens on focus (to show syntax) and blur (to show preview).

**Files Modified:**
- `static/script.js` - Simplified `input` event handler.

**Related Issues:** Caret management, ZWS handling.

---

## [2026-01-15 23:45] - WYSIWYG Markdown Editing Implementation
**Problem:** 
Editing markdown using a transparent textarea overlay felt disconnected and didn't allow for real-time visual feedback of formatted text during editing. Syntax markers were often hard to manage.

**Root Cause:** 
Traditional `<textarea>` elements only support plain text, forcing a separate rendering layer (preview) to be overlaid on top.

**Solution:** 
Transitioned to a `contenteditable="true"` architecture:
- Replaced the transparent textarea with a dynamic `contenteditable` div.
- Implemented dual-rendering: `parseMarkdown()` for clean preview (blur) and `highlightSyntax()` for editing (focus).
- Added `extractRawText()` to reliably reconstruct markdown from the DOM.
- Implemented character-offset based caret management (`getCaretCharacterOffset` and `setCaretPosition`) to preserve cursor position during real-time re-highlighting.
- Styled syntax markers with `.syn-marker` class (0.6 opacity, normal font weight) to make them unobtrusive.

**Files Modified:**
- `static/script.js` - Major refactor of `applyMarkdownFormatting`, added `highlightSyntax`, `extractRawText`, caret helpers.
- `static/style.css` - Added `.syn-marker` and contenteditable focus styles.
- `md/WYSIWYG_EDIT_MODE.md` - New documentation.

**Related Issues:** Click-to-Edit cursor positioning.

---

## [2026-01-15 23:30] - Reverted Forced Sheet Scrolling to Top
**Problem:** 
A previously implemented feature forced the sheet to scroll so that the focused cell line was positioned at the very top (header) of the viewport. Users found this disorienting as it caused excessive "jumping" of the entire sheet.

**Root Cause:** 
Explicit `tableContainer.scrollTop` adjustments in `positionCursorAtMouseClick` and forced centering in cell `onclick` handlers.

**Solution:** 
Reverted the sheet-level scrolling logic to restore "normal" browser behavior:
- Removed `tableContainer.scrollTop` logic from `positionCursorAtMouseClick`.
- Removed `.onclick` handlers that called `keepCursorCentered` in `renderTable`.
- The system now relies on the browser's default focus mechanism, which avoids unnecessary sheet jumps.

**Files Modified:**
- `static/script.js` - Removed scroll logic in `positionCursorAtMouseClick`, removed handlers in `renderTable`.

**Related Issues:** Click-to-Edit scroll restore.

---

## [2026-01-12 23:45] - PENDING: Markdown Edit to Raw Mode Scroll Jump

**Problem:**
When exiting markdown edit mode and then switching to raw mode, the scroll jumps to the end of the sheet.

**Status:** PENDING - To be fixed later

**Related Issues:** Click-to-Edit scroll restore, Raw mode toggle

---

## [2026-01-12 23:30] - F8 Word Pick Now Copies to Clipboard

**Problem:**
When using F8 to pick a word under cursor/hover, users wanted the word to also be copied to clipboard for easy pasting elsewhere.

**Solution:**
Added clipboard copy functionality to F8 handler:
- Copies the picked word to clipboard before adding to search box
- Uses `execCommand('copy')` with a hidden textarea for reliable cross-browser support
- Shows toast notification confirming the copy

**Files Modified:**
- `static/script.js` - F8 handler (~line 515)

**Related Issues:** None

---

## [2026-01-12 23:00] - Click-to-Edit Cursor Visibility and Scroll Restore

**Problem:**
1. When clicking on markdown preview to edit, if the cursor position was far down in the cell content, users had to scroll to see it
2. After exiting edit mode (blur), the scroll position was lost and users couldn't find where they were
3. Switching between markdown and raw mode while editing caused scroll position issues

**Solution:**
Updated `positionCursorAtMouseClick()` to:
1. Always scroll the table container to position the cursor line immediately after the header (10px padding)
2. Save the original scroll position before scrolling
3. Add a blur event listener that restores the original scroll position when exiting edit mode
4. Use `e.relatedTarget` to detect if blur was caused by clicking toggle buttons - if so, skip restore and let `renderTable` handle scroll

This way users can see what they're editing at the top of the view, and when done, they return to their original position.

**Files Modified:**
- `static/script.js` - `positionCursorAtMouseClick()` (~line 5870)

**Related Issues:** Raw mode toggle scroll issues

---

## [2026-01-12 22:30] - Raw Mode Visual Indicator

**Problem:**
It was hard to tell when raw mode (markdown preview disabled) was active vs when markdown preview was enabled.

**Solution:**
- Added `.raw-mode-active` CSS class with orange background (`#fff3e0`) and border (`#ff9800`)
- Toggle function adds/removes this class on the button label
- Toast message now says "Raw mode enabled" instead of "Markdown preview disabled"
- Changed button icon to 📄 and updated tooltip

**Files Modified:**
- `static/style.css` - Added `.raw-mode-active` styles (~line 418)
- `static/script.js` - `toggleMarkdownPreview()` and initialization (~line 5712, ~line 187)
- `templates/index.html` - Updated button title and icon (~line 149)

**Related Issues:** None

---

## [2026-01-12 22:00] - Scroll Position Lost on Refresh and Raw Mode Toggle

**Problem:**
1. Page refresh caused scroll to jump to top
2. Toggling to raw mode (disabling markdown preview) caused scroll to jump to top
3. Toggling back to markdown mode worked fine

**Root Cause:**
1. The scroll event listener was saving `0` to localStorage during initial page load before the saved position could be restored
2. `adjustAllMarkdownCells()` ran after scroll restore attempts, causing layout changes that reset scroll
3. The `renderTable` wrapper's height adjustment timeout (300ms) happened after scroll restore (0-300ms)

**Solution:**
1. Added 1-second delay before scroll save listener becomes active (`initialLoadComplete` flag)
2. `adjustAllMarkdownCells()` now saves/restores scroll position around height adjustments
3. `renderTable` wrapper now saves scroll from both localStorage and current position, then restores AFTER `adjustAllMarkdownCells()` completes (350ms)

**Files Modified:**
- `static/script.js` - Scroll save listener (~line 93), `adjustAllMarkdownCells()` (~line 9814), `renderTable` wrapper (~line 9848)

**Related Issues:** Raw mode cell height adjustment

---

## [2026-01-12 21:30] - List Item Tab Alignment & Hanging Indent Issues

**Problem:** 
1. Tab characters within list items (`- item`) weren't aligning properly across different list items
2. When list content wrapped to the next line, it didn't indent to align with text after the bullet
3. Longer words like `সম্প্রসারণ` needed extra tabs to align with shorter words

**Root Cause:**
List items were using `display: inline-flex` with `width: 100%` and `flex: 1` on the content span. Flex containers don't preserve tab alignment the same way as normal text flow.

**Solution:**
Changed list rendering to use:
- `display: inline-block; width: 100%` instead of `display: inline-flex`
- `text-indent: -1em; margin-left: 1em` for proper hanging indent
- `white-space: pre-wrap` on content to preserve tabs
- Added `tab-size: 8` to CSS for consistent tab rendering

**Files Modified:**
- `static/script.js` - List parsing in `oldParseMarkdownBody()` (~line 2253)
- `static/style.css` - Added `tab-size` to `td input`, `td textarea`, `.markdown-preview`
- `export_static.py` - Matching list parsing updates

**Related Issues:** None

---

## [2026-01-12 21:00] - Raw Mode Showing Text Twice

**Problem:**
When markdown preview was disabled (raw mode), cell content appeared twice - both the input/textarea and a preview overlay were visible.

**Root Cause:**
The CSS that hid the markdown preview in raw mode was commented out, but the `applyMarkdownFormatting()` function was still creating preview elements even in raw mode.

**Solution:**
Updated `applyMarkdownFormatting()` to check `isMarkdownEnabled` early and:
- Remove existing preview element
- Remove `has-markdown` class from input
- Return early without creating new preview

The CSS `.hide-markdown-preview .markdown-preview { display: none }` was kept commented out since previews are no longer created in raw mode.

**Files Modified:**
- `static/script.js` - Early return in `applyMarkdownFormatting()` (~line 1380)

**Related Issues:** Raw mode cell height (see below)

---

## [2026-01-12 20:30] - Raw Mode Cell Height Not Adjusting

**Problem:**
In raw mode (markdown preview disabled), cells weren't expanding to show all content. The last lines of text were cut off.

**Root Cause:**
`adjustCellHeightForMarkdown()` required both an input AND a preview element to exist, and checked for `has-markdown` class. In raw mode, previews are removed and `has-markdown` class is removed, so the function returned early without adjusting height.

**Solution:**
Updated `adjustCellHeightForMarkdown()` to:
1. Check if markdown is enabled
2. In raw mode (no preview), resize textareas based on `scrollHeight` directly
3. Updated `adjustAllMarkdownCells()` to process all textareas in raw mode, not just those with `has-markdown` class

**Files Modified:**
- `static/script.js` - `adjustCellHeightForMarkdown()` (~line 9727), `adjustAllMarkdownCells()` (~line 9798)

**Related Issues:** Raw mode text showing twice (fixed above)

---

## Template for New Entries

```markdown
## [YYYY-MM-DD HH:MM] - Brief Problem Title

**Problem:** 
Description of the issue observed

**Root Cause:** 
What was actually causing the problem

**Solution:** 
How it was fixed (include key code changes)

**Files Modified:**
- `file1.js` - Brief description of change
- `file2.css` - Brief description of change

**Related Issues:** Links to related problems or "None"
```
