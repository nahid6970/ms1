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

## Synchronization & Caret Management

Because the editor works with HTML but the data is stored as raw markdown, several key systems manage the translation:

### Data Flow
1.  **Input:** User types in the `contenteditable` div.
2.  **Extraction:** `extractRawText(element)` walks the DOM to reconstruct the plain markdown string (handling `<br>` as `\n`).
3.  **Storage:** The hidden `<input>` or `<textarea>` element's `.value` is updated silently as the "Source of Truth".
4.  **Re-rendering:** On every `input` event, the content is re-processed by `highlightSyntax()` to ensure markers stay accurate.

### Caret Persistence
Standard `contenteditable` re-rendering typically loses the cursor position. We use two specialized functions to maintain it:
*   `getCaretCharacterOffset(element)`: Counts plain-text characters from the start to the cursor.
*   `setCaretPosition(element, offset)`: Walks the new DOM tree to place the cursor at the exact same character point after a re-render.

## Implementation Details (`static/script.js`)

| Function | Description |
| :--- | :--- |
| `applyMarkdownFormatting` | Sets up the `contenteditable` environment and attaches event listeners. |
| `highlightSyntax(text)` | Highlighting engine that injects `.syn-marker` spans. |
| `extractRawText(element)` | DOM-to-String converter for raw markdown extraction. |
| `handlePreviewMouseDown`| Maps a mouse click on HTML coordinates to a character offset for focusing. |

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
