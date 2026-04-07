# Convex Config Backup � Integration Guide

Add cloud backup/restore (with full version history) to any Python PyQt script using Convex.

---

## Convex Project

One shared Convex project handles all your scripts. Located at:

C:\@delta\ms1\convex_config_backup\


### Current Deployment
**CONVEX_URL:** https://different-gnat-734.convex.cloud

---

## Integration Reference (Self-Contained)

### 1. Imports
`python
import urllib.request
import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                            QLineEdit, QPushButton, QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, QByteArray, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtSvg import QSvgRenderer
`

### 2. Constants & Cyberpunk Theme
`python
CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "your_unique_script_name"

# Cyberpunk-style colors
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

# SVG Collection
SVGS = {
    "UPLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',        
    "DOWNLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',   
    "TRASH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2-0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
    "DIFF": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>'
}
`

### 3. UI Components

#### CyberButton (SVG + Hover Support)
`python
class CyberButton(QPushButton):
    """Modern button with SVG icon support and dynamic hover color-switching."""
    def __init__(self, text="", parent=None, color=CP_YELLOW, is_outlined=False, svg_data=None):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.svg_data = svg_data
        self.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        if svg_data:
            self.update_icon(self.color if self.is_outlined else CP_BG)
        self.update_style()

    def update_icon(self, color):
        if not self.svg_data: return
        # Inject color into SVG currentColor placeholder
        colored_svg = self.svg_data.replace('currentColor', color)
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))
        pix = QPixmap(18, 18)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        renderer.render(painter)
        painter.end()
        self.setIcon(QIcon(pix))
        self.setIconSize(QSize(18, 18))

    def enterEvent(self, event):
        if self.svg_data:
            self.update_icon(CP_BG if self.is_outlined else self.color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.svg_data:
            self.update_icon(self.color if self.is_outlined else CP_BG)
        super().leaveEvent(event)

    def update_style(self):
        if self.is_outlined:
            self.setStyleSheet(f"""
                QPushButton {{ background-color: transparent; color: {self.color}; border: 2px solid {self.color}; padding: 5px 15px; font-family: 'Consolas'; }}
                QPushButton:hover {{ background-color: {self.color}; color: {CP_BG}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{ background-color: {self.color}; color: {CP_BG}; border: none; padding: 5px 15px; font-family: 'Consolas'; }}
                QPushButton:hover {{ background-color: {CP_BG}; color: {self.color}; border: 1px solid {self.color}; }}
            """)
`

#### ConvexLabelDialog
`python
class ConvexLabelDialog(QDialog):
    """Backup label dialog with inline CHECK button to compare local vs latest backup."""
    def __init__(self, parent=None, convex_call_fn=None, config_data=None):
        super().__init__(parent)
        self.setWindowTitle("BACKUP LABEL")
        self.setFixedWidth(420)
        self._convex_call = convex_call_fn
        self._config_data = config_data or {}
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }} QLabel {{ color: {CP_TEXT}; }} QLineEdit {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px; font-family: Consolas; }}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter a label for this backup:"))
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("e.g. before v2 update")
        layout.addWidget(self.inp)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("font-family: Consolas; font-size: 9pt; padding: 4px;")
        layout.addWidget(self.status_lbl)

        btns = QHBoxLayout()
        ok = CyberButton("BACKUP", color=CP_CYAN)
        ok.clicked.connect(self.accept)
        self.check_btn = CyberButton("CHECK", color=CP_YELLOW, is_outlined=True)
        self.check_btn.clicked.connect(self._check_sync)
        cancel = CyberButton("CANCEL", color=CP_DIM, is_outlined=True)
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addWidget(self.check_btn); btns.addWidget(cancel)
        layout.addLayout(btns)

    def _check_sync(self):
        if not self._convex_call:
            self.status_lbl.setText("No connection available.")
            return
        try:
            self.check_btn.setEnabled(False)
            self.status_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: Consolas; font-size: 9pt; padding: 4px;")
            self.status_lbl.setText("Checking...")
            QApplication.processEvents()
            result = self._convex_call("query", {"path": "functions:list", "args": {"scriptName": SCRIPT_NAME}})
            backups = result.get("value", [])
            if not backups:
                self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText("⚠ No backups found — backup recommended!")
                return
            latest = max(backups, key=lambda b: b["createdAt"])
            remote = self._convex_call("query", {"path": "functions:get", "args": {"id": latest["id"]}}).get("value", {})
            skip = {"$schema", "gui_settings"}
            local = {k: v for k, v in self._config_data.items() if k not in skip}
            def fix(obj):
                if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
                if isinstance(obj, list): return [fix(i) for i in obj]
                if isinstance(obj, float) and obj.is_integer(): return int(obj)
                return obj
            remote_cmp = {k: v for k, v in fix(remote).items() if k not in skip}
            dirty = json.dumps(local, sort_keys=True) != json.dumps(remote_cmp, sort_keys=True)
            if dirty:
                self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText(f"⚠ OUT OF SYNC with '{latest['label']}' — backup recommended!")
            else:
                self.status_lbl.setStyleSheet(f"color: {CP_GREEN}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText(f"✔ In sync with '{latest['label']}' — no backup needed.")
        except Exception as e:
            self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
            self.status_lbl.setText(f"Error: {e}")
        finally:
            self.check_btn.setEnabled(True)

    @staticmethod
    def get_label(parent=None, convex_call_fn=None, config_data=None):
        dlg = ConvexLabelDialog(parent, convex_call_fn=convex_call_fn, config_data=config_data)
        ok = dlg.exec() == QDialog.DialogCode.Accepted
        return dlg.inp.text(), ok
`

