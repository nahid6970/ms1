# AI Cell Instructions

## Overview

Each table cell has a sparkle button that opens a small instruction editor. The instruction and the cell's current content are sent to the selected Gemini model. Gemini's response replaces the contents of that cell.

The sparkle button stays visible beneath the sticky table header as its cell scrolls. When opened, the instruction editor stays directly below the button while scrolling through that cell. The controls float over the cell without pushing its content down, and opening the editor does not jump the page to the top.

The floating editor is capped at 420px (or 70% of the viewport height) and scrolls internally when prompt history is long. Its Google Search checkbox has a fixed compact width so it cannot squeeze the label text into a tall, narrow column.

## Setup

1. Open **Settings → AI Cell Instructions**.
2. Enter and save a Gemini API key. The key is stored in this browser's `localStorage`.
3. Select **Test All Models**, enter a test prompt, and run the test. Models are checked sequentially; only models that return text successfully are added to the model picker.
4. Select one of the working models.

The model tester sends its prompt to each listed model and may use Gemini API quota.

## Updating a cell

1. Click the cell's **✨** button.
2. Enter the change you want in the instruction box, choose a previous prompt from **Recent prompts**, or click the microphone button to dictate it in the voice language selected for the app. The browser may request microphone access. The box grows automatically for multiline instructions. If the cell begins with an `Instruction: ...` line, that instruction is prefilled.
3. Click **Update**. Gemini uses the instruction and the cell's current content, then replaces the content in the same cell.
4. To use live web sources, enable **Web research (Google Search)** before clicking Update. The feature splits large cells into sections and researches them sequentially. It shows a review with the proposed cell content, source links, inline citations, and Google's search suggestions. Click **Apply to cell** to save the result, or **Cancel** to discard it. Research never changes the cell before you apply the preview.

### Web research, citations, and large cells

- Web research is opt-in for each request. It uses Gemini's Google Search grounding tool; ordinary updates keep their existing behavior.
- Input is divided at paragraph, line, or word boundaries into sections of at most 24,000 characters, then checked with Gemini's token-count endpoint and subdivided as needed to stay under 12,000 input tokens. At most 12 sections are researched in one operation. Very long unbroken lines or cells requiring more sections need a narrower request or added line breaks.
- Sections are processed one at a time to keep requests bounded. Each section may trigger Google Search grounding and consume API quota. Source references are merged, deduplicated, added beside supported text, and listed as clickable links at the end of the proposed cell content.
- The review shows Google's returned Search suggestions separately from the cell content. Google requires these suggestions to be shown with grounded answers; the app displays the returned suggestion HTML in a sandboxed frame.
- If a section fails, no part of the cell is saved. The cell is checked again when **Apply to cell** is clicked; if it changed during research, the stale result is rejected.
- Research requests send the relevant cell text and instruction to Google. Review Google's current [Gemini API terms](https://ai.google.dev/gemini-api/terms) before using sensitive content. See the [Google Search grounding guide](https://ai.google.dev/gemini-api/docs/generate-content/google-search) and [token-counting guide](https://ai.google.dev/gemini-api/docs/tokens).

## Recent prompts and pinned prompts

- After a successful cell update, the instruction is saved in this browser and appears in the editor's **Recent prompts** list.
- Click a prompt to put it back into the instruction box. You can edit it before running it again.
- Click the star beside a prompt to pin or unpin it. Pinned prompts stay at the top of the list.
- Click **×** beside a prompt to remove it from saved prompt history.
- The app keeps up to 20 unpinned prompts. Pinned prompts do not count toward this limit, and there is no limit on pinned prompts. Reusing a prompt moves it to the top of its group.
- Prompt history is stored in this browser's `localStorage`; it is available on this browser, not synced between browsers or devices.
- Clearing this browser's site data removes saved prompts.

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

## Search behavior

Regular cell updates do not perform a web search. Enable **Web research (Google Search)** when you want Gemini's Google Search grounding for current or source-backed information. Search results can still be incomplete or imperfect; review the proposed content and linked sources before applying it.

## Restart and refresh

These AI cell controls are implemented in the browser files (`static/script.js`, `static/style.css`, and `templates/index.html`) and do not require an app server restart. Refresh the browser after those files change.

## Related files

- `static/script.js` — Gemini requests, model testing, and cell update behavior
- `static/style.css` — sparkle button and inline instruction editor styles
- `templates/index.html` — AI settings and model tester markup
