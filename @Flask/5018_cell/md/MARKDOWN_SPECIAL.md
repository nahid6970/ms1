# Special Markdown & Highlight Syntaxes

## Text Stroke
**Syntax:** `ŝŝthickness:textŝŝ` or `ŝŝtextŝŝ` (default 2px)
**Output:** Text with a thick outline/border around letters
**Examples:**
- `ŝŝCUPINEŝŝ` → 2px stroke (default)
- `ŝŝ3:CUPINEŝŝ` → 3px stroke
- `ŝŝ5:THICK TEXTŝŝ` → 5px stroke
**Details:** See `md/TEXT_STROKE.md`.

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
**Syntax:** `:::Title Text:::` or `:::Params:::Title Text:::`
**Output:** Text with top and bottom borders, bold, and centered.
**Customization:**
- **Params:** `BORDERC_THICK_FSIZE_FCOLOR` (e.g., `R_3px_1.5em_f-B`)
- **Colors:** R, G, B, Y, O, P, C, W, K, GR or Hex codes.
- **Thickness:** Any pixel value (e.g., `2px`, `5px`).
- **Font Size:** Values in `em`, `rem`, or `px` (e.g., `1.5em`, `20px`).
- **Font Color:** Use `f-` prefix followed by color code or hex (e.g., `f-R`, `f-#000`).
**Example:** `:::R_3px_1.2em_f-K:::Important Section:::` creates a red 3px bordered title with black 1.2em text.

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
