# Convex Config Backup — Integration Guide

Add cloud backup/restore (with full version history) to any Python PyQt script using Convex.

---

## Convex Project

One shared Convex project handles all your scripts. Located at:
```
C:\@delta\ms1\convex_config_backup\
```

### First-time setup
```bash
cd C:\@delta\ms1\convex_config_backup
npm install
npx convex dev
```
Copy the printed URL (e.g. `https://xxx.convex.cloud`) — you'll need it below.

### Schema
Each backup row stores:
- `scriptName` — unique key per script (e.g. `"script_manager"`)
- `label` — your description (e.g. `"before v2 update"`)
- `data` — the full JSON config as-is
- `createdAt` — timestamp (ms)

Backups are **never overwritten** — every backup is a new row, so you always have full history.

---

## Adding to a New Script

### Step 1 — Add imports (top of file)
```python
import urllib.request
```

### Step 2 — Add constants (after your CONFIG_FILE line)
```python
CONVEX_URL = "https://xxx.convex.cloud"  # your Convex deployment URL
SCRIPT_NAME = "my_script_name"           # unique key for this script
```

### Step 3 — Add dialog classes (before your MainWindow class)
Copy both classes from `script_manager_gui_qt.py`:
- `ConvexLabelDialog` — prompts for a backup label
- `RestoreDialog` — lists backups and lets user pick one

### Step 4 — Add methods to your MainWindow class
Copy these three methods from `script_manager_gui_qt.py`:
- `_convex_call(self, endpoint, payload)` — generic HTTP helper
- `backup_to_convex(self)` — saves current config
- `restore_from_convex(self)` — fetches and restores a chosen backup

### Step 5 — Add buttons to your UI
```python
self.btn_backup = QPushButton("☁")
self.btn_backup.clicked.connect(self.backup_to_convex)

self.btn_restore = QPushButton("⬇")
self.btn_restore.clicked.connect(self.restore_from_convex)
```

### Step 6 — Adapt `restore_from_convex` to your save method
The restore method calls `self.save_config()` after writing `self.config`.
Make sure your script has a `save_config()` method that writes `self.config` to disk and refreshes the UI.
If your method is named differently, update the call inside `restore_from_convex`.

---

## How It Works

### Backup flow
1. User clicks ☁
2. `ConvexLabelDialog` asks for a label
3. `self.config` (the in-memory dict) is sent to Convex via HTTP POST
4. Convex inserts a new row — old backups are untouched

### Restore flow
1. User clicks ⬇
2. Script queries Convex for all backups for this `SCRIPT_NAME`
3. `RestoreDialog` shows them sorted newest-first with date + label
4. User picks one → full JSON is fetched and written to disk
5. UI reloads

---

## Convex HTTP API (no SDK needed)

```python
import urllib.request, json

def convex_call(convex_url, endpoint, payload):
    url = f"{convex_url.rstrip('/')}/api/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

# Save
convex_call(CONVEX_URL, "mutation", {
    "path": "functions:save",
    "args": {"scriptName": "my_script", "label": "my label", "data": config_dict}
})

# List backups
result = convex_call(CONVEX_URL, "query", {
    "path": "functions:list",
    "args": {"scriptName": "my_script"}
})
backups = result["value"]  # list of {id, label, createdAt}

# Get one backup's data
result = convex_call(CONVEX_URL, "query", {
    "path": "functions:get",
    "args": {"id": backup_id}
})
config = result["value"]
```

---

## Notes

- The Convex backend stays live even when your terminal is closed
- Free tier: 40 deployments/month — only `npx convex dev/deploy` counts, not data operations
- To add a new script: just use a different `SCRIPT_NAME`, no Convex changes needed
- To delete old backups: use the Convex dashboard at `https://dashboard.convex.dev`
