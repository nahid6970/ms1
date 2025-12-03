# Pipe Table Color Test

## Test 1: Column-Wide Colors (Recommended)
```
| :R-A:Name | :G-A:Age | :B-A:City |
|-----------|----------|-----------|
| John      | 25       | NYC       |
| Jane      | 30       | LA        |
| Bob       | 35       | SF        |
```

Expected:
- Red pipe after "Name" column (ALL rows)
- Green pipe after "Age" column (ALL rows)
- Blue pipe after "City" column (ALL rows)
- All headers bold with underline

## Test 1b: Per-Cell Colors (Old Method)
```
| :R:Name | :G:Age | :B:City |
|---------|--------|---------|
| John    | 25     | NYC     |
| Jane    | 30     | LA      |
| Bob     | 35     | SF      |
```

Expected:
- Red pipe after "Name" (header row only)
- Green pipe after "Age" (header row only)
- Blue pipe after "City" (header row only)
- Data rows use default gray pipes

## Test 2: Without Headers (Column-Wide Colors)
```
| :Y-A:Apple  | :O-A:$1.50 | :P-A:100 |
| Banana      | $0.80      | 150      |
| Orange      | $2.00      | 80       |
```

Expected:
- Yellow pipes after first column (ALL rows)
- Orange pipes after second column (ALL rows)
- Purple pipes after third column (ALL rows)
- No bold headers (no separator row)
- Only first row needs color codes!

## Test 3: Mixed Colors with Alignment (Column-Wide)
```
| :R-A::Product: | :G-A:Price: | :B-A::Stock: |
|----------------|-------------|--------------|
| Apple          | $1.50       | 100          |
| Banana         | $0.80       | 150          |
```

Expected:
- Red pipe + center aligned "Product" (ALL rows)
- Green pipe + right aligned "Price" (ALL rows)
- Blue pipe + center aligned "Stock" (ALL rows)

## Test 4: All Available Colors (Column-Wide)
```
| :R-A:Red | :G-A:Green | :B-A:Blue | :Y-A:Yellow | :O-A:Orange |
|----------|------------|-----------|-------------|-------------|
| A        | B          | C         | D           | E           |
| A2       | B2         | C2        | D2          | E2          |
```

```
| :P-A:Purple | :C-A:Cyan | :W-A:White | :K-A:Black | :GR-A:Gray |
|-------------|-----------|------------|------------|------------|
| F           | G         | H          | I          | J          |
| F2          | G2        | H2         | I2         | J2         |
```

## Test 5: Default Gray (No Color Code)
```
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
```

Expected:
- Default gray pipes (no color codes used)

## Color Reference

### Color Codes:

**Column-Wide (Recommended - use `-A` suffix):**
- **:R-A:** = Red for entire column
- **:G-A:** = Green for entire column
- **:B-A:** = Blue for entire column
- **:Y-A:** = Yellow for entire column
- **:O-A:** = Orange for entire column
- **:P-A:** = Purple for entire column
- **:C-A:** = Cyan for entire column
- **:W-A:** = White for entire column
- **:K-A:** = Black for entire column
- **:GR-A:** = Gray for entire column

**Per-Cell (without `-A`):**
- **:R:** = Red for single cell only
- **:G:** = Green for single cell only
- (etc.)

### Alignment Codes:
- `:text:` = Center aligned
- `text:` = Right aligned
- `text` = Left aligned (default)

### Combining:
- `:R-A::text:` = Red separator (all rows) + center aligned
- `:G-A:text:` = Green separator (all rows) + right aligned
- `:B-A:text` = Blue separator (all rows) + left aligned

## Implementation Notes

✅ **Column-Wide Colors:** Use `:R-A:` in first row to apply to entire column
✅ **Per-Cell Colors:** Use `:R:` to apply to single cell only
✅ Color code must be at the start: `:R-A:Name` or `:R:Name`
✅ Alignment can follow color: `:R-A::Name:` (red column + center)
✅ Works with or without headers
✅ 3px separator width (matching Timeline)
✅ Transparent backgrounds
✅ Full support in static export

## Benefits of `-A` Syntax

✅ **Less typing** - Only specify color once in first row
✅ **Cleaner markup** - Data rows don't need color codes
✅ **Easier to maintain** - Change color in one place
✅ **More readable** - Less clutter in table cells
