import sys, os, subprocess
import win32gui, win32process, win32con
import psutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QHeaderView, QAbstractItemView, QCheckBox, QSplitter, QTextEdit,
    QGroupBox, QFormLayout, QDialog, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# ── CYBERPUNK PALETTE ──────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"
CP_SUB    = "#808080"

THEME = f"""
QMainWindow, QDialog {{ background-color: {CP_BG}; }}
QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 9pt; background-color: {CP_BG}; }}
QLineEdit, QTextEdit {{
    background-color: {CP_PANEL}; color: {CP_CYAN};
    border: 1px solid {CP_DIM}; padding: 4px;
}}
QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM};
    color: white; padding: 5px 10px; font-weight: bold;
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QTableWidget {{
    background-color: {CP_PANEL}; color: {CP_TEXT};
    gridline-color: {CP_DIM}; border: 1px solid {CP_DIM};
    selection-background-color: #1a1a1a;
}}
QTableWidget::item:selected {{ background-color: #1c1c1c; color: {CP_CYAN}; }}
QHeaderView::section {{
    background-color: {CP_BG}; color: {CP_YELLOW};
    border: 1px solid {CP_DIM}; padding: 4px; font-weight: bold;
}}
QScrollBar:vertical {{
    background: {CP_BG}; width: 8px;
}}
QScrollBar::handle:vertical {{ background: {CP_DIM}; }}
QScrollBar::handle:vertical:hover {{ background: {CP_CYAN}; }}
QCheckBox {{ color: {CP_TEXT}; spacing: 6px; }}
QCheckBox::indicator {{
    width: 13px; height: 13px;
    border: 1px solid {CP_DIM}; background: {CP_PANEL};
}}
QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
QLabel {{ background-color: transparent; }}
QSplitter::handle {{ background: {CP_DIM}; }}
"""

