# Pipe Table Color Test

## Test 1: Basic Colored Separators
```
| :R:Name | :G:Age | :B:City |
|---------|--------|---------|
| John    | 25     | NYC     |
| Jane    | 30     | LA      |
| Bob     | 35     | SF      |
```

Expected:
- Red pipe after "Name"
- Green pipe after "Age"
- Blue pipe after "City"
- All headers bold with underline

## Test 2: Without Headers (Just Data)
```
| :Y:Apple  | :O:$1.50 | :P:100 |
| :Y:Banana | :O:$0.80 | :P:150 |
| :Y:Orange | :O:$2.00 | :P:80  |
```

Expected:
- Yellow pipes after first column
- Orange pipes after second column
- Purple pipes after third column
- No bold headers (no separator row)

## Test 3: Mixed Colors with Alignment
```
| :R::Product: | :G:Price: | :B::Stock: |
|--------------|-----------|------------|
| Apple        | $1.50     | 100        |
| Banana       | $0.80     | 150        |
```

Expected:
- Red pipe + center aligned "Product"
- Green pipe + right aligned "Price"
- Blue pipe + center aligned "Stock"

## Test 4: All Available Colors
```
| :R:Red | :G:Green | :B:Blue | :Y:Yellow | :O:Orange |
|--------|----------|---------|-----------|-----------|
| A      | B        | C       | D         | E         |
```

```
| :P:Purple | :C:Cyan | :W:White | :K:Black | :GR:Gray |
|-----------|---------|----------|----------|----------|
| F         | G       | H        | I        | J        |
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

### Alignment Codes:
- `:text:` = Center aligned
- `text:` = Right aligned
- `text` = Left aligned (default)

### Combining:
- `:R::text:` = Red separator + center aligned
- `:G:text:` = Green separator + right aligned
- `:B:text` = Blue separator + left aligned

## Implementation Notes

✅ Color code must be at the start: `:R:Name`
✅ Alignment can follow color: `:R::Name:` (red + center)
✅ Works with or without headers
✅ 3px separator width (matching Timeline)
✅ Transparent backgrounds
✅ Full support in static export
