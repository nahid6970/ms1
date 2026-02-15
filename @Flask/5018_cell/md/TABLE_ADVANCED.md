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
- Adds missing leading/trailing pipes.
- Regenerates separator lines (`---`).

## Table Detection & Rows
- **Detection:** `isTableLine(line)` (checks for pipes).
- **Rowspan:** `^^` syntax merges a cell with the one above (uses `grid-row: span N`).
- **Markdown Spanning:** Markdown and custom color syntax can span multiple cells
  - Example: `==Cell1 | Cell2 | Cell3==` applies highlight to all three cells
  - Works with: `**`, `==`, `!!`, `??`, `@@`, `##`, `~~`, `<<`, `>>`, and custom syntax markers
  - Each cell gets properly closed syntax: `==Cell1== | ==Cell2== | ==Cell3==`
- **Processing:** `parseGridTable()` parses pipes, colors, alignment, and rowspan.

## Table Styling
- `.md-grid` (CSS Grid layout)
- `.md-cell` (3px right border)
- `.md-header` (Bottom border)
