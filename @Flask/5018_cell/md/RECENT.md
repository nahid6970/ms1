# Recent Development Log

**KEEP ONLY LAST 5 SESSIONS** - Move older sessions to `md/ARCHIVE_RECENT.md` (don't delete them!)

**Archiving Process:** When you have 6+ sessions, move the oldest one to ARCHIVE_RECENT.md with "ARCHIVED" prefix.

## [2026-02-28 10:30] - Fixed Cursor Position Issues in Visual Mode

**Session Duration:** 0.3 hours

**What We Accomplished:**

### 🐛 Fixed Cursor Jump and Drift Issues
- **Problem**: 
  1. Selecting multiple lines and pressing backspace caused the cursor to jump to the top of the cell.
  2. Editing multi-line content caused the cursor to drift or move in the wrong direction due to incorrect newline handling.
- **Root Cause**: 
  - `extractRawTextBeforeCaret` returned 0 offset when the selection started at an element node.
  - `setCaretPosition` did not account for newlines created by `DIV` and `P` tags, mismatching `extractRawText` logic.
  - `beforeinput` handler restored cursor position even for single-character deletions (like simple backspace), fighting against natural browser behavior.
- **Solution**: 
  - **Fixed Offset Calculation**: Updated `extractRawTextBeforeCaret` to correctly traverse children of element nodes.
  - **Synced Cursor Placement**: Updated `setCaretPosition` to handle `DIV`/`P` newlines exactly like `extractRawText`.
  - **Refined Restoration**: Modified `beforeinput` to ONLY restore cursor for range-based deletions (to prevent scroll jumps) and explicitly excluded 'insertLineBreak' (Enter).
- **Result**: Cursor now stays correctly positioned during all editing operations, including multi-line deletions and simple typing.

**Files Modified:**
- `static/script.js` - Updated `extractRawTextBeforeCaret`, `setCaretPosition`, and `beforeinput` handler (~30 lines)

**Technical Details:**
- **Recursion**: Added recursive child traversal to `extractRawTextBeforeCaret` for element stops.
- **Newline Logic**: Added `lastCharWasNewline` tracking to `setCaretPosition` to handle block-level element spacing.
- **Event Filtering**: Used `!sel.isCollapsed` to strictly limit cursor restoration to selection-based operations.

**Current Status:**
- ✅ No scroll jump on multi-line delete.
- ✅ No cursor drift on multi-line editing.
- ✅ Natural typing and backspacing feel correct.

**Time Spent:** 0.3 hours

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

---

*Older sessions archived in md/ARCHIVE_RECENT.md*
