# Find & Replace Syntax Feature

**Location:** F3 Quick Formatter → 🔄 Button

Replace syntax patterns across an entire cell with a different syntax pattern while preserving the content.

---

## Overview

The Find & Replace Syntax feature allows you to convert one markdown/formatting syntax to another throughout an entire cell. This is useful when you want to change the styling of multiple text segments at once.

**Example Use Case:**
- Convert all red colored text `{fg:#ff0000}text{/}` to black highlight `==text==`
- Change all bold text `**text**` to italic `@@text@@`
- Replace custom syntax markers with standard ones

---

## How to Use

1. **Select any text** in a cell and press **F3** to open Quick Formatter
2. Click the **🔄 Find & Replace Syntax** button
3. **Select or type** the syntax pattern to find
4. **Click a button or type** the replacement syntax
5. **Preview** the changes before applying
6. Click **Replace All** to apply changes

---

## Interface Components

### Find Syntax Section

**Dropdown Menu:**
- Automatically scans the entire cell content
- Lists all detected syntax patterns with:
  - Syntax name (e.g., "Bold", "Color: fg:#ff0000")
  - Occurrence count (e.g., "3x")
  - Example preview of first match
- Click to auto-fill the find pattern

**Manual Input:**
- Type custom patterns if not in dropdown
- Use `text` as placeholder for content
- Example: `{fg:#ff0000}**text**{/}`

### Replace With Section

**Quick Buttons:**
- **Black** - `==text==` (black highlight)
- **Red** - `!!text!!` (red highlight)
- **Blue** - `??text??` (blue highlight)
- **Bold** - `**text**`
- **Italic** - `@@text@@`
- **Underline** - `__text__`
- **Custom Syntaxes** - Your manually added syntax markers

**Manual Input:**
- Type custom replacement patterns
- Use `text` as placeholder for content
- Example: `==text==`

### Live Preview

Shows:
- Number of occurrences found
- Before/after example of first match
- Updates as you type

---

## Detected Syntax Types

The feature automatically detects:

### Standard Syntaxes
- Bold (`**text**`)
- Italic (`@@text@@`)
- Underline (`__text__`)
- Strikethrough (`~~text~~`)
- Heading (`##text##`)
- Small text (`..text..`)
- Wavy underline (`_.text._`)
- Code (`` `text` ``)

### Highlights
- Black highlight (`==text==`)
- Red highlight (`!!text!!`)
- Blue highlight (`??text??`)

### Advanced Syntaxes
- Custom colors - Grouped by exact color values
  - `{fg:#ff0000}text{/}` detected separately from
  - `{fg:#ffffff;bg:#000000}text{/}`
- Border boxes (`#R#text#/#`)
- Font sizes (`#2#text#/#`)
- Title text (`:::text:::`)

### Custom Syntaxes
- All user-defined syntax markers
- Displayed as "Custom: marker"
- Example: `%%text%%`, `$$text$$`

---

## Examples

### Example 1: Color to Highlight
**Find:** `{fg:#ff0000}text{/}`  
**Replace:** `==text==`  
**Result:** All red colored text becomes black highlighted text

### Example 2: Bold to Italic
**Find:** `**text**`  
**Replace:** `@@text@@`  
**Result:** All bold text becomes italic text

### Example 3: Custom Syntax to Standard
**Find:** `%%text%%`  
**Replace:** `!!text!!`  
**Result:** All custom %% markers become red highlights

### Example 4: Nested Syntax
**Find:** `{fg:#ff0000}**text**{/}`  
**Replace:** `==text==`  
**Result:** Red colored bold text becomes black highlight (removes both syntaxes)

---

## Important Notes

1. **Whole Cell Scope:** Operates on entire cell content, not just selection
2. **Pattern Matching:** Uses `text` as placeholder - must be present in both find and replace patterns
3. **Case Sensitive:** Exact pattern matching
4. **Preserves Content:** Only syntax markers are changed, content remains intact
5. **No Undo:** Changes are applied immediately - use with caution
6. **Regex-based:** Special characters in patterns are escaped automatically

---

## Tips

- **Preview First:** Always check the preview before clicking Replace All
- **Specific Colors:** Different color values are detected separately
- **Custom Syntaxes:** Your custom markers appear automatically in both dropdown and buttons
- **Complex Patterns:** For nested syntaxes, the entire pattern must match exactly
- **Test Small:** Try on a test cell first if unsure about the pattern

---

## Related Features

- **F3 Quick Formatter:** Main formatting interface
- **🔧 Syntax Inspector:** Reorder nested syntaxes
- **🎯 Select All Matching:** Multi-cursor editing for occurrences
- **Custom Syntax Manager:** Add/edit custom syntax markers
