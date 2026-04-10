import sys
import os
import json
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup,
    QGroupBox, QGridLayout, QListWidget, QScrollArea, QDialog, QFormLayout, QSpinBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEvent

# ── PALETTE ──────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

GLOBAL_QSS = f"""
QMainWindow, QDialog, QWidget {{
    background-color: {CP_BG};
    color: {CP_TEXT};
    font-family: 'Consolas';
    font-size: 10pt;
}}
QGroupBox {{
    border: 1px solid {CP_DIM};
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: {CP_YELLOW};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
}}
QLineEdit {{
    background-color: {CP_PANEL};
    color: {CP_CYAN};
    border: 1px solid {CP_DIM};
    padding: 4px;
    selection-background-color: {CP_CYAN};
    selection-color: #000000;
}}
QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM};
    border: 1px solid {CP_DIM};
    color: white;
    padding: 6px 12px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: #2a2a2a;
    border: 1px solid {CP_YELLOW};
    color: {CP_YELLOW};
}}
QPushButton:pressed {{
    background-color: {CP_YELLOW};
    color: black;
}}
QListWidget {{
    background-color: {CP_PANEL};
    color: {CP_CYAN};
    border: 1px solid {CP_DIM};
}}
QListWidget::item:hover {{ background-color: #1a1a1a; }}
QListWidget::item:selected {{
    background-color: {CP_CYAN};
    color: #000000;
}}
QRadioButton {{
    color: {CP_YELLOW};
    spacing: 6px;
}}
QRadioButton::indicator {{
    width: 12px; height: 12px;
    border: 1px solid {CP_DIM};
    border-radius: 6px;
    background: {CP_PANEL};
}}
QRadioButton::indicator:checked {{
    background: {CP_YELLOW};
    border-color: {CP_YELLOW};
}}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{
    background: {CP_BG}; width: 8px;
}}
QScrollBar::handle:vertical {{
    background: {CP_DIM}; min-height: 20px;
}}
"""