#### RestoreDialog
`python
class RestoreDialog(QDialog):
    """Shows list of backups and lets user pick one to restore or delete."""
    def __init__(self, backups, convex_call_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RESTORE FROM BACKUP")
        self.setFixedWidth(520)
        self.selected_id = None
        self._convex_call = convex_call_fn
        self._backups = list(backups)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_YELLOW}; font-family: 'Consolas'; font-size: 10pt; }} QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }} QPushButton {{ font-family: 'Consolas'; font-size: 10pt; font-weight: bold; }}")
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(QLabel("Select a backup to restore:"))
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: 1px solid #3a3a3a;")
        self._scroll.setFixedHeight(300)
        self._layout.addWidget(self._scroll)
        
        cancel = CyberButton("ABORT", color=CP_DIM, is_outlined=True)
        cancel.clicked.connect(self.reject)
        self._layout.addWidget(cancel)
        self._render_list()

    def _render_list(self):
        import datetime
        inner = QWidget()
        inner.setStyleSheet(f"background: {CP_PANEL};")
        vbox = QVBoxLayout(inner)
        vbox.setSpacing(4)
        for b in self._backups:
            # 12-hour format: %I:%M %p
            dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M %p")
            row = QHBoxLayout()

            # Separator: ->
            btn = QPushButton(f"  {dt}  ->  {b['label']}")
            btn.setStyleSheet(f"text-align: left; padding: 8px; background: {CP_BG}; color: {CP_TEXT}; border: 1px solid #2a2a2a;")
            btn.clicked.connect(lambda checked, bid=b["id"]: self._select(bid))

            # Delete button with SVG icon
            del_btn = QPushButton()
            del_btn.setFixedSize(32, 32)
            del_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")

            # Render TRASH icon with RED color
            renderer = QSvgRenderer(QByteArray(SVGS["TRASH"].replace('currentColor', CP_RED).encode()))
            pix = QPixmap(22, 22)
            pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pix)
            renderer.render(painter)
            painter.end()
            del_btn.setIcon(QIcon(pix))
            del_btn.clicked.connect(lambda checked, bid=b["id"]: self._delete(bid))

            row.addWidget(btn)
            row.addWidget(del_btn)
            vbox.addLayout(row)
        vbox.addStretch()
        self._scroll.setWidget(inner)

    def _delete(self, backup_id):
        try:
            self._convex_call("mutation", {"path": "functions:remove", "args": {"id": backup_id}})
            self._backups = [b for b in self._backups if b["id"] != backup_id]
            self._render_list()
        except Exception as e:
            QMessageBox.critical(self, "DELETE FAILED", str(e))

    def _select(self, backup_id):
        self.selected_id = backup_id
        self.accept()
`


### 4. Implementation Methods (Add to MainWindow)

