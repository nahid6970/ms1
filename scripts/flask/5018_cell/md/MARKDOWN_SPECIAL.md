# Special Markdown & Highlight Syntaxes

## Small Text
**Syntax:** `..small text..` 
**Output:** `<span style="font-size: 0.75em;">$1</span>`

## Variable Font Size Headings
**Syntax:** `#2#text#/#` (2x size), `#0.5#text#/#` (0.5x size)
**Output:** `<span style="font-size: {size}em; font-weight: 600;">`

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
