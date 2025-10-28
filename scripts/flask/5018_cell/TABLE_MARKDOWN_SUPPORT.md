# Table Markdown Support - Complete Reference

## Overview
All markdown syntax (except lists) now works inside table cells!

## Supported Markdown in Tables

### Text Formatting

| Syntax | Example | Result |
|--------|---------|--------|
| Bold | `**text**` | **text** |
| Italic | `@@text@@` | *text* |
| Underline | `__text__` | <u>text</u> |
| Strikethrough | `~~text~~` | ~~text~~ |
| Superscript | `^text^` | text^sup^ |
| Subscript | `~text~` | text~sub~ |
| Code | `` `text` `` | `text` |
| Highlight | `==text==` | ==text== |
| Heading | `##text##` | **TEXT** (larger) |

### Colors

| Syntax | Example | Result |
|--------|---------|--------|
| Text Color | `{fg:red}text{/}` | <span style="color:red">text</span> |
| Background | `{bg:yellow}text{/}` | <span style="background:yellow">text</span> |
| Both | `{fg:white;bg:blue}text{/}` | <span style="color:white;background:blue">text</span> |

### Links

| Syntax | Example | Result |
|--------|---------|--------|
| Link | `{link:https://google.com}Google{/}` | [Google](https://google.com) |

## Complete Examples

### Example 1: Product Table with Formatting
```
Product | Price | Status | Notes
**iPhone** | $999 | {fg:green}In Stock{/} | @@New model@@
iPad | $599 | {fg:red}Sold Out{/} | `Restock soon`
MacBook | $1299 | {fg:green}In Stock{/} | ==Best seller==
```

**Result:**
- "iPhone" is bold
- Prices are normal text
- "In Stock" is green, "Sold Out" is red
- "New model" is italic
- "Restock soon" is code-styled
- "Best seller" is highlighted

### Example 2: Chemical Formulas
```
Compound | Formula | State
Water | H~2~O | Liquid
Carbon Dioxide | CO~2~ | Gas
Sulfuric Acid | H~2~SO~4~ | Liquid
```

**Result:**
- Numbers are subscripted (H₂O, CO₂, H₂SO₄)

### Example 3: Math Expressions
```
Expression | Result
x^2^ + y^2^ | Pythagorean
E = mc^2^ | Einstein
a^n^ + b^n^ | Fermat
```

**Result:**
- Exponents are superscripted (x², mc², aⁿ)

### Example 4: Documentation Table
```
Function | Description | Status
`getData()` | Fetches data | {fg:green}**Active**{/}
`setData()` | Updates data | {fg:orange}**Deprecated**{/}
`deleteData()` | Removes data | {fg:red}~~Removed~~{/}
```

**Result:**
- Function names are code-styled
- Status has colors AND formatting (bold/strikethrough)

### Example 5: Links Table
```
Site | Link
Google | {link:https://google.com}Visit{/}
GitHub | {link:https://github.com}Code{/}
Stack Overflow | {link:https://stackoverflow.com}Help{/}
```

**Result:**
- All links are clickable

### Example 6: Mixed Formatting
```
Item | Details
Name | **John** __Doe__
Age | 25 years
Email | `john@example.com`
Status | {fg:white;bg:green}**ACTIVE**{/}
Notes | @@Important@@ ==Priority==
```

**Result:**
- Multiple formatting types in single cell
- Bold + underline for name
- Code for email
- Colored background with bold text
- Italic + highlight for notes

## What Doesn't Work in Tables

### Lists (Not Supported in Cells)
```
❌ - Bullet point
❌ -- Sub-bullet
❌ 1. Numbered item
```

**Reason:** Lists need multiple lines and special formatting that doesn't work well in table cells.

**Workaround:** Use separate rows or create the list outside the table.

### Code Blocks (Not Supported in Cells)
```
❌ ```
   code block
   ```
```

**Reason:** Multi-line code blocks don't fit table cell structure.

**Workaround:** Use inline code (`` `code` ``) or put code blocks outside the table.

## Combining Markdown

You can combine multiple markdown types in a single cell:

```
Name | Description
**Bold** @@Italic@@ | {fg:red}Red{/} ==Highlight==
__Underline__ `Code` | ~~Strike~~ ^Super^
```

**All combinations work!**

## Tips

1. **Order matters**: Apply formatting in the right order
   - ✅ `**{fg:red}text{/}**` → Bold red text
   - ✅ `{fg:red}**text**{/}` → Red bold text

2. **Nesting**: Some markdown can be nested
   - ✅ `**@@text@@**` → Bold italic
   - ✅ `{fg:red}**text**{/}` → Red bold

3. **Spacing**: Spaces around markdown don't matter
   - ✅ `**text**` same as `** text **`

4. **Escaping**: If you need literal `**` or `@@`, currently not supported
   - Workaround: Use different symbols or Unicode

## Browser Rendering

All markdown in tables renders using:
- CSS Grid for table layout
- Inline HTML for formatting
- Standard CSS for styling

Works in all modern browsers:
- Chrome 57+
- Firefox 52+
- Safari 10.1+
- Edge 16+

## Performance

- Fast rendering (no complex parsing)
- Lightweight (no external libraries)
- Efficient (CSS-based styling)

## Testing Your Tables

Try this comprehensive test:

```
Feature | Example | Status
**Bold** | **Important** | {fg:green}✓{/}
@@Italic@@ | @@Emphasis@@ | {fg:green}✓{/}
__Underline__ | __Highlight__ | {fg:green}✓{/}
~~Strike~~ | ~~Removed~~ | {fg:green}✓{/}
`Code` | `function()` | {fg:green}✓{/}
==Mark== | ==Important== | {fg:green}✓{/}
^Super^ | x^2^ | {fg:green}✓{/}
~Sub~ | H~2~O | {fg:green}✓{/}
##Head## | ##Title## | {fg:green}✓{/}
{fg:red}Color{/} | {fg:blue}Text{/} | {fg:green}✓{/}
{link:url}Link{/} | {link:https://google.com}Google{/} | {fg:green}✓{/}
```

All should render with proper formatting! ✨
