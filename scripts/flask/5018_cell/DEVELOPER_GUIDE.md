# Project Developer Guide & Documentation

This document serves as a guide for understanding the codebase, specifically the custom spreadsheet application. It highlights key architectural decisions and provides a checklist for implementing new features to ensure consistency across the application.

## Project Overview
This is a Flask-based web application that provides a dynamic, spreadsheet-like interface (`5018_cell`). It supports rich text formatting via Markdown, custom grid tables, and real-time data manipulation.

### Key Files
- **`app.py`**: Flask backend handling routes, API endpoints for data persistence (loading/saving JSON), and serving static files.
- **`static/script.js`**: The core logic engine (~6800+ lines). Handles state management (`tableData`), rendering (`renderTable`), event listeners, and Markdown parsing.
- **`static/style.css`**: Custom styling for the grid, modals, and markdown elements.
- **`templates/index.html`**: The main application shell with modals and UI structure.
- **`export_static.py`**: Python script to generate a standalone HTML file with all features embedded (no Flask needed).
- **`data.json`**: JSON file storing all spreadsheet data, sheets, categories, and cell styles.

### Core Features
- **Multi-sheet support** with categories for organization
- **Sub-sheet hierarchy** - Create nested sub-sheets under parent sheets with horizontal navigation bar
- **Scroll position memory** - Each sheet remembers its scroll position when switching between sheets
- **Rich markdown formatting** in cells (bold, italic, colors, tables, math, collapsible text, etc.)
- **Cell styling** (borders, colors, fonts, alignment, merging)
- **Column customization** (width, type, styling, header styling)
- **Search functionality** with multi-term support and highlighting
- **Keyboard shortcuts** (F1-F4, Alt+M, Ctrl+S, etc.)
- **Quick Formatter** (F2) for instant text formatting
- **Static export** for sharing spreadsheets as standalone HTML files

## ⚡ Critical Implementation Rule: "The Rule of 6"

When adding new **Markdown Syntax** or **Cell Formatting Features**, you **MUST** implement logic in at least **6 specific locations** to ensure the feature works consistently across both the live app and static export.

**Note:** The Custom Color Syntax feature is an exception to this rule - it's a meta-feature that allows users to create their own syntaxes dynamically without code changes. See the "Custom Color Syntax Feature" section for details.

### Main App (static/script.js)

#### 1. `parseMarkdown(text)` & Parsing Logic
**Location:** `static/script.js` ~ line 980+ (both `parseMarkdownInline()` and `oldParseMarkdownBody()`)
**Purpose:** Converts the raw text syntax into HTML.
**Action:** Add your regex or parsing logic here.
*   *Example:* For `Table*N`, we added detection for `(?:^|\n)Table\*(\d+)` (allowing text before it) and a helper function `parseCommaTable`.
*   *Example:* For bold `**text**`, we use `.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')`.
*   *Example:* For collapsible text `{{text}}`, we use `.replace(/\{\{(.+?)\}\}/g, ...)` to create a toggle button with hidden content.
*   **Note:** Add to BOTH `parseMarkdownInline()` and `oldParseMarkdownBody()` functions!

#### 2. `checkHasMarkdown(value)`
**Location:** `static/script.js` ~ line 857+
**Purpose:** Centralized helper function to detect if a string contains any supported Markdown syntax.
**Action:** Add your syntax pattern to the return statement.
```javascript
function checkHasMarkdown(value) {
    // ...
    return (
        // ... existing checks
        str.includes('**') ||
        str.includes('YourSyntax') // <--- ADD THIS
    );
}
```

#### 3. `renderTable()`
**Location:** `static/script.js` ~ line 3947+
**Purpose:** Renders the table rows and cells.
**Action:** **NO ACTION REQUIRED.**
*   The `renderTable()` function has been optimized to automatically call `applyMarkdownFormatting()` for every cell.
*   It uses a `DocumentFragment` to build the entire table body in memory before appending it to the DOM, significantly reducing reflows.
*   `applyMarkdownFormatting()` internally calls `checkHasMarkdown()` to decide whether to render a preview.
*   Therefore, you only need to update `checkHasMarkdown()` (Step 2) and `parseMarkdown()` (Step 1).

#### 4. `stripMarkdown(text)`
**Location:** `static/script.js` ~ line 4539+
**Purpose:** Removes your syntax so that sorting and searching work on the *content*, not the *markup*.
**Action:** Add a regex replace to strip your syntax tags.
```javascript
function stripMarkdown(text) {
    // ...
    text = text.replace(/YourRegex/g, '$1'); // <--- ADD THIS
    return text;
}
```

### Static Export (export_static.py)

#### 5. `hasMarkdown` Detection
**Location:** `export_static.py` ~ line 1146+
**Purpose:** Detects if a cell contains markdown to trigger parsing in static HTML.
**Action:** Add your syntax pattern to the detection chain.
```javascript
const hasMarkdown = cellValue.includes('**') || 
    // ... existing checks
    cellValue.includes('YourSyntax') || // <--- ADD THIS
```
**CRITICAL:** If you forget this step, your syntax will NOT work in static export even if it works in the live app!

#### 6. `parseMarkdown()` in Static Export
**Location:** `export_static.py` ~ line 1350+ and 1450+
**Purpose:** Converts syntax to HTML in the static export (same as main app but in Python string format).
**Action:** Add the same regex replacement as in script.js, but with proper Python string escaping.
*   **Note:** There are TWO parseMarkdown functions in export_static.py - update BOTH!
*   **Escaping:** Use `\\` for backslashes in Python strings (e.g., `\\*\\*` for `**`, `\\?\\?` for `??`)

### Documentation (Often Forgotten!)

#### 7. Markdown Formatting Guide Modal
**Location:** `templates/index.html` - Search for "Markdown Formatting Guide"
**Purpose:** Users need to know the syntax exists and how to use it!
**Action:** Add example with syntax and preview to the appropriate section.

#### 8. DEVELOPER_GUIDE.md
**Location:** This file - Add under "New Features & Enhancements"
**Purpose:** Document implementation details for future reference.
**Action:** Add concise section with syntax, examples, and key implementation notes.

## New Features & Enhancements

### Hidden Content Features (Collapsible & Correct Answer)

These two markdown syntaxes work together and are controlled by the same 👁️ button in the toolbar.

#### Collapsible Text: `{{hidden text}}`
**Purpose:** Hides text behind individual toggle buttons that can be clicked to show/hide the content.
**Behavior:**
- Each `{{text}}` gets its own 👁️ toggle button
- Click the button to show/hide that specific text
- Useful for hints, explanations, or spoilers

**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/\{\{(.+?)\}\}/g` generates HTML with a button and hidden span
- **Detection:** Added `value.includes('{{')` to `hasMarkdown` checks
- **Stripping:** Added `.replace(/\{\{(.+?)\}\}/g, '$1')` to `stripMarkdown()`
- **CSS:** `.collapsible-wrapper`, `.collapsible-toggle`, `.collapsible-content` styles
- **Quick Formatter:** Added a 👁️ button to wrap selected text with `{{}}`
- **Static Export:** Full support in `export_static.py`

#### Correct Answer: `[[correct answer]]`
**Purpose:** Marks correct answers in MCQ tests. Text appears normal until clicked, then reveals with green background.
**Behavior:**
- Text looks completely normal (no visual difference)
- Click the text itself to reveal green background
- Prevents students from identifying correct answers visually

**Implementation:**
- **Parsing:** `[[text]]` -> `<span class="correct-answer">$1</span>`
- **Styling:** Transparent by default, green (#29e372) when `.revealed` class is added
- **Detection:** Added `str.includes('[[')` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/\[\[(.+?)\]\]/g, '$1')` to `stripMarkdown()`
- **Static Export:** Full support with click-to-reveal behavior

#### Global Toggle Button (👁️)
**Location:** Toolbar, next to row numbers and wrap toggles
**Function:** `toggleAllCollapsibles()`
**Behavior:**
- Shows/hides ALL collapsible text (`{{}}`) at once
- Reveals/hides ALL correct answers (`[[]]`) at once
- If any content is visible, clicking hides everything
- If all content is hidden, clicking reveals everything
- Shows alert "No hidden content found" if no `{{}}` or `[[]]` syntax exists

**Key Functions:**
- `toggleAllCollapsibles()` - Global toggle for both syntaxes
- `toggleCollapsible(id)` - Individual toggle for `{{}}` buttons
- Click event listener - Individual toggle for `[[]]` spans

### Cell Complete Checkmark Feature
**Purpose:** Mark cells as complete with a green checkmark for task tracking.
**Access:** Right-click context menu → "Mark Complete"
**Implementation:** 
- `toggleCellComplete()` function follows same pattern as other toggle functions (Bold, Italic, Center)
- CSS: `.cell-complete::before` pseudo-element shows green ✓ in top-left corner
- Data stored via `setCellStyle(row, col, 'complete', boolean)`
- Applied in `renderTable()` and supported in static export

