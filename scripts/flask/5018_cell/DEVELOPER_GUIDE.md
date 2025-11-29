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
- **Rich markdown formatting** in cells (bold, italic, colors, tables, math, collapsible text, etc.)
- **Cell styling** (borders, colors, fonts, alignment, merging)
- **Column customization** (width, type, styling, header styling)
- **Search functionality** with multi-term support and highlighting
- **Keyboard shortcuts** (F1-F4, Alt+M, Ctrl+S, etc.)
- **Quick Formatter** (F2) for instant text formatting
- **Static export** for sharing spreadsheets as standalone HTML files

## ⚡ Critical Implementation Rule: "The Rule of 6"

When adding new **Markdown Syntax** or **Cell Formatting Features**, you **MUST** implement logic in at least **6 specific locations** to ensure the feature works consistently across both the live app and static export.

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
- **Parsing:** Added regex replacements in `parseMarkdown()`: `.replace(/==(.+?)==/g, '<mark>$1</mark>')` and similar for `!!` and `??`.
- **Detection:** Added `value.includes('!!')` and `value.includes('??')` to `hasMarkdown` checks.
- **Stripping:** Added `.replace(/!!(.+?)!!/g, '$1')` and `.replace(/\?\?(.+?)\?\?/g, '$1')` to `stripMarkdown()`.
- **Quick Formatter:** Added Black, Red, and Blue buttons in a separate "Quick Highlights" section.
- **Static Export:** Updated `export_static.py` with the same parsing logic.
- **Key Functions:**
  - `parseMarkdown()` - Converts highlight syntax to HTML
  - `checkHasMarkdown()` - Detects the syntax
  - `stripMarkdown()` - Removes syntax for sorting/searching

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
- **Key Functions:**
  - `searchTable()` - Main search logic with comma-splitting
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
- **Usage:** Select text in a cell, press F2, and click the appropriate conversion button.
- **Key Functions:**
  - `linesToComma()` - Converts line breaks to commas
  - `commaToLines()` - Converts commas to line breaks

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

### Horizontal Separator Feature
**Syntax:** `-----` (5 or more dashes on a single line)
**Purpose:** Creates a horizontal separator line to visually divide content sections.
**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/^-{5,}$/gm` converts to `<div class="md-separator"></div>`
- **Detection:** Added `str.match(/^-{5,}$/m)` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/^-{5,}$/gm, '')` to `stripMarkdown()` to remove for sorting/searching
- **Styling:** 4px solid gray div with 12px equal vertical margin (CSS class `.md-separator`)
- **Spacing Fix:** In `oldParseMarkdownBody()`, uses `reduce()` instead of `join('\n')` to skip newlines before/after separators, preventing double spacing
- **Markdown Guide:** Added to the Code & Highlights section
- **Static Export:** Updated `export_static.py` with the same parsing logic and reduce() for proper spacing
- **Key Functions:**
  - `parseMarkdown()` - Converts `-----` to separator div
  - `checkHasMarkdown()` - Detects 5+ dashes on a line
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
- **F1** - Reorder categories
- **F2** - Quick Formatter (format selected text)
- **F3** - Column settings for current column
- **F4** - Toggle ribbons (hide/show toolbar and sheet tabs)
- **Alt+M** - Toggle between current and previous sheet
- **Ctrl+S** - Save data
- **Ctrl+F** - Focus search box
- **\*** in search - Search by sheet nickname

## Common Development Tasks

### Adding a New Markdown Syntax
1. Add parsing logic to `parseMarkdown()` (~line 980+)
2. Add detection to `checkHasMarkdown()` (~line 780+)
3. Add stripping logic to `stripMarkdown()` (~line 4060+)
4. Update `export_static.py` with same parsing logic
5. Add to Markdown Guide modal in `templates/index.html`
6. Test: Create cell with syntax, check preview, search, sort, and static export

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
- **Category inheritance:** Sub-sheets automatically inherit their parent's category
- **Deletion cascade:** Deleting a parent deletes all its sub-sheets
- **Navigation:** Clicking any tab switches to that sheet

**Key Functions:**
- `renderSubSheetBar()` - Renders the horizontal sub-sheet navigation bar
- `addSubSheet(parentIndex)` - Creates a new sub-sheet under the specified parent
- `showSubSheetContextMenu(event, sheetIndex)` - Shows right-click menu for rename/delete
- `deleteSheet(index)` - Deletes sheet and reindexes all parent references

**CSS Classes:**
- `.subsheet-bar` - Container for the navigation bar
- `.subsheet-tabs` - Flex container for tabs
- `.subsheet-tab` - Individual sheet tab (compact, wraps naturally)
- `.subsheet-tab.active` - Currently active sheet (blue background)
- `.subsheet-add-btn` - + button to add sub-sheets
- `.subsheet-context-menu` - Right-click context menu

**Files Modified:**
- `templates/index.html` - Added sub-sheet bar HTML
- `static/script.js` - Added rendering, creation, and context menu logic
- `static/style.css` - Added sub-sheet bar and context menu styles
- `app.py` - Updated API to accept `parentSheet` parameter

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

### Color Highlight Spacing Fix (Static Export)
**Issue:** In static HTML export, colored text boxes (`==text==`, `!!text!!`, `??text??`, `{fg:...;bg:...}`) had inconsistent vertical spacing between lines.

**Solution:** Applied specific styling to reduce spacing:
- **Padding:** Reduced to `0px` top/bottom (from `2px`)
- **Margin-top:** Set to `-2px` to pull boxes closer together
- **Line-height:** Reduced to `1.3` (from `1.8`)
- **Display:** Set to `inline-block` with `vertical-align: baseline`
- **Margin-right:** Added `2px` for spacing between adjacent highlights

**Note:** Main app uses slightly different values (`1px` padding, `-1px` margin-top) which work better in the live environment. Static export needs more aggressive spacing reduction.

**Files Modified:**
- `export_static.py` - Updated all color highlight styling
- CSS for `mark` tag in embedded styles


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
