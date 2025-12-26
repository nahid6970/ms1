# Advanced Table Features

## Table Syntax Enhancements
- **Flexible Placement:** Tables can be placed anywhere in a cell.
- **Explicit Termination:** `Table*end` closes a table.
- **Multiple Tables:** Recursive handling of multiple tables in one cell.

## Pipe Table Formatter (F3 → 📊)
**Function:** `formatPipeTable()`
**Actions:**
- Aligns pipes vertically (`|`).
- Calculates optimal column widths (ignoring separator rows).
- **Unicode Support:** Uses grapheme cluster counting (`Intl.Segmenter`) to accurately align Bangla, English, and mixed-script text.
- Adds missing leading/trailing pipes.
- Regenerates separator lines (`---`).

## Table Detection & Rows
- **Detection:** `isTableLine(line)` (checks for pipes).
- **Rowspan:** `^^` syntax merges a cell with the one above (uses `grid-row: span N`).
- **Processing:** `parseGridTable()` parses pipes, colors, alignment, and rowspan.

## Table Styling
- `.md-grid` (CSS Grid layout)
- `.md-cell` (3px right border)
- `.md-header` (Bottom border)
