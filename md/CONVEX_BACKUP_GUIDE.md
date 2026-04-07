# Convex Config Backup — Integration Guide

Add cloud backup/restore (with full version history) to any Python PyQt script using Convex.

---

## Convex Project

One shared Convex project handles all your scripts. Located at:
`
C:\@delta\ms1\convex_config_backup\
`

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
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
`

### 2. Constants & Cyberpunk Theme
`python
CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "your_unique_script_name"

# Cyberpunk-style colors for Convex dialogs
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_GREEN = "#00ff21"
`

### 3. Dialog Classes

#### ConvexLabelDialog
`python
class ConvexLabelDialog(QDialog):
    """Simple dialog to get a backup label from the user."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("BACKUP LABEL")
        self.setFixedWidth(380)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }} QLabel {{ color: {CP_TEXT}; }} QLineEdit {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px; font-family: Consolas; }} QPushButton {{ background: {CP_DIM}; color: white; padding: 6px 14px; border: 1px solid {CP_DIM}; }} QPushButton:hover {{ border: 1px solid {CP_CYAN}; }}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter a label for this backup:"))
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("e.g. before v2 update")
        layout.addWidget(self.inp)
        btns = QHBoxLayout()
        ok = QPushButton("BACKUP")
        ok.setStyleSheet(f"background: {CP_CYAN}; color: black; font-weight: bold;")
        ok.clicked.connect(self.accept)
        cancel = QPushButton("CANCEL")
        cancel.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addWidget(cancel)
        layout.addLayout(btns)

    @staticmethod
    def get_label(parent=None):
        dlg = ConvexLabelDialog(parent)
        ok = dlg.exec() == QDialog.DialogCode.Accepted
        return dlg.inp.text(), ok
`

#### RestoreDialog
`python
class RestoreDialog(QDialog):
    """Shows list of backups and lets user pick one to restore or delete."""
    DEL_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#FF003C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>'''

    def __init__(self, backups, convex_call_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RESTORE FROM BACKUP")
        self.setFixedWidth(520)
        self.selected_id = None
        self._convex_call = convex_call_fn
        self._backups = list(backups)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_YELLOW}; }} QLabel {{ color: {CP_TEXT}; }} QPushButton {{ background: {CP_DIM}; color: white; padding: 6px 14px; border: 1px solid {CP_DIM}; }} QPushButton:hover {{ border: 1px solid {CP_YELLOW}; }}")
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
            dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %H:%M")
            row = QHBoxLayout()
            row.setSpacing(4)
            btn = QPushButton(f"  {dt}  —  {b['label']}")
            btn.setStyleSheet(f"text-align: left; padding: 8px; background: {CP_BG}; color: {CP_TEXT}; border: 1px solid #2a2a2a;")
            btn.clicked.connect(lambda checked, bid=b["id"]: self._select(bid))
            
            # Delete button with SVG icon
            del_btn = QPushButton()
            del_btn.setFixedSize(32, 32)
            del_btn.setToolTip("Delete this backup")
            del_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")
            
            renderer = QSvgRenderer(QByteArray(self.DEL_SVG.encode()))
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
    label, ok = ConvexLabelDialog.get_label(self)
    if not ok or not label.strip(): return
    
    # Adapt backup_data to your script's config structure
    backup_data = self.config 
    
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
# Backup button (Cyan ☁)
self.backup_btn = QPushButton("☁")
self.backup_btn.setToolTip("Backup to Cloud")
self.backup_btn.setStyleSheet(f"QPushButton {{ background-color: #1a3a5c; color: {CP_CYAN}; border: 1px solid {CP_CYAN}; }}")
self.backup_btn.clicked.connect(self.backup_to_convex)

# Restore button (Yellow ⬇)
self.restore_btn = QPushButton("⬇")
self.restore_btn.setToolTip("Restore from Cloud")
self.restore_btn.setStyleSheet(f"QPushButton {{ background-color: #1a3a5c; color: {CP_YELLOW}; border: 1px solid {CP_YELLOW}; }}")
self.restore_btn.clicked.connect(self.restore_from_convex)
`

---

## Notes
- Convex stores numbers as floats; use _fix_floats before loading into PyQt.
- SCRIPT_NAME must be unique across all projects using this shared Convex URL.
- Backups are immutable (full history), but individual versions can be deleted via the Trash icon in the Restore dialog.
