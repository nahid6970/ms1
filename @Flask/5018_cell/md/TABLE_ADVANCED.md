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
- `.md-grid` — CSS Grid layout, **2px top+bottom outer border**
- `.md-cell` — 3px right border, **`md-first-col` class adds 3px left border** on first column
- `.md-header` — Bold first row (bottom border 2px)
- `.md-ruled` — Ruled table class: adds 1px `border-bottom` to every row

## Ruled Table Syntax
Use `━` (U+2501) as the separator row instead of `-` to enable row separators:
```
| Name | Year | Author |
|━━━|━━━|━━━|
| Foo  | 1821 | Bar    |
| Baz  | 1822 | Qux    |
```
- First row gets bold header style (same as `---`)
- Every data row gets a 1px bottom border separator
- Table gets 2px top/bottom outer borders + 3px left border

## Rowspan Border Fix
- `^^` rowspan cells use `md-rowspan-row` (border-bottom only) + `md-rowspan-top` (border-top on first row of each span block) to avoid doubled/bolder borders between adjacent rowspan rows.
