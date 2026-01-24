# Markdown View Modes

The application supports three distinct view modes for markdown-enabled cells, managed by two dedicated buttons in the toolbar.

## Mode Overview

| Button | Mode | ID | Behavior |
| :--- | :--- | :--- | :--- |
| **📝 (Raw)** | **Raw Mode** | 0 | Shows the raw markdown text inside a standard `<textarea>` or `<input>`. No formatting is applied. |
| **👁️ (Visual)** | **Standard Mode** | 1 | **Blur:** Shows clean rendered HTML.<br>**Focus:** Shows rendered HTML with dimmed syntax markers (`.syn-marker`). |
| **👁️ (Visual)** | **Clean Mode** | 2 | **Blur:** Shows clean rendered HTML.<br>**Focus:** Shows rendered HTML with **completely hidden** syntax markers. |

## Controls

### 1. Raw Mode Toggle (📝)
- **Click:** Switches between **Raw Mode** and your last used **Visual Mode**.
- **Visual:** Active when 📝 icon is fully opaque.

### 2. Visual Mode Toggle (👁️)
- **Click / Right-Click:** Cycles between **Standard Mode** and **Clean Mode**.
- **Visual:** Active when 👁️ icon is fully opaque.
- **Indicator:** In **Clean Mode**, the 👁️ icon has a **Magenta Glow**.

## Mode Persistence

The current mode is persisted in `localStorage` under `markdownPreviewMode`.
- `0`: Raw Mode
- `1`: Standard Markdown Mode
- `2`: Clean Markdown Mode

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
The `setMode(mode)` function manages the transitions:
1. Updates CSS classes on the table.
2. Updates UI indicators (checkboxes, active label classes).
3. Updates `localStorage`.
4. Calls `renderTable()` to refresh the view.
