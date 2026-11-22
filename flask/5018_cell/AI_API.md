# AI API Reference — 5018_cell

Base URL: `http://localhost:5018`

Sheets can be identified by **arrayIndex** (e.g. `3`) or **customIndex** (14-digit timestamp, e.g. `20260519230334`).  
Use customIndex whenever possible — it never changes even if sheets are reordered.

## Syntax reference

```
GET /ai/syntaxes
```

Returns the built-in syntax guides, the AI cell syntax guidance, and the custom syntax markers currently configured in this app. CLI agents should read this before proposing cell content changes and should inspect `static/script.js` when parser behavior is unclear.

Response fields:
- `builtInSyntaxGuide` — contents of `md/MARKDOWN_SPECIAL.md`
- `aiCellSyntaxGuidance` — contents of `md/AI_CELL_INSTRUCTIONS.md`
- `customSyntaxes` — active custom markers and their colors/styles, emitted as literal UTF-8 characters
- `customSyntaxExamples` — paired syntax examples and exact Unicode code points for prefixes and suffixes
- `parserSource` — source files to inspect for actual parsing behavior

Custom markers may use visually similar Unicode characters. Preserve the literal marker and its listed code points exactly; do not normalize or replace it with a lookalike.

---

## Step 1 — Get the full schema (always start here)

```
GET /ai/schema
```

Returns every sheet with its `arrayIndex`, `customIndex`, `name`, `category`, `colCount`, `rowCount`, and column names.

```json
{
  "sheets": [
    {
      "arrayIndex": 0,
      "customIndex": "20260519230334",
      "name": "Verb List",
      "nickname": "",
      "category": "English Grammar",
      "parentSheet": null,
      "colCount": 3,
      "rowCount": 42,
      "columns": ["A", "B", "C"]
    }
  ],
  "categories": ["English Grammar", "Math", "..."]
}
```

---

## Step 2 — Read a full sheet

```
GET /ai/sheet/<id>
```

- `<id>` = arrayIndex or customIndex

Returns all rows (2D array), column names, and cellStyles.

```json
{
  "arrayIndex": 0,
  "customIndex": "20260519230334",
  "name": "Verb List",
  "columns": ["A", "B", "C"],
  "rows": [
    ["run", "ran", "run"],
    ["go",  "went", "gone"]
  ],
  "rowNumbering": { "apiRowIndexBase": 0, "visibleRowLabelBase": 1 },
  "cellStyles": {}
}
```

API row and column indexes are **0-indexed**. `rows[0]` is the first data row and Col 0 is column A. The visible row label is API row index + 1, so visible row 30 is `row: 29` in API requests. Agents should use visible row labels when describing locations to the user and zero-based indexes only in API requests.

---

## Step 3 — Find cells by text

```
GET /ai/find?sheet=<id>&q=<search text>
```

Case-insensitive substring match. Returns matching row/col indexes.

```
GET /ai/find?sheet=20260519230334&q=went
```

```json
{
  "sheetIndex": 0,
  "query": "went",
  "matches": [
    { "row": 1, "col": 1, "value": "went" }
  ]
}
```

---

## Step 4a — Read a single cell

```
GET /ai/cell/<id>/<row>/<col>
```

```
GET /ai/cell/20260519230334/1/1
```

```json
{
  "sheetIndex": 0,
  "customIndex": "20260519230334",
  "row": 1,
  "col": 1,
  "value": "went",
  "style": null
}
```

---

## Step 4b — Update a single cell

```
POST /ai/cell/<id>/<row>/<col>
Content-Type: application/json

{ "value": "new content here" }
```

For CLI-driven edits, prefer submitting a proposal for in-app review (Step 4c) instead of writing directly. The direct update endpoint above applies the change immediately and bypasses the review dialog.

Example — update row 1, col 1 of sheet with customIndex `20260519230334`:

```
POST /ai/cell/20260519230334/1/1
{ "value": "**went** (irregular)" }
```

Response:
```json
{ "success": true, "row": 1, "col": 1, "value": "**went** (irregular)" }
```

---

## Step 4c — Submit a cell update proposal for review

```
POST /ai/cell/<id>/<row>/<col>/proposal
Content-Type: application/json

{ "value": "complete proposed replacement content" }
```

Returns HTTP 202 with a `proposalId`. The open app displays the current and proposed content for approval. A proposal does not change the cell until approved in the app.

The app polls `GET /ai/proposals` for pending proposals. The UI approves with `POST /ai/proposals/<proposalId>/approve` or rejects with `DELETE /ai/proposals/<proposalId>`. Approval returns HTTP 409 if the cell changed after the proposal was created; reread the cell and submit a new proposal. Pending proposals are held in memory and are cleared if Flask restarts.

## Step 4d — Submit a whole-sheet batch proposal for review

Use the sheet-level task button to copy instructions for an AI agent. The agent can read the full sheet with `GET /ai/sheet/<id>`, then submit a batch for in-app review:

```
POST /ai/sheet/<id>/proposal
Content-Type: application/json

{
  "edits": [
    { "row": 0, "col": 1, "value": "complete proposed replacement" },
    { "row": 3, "col": 2, "value": "another replacement" }
  ]
}
```

Rows and columns are zero-based. A proposal can contain up to 200 distinct cells from one sheet. The app displays every proposed cell change together. Approval applies the entire batch only if every cell still matches the value captured when the proposal was submitted; if any cell changed, the batch is rejected as stale and must be regenerated. Rejection discards the whole batch. Proposals are held in memory and cleared if Flask restarts.

## Step 4e — Directly batch update multiple cells

```
POST /ai/cells
Content-Type: application/json

[
  { "sheet": "20260519230334", "row": 0, "col": 0, "value": "run" },
  { "sheet": "20260519230334", "row": 1, "col": 0, "value": "go" },
  { "sheet": 3,                "row": 2, "col": 1, "value": "other sheet cell" }
]
```

Each object can use a different sheet id. Returns a result array — one entry per update.

---

## Notes for AI

- **Always call `/ai/schema` first** to confirm sheet indexes before reading or writing.
- Cell values support markdown syntax (e.g. `**bold**`, `==highlight==`, `@@color@@`).
- `row` and `col` are both 0-indexed integers.
- If a cell is out of range, the API returns `{ "error": "Cell out of range" }` with HTTP 404.
- Writes are saved to disk immediately and auto-export the static HTML.