### Single Row View Mode
**Purpose:** Allows viewing and editing one row at a time, useful for focused review or quiz/flashcard-style workflows.
**UI Controls:**
- 📖 Toggle button to enable/disable Single Row Mode
- ⬅️ Previous row button (disabled at first row)
- ➡️ Next row button (disabled at last row)
**Implementation:**
- **State Variables:** `singleRowMode` (boolean), `singleRowIndex` (current row index)
- **Functions:**
  - `toggleSingleRowMode()` - Toggles mode on/off, updates UI
  - `prevSingleRow()` - Decrements index and re-renders
  - `nextSingleRow()` - Increments index and re-renders
  - `updateSingleRowButtons()` - Manages button disabled states
- **Rendering:** `renderTable()` conditionally renders only `sheet.rows[singleRowIndex]` when mode is active
- **Styling:** `.btn-icon-toggle.active` for active state, disabled button styles

### Color Highlight Shortcuts
**Syntax:** 
- `==text==` → Black background with white text
- `!!text!!` → Red background with white text  
- `??text??` → Blue background with white text

**Purpose:** Quick color highlighting without using the full `{fg:color;bg:color}text{/}` syntax.

**Implementation:**
- **Parsing:** Added regex replacements in both `parseMarkdownInline()` (for table cells) and `oldParseMarkdownBody()` (for regular cells)
- **Detection:** Added `value.includes('!!')` and `value.includes('??')` to `hasMarkdown` checks
- **Stripping:** Added `.replace(/!!(.+?)!!/g, '$1')` and `.replace(/\?\?(.+?)\?\?/g, '$1')` to `stripMarkdown()`
- **Quick Formatter:** Added Black, Red, and Blue buttons in a separate "Quick Highlights" section
- **Static Export:** Updated `export_static.py` with the same parsing logic in both inline and body parsers
- **Table Support:** All three color syntaxes work inside `Table*N` markdown cells

**Styling (applies to all color syntaxes):**
- `display: inline` - Allows natural text wrapping without forcing line breaks
- `box-decoration-break: clone` - Ensures background continues properly on wrapped lines
- `padding: 1px 4px` - Consistent padding for all highlights
- `border-radius: 3px` - Rounded corners
- Same styling applied to custom color syntax `{fg:...;bg:...}text{/}`

**Key Functions:**
  - `parseMarkdownInline()` - Converts highlight syntax in table cells
  - `oldParseMarkdownBody()` - Converts highlight syntax in regular cells
  - `checkHasMarkdown()` - Detects the syntax
  - `stripMarkdown()` - Removes syntax for sorting/searching

### Custom Color Syntax Feature
**Purpose:** Users can create unlimited custom color highlight syntaxes with any characters and colors.

**Access:** Settings Modal (⚙️) → 🎨 Custom Color Syntax section

**Usage:**
- Add custom syntax with marker (e.g., `++`, `$$`, `%%`) up to 4 characters
- Click BG/FG color buttons to open color picker with transparent option
- Use in cells: `++highlighted text++`
- Edit/delete syntaxes anytime - changes apply immediately and auto-save

**UI Features:**
- Compact one-line layout: `[Syntax] BG: [Color] FG: [Color] [Preview] [🗑️]`
- Color picker popup with BG/FG radio buttons, transparent checkbox, and live preview
- Same color palette as cell color picker (100 colors)
- Preview shows syntax with selected colors in real-time

**Implementation:**
- **Storage:** `custom_syntaxes.json` - array of `{ marker, bgColor, fgColor }`
- **API Endpoints:** `/api/custom-syntaxes` (GET/POST) in app.py - auto-exports static HTML on save
- **Parsing:** `applyCustomColorSyntaxes(text)` applies all syntaxes (~line 9100+ in script.js)
- **Integration:** Called in both `parseMarkdownInline()` and `oldParseMarkdownBody()` in both script.js and export_static.py
- **Quick Highlights Integration:** Custom syntaxes automatically appear as buttons in F3 Quick Formatter
  - Buttons are dynamically generated and inserted before the 🎨 color picker button
  - Each button shows the marker with its configured colors
  - Click to apply syntax, right-click to add to multi-format selection
  - Grid layout maintains 5 buttons per row (same as other F3 sections)
  - Updates automatically when syntaxes are added/edited/deleted
- **Key Functions:** 
  - `loadCustomColorSyntaxes()` - Loads from JSON file via API
  - `saveCustomColorSyntaxes()` - Saves to JSON file via API
  - `renderCustomColorSyntaxList()` - Renders compact UI list in settings
  - `renderCustomSyntaxButtons()` - Renders buttons in F3 Quick Highlights section
  - `showCustomSyntaxColorPicker()` - Shows color picker popup with BG/FG selection
  - `addCustomColorSyntax()`, `updateCustomSyntax()`, `removeCustomSyntax()`
- **Static Export:** ✅ Fully implemented - syntaxes embedded from JSON file into exported HTML

### Multi-Term Search Feature
**Syntax:** `term1, term2, term3` (comma-separated)
**Purpose:** Search for multiple terms at once. Shows rows containing ANY of the search terms.
**Implementation:**
- **Search Logic:** In `searchTable()`, the search input is split by commas: `searchTerm.split(',').map(term => term.trim().toLowerCase())`
- **Markdown Stripping:** Search terms are processed through `stripMarkdown()` to ignore markdown syntax when searching.
- **Matching:** Each cell is checked against all terms, and if any term matches, the row is shown.
- **Highlighting:** All matching terms are highlighted using `highlightMultipleTermsInHtml()` which:
  - Finds all matches for all terms
  - Sorts and merges overlapping matches
  - Creates highlights in a single pass to avoid conflicts
- **Overlay:** For cells without markdown preview, `createTextHighlightOverlayMulti()` creates an overlay that exactly matches the input's position and styling.
- **Feedback:** Toast message shows which terms were found, e.g., "Found 5 row(s) matching: johnny, donny"
- **Cell Highlighting:** Search does NOT add `.search-highlight` class to cells - preserves custom cell background colors. Only matching text gets yellow highlight.
- **Key Functions:**
  - `searchTable()` - Main search logic with comma-splitting (~line 4120)
  - `highlightMultipleTermsInHtml()` - Highlights all matching terms in HTML
  - `createTextHighlightOverlayMulti()` - Creates overlay for input/textarea elements
  - `stripMarkdown()` - Removes markdown from search terms

### Line Conversion Tools
**Purpose:** Convert between line-separated text and comma-separated text.
**Implementation:**
- **Lines to Comma:** `linesToComma()` function converts newline-separated text to comma-separated format.
- **Comma to Lines:** `commaToLines()` function converts comma-separated text to newline-separated format.
- **Quick Formatter:** Added two buttons in the formatter popup:
  - "Lines → Comma" button converts selected text from lines to comma-separated
  - "Comma → Lines" button converts selected text from comma-separated to lines
- **Usage:** Select text in a cell, press F3, and click the appropriate conversion button.
- **Key Functions:**
  - `linesToComma()` - Converts line breaks to commas
  - `commaToLines()` - Converts commas to line breaks

### Pipe Table Formatter
**Purpose:** Automatically format and align pipe tables (like Vim/Emacs table formatting).
**Syntax:** Select any pipe table text and click the 📊 button in Quick Formatter (F3).

**Before:**
```
:R-A:Name | :G:Age | :B-A:City
---------|--------|--------
John | 25     | NYC
Jane       | 30     | LA
```

**After:**
```
| :R-A:Name | :G:Age | :B-A:City |
|-----------|--------|-----------|
| John      | 25     | NYC       |
| Jane      | 30     | LA        |
```

**Features:**
- Aligns all pipes vertically
- Calculates optimal column width based on content (not separator rows)
- Pads cells with spaces to match column width
- Regenerates separator rows to match content width
- Preserves color codes (`:R-A:`, etc.)
- Preserves alignment markers (`:text:`, `text:`)
- Adds leading/trailing pipes if missing
- Works with any number of columns

**Smart Width Calculation:**
- Separator rows (lines with only dashes) are **ignored** when calculating column widths
- Only actual content (headers and data) determines optimal width
- Separator rows are regenerated to match the content width
- This prevents overly wide columns from long separator rows

**Implementation:**
- **Function:** `formatPipeTable()` in `static/script.js` (~line 6070)
- **Algorithm:**
  1. Parse table into rows and columns
  2. Calculate maximum width for each column (excluding separator rows)
  3. Pad cells to match column width
  4. Regenerate separator rows with correct width
  5. Rebuild table with aligned pipes
- **Button:** 📊 in Quick Formatter (F3) - Located in Utilities section
- **Usage:** Select table text → Press F3 → Click 📊

**Key Functions:**
- `formatPipeTable(event)` - Main formatting function

### Page Load Time Indicator
**Purpose:** Shows how long the page took to load, helping with performance monitoring.
**Implementation:**
- **Calculation:** Uses `performance.now()` which returns milliseconds since page load started, divided by 1000 and formatted to 2 decimals
- **Display:** Shows in the sheet controls area as "⏱️ X.XXs"
- **Location:** In `loadData()` function, after `renderTable()` completes
- **Timing:** Uses `requestAnimationFrame` to ensure DOM updates are finished before measuring
- **Accuracy:** Captures the full user-perceived load time including data fetching, parsing, and table rendering
- **Key Functions:**
  - `loadData()` - Where the timer is calculated and displayed
  - `renderTable()` - Must complete before timer is shown

