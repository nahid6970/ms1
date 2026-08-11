# Cell Justify Alignment Feature

## Overview
The Justify Alignment feature allows users to apply justified text alignment to cells, similar to Microsoft Word's justify option. This distributes text evenly across the cell width, creating clean edges on both left and right sides.

## How to Use

### Via Context Menu
1. **Right-click** on a cell to open the context menu
2. Select **"Justify Align"** from the menu
3. A checkmark (✓) will appear next to the option when active
4. Click again to toggle off

### Multiple Cell Selection
- Select multiple cells using Ctrl+Click or Shift+Click
- Right-click and choose "Justify Align"
- The alignment will be applied to all selected cells
- A toast notification will confirm: "Justify align applied for X cells"

## Behavior

### Mutual Exclusivity with Center Align
- **Justify** and **Center** alignment are mutually exclusive
- Enabling Justify will automatically disable Center alignment
- Enabling Center will automatically disable Justify alignment
- This ensures clean, predictable text alignment

### Visual Effect
- Text is distributed evenly across the cell width
- Creates straight edges on both left and right sides
- Particularly useful for:
  - Multi-line text content
  - Paragraphs in cells
  - Professional document formatting
  - Creating clean, newspaper-style layouts

## Implementation Details

### Storage
- Stored in `cellStyles` object with key `"row-col"`
- Property: `justify: true/false`
- Persisted in `data.json`

### Context Menu Indicator
- Element ID: `ctxJustify`
- Shows checkmark (✓) when active
- Updates dynamically when cells are selected

### Function
- **Function**: `toggleCellJustify()`
- **Location**: `static/script.js`
- **Behavior**:
  - Toggles justify state for selected cell(s)
  - Clears center alignment if setting justify
  - Updates visual indicators
  - Shows success toast for multiple cells

## CSS Styling
```css
/* Applied to cell content when justify is enabled */
.cell-content {
    text-align: justify;
}
```

## Export Support
- ✅ Fully supported in static HTML exports
- ✅ Rendered correctly in `export_static.py`
- ✅ Maintains alignment in exported files

## Related Features
- **Center Align**: Mutually exclusive alternative alignment
- **Bold/Italic**: Can be combined with justify alignment
- **Text Color**: Works alongside justify alignment
- **Background Color**: Compatible with justify alignment

## Use Cases

### Professional Documents
```
Long paragraphs of text that need to look
polished and professional with clean edges
on both sides, similar to newspaper columns
or formal reports.
```

### Multi-line Descriptions
- Product descriptions
- Meeting notes
- Documentation cells
- Report summaries

### Layout Consistency
- Creating uniform visual appearance
- Matching traditional document formatting
- Professional presentations

## Keyboard Shortcuts
- No dedicated keyboard shortcut (context menu only)
- Can be applied to multiple cells at once

## Technical Notes

### Rule of 6 Compliance
When this feature was added, it followed the "Rule of 6" for cell formatting:
1. ✅ **Parsing Logic**: Not applicable (CSS-only feature)
2. ✅ **Detection**: Not applicable (CSS-only feature)
3. ✅ **Stripping**: Not applicable (CSS-only feature)
4. ✅ **Static Detection**: Applied in `export_static.py` rendering
5. ✅ **Static Parsing**: Applied in `export_static.py` rendering
6. ✅ **User Guide**: Documented in this file

### Code Locations
- **Main App**: `static/script.js` - `toggleCellJustify()` function (line ~3588)
- **Context Menu**: `templates/index.html` - `ctxJustify` element
- **Rendering**: `static/script.js` - `renderTable()` function (line ~7298)
- **Export**: `export_static.py` - `renderTable()` function (line ~1700)

## Compatibility
- ✅ Works with all markdown formatting
- ✅ Compatible with text wrapping
- ✅ Supports multi-line content
- ✅ Works in merged cells
- ✅ Exports correctly to static HTML
- ✅ Mobile responsive

## Known Limitations
- Single-line text may not show visible justification effect
- Very short text won't be justified (browser behavior)
- Best results with multi-line content

## Version History
- **2026-01-20**: Feature implemented with context menu support
- **2026-01-20**: Export support added to `export_static.py`
- **2026-01-20**: Documentation created
