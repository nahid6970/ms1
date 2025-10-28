# Table Markdown - Test Examples

## Test Case 1: Simple Table
**Input:**
```
| Name | Age | City |
| John | 25 | NYC |
| Jane | 30 | LA |
```

**Expected:** A 3-column table with header row and 2 data rows

---

## Test Case 2: Table with Inline Markdown
**Input:**
```
| Feature | Status | Priority |
| **Login** | @@done@@ | `high` |
| Search | pending | `medium` |
```

**Expected:** Table with bold "Login", italic "done", and code-styled priorities

---

## Test Case 3: Table with Links
**Input:**
```
| Site | Link |
| Google | {link:https://google.com}Visit{/} |
| GitHub | {link:https://github.com}Code{/} |
```

**Expected:** Table with clickable links in the second column

---

## Test Case 4: Mixed Content (Table + Other Markdown)
**Cell A1:**
```
| Product | Price |
| Apple | $1.50 |
```

**Cell B1:**
```
**Bold text**
@@Italic text@@
- Bullet point
```

**Expected:** 
- Cell A1 shows a table
- Cell B1 shows bold text, italic text, and a bullet point
- Both cells render their markdown independently

---

## Test Case 5: Table with Empty Cells
**Input:**
```
| Name | Email | Phone |
| John | john@example.com | |
| Jane | | 555-1234 |
```

**Expected:** Table with some empty cells (blank but still bordered)

---

## Test Case 6: Single Row Table (Header Only)
**Input:**
```
| Column 1 | Column 2 | Column 3 |
```

**Expected:** A single-row table with header styling

---

## Test Case 7: Table with Special Characters
**Input:**
```
| Symbol | Meaning |
| & | Ampersand |
| < | Less than |
| > | Greater than |
```

**Expected:** Table displaying special characters correctly

---

## Test Case 8: Non-Table Content (Should Not Break)
**Cell A1:**
```
This is just regular text with a pipe | character in the middle
```

**Expected:** Regular text with a pipe character (not rendered as table because line doesn't START with |)

---

## Test Case 9: Multiple Tables in One Cell
**Input:**
```
| Table 1 | Data |
| A | 1 |

Some text between tables

| Table 2 | Data |
| B | 2 |
```

**Expected:** Two separate tables with text in between

---

## Test Case 10: Table After Other Markdown
**Input:**
```
**Important Data:**

| Name | Value |
| Speed | 100 |
| Power | 200 |
```

**Expected:** Bold heading followed by a table

---

## Verification Checklist

✅ Tables render correctly with borders
✅ First row is styled as header (bold, different background)
✅ Inline markdown works inside table cells
✅ Tables don't interfere with other cells
✅ Mixed content (table + markdown) works in same cell
✅ Empty cells render properly
✅ Special characters display correctly
✅ Font size scaling applies to tables
✅ Tables work in wrap mode
✅ Search functionality works with table content
