# Pipe Table Update

## Changes Made

### 1. Clean Pipe Separator Style
- **Before**: Tables showed full grid boxes around every cell
- **After**: Tables now show only vertical pipe separators (`|`) between columns
- No horizontal lines between rows (except for headers)
- Transparent backgrounds for cleaner look

### 2. Optional Headers
- **Before**: First row was always treated as a header (bold, gray background)
- **After**: Headers are now optional!

#### How to Use Headers:
Add a separator row with dashes after your header row:

```
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |
```

This will make "Name", "Age", "City" bold with an underline.

#### Tables Without Headers:
Just skip the separator row:

```
| John | 25  | NYC  |
| Jane | 30  | LA   |
| Bob  | 35  | SF   |
```

All rows will be treated as regular data rows (no bold, no special styling).

### 3. Visual Improvements
- Increased padding (4px → 12px) for better readability
- Removed gap between cells for seamless pipe appearance
- Transparent backgrounds blend with page
- Headers get a bottom border instead of full box

## Examples

### With Header:
```
| Product | Price | Stock |
|---------|-------|-------|
| Apple   | $1.50 | 100   |
| Banana  | $0.80 | 150   |
```

Result:
- "Product", "Price", "Stock" are **bold** with underline
- Data rows are normal text
- Vertical pipes between columns

### Without Header:
```
| Apple  | $1.50 | 100 |
| Banana | $0.80 | 150 |
| Orange | $2.00 | 80  |
```

Result:
- All rows look the same
- No bold text
- Just clean data with pipe separators

### Alignment Still Works:
```
| Left | :Center: | Right: |
|------|----------|--------|
| A    | B        | C      |
```

- `:text:` = center aligned
- `text:` = right aligned
- `text` = left aligned (default)

## Files Updated
1. `static/script.js` - parseGridTable() function
2. `static/style.css` - .md-grid, .md-cell, .md-header styles
3. `export_static.py` - parseGridTable() function and CSS

## Benefits
✅ Cleaner, more minimal appearance
✅ Flexibility - use headers only when needed
✅ Better for simple data tables
✅ Maintains all existing features (alignment, resizing, wrapping)
✅ Works in both live app and static export
