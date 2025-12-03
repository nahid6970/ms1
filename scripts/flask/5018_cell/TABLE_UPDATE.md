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

### Syntax:
```
| :R:Name | :G:Age | :B:City |
|---------|--------|---------|
| John    | 25     | NYC     |
| Jane    | 30     | LA      |
```

Result:
- **Red** pipe after "Name" column
- **Green** pipe after "Age" column  
- **Blue** pipe after "City" column

### Available Colors:
- **:R:** = Red (#ff0000)
- **:G:** = Green (#00ff00)
- **:B:** = Blue (#0000ff)
- **:Y:** = Yellow (#ffff00)
- **:O:** = Orange (#ff8800)
- **:P:** = Purple (#ff00ff)
- **:C:** = Cyan (#00ffff)
- **:W:** = White (#ffffff)
- **:K:** = Black (#000000)
- **:GR:** = Gray (#808080)

### Combining Colors with Alignment:
```
| :R::Name: | :G:Age: | :B::City: |
|-----------|---------|-----------|
| John      | 25      | NYC       |
```

- `:R::text:` = Red separator + center aligned
- `:G:text:` = Green separator + right aligned
- `:B:text` = Blue separator + left aligned

### Separator Width:
- Changed from 1px to **3px** (matching Timeline feature)
- More visible and easier to distinguish colors

## Files Updated
1. `static/script.js` - parseGridTable() function with color support
2. `static/style.css` - .md-grid, .md-cell (3px border width)
3. `export_static.py` - parseGridTable() function with color support and CSS

## Benefits
✅ Cleaner, more minimal appearance
✅ Flexibility - use headers only when needed
✅ Better for simple data tables
✅ Colored separators for visual organization
✅ Thicker 3px separators (matching Timeline)
✅ Maintains all existing features (alignment, resizing, wrapping)
✅ Works in both live app and static export
