# Table Markdown - Usage Guide

## Supported Formats

The table feature now supports **two formats** for creating tables:

### Format 1: Traditional (with leading/trailing pipes)
```
| Name | Age | City |
| Anna | 22  | NYC  |
| Bob  | 30  | LA   |
```

### Format 2: Inline (without leading/trailing pipes)
```
Name | Age | City
Anna | 22  | NYC
Bob  | 30  | LA
```

Both formats produce the same result!

## Features

### 1. Smaller Font Size
Tables now use **0.85em** font size (85% of the cell's font size) for better readability and to fit more data.

### 2. Flexible Syntax
- You can use pipes at the start and end: `| Name | Age |`
- Or just between columns: `Name | Age`
- Both work the same way!

### 3. First Row as Header
The first row is automatically styled as a header with:
- Gray background (#f8f9fa)
- Bold text
- Same border as other cells

### 4. Inline Markdown Support
Inside table cells, you can use:
- **Bold**: `**text**` → **text**
- *Italic*: `@@text@@` → *text*
- Code: `` `text` `` → `text`
- Links: `{link:url}text{/}` → [text](url)

## Examples

### Example 1: Simple Table
**Input:**
```
Name | Age | City
John | 25 | NYC
Jane | 30 | LA
```

**Result:** A 3-column table with header row

---

### Example 2: Table with Formatting
**Input:**
```
Feature | Status | Priority
**Login** | @@done@@ | `high`
Search | pending | `medium`
```

**Result:** Table with bold "Login", italic "done", and code-styled priorities

---

### Example 3: Table with Links
**Input:**
```
Site | Link
Google | {link:https://google.com}Visit{/}
GitHub | {link:https://github.com}Code{/}
```

**Result:** Table with clickable links

---

### Example 4: Mixed Format (both styles in same cell)
**Input:**
```
| Name | Age |
John | 25
| Jane | 30 |
```

**Result:** All rows render correctly (mixing formats is fine!)

---

### Example 5: Mixed Content (table + other markdown)
**Input:**
```
**Product List:**

Name | Price
Apple | $1.50
Banana | $0.75

Total: **$2.25**
```

**Result:** 
- Bold heading
- Table with 2 rows
- Bold total below

## Tips

1. **Minimum 2 columns**: You need at least one pipe (`|`) to create a table
2. **Consistent columns**: All rows should have the same number of columns
3. **Empty cells**: Just leave the space empty: `Name | | Age` (middle cell is empty)
4. **Spacing**: Spaces around pipes are optional: `Name|Age` works the same as `Name | Age`

## Visual Styling

- **Font size**: 85% of cell font (smaller than regular text)
- **Cell padding**: 4px vertical, 6px horizontal
- **Border**: 1px solid #ced4da (light gray)
- **Gap**: 4px between cells
- **Header background**: #f8f9fa (light gray)
- **Cell background**: White

## Browser Compatibility

Uses CSS Grid, supported in:
- Chrome 57+
- Firefox 52+
- Safari 10.1+
- Edge 16+

## Performance

- Lightweight CSS Grid layout
- No HTML table elements
- Fast rendering
- Smooth scrolling

Enjoy your tables! 🎉
