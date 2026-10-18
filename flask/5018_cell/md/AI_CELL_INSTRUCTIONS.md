# AI Cell Instructions

## Overview

Each table cell has a sparkle button that opens a small instruction editor. The instruction and the cell's current content are sent to the selected Gemini model. Gemini's response replaces the contents of that cell.

## Setup

1. Open **Settings → AI Cell Instructions**.
2. Enter and save a Gemini API key. The key is stored in this browser's `localStorage`.
3. Select **Test All Models**, enter a test prompt, and run the test. Models are checked sequentially; only models that return text successfully are added to the model picker.
4. Select one of the working models.

The model tester sends its prompt to each listed model and may use Gemini API quota.

## Updating a cell

1. Click the cell's **✨** button.
2. Enter the change you want in the instruction box, or click the **🎙️** button to dictate it in the voice language selected for the app. If the cell begins with an `Instruction: ...` line, that instruction is prefilled.
3. Click **Update**. Gemini uses the instruction and the cell's current content, then replaces the content in the same cell.

When a cell begins with an `Instruction:` line, that first line is treated as the instruction metadata; the remaining lines are sent as the cell content. For cells without that prefix, the whole current value is sent as content.

The table refreshes immediately after a successful update, and the normal cell save flow persists the result.

## Formatting syntax for Gemini output

The cell instruction prompt tells Gemini to use these project-specific forms:

| Use | Syntax | Meaning |
| --- | --- | --- |
| Extra-large text | `#1.5#text#/#` | 1.5× text |
| Large text | `##text##` | Larger text |
| Bold | `**text**` | Bold text |
| Italic | `@@text@@` | Italic text |
| Underline | `__text__` | Underlined text |
| List level 1 | `- text` | First list level |
| List level 2 | `-- text` | Nested list level |
| List level 3 | `--- text` | Third list level |
| Table | `| H1 | H2 |` with `| --- | --- |` separator | Pipe table |

Single-star emphasis (`*text*`) and asterisk bullets are not supported. Before saving, the AI instruction converts common single-star emphasis to the project's `@@text@@` italic syntax and asterisk bullets to hyphen bullets. It also converts Markdown heading lines such as `### Heading` to `##Heading##`, removes standalone horizontal divider lines, normalizes spaced nested bullets (`- - item`) to contiguous list markers, and removes zero-width spaces. Pipe table separators are preserved.

## Current search behavior

Cell updates currently call Gemini's `generateContent` endpoint directly. They do **not** perform Tavily or other web searches, so they cannot guarantee the latest online information. A request to update time-sensitive facts may rely on the selected model's existing knowledge.

## Restart and refresh

These AI cell controls are implemented in the browser files (`static/script.js`, `static/style.css`, and `templates/index.html`) and do not require an app server restart. Refresh the browser after those files change.

## Related files

- `static/script.js` — Gemini requests, model testing, and cell update behavior
- `static/style.css` — sparkle button and inline instruction editor styles
- `templates/index.html` — AI settings and model tester markup