`python
def _fix_floats(self, obj):
    """Recursively convert float values that should be ints (whole numbers)."""
    if isinstance(obj, dict):
        return {k: self._fix_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [self._fix_floats(i) for i in obj]
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    return obj

def _convex_call(self, endpoint, payload):
    """Generic Convex HTTP API call."""
    url = f"{CONVEX_URL.rstrip('/')}/api/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def backup_to_convex(self):
    label, ok = ConvexLabelDialog.get_label(self, convex_call_fn=self._convex_call, config_data=self.config)
    if not ok or not label.strip(): return
    
    # CRITICAL: Convex reserves field names starting with $
    # Strip  if present
    backup_data = self.config.copy()
    if "\" in backup_data:
        del backup_data["\"]

    try:
        res = self._convex_call("mutation", {
            "path": "functions:save",
            "args": {"scriptName": SCRIPT_NAME, "label": label.strip(), "data": backup_data}
        })
        if res.get("status") == "success":
            QMessageBox.information(self, "BACKUP", f'Config backed up: "{label.strip()}"')
        else:
            QMessageBox.warning(self, "BACKUP ERROR", str(res))
    except Exception as e:
        QMessageBox.critical(self, "BACKUP FAILED", str(e))

def restore_from_convex(self):
    try:
        result = self._convex_call("query", {
            "path": "functions:list",
            "args": {"scriptName": SCRIPT_NAME}
        })
        backups = result.get("value", [])
        if not backups:
            QMessageBox.information(self, "RESTORE", "No backups found.")
            return

        dlg = RestoreDialog(backups, self._convex_call, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_id:
            data = self._convex_call("query", {
                "path": "functions:get",
                "args": {"id": dlg.selected_id}
            }).get("value")

            if data:
                self.config = self._fix_floats(data)
                self.save_config()    # Implement this to write to disk
                self.update_display() # Implement this to refresh UI
                QMessageBox.information(self, "RESTORE", "Restored successfully.")
    except Exception as e:
        QMessageBox.critical(self, "RESTORE FAILED", str(e))
`

### 5. UI Buttons

`python
# Backup button (Cyan Upload)
self.backup_btn = CyberButton("", color=CP_CYAN, is_outlined=True, svg_data=SVGS["UPLOAD"])
self.backup_btn.setToolTip("Backup to Cloud")
self.backup_btn.clicked.connect(self.backup_to_convex)

# Restore button (Yellow Download)
self.restore_btn = CyberButton("", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["DOWNLOAD"])
self.restore_btn.setToolTip("Restore from Cloud")
self.restore_btn.clicked.connect(self.restore_from_convex)
`

---

## Notes
- Convex stores numbers as floats; use _fix_floats before loading into PyQt.
- SCRIPT_NAME must be unique across all projects using this shared Convex URL.
- **Reserved Fields**: Fields starting with $ (like \) are RESERVED by Convex and must be removed before saving.
- **Time Format**: Use 12-hour format (%I:%M %p) and -> separator in the Restore dialog list for consistency.
- Backups are immutable (full history), but individual versions can be deleted via the Trash icon in the Restore dialog.

---

## Rule List Sorting (komorebi_gui_custom)

A sort dropdown sits in the top bar next to the search input. 4 modes:

| Option | Behavior |
|---|---|
| `SORT: NAME ↑` | Alphabetical by ID (A→Z) |
| `SORT: NAME ↓` | Alphabetical by ID (Z→A) |
| `SORT: DATE ↑` | Insertion order (oldest first) |
| `SORT: DATE ↓` | Insertion order (newest first) |

"Date" order reflects the order items appear in `ignore_rules` then `tray_and_multi_window_applications` in the JSON. Items in both lists use their first-seen index.

### UI (init_ui)

```python
self.sort_combo = QComboBox()
self.sort_combo.addItems(["SORT: NAME ↑", "SORT: NAME ↓", "SORT: DATE ↑", "SORT: DATE ↓"])
self.sort_combo.currentIndexChanged.connect(self.refresh_list)
top_bar.addWidget(self.sort_combo)
```

### Sorting logic (refresh_list)

```python
order = {}
idx = 0
for r in self.config_data.get("ignore_rules", []):
    k = (r["kind"], r["id"], r.get("matching_strategy", "Equals"))
    order.setdefault(k, idx); idx += 1
for a in self.config_data.get("tray_and_multi_window_applications", []):
    k = (a["kind"], a["id"], a.get("matching_strategy", "Equals"))
    order.setdefault(k, idx); idx += 1

sort_mode = self.sort_combo.currentText() if hasattr(self, 'sort_combo') else 'SORT: NAME ↑'
if 'NAME' in sort_mode:
    items = sorted(unified.items(), key=lambda x: x[1]['id'].lower(), reverse='↓' in sort_mode)
else:
    items = sorted(unified.items(), key=lambda x: order[x[0]], reverse='↓' in sort_mode)
items = [v for _, v in items]
```