### Markdown Cell Height Adjustment
**Purpose:** Ensures cells are sized to fit whichever is larger - the raw markdown text or the rendered preview.

**Key Function:**
- `adjustCellHeightForMarkdown(cell)` - Measures and applies max height (~line 7715)

**How it works:**
1. Gets both input/textarea and markdown preview elements
2. Temporarily shows both to measure their `scrollHeight`
3. Uses `Math.max(inputHeight, previewHeight)` to get larger height
4. Applies that height to both elements via `minHeight`
5. Ensures cell never cuts off content in either view

**Called by:**
- `adjustAllMarkdownCells()` - Applies to all cells after table render (~line 7745)

**Why needed:** Without this, switching between edit mode (raw text) and preview mode could cause content to be cut off if one is taller than the other.

**Multi-line text handling:** Cells with newlines (`\n`) are automatically treated as markdown content (via `checkHasMarkdown()`) to ensure proper height calculation and line break rendering.

### Quick Formatter Enhancements
**Improvements:**
- **Instant Application:** Removed the "Apply" button. All formatting is now applied instantly when buttons are clicked.
- **Color Highlights:** Added dedicated buttons for quick color highlighting (Black, Red, Blue) in a separate section.
- **Better Layout:** Organized buttons into logical groups with clear visual separation.
- **Click-Outside-to-Close:** Added event listener to close the formatter popup when clicking outside of it.
- **Improved UX:** Streamlined workflow - select text, press F3, click format button, done.

**Button Order (F3 Popup):**
1. **Text Formatting:** Bold, Italic, Underline, Strikethrough, Heading, Small Text, Code
2. **Special Formatting:** Superscript, Subscript
3. **Utilities:** Link, Search Google, Sort Lines, Lines↔Comma conversion
4. **Advanced:** Select All Matching, Hide Text (collapsible), Correct Answer (MCQ)
5. **Clear Format:** 🧹 Remove All Formatting (always last before separator)
6. **Text Case Section:** UPPERCASE, lowercase, Proper Case
7. **Quick Highlights Section:** Black, Red, Blue, Custom Color

### Sort Lines Feature
**Purpose:** Intelligently sorts selected lines while preserving parent-child relationships in lists.

**Sorting Priority:**
1. Lines without dashes (highest priority)
2. Lines with single dash `-`
3. Lines with double dash `--`
4. Within same priority: alphabetical or numerical sorting

**Parent-Child Detection:**
- **Format 1:** `Parent` followed by `- child`
- **Format 2:** `- Parent` followed by `-- child`
- **Mixed Format:** Automatically detects and handles both formats in the same selection

**Smart Grouping:**
- Children stay with their parents during sorting
- Parents are sorted, and their children move with them
- When multiple `- ` lines appear together, they're treated as separate parents (not children of each other)

**Examples:**
```
Before:          After:
B-List           A-List
- BB             - AA
A-List           B-List
- AA             - BB

Before:          After:
- B-List         - A-List
-- BB            -- AA
- A-List         - B-List
-- AA            -- BB
```

**Key Function:**
- `sortLines()` - Located in `static/script.js` ~ line 7057+

**⚠️ IMPORTANT - Button Order Rule:**
When adding new buttons to the Quick Formatter, the **Clear Format button (🧹 Remove All Formatting)** MUST always be:
- **Last button** in the main formatting section
- **Immediately before** the `<div class="quick-formatter-separator"></div>`
- **Before** the Quick Highlights section

This ensures users can easily find the clear button at the end of all formatting options.

**Key Functions:**
  - `showQuickFormatter()` - Opens the formatter popup (F3 shortcut)
  - `applyQuickFormat()` - Applies formatting instantly without Apply button
  - `removeFormatting()` - Clears all markdown syntax from selected text
  - `changeTextCase()` - Converts selected text to UPPERCASE, lowercase, or Proper Case
  - Various format functions: `makeBold()`, `makeItalic()`, `makeUnderline()`, etc.

### Text Case Conversion Feature
**Purpose:** Quickly convert selected text to different cases without retyping.

**Available Cases:**
1. **UPPERCASE** - Converts all letters to capitals (ABC)
2. **lowercase** - Converts all letters to lowercase (abc)
3. **Proper Case** - Capitalizes first letter of each word (Abc)

**Usage:** Select text in a cell, press F3, click the desired case button.

**Key Function:**
- `changeTextCase(caseType, event)` - Converts text based on caseType ('upper', 'lower', 'proper')



### Small Text Feature
**Syntax:** `..small text..`
**Purpose:** Makes text smaller (75% of normal size), useful for footnotes, captions, or de-emphasizing text.
**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/\.\.(.+?)\.\./g` converts to `<span style="font-size: 0.75em;">$1</span>`
- **Detection:** Added `str.includes('..')` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/\.\.(.+?)\.\./g, '$1')` to `stripMarkdown()`
- **Markdown Guide:** Added to the Text Formatting section showing the syntax and preview
- **Static Export:** Updated `export_static.py` with the same parsing logic
- **Key Functions:**
  - `parseMarkdown()` - Converts `..text..` to smaller HTML
  - `checkHasMarkdown()` - Detects the syntax
  - `stripMarkdown()` - Removes syntax for sorting/searching

### Variable Font Size Heading Feature
**Syntax:** `#2#text#/#` (any number: 0.5, 1.5, 2, 3, 10, etc.)
**Purpose:** Creates headings with custom font sizes - flexible alternative to fixed `##heading##`.
**Examples:**
- `#2#Big Heading#/#` → 2x normal size
- `#1.5#Medium Heading#/#` → 1.5x normal size
- `#0.8#Small Heading#/#` → 0.8x normal size
**Implementation:**
- **Parsing:** Regex `/#([\d.]+)#(.+?)#\/#/g` converts to `<span style="font-size: {size}em; font-weight: 600;">`
- **Detection:** Added `str.match(/#[\d.]+#.+?#\/#/)` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/#[\d.]+#(.+?)#\/#/g, '$1')` to `stripMarkdown()`
- **Static Export:** Full support in both parseMarkdown functions

### Border Box Feature
**Syntax:** `#R#text#/#` (color codes: R, G, B, Y, O, P, C, W, K, GR)
**Purpose:** Adds colored border around text - uses same colors as Timeline/Table features.
**Examples:** `#R#Important#/#` → Red border, `#G#Success#/#` → Green border, `#B#Note#/#` → Blue border
**Implementation:** Regex `/#([A-Z]+)#(.+?)#\/#/g` - parsed before font size (letters vs numbers). 2px solid border, 4px radius, wraps properly.
**Note:** Does NOT conflict with font size `#2#text#/#` (numbers) - border uses letters only.

### Colored Underline Feature
**Syntax:** `_R_text__` (color codes: R, G, B, Y, O, P, C, W, K, GR)
**Purpose:** Adds colored underline to text - uses same colors as Border/Timeline/Table.
**Examples:** `_R_Important__` → Red underline, `_G_Success__` → Green underline, `_B_Note__` → Blue underline
**Implementation:** Regex `/_([A-Z]+)_(.+?)__/g` - parsed before regular `__text__`. 2px thickness.
**Note:** Regular underline `__text__` still works (no color code).

### Wavy Underline Feature
**Syntax:** `_.text._`
**Purpose:** Adds wavy underline to text (like spelling error indicators).
**Implementation:**
- **Parsing:** Regex `/_\.(.+?)\._/g` converts to `<span style="text-decoration: underline wavy;">`
- **Detection:** Added `str.includes('_.')` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/_\.(.+?)\._/g, '$1')` to `stripMarkdown()`
- **Static Export:** Full support in both parseMarkdown functions

### Horizontal Separator Feature
**Syntax:** `-----` (5 or more dashes on a single line)
**Purpose:** Creates a horizontal separator line to visually divide content sections.
**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/^-{5,}$/gm` converts to `<div class="md-separator"></div>`
- **Detection:** Added `str.match(/^-{5,}$/m)` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/^-{5,}$/gm, '')` to `stripMarkdown()` to remove for sorting/searching
- **Styling:** 4px solid gray div with 6px vertical margin (CSS class `.md-separator`)
- **Spacing Fix:** In `oldParseMarkdownBody()`, uses `reduce()` instead of `join('\n')` to skip newlines before/after separators, preventing double spacing
- **Markdown Guide:** Added to the Code & Highlights section
- **Static Export:** Updated `export_static.py` with the same parsing logic and reduce() for proper spacing
- **Key Functions:**
  - `parseMarkdown()` - Converts `-----` to separator div
  - `checkHasMarkdown()` - Detects 5+ dashes on a line

### Separator Background Color Feature
**Syntax:** `[COLOR1]-----[COLOR2/HEX]` where COLOR1 = separator line color, COLOR2 = background/text color
**Purpose:** Apply background and text colors to content after a separator, useful for highlighting sections, creating visual blocks, or color-coding information.

**Examples:**
- `-----R` → Normal separator + RED background for content below
- `-----R-W` → Normal separator + RED background with WHITE text (NEW!)
- `R-----` → RED separator line (no background change)
- `R-----G` → Red separator line + GREEN background for content below
- `R-----K-W` → Red separator + BLACK background with WHITE text (NEW!)
- `-----#514522` → Normal separator + custom hex background
- `-----#f00` → Normal separator + red background (3-digit hex, NEW!)
- `-----#514522-#000000` → Custom hex background + black text
- `-----#f00-#fff` → Red background + white text (3-digit hex, NEW!)
- `G-----#514522-#ffffff` → Green separator + custom bg/text colors
- `-----` → Ends background color section (returns to normal)

