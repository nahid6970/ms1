# Pipe Table Formatter Test Cases

## Test 1: Basic Messy Table
**Before:**
```
:R-A:Name | :G:Age | :B-A:City
---------|--------|--------
John | 25     | NYC
Jane       | 30     | LA
```

**After (Expected):**
```
| :R-A:Name | :G:Age | :B-A:City |
|-----------|--------|-----------|
| John      | 25     | NYC       |
| Jane      | 30     | LA        |
```

## Test 2: Overly Long Separator Rows
**Before:**
```
| Name | Age              | City |
| ---- | ---------------- | ---- |
| John | 25               | NYC  |
| Jane | 30               | LA   |
```

**After (Expected):**
```
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |
```

**Note:** Age column sized for content ("Age", "25", "30"), not the long separator!

## Test 3: Missing Leading/Trailing Pipes
**Before:**
```
Name | Age | City
-----|-----|-----
John | 25  | NYC
Jane | 30  | LA
```

**After (Expected):**
```
| Name | Age | City |
|------|-----|------|
| John | 25  | NYC  |
| Jane | 30  | LA   |
```

## Test 4: Uneven Column Widths
**Before:**
```
| Product | Price | Stock |
|---|---|---|
| Apple | $1.50 | 100 |
| Banana | $0.80 | 150 |
| Orange | $2.00 | 80 |
```

**After (Expected):**
```
| Product | Price | Stock |
|---------|-------|-------|
| Apple   | $1.50 | 100   |
| Banana  | $0.80 | 150   |
| Orange  | $2.00 | 80    |
```

## Test 5: With Color Codes and Alignment
**Before:**
```
:R-A::Name: | :G-A:Age: | :B-A::City:
---|---|---
John | 25 | NYC
Jane | 30 | LA
```

**After (Expected):**
```
| :R-A::Name: | :G-A:Age: | :B-A::City: |
|-------------|-----------|-------------|
| John        | 25        | NYC         |
| Jane        | 30        | LA          |
```

## Test 6: Table Without Headers
**Before:**
```
:Y-A:Apple | :O-A:$1.50 | :P-A:100
Banana | $0.80 | 150
Orange | $2.00 | 80
```

**After (Expected):**
```
| :Y-A:Apple | :O-A:$1.50 | :P-A:100 |
| Banana     | $0.80      | 150      |
| Orange     | $2.00      | 80       |
```

**Note:** No separator row, all rows treated as data.

## Test 7: Wide Content in Data Rows
**Before:**
```
| Name | Description | Price |
|---|---|---|
| Product A | Very long description here | $10 |
| B | Short | $5 |
```

**After (Expected):**
```
| Name      | Description                | Price |
|-----------|----------------------------|-------|
| Product A | Very long description here | $10   |
| B         | Short                      | $5    |
```

**Note:** Column width based on longest content, not separator.

## Test 8: Bangla/Unicode Text Support
**Before:**
```
| নাম | বয়স | শহর |
|---|---|---|
| রহিম | ২৫ | ঢাকা |
| করিম | ৩০ | চট্টগ্রাম |
| English | Mixed | Text |
```

**After (Expected):**
```
| নাম     | বয়স | শহর      |
|---------|------|----------|
| রহিম    | ২৫   | ঢাকা     |
| করিম    | ৩০   | চট্টগ্রাম |
| English | Mixed | Text     |
```

**Note:** Unicode characters (Bangla) are properly measured for visual width, ensuring correct alignment with mixed English/Bangla content.

## How to Test:

1. Copy the "Before" text
2. Paste into a cell
3. Select all the table text
4. Press **F3**
5. Click **📊 Format Table**
6. Verify output matches "After (Expected)"

## Key Features to Verify:

✅ Pipes align vertically
✅ Cells padded to match column width
✅ Separator rows regenerated (not used for width calculation)
✅ Color codes preserved (`:R-A:`, `:G:`, etc.)
✅ Alignment markers preserved (`:text:`, `text:`)
✅ Leading/trailing pipes added if missing
✅ Works with any number of columns
✅ Optimal width based on content only
✅ **Unicode/Bangla text properly aligned** (visual width calculation)
