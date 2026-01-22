# WYSIWYG Markdown Edit Mode

This document describes the "WYSIWYG with Visible Syntax" editing experience implemented for markdown-enabled cells. This architecture replaces the traditional transparent textarea overlay with a single dynamic `contenteditable` interface.

## Core Architecture: Dual Rendering

The system uses a single `div` with `contenteditable="true"` (the `.markdown-preview` overlay) that switches between two rendering modes based on focus state.

### 1. Blur State (Clean Preview)
*   **Trigger:** When the cell is not focused.
*   **Renderer:** `parseMarkdown(text)`
*   **Visual:** Shows the final rendered HTML. Syntax markers (e.g., `**`, `@@`) are completely hidden.
*   **Purpose:** Clean reading and presentation experience.

### 2. Focus State (Syntax Highlighting)
*   **Trigger:** When the user clicks or focuses the cell.
*   **Renderer:** `highlightSyntax(text)`
*   **Visual:** Styled HTML remains visible, but markdown syntax markers are revealed using a subtle, secondary style.
*   **Purpose:** Intuitive editing while maintaining visual context.

## Syntax Markers (`.syn-marker`)

To keep the markers unobtrusive during editing, they are wrapped in a special span:
```html
<span class="syn-marker">**</span>Bold Content<span class="syn-marker">**</span>
```

**Applied CSS Styles:**
*   `opacity: 0.6`: Makes markers faded.
*   `font-weight: normal !important`: Prevents markers from being bolded when the content is bold.
*   `text-decoration: none !important`: Prevents underlines from crossing through the markers.
*   Markers use a neutral color (e.g., `#888`).

## Synchronization & Data Flow

Because the editor works with HTML but the data is stored as raw markdown, several key systems manage the translation:

### Data Flow (Updated)
1.  **Focus:** User clicks cell. `highlightSyntax(text)` renders content with visible syntax markers.
2.  **Input:** User types, deletes, or presses Enter. Browser updates the DOM natively.
3.  **Sync:** `extractRawText(element)` walks the DOM to reconstruct the plain markdown string.
4.  **Storage:** Data is saved directly to `tableData.sheets[currentSheet].rows[rowIndex][colIndex]`.
5.  **Backend:** `saveData()` is called with a 1-second debounce.
6.  **Blur:** User clicks away. `parseMarkdown(text)` renders the clean preview.

**Important:** We do NOT re-render on every keystroke to avoid cursor jumping. The browser handles DOM updates naturally.

### Zero-Width Spaces (ZWS)
Empty lines (consecutive `<br>` tags) are not clickable by default. We insert zero-width spaces (`\u200B`) after `<br>` tags to provide cursor anchor points.

*   **Enter Key:** Inserts `<br>` + ZWS, positions cursor after ZWS.
*   **Backspace/Delete:** Automatically skips over ZWS to delete the actual character.
*   **Data Extraction:** `extractRawText()` strips all ZWS before saving.

### Scroll Prevention
When focusing a cell, the browser may scroll to bring it into view. We prevent this with:
*   `focus({ preventScroll: true })`
*   Save/restore of `tableContainer.scrollTop` and `scrollLeft`
*   CSS `scroll-margin: 0` on `.markdown-preview`

## Implementation Details (`static/script.js`)

| Function | Description |
| :--- | :--- |
| `applyMarkdownFormatting` | Sets up the `contenteditable` environment and attaches event listeners. |
| `highlightSyntax(text)` | Highlighting engine that injects `.syn-marker` spans and handles empty lines. |
| `extractRawText(element)` | DOM-to-String converter for raw markdown extraction (strips ZWS). |
| `handlePreviewMouseDown`| Maps a mouse click on HTML coordinates to a character offset for focusing. |
| `getCaretCharacterOffset` | Gets cursor position as character count (used on blur). |
| `setCaretPosition` | Sets cursor position by character offset (ZWS-aware). |

## Key Event Handlers

| Event | Behavior |
| :--- | :--- |
| `focus` | Switches to `highlightSyntax()` rendering, preserves scroll position. |
| `blur` | Switches to `parseMarkdown()` rendering, saves data via `updateCell()`. |
| `input` | Syncs data to `tableData` and `saveData()`, adjusts cell height. Does NOT re-render. |
| `keydown (Enter)` | Inserts `<br>` + ZWS, positions cursor correctly. |
| `keydown (Backspace/Delete)` | Skips over ZWS to delete actual characters. |

## Supported Visible Styles
The following styles are visible and interactive in Edit Mode:
*   **Bold** (`**text**`)
*   *Italic* (`@@text@@`)
*   <u>Underline</u> (`__text__`)
*   ~~Strikethrough~~ (`~~text~~`)
*   ==Highlight== (`==text==`)
*   <sup>Superscript</sup> (`^text^`)
*   <sub>Subscript</sub> (`~text~`)
*   Red/Blue Backgrounds (`!!text!!`, `??text??`)
*   Custom Color Syntaxes (e.g., `{fg:color}text{/}`)
