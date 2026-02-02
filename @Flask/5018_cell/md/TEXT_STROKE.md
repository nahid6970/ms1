# Text Stroke Feature

A new markdown syntax for adding stroke/outline effects to text, making it appear thicker and more prominent.

## Syntax

**Basic (default 2px stroke):**
```
ŝŝtext ŝŝ
```

**Custom thickness:**
```
ŝŝthickness:text ŝŝ
```

## Examples

- `ŝŝCUPINE ŝŝ` → Text with 2px black stroke (default)
- `ŝŝ5:CUPINE ŝŝ` → Text with 5px black stroke
- `ŝŝ0.5:thin ŝŝ` → Text with 0.5px black stroke
- `ŝŝ8:BOLD ŝŝ` → Text with 8px black stroke

## Visual Effect

The text-stroke effect adds a black outline around the letters, making them appear thicker and more prominent. The thickness can be adjusted from very thin (0.5px) to very thick (10px or more).

## Implementation Details

### CSS Properties Used
```css
-webkit-text-stroke: [thickness]px black;
text-stroke: [thickness]px black;
font-weight: bold;
paint-order: stroke fill;
```

### Files Modified (Rule of 6)

1. **static/script.js - parseMarkdownInline()**: Added regex to parse `ŝŝthickness:text ŝŝ` and `ŝŝtext ŝŝ`
2. **static/script.js - checkHasMarkdown()**: Added `str.includes('ŝŝ')` detection
3. **static/script.js - stripMarkdown()**: Added regex to strip stroke markers for search/sort
4. **export_static.py - hasMarkdown**: Added `cellValue.includes('ŝŝ')` detection
5. **export_static.py - parseMarkdownInline()**: Added Python regex for both stroke patterns
6. **templates/index.html - Markdown Guide**: Added examples to the formatting guide modal

### Additional Updates
- **static/script.js - oldParseMarkdownBody()**: Added stroke parsing for multi-line content
- **static/script.js - highlightSyntax()**: Added syntax highlighting for edit mode
- **export_static.py - oldParseMarkdownBody()**: Added stroke parsing for static export

## Usage Tips

- Use thinner strokes (0.5-2px) for subtle emphasis
- Use medium strokes (3-5px) for headings and important text
- Use thick strokes (6-10px) for dramatic effect or logos
- The stroke is always black to ensure maximum contrast
- Works best with larger font sizes

## Browser Compatibility

The feature uses `-webkit-text-stroke` which is supported in:
- Chrome/Edge (all versions)
- Safari (all versions)
- Firefox (49+)
- Opera (all versions)

## Date Added
2026-02-02