**Color Codes:** R (red), G (green), B (blue), Y (yellow), O (orange), P (purple), C (cyan), W (white), K (black), GR (gray)

**Hex Colors:** 
- 6-digit: `#RRGGBB` (e.g., `#ff0000`)
- 3-digit: `#RGB` (e.g., `#f00` = `#ff0000`) - NEW!
- With text color: `#RRGGBB-#RRGGBB` or `#RGB-#RGB`

**Color Code Combinations:** NEW!
- `R-W` = Red background with white text
- `G-K` = Green background with black text
- `B-Y` = Blue background with yellow text

**Implementation:**
- **Parsing:** Regex `/^([A-Z]+)?-{5,}((?:[A-Z]+(?:-[A-Z]+)?)|(?:#[0-9a-fA-F]{3,6}(?:-#[0-9a-fA-F]{3,6})?))?$/gm` captures:
  - Optional prefix color (separator line): `[A-Z]+`
  - Optional suffix: color code(s) OR hex color(s)
  - Color code format: `R`, `G`, `B` OR `R-W`, `G-K` (bg-text)
  - Hex format: `#RGB` or `#RRGGBB` or `#RGB-#RGB` or `#RRGGBB-#RRGGBB`
  - 3-digit hex auto-expanded: `#f00` → `#ff0000`
- **Post-processing:** Wraps content after colored separator in `<div>` with background and optional text color until another separator is encountered
- **Detection:** Added patterns to `checkHasMarkdown()`: color codes + hex patterns `/^-{5,}#[0-9a-fA-F]{3,6}/m`, `/^[A-Z]+-{5,}#[0-9a-fA-F]{3,6}/m`
- **Stripping:** Unified regex `/^[A-Z]*-{5,}(?:[A-Z]+(?:-[A-Z]+)?|#[0-9a-fA-F]{3,6}(?:-#[0-9a-fA-F]{3,6})?)?$/gm` removes all separator variations
- **Styling:** Background wrapper has `padding: 2px 6px; margin: 0;` + optional `color` for text
- **Spacing:** No newlines added after separator or wrapper div to prevent gaps
- **Static Export:** Full support in `export_static.py` with same logic

**Behavior:**
- Background color continues until another separator or end of cell
- Plain `-----` separator closes any active background section
- Multiple color sections can exist in one cell
- Works with all markdown features (bold, tables, etc.)

**Key Functions:**
- `parseMarkdownInline()` and `oldParseMarkdownBody()` - Parse separator with colors
- `expandHex()` helper - Expands 3-digit hex to 6-digit (inline in replace callback)
- Post-processing loop - Wraps content in background divs
- `reduce()` function - Skips newlines after separator and wrapper to prevent gaps

**Documentation:** See `md/SEPARATOR_BACKGROUND_COLOR.md` for detailed examples and test cases

### Math Expressions (KaTeX)
**Syntax:** `\(LaTeX expression\)` - Supports square roots, fractions, superscripts, and all LaTeX math

**Examples:** `\(\sqrt{25}\)` → √25 | `\(\frac{a}{b}\)` → fraction | `\(x^2\)` → superscript

**Quick Formatters (F3):**
- **√ button:** Wraps selection with `\(\sqrt{...}\)`
- **a/b button:** Smart converter - `a*b/c` → `\(\frac{a\times b}{c}\)` (handles nested parentheses)

**Implementation:**
- Regex: `/\\\((.*?)\\\)/g` matches delimiters, `katex.renderToString()` renders
- `stripMarkdown()` removes `\( ... \)` for search/sort
- Static export: 
  - Regex: `/\\\((.*?)\\\)/g` with Python string escaping (`\\\\\\(` in source)
  - Removes newlines from KaTeX output to prevent `<br>` insertion into SVG paths
  - Includes integrity hashes for CDN security

**Documentation:** See `md/KATEX_MATH.md` for complete guide with examples and troubleshooting
  - `stripMarkdown()` - Removes separator for sorting/searching
  - `oldParseMarkdownBody()` - Uses reduce to control newlines around separators
  - `export_static.py` - Also uses reduce() to skip `<br>` tags around separators

### Table Syntax Enhancements
We have enhanced the `Table*N` syntax to support more complex layouts:
- **Flexible Placement:** Tables can now be placed anywhere in the cell, not just at the beginning.
- **Explicit Termination (`Table*end`):** Users can explicitly close a table using `Table*end`. This is crucial for placing text *after* a table or stacking multiple tables in one cell.
- **Multiple Tables:** The parser now recursively handles multiple tables within a single cell.
- **Empty Line Preservation:** We use `white-space: pre-wrap` in the preview to ensure empty lines between tables and text are respected.

## Data Structure
The application state is held in `tableData` and persisted to `data.json`:
```javascript
let tableData = {
    sheets: [
        {
            name: "Sheet1",
            nickname: "Optional search nickname",
            rows: [ ["cell1", "cell2"], ... ],
            columns: [ 
                { 
                    name: "A", 
                    width: 150, 
                    type: 'text',
                    font: 'JetBrains Mono',
                    fontSize: 18,
                    bgColor: '#ffffff',
                    textColor: '#000000',
                    headerBgColor: '#f8f9fa',
                    headerTextColor: '#333333',
                    headerBold: false,
                    headerItalic: false,
                    headerCenter: false
                }, 
                ... 
            ],
            cellStyles: { 
                "0-0": { 
                    bold: true, 
                    italic: false,
                    center: false,
                    fontSize: 20,
                    bgColor: '#ffff00',
                    textColor: '#000000',
                    border: 'all' // or 'top', 'bottom', 'left', 'right', 'none'
                } 
            }, // Key is "row-col"
            mergedCells: {
                "0-0": { rowspan: 2, colspan: 3 }
            }
        }
    ],
    activeSheet: 0,
    categories: ["Uncategorized", "Bengali", "English", ...],
    sheetCategories: { "0": "Bengali", "1": "English", ... } // Maps sheet index to category
};
```

### Key Global Variables
- `tableData` - Main data structure (synced with data.json)
- `currentSheet` - Index of currently active sheet
- `currentCategory` - Currently selected category filter
- `sheetHistory` - Array tracking recently viewed sheets (for Alt+M toggle)
- `isMarkdownEnabled` - Boolean for markdown preview toggle
- `isRowNumbersEnabled` - Boolean for row number visibility

### Column Styling
Column-wide styles (like background color, font, text color) are stored in the `columns` array.
**Implementation Rule:** In `renderTable()`, these styles must be applied to the `<td>` or `<input>`/`<textarea>` elements *before* applying cell-specific styles (`cellStyles`). This ensures that:
1.  Column defaults are applied to all cells in the column.
2.  Individual cell styles (e.g., from context menu) can override the column defaults.

## CSS Grid System
The grid system relies on CSS variables for dynamic column counts:
```css
.md-grid {
    display: grid;
    grid-template-columns: repeat(var(--cols), auto);
    /* ... */
}
```

## Important Keyboard Shortcuts
- **F1** - Reorder categories (~line 320 in script.js)
- **F2** - Recent sheets popup (~line 330 in script.js, function at ~line 5112)
- **F3** - Quick Formatter for selected text (~line 340 in script.js)
- **F4** - Toggle ribbons (hide/show toolbar and sheet tabs) (~line 360 in script.js)
- **Alt+M** - Toggle between current and previous sheet (~line 400 in script.js)
- **Alt+N** - Add new row (~line 390 in script.js)
- **Ctrl+S** - Save data (~line 300 in script.js)
- **Ctrl+F** - Focus search box (~line 310 in script.js)
- **\*** in search - Search by sheet nickname

**Note:** Line numbers are approximate and may shift as code is updated. Search for the keyboard shortcut handler function `handleKeyboardShortcuts` to find all shortcuts.

### F1 Quick Navigation Window - Context Menus
The F1 window (opened with F1 key) provides comprehensive management through right-click context menus:

**Category Context Menu** (Right-click on any category):
- ➕ **Add Category** - Opens modal to create a new category
- ✏️ **Rename** - Rename the selected category
- 🗑️ **Delete** - Delete the category (moves sheets to Uncategorized)

**Parent Sheet Context Menu** (Right-click on green main sheets):
- ✏️ **Rename** - Rename the sheet
- 📁 **Move to Category** - Move sheet and all sub-sheets to a different category
- 🗑️ **Delete** - Delete sheet and all its sub-sheets (with warning)

