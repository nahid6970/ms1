# 5018_cell → Cloudflare Migration Notes

## Architecture Mapping

| Current (Flask/Local) | Cloudflare Equivalent |
|---|---|
| Flask REST API (`app.py`) | Cloudflare Workers (TypeScript) |
| `data.json` on disk | D1 (SQLite) — store as JSON blob or proper table |
| `sheet_active.json` | KV store |
| `custom_syntaxes.json` | KV store |
| `setting.json` | KV store |
| `index.html` + `static/` | Cloudflare Pages |
| `export_static.py` auto-export | Drop or trigger manually |
| `os.startfile()` `/api/open-file` | **Cannot migrate** (see below) |

---

## What Needs to Change

### Backend Rewrite (app.py → Worker)
- Rewrite the ~10 REST endpoints in TypeScript
- Replace all `open()` file reads/writes with D1 queries or KV operations
- Remove all hardcoded absolute paths (`C:\@delta\...`)
- The logic itself is trivial CRUD — low effort rewrite

### Hardcoded Paths to Remove
```
DATA_FILE = r'C:\@delta\ms1\@Flask\5018_cell\data.json'
STATE_FILE = r'C:\@delta\output\5018_output\sheet_active.json'
CUSTOM_SYNTAXES_FILE = r'C:\@delta\ms1\@Flask\5018_cell\custom_syntaxes.json'
SETTINGS_FILE = r'C:\@delta\db\5018_cell\setting.json'
```

### Auto-Export (`export_static.py`)
- Currently runs as a subprocess on every save
- Cannot run Python subprocesses in Workers
- Options: drop the feature, or manually trigger export separately

---

## What Cannot Be Migrated

### `os.startfile()` — `/api/open-file` endpoint
- **What it does:** When a cell contains a `file://` link (e.g., `[doc](file:///C:/notes.pdf)`), clicking it sends the path to Flask which opens it in Windows using `os.startfile()`
- **Why it can't work:** There's no local Windows machine on the cloud end to open files on
- **Fix:** Remove the `file://` branch in `script.js` (~line 2465), or show a toast saying local file links aren't supported

---

## Pros

- Zero server to maintain
- Accessible from any device/browser, not just local machine
- Free tier: 100k requests/day, 1GB D1 storage
- Global edge = fast loads anywhere
- Automatic HTTPS, no port forwarding or `localhost:5018`
- Easy to share with others

## Cons

- Full backend rewrite required (Python → TypeScript)
- `export_static.py` feature must be dropped or rethought
- `file://` local file opening is gone permanently
- Data is now in the cloud — need to consider privacy/auth
  - Mitigate with **Cloudflare Access** (zero-code login gate)
- D1 has a 1MB row size limit — if `data.json` grows very large, need to chunk it
- Workers have a 10ms CPU time limit on free tier (subrequest time not counted) — fine for simple CRUD

---

## Migration Effort Estimate

| Task | Effort |
|---|---|
| Rewrite `app.py` as Worker | ~2–4 hours |
| Set up D1 schema + KV bindings | ~1 hour |
| Deploy Pages + Worker | ~1 hour |
| Set up Cloudflare Access (auth) | ~30 min |
| Remove/handle `open-file` in JS | ~15 min |
| **Total** | **~5–6 hours** |

The frontend (`script.js`, `style.css`, `index.html`) requires **zero changes** — it just talks to API endpoints.

---

## Recommended D1 Schema (Simple Approach)

```sql
CREATE TABLE store (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
-- keys: 'data', 'active_sheet', 'custom_syntaxes', 'settings'
```

Store each JSON blob as a single row. Simple, mirrors current file-based approach exactly.

---

## Notes
- Assessed: 2026-06-07
- Project: `C:\@delta\ms1\@Flask\5018_cell`
- Current stack: Flask + local JSON files + vanilla JS frontend
