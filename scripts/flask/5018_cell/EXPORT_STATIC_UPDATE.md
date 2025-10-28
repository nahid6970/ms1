# Export Static Update - Table Markdown Support

## Overview
Updated `export_static.py` to include the new CSS Grid table markdown feature, ensuring exported HTML files have the same table rendering capabilities as the main application.

## Changes Made

### 1. Added Helper Functions (Before parseMarkdown)

#### `parseGridTable(lines)`
Converts pipe-separated lines into CSS Grid HTML:
```javascript
function parseGridTable(lines) {
    const rows = lines.map(l =>
        l.trim().replace(/^\\|\\|$/g, '').split('|').map(c => c.trim()));
    const cols = rows[0].length;
    const grid = rows.map(r =>
        r.map(c => parseMarkdownInline(c))
    );
    
    let html = `<div class="md-grid" style="--cols:${cols}">`;
    grid.forEach((row, i) => {
        row.forEach(cell => {
            html += `<div class="md-cell ${i ? '' : 'md-header'}">${cell}</div>`;
        });
    });
    html += '</div>';
    return html;
}
```

#### `parseMarkdownInline(text)`
Handles inline markdown within table cells:
```javascript
function parseMarkdownInline(text) {
    return text
        .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/@@(.+?)@@/g, '<em>$1</em>')
        .replace(/\\{link:(.+?)\\}(.+?)\\{\\/\\}/g, '<a href="$1" target="_blank">$2</a>')
        .replace(/`(.+?)`/g, '<code>$1</code>');
}
```

#### `oldParseMarkdownBody(lines)`
Processes non-table markdown content (moved from original parseMarkdown):
- Handles all existing markdown syntax
- Returns formatted HTML with `<br>` for line breaks

### 2. Updated Main parseMarkdown Function

Added grid table detection logic:
```javascript
function parseMarkdown(text) {
    if (!text) return '';

    const lines = text.split('\\n');
    
    // Detect table lines
    const isTableLine = (line) => {
        const trimmed = line.trim();
        return trimmed.startsWith('|') || (trimmed.includes('|') && trimmed.split('|').length >= 2);
    };
    
    const hasGrid = lines.some(l => isTableLine(l));

    if (hasGrid) {
        const blocks = [];
        let cur = [], inGrid = false;

        lines.forEach(l => {
            const isGrid = isTableLine(l);
            if (isGrid !== inGrid) {
                if (cur.length) blocks.push({ grid: inGrid, lines: cur });
                cur = [];
                inGrid = isGrid;
            }
            cur.push(l);
        });
        if (cur.length) blocks.push({ grid: inGrid, lines: cur });

        return blocks.map(b =>
            b.grid ? parseGridTable(b.lines) : oldParseMarkdownBody(b.lines)
        ).join('<br>');
    }

    return oldParseMarkdownBody(lines);
}
```

### 3. Added CSS Styles

Added complete grid table styling before `</style>` tag:
```css
/* Markdown Grid Table Styles (CSS Grid - no <table> elements) */
.md-grid {
    display: grid;
    grid-template-columns: repeat(var(--cols), auto);
    gap: 4px;
    margin: 4px 0;
    font-size: 0.85em;
    font-family: inherit;
    width: fit-content;
    max-width: 100%;
}

.md-cell {
    padding: 4px 6px;
    border: 1px solid #ced4da;
    background: #fff;
    overflow: visible;
    word-break: normal;
    white-space: nowrap;
    min-width: fit-content;
}

.md-header {
    background: #f8f9fa;
    font-weight: 600;
    white-space: nowrap;
}

.md-grid strong { font-weight: bold; }
.md-grid em { font-style: italic; }
.md-grid code { /* code styling */ }
.md-grid a { color: #007bff; text-decoration: underline; }
```

### 4. Updated hasMarkdown Detection

Added table detection to the cell rendering logic (around line 1100):
```javascript
const hasMarkdown = cellValue.includes('**') || 
    // ... other checks ...
    cellValue.trim().startsWith('|') ||
    (cellValue.includes('|') && cellValue.split('|').length >= 2);
```

## Features Supported in Export

### Table Formats
Both formats work in exported HTML:

**Traditional:**
```
| Name | Age | City |
| Anna | 22  | NYC  |
```

**Inline:**
```
Name | Age | City
Anna | 22  | NYC
```

### Inline Markdown in Tables
- **Bold**: `**text**`
- *Italic*: `@@text@@`
- Code: `` `text` ``
- Links: `{link:url}text{/}`

### All Other Markdown
- Headings, lists, colors, highlights, etc.
- All work exactly as in the main application

## Consistency with Main App

The export now matches `static/script.js` exactly:

| Feature | Main App | Export | Status |
|---------|----------|--------|--------|
| Grid Tables | ✓ | ✓ | ✅ Matching |
| Inline Format | ✓ | ✓ | ✅ Matching |
| Auto-sizing | ✓ | ✓ | ✅ Matching |
| Smaller Font | ✓ | ✓ | ✅ Matching |
| Inline Markdown | ✓ | ✓ | ✅ Matching |
| Mixed Content | ✓ | ✓ | ✅ Matching |

## Testing the Export

1. Run the export script:
   ```bash
   python export_static.py
   ```

2. Open the generated `mycell.html` file

3. Test with table content:
   ```
   Name | Age | Role
   Bob | 25 | Developer
   Jane | 30 | Designer
   ```

4. Verify:
   - Table renders with CSS Grid
   - Columns auto-size to content
   - First row is header (gray background)
   - Font is 85% of cell font
   - Table only takes needed width

## File Locations

- **Export Script**: `export_static.py`
- **Output File**: `C:\Users\nahid\ms\db\5000_myhome\mycell.html`
- **Data Source**: `C:\Users\nahid\ms\ms1\scripts\flask\5018_cell\data.json`

## Notes

- JavaScript code in export uses escaped backslashes (`\\n`, `\\|`, etc.) because it's embedded in Python string
- CSS Grid is fully supported in all modern browsers
- Export file is standalone - no external dependencies
- All markdown features work offline in exported HTML

## Maintenance

When adding new markdown syntax in the future, update these 3 locations in `export_static.py`:

1. **hasMarkdown detection** (line ~1100)
2. **parseMarkdown() function** (line ~1300)
3. **CSS styles** (line ~750)

These must match the implementation in:
- `static/script.js`
- `static/style.css`
- `templates/index.html`

## Result

Exported HTML files now have full table markdown support with the same visual appearance and functionality as the main application! 🎉
