# Special Markdown & Highlight Syntaxes

## List Items
**Syntax:** 
- `- item` → Bullet list (•)
- `-- item` → Sub-bullet (◦) with 1em indent
- `--- item` → Sub-sub-bullet (▪) with 2em indent
- `---- item` → Level 4 bullet (▸) with 3em indent
- `----- item` → Level 5 bullet (−) with 4em indent
- `1. item` → Numbered list

**Features:**
- Hanging indent: wrapped lines align with text after the bullet, not the bullet itself
- Tab preservation: tab characters within list content maintain alignment
- Uses `display: inline-block` with `text-indent` for proper hanging indent
- `white-space: pre-wrap` preserves tabs and spaces

**Example:**
```
- আকুঞ্চন		প্রসারণ
- কুঞ্চন		প্রসারণ
-- Sub-item with indent
--- Deep nested item
1. First numbered item
2. Second numbered item
```

## Small Text
**Syntax:** `..small text..` 
**Output:** `<span style="font-size: 0.75em;">$1</span>`

## Variable Font Size Headings
**Syntax:** `#2#text#/#` (2x size), `#0.5#text#/#` (0.5x size)
**Output:** `<span style="font-size: {size}em; font-weight: 600;">`

## Title Text
**Syntax:** `:::Title Text:::`
**Output:** Text with top and bottom borders, bold, and centered. Useful for important section titles.

## Border Box
**Syntax:** `#R#text#/#` (color codes: R, G, B, Y, O, P, C, W, K, GR)
**Output:** Colored border around text.

## Colored Underline
**Syntax:** `_R_text__` (color codes: R, G, B, Y, O, P, C, W, K, GR)
**Output:** 2px thick colored underline.

## Wavy Underline
**Syntax:** `_.text._`
**Output:** Wavy underline (like spellcheck).

## Horizontal Separators
**Syntax:** `-----` (5+ dashes)
**Output:** `<div class="md-separator"></div>` (4px solid gray line).

## Separator Background Colors
**Syntax:** `[COLOR1]-----[COLOR2/HEX]`
**Function:** Line color (COLOR1) + Section background color (COLOR2) until next separator.
**Details:** See `md/SEPARATOR_BACKGROUND_COLOR.md`.

## Alternative Link Syntax
**Syntax:** `https://url[Link Text]`
**Function:** Shorter than `{link:url}...` and supports nested markdown.

## Custom Color Syntax
**Syntax:** User-defined (e.g., `++text++`, `%%text%%`)
**Function:** Apply custom colors and formatting defined in Settings.
**Details:** See `md/CUSTOM_SYNTAX.md`.
