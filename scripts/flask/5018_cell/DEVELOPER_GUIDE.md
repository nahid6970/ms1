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
- **Rich markdown formatting** in cells (bold, italic, colors, tables, math, collapsible text, etc.)
- **Cell styling** (borders, colors, fonts, alignment, merging)
- **Column customization** (width, type, styling, header styling)
- **Search functionality** with multi-term support and highlighting
- **Keyboard shortcuts** (F1-F4, Alt+M, Ctrl+S, etc.)
- **Quick Formatter** (F2) for instant text formatting
- **Static export** for sharing spreadsheets as standalone HTML files

## ⚡ Critical Implementation Rule: "The Rule of 4"

When adding new **Markdown Syntax** or **Cell Formatting Features**, you **MUST** implement logic in at least **4 specific locations** in `static/script.js` to ensure the feature works consistently (persists on reload, renders correctly, and doesn't break sorting).

### 1. `parseMarkdown(text)` & Parsing Logic
**Location:** `static/script.js` ~ line 980+
**Purpose:** Converts the raw text syntax into HTML.
**Action:** Add your regex or parsing logic here.
*   *Example:* For `Table*N`, we added detection for `(?:^|\n)Table\*(\d+)` (allowing text before it) and a helper function `parseCommaTable`.
*   *Example:* For bold `**text**`, we use `.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')`.
*   *Example:* For collapsible text `{{text}}`, we use `.replace(/\{\{(.+?)\}\}/g, ...)` to create a toggle button with hidden content.

### 2. `checkHasMarkdown(value)`
**Location:** `static/script.js` ~ line 780+
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

### 3. `renderTable()`
**Location:** `static/script.js` ~ line 3947+
**Purpose:** Renders the table rows and cells.
**Action:** **NO ACTION REQUIRED.**
*   The `renderTable()` function has been optimized to automatically call `applyMarkdownFormatting()` for every cell.
*   It uses a `DocumentFragment` to build the entire table body in memory before appending it to the DOM, significantly reducing reflows.
*   `applyMarkdownFormatting()` internally calls `checkHasMarkdown()` to decide whether to render a preview.
*   Therefore, you only need to update `checkHasMarkdown()` (Step 2) and `parseMarkdown()` (Step 1).

### 4. `stripMarkdown(text)`
**Location:** `static/script.js` ~ line 4060+
**Purpose:** Removes your syntax so that sorting and searching work on the *content*, not the *markup*.
**Action:** Add a regex replace to strip your syntax tags.
```javascript
function stripMarkdown(text) {
    // ...
    text = text.replace(/YourRegex/g, '$1'); // <--- ADD THIS
    return text;
}
```

## New Features & Enhancements

### Collapsible Text Feature
**Syntax:** `{{hidden text}}`
**Purpose:** Hides text behind a toggle button (👁️) that can be clicked to show/hide the content.
**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/\{\{(.+?)\}\}/g` detects the syntax and generates HTML with a button and hidden span.
- **Detection:** Added `value.includes('{{')` to the `hasMarkdown` checks.
- **Stripping:** Added `.replace(/\{\{(.+?)\}\}/g, '$1')` to `stripMarkdown()`.
- **CSS:** Added `.collapsible-wrapper`, `.collapsible-toggle`, and `.collapsible-content` styles with baseline alignment.
- **Quick Formatter:** Added a 👁️ button to wrap selected text with `{{}}`.
- **Static Export:** Updated `export_static.py` with the same parsing logic.
- **Key Functions:**
  - `parseMarkdown()` - Converts `{{text}}` to HTML
  - `checkHasMarkdown()` - Detects the syntax
  - `stripMarkdown()` - Removes syntax for sorting/searching
  - `toggleAllCollapsibles()` - Shows/hides all collapsible text at once

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
- **Improved UX:** Streamlined workflow - select text, press F2, click format button, done.
- **Key Functions:**
  - `showQuickFormatter()` - Opens the formatter popup (F2 shortcut)
  - `applyQuickFormat()` - Applies formatting instantly without Apply button
  - Various format functions: `makeBold()`, `makeItalic()`, `makeUnderline()`, etc.

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
- **Parsing:** In `parseMarkdown()`, the regex `/^-{5,}$/gm` converts to `<hr>` with custom styling
- **Detection:** Added `str.match(/^-{5,}$/m)` to `checkHasMarkdown()`
- **Stripping:** Added `.replace(/^-{5,}$/gm, '')` to `stripMarkdown()` to remove for sorting/searching
- **Styling:** 2px solid gray line with 8px vertical margin
- **Markdown Guide:** Added to the Code & Highlights section
- **Static Export:** Updated `export_static.py` with the same parsing logic
- **Key Functions:**
  - `parseMarkdown()` - Converts `-----` to `<hr>` element
  - `checkHasMarkdown()` - Detects 5+ dashes on a line
  - `stripMarkdown()` - Removes separator for sorting/searching

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
