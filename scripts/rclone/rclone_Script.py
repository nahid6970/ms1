import sys
import os
import subprocess
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup,
    QGroupBox, QGridLayout, QListWidget, QScrollArea,
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

    def run(self):
        try:
            base = self.path.rstrip("/") + "/"
            def parse(cmd):
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, encoding="utf-8", errors="replace")
                return [base + line.split()[-1] for line in r.stdout.splitlines() if line.split()]

            folders = parse(["rclone", "lsd",  "--max-depth", "1", self.path])
            files   = parse(["rclone", "lsf",  "--max-depth", "1", "--files-only", self.path])
            self.done.emit(folders + files)
        except Exception:
            self.done.emit([])


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

        # Floating popup
        self._popup = QListWidget(None)  # no parent = top-level window
        self._popup.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
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
        self._popup.hide()
        self._popup.clear()
        if self._fetcher and self._fetcher.isRunning():
            self._fetcher.terminate()
        if text.endswith("/") and self._matching_prefix(text):
            self._fetcher = FolderFetcher(text)
            self._fetcher.done.connect(self._populate)
            self._fetcher.start()

    def _populate(self, folders):
        self._popup.clear()
        if not folders:
            return
        for f in folders:
            self._popup.addItem(f)
        # Position popup directly below this widget
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self._popup.move(pos)
        self._popup.setFixedWidth(self.width())
        row_h = self._popup.sizeHintForRow(0) + 2
        self._popup.setFixedHeight(min(len(folders), 10) * row_h + 4)
        self._popup.show()

    def _on_item_clicked(self, item):
        self.setText(item.text())
        self._popup.hide()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._popup.setFixedWidth(self.width())


# ── TOGGLE LABEL (flag chip) ──────────────────────────────────────────────────
class ToggleLabel(QLabel):
    def __init__(self, text, active=False):
        super().__init__(text)
        self.active = active
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(190)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh()

    def _refresh(self):
        bg = CP_GREEN if self.active else CP_RED
        self.setStyleSheet(f"background:{bg}; color:#000; font-weight:bold; padding:4px; font-family:Consolas;")

    def mousePressEvent(self, _):
        self.active = not self.active
        self._refresh()


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────
class RcloneApp(QMainWindow):
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

        # ── Command ──────────────────────────────────────────────────────────
        cmd_group = QGroupBox("COMMAND")
        cmd_layout = QHBoxLayout(cmd_group)
        self.cmd_group_btn = QButtonGroup(self)
        for val in ["ls", "copy", "sync", "tree", "ncdu", "size", "mount", "rcd"]:
            rb = QRadioButton(val)
            if val == "ls":
                rb.setChecked(True)
            self.cmd_group_btn.addButton(rb)
            cmd_layout.addWidget(rb)
        cmd_layout.addStretch()
        root.addWidget(cmd_group)

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
        root.addWidget(stor_group)

        # ── From / To ─────────────────────────────────────────────────────────
        ft_group = QGroupBox("FROM / TO")
        ft_layout = QGridLayout(ft_group)
        ft_layout.addWidget(QLabel("From:"), 0, 0)
        self.from_input = PathInput("type storage prefix e.g. gu:/")
        ft_layout.addWidget(self.from_input, 0, 1)
        ft_layout.addWidget(QLabel("To:"), 1, 0)
        self.to_input = PathInput("type storage prefix e.g. o0:/")
        ft_layout.addWidget(self.to_input, 1, 1)
        root.addWidget(ft_group)

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
        cols = 4
        for i, (name, _, active) in enumerate(flag_defs):
            lbl = ToggleLabel(name, active)
            self.flag_labels.append(lbl)
            flags_grid.addWidget(lbl, i // cols, i % cols)
        root.addWidget(flags_group)

        # ── Filter Flags ──────────────────────────────────────────────────────
        filter_group = QGroupBox("FILTERS")
        filter_grid = QGridLayout(filter_group)
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
        for i, (name, _, default) in enumerate(filter_defs):
            lbl = ToggleLabel(name, False)
            entry = QLineEdit(default)
            entry.setFixedWidth(120)
            self.filter_labels.append(lbl)
            self.filter_entries.append(entry)
            filter_grid.addWidget(lbl,   i, 0)
            filter_grid.addWidget(entry, i, 1)
        root.addWidget(filter_group)

        # ── Grep ──────────────────────────────────────────────────────────────
        grep_group = QGroupBox("GREP")
        grep_layout = QHBoxLayout(grep_group)
        grep_layout.addWidget(QLabel("Grep Text:"))
        self.grep_entry = QLineEdit()
        self.grep_entry.setFixedWidth(240)
        grep_layout.addWidget(self.grep_entry)
        grep_layout.addStretch()
        root.addWidget(grep_group)

        # ── Buttons ───────────────────────────────────────────────────────────
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

        btn_row.addWidget(exec_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addWidget(restart_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)
        root.addStretch()

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

        def run():
            subprocess.Popen(final, shell=True).wait()
            print("\033[92mTask Completed\033[0m")

        threading.Thread(target=run, daemon=True).start()

    def restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = RcloneApp()
    win.resize(900, 800)
    win.show()
    sys.exit(app.exec())
