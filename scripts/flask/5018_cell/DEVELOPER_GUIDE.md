# Project Developer Guide & Documentation

This document serves as a guide for understanding the codebase, specifically the custom spreadsheet application. It highlights key architectural decisions and provides a checklist for implementing new features to ensure consistency across the application.

## Project Overview
This is a Flask-based web application that provides a dynamic, spreadsheet-like interface (`5018_cell`). It supports rich text formatting via Markdown, custom grid tables, and real-time data manipulation.

### Key Files
- **`app.py`**: Flask backend handling routes, API endpoints for data persistence (loading/saving JSON), and serving static files.
- **`static/script.js`**: The core logic engine. Handles state management (`tableData`), rendering (`renderTable`), event listeners, and Markdown parsing.
- **`static/style.css`**: Custom styling for the grid, modals, and markdown elements.
- **`templates/index.html`**: The main application shell.

## ⚡ Critical Implementation Rule: "The Rule of 4"

When adding new **Markdown Syntax** or **Cell Formatting Features**, you **MUST** implement logic in at least **4 specific locations** in `static/script.js` to ensure the feature works consistently (persists on reload, renders correctly, and doesn't break sorting).

### 1. `parseMarkdown(text)` & Parsing Logic
**Location:** `static/script.js` ~ line 980+
**Purpose:** Converts the raw text syntax into HTML.
**Action:** Add your regex or parsing logic here.
*   *Example:* For `Table*N`, we added detection for `(?:^|\n)Table\*(\d+)` (allowing text before it) and a helper function `parseCommaTable`.
*   *Example:* For bold `**text**`, we use `.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')`.
*   *Example:* For collapsible text `{{text}}`, we use `.replace(/\{\{(.+?)\}\}/g, ...)` to create a toggle button with hidden content.

### 5. Collapsible Text Feature (New)
**Syntax:** `{{hidden text}}`
**Purpose:** Hides text behind a toggle button (👁️) that can be clicked to show/hide the content.
**Implementation:**
- **Parsing:** In `parseMarkdown()`, the regex `/\{\{(.+?)\}\}/g` detects the syntax and generates HTML with a button and hidden span.
- **Detection:** Added `value.includes('{{')` to the `hasMarkdown` checks in both `applyMarkdownFormatting()` and `renderTable()`.
- **Stripping:** Added `.replace(/\{\{(.+?)\}\}/g, '$1')` to `stripMarkdown()` to remove the markers when clearing formatting.
- **CSS:** Added `.collapsible-wrapper`, `.collapsible-toggle`, and `.collapsible-content` styles with baseline alignment.
- **Quick Formatter:** Added a 👁️ button to wrap selected text with `{{}}`.
- **Static Export:** Updated `export_static.py` with the same parsing logic in both `parseMarkdownInline()` and `oldParseMarkdownBody()`.

### 6. Multi-Term Search Feature
**Syntax:** `term1, term2, term3` (comma-separated)
**Purpose:** Search for multiple terms at once. Shows rows containing ANY of the search terms.
**Implementation:**
- **Search Logic:** In `searchTable()`, the search input is split by commas: `searchTerm.split(',').map(term => term.trim().toLowerCase())`
- **Matching:** Each cell is checked against all terms, and if any term matches, the row is shown.
- **Highlighting:** All matching terms are highlighted using `highlightMultipleTermsInHtml()` which:
  - Finds all matches for all terms
  - Sorts and merges overlapping matches
  - Creates highlights in a single pass to avoid conflicts
- **Overlay:** For cells without markdown preview, `createTextHighlightOverlayMulti()` creates an overlay that exactly matches the input's position and styling.
- **Feedback:** Toast message shows which terms were found, e.g., "Found 5 row(s) matching: johnny, donny"

### 7. Table Syntax Enhancements
We have enhanced the `Table*N` syntax to support more complex layouts:
- **Flexible Placement:** Tables can now be placed anywhere in the cell, not just at the beginning.
- **Explicit Termination (`Table*end`):** Users can explicitly close a table using `Table*end`. This is crucial for placing text *after* a table or stacking multiple tables in one cell.
- **Multiple Tables:** The parser now recursively handles multiple tables within a single cell.
- **Empty Line Preservation:** We use `white-space: pre-wrap` in the preview to ensure empty lines between tables and text are respected.

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
*   `applyMarkdownFormatting()` internally calls `checkHasMarkdown()` to decide whether to render a preview.
*   Therefore, you only need to update `checkHasMarkdown()` (Step 2) and `parseMarkdown()` (Step 1).

### 4. `stripMarkdown(text)`
**Location:** `static/script.js` ~ line 4060+
**Purpose:** Removes your syntax so that sorting and searching work on the *content*, not the *markup*.
**Action:** Add a regex replace to strip your syntax tags.
```javascript
The grid system relies on CSS variables for dynamic column counts:
```css
.md-grid {
    display: grid;
    grid-template-columns: repeat(var(--cols), auto);
    /* ... */
}
```

### Data Structure
The application state is held in `tableData`:
```javascript
let tableData = {
    sheets: [
        {
            name: "Sheet1",
            rows: [ ["cell1", "cell2"], ... ],
            columns: [ { width: 100, type: 'text' }, ... ],
            cellStyles: { "0-0": { bold: true } } // Key is "row-col"
        }
    ],
    activeSheet: 0
};
```

### Column Styling
Column-wide styles (like background color, font, text color) are stored in the `columns` array.
**Implementation Rule:** In `renderTable()`, these styles must be applied to the `<td>` or `<input>`/`<textarea>` elements *before* applying cell-specific styles (`cellStyles`). This ensures that:
1.  Column defaults are applied to all cells in the column.
2.  Individual cell styles (e.g., from context menu) can override the column defaults.

## Future Improvements Checklist
- [ ] When adding new syntax, update the "Markdown Guide" modal in `templates/index.html` so users know it exists.
- [ ] Check `style.css` for dark mode compatibility if adding new UI elements.