**Sub-Sheet Context Menu** (Right-click on blue sub-sheets):
- ✏️ **Rename** - Rename the sub-sheet
- 🗑️ **Delete** - Delete the sub-sheet only

**Quick Action Buttons:**
- **Categories section:** ➕ Add Category, ⬆️ Move Up, ⬇️ Move Down
- **Sheets section:** ➕ Sheet (adds to current category), ➕ Separator

**Key Functions:**
- `showF1CategoryContextMenu(event, categoryName)` - Shows category context menu
- `showF1SheetContextMenu(event, sheetIndex, isSubSheet)` - Shows sheet context menu (different options for parent vs sub-sheet)
- `renameF1Category(categoryName)` - Opens rename modal for category
- `renameF1Sheet(sheetIndex)` - Opens rename modal for sheet
- `moveF1SheetToCategory(sheetIndex)` - Opens move to category modal
- `deleteF1Category(categoryName)` - Deletes category
- `deleteF1Sheet(sheetIndex)` - Deletes sheet
- `addF1Sheet()` - Adds new sheet to current category

**Implementation Notes:**
- Context menus use the existing modal dialogs (rename, move to category, etc.)
- All operations refresh both category and sheet lists in F1 window
- Tree sidebar remains unchanged and continues to work independently
- F1 window provides faster access to common operations without leaving the navigation view

## Common Development Tasks

### Adding a New Markdown Syntax
1. Add parsing logic to `parseMarkdownInline()` and `oldParseMarkdownBody()` in `static/script.js`
2. Add detection to `checkHasMarkdown()` in `static/script.js`
3. **Add stripping to `stripMarkdown()` in `static/script.js`** - Required for search/sort to work
4. Update `export_static.py` - add to both `parseMarkdownInline()` and `oldParseMarkdownBody()`
5. **Add to Markdown Guide modal** in `templates/index.html` (search for "Markdown Formatting Guide") - Users need to know the syntax exists!
6. **Add to DEVELOPER_GUIDE.md** - Document the feature with examples and implementation details
7. Test: Create cell with syntax, check preview, search, sort, and static export
8. **Optional:** Add to Quick Formatter (F3) if users would benefit from quick-apply button

**⚠️ IMPORTANT:** Steps 5 & 6 are often forgotten but critical - users can't use features they don't know about!

### Modifying the Table Rendering
- Main function: `renderTable()` (~line 3947+)
- Uses `DocumentFragment` for performance
- Calls `applyMarkdownFormatting()` for each cell
- Apply column styles before cell styles (order matters!)

### Adding a New Feature to Quick Formatter
1. Add button to the formatter popup HTML (created in `showQuickFormatter()`)
2. Create formatting function (e.g., `makeYourFormat()`)
3. Wire button click to call the function
4. Function should wrap selected text with your syntax
5. Test with F2 shortcut

### Debugging Tips
- Check browser console for errors
- Use `console.log(tableData)` to inspect state
- Check `data.json` to see persisted data structure
- Use browser DevTools to inspect cell elements and styles
- Test static export with `python export_static.py` to ensure feature works offline

## Future Improvements Checklist
- [ ] When adding new syntax, update the "Markdown Guide" modal in `templates/index.html` so users know it exists.
- [ ] Check `style.css` for dark mode compatibility if adding new UI elements.
- [ ] Update `export_static.py` when adding new markdown syntax or JavaScript features.
- [ ] Test features in both live Flask app and exported static HTML.


### Timeline/Flowchart Layout Feature
**Syntax:** `Timeline*Name` or `Timeline-R*Name` or `TimelineC-B*Name` (R/G/B/Y/O/P/C/W/K/GR for separator colors)
**Implementation:** Regex `/^(Timeline(?:C)?)(?:-([A-Z]+))?\*(.+?)$/gm` in parseMarkdownInline/oldParseMarkdownBody, post-processing closes divs on empty lines
**Empty line separation:** Timeline blocks separated by empty lines are treated as separate timelines

### Word Connector Feature
**Syntax:** `[1]Word` or `[1-R]Word` (R/G/B/Y/O/P/C/W/K/GR for colors)
**Implementation:** Regex `/\[(\d+)(?:-([A-Z]+))?\](\S+)/g` in parseMarkdownInline/oldParseMarkdownBody, `drawWordConnectors()` draws SVG U-shaped lines with arrows
**Static Export:** 500ms delay for getBoundingClientRect() positioning

### Sub-Sheet Hierarchy Feature
**Purpose:** Organize related sheets in a parent-child hierarchy with visual navigation.

**Features:**
- **Create sub-sheets** under any parent sheet using the + button
- **Horizontal navigation bar** below toolbar showing current sheet family
- **Visual hierarchy** - Parent sheet + all its sub-sheets displayed as tabs
- **Right-click context menu** on tabs for rename/delete operations
- **Smart deletion** - Deleting a parent also deletes all its sub-sheets (with warning)
- **Automatic reindexing** - Parent references update correctly when sheets are deleted

**UI Components:**
1. **Sub-Sheet Bar** - Horizontal bar below toolbar
   - Shows parent sheet tab (always first)
   - Shows all sub-sheet tabs
   - + button at the end to add new sub-sheets
   - Tabs wrap to multiple lines if needed
   - Compact design - tabs fit their content

2. **Context Menu** (Right-click on any tab)
   - ✏️ Rename - Opens rename modal
   - 🗑️ Delete - Deletes sheet with confirmation

**Data Structure:**
```javascript
{
    name: "Sheet Name",
    parentSheet: 2,  // Index of parent sheet (undefined for top-level sheets)
    columns: [...],
    rows: [...]
}
```

**Implementation Details:**
- **Parent tracking:** Sub-sheets store `parentSheet` as the index of their parent
- **Reindexing:** When sheets are deleted, all `parentSheet` references are updated
- **Category inheritance:** Sub-sheets automatically inherit their parent's category when created
- **Category synchronization:** When moving a parent sheet to a new category, all sub-sheets automatically move with it
- **Deletion cascade:** Deleting a parent deletes all its sub-sheets (with confirmation warning)
- **Navigation:** Clicking any tab switches to that sheet
- **F1 Window filtering:** Sub-sheets are hidden from the F1 reorder window - only parent sheets are shown

**Key Functions:**
- `renderSubSheetBar()` - Renders the horizontal sub-sheet navigation bar
- `addSubSheet(parentIndex)` - Creates a new sub-sheet under the specified parent
- `showSubSheetContextMenu(event, sheetIndex)` - Shows right-click menu for rename/delete

### Scroll Position Memory
**Purpose:** Remembers scroll position for each sheet when switching between sheets.

**Implementation:**
- **Storage:** `localStorage.sheetScrollPositions` - object mapping sheet index to `{ scrollTop, scrollLeft }`
- **Save:** In `switchSheet()` before switching - saves current sheet's scroll position
- **Restore:** In `switchSheet()` after rendering - restores target sheet's scroll position with `setTimeout()`
- **Persistence:** Survives page refresh and works across all sheet navigation methods

**Key Function:** `switchSheet(index)` - Handles both saving and restoring scroll positions (~line 3037)
- `deleteSheet(index)` - Deletes sheet, all its sub-sheets, and reindexes all parent references
- `moveToCategoryForm.onsubmit` - Moves parent sheet and all sub-sheets to new category together
- `populateF1Sheets()` - Renders both parent and sub-sheets in F1 window with color-coded backgrounds (green for main, blue for sub-sheets)

**CSS Classes:**
- `.subsheet-bar` - Container for the navigation bar
- `.subsheet-tabs` - Flex container for tabs
- `.subsheet-tab` - Individual sheet tab (compact, wraps naturally)
- `.subsheet-tab.active` - Currently active sheet (blue background)
- `.subsheet-add-btn` - + button to add sub-sheets
- `.subsheet-context-menu` - Right-click context menu
- `.f1-parent-sheet` - Main sheet styling in F1 window (green background)
- `.f1-sub-sheet` - Sub-sheet styling in F1 window (blue background, smaller)
- `.f1-sheet-group` - Container grouping parent and sub-sheets together (uses `display: contents` for seamless flow)

**Files Modified:**
- `templates/index.html` - Added sub-sheet bar HTML
- `static/script.js` - Added rendering, creation, context menu, category sync, and F1 filtering logic
- `static/style.css` - Added sub-sheet bar and context menu styles
- `app.py` - Updated API to accept `parentSheet` parameter
- `export_static.py` - Added sub-sheet bar support for static HTML export

