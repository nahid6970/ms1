# Problems & Fixes Log

This document tracks historical bugs, issues, and their solutions. Use this to:
- Understand past problems and how they were resolved
- Check if old fixes might conflict with new features
- Debug similar issues by referencing past solutions

---

## [2026-01-17 22:45] - Math Category Refinement and Git Workflow Setup

**Problem:**
Math category had too many buttons (12 total) making it cluttered, and needed to establish proper Git commit workflow with documentation updates.

**Root Cause:**
Initial implementation added all possible math symbols without considering UI focus and usability. Also lacked structured Git workflow.

**Solution:**
1. **Simplified Math category** to 4 essential buttons:
   - Moved superscript (X^2^) and subscript (X~2~) from main section to Math
   - Removed 10 math symbol buttons (×, ÷, ±, ≠, ≤, ≥, ≈, ∞, π, α)
   - Kept core functions: √ (Square Root), a/b (Fraction), X^2^, X~2~

2. **Enhanced documentation system**:
   - Added `#[[file:md/RECENT.md]]` reference in DEVELOPER_GUIDE.md
   - Clarified archiving process (move to ARCHIVE_RECENT.md, don't delete)
   - Established Git commit rules with emoji messages

3. **Code cleanup**:
   - Removed unused `applyMathFormat()` function (~60 lines)
   - Updated documentation to reflect changes

**Files Modified:**
- `templates/index.html` - Math category refinement
- `static/script.js` - Removed applyMathFormat() function
- `md/KEYBOARD_SHORTCUTS.md` - Updated documentation
- `DEVELOPER_GUIDE.md` - Enhanced Recent.md integration
- `md/RECENT.md` - Updated with session details
- `md/ARCHIVE_RECENT.md` - Created archive template

**Related Issues:** F3 formatter organization, documentation system, Git workflow

**Result:** Cleaner, more focused Math category with 4 essential buttons and established documentation/Git workflow.

---

## [2026-01-17 22:50] - Project Template Creation and Math Category Optimization

**Problem:**
Need reusable project template for future projects and Math category button order could be improved for better UX.

**Root Cause:**
No standardized project setup template available, and Math category had less commonly used functions (√, a/b) before more basic ones (superscript, subscript).

**Solution:**
1. **Created PROJECT_TEMPLATE_GUIDE.md**:
   - Complete project setup checklist with directory structure
   - Documentation templates (RECENT.md, PROBLEMS_AND_FIXES.md, etc.)
   - Git workflow with emoji commit guidelines
   - Technology-specific customization guide
   - Ready-to-use file templates (README.md, .gitignore)

2. **Reordered Math category buttons** for logical flow:
   - X^2^ (Superscript) → First (most common)
   - X~2~ (Subscript) → Second (very common)
   - √ (Square Root) → Third (specialized)
   - a/b (Fraction) → Fourth (advanced)

3. **Enhanced DEVELOPER_GUIDE.md** with complete Git workflow documentation

**Files Modified:**
- `templates/index.html` - Math category button reordering
- `DEVELOPER_GUIDE.md` - Added Git Commit Workflow section
- `PROJECT_TEMPLATE_GUIDE.md` - Created comprehensive project template
- `md/RECENT.md` - Updated session details

**Related Issues:** Project setup efficiency, UX optimization, documentation standardization

**Result:** Reusable project template created and Math category optimized for better user experience.

---

## [2026-01-17 22:55] - Header Z-Index Fix for Edit Mode Scrolling

**Problem:**
When in contentEditable edit mode and scrolling the sheet, the edit box would cover/interrupt the table headers, causing them to disappear from view.

**Root Cause:**
Z-index conflict - table headers (`th`) had `z-index: 10` while contentEditable cells in edit mode had `z-index: 100`, causing edit boxes to render above the headers during scrolling.

**Solution:**
Increased table headers' z-index from `10` to `200` to ensure they always stay above edit boxes and remain visible during scrolling.

**Files Modified:**
- `static/style.css` - Updated `th` selector z-index property

**Related Issues:** UI layering, edit mode UX, header visibility

**Result:** Table headers now remain visible and properly positioned above edit boxes during scrolling in edit mode.

---

## [2026-01-17 23:00] - Code Formatting Bug Fix in Edit Mode

**Problem:**
When using backticks for code formatting like `text`, it rendered correctly in markdown preview mode but in edit mode everything after the opening backtick appeared as code formatting, breaking the rest of the text.

**Root Cause:**
The `highlightSyntax()` function had malformed HTML in the code formatting regex - it was using `</strong>` closing tag instead of `</code>`, creating invalid HTML that broke the parsing and affected subsequent text formatting.

**Solution:**
Fixed the backtick formatting rule in `highlightSyntax()` function by changing the closing tag from `</strong>` to `</code>`:

**Before:**
```javascript
formatted = formatted.replace(/`(.*?)`/g, '<code><span class="syn-marker">`</span>$1<span class="syn-marker">`</span></strong>');
```

**After:**
```javascript
formatted = formatted.replace(/`(.*?)`/g, '<code><span class="syn-marker">`</span>$1<span class="syn-marker">`</span></code>');
```

**Files Modified:**
- `static/script.js` - highlightSyntax() function code formatting rule

**Related Issues:** Edit mode syntax highlighting, HTML parsing, code formatting

**Result:** Code formatting with backticks now works correctly in both preview and edit modes without affecting other text.

---

## [2026-01-17 23:10] - Superscript Mode Toggle Implementation

**Problem:**
Syntax conflict between math notation (`2^3 = 8`) and superscript formatting (`x^2^`). Users needed ability to control when `^text^` should be parsed as superscript vs displayed as normal text for mathematical expressions.

**Root Cause:**
The parsing functions always converted `^text^` to superscript formatting, making it impossible to display mathematical expressions like `2^3` without unwanted formatting.

**Solution:**
Implemented per-cell superscript mode toggle:

1. **Added context menu option**: "^Superscript^ Mode" in right-click cell menu
2. **Per-cell control**: Each cell stores `superscriptMode` property in cell styles
3. **Conditional parsing**: Modified parsing functions to only convert `^text^` when mode is enabled:
   - `parseMarkdown(text, cellStyle = {})`
   - `parseMarkdownInline(text, cellStyle = {})`
   - `oldParseMarkdownBody(lines, cellStyle = {})`
4. **Multi-cell support**: Toggle works with multiple selected cells
5. **Visual feedback**: Checkmark indicator shows current state

**Technical Implementation:**
```javascript
// Conditional superscript parsing
if (cellStyle.superscriptMode) {
    formatted = formatted.replace(/\^(.+?)\^/g, '<sup>$1</sup>');
}
```

**Files Modified:**
- `templates/index.html` - Added context menu option
- `static/script.js` - Added toggleSuperscriptMode() and updated parsing functions

**Related Issues:** Math notation conflicts, syntax parsing, context menu functionality

**Result:** Users can now control per-cell whether `^text^` displays as normal text (for math) or superscript formatting (for variables).

---

## [2026-01-17 23:12] - Set Superscript Mode Default to Enabled

**Problem:**
Superscript mode was disabled by default, requiring users to manually enable it for each cell. Since most cells use `^text^` for superscript formatting, this created unnecessary workflow friction.

**Root Cause:**
The `getCellStyle()` function returned undefined for `superscriptMode` by default, which was treated as false/disabled in the parsing logic.

**Solution:**
Modified `getCellStyle()` function to return `superscriptMode: true` as the default value for new cells:

```javascript
// Set default values for new cells
if (style.superscriptMode === undefined) {
    style.superscriptMode = true; // Default to enabled
}
```

**Files Modified:**
- `static/script.js` - Updated getCellStyle() function default behavior

**Related Issues:** User workflow optimization, default behavior, superscript parsing

**Result:** New cells now have superscript mode enabled by default, making `^text^` work immediately without manual configuration. Existing cells maintain their current settings for backward compatibility.

---

## [2026-01-17 23:20] - LaTeX Math Syntax Support Implementation

**Problem:**
AI assistants provide math solutions in LaTeX format (`$\sqrt{25}$`, `$\log_2 8 = 3$`) but the application only supported KaTeX syntax (`\(...\)`), causing AI-generated math to display as raw text instead of rendered mathematics.

**Root Cause:**
The parsing functions only recognized KaTeX `\(...\)` syntax and didn't convert the standard LaTeX `$...$` format that AI assistants commonly use.

**Solution:**
Implemented LaTeX to KaTeX conversion across all parsing functions:

1. **Conversion Logic**: Added `text.replace(/\$([^$]+)\$/g, '\\($1\\)')` to convert `$math$` → `\(math\)`
2. **JavaScript Functions Updated**:
   - `parseMarkdownInline()` - Inline math parsing
   - `oldParseMarkdownBody()` - Main text parsing
   - `highlightSyntax()` - Edit mode syntax highlighting
   - `stripMarkdown()` - Search/sort functionality
   - `checkHasMarkdown()` - Markdown detection
3. **Python Export Support**: Updated `export_static.py` parseMarkdown functions
4. **Detection Enhancement**: Added `$` detection to hasMarkdown checks

**Technical Implementation:**
```javascript
// Convert LaTeX $...$ syntax to KaTeX \(...\) syntax
formatted = formatted.replace(/\$([^$]+)\$/g, '\\($1\\)');
```

**Files Modified:**
- `static/script.js` - Added LaTeX conversion to 5 parsing functions
- `export_static.py` - Added LaTeX conversion to export functions

**Related Issues:** AI compatibility, math rendering, LaTeX vs KaTeX syntax

**Result:** AI-generated math content now renders properly. Users can copy-paste math solutions from AI assistants and they display as beautiful mathematical notation instead of raw LaTeX code. Both `$...$` and `\(...\)` syntaxes work seamlessly.

---

## [2026-01-17 22:15] - Square Root and Fraction Buttons Not Working in ContentEditable

**Problem:**
The Square Root (√) and Smart Fraction (a/b) buttons in the F3 formatter were not working in contentEditable (preview edit) mode, similar to other F3 functions that were previously fixed.

**Root Cause:**
The `applySqrtFormat()` and `applyHatFormat()` functions were only written for INPUT/TEXTAREA elements using `.value`, `.selectionStart`, `.selectionEnd` properties, which don't exist in contentEditable mode.

**Solution:**
Updated both functions to support dual modes:
1. **ContentEditable mode:**
   - Check `quickFormatterSelection.isContentEditable` at the start
   - Extract selected text from `quickFormatterSelection.text`
   - Use Range API to insert/replace text with `range.deleteContents()` and `range.insertNode()`
   - Update underlying input with `extractRawText()`
   - Trigger input event for auto-save
   - Set cursor position with `setCaretPosition()`

2. **INPUT/TEXTAREA mode:**
   - Use existing logic with `.value` and `.setSelectionRange()`

**Files Modified:**
- `static/script.js` - applySqrtFormat (~line 8642), applyHatFormat (~line 8676)

**Related Issues:** F3 Quick Formatter, contentEditable support, Math category

**Note:** This follows the same pattern used to fix other F3 formatter functions like H+, Border Box, Sort Lines, etc. All F3 formatter functions now support both contentEditable and legacy input modes.

---

## [2026-01-17 21:30] - Double-Click Word Selection Includes Trailing Space

**Problem:**
When double-clicking on a word in contentEditable mode, the browser's default behavior would select the word plus any trailing whitespace. For example, double-clicking "abcd" in "abcd abc" would select "abcd " (with the space).

**Root Cause:**
Browser default double-click behavior includes trailing whitespace in word selection for easier text manipulation (e.g., cut/paste operations).

**Solution:**
Added custom double-click handler for contentEditable preview elements:
1. Intercept the double-click event
2. Check if selection ends with whitespace using regex `/\s$/`
3. Count trailing whitespace characters
4. Adjust the range's end position backward to exclude trailing spaces
5. Update the selection with the trimmed range

**Files Modified:**
- `static/script.js` - preview double-click handler (~line 2140)

**Related Issues:** ContentEditable, text selection, UX improvement

**Result:** Clean word selection without trailing spaces in contentEditable mode.

---

## [2026-01-17 21:00] - F3 Multi-Format Selection Issues

**Problem:**
1. Multi-format selection (right-click to select multiple formats, left-click to apply all) was not working in contentEditable mode
2. When clicking on a format that was already selected, it would apply that format twice (once from selectedFormats array, once as the clicked format)

**Root Cause:**
1. The `applyMultipleFormats()` function only handled INPUT/TEXTAREA with `.value` property, not contentEditable
2. The function always added the last clicked format without checking if it was already in the selectedFormats array

**Solution:**
1. Added full contentEditable support to `applyMultipleFormats()`:
   - Check `quickFormatterSelection.isContentEditable`
   - Use Range API to insert formatted text
   - Update underlying input with `extractRawText()`
   - Trigger input event for auto-save
2. Added duplicate detection:
   - Check if `lastPrefix|lastSuffix` key exists in selectedFormats
   - Only add the last clicked format if it's not already selected
   - Adjust format count in toast message accordingly

**Files Modified:**
- `static/script.js` - applyMultipleFormats (~line 8719)

**Related Issues:** F3 Quick Formatter, multi-format selection, contentEditable

**Usage:**
- Right-click on format buttons (Bold, Italic, Underline, etc.) to select them
- Checkmarks (✓) appear on selected formats
- Left-click any format button to apply all selected formats at once
- Works in both raw mode and preview edit mode

---

## [2026-01-17 20:30] - Link Syntax and Clear Format Behavior

**Problem:**
1. Link button in F3 formatter was using old syntax `{link:url}text{/}`
2. When using "Clear Format" button, the new link syntax `url[text]` would be completely removed, losing the URL

**Root Cause:**
1. `applyLinkFormat()` was hardcoded to use old syntax and didn't support contentEditable
2. `stripMarkdown()` was converting `url[text]` → `text`, discarding the URL

**Solution:**
1. Updated `applyLinkFormat()` to:
   - Use new syntax: `url[text]` instead of `{link:url}text{/}`
   - Support contentEditable mode with Range API
   - Keep old syntax working for backward compatibility
2. Updated `stripMarkdown()` to:
   - Convert new syntax: `url[text]` → `url text` (keeps both URL and text)
   - Convert old syntax: `{link:url}text{/}` → `text` (keeps only text)

**Files Modified:**
- `static/script.js` - applyLinkFormat (~line 8071), stripMarkdown (~line 7280)

**Related Issues:** Link formatting, F3 Quick Formatter, stripMarkdown

**Note:** Both link syntaxes work for rendering. The new syntax is cleaner and preserves more information when clearing formats.

---

## [2026-01-17 20:00] - Auto-Switch to Raw Mode for Multi-Cursor Features

**Problem:**
Multi-cursor and multi-selection features (Ctrl+Shift+D, Ctrl+Alt+Up/Down, Select All Matching button) only work in raw mode, but users had to manually switch modes when trying to use them in preview mode.

**Root Cause:**
These features require direct text manipulation with `.value`, `.selectionStart`, `.selectionEnd` properties that don't exist in contentEditable. They were showing toast messages directing users to switch modes manually.

**Solution:**
Implemented automatic mode switching:
1. Created `enableRawMode()` helper function to programmatically switch to raw mode
2. Updated all three feature handlers to:
   - Detect if in contentEditable (preview) mode
   - Call `enableRawMode()` to switch automatically
   - Show toast: "Switched to Raw Mode for [feature name]"
   - Wait 100ms for table re-render
   - Focus the appropriate input/textarea in the same cell
   - For text-based features, try to restore the selection

**Files Modified:**
- `static/script.js` - enableRawMode (~line 6557), Ctrl+Shift+D handler (~line 700), Ctrl+Alt+Up/Down handlers (~line 716, 732), selectAllMatchingOccurrences (~line 9142)

**Related Issues:** Multi-cursor, multi-selection, mode switching, UX improvement

**Features Affected:**
- 🎯 Select All Matching button (F3 formatter)
- Ctrl+Shift+D (Select Next Occurrence)
- Ctrl+Alt+Up/Down (Multi-line cursor)

---

## [2026-01-17 19:00] - F3 Formatter Functions Not Working in ContentEditable

**Problem:**
Several F3 Quick Formatter functions were not working in contentEditable (preview edit) mode:
1. H+ (Variable Font Size) - `#2#text#/#` syntax
2. Border Box (□) - `#R#text#/#` syntax
3. Sort Lines (🔤)
4. Lines to Comma (➡️)
5. Comma to Lines (⬇️)

**Root Cause:**
These functions only handled INPUT/TEXTAREA elements using `.value`, `.selectionStart`, `.selectionEnd` properties, which don't exist in contentEditable mode.

**Solution:**
Updated all five functions to support both modes:
1. Check `quickFormatterSelection.isContentEditable` at the start
2. For contentEditable:
   - Extract selected text from `quickFormatterSelection.text`
   - Use Range API to insert/replace text
   - Update underlying input with `extractRawText()`
   - Trigger input event for auto-save
   - Set cursor position with `setCaretPosition()`
3. For INPUT/TEXTAREA:
   - Use existing logic with `.value` and `.setSelectionRange()`

**Files Modified:**
- `static/script.js` - applyVariableFontSize (~line 12048), applyBorderBox (~line 12147), sortLines (~line 12252), linesToComma (~line 12412), commaToLines (~line 12492)

**Related Issues:** F3 Quick Formatter, contentEditable support

---

## [2026-01-17 18:30] - Alt+Up/Down Exits Edit Mode

**Problem:**
Using Alt+Up/Down to move lines in contentEditable mode would work but then exit edit mode, forcing the user to click back into the cell.

**Root Cause:**
The `moveLines()` function was updating the underlying input element and triggering an `input` event, which caused a blur/focus cycle that exited edit mode.

**Solution:**
Changed the update strategy for contentEditable mode:
1. Update contentEditable with `highlightSyntax()` instead of plain text
2. Update tableData directly without triggering input events
3. Update input.value silently (no event dispatch)
4. Call `saveData()` directly for background persistence
5. Restore cursor position with `setCaretPosition()`

**Files Modified:**
- `static/script.js` - moveLines (~line 800)

**Related Issues:** Alt+Up/Down, line movement, contentEditable, edit mode

---

## [2026-01-16 20:00] - Click-to-Edit Cursor Positioning Incorrect (RESOLVED)

**Problem:**
When clicking on markdown preview to enter edit mode, the cursor appeared at the wrong position. For example:
- Raw input: `"##This Text Is Big Text## This Is Normal Text"`
- User clicks on "This Text Is Big Te|" (after 19 visible characters)
- Expected: Cursor at raw position 21 (accounting for opening `##`)
- Actual: Cursor at raw position 19 (inside the visible content, ignoring markdown syntax)

The offset is calculated from the rendered HTML (visible text without markdown syntax), but needs to be mapped to the raw input (with syntax like `##`, `**`, `@@`, etc.).

**Root Cause (Resolved by Gemini):**
The initial approach tried to use `stripMarkdown()` on partial substrings to build a mapping, but regex patterns like `/##(.+?)##/g` need to see the complete pattern to match. When called on partial strings like `"##T"`, the regex doesn't match, so nothing gets stripped, resulting in 1:1 mapping.

**Solution (Implemented by Gemini):**
Created `calculateVisibleToRawMap()` function that:
1. Parses the full string once to identify all markdown patterns
2. Marks hidden ranges (which character positions are syntax vs content)
3. Builds a mapping by walking through and counting only non-hidden characters
4. Uses this mapping to convert visible offset to raw offset

**Why It Works:**
- Regex patterns match on the full string where patterns are complete
- Marks which parts are syntax vs content
- No need to call `stripMarkdown()` multiple times
- Handles all patterns including custom syntaxes

**Files Modified:**
- `static/script.js` - calculateVisibleToRawMap (~line 1402), handlePreviewMouseDown (~line 1520)
- `md/PROBLEMS_AND_FIXES.md` - Updated with resolution
- `md/CLICK_TO_EDIT_CURSOR_POSITIONING.md` - Updated with solution details

**Related Issues:** Edit mode, cursor positioning, markdown syntax

**Key Learning:**
The fundamental mistake was assuming `stripMarkdown()` would work on partial strings. Regex patterns need complete patterns to match. The solution was to parse once, mark ranges, then map - a much more robust approach.

---

## [2026-01-16 18:15] - Multi-Line Cursor Selection Support

**Problem:**
Multi-line cursors (Ctrl+Alt+Up/Down) could only insert/delete text at cursor positions. There was no way to select text on multiple lines simultaneously or move cursors by word boundaries, making it difficult to select and replace different words on each line.

**Root Cause:**
The multi-line cursor system only tracked cursor positions (line, column), not selections. The keydown handler didn't support Shift+arrow keys or Ctrl+Space for word navigation.

**Solution:**
1. Added selection tracking to cursor objects: `selectionStart` and `selectionEnd` properties
2. Implemented Shift+arrow key support (Shift+Left, Shift+Right, Shift+Home, Shift+End) to extend selections
3. Added Ctrl+Space to move cursors to next word boundary (stops at spaces and special characters)
4. Updated `handleMultiLineCursorMove()` to handle selection extension with `extendSelection` parameter
5. Modified typing/deletion logic to handle selections (replace selected text when typing, delete selection on Backspace/Delete)
6. Enhanced `showCursorMarkers()` to visualize selections with blue highlight overlays (rgba(0, 123, 255, 0.3))
7. Native cursor on last line shows native selection, other lines show CSS selection highlights

**Files Modified:**
- `static/script.js` - setupMultiLineCursorListener (~line 9518), handleMultiLineCursorMove (~line 9633), showCursorMarkers (~line 9344), getAbsolutePosition helper (~line 9710)

**Related Issues:** Multi-cursor editing, Ctrl+Alt+arrows

**Usage:**
- Ctrl+Alt+Down/Up: Add cursors on adjacent lines
- Shift+Home/End: Select from cursor to line start/end on all lines
- Shift+Arrow: Extend selection character by character
- Ctrl+Space: Jump to next word boundary
- Type: Replace all selections with typed text
- Backspace/Delete: Delete all selections

---

## [2026-01-16 18:00] - Multi-Line Cursor Visual Markers Not Updating

**Problem:**
When using Ctrl+Alt+Up/Down to create multi-line cursors, the visual cursor markers were disabled (commented out). When re-enabled, they didn't update when moving cursors with arrow keys, and the last cursor showed both a CSS marker and the native cursor (double cursor).

**Root Cause:**
1. Visual cursor markers (`showCursorMarkers`) were commented out in both `addCursorBelow/Above` and the keydown listener, likely due to previous issues
2. Arrow key navigation wasn't implemented for multi-line cursors - they only worked for typing/deleting
3. The `showCursorMarkers` function was showing markers for ALL cursors including the last one, causing a double cursor effect

**Solution:**
1. Re-enabled `showCursorMarkers()` calls in `addCursorBelow()` and `addCursorAbove()`
2. Added arrow key handling in the keydown listener (ArrowLeft, ArrowRight, Home, End, Escape)
3. Created `handleMultiLineCursorMove()` function to update cursor positions and refresh visual markers when arrow keys are pressed
4. Updated `showCursorMarkers()` to skip the last cursor (shows native cursor only) to avoid double cursor
5. Added Escape key to clear multi-cursor mode

**Files Modified:**
- `static/script.js` - addCursorBelow (~line 9419), addCursorAbove (~line 9461), setupMultiLineCursorListener (~line 9518), showCursorMarkers (~line 9344), handleMultiLineCursorMove (~line 9633)

**Related Issues:** Multi-cursor visual feedback, Ctrl+Alt+arrows

---

## [2026-01-16 17:45] - Multi-Cursor Home/End Not Consolidating Cursors Per Line

**Problem:**
When using Ctrl+Shift+D to select multiple occurrences of a word (including multiple on the same line), pressing Home or End would move each cursor independently, resulting in multiple cursors at the same position on the same line. When typing, text would be inserted multiple times on that line.

**Root Cause:**
The `handleMultiCursorMove()` function moved each cursor independently without checking if multiple cursors ended up at the same position after Home/End navigation.

**Solution:**
Added cursor consolidation logic specifically for Home/End keys:
1. After moving all cursors to line start (Home) or line end (End), check for duplicate positions
2. Use a Set to track seen positions and filter out duplicates
3. Update the selectedMatches and matches arrays with the consolidated list
4. Update the visual indicator to show the correct count of remaining cursors

This ensures one cursor per line after Home/End, making multi-line editing more intuitive.

**Files Modified:**
- `static/script.js` - handleMultiCursorMove (~line 9163)

**Related Issues:** Multi-cursor editing, Ctrl+Shift+D

---

## [2026-01-16 17:30] - Keyboard Shortcuts Not Working (F9, Ctrl+Shift+D, Ctrl+Alt+Arrows)

**Problem:**
1. F9 (swap words) not working in contentEditable mode
2. Ctrl+Shift+D (select next occurrence) not working at all
3. Ctrl+Alt+Up/Down (multi-cursor) not working at all

**Root Cause:**
1. F9 was only implemented for INPUT/TEXTAREA, not contentEditable
2. Ctrl+Shift+D and Ctrl+Alt+arrows were being detected by the browser but the handlers were checking for INPUT/TEXTAREA only, and the active element was the contentEditable DIV
3. These are complex multi-cursor features that require direct access to `.value`, `.selectionStart`, `.selectionEnd` properties which don't exist in contentEditable

**Solution:**
1. **F9**: Updated to handle both contentEditable and INPUT/TEXTAREA modes using the same pattern as other formatter functions (check `isContentEditable`, use `window.getSelection()` and `Range` API, update underlying input)
2. **Ctrl+Shift+D, Ctrl+Alt+arrows**: These features require raw mode because they manipulate text selections and cursors in ways that are incompatible with contentEditable's DOM structure. Added user-friendly toast messages: "Select next occurrence only works in raw mode (📄 button)" and "Multi-cursor only works in raw mode (📄 button)"
3. Moved keyboard event listener to capture phase (`addEventListener(..., true)`) to catch events before browser defaults
4. Added `e.preventDefault()` at the top of Ctrl+Alt+arrow handlers to prevent Windows screen rotation shortcuts

**Files Modified:**
- `static/script.js` - F9 handler (~line 561), Ctrl+Shift+D handler (~line 660), Ctrl+Alt+arrow handlers (~line 675, 690), event listener registration (~line 42)

**Related Issues:** ContentEditable vs INPUT/TEXTAREA feature compatibility

**Note:** Multi-cursor features (Ctrl+Shift+D, Ctrl+Alt+arrows) are intentionally limited to raw mode because they require precise character-level manipulation that's not feasible in contentEditable's rich DOM structure.

---

## [2026-01-16 17:00] - F3 Formatting Not Persisting After Refresh

**Problem:**
When applying formatting via F3 (bold, italic, colors, etc.) in contentEditable mode, the syntax would disappear after refreshing the page. The formatting was visible temporarily but not saved to the database.

**Root Cause:**
The `applyQuickFormat()` function was trying to update the underlying input element using a complex approach:
1. It extracted raw text from contentEditable
2. Used string replace to find/replace selected text (unreliable with duplicate text)
3. Called `highlightSyntax()` to re-render the preview
4. Manually updated tableData and triggered save

This approach was fragile and didn't properly sync the contentEditable DOM with the underlying input element.

**Solution:**
Simplified the contentEditable handling to match the pattern used in other formatter functions:
1. Insert formatted text directly into contentEditable using `range.insertNode(textNode)`
2. Extract the complete raw text using `extractRawText(input)`
3. Update the underlying input element's `.value` property
4. Trigger `input` event on the underlying element (which handles tableData update and auto-save)

This ensures the contentEditable changes are properly synced to the hidden input/textarea, which is what gets saved to the database.

**Files Modified:**
- `static/script.js` - applyQuickFormat (~line 7538)

**Related Issues:** All F3 formatter functions must properly sync contentEditable changes to underlying input

---

## [2026-01-16 16:45] - F3 Quick Formatter Additional Functions Not Working

**Problem:**
1. Text case conversion (uppercase, lowercase, proper case) buttons in F3 not working
2. Scroll position jumping to top after applying F3 formatting

**Root Cause:**
1. `changeTextCase()` function was only written for INPUT/TEXTAREA elements, not contentEditable
2. No scroll position saving/restoration when opening/closing F3 formatter

**Solution:**
1. Updated `changeTextCase()` to handle both contentEditable and legacy modes (same pattern as formatPipeTable and removeFormatting)
2. Added `quickFormatterScrollPosition` variable to save scroll position
3. `showQuickFormatter()` now saves `tableContainer.scrollTop` when opening
4. `closeQuickFormatter()` now restores scroll position with 50ms delay after closing

**Files Modified:**
- `static/script.js` - changeTextCase (~line 8017), showQuickFormatter (~line 7330), closeQuickFormatter (~line 7450)

**Related Issues:** All F3 formatter functions need contentEditable support

**Note:** This is part of a larger pattern - any F3 formatter function that modifies text needs to check `quickFormatterSelection.isContentEditable` and handle both modes appropriately.

---

## [2026-01-16 16:30] - Markdown Links Not Opening in Browser

**Problem:**
When clicking on links in markdown preview (when NOT in edit mode), the cell would enter edit mode instead of opening the link in a browser.

**Root Cause:**
The markdown preview element has `contentEditable="true"`, so any click on it (including on links) triggers focus and enters edit mode. The click event handler alone wasn't enough to prevent this because the focus happens on mousedown, before the click event.

**Solution:**
Added both `mousedown` and `click` event handlers to intercept link clicks:
1. `mousedown` handler prevents the default focus behavior when clicking on links
2. `click` handler opens the link in a new tab using `window.open()`
3. Both handlers use `e.preventDefault()`, `e.stopPropagation()`, and `e.stopImmediatePropagation()` to prevent event bubbling
4. Both handlers use capture phase (`true` parameter) to catch events before they bubble

**Files Modified:**
- `static/script.js` - Link click handlers (~line 1689)

**Related Issues:** ContentEditable focus behavior

---

## [2026-01-16 16:15] - F3 Quick Formatter Functions Not Working with ContentEditable

**Problem:**
1. Table formatter (F3 → 📊) not working - button clicks weren't registering any action
2. Remove formatting (F3 → 🧹) not working - function was completely missing from script.js

**Root Cause:**
1. The `formatPipeTable()` function was written to work with INPUT/TEXTAREA elements (using `.value` property and `.selectionStart/.selectionEnd`)
2. When markdown preview is active, F3 opens on the contentEditable DIV instead, which uses different APIs (`.textContent`, `window.getSelection()`, `Range` objects)
3. The `quickFormatterSelection` object structure is different for contentEditable: `{isContentEditable: true, range: Range, text: '...'}` vs `{start: number, end: number}`
4. The `removeFormatting()` function was deleted from script.js at some point

**Solution:**
1. Updated `formatPipeTable()` to detect if target is contentEditable and handle both modes:
   - ContentEditable: Use `quickFormatterSelection.text` for selected text, `range.deleteContents()` and `range.insertNode()` for replacement
   - Legacy: Use `input.value.substring(start, end)` and string manipulation
2. Added `removeFormatting()` function back with same dual-mode support
3. Both functions now update the underlying input element when working with contentEditable
4. Added cache control headers to Flask app to prevent browser caching issues during development

**Files Modified:**
- `static/script.js` - formatPipeTable (~line 7848), removeFormatting (~line 11598)
- `app.py` - Added cache control headers (~line 7)

**Related Issues:** All F3 quick formatter functions need to support both contentEditable and legacy input modes

---

## [2026-01-16 15:30] - Multiple Shortcut and Feature Fixes

**Problem:**
1. Table formatter (F3 → 📊) and clear cell formatting not working
2. Links in markdown preview not opening when clicked
3. Ctrl+Shift+D not working (Chrome's default bookmark shortcut interfering)
4. F9 shortcut not working

**Root Cause:**
1. Clear cell formatting wasn't saving data after clearing
2. Markdown preview has `contentEditable="true"`, so clicking links positioned cursor instead of following the link
3. Ctrl+Shift+D wasn't preventing default early enough, allowing Chrome's bookmark shortcut to interfere
4. F9 had `e.preventDefault()` in wrong position (after checking element instead of before)

**Solution:**
1. Added `saveData()` call to `clearCellFormatting()` function
2. Added click event listener to markdown preview that intercepts link clicks, prevents default editing behavior, and opens links in new tab using `window.open()`
3. Moved `e.preventDefault()` and added `e.stopPropagation()` to top of Ctrl+Shift+D handler before element checks
4. Moved `e.preventDefault()` to top of F9 handler before element checks

**Files Modified:**
- `static/script.js` - Link click handler (~line 1675), clearCellFormatting (~line 4281), Ctrl+Shift+D handler (~line 607), F9 handler (~line 561)

**Related Issues:** Markdown preview contentEditable architecture

---

## [2026-01-16 01:20] - F3 Quick Formatter Blur Handler Fix
**Problem:** 
When applying formatting via F3, the effect would appear briefly then disappear, leaving all text looking normal (unformatted).

**Root Cause:** 
When F3 opens, it steals focus from the contenteditable preview. This triggered the `blur` event handler, which immediately called `parseMarkdown()` to render the clean preview. After formatting was applied and the preview refocused, the clean preview content was being used instead of the newly formatted content.

**Solution:** 
Added a check in the blur event handler to skip processing when the quick formatter is visible (`quickFormatter.style.display === 'block'`). This prevents the premature switch from syntax-highlighted mode to clean preview mode.

**Files Modified:**
- `static/script.js` - Added quick formatter visibility check in blur handler.

**Related Issues:** F3 formatting, contenteditable focus/blur.

---

## [2026-01-16 01:00] - F3 Quick Formatter Duplicate Functions Removed
**Problem:** 
F3 quick formatter buttons clicked but did nothing - no formatting was applied and the window stayed open.

**Root Cause:** 
Duplicate function definitions existed in `script.js`. The old versions (lines 10470-11255) were defined after the fixed versions (lines 7483+), causing JavaScript to overwrite the fixed functions with the old ones that didn't support contenteditable elements.

**Solution:** 
Removed approximately 785 lines of duplicate quick formatter functions from lines 10470-11255. Now only the fixed versions that support both contenteditable and legacy input/textarea remain.

**Files Modified:**
- `static/script.js` - Removed duplicate function block.

**Related Issues:** F3 formatting, function duplication.

---

## [2026-01-16 00:45] - F3 Quick Formatter Contenteditable Support
**Problem:** 
F3 quick formatter didn't open when text was selected in the WYSIWYG contenteditable editor.

**Root Cause:** 
The F3 keydown handler only checked for `INPUT` and `TEXTAREA` elements. The WYSIWYG editor uses a `contenteditable` DIV (`.markdown-preview`), which wasn't detected.

**Solution:** 
Updated multiple functions to support contenteditable elements:
- **F3 handler:** Added check for `.markdown-preview` with `isContentEditable`.
- **`showQuickFormatter`:** Uses `window.getSelection()` to get range and text for contenteditable.
- **`updateSelectionStats`:** Gets selected text from stored `quickFormatterSelection.text`.
- **`applyQuickFormat`:** For contenteditable, extracts raw text, replaces selection, updates tableData & hidden input, and re-renders with `highlightSyntax()`.
- **`searchGoogle`/`searchGoogleWithExtra`:** Gets text from contenteditable selection.

**Files Modified:**
- `static/script.js` - Updated F3 handler, showQuickFormatter, updateSelectionStats, applyQuickFormat, searchGoogle, searchGoogleWithExtra.

**Related Issues:** WYSIWYG editing, F3 quick formatting.

---

## [2026-01-16 00:40] - WYSIWYG Enter Key Cell Expansion Fix
**Problem:** 
When pressing Enter at the end of a cell, the new line would overflow the cell border and the cursor would become invisible.

**Root Cause:** 
The Enter key handler was updating cell height, but not accounting for the newly added `<br>` element. The height calculation happened before the browser had a chance to layout the new content, and the cursor wasn't scrolled into view.

**Solution:** 
- Added extra padding (+20px) to height calculation to ensure room for the cursor.
- Changed cell and preview height to `'auto'` with `minHeight` to allow natural expansion.
- Added `br.scrollIntoView({ block: 'nearest', behavior: 'instant' })` to scroll the cursor into view.

**Files Modified:**
- `static/script.js` - Enhanced Enter key handler in `applyMarkdownFormatting`.

**Related Issues:** Cell height adjustment, cursor visibility.

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
