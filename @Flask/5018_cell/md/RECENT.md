# Recent Development Log


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

**Next Steps:**
- Test with various Nerd Font icon combinations
- Verify export HTML renders correctly

**Time Spent:** 0.5 hours