# ── BROWSER DIALOG ──────────────────────────────────────────────────────────
class BrowserDialog(QDialog):
    def __init__(self, parent, start_path):
        super().__init__(parent)
        self.setWindowTitle(f"Browsing: {start_path}")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(parent.styleSheet())
        
        self.current_path = start_path
        self.selected_path = None
        self._all_items = []
        
        layout = QVBoxLayout(self)
        
        # Search Box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter current view...")
        self.search_input.textChanged.connect(self._filter_list)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # List View
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self.list_widget)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("SELECT CURRENT FOLDER")
        self.select_btn.clicked.connect(self._select_current)
        
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.select_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self._fetch_content(self.current_path)

    def _fetch_content(self, path):
        self.setWindowTitle(f"Browsing: {path}")
        self.current_path = path
        self.list_widget.clear()
        self.list_widget.addItem("Loading...")
        
        self._fetcher = FolderFetcher(path)
        self._fetcher.done.connect(self._populate)
        self._fetcher.start()

    def _populate(self, items):
        self.list_widget.clear()
        # We store the raw items (with trailing slashes for folders)
        self._all_items = items
        self._filter_list(self.search_input.text())

    def _filter_list(self, text):
        self.list_widget.clear()
        search = text.lower()
        
        # Re-fetch the folders vs files logic to ensure folders stay top
        dirs = []
        files = []
        
        for full_path in self._all_items:
            # item from fetcher is full path. We show just the tail.
            name = full_path.split("/")[-1] or full_path.split("/")[-2]
            if search and search not in name.lower():
                continue
                
            if full_path.endswith("/"):
                dirs.append(full_path)
            else:
                files.append(full_path)
        
        for d in dirs:
            item = QListWidget().addItem("") # placeholder to get correct type
            item = self.list_widget.addItem(f"📁 {d.split('/')[-2]}/")
            self.list_widget.item(self.list_widget.count()-1).setData(Qt.ItemDataRole.UserRole, d)
            
        for f in files:
            self.list_widget.addItem(f"📄 {f.split('/')[-1]}")
            self.list_widget.item(self.list_widget.count()-1).setData(Qt.ItemDataRole.UserRole, f)

    def _on_double_click(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path.endswith("/"):
            self._fetch_content(path)
        else:
            self.selected_path = path
            self.accept()

    def _select_current(self):
        self.selected_path = self.current_path
        self.accept()

# ── FOLDER FETCH THREAD ───────────────────────────────────────────────────────
class FolderFetcher(QThread):
    done = pyqtSignal(list)

    def __init__(self, path):
        super().__init__()
        self.path = path.rstrip("/") + "/"
        self._procs = []

    def run(self):
        try:
            # Use lsf for spaces. We KEEP the trailing slash for folders
            # so the dialog knows how to navigate.
            p = subprocess.Popen(
                ["rclone", "lsf", "--max-depth", "1", "--format", "p", "--drive-acknowledge-abuse", self.path],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )
            self._procs = [p]
            
            out, _ = p.communicate(timeout=15)
            lines = out.decode("utf-8", errors="replace").splitlines()

            items = []
            for line in lines:
                name = line.strip()
                if not name: continue
                # full path with slash if it's a directory
                items.append(self.path + name)

            self.done.emit(items)
        except Exception:
            self.done.emit([])

    def stop(self):
        for p in self._procs:
            try: p.kill()
            except: pass
        self.wait(100)


# ── PATH INPUT WITH TAB-TRIGGERED POPUP ──────────────────────────────────────
class PathInput(QLineEdit):
    STORAGE_PREFIXES = [
        "C:/", "D:/",
        "cgu:/", "gu:/", "g00:/",
        "g01:/", "g02:/", "g03:/", "g04:/", "g05:/",
        "g06:/", "g07:/", "g08:/", "g09:/", "g10:/",
        "g11:/", "g12:/", "g13:/", "g14:/", "g15:/",
        "o0:/", "ouk:/", "m0:/", "m1:/",
    ]

    def __init__(self, placeholder=""):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setMinimumWidth(420)

    def _matching_prefix(self, text):
        for p in self.STORAGE_PREFIXES:
            if text.lower().startswith(p.lower()):
                return p
        return None

    def event(self, e):
        # Intercept Tab key before focus navigation takes it
        if e.type() == QEvent.Type.KeyPress and e.key() == Qt.Key.Key_Tab:
            path = self.text().strip()
            if path:
                # Ensure path ends in slash for rclone if it looks like a remote/dir
                if ":" in path and not path.endswith("/"):
                    path += "/"
                
                dlg = BrowserDialog(self.window(), path)
                if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_path:
                    self.setText(dlg.selected_path)
                return True # Mark event as handled to prevent focus skip
        
        return super().event(e)

    def keyPressEvent(self, e):
        # We handle Tab in event(), so just call super for others
        super().keyPressEvent(e)


# ── TOGGLE LABEL (flag chip) ──────────────────────────────────────────────────
class ToggleLabel(QLabel):
    def __init__(self, text, active=False, on_change=None):
        super().__init__(text)
        self.active = active
        self._on_change = on_change
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(190)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh()

    def _refresh(self):
        bg = "#90ee90" if self.active else "#ff9999"  # light green / light red
        self.setStyleSheet(f"background:{bg}; color:#000; font-weight:bold; padding:4px; font-family:Consolas;")

    def mousePressEvent(self, _):
        self.active = not self.active
        self._refresh()
        if self._on_change:
            self._on_change()


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────
class RcloneApp(QMainWindow):
    SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

    def _load_settings(self):
        try:
            with open(self.SETTINGS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_toggles(self):
        cfg = self._load_settings()
        cfg["flags"]   = [lbl.active for lbl in self.flag_labels]
        cfg["filters"] = [lbl.active for lbl in self.filter_labels]
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(cfg, f)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rclone + WinFSP")
        self.setStyleSheet(GLOBAL_QSS)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        root = QVBoxLayout(container)
        root.setSpacing(8)
        root.setContentsMargins(12, 12, 12, 12)

        # Two-column layout
        outer = QHBoxLayout()
        outer.setSpacing(10)
        root.addLayout(outer)

        # ── LEFT COLUMN ───────────────────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(8)

        # ── Command ──────────────────────────────────────────────────────────
        cmd_group = QGroupBox("COMMAND")
        cmd_layout = QHBoxLayout(cmd_group)
        self.cmd_group_btn = QButtonGroup(self)
        for val in ["ls", "copy", "sync", "tree", "ncdu", "size", "mount", "rcd", "about"]:
            rb = QRadioButton(val)
            if val == "ls":
                rb.setChecked(True)
            self.cmd_group_btn.addButton(rb)
            cmd_layout.addWidget(rb)
        cmd_layout.addStretch()
        left.addWidget(cmd_group)

        # ── Storage ───────────────────────────────────────────────────────────
        stor_group = QGroupBox("STORAGE")
        stor_grid = QGridLayout(stor_group)
        stor_grid.setSpacing(2)
        self.storage_btn_group = QButtonGroup(self)
        storage_radios = [
            ("N/A",  "",      0, 0), ("C:/",  "C:/",  0, 1), ("D:/",  "D:/",  0, 2),
            ("cgu:/","cgu:/", 1, 0), ("gu:/", "gu:/", 1, 1), ("g00:/","g00:/",1, 2),
            ("g01:/","g01:/", 2, 0), ("g02:/","g02:/",2, 1), ("g03:/","g03:/",2, 2),
            ("g04:/","g04:/", 2, 3), ("g05:/","g05:/",2, 4),
            ("g06:/","g06:/", 3, 0), ("g07:/","g07:/",3, 1), ("g08:/","g08:/",3, 2),
            ("g09:/","g09:/", 3, 3), ("g10:/","g10:/",3, 4),
            ("g11:/","g11:/", 4, 0), ("g12:/","g12:/",4, 1), ("g13:/","g13:/",4, 2),
            ("g14:/","g14:/", 4, 3), ("g15:/","g15:/",4, 4),
            ("o0:/", "o0:/",  5, 0), ("ouk:/","ouk:/",5, 1),
            ("m0:/", "m0:/",  6, 0), ("m1:/", "m1:/", 6, 1),
        ]
        for text, val, r, c in storage_radios:
            rb = QRadioButton(text)
            rb.setProperty("rclone_val", val)
            if val == "":
                rb.setChecked(True)
            self.storage_btn_group.addButton(rb)
            stor_grid.addWidget(rb, r, c)
        left.addWidget(stor_group)

        # ── From / To ─────────────────────────────────────────────────────────
        ft_group = QGroupBox("FROM / TO")
        ft_layout = QGridLayout(ft_group)
        ft_layout.addWidget(QLabel("From:"), 0, 0)
        self.from_input = PathInput("type storage prefix e.g. gu:/")
        ft_layout.addWidget(self.from_input, 0, 1)
        ft_layout.addWidget(QLabel("To:"), 1, 0)
        self.to_input = PathInput("type storage prefix e.g. o0:/")
        ft_layout.addWidget(self.to_input, 1, 1)
        left.addWidget(ft_group)

        # ── Main Flags ────────────────────────────────────────────────────────
        flags_group = QGroupBox("FLAGS")
        flags_grid = QGridLayout(flags_group)
        flags_grid.setSpacing(4)
        self.flag_labels = []
        flag_defs = [
            ("Fast List",               "--fast-list",                      True),
            ("Readable",                "--human-readable",                  True),
            ("Acknowledge Abuse",       "--drive-acknowledge-abuse",         True),
            ("Progress",                "-P",                                True),
            ("Dry Run",                 "--dry-run",                         False),
            ("Web Gui **Rcd",           "--rc-web-gui",                      False),
            ("vfs-cache",               "--vfs-cache-mode writes",           False),
            ("Verbose Lengthy",         "-vv",                               False),
            ("Verbose Minimal",         "-v",                                False),
            ("Log Level",               "--log-level ERROR",                 False),
            ("Stats Oneline",           "--stats-one-line",                  False),
            ("Trashed Only",            "--drive-trashed-only",              False),
            ("Shared With Me",          "--drive-shared-with-me",            False),
            ("Skip Dangling Shortcuts", "--drive-skip-dangling-shortcuts",   False),
            ("Skip Shortcuts",          "--drive-skip-shortcuts",            False),
            ("Date **tree",             "-D",                                False),
            ("Modified Time **tree",    "-t",                                False),
        ]
        self.flag_defs = flag_defs
        saved_flags = self._load_settings().get("flags", [])
        cols = 3
        for i, (name, _, active) in enumerate(flag_defs):
            state = saved_flags[i] if i < len(saved_flags) else active
            lbl = ToggleLabel(name, state, on_change=self._save_toggles)
            self.flag_labels.append(lbl)
            flags_grid.addWidget(lbl, i // cols, i % cols)
        left.addWidget(flags_group)

        left.addStretch()
        outer.addLayout(left, stretch=3)

        # ── RIGHT COLUMN ──────────────────────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(8)

        # ── Filter Flags ──────────────────────────────────────────────────────
        filter_group = QGroupBox("FILTERS")
        filter_grid = QGridLayout(filter_group)
        filter_grid.setColumnStretch(1, 1)
        filter_defs = [
            ("Transfers", "--transfers", "4"),
            ("Include",   "--include",   "*.jpg"),
            ("Exclude",   "--exclude",   "*.jpg"),
            ("Max Age",   "--max-age",   "1d"),
            ("Min Age",   "--min-age",   "1d"),
            ("Max Size",  "--max-size",  "100M"),
            ("Min Size",  "--min-size",  "100M"),
        ]
        self.filter_defs = filter_defs
        self.filter_labels = []
        self.filter_entries = []
        saved_filters = self._load_settings().get("filters", [])
        for i, (name, _, default) in enumerate(filter_defs):
            state = saved_filters[i] if i < len(saved_filters) else False
            lbl = ToggleLabel(name, state, on_change=self._save_toggles)
            entry = QLineEdit(default)
            self.filter_labels.append(lbl)
            self.filter_entries.append(entry)
            filter_grid.addWidget(lbl,   i, 0)
            filter_grid.addWidget(entry, i, 1)
        right.addWidget(filter_group)

        # ── Grep ──────────────────────────────────────────────────────────────
        grep_group = QGroupBox("GREP")
        grep_layout = QHBoxLayout(grep_group)
        grep_layout.addWidget(QLabel("Grep Text:"))
        self.grep_entry = QLineEdit()
        grep_layout.addWidget(self.grep_entry)
        right.addWidget(grep_group)

        right.addStretch()
        outer.addLayout(right, stretch=3)

        btn_row = QHBoxLayout()
        exec_btn = QPushButton("▶  EXECUTE")
        exec_btn.setStyleSheet(f"background:{CP_CYAN}; color:#000; font-weight:bold; padding:8px 20px; border:none;")
        exec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exec_btn.clicked.connect(self.execute_command)

        clear_btn = QPushButton("CLEAR")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(lambda: subprocess.run("cls", shell=True))

        restart_btn = QPushButton("↺  RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self.restart)

        settings_btn = QPushButton("⚙  SETTINGS")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.open_settings)

        btn_row.addWidget(exec_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(restart_btn)
        btn_row.addWidget(settings_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

    def _selected_storage(self):
        btn = self.storage_btn_group.checkedButton()
        return btn.property("rclone_val") if btn else ""

    def _selected_command(self):
        btn = self.cmd_group_btn.checkedButton()
        return btn.text() if btn else "ls"

    def execute_command(self):
        cmd   = self._selected_command()
        stor  = self._selected_storage()
        frm   = self.from_input.text().strip()
        to    = self.to_input.text().strip()

        parts = ["rclone", cmd, stor, frm, to]
        if cmd == "mount":
            parts.append(f"c:/{stor.strip(':/')}/")

        for i, (_, flag, _) in enumerate(self.flag_defs):
            if self.flag_labels[i].active:
                parts.append(flag)

        for i, (_, prefix, _) in enumerate(self.filter_defs):
            if self.filter_labels[i].active:
                parts.append(f"{prefix}={self.filter_entries[i].text()}")

        grep = self.grep_entry.text().strip()
        if grep:
            parts.append(f"| grep -i {grep}")

        final = " ".join(p for p in parts if p)
        print("Executing:", final)

        # Escape special characters for the echo command to prevent them from being interpreted as pipes/redirects
        echo_safe_final = final.replace("|", "^|").replace("&", "^&").replace(">", "^>").replace("<", "^<")
        completion_cmd = 'powershell -NoProfile -Command "Write-Host \' COMPLETE \' -ForegroundColor Black -BackgroundColor Green"'
        
        # Use '&' to ensure completion message shows even if the command fails or is interrupted
        cmd_str = f'echo Command: {echo_safe_final} & {final} & {completion_cmd}'
        subprocess.Popen(f'start cmd /k "{cmd_str}"', shell=True)

    def restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setStyleSheet(parent.styleSheet())
        layout = QVBoxLayout(self)

        form = QFormLayout()
        cfg = parent._load_settings()

        self.w_spin = QSpinBox()
        self.w_spin.setRange(400, 3840)
        self.w_spin.setValue(cfg.get("width", 900))
        self.w_spin.setStyleSheet(f"background:{CP_PANEL}; color:{CP_CYAN}; border:1px solid {CP_DIM}; padding:4px;")

        self.h_spin = QSpinBox()
        self.h_spin.setRange(300, 2160)
        self.h_spin.setValue(cfg.get("height", 800))
        self.h_spin.setStyleSheet(f"background:{CP_PANEL}; color:{CP_CYAN}; border:1px solid {CP_DIM}; padding:4px;")

        form.addRow("Width:", self.w_spin)
        form.addRow("Height:", self.h_spin)
        layout.addLayout(form)

        save_btn = QPushButton("SAVE")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

    def _save(self):
        p = self.parent()
        cfg = p._load_settings()
        cfg["width"]  = self.w_spin.value()
        cfg["height"] = self.h_spin.value()
        with open(p.SETTINGS_FILE, "w") as f:
            json.dump(cfg, f)
        p.resize(cfg["width"], cfg["height"])
        self.accept()


if __name__ == "__main__":
    os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false"
    app = QApplication(sys.argv)
    win = RcloneApp()
    cfg_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
    try:
        with open(cfg_file) as f:
            cfg = json.load(f)
        win.resize(cfg.get("width", 900), cfg.get("height", 800))
    except Exception:
        win.resize(900, 800)
    win.show()
    sys.exit(app.exec())
