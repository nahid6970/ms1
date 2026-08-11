# AI API Reference — 5018_cell

Base URL: `http://localhost:5018`

Sheets can be identified by **arrayIndex** (e.g. `3`) or **customIndex** (14-digit timestamp, e.g. `20260519230334`).  
Use customIndex whenever possible — it never changes even if sheets are reordered.

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
  "cellStyles": {}
}
```

Row and column are **0-indexed**. Row 0 = first data row, Col 0 = column A.

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

## Step 4c — Batch update multiple cells

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
