# Markdown View Modes

The application supports three distinct view modes for markdown-enabled cells, allowing users to balance between deep editing and a clean visual experience.

## Mode Overview

Users can cycle through these modes by clicking (left-click) or right-clicking the **Page Icon (📄)** in the toolbar.

| Mode | ID | Behavior | Best For |
| :--- | :--- | :--- | :--- |
| **Raw Mode** | 0 | Shows the raw markdown text inside a standard `<textarea>` or `<input>`. No formatting is applied. | Debugging syntax, bulk text changes, and complex editing. |
| **Standard Mode** | 1 | **Blur:** Shows clean rendered HTML.<br>**Focus:** Shows rendered HTML with dimmed syntax markers (`.syn-marker`). | Balanced "Rich-Text" editing where syntax is still visible but unobtrusive. |
| **Clean Mode** | 2 | **Blur:** Shows clean rendered HTML.<br>**Focus:** Shows rendered HTML with **completely hidden** syntax markers. | True WYSIWYG editing. The text appears exactly as it will be rendered. |

## Mode Persistence

The current mode is persisted in `localStorage` under `markdownPreviewMode`.
- `0`: Raw Mode (icon checkbox unchecked)
- `1`: Standard Markdown Mode (icon checkbox checked, default look)
- `2`: Clean Markdown Mode (icon checkbox checked, icon has magenta glow)

## Technical Implementation

### CSS Classes
The active mode is applied as a class to the `#dataTable` element:
- **Raw Mode:** `.hide-markdown-preview` (Standard inputs are shown, previews are hidden).
- **Clean Mode:** `.clean-markdown-mode`.

### Syntax Hiding (Clean Mode)
In Clean Mode, syntax markers are hidden via CSS while the parent styled elements remain visible:
```css
.clean-markdown-mode .syn-marker {
    display: none !important;
}
```

### Toggle Logic (`static/script.js`)
The `toggleMarkdownPreview()` function manages the cycle:
1. Reads `currentMode` from `localStorage`.
2. Calculates `nextMode = (current + 1) % 3`.
3. Updates CSS classes on the table.
4. Updates UI indicators (checkbox, label classes).
5. Calls `renderTable()` to refresh the view.

## Visual Indicators

- **Raw Mode:** The 📄 icon is dimmed (unchecked).
- **Standard Mode:** The 📄 icon is active (checked, default cyan/green).
- **Clean Mode:** The 📄 icon is active and has a **Magenta Glow** (`clean-mode-active` class) to indicate syntax is suppressed.
