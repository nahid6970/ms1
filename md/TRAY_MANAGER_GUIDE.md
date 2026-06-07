# Tray Manager Integration Guide

**File:** `C:\@delta\ms1\Tray_Manager.py`  
**Settings:** `C:\@delta\ms1\tray_settings.json`  
**Theme:** Cyberpunk — see `THEME_GUIDE.md`

---

## How It Works

A single persistent app with two parts:
- **pystray** — green ball tray icon, lives in the system tray
- **PyQt6 GUI** — opens on click, shows one `ScriptCard` per managed script

Each `ScriptCard` displays:
- Project name (large, **green** if running / **red** if stopped)
- Play ▶ / Stop ◼ PIL-drawn icon button right next to the title
- Optional settings widget below the header

Status is polled every **5 seconds** via subprocess calls (`tasklist`, `netstat`).

---

## How to Add a New Project

### Step 1 — Define status / start / stop functions

```python
# ── My New Script ─────────────────────────────────────────────────────────
def mynew_status() -> bool:
    return is_process_running("myprocess.exe")
    # OR for Flask/port-based: return is_flask_running(PORT)

def mynew_start():
    subprocess.Popen(["path\\to\\script.py"], shell=True)
    # OR: subprocess.Popen([sys.executable, MYNEW_SCRIPT], creationflags=subprocess.CREATE_NO_WINDOW)

def mynew_stop():
    subprocess.run(["taskkill", "/IM", "myprocess.exe", "/F"], shell=True)
```

### Step 2 — (Optional) Create a settings widget

```python
class MyNewSettings(QWidget):
    def __init__(self):
        super().__init__()
        self._settings = load_settings()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 4, 0, 4)
        row.setSpacing(6)

        row.addWidget(QLabel("Some setting:"))
        self._field = QLineEdit(self._settings.get("mynew", {}).get("some_key", "default"))
        row.addWidget(self._field)

        save_btn = QPushButton("💾")
        save_btn.setFixedSize(32, 32)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        row.addWidget(save_btn)

    def _save(self):
        self._settings.setdefault("mynew", {})["some_key"] = self._field.text()
        save_settings(self._settings)
```

### Step 3 — Add the card in `TrayManagerWindow.__init__`

```python
self._add_card(ScriptCard(
    title="My New Script",
    status_fn=mynew_status,
    start_fn=mynew_start,
    stop_fn=mynew_stop,
    settings_widget=MyNewSettings()   # or None if no settings needed
))
```

### Step 4 — Add default settings to `DEFAULT_SETTINGS`

```python
DEFAULT_SETTINGS = {
    "upload_files": { ... },
    "mynew": {
        "some_key": "default_value"
    }
}
```

---

## Status Detection Methods

| Script type | How to detect |
|---|---|
| `.exe` process | `is_process_running("name.exe")` |
| Flask / any port | `is_flask_running(PORT)` |
| Python script (launched by this app) | check `_proc.poll() is None` on the stored `Popen` handle |

---

## Settings File (`tray_settings.json`)

Flat JSON, one key per project:

```json
{
  "upload_files": {
    "save_folder": "C:/Users/nahid/Desktop/ShareFolder"
  },
  "mynew": {
    "some_key": "value"
  }
}
```

---

## Currently Integrated Projects

### Komorebi
- **Script:** `C:\@delta\ms1\TOOLS\komorebi_tray.py` (logic absorbed directly)
- **Detection:** `is_process_running("komorebi.exe")`
- **Start:** `komorebic start`
- **Stop:** `komorebic stop`
- **Settings:** none

### Upload Files (Flask :5002)
- **Script:** `C:\@delta\ms1\@Flask\5002_upload_files\upload_files.py`
- **Detection:** `is_flask_running(5002)`
- **Start:** launches `upload_files.py` as subprocess
- **Stop:** kills PID owning port 5002
- **Settings:** `save_folder` — where uploaded files from Android are saved
