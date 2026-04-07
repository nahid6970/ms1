# Convex Config Backup & Integration Guide

Add cloud backup/restore (with full version history) to any Python PyQt script using Convex.

## Convex Project

One shared Convex project handles all your scripts. Located at:
`C:\@delta\ms1\convex_config_backup\`

### Current Deployment

**CONVEX_URL:** https://different-gnat-734.convex.cloud

---

## Integration Reference (Self-Contained)

### 1. Imports

```python
import urllib.request
import json
import os
import difflib
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, QByteArray, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtSvg import QSvgRenderer
```

> `difflib` is required for the `DiffDialog` feature.

---

### 2. Constants & Cyberpunk Theme

```python
CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "your_unique_script_name"

# Cyberpunk-style colors
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"
CP_GREEN  = "#00FF88"

# SVG Collection
SVGS = {
    "UPLOAD":   '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',
    "DOWNLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',
    "TRASH":    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2-0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
    "DIFF":     '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
}
```

---

### 3. UI Components

#### CyberButton (SVG + Hover Support)

```python
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
```

---

#### DiffDialog *(NEW)*

A GitHub-style color-coded diff viewer. Compares any two JSON-serializable data structures line by line using `difflib.unified_diff`.

- **Green lines** (`+`) = present in Local, not in Remote (additions)
- **Red lines** (`-`) = present in Remote, not in Local (removals)
- **Cyan lines** (`@@`) = hunk headers
- Both datasets are normalized before comparison (floats that are whole numbers → int, keys sorted)

```python
class DiffDialog(QDialog):
    """GitHub-style color-coded comparison view."""
    def __init__(self, local_data, remote_data, title="SYSTEM // DIFF_VIEW", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 700)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }}")

        layout = QVBoxLayout(self)

        header = QLabel("COMPARISON: REMOTE (RED) vs LOCAL (GREEN)")
        header.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {CP_YELLOW}; padding: 5px;")
        layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: 1px solid {CP_DIM}; background-color: {CP_PANEL}; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {CP_DIM}; }}
        """)

        content = QWidget()
        content.setStyleSheet(f"background-color: {CP_PANEL};")
        vbox = QVBoxLayout(content)
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 5, 5, 5)

        # Normalize: convert whole-number floats to int for accurate comparison
        def fix(obj):
            if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
            if isinstance(obj, list): return [fix(i) for i in obj]
            if isinstance(obj, float) and obj.is_integer(): return int(obj)
            return obj

        local_str  = json.dumps(fix(local_data),  indent=2, sort_keys=True).splitlines()
        remote_str = json.dumps(fix(remote_data), indent=2, sort_keys=True).splitlines()

        diff = list(difflib.unified_diff(remote_str, local_str, fromfile='Backup', tofile='Local', lineterm=''))

        if not diff:
            lbl = QLabel("No differences detected.")
            lbl.setStyleSheet(f"color: {CP_GREEN}; font-family: 'Consolas'; padding: 10px;")
            vbox.addWidget(lbl)
        else:
            for line in diff:
                lbl = QLabel(line)
                lbl.setFont(QFont("Consolas", 9))
                if line.startswith('+'):
                    lbl.setStyleSheet("background-color: #12261e; color: #3fb950; padding: 1px 4px;")
                elif line.startswith('-'):
                    lbl.setStyleSheet("background-color: #2c1619; color: #f85149; padding: 1px 4px;")
                elif line.startswith('@@'):
                    lbl.setStyleSheet(f"background-color: #0d1117; color: {CP_CYAN}; padding: 1px 4px;")
                else:
                    lbl.setStyleSheet(f"color: {CP_TEXT}; padding: 1px 4px;")
                vbox.addWidget(lbl)

        vbox.addStretch()
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)

        close = CyberButton("CLOSE PROTOCOL", color=CP_DIM, is_outlined=True)
        close.clicked.connect(self.accept)
        layout.addWidget(close)
```

**Usage:**
```python
DiffDialog(local_data, remote_data, parent=self).exec()
# local_data  = your current in-memory config (list or dict)
# remote_data = data fetched from Convex backup
```

---

#### ConvexLabelDialog *(updated — diff support added)*

Now stores the fetched remote data and shows a **SHOW DIFF** button when an out-of-sync state is detected.

**Key changes from previous version:**
- `config_data` is now a **list** (not a dict) — adapt if your config is a dict
- `_remote_data` field stores the last fetched remote snapshot
- `diff_btn` (hidden by default) appears only when out-of-sync
- `_show_diff()` opens a `DiffDialog` comparing local vs remote

```python
class ConvexLabelDialog(QDialog):
    """Backup label dialog with inline CHECK button to compare local vs latest backup."""
    def __init__(self, parent=None, convex_call_fn=None, config_data=None):
        super().__init__(parent)
        self.setWindowTitle("BACKUP LABEL")
        self.setFixedWidth(420)
        self._convex_call = convex_call_fn
        self._config_data = config_data or []   # list or dict depending on your project
        self._remote_data = None                # populated after CHECK
        self.setStyleSheet(
            f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }} "
            f"QLabel {{ color: {CP_TEXT}; }} "
            f"QLineEdit {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px; font-family: Consolas; }}"
        )
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

        self.diff_btn = CyberButton("SHOW DIFF", color=CP_YELLOW, is_outlined=True)
        self.diff_btn.clicked.connect(self._show_diff)
        self.diff_btn.hide()  # hidden until CHECK reveals a diff

        cancel = CyberButton("CANCEL", color=CP_DIM, is_outlined=True)
        cancel.clicked.connect(self.reject)

        btns.addWidget(ok)
        btns.addWidget(self.check_btn)
        btns.addWidget(self.diff_btn)
        btns.addWidget(cancel)
        layout.addLayout(btns)

    def _show_diff(self):
        if self._remote_data is not None:
            DiffDialog(self._config_data, self._remote_data, parent=self).exec()

    def _check_sync(self):
        if not self._convex_call:
            self.status_lbl.setText("No connection available.")
            return
        try:
            self.check_btn.setEnabled(False)
            self.status_lbl.setStyleSheet(f"color: {CP_DIM}; font-family: Consolas; font-size: 9pt; padding: 4px;")
            self.status_lbl.setText("Checking...")
            QApplication.processEvents()

            result = self._convex_call("query", {"path": "functions:list", "args": {"scriptName": SCRIPT_NAME}})
            backups = result.get("value", [])
            if not backups:
                self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText("⚠ No backups found — backup recommended!")
                return

            latest = max(backups, key=lambda b: b["createdAt"])
            remote_raw = self._convex_call(
                "query", {"path": "functions:get", "args": {"id": latest["id"]}}
            ).get("value", [])

            def fix(obj):
                if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
                if isinstance(obj, list): return [fix(i) for i in obj]
                if isinstance(obj, float) and obj.is_integer(): return int(obj)
                return obj

            self._remote_data = fix(remote_raw)
            dirty = json.dumps(self._config_data, sort_keys=True) != json.dumps(self._remote_data, sort_keys=True)

            if dirty:
                self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText(f"⚠ OUT OF SYNC with '{latest['label']}' — backup recommended!")
                self.diff_btn.show()   # reveal SHOW DIFF button
            else:
                self.status_lbl.setStyleSheet(f"color: {CP_GREEN}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText(f"✔ In sync with '{latest['label']}' — no backup needed.")
                self.diff_btn.hide()

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
```

---

#### RestoreDialog *(updated — per-backup diff button added)*

Each backup row now has a **diff icon button** alongside the existing trash/delete button. Clicking it fetches that backup's data from Convex and opens a `DiffDialog` comparing it against the current local config.

**Key changes from previous version:**
- Constructor takes `local_data=None` — pass your in-memory config here
- `_diff(backup_id)` fetches remote data and launches `DiffDialog`
- `DIFF` SVG icon rendered in yellow on each row

```python
class RestoreDialog(QDialog):
    """Shows list of backups and lets user pick one to restore or delete."""
    def __init__(self, backups, convex_call_fn, local_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RESTORE FROM BACKUP")
        self.setFixedWidth(550)
        self.selected_id = None
        self._convex_call = convex_call_fn
        self._backups = list(backups)
        self._local_data = local_data   # current local config for diff comparison
        self.setStyleSheet(
            f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_YELLOW}; }} "
            f"QLabel {{ color: {CP_TEXT}; }} "
            f"QPushButton {{ background: {CP_DIM}; color: white; padding: 6px 14px; border: 1px solid {CP_DIM}; }} "
            f"QPushButton:hover {{ border: 1px solid {CP_YELLOW}; }}"
        )
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(QLabel("Select a backup to restore:"))
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: 1px solid #3a3a3a;")
        self._scroll.setFixedHeight(300)
        self._layout.addWidget(self._scroll)
        cancel = QPushButton("CANCEL")
        cancel.clicked.connect(self.reject)
        self._layout.addWidget(cancel)
        self._render_list()

    def _render_list(self):
        import datetime
        inner = QWidget()
        inner.setStyleSheet(f"background: {CP_PANEL};")
        vbox = QVBoxLayout(inner)
        vbox.setSpacing(4)
        vbox.setContentsMargins(4, 4, 4, 4)
        for b in self._backups:
            dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M %p")
            row = QHBoxLayout()
            row.setSpacing(4)

            # Main restore button
            btn = QPushButton(f"  {dt}  ->  {b['label']}")
            btn.setStyleSheet(
                f"text-align: left; padding: 8px; background: {CP_BG}; color: {CP_TEXT}; "
                f"border: 1px solid #2a2a2a; font-family: 'Consolas'; font-size: 10pt; font-weight: bold;"
            )
            btn.clicked.connect(lambda checked, bid=b["id"]: self._select(bid))

            # Diff button (compare this backup with local config)
            diff_btn = QPushButton()
            diff_btn.setFixedSize(32, 32)
            diff_btn.setToolTip("Compare with local config")
            diff_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")
            renderer_diff = QSvgRenderer(QByteArray(SVGS["DIFF"].replace('currentColor', CP_YELLOW).encode()))
            pix_diff = QPixmap(22, 22)
            pix_diff.fill(Qt.GlobalColor.transparent)
            painter_diff = QPainter(pix_diff)
            renderer_diff.render(painter_diff)
            painter_diff.end()
            diff_btn.setIcon(QIcon(pix_diff))
            diff_btn.clicked.connect(lambda checked, bid=b["id"]: self._diff(bid))

            # Delete button
            del_btn = QPushButton()
            del_btn.setFixedSize(32, 32)
            del_btn.setToolTip("Delete this backup")
            del_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")
            renderer = QSvgRenderer(QByteArray(SVGS["TRASH"].replace('currentColor', CP_RED).encode()))
            pix = QPixmap(22, 22)
            pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pix)
            renderer.render(painter)
            painter.end()
            del_btn.setIcon(QIcon(pix))
            del_btn.clicked.connect(lambda checked, bid=b["id"]: self._delete(bid))

            row.addWidget(btn)
            row.addWidget(diff_btn)
            row.addWidget(del_btn)
            vbox.addLayout(row)
        vbox.addStretch()
        self._scroll.setWidget(inner)

    def _diff(self, backup_id):
        """Fetch backup and show DiffDialog against local config."""
        try:
            data = self._convex_call(
                "query", {"path": "functions:get", "args": {"id": backup_id}}
            ).get("value")
            if data and self._local_data:
                DiffDialog(self._local_data, data, parent=self).exec()
        except Exception as e:
            QMessageBox.critical(self, "DIFF FAILED", str(e))

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
```

---

### 4. Implementation Methods (Add to MainWindow)

```python
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
    label, ok = ConvexLabelDialog.get_label(self, convex_call_fn=self._convex_call, config_data=self.items)
    if not ok or not label.strip(): return

    backup_data = self.items  # or self.config — whatever your data structure is
    try:
        self._convex_call("mutation", {
            "path": "functions:save",
            "args": {"scriptName": SCRIPT_NAME, "label": label.strip(), "data": backup_data}
        })
        QMessageBox.information(self, "BACKUP", f'Config backed up: "{label.strip()}"')
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

        # Pass local_data so RestoreDialog can offer per-backup diff
        dlg = RestoreDialog(backups, self._convex_call, local_data=self.items, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_id:
            data = self._convex_call("query", {
                "path": "functions:get",
                "args": {"id": dlg.selected_id}
            }).get("value")

            if data:
                self.items = self._fix_floats(data)
                self.save_items()    # write to disk
                self.populate_lists()  # refresh UI
                QMessageBox.information(self, "RESTORE", "Restored successfully.")
    except Exception as e:
        QMessageBox.critical(self, "RESTORE FAILED", str(e))
```

---

### 5. UI Buttons

```python
# Backup button (Cyan Upload)
self.backup_btn = CyberButton("", color=CP_CYAN, is_outlined=True, svg_data=SVGS["UPLOAD"])
self.backup_btn.setToolTip("Backup to Cloud")
self.backup_btn.setFixedWidth(42)
self.backup_btn.clicked.connect(self.backup_to_convex)

# Restore button (Yellow Download)
self.restore_btn = CyberButton("", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["DOWNLOAD"])
self.restore_btn.setToolTip("Restore from Cloud")
self.restore_btn.setFixedWidth(42)
self.restore_btn.clicked.connect(self.restore_from_convex)
```

---

## Notes

- Convex stores numbers as floats; use `_fix_floats` before loading into PyQt.
- `SCRIPT_NAME` must be unique across all projects using this shared Convex URL.
- **Reserved Fields**: Fields starting with `$` (like `$schema`) are RESERVED by Convex and must be removed before saving.
- **Time Format**: Use 12-hour format (`%I:%M %p`) and `->` separator in the Restore dialog list for consistency.
- Backups are immutable (full history), but individual versions can be deleted via the Trash icon in the Restore dialog.
- **`config_data` type**: In list-based projects (e.g. startup manager), pass `self.items` (a `list`). In dict-based projects (e.g. komorebi), pass `self.config` (a `dict`). Both work with `DiffDialog` since it uses `json.dumps` for comparison.

---

## Diff Feature Overview

The diff system has two entry points:

| Where | How to trigger | What it compares |
|---|---|---|
| **ConvexLabelDialog** | Click CHECK → then SHOW DIFF (appears only when out-of-sync) | Local current data vs latest backup |
| **RestoreDialog** | Click the `<>` diff icon on any backup row | Local current data vs that specific backup |

Both open `DiffDialog`, which uses `difflib.unified_diff` on the JSON-serialized, normalized forms of both datasets. Color scheme matches GitHub's dark diff view.

---

## Sort UI (Reference — list-based projects)

A sort combo and order button sit in the toolbar. Two sort fields, two directions:

| Field | Direction | Behavior |
|---|---|---|
| Name | ASC | A → Z by item name |
| Name | DESC | Z → A by item name |
| Date | ASC | Oldest `added_at` first |
| Date | DESC | Newest `added_at` first |

```python
# In setup_ui:
self.sort_combo = QComboBox()
self.sort_combo.addItems(["Name", "Date"])
self.sort_combo.currentTextChanged.connect(self.change_sort)

self.order_btn = CyberButton(self.sort_order, color=CP_CYAN, is_outlined=True)
self.order_btn.clicked.connect(self.toggle_sort_order)

# Sorting logic in populate_lists:
sorted_items = sorted(
    self.items,
    key=lambda x: x["name"].lower() if self.sort_by == "Name" else x.get("added_at", 0),
    reverse=(self.sort_order == "DESC")
)
```
