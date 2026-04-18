# Image Markdown Feature

## Feature Overview
Added support for standard markdown image syntax with extended options for custom dimensions. This allows users to embed images directly into table cells with optional resizing.

## Syntax
- **Standard:** `![alt text](url)`
- **With Width:** `![alt;width](url)` (e.g., `![My Image;200px](https://example.com/img.jpg)`)
- **With Width & Height:** `![alt;width;height](url)` (e.g., `![My Image;100%;150px](https://example.com/img.jpg)`)

## Features
- **Responsive by Default:** Images without specified width use `max-width: 100%` and `height: auto` to fit cell boundaries.
- **Custom Sizing:** Support for any CSS units (`px`, `%`, `em`, etc.) via the alt-text parameter splitting logic.
- **Alt Text:** Preserves standard accessibility by mapping the first part of the brackets to the `alt` attribute.
- **Static Export Support:** Full compatibility with `export_static.py` for offline viewing.

## Implementation Details

### 1. Detection (`static/script.js`)
- Updated `checkHasMarkdown(value)` to include `str.includes('![')`.
- This ensures the "Markdown" badge appears and the preview overlay is triggered.

### 2. Parsing Logic (`static/script.js`)
- Integrated into `parseMarkdownInline()` and `oldParseMarkdownBody()`.
- Regex: `/!\[([^\]]+)\]\(([^)]+)\)/g`
- Logic splits the bracket content by `;` to extract dimensions.

### 3. Stripping (`static/script.js`)
- Updated `stripMarkdown(text)` to remove image markers while preserving the alt text for plain-text contexts (like search index).

### 4. Static Rendering (`export_static.py`)
- Synced `hasMarkdown` detection and parsing logic into the Python export script.
- Uses identical regex and dimension handling for visual consistency.

### 5. Styling (`static/style.css`)
- Added `.markdown-preview img` styles:
  ```css
  max-width: 100%;
  height: auto;
  display: block;
  margin: 5px 0;
  ```

### 6. User Documentation (`templates/index.html`)
- Added a dedicated "Images" section to the Markdown Formatting Guide modal.

## Examples

| Syntax | Description |
|--------|-------------|
| `![Logo](https://example.com/logo.png)` | Default fit (max-width 100%) |
| `![Banner;100%](https://example.com/b.jpg)` | Full cell width |
| `![Icon;32px;32px](https://example.com/i.png)` | Specific thumbnail size |

## Date Completed
2026-04-18
