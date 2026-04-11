# Convex Config Backup — Integration Guide (Unified Manager)

Add cloud backup/restore (with full version history and unified sync management) to any Python PyQt script using Convex.

---

## Convex Project

One shared Convex project handles all your scripts. Located at:

C:\@delta\ms1\convex_config_backup\

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
from functools import partial
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
                            QLineEdit, QPushButton, QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, QByteArray, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from PyQt6.QtSvg import QSvgRenderer
```

### 2. Constants & SVGs
```python
CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "your_unique_script_name"

# SVG Collection (Cyberpunk Style)
SVGS = {
    "UPLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',        
    "DOWNLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',   
    "TRASH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2-0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
    "DIFF": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
    "CLOUD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>'
}
```

### 3. UI Components

#### ConvexButton (SVG + Hover Support)
```python
class ConvexButton(QPushButton):
    """Modern button with SVG icon support and dynamic hover color-switching."""
    def __init__(self, text="", parent=None, color="#FCEE0A", is_outlined=False, svg_data=None):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.svg_data = svg_data
        self.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        if svg_data:
            self.update_icon(self.color if self.is_outlined else "#050505")
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
        if self.svg_data: self.update_icon("#050505" if self.is_outlined else self.color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.svg_data: self.update_icon(self.color if self.is_outlined else "#050505")
        super().leaveEvent(event)

    def update_style(self):
        if self.is_outlined:
            self.setStyleSheet(f"QPushButton {{ background-color: transparent; color: {self.color}; border: 2px solid {self.color}; padding: 5px 15px; }} QPushButton:hover {{ background-color: {self.color}; color: #050505; }}")
        else:
            self.setStyleSheet(f"QPushButton {{ background-color: {self.color}; color: #050505; border: none; padding: 5px 15px; }} QPushButton:hover {{ background-color: #050505; color: {self.color}; border: 1px solid {self.color}; }}")
```

#### DiffDialog
```python
class DiffDialog(QDialog):
    """GitHub-style color-coded comparison view."""
    def __init__(self, local_data, remote_data, title="SYSTEM // DIFF_VIEW", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 700)
        self.setStyleSheet("QDialog { background-color: #050505; border: 2px solid #00F0FF; }")
        layout = QVBoxLayout(self)
        header = QLabel("COMPARISON: REMOTE (RED) vs LOCAL (GREEN)")
        header.setStyleSheet("color: #FCEE0A; font-family: Consolas; font-weight: bold;")
        layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        content = QWidget()
        vbox = QVBoxLayout(content)
        vbox.setSpacing(0)

        def fix(obj):
            if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
            if isinstance(obj, list): return [fix(i) for i in obj]
            if isinstance(obj, float) and obj.is_integer(): return int(obj)
            return obj

        l_str = json.dumps(fix(local_data), indent=2, sort_keys=True).splitlines()
        r_str = json.dumps(fix(remote_data), indent=2, sort_keys=True).splitlines()
        diff = list(difflib.unified_diff(r_str, l_str, fromfile='Backup', tofile='Local', lineterm=''))

        if not diff:
            vbox.addWidget(QLabel("No differences detected."))
        else:
            for line in diff:
                lbl = QLabel(line)
                lbl.setFont(QFont("Consolas", 9))
                if line.startswith('+'): lbl.setStyleSheet("background-color: #12261e; color: #3fb950;")
                elif line.startswith('-'): lbl.setStyleSheet("background-color: #2c1619; color: #f85149;")
                else: lbl.setStyleSheet("color: #E0E0E0;")
                vbox.addWidget(lbl)
        
        vbox.addStretch()
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)
        close = ConvexButton("CLOSE", color="#3a3a3a", is_outlined=True)
        close.clicked.connect(self.accept)
        layout.addWidget(close)