# ── WINDOW ENUMERATION ─────────────────────────────────────────────────────────
def get_all_windows(include_hidden=True, include_no_title=True):
    results = []

    def callback(hwnd, _):
        try:
            title = win32gui.GetWindowText(hwnd)
            cls   = win32gui.GetClassName(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            rect  = win32gui.GetWindowRect(hwnd)
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

            if not include_hidden and not visible:
                return
            if not include_no_title and not title.strip():
                return

            # get PID → exe
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                proc = psutil.Process(pid)
                exe = proc.name()
                exe_path = proc.exe()
            except Exception:
                pid, exe, exe_path = 0, "N/A", "N/A"

            results.append({
                "hwnd":     hwnd,
                "title":    title or "(no title)",
                "class":    cls,
                "visible":  visible,
                "pid":      pid,
                "exe":      exe,
                "exe_path": exe_path,
                "rect":     rect,
                "style":    hex(style),
                "ex_style": hex(ex_style),
            })
        except Exception:
            pass

    win32gui.EnumWindows(callback, None)
    return results


# ── DETAIL DIALOG ──────────────────────────────────────────────────────────────
class DetailDialog(QDialog):
    def __init__(self, info: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Window Details — HWND {info['hwnd']}")
        self.resize(560, 420)
        layout = QVBoxLayout(self)

        txt = QTextEdit()
        txt.setReadOnly(True)
        lines = [
            f"HWND      : {info['hwnd']}",
            f"Title     : {info['title']}",
            f"Class     : {info['class']}",
            f"Visible   : {info['visible']}",
            f"PID       : {info['pid']}",
            f"EXE       : {info['exe']}",
            f"EXE Path  : {info['exe_path']}",
            f"Rect      : {info['rect']}",
            f"Style     : {info['style']}",
            f"ExStyle   : {info['ex_style']}",
        ]
        txt.setPlainText("\n".join(lines))
        layout.addWidget(txt)

        close_btn = QPushButton("CLOSE")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ── SETTINGS DIALOG ────────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        layout = QVBoxLayout(self)
        grp = QGroupBox("CUSTOMIZATION")
        form = QFormLayout()
        # placeholder — add settings here
        form.addRow(QLabel("(No settings configured yet)"))
        grp.setLayout(form)
        layout.addWidget(grp)
        layout.addStretch()
        close_btn = QPushButton("CLOSE")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ── MAIN WINDOW ────────────────────────────────────────────────────────────────
COLS = ["HWND", "Title", "Class", "Visible", "PID", "EXE"]

class WindowSpy(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Spy 411")
        self.resize(1100, 650)
        self._all_data = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── top bar ──
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Filter by title / class / exe ...")
        self.search.textChanged.connect(self._apply_filter)

        self.chk_hidden  = QCheckBox("Show Hidden")
        self.chk_hidden.setChecked(True)
        self.chk_notitle = QCheckBox("Show No-Title")
        self.chk_notitle.setChecked(True)

        btn_refresh  = QPushButton("⟳ REFRESH")
        btn_settings = QPushButton("⚙ SETTINGS")
        btn_restart  = QPushButton("↺ RESTART")

        btn_refresh.clicked.connect(self.refresh)
        btn_settings.clicked.connect(self._open_settings)
        btn_restart.clicked.connect(self._restart)

        top.addWidget(QLabel("FILTER:"))
        top.addWidget(self.search, 1)
        top.addWidget(self.chk_hidden)
        top.addWidget(self.chk_notitle)
        top.addWidget(btn_refresh)
        top.addWidget(btn_settings)
        top.addWidget(btn_restart)
        root.addLayout(top)

        # ── splitter: table | detail ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # table
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS))
        self.table.setHorizontalHeaderLabels(COLS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.doubleClicked.connect(self._show_detail)
        self.table.clicked.connect(self._on_row_click)
        splitter.addWidget(self.table)

        # detail panel
        detail_wrap = QGroupBox("DETAILS  (click row / double-click for full view)")
        dv = QVBoxLayout(detail_wrap)
        self.detail_txt = QTextEdit()
        self.detail_txt.setReadOnly(True)
        self.detail_txt.setMinimumWidth(280)
        dv.addWidget(self.detail_txt)
        splitter.addWidget(detail_wrap)
        splitter.setSizes([720, 380])

        root.addWidget(splitter, 1)

        # ── status bar ──
        self.status = QLabel("Ready.")
        self.status.setStyleSheet(f"color: {CP_SUB};")
        root.addWidget(self.status)

    # ── actions ──────────────────────────────────────────────────────────────
    def refresh(self):
        inc_hidden  = self.chk_hidden.isChecked()
        inc_notitle = self.chk_notitle.isChecked()
        self._all_data = get_all_windows(inc_hidden, inc_notitle)
        self._apply_filter()
        self.status.setText(f"Total windows found: {len(self._all_data)}")

    def _apply_filter(self):
        q = self.search.text().lower()
        filtered = [
            w for w in self._all_data
            if q in w["title"].lower() or q in w["class"].lower() or q in w["exe"].lower()
        ] if q else self._all_data

        self.table.setRowCount(len(filtered))
        for r, w in enumerate(filtered):
            vis_color = CP_GREEN if w["visible"] else CP_RED
            vals = [str(w["hwnd"]), w["title"], w["class"],
                    "YES" if w["visible"] else "NO", str(w["pid"]), w["exe"]]
            for c, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, w)
                if c == 3:  # visible column
                    item.setForeground(QColor(vis_color))
                self.table.setItem(r, c, item)

        self.status.setText(f"Showing {len(filtered)} / {len(self._all_data)} windows")

    def _on_row_click(self, idx):
        item = self.table.item(idx.row(), 0)
        if not item:
            return
        w = item.data(Qt.ItemDataRole.UserRole)
        lines = [
            f"HWND      : {w['hwnd']}",
            f"Title     : {w['title']}",
            f"Class     : {w['class']}",
            f"Visible   : {w['visible']}",
            f"PID       : {w['pid']}",
            f"EXE       : {w['exe']}",
            f"EXE Path  : {w['exe_path']}",
            f"Rect      : {w['rect']}",
            f"Style     : {w['style']}",
            f"ExStyle   : {w['ex_style']}",
        ]
        self.detail_txt.setPlainText("\n".join(lines))

    def _show_detail(self, idx):
        item = self.table.item(idx.row(), 0)
        if not item:
            return
        dlg = DetailDialog(item.data(Qt.ItemDataRole.UserRole), self)
        dlg.exec()

    def _open_settings(self):
        SettingsDialog(self).exec()

    def _restart(self):
        python = sys.executable
        os.execv(python, [python] + sys.argv)


# ── ENTRY ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME)
    win = WindowSpy()
    win.show()
    sys.exit(app.exec())