**Important Behaviors:**
1. **Category Movement:** When you move a parent sheet to a different category, all its sub-sheets automatically move with it
2. **F1 Window Display:** Both parent sheets AND sub-sheets are shown side-by-side in the F1 quick navigation window
   - **Main sheets:** Green background (#d1fae5) with green left border (3px)
   - **Sub-sheets:** Blue background (#dbeafe) with blue left border (3px), slightly smaller
   - **Active sheet:** White background with colored border to highlight selection
   - All sheets flow together in a grid layout for easy navigation
3. **Deletion Warning:** Deleting a parent sheet shows a warning that all sub-sheets will also be deleted
4. **Index Reindexing:** After any sheet deletion, all `parentSheet` references are automatically updated to maintain correct relationships

### Recent Sheets Popup (F2)
**Purpose:** Quick navigation to recently viewed sheets with visual indicators for sub-sheets.

**Features:**
- **Keyboard Shortcut:** Press F2 to open recent sheets popup
- **Recent First:** Shows sheets ordered by recency (most recent at top)
- **Current Sheet Highlight:** Active sheet shown with blue background
- **Sub-sheet Indicator:** Sub-sheets display as "Sheet Name [Parent Name]" with parent name greyed and smaller
- **Quick Navigation:** Click or press Enter to switch to a sheet
- **Click Outside to Close:** Popup closes when clicking outside or pressing Escape

**Implementation:**
- **Sheet History:** Tracked in `sheetHistory` array (max 20 sheets)
- **Storage:** Persisted to localStorage for cross-session memory
- **Sub-sheet Display:** Parent name shown in grey, smaller font (12px vs 14px)

**Key Functions:**
- `openF2Popup()` - Opens the popup (~line 5112)
- `closeF2Popup()` - Closes the popup (~line 5134)
- `populateF2RecentSheets()` - Renders sheet list with sub-sheet formatting (~line 5150)

**Files Modified:**
- `static/script.js` - F2 keyboard handler, popup functions, sub-sheet name formatting
- `static/style.css` - F2 popup styles, parent name styling (~line 3151+)
- `templates/index.html` - F2 popup HTML structure (if exists)

**CSS Classes:**
- `.f2-sheets-list` - Container for sheet items
- `.f2-sheet-item` - Individual sheet row
- `.f2-sheet-number` - Sheet position number (#1, #2, etc.)
- `.f2-sheet-name` - Sheet name text
- `.f2-parent-name` - Parent sheet name (greyed, smaller)

### Cell Sort Ranking System
**Purpose:** Pin important rows to the top when sorting by assigning custom sort ranks to cells.

**Features:**
- **Right-Click Menu:** "Set Sort Rank" option (🏆 icon) in cell context menu
- **Rank Badge:** Small blue badge in top-right corner showing rank number
- **Smart Sorting:** Ranked cells sort first (by rank), then unranked cells sort normally
- **Visual Indicator:** Tiny badge (9px font) with semi-transparent blue background
- **Easy Removal:** Set rank to empty to remove

**How It Works:**
1. Right-click on a cell → "Set Sort Rank"
2. Enter a number (e.g., 1, 2, 3)
3. Badge appears in top-right corner
4. When sorting that column:
   - Cells with rank 1 appear first
   - Then rank 2, rank 3, etc.
   - Then all unranked cells (sorted normally)

**Data Storage:**
- Stored in `cellStyles[rowIndex-colIndex].rank`
- Persisted with other cell styles in data.json
- Survives row reordering and sheet switching

**Key Functions:**
- `setCellRank()` - Prompts for rank and applies it (~line 2704)
- `sortColumn()` - Modified to prioritize ranked cells (~line 5002)

**Files Modified:**
- `templates/index.html` - Added "Set Sort Rank" to context menu
- `static/script.js` - Rank setting, badge rendering, sort logic
- `static/style.css` - Badge styling (`.cell-rank-badge`)

**CSS Styling:**
```css
.cell-rank-badge {
    position: absolute;
    top: 2px;
    right: 2px;
    background: #007bff;
    color: white;
    font-size: 9px;
    font-weight: 600;
    padding: 1px 4px;
    border-radius: 3px;
    opacity: 0.85;
}
```

### Context Menu Click-Outside-to-Close
**Purpose:** Improved UX - context menu now closes when clicking outside of it.

**Implementation:**
- Added `closeCellContextMenuOnClickOutside()` listener
- Attached on menu open, removed on menu close
- 10ms delay to prevent immediate closure from the opening click

**Key Functions:**
- `showCellContextMenu()` - Opens context menu (~line 1843)
- `closeCellContextMenu()` - Removes listener
- `closeCellContextMenuOnClickOutside()` - Handles outside clicks

### Cell Color History Feature
**Purpose:** Track and display most frequently used cell color combinations for quick reuse.

**Location:** Right-click cell → "🎨 Cell Colors" → Right sidebar panel

**Features:**
- **Automatic Tracking:** Every color application is tracked in localStorage
- **Most Used Display:** Shows top 10 color combinations sorted by usage count
- **Vertical Sidebar:** 100px wide panel positioned outside main modal on the right
- **Hover to Delete:** × button appears on hover to remove colors from history
- **Visual Preview:** Each item shows "Aa" with actual background and text colors
- **Usage Tooltip:** Hover shows hex colors and usage count

**Key Functions:**
- `showUnifiedColorPickerModal()` - Creates modal with sidebar (~line 2157)
- `loadCellColorHistory()` - Loads and displays history (~line 2445)
- `trackCellColorUsage(bg, fg)` - Tracks color usage (~line 2500)
- `deleteCellColorHistory(index)` - Removes color from history (~line 2490)

**Data Storage:**
- Stored in `localStorage` as `cellColorHistory`
- Format: `[{ bg: '#hex', fg: '#hex', count: number }]`
- Sorted by count (descending) when displayed

**CSS Classes:**
- `.color-history-sidebar` - Right panel container (~line 2040 in style.css)
- `.color-history-list` - Vertical scrollable list
- `.cell-color-history-item` - Individual color item (50px height)
- `.cell-history-delete` - Delete button (appears on hover)

### Sidebar Navigation & Tree View
**Purpose:** Modern sidebar navigation with collapsible category tree structure for organizing sheets.

**Features:**
- **Tree Structure:** Categories as folders, sheets as files with visual CSS tree lines
- **Collapsible Categories:** Click folder icon to expand/collapse (no separate arrow)
- **Visual Indicators:**
  - 📁 Closed folder (collapsed category)
  - 📂 Open folder (expanded category)
  - 📄 Sheet file icon
  - CSS-based tree lines (├─, └─, │) connecting sheets
- **Context Menus:** Right-click on categories or sheets to access actions (Rename, Delete, Add Sheet, etc.)
- **Sub-sheet Handling:** Sub-sheets hidden from tree (shown in Sub-Sheet Bar when parent selected)
- **Active Sheet Highlight:** Current sheet shown with blue background
- **Compact Design:** No header bar - maximizes space for tree content

**UI Components:**
1. **Hamburger Button (☰):** Toggles sidebar open/closed from top-left
2. **Sidebar Panel:**
   - **Toolbar:** "📁+ Add Category" button at top
   - **Tree Container:** Scrollable area with category/sheet tree
3. **Tree Items:**
   - **Categories:** Start collapsed by default, folder icon changes on expand/collapse
   - **Sheets:** Indented with CSS tree lines (no text characters like ├─)

**Tree Line Implementation:**
- Tree lines created with CSS `::before` and `::after` pseudo-elements (not text characters)
- Vertical line (│) connects items using `::before`
- Horizontal line (─) extends from vertical using `::after`
- Last item shows └─ corner (no line below)
- Categories have NO tree lines (clean appearance)

**CSS Tree Lines:**
```css
.tree-sheet::before {  /* Vertical line (│) */
    content: '';
    position: absolute;
    left: 20px;
    top: 0;
    bottom: 50%;
    width: 1px;
    background: #ccc;
}

.tree-sheet::after {  /* Horizontal line (─) */
    content: '';
    position: absolute;
    left: 20px;
    top: 50%;
    width: 12px;
    height: 1px;
    background: #ccc;
}

.tree-sheet.last::before {  /* Last item: └─ instead of ├─ */
    bottom: 50%;
}
```

**Key Functions:**
- `toggleSidebar()` - Opens/closes sidebar with slide animation (~line 8200)
- `renderSidebar()` - Renders category tree structure (~line 8224)
- `showTreeContextMenu(event, type, id)` - Right-click menu for categories/sheets (~line 8320)

**Files Modified:**
- `templates/index.html` - Sidebar HTML structure (no header, just toolbar + tree)
- `static/style.css` - Sidebar, tree, and CSS tree line styles
- `static/script.js` - Tree rendering with folder icon toggle logic
- `export_static.py` - Full sidebar support (replaces dropdowns in static export)

**Header Display:**
- Current sheet name and category shown in top bar
- Updates automatically when switching sheets
- Format: `Sheet Name` / `Category Name`

**Static Export:**
- Full sidebar functionality included
- Dropdowns removed (replaced by sidebar tree)
- Same visual appearance and behavior as main app

## Settings Modal (⚙️)

The Settings Modal provides centralized access to application-wide customization options. Access it by clicking the ⚙️ button in the toolbar.

### Settings Sections

#### 🎨 Appearance
- **Grid Line Color** - Customize table border colors
- **Vrinda Font Toggle** - Enable/disable Vrinda font for Bangla text

#### 🎨 Custom Color Syntax
- **Dynamic Syntax Creation** - Add unlimited custom color highlight syntaxes
- **Full Customization** - Choose any marker characters and colors
- **Live Management** - Add, edit, or remove syntaxes with instant preview
- See "Custom Color Syntax Feature" section for detailed documentation

#### 📚 Help & Documentation
- **Markdown Guide** - View comprehensive markdown formatting reference
- **Interactive Examples** - See syntax and rendered output side-by-side

### Key Features
- **Persistent Settings** - All preferences saved to localStorage
- **Real-time Updates** - Changes apply immediately without page reload
- **Static Export Support** - Settings modal fully functional in exported HTML files
- **Responsive Design** - Modal adapts to different screen sizes

### Implementation
- **Modal Structure:** Defined in `templates/index.html` (~line 420+)
- **JavaScript Functions:** Located in `static/script.js` (~line 9020+)
- **Styling:** Custom modal styles in `static/style.css`
- **Static Export:** Full modal HTML and JS included in `export_static.py`

### Grid Line Color Customization
**Purpose:** Allows users to customize the color of table borders and cell separators.

**Implementation:**
- **CSS Variable:** Uses `--grid-line-color` CSS variable (default: `#dddddd`)
- **Settings UI:** Added settings modal with color picker and hex input
- **Storage:** Color preference saved to `localStorage` as `gridLineColor`
- **Application:** Applied to all `th` and `td` borders via CSS variable
- **Custom Borders:** Cells with custom borders (via cell styling) override the grid line color

**Settings Modal Features:**
- Color picker for visual selection
- Hex code input for precise color entry
- Reset button to restore default color (#dddddd)
- Real-time preview (changes apply immediately)

**Static Export Support:**
- Settings button (⚙️) added to toolbar
- Full settings modal included in static HTML
- Loads saved color from localStorage on page load
- All JavaScript functions included for color management

**Key Functions:**
- `openSettings()` - Opens settings modal and loads current color
- `closeSettings()` - Closes settings modal
- `syncGridLineColor(value)` - Syncs color picker and hex input
- `applyGridLineColor(color)` - Applies color to CSS variable and saves to localStorage
- `resetGridLineColor()` - Resets to default #dddddd

**Files Modified:**
- `export_static.py` - Added CSS variable, settings modal HTML, and JavaScript functions
- CSS styles for modal, color picker, and input fields

## Recent Bug Fixes & Improvements

### Cell Style Reindexing After Row Deletion
**Issue:** When deleting rows, cell styles (colors, borders, etc.) would shift to wrong cells because the row indices in `cellStyles` keys weren't updated.

**Solution:** Added `reindexCellStylesAfterRowDeletion()` function that:
- Takes deleted row indices and recalculates new row positions
- Updates all `cellStyles` and `mergedCells` keys to reflect new row numbers
- Skips styles for deleted rows
- Called automatically after `deleteEmptyRows()`

**Key Functions:**
- `reindexCellStylesAfterRowDeletion()` - Reindexes cell styles after deletion
- `deleteEmptyRows()` - Calls reindexing after deleting rows

### Color Syntax Wrapping & Display Fix
**Issue:** All color syntaxes (`==`, `!!`, `??`, and `{fg:...;bg:...}`) were using `display: inline-block`, which forced text to stay on one line and pushed subsequent text to the next line, creating large gaps and breaking text flow.

**Solution:** Unified styling across all color syntaxes for consistent inline behavior:
- **Changed `display: inline-block` to `display: inline`** - Allows natural text wrapping and inline flow
- **Removed `margin-top` and `margin-right`** - Not needed with inline display
- **Added `box-decoration-break: clone`** - Ensures background color and border-radius continue properly when text wraps to multiple lines
- **Consistent padding:** `1px 4px` for all color syntaxes
- **Applied to all parsers:** Both `parseMarkdownInline()` (table cells) and `oldParseMarkdownBody()` (regular cells)

**Affected Syntaxes:**
- `==text==` (black) - Uses `<mark>` tag with CSS
- `!!text!!` (red) - Inline styles
- `??text??` (blue) - Inline styles  
- `{fg:color;bg:color}text{/}` - Custom colors with inline styles

**Files Modified:**
- `static/script.js` - Updated all color syntax inline styles in both parsers
- `static/style.css` - Updated `mark` tag CSS
- `export_static.py` - Updated all color syntax inline styles in both parsers

**Result:** All color highlights now flow naturally with text, wrap properly across lines, and maintain consistent styling.

### Sub-Sheet Parent Reference Fix (F1 Drag & Drop)
**Issue:** When dragging sheets to reorder them in the F1 popup, sub-sheets would lose their parent references or point to wrong parents, breaking the hierarchy.

**Solution:** Updated `handleF1Drop()` to properly maintain parent-child relationships:
- Mark sub-sheets whose parent is being moved (temporary marker: -1)
- Adjust all `parentSheet` indices after sheet removal
- Adjust all `parentSheet` indices after sheet insertion
- Update marked sub-sheets to point to parent's new position

**Key Function:**
- `handleF1Drop()` - Handles drag and drop in F1 popup (~line 7050)

**Files Modified:**
- `static/script.js` - Updated drag and drop logic with parent reference tracking

### Move to Category Sheet Index Fix
**Issue:** When right-clicking a sheet in the tree and selecting "Move to Category", it would move the currently active sheet instead of the right-clicked sheet. This caused confusion and required multiple manual moves.

**Solution:** Store the sheet index when opening the modal:
- Added `moveToCategorySheetIndex` variable to track which sheet was right-clicked
- `showMoveToCategoryModal(sheetIndex)` now stores the passed index
- Form handler uses stored index instead of `currentSheet`
- Correctly moves the right-clicked sheet and all its sub-sheets in one action

**Key Functions:**
- `showMoveToCategoryModal()` - Stores sheet index (~line 3362)
- `moveToCategoryForm.onsubmit` - Uses stored index (~line 3452)

**Files Modified:**
- `static/script.js` - Added index tracking, updated form handler

### F1 Popup Cyberpunk Styling
**Purpose:** Redesigned F1 Quick Navigation popup with dark terminal/cyberpunk aesthetic.

**Key Functions:**
- `openF1Popup()` - Opens F1 popup (~line 5179 in script.js)
- `closeF1Popup()` - Closes F1 popup
- `filterF1Sheets()` - Filters sheets based on search input (~line 7420)
- `toggleF1SearchMode()` - Cycles through search modes (~line 7403)
- `populateF1Categories()` - Renders category list

**Search Mode Toggle Feature:**
- **Button:** Left of search input, cycles through 3 modes on click
- **Modes:** 
  - 🔍 Normal (gray) - Search current category
  - * All sheets (green #00ff9d) - Search all sheets by name
  - # Content (cyan #00f3ff) - Search inside sheet content
- **Persistence:** Mode saved to `localStorage.f1SearchMode`, persists across refreshes
- **Auto-prefix:** Automatically prepends * or # to search queries based on mode
- **Variable:** `f1SearchMode` stores current mode ('', '*', or '#')

**Main CSS Classes:**
- `.f1-popup` - Dark background (#0d0d0d), green border (#00ff9d)
- `.f1-search-mode-toggle` - Toggle button with hover effects (~line 2136)
- `.f1-category-title`, `.f1-sheets-title` - Combined definition at line ~2177
- `.f1-category-radio` - Hidden with `display: none`
- `.f1-parent-sheet.active` - Bright green (#00ff9d)
- `.f1-sub-sheet.active` - Bright cyan (#00f3ff)

### F2 Popup Cyberpunk Styling
**Purpose:** Recent Sheets popup (F2) styled to match F1 cyberpunk theme.

**Key Functions:**
- `openF2Popup()` - Opens F2 popup, clears search, focuses input (~line 5236)
- `closeF2Popup()` - Closes F2 popup (~line 5257)
- `filterF2Sheets()` - Filters recent sheets by name (~line 5273)
- `populateF2RecentSheets()` - Renders recent sheets list (~line 5291)

**Features:**
- **Search box** - Real-time filtering of recent sheets
- **Auto-focus** - Search input focused on open
- **Cyberpunk styling** - Dark green theme matching F1
- **Sky blue parent names** - Parent sheet names in brackets use #5dade2
- **Green scrollbar** - Custom scrollbar matching theme

**Main CSS Classes:**
- `.f2-sheets-list` - Container with green scrollbar (~line 3268)
- `.f2-sheet-item` - Dark green background, green left border (~line 3278)
- `.f2-sheet-number` - Green bordered number badge (~line 3310)
- `.f2-parent-name` - Sky blue color for parent sheet indicator (~line 3336)

**Critical Issues Encountered:**

**1. Duplicate CSS Causing Style Conflicts**
- **Problem:** Found multiple `.f1-sheets-title` definitions at lines ~3519 and ~3715 overriding main styles
- **Why it happened:** CSS file had accumulated duplicate sections over time
- **Solution:** Used `strReplace` with unique context strings to remove duplicates
- **Lesson:** When using `strReplace`, if string appears multiple times, include more surrounding context to make it unique
- **Search tip:** Use `grepSearch` to find all occurrences and their line numbers first

**2. strReplace Failing with "found multiple times" Error**
- **Problem:** Trying to replace duplicate sections kept failing because identical code existed in multiple places
- **Solution:** Read more context (20-30 lines before/after) to find unique surrounding code, then include that in the replacement
- **Example:** Instead of replacing just the duplicate block, include the unique function/comment before it

**Files Modified:**
- `static/style.css` - Lines ~2056-2530 (F1 popup styles)
- `templates/index.html` - Line ~650 (removed header, moved close button)

## Font System

### Default Font Configuration

The application uses a **dual-font system** to support both English and Bangla text:

**Default Font Stack:**
```css
font-family: Vrinda, 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
```

- **Vrinda** - Primary font for Bangla characters (Windows system font)
- **Segoe UI, Tahoma, etc.** - Fallback fonts for English and other languages

### Where Fonts Are Applied

1. **Table Cells (td input)** - Line ~556 in `style.css`
2. **Textareas (td textarea)** - Line ~561 in `style.css`
3. **Markdown Preview** - Line ~720 in `style.css`
4. **Merged Cell Textareas** - Line ~1690 in `style.css`

### Vrinda Font Toggle

Users can disable Vrinda font via **Settings → Use Vrinda Font for Bangla**

**How it works:**
- **Enabled (default):** Uses `Vrinda` as first font in the stack
- **Disabled:** Adds `.disable-vrinda` class to table, which overrides with `!important`:
  ```css
  .disable-vrinda td input,
  .disable-vrinda td textarea {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
  }
  ```

**State Management:**
- Stored in `localStorage` as `vrindaFontEnabled` (default: `true`)
- Function: `toggleVrindaFont(enabled)` in `script.js` ~line 2953
- Initialized on page load ~line 187

### Column-Specific Fonts

Users can set custom fonts per column via **Column Settings (F3)**:

**Available Fonts:**
- Default (uses Vrinda stack)
- JetBrains Mono (loaded from Google Fonts)
- Arial
- Courier New
- Georgia
- Times New Roman
- Verdana
- Agency FB
- Comic Sans MS

**Implementation:**
- Column font is stored in `tableData.sheets[n].columns[n].font`
- Applied as inline style during `renderTable()`
- Takes precedence over default Vrinda font stack

### Font Loading

**JetBrains Mono** is loaded from Google Fonts in `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&display=swap" rel="stylesheet">
```

### Mobile/Cross-Platform Considerations

**Issue:** System fonts like Vrinda, Comic Sans, and custom fonts may not be available on all devices (especially mobile).

**Solutions:**
1. **Vrinda (Bangla):** Only available on Windows. On other platforms, falls back to system default.
2. **JetBrains Mono:** Loaded from Google Fonts, works cross-platform.
3. **Other fonts:** System-dependent. Consider adding web font fallbacks for critical fonts.

**For Static Export:**
- JetBrains Mono is included via Google Fonts link
- Other system fonts (Vrinda, Comic Sans, etc.) will only work if installed on the viewing device
- Consider adding web font alternatives (e.g., Noto Sans Bengali for Bangla) if cross-platform support is critical


## Quick Function Reference - Table Features

### Pipe Table Parsing & Rendering
- **`parseGridTable(lines)`** - Main function that parses pipe tables into HTML grid (~line 1100 in script.js)
  - Handles color codes (`:R-A:`, `:G:`, etc.)
  - Handles alignment (`:text:`, `text:`)
  - Handles rowspan with `^^` syntax (cells merge with cell above)
  - Removes leading/trailing pipes
  - Generates separator rows
  - Location: `static/script.js` ~line 1100, `export_static.py` ~line 1524

### Table Rowspan Feature
- **Syntax:** `^^` in a cell merges it with the cell directly above
- **Implementation:** Two-pass algorithm:
  1. First pass: Identify `^^` cells and calculate rowspan counts
  2. Second pass: Render cells with `grid-row: span N` style, skip `^^` cells
- **Functions:**
  - `parseGridTable()` - Handles rowspan for pipe tables (~line 1100)
  - `parseCommaTable()` - Handles rowspan for comma tables (~line 1106)
- **CSS:** Uses CSS Grid's `grid-row: span N` property for spanning
- **Works with:** Colors, alignment, borders, all table features
- **Documentation:** See `md/TABLE_ROWSPAN.md` for examples

### Table Formatter (F3 → 📊)
- **`formatPipeTable(event)`** - Auto-formats and aligns pipe tables (~line 6070 in script.js)
  - Calculates optimal column widths (ignores separator rows)
  - Pads cells with spaces
  - Regenerates separator rows
  - Adds leading/trailing pipes if missing
  - Location: `static/script.js` ~line 6070

### Table Detection
- **`isTableLine(line)`** - Detects if a line is part of a pipe table (~line 1451 in script.js)
  - Checks for pipes and minimum column count
  - Location: `static/script.js` ~line 1451

### Color & Alignment Processing
- **Column-wide colors**: Processed in `parseGridTable()` with `:COLOR-A:` syntax
- **Per-cell colors**: Processed in `parseGridTable()` with `:COLOR:` syntax
- **Alignment markers**: `:text:` (center), `text:` (right) processed in `parseGridTable()`

### CSS Styling
- **`.md-grid`** - Grid container with CSS Grid layout (~line 2678 in style.css)
- **`.md-cell`** - Individual table cells with 3px right border (~line 2689 in style.css)
- **`.md-header`** - Header row styling with bottom border (~line 2699 in style.css)
### Dynamic Cursor & Click-to-Edit
**Purpose:** Improves the editing experience in cells with rendered markdown by ensuring precise cursor placement and visibility.

**Problem:** 
- Markdown cells display a *rendered preview* overlay on top of the raw text input.
- Clicking on the rendered preview (e.g., "Big Text") typically focuses the input at the *end* or an incorrect position because the rendered text size/layout differs from the raw markdown syntax characters.
- The default system cursor is often thin and hard to see in dense text.

**Solution Implementation:**
1.  **Smart Click Positioning (`handlePreviewMouseDown`):**
    - **Trigger:** Intercepts `mousedown` events on the `.markdown-preview` overlay.
    - **Logic:**
        - Prevents default browser focus (which causes jumping).
        - Identifies the exact text node and character offset clicked in the preview.
        - Calculates the "N-th occurrence" of that text segment in the preview.
        - Maps this to the corresponding N-th occurrence in the **raw markdown source** in the hidden input.
        - Synchronously focuses the input and sets `selectionStart` / `selectionEnd` to the calculated index.
        - Uses `focus({ preventScroll: true })` to stop the browser from scrolling wildly.
    - **Result:** Clicking a word in the preview places the cursor exactly at that word in the raw markdown.

2.  **Custom Block Cursor:**
    - **Visuals:** Replaces the native thin cursor (hidden via `caret-color: transparent`) with a **5px thick black blinking block** (`.custom-cursor`).
    - **Positioning (`updateCustomCursor`):**
        - Uses a "Mirror Element" technique: Creates an invisible duplicate of the textarea with identical font/wrapping styles.
        - Inserts text up to the cursor position into the mirror.
        - Appends a marker element (`|`) to find the exact pixel coordinates of the end of the text.
        - Calculates the **Absolute Document Position** by combining:
            - Mirror Element Position (Document Relative)
            - Internal Text Scrolloffset (`input.scrollTop`)
            - Window Scroll Position (`window.scrollY`)
        - Updates on `input`, `click`, `scroll` (window & element), and `selectionchange` events.
    - **Visibility:** Automatically hides if the cursor moves out of the visible viewport of the scrolling text box.

3.  **Scroll Stabilization:**
    - Uses `keepCursorCentered(textarea)` to manually scroll the textarea so the cursor line is always vertically centered after a click, ensuring the user immediately sees their edit point.

### PDF Export Feature
**Purpose:** Export individual cells (with maintained formatting/styling) to a downloadable PDF file.

**Implementation:**
- **Libraries:** Uses `jsPDF` for PDF generation and `html2canvas` for visual capture.
- **Workflow:**
    1.  User selects **Context Menu > Export Cell to PDF**.
    2.  Prompts for filename.
    3.  **Visual Capture:** Renders cell content into an off-screen container that mimics the exact styling (fonts, colors, markdown).
    4.  **Scaling:** Automatically calculates PDF page height to fit *all* content (no cut-offs for long text).
    5.  **Generation:** Captures container as high-quality image -> Adds to PDF -> Downloads.
- **Key Function:** `captureAndGeneratePDF(container, filename)` in `static/script.js`.

### Copy Sheet Content Feature
**Purpose:** Quickly copy all text from the current sheet to the clipboard, formatted for easy reading.

**Access:** 📋 Clipboard button in Toolbar (next to 👁️ toggle).

**Behavior:**
- Collects text from all non-empty cells.
- **Row Separation:** Joins cells in a row with spaces.
- **Gap Separation:** Joins different rows with **double newlines** (`\n\n`), creating a distinct one-line gap between each row's content.
- **Types:** Safely handles strings, numbers, and empty cells.
- **Fallback:** Uses ancient `document.execCommand('copy')` as a backup if the modern Clipboard API is blocked (e.g., non-secure HTTP).
- **Key Function:** `copySheetContent()` in `static/script.js`.