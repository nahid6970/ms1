# Click-to-Edit Cursor Positioning

## Overview

When users click on a markdown preview cell to enter edit mode, the cursor should appear at the exact position where they clicked. This is challenging because the preview shows rendered text (without markdown syntax), but the edit mode shows raw text (with syntax like `**bold**`, `@@italic@@`, etc.).

## The Challenge

**Example:**
- Raw input: `**ctrl-check+shift+d** ABCD`
- Rendered preview: `ctrl-check+shift+d ABCD` (bold formatting applied, syntax hidden)
- User clicks between "AB|CD"
- Visible offset: 21 (position in rendered text)
- Raw offset: 23 (position in raw text, accounting for `**` markers)

The system must map the visible offset (21) to the correct raw offset (23).

## Solution Architecture

### 1. Detect Click Position (Visible Offset)

```javascript
// Get click position in rendered HTML
let range;
if (document.caretRangeFromPoint) {
    range = document.caretRangeFromPoint(e.clientX, e.clientY);
}

// Extract text before caret to get visible offset
const textBefore = extractRawTextBeforeCaret(preview, range);
const visibleOffset = textBefore.length;
```

### 2. Map Visible Offset to Raw Offset

Uses binary search for efficiency (O(log n) instead of O(n)):

```javascript
const rawInput = input.value;
let left = 0;
let right = rawInput.length;
let rawOffset = 0;

while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const rawSubstr = rawInput.substring(0, mid);
    const strippedSubstr = stripMarkdown(rawSubstr);
    const visibleLen = strippedSubstr.length;
    
    if (visibleLen === visibleOffset) {
        rawOffset = mid;
        break;
    } else if (visibleLen < visibleOffset) {
        left = mid + 1;
    } else {
        right = mid - 1;
    }
}
```

### 3. Fine-Tune Position

Handle edge cases where binary search lands in the middle of markdown syntax:

```javascript
while (rawOffset < rawInput.length) {
    const rawSubstr = rawInput.substring(0, rawOffset);
    const strippedSubstr = stripMarkdown(rawSubstr);
    if (strippedSubstr.length >= visibleOffset) {
        break;
    }
    rawOffset++;
}
```

### 4. Set Cursor Position

```javascript
requestAnimationFrame(() => {
    setCaretPosition(preview, rawOffset);
});
```

## Markdown Patterns Handled

The `stripMarkdown` function handles all these patterns:
- `**bold**` → bold
- `@@italic@@` → italic
- `__underline__` → underline
- `~~strikethrough~~` → strikethrough
- `==highlight==` → highlight
- `!!red!!` → red background
- `??blue??` → blue background
- `` `code` `` → code
- `^sup^` → superscript
- `~sub~` → subscript
- `##heading##` → heading
- `..small..` → small text
- `[[correct]]` → correct answer marker
- `{fg:#fff;bg:#000}text{/}` → colored text
- `{link:url}text{/}` → link
- `url[text]` → link
- And many more...

## Performance

- **Binary Search:** O(log n) iterations where n = raw input length
- **stripMarkdown calls:** ~log(n) times (once per binary search iteration)
- **Fine-tuning:** O(k) where k is typically small (length of markdown syntax at position)
- **Total:** O(log n) for most cases, very efficient even for large cells

## Edge Cases

1. **Click at start:** visibleOffset = 0 → rawOffset = 0
2. **Click at end:** visibleOffset = max → rawOffset = rawInput.length
3. **Click inside markdown syntax:** Fine-tuning loop ensures cursor lands after the syntax
4. **Multiple markdown patterns:** stripMarkdown handles all patterns correctly
5. **Nested patterns:** stripMarkdown processes in correct order

## Related Functions

- `handlePreviewMouseDown()` - Main click handler (~line 1402)
- `extractRawTextBeforeCaret()` - Gets visible text before click position
- `stripMarkdown()` - Removes all markdown syntax (~line 7040)
- `setCaretPosition()` - Sets cursor in contentEditable element
- `highlightSyntax()` - Renders markdown with visible syntax in edit mode

## Testing

To test cursor positioning:
1. Create a cell with various markdown patterns
2. Click at different positions in the preview
3. Check console logs for offset mapping
4. Verify cursor appears at correct position in edit mode

Example test cases:
- `**bold** text` - click on "text"
- `@@italic@@ **bold**` - click between patterns
- `{fg:#f00}colored{/} normal` - click on "colored"
- Long text with multiple patterns throughout

## Future Improvements

- Cache mapping for repeated clicks (if performance becomes an issue)
- Handle RTL text and bidirectional text
- Support for table cells with complex nested structures
