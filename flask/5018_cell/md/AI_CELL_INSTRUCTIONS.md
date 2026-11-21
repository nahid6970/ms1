# AI Cell Instructions

## Overview

Each table cell has a sparkle button that opens a small instruction editor. The instruction and the cell's current content are sent to the selected Gemini model. Gemini's response replaces the contents of that cell.

The sparkle button stays visible beneath the sticky table header as its cell scrolls. When opened, the instruction editor stays directly below the button while scrolling through that cell. The controls float over the cell without pushing its content down, and opening the editor does not jump the page to the top.

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

## Updating a cell with a CLI agent

1. Open the cell's **✨** instruction editor and click **Copy CLI task**.
2. Paste the task into a CLI agent. It includes a stable sheet and cell reference and tells the agent to read the cell through the API, show what it found, and ask what you want changed before editing.
3. The task directs the agent to read `GET /ai/syntaxes` before proposing content. This endpoint returns the built-in syntax guides and the app's currently configured custom markers. The agent should inspect `static/script.js` if it needs to verify parser behavior.
4. After you give the agent an instruction, it submits a proposal through `POST /ai/cell/<id>/<row>/<col>/proposal`. The app shows a rendered preview and source diff. Use **View preview** and **View source** to review, then choose **Approve change** or **Reject**.

The proposal does not change the cell until you approve it. Approval checks that the cell still matches the value the agent originally read. If the cell changed meanwhile, the app refuses the stale proposal. Pending proposals are kept in memory and are cleared when Flask restarts. The direct `POST /ai/cell/<id>/<row>/<col>` API still applies changes immediately, so CLI agents should use the proposal endpoint.

Custom markers can contain Unicode characters that look alike. The syntax endpoint returns literal examples and Unicode code points; agents should copy the exact marker and must not normalize or substitute visually similar characters.

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

## Current search behavior

Cell updates currently call Gemini's `generateContent` endpoint directly. They do **not** perform Tavily or other web searches, so they cannot guarantee the latest online information. A request to update time-sensitive facts may rely on the selected model's existing knowledge.

## Restart and refresh

These AI cell controls are implemented in the browser files (`static/script.js`, `static/style.css`, and `templates/index.html`) and do not require an app server restart. Refresh the browser after those files change.

## Related files

- `static/script.js` — Gemini requests, model testing, and cell update behavior
- `static/style.css` — sparkle button and inline instruction editor styles
- `templates/index.html` — AI settings and model tester markup
