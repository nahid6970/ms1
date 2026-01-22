# Table Rowspan Feature

The `^^` syntax allows cells to span multiple rows in both comma tables and pipe tables.

## Syntax

Use `^^` in a cell to merge it with the cell directly above it.

## Examples

### Example 1: Pipe Table with Rowspan

```
|Header1|Header2|Header3|Header4|
|---|---|---|---|
|Row1Col1|Row1Col2|Row1Col3|Row1Col4|
|Row2Col1|Row2Col2|^^|^^|
```

**Result:** Columns 3 and 4 of Row1 will span both Row1 and Row2.

### Example 2: Comma Table with Rowspan

```
Table*4
Header1, Header2, Header3, Header4,
Row1Col1, Row1Col2, Row1Col3, Row1Col4,
Row2Col1, Row2Col2, ^^, ^^
```

**Result:** Same as above - columns 3 and 4 span two rows.

### Example 3: Multiple Rowspans

```
|Name|Age|City|Country|
|---|---|---|---|
|Alice|25|NYC|USA|
|Bob|30|^^|^^|
|Charlie|35|^^|^^|
```

**Result:** The "NYC" and "USA" cells span three rows (Alice, Bob, and Charlie).

### Example 4: Mixed Rowspans

```
|Col1|Col2|Col3|
|---|---|---|
|A1|B1|C1|
|A2|^^|C2|
|A3|B3|^^|
```

**Result:** 
- B1 spans rows 1-2
- C2 spans rows 2-3

## Visual Styling

Rows that contain rowspan cells have thin black borders above and below **all cells in those rows**:
- **Top border**: 1px solid black line above all cells in the row group
- **Bottom border**: 1px solid black line below all cells in the row group
- This creates a visual box around the entire merged row section
- Makes it easy to see which rows are grouped together

Example: If columns 3-4 span rows 1-3, then **all cells** in rows 1-3 (including columns 1-2) will have the black borders.

## Rules

1. `^^` must have a cell directly above it to merge with
2. You can chain multiple `^^` cells vertically to span more than 2 rows
3. When chaining `^^`, the algorithm finds the first non-`^^` cell above and extends its span
4. Works with all table features: colors, alignment, borders
5. The content of `^^` cells is ignored (they're hidden)
6. Spanning cells get black top/bottom borders for visual clarity

## How Chaining Works

When you have multiple `^^` in the same column:
```
|Col1|Col2|
|---|---|
|A1|B1|
|A2|^^|
|A3|^^|
```

The algorithm:
- Row 2 `^^` → finds B1 (first non-`^^` above) → B1 rowspan = 2
- Row 3 `^^` → finds B1 (skips Row 2's `^^`) → B1 rowspan = 3

Result: B1 spans all 3 rows!

## The Rule of 6

This feature follows "The Rule of 6" for markdown syntax:
- **Simple**: Just type `^^` to merge cells
- **Intuitive**: The `^^` symbol visually suggests "pointing up"
- **Consistent**: Works the same in both comma and pipe tables
- **Minimal**: Only 2 characters needed
- **Readable**: Easy to see merged cells in source
- **Powerful**: Enables complex table layouts
