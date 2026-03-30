import sys
import os
import json
import subprocess

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup,
    QGroupBox, QGridLayout, QListWidget, QScrollArea, QDialog, QFormLayout, QSpinBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

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

# ── FOLDER FETCH THREAD ───────────────────────────────────────────────────────
class FolderFetcher(QThread):
    done = pyqtSignal(list)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self._procs = []

    def run(self):
        try:
            base = self.path.rstrip("/") + "/"
            p_dirs  = subprocess.Popen(["rclone", "lsd", self.path],
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            p_files = subprocess.Popen(["rclone", "lsf", "--max-depth", "1", "--files-only", self.path],
                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            self._procs = [p_dirs, p_files]
            
            dirs_out,  _ = p_dirs.communicate(timeout=15)
            files_out, _ = p_files.communicate(timeout=15)

            def parse(raw):
                return [base + line.split()[-1]
                        for line in raw.decode("utf-8", errors="replace").splitlines() if line.split()]

            self.done.emit(parse(dirs_out) + parse(files_out))
        except Exception:
            self.done.emit([])

    def stop(self):
        for p in self._procs:
            try: p.kill()
            except: pass
        self.wait(100)


# ── PATH INPUT WITH FLOATING DROPDOWN ────────────────────────────────────────
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
        self._fetcher = None
        self._all_items = []
        self._last_fetched_path = ""

        # Floating popup — no focus steal
        self._popup = QListWidget(None)
        self._popup.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
        )
        self._popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._popup.setStyleSheet(f"""
            QListWidget {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_CYAN};
                font-family: Consolas;
                font-size: 10pt;
            }}
            QListWidget::item:hover {{ background-color: #1a1a1a; }}
            QListWidget::item:selected {{ background-color: {CP_CYAN}; color: #000; }}
        """)
        self._popup.itemClicked.connect(self._on_item_clicked)

        self.textChanged.connect(self._on_text_changed)

    def _matching_prefix(self, text):
        for p in self.STORAGE_PREFIXES:
            if text.lower().startswith(p.lower()):
                return p
        return None

    def _on_text_changed(self, text):
        # Only show dropdown if a slash is present
        if "/" not in text:
            self._popup.hide()
            self._all_items = []
            self._last_fetched_path = ""
            return

        # Handle Folder Suggestions
        last_slash_idx = text.rfind("/")
        base_path = text[:last_slash_idx + 1]
        search_term = text[last_slash_idx + 1:]

        # Trigger fetch if we hit a new directory
        if text.endswith("/") and self._matching_prefix(text):
            if text != self._last_fetched_path:
                if self._fetcher and self._fetcher.isRunning():
                    try: self._fetcher.done.disconnect()
                    except: pass
                    self._fetcher.stop()
                self._fetcher = FolderFetcher(text)
                self._fetcher.done.connect(self._populate)
                self._fetcher.start()

        # Filter existing items if base_path matches our cache
        if self._all_items and base_path == self._last_fetched_path:
            matches = [item for item in self._all_items if search_term.lower() in item.lower()]
            if matches:
                self._update_popup(matches)
            else:
                self._popup.hide()
        elif not text.endswith("/") and not self._all_items:
             self._popup.hide()

    def _populate(self, folders):
        if not self._fetcher: return
        self._last_fetched_path = self._fetcher.path
        self._all_items = folders

        text = self.text()
        if "/" not in text:
            self._popup.hide()
            return

        last_slash_idx = text.rfind("/")
        search_term = text[last_slash_idx + 1:]

        matches = [item for item in self._all_items if search_term.lower() in item.lower()]
        if matches:
            self._update_popup(matches)
        else:
            self._popup.hide()

    def _update_popup(self, items):
        if not items or "/" not in self.text():
            self._popup.hide()
            return
        
        self._popup.clear()
        for i in items:
            self._popup.addItem(i)
        
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self._popup.move(pos)
        self._popup.setFixedWidth(self.width())
        row_h = self._popup.sizeHintForRow(0) + 2
        self._popup.setFixedHeight(min(len(items), 10) * row_h + 4)
        self._popup.show()

    def focusInEvent(self, e):
        super().focusInEvent(e)

    def _on_item_clicked(self, item):
        if not item: return
        path = item.text() # Capture text BEFORE setText, as setText can trigger clear()
        self.setText(path)
        if not path.endswith("/"):
            self._popup.hide()

    def keyPressEvent(self, e):
        key = e.key()
        if self._popup.isVisible():
            cur = self._popup.currentRow()
            count = self._popup.count()
            if key == Qt.Key.Key_Down:
                self._popup.setCurrentRow(min(cur + 1, count - 1))
                return
            if key == Qt.Key.Key_Up:
                self._popup.setCurrentRow(max(cur - 1, 0))
                return
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                item = self._popup.currentItem()
                if item:
                    self._on_item_clicked(item)
                return
            if key == Qt.Key.Key_Escape:
                self._popup.hide()
                return
        super().keyPressEvent(e)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._popup.setFixedWidth(self.width())


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
