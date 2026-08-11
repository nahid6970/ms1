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

## New Feature: Colored Column Separators

You can now color the pipe separators between columns using color codes!

### Syntax Option 1: Column-Wide Colors (Recommended)
Use `-A` suffix to apply color to entire column - only specify once in header!

```
| :R-A:Name | :G-A:Age | :B-A:City |
|-----------|----------|-----------|
| John      | 25       | NYC       |
| Jane      | 30       | LA        |
| Bob       | 35       | SF        |
```

Result:
- **Red** pipe after entire "Name" column (all rows)
- **Green** pipe after entire "Age" column (all rows)
- **Blue** pipe after entire "City" column (all rows)

### Syntax Option 2: Per-Cell Colors
Apply color to individual cells only:

```
| :R:Name | :G:Age | :B:City |
|---------|--------|---------|
| John    | 25     | NYC     |
| Jane    | 30     | LA      |
```

Result:
- Colors only apply to header row
- Other rows use default gray

### Available Colors:
- **:R:** or **:R-A:** = Red (#ff0000)
- **:G:** or **:G-A:** = Green (#00ff00)
- **:B:** or **:B-A:** = Blue (#0000ff)
- **:Y:** or **:Y-A:** = Yellow (#ffff00)
- **:O:** or **:O-A:** = Orange (#ff8800)
- **:P:** or **:P-A:** = Purple (#ff00ff)
- **:C:** or **:C-A:** = Cyan (#00ffff)
- **:W:** or **:W-A:** = White (#ffffff)
- **:K:** or **:K-A:** = Black (#000000)
- **:GR:** or **:GR-A:** = Gray (#808080)

### Combining Colors with Alignment:
```
| :R-A::Name: | :G-A:Age: | :B-A::City: |
|-------------|-----------|-------------|
| John        | 25        | NYC         |
```

- `:R-A::text:` = Red separator (all rows) + center aligned
- `:G-A:text:` = Green separator (all rows) + right aligned
- `:B-A:text` = Blue separator (all rows) + left aligned

### Separator Width:
- Changed from 1px to **3px** (matching Timeline feature)
- More visible and easier to distinguish colors

## Files Updated
1. `static/script.js` - parseGridTable() function with color support
2. `static/style.css` - .md-grid, .md-cell (3px border width)
3. `export_static.py` - parseGridTable() function with color support and CSS

## New Feature: Table Formatter (F3)

Automatically format and align your pipe tables with one click!

### Usage:
1. Select your messy table text
2. Press **F3** (Quick Formatter)
3. Click the **📊 Format Table** button

### Example:

**Before (messy):**
```
:R-A:Name | :G:Age | :B-A:City
---------|--------|--------
John | 25     | NYC
Jane       | 30     | LA
```

**After (formatted):**
```
| :R-A:Name | :G:Age | :B-A:City |
|-----------|--------|-----------|
| John      | 25     | NYC       |
| Jane      | 30     | LA        |
```

### What it does:
✅ Aligns all pipes vertically
✅ Calculates optimal column width based on **content only**
✅ Ignores separator rows when calculating width (prevents overly wide columns)
✅ Regenerates separator rows to match content width
✅ Pads cells with spaces to match column width
✅ Preserves color codes and alignment markers
✅ Adds leading/trailing pipes if missing

### Smart Width Calculation:

The formatter is smart about column widths:
- **Ignores separator rows** (lines with only dashes) when calculating width
- Only uses actual content (headers and data) to determine optimal width
- Then regenerates separator rows to match

**Example:**
```
Before:
| Name | Age              | City |
| ---- | ---------------- | ---- |
| John | 25               | NYC  |

After:
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
```

The "Age" column is sized for "Age" and "25", not the long separator row!

## Benefits
✅ Cleaner, more minimal appearance
✅ Flexibility - use headers only when needed
✅ Better for simple data tables
✅ Colored separators for visual organization
✅ Thicker 3px separators (matching Timeline)
✅ **Auto-formatting** with F3 → 📊 button
✅ Maintains all existing features (alignment, resizing, wrapping)
✅ Works in both live app and static export