```

#### CloudSyncDialog (Unified Manager)
```python
class CloudSyncDialog(QDialog):
    """Unified Cloud Sync Manager: Backup and Restore in one interface."""
    def __init__(self, convex_call_fn, config_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CLOUD // SYNC MANAGER")
        self.resize(550, 750)
        self._convex_call = convex_call_fn
        self._config_data = config_data
        self._backups = []
        self._remote_data = None
        self.selected_id = None
        
        self.setStyleSheet("QDialog { background-color: #050505; border: 2px solid #00F0FF; } QLabel { color: #E0E0E0; font-family: Consolas; } QLineEdit { background: #111111; color: #00F0FF; border: 1px solid #3a3a3a; padding: 8px; font-family: Consolas; } QGroupBox { color: #FCEE0A; font-weight: bold; border: 1px solid #3a3a3a; margin-top: 10px; padding-top: 15px; }")
        
        layout = QVBoxLayout(self)
        grp_new = QGroupBox("CREATE NEW BACKUP")
        new_lay = QVBoxLayout(grp_new)
        self.inp_label = QLineEdit()
        self.inp_label.setPlaceholderText("Enter backup label...")
        new_lay.addWidget(self.inp_label)
        self.status_lbl = QLabel("Ready to sync.")
        new_lay.addWidget(self.status_lbl)
        
        btn_row = QHBoxLayout()
        self.btn_backup = ConvexButton("UPLOAD", color="#00F0FF", svg_data=SVGS["UPLOAD"])
        self.btn_backup.clicked.connect(self._do_backup)
        self.btn_check = ConvexButton("CHECK", color="#FCEE0A", is_outlined=True)
        self.btn_check.clicked.connect(self._check_sync)
        btn_row.addWidget(self.btn_backup); btn_row.addWidget(self.btn_check)
        new_lay.addLayout(btn_row)
        layout.addWidget(grp_new)
        
        layout.addWidget(QLabel("CLOUD BACKUP HISTORY:"))
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)
        
        QTimer.singleShot(10, self._fetch_and_render)

    def _fetch_and_render(self):
        result = self._convex_call("query", {"path": "functions:list", "args": {"scriptName": SCRIPT_NAME}})
        self._backups = result.get("value", [])
        self._render_list()

    def _render_list(self):
        import datetime
        inner = QWidget(); vbox = QVBoxLayout(inner)
        for b in sorted(self._backups, key=lambda x: x["createdAt"], reverse=True):
            dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M %p")
            row = QHBoxLayout()
            btn = QPushButton(f"  {dt}  ->  {b['label']}")
            btn.setStyleSheet("text-align: left; padding: 8px; background: #050505; color: #E0E0E0; border: 1px solid #2a2a2a; font-family: Consolas;")
            btn.clicked.connect(lambda checked, bid=b["id"]: self._select_restore(bid))
            
            diff_btn = QPushButton()
            diff_btn.setFixedSize(32, 32)
            renderer_diff = QSvgRenderer(QByteArray(SVGS["DIFF"].replace('currentColor', "#FCEE0A").encode()))
            pix_diff = QPixmap(20, 20); pix_diff.fill(Qt.GlobalColor.transparent)
            painter_diff = QPainter(pix_diff); renderer_diff.render(painter_diff); painter_diff.end()
            diff_btn.setIcon(QIcon(pix_diff)); diff_btn.clicked.connect(lambda checked, bid=b["id"], lbl=b["label"]: self._show_list_diff(bid, lbl))
            
            row.addWidget(btn); row.addWidget(diff_btn)
            vbox.addLayout(row)
        vbox.addStretch(); self.scroll.setWidget(inner)

    def _do_backup(self):
        label = self.inp_label.text().strip()
        if not label: return
        self._convex_call("mutation", {"path": "functions:save", "args": {"scriptName": SCRIPT_NAME, "label": label, "data": self._config_data}})
        self.inp_label.clear(); self._fetch_and_render()

    def _check_sync(self):
        # ... logic to compare config_data vs latest remote ...
        pass

    def _show_list_diff(self, bid, label):
        remote = self._convex_call("query", {"path": "functions:get", "args": {"id": bid}}).get("value", {})
        DiffDialog(self._config_data, remote, title=f"DIFF // {label}", parent=self).exec()

    def _select_restore(self, bid):
        self.selected_id = bid; self.accept()
```

### 4. Implementation (MainWindow)

```python
def open_cloud_sync(self):
    backup_data = self.config.copy()
    if "$schema" in backup_data: del backup_data["$schema"]
    
    dlg = CloudSyncDialog(self._convex_call, backup_data, self)
    if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_id:
        data = self._convex_call("query", {"path": "functions:get", "args": {"id": dlg.selected_id}}).get("value")
        if data:
            self.config = self._fix_floats(data)
            self.save_config()
            QMessageBox.information(self, "RESTORE", "Restored successfully.")
```

---

## Notes
- **Unified Button**: Use `SVGS["CLOUD"]` for the main entry point in the toolbar.
- **Git-Style Diff**: Use `difflib.unified_diff` to highlight changes before restoring.
- **Immuntability**: Backups are preserved by timestamp; history is shown newest first.
- **Validation**: Use the `CHECK` button to ensure you don't overwrite newer changes unintentionally.
