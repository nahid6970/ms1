import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QScrollArea, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QMimeData, QUrl
from PyQt5.QtGui import QFont, QDrag

CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "md_launcher_config.json")

def load_config():
    default = {"md_folder": "C:/@delta/ms1/md", "window_width_percent": 0.4}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return {**default, **json.load(f)}
    except: pass
    return default

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

class MDRow(QWidget):
    clicked = pyqtSignal()

    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.setFixedHeight(36)
        self.setObjectName("row")
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)

        self.name_label = QLabel(self.file_name)
        self.name_label.setFont(QFont("Consolas", 9))
        self.name_label.setStyleSheet(f"background: transparent; color: {CP_TEXT};")

        layout.addWidget(self.name_label)
        layout.addStretch()

        self._set_style(False)

    def _set_style(self, selected):
        if selected:
            self.setStyleSheet(f"QWidget#row {{ background: #1a1a1a; border-left: 2px solid {CP_YELLOW}; }} QLabel {{ background: transparent; border: none; }}")
        else:
            self.setStyleSheet(f"QWidget#row {{ background: transparent; border-left: 2px solid transparent; }} QLabel {{ background: transparent; border: none; }}")

    def set_selected(self, selected):
        self._set_style(selected)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.pos()
            self.clicked.emit()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton): return
        if (event.pos() - self._drag_start).manhattanLength() < QApplication.startDragDistance(): return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(os.path.abspath(self.file_path))])
        drag.setMimeData(mime)
        drag.exec_(Qt.CopyAction)


class MDLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.block_close = False
        self.all_files = []
        self.rows = []
        self.current_idx = 0

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.win_w = int(screen.width() * self.config.get("window_width_percent", 0.4))
        self.setGeometry((screen.width() - self.win_w) // 2, 10, self.win_w, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"""
            background: {CP_BG};
            border: 1px solid {CP_DIM};
        """)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Search box
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search files...")
        self.search.setFont(QFont("Consolas", 10))
        self.search.setFixedHeight(36)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {CP_PANEL};
                color: {CP_CYAN};
                border: none;
                border-bottom: 1px solid {CP_DIM};
                padding: 0 12px;
            }}
            QLineEdit:focus {{ border-bottom: 1px solid {CP_CYAN}; }}
        """)
        self.search.textChanged.connect(self.filter_files)
        layout.addWidget(self.search)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 6px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 3px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
        """)

        self.list_widget = QWidget()
        self.list_widget.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()

        self.scroll.setWidget(self.list_widget)
        self.scroll.viewport().setStyleSheet(f"background: {CP_BG};")
        layout.addWidget(self.scroll)

        self.scan_files()

        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus)
        QTimer.singleShot(500, lambda: self.focus_timer.start(100))

    def scan_files(self):
        folder = self.config["md_folder"]
        os.makedirs(folder, exist_ok=True)
        self.all_files = []
        for root, _, files in os.walk(folder):
            for f in files:
                if f.endswith(".md"):
                    self.all_files.append(os.path.join(root, f))
        self.filter_files(self.search.text())

    def filter_files(self, query=""):
        # Clear rows
        for row in self.rows:
            row.setParent(None)
        self.rows = []

        q = query.lower()
        filtered = [p for p in self.all_files if q in os.path.basename(p).lower()]

        for i, path in enumerate(filtered):
            row = MDRow(path)
            row.clicked.connect(lambda idx=i: self.set_index(idx))
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)
            self.rows.append(row)

        self.current_idx = 0
        if self.rows:
            self.rows[0].set_selected(True)

        # Resize window height to fit rows (max 500px)
        h = 36 + min(len(self.rows), 12) * 36 + 4
        self.setFixedHeight(h)

    def set_index(self, idx):
        if not self.rows: return
        if 0 <= self.current_idx < len(self.rows):
            self.rows[self.current_idx].set_selected(False)
        self.current_idx = max(0, min(idx, len(self.rows) - 1))
        self.rows[self.current_idx].set_selected(True)

    def check_focus(self):
        if self.block_close: return
        if not self.isActiveWindow():
            self.close()

    def closeEvent(self, event):
        QApplication.quit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Down:
            self.set_index(self.current_idx + 1)
        elif event.key() == Qt.Key_Up:
            self.set_index(self.current_idx - 1)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.rows:
                path = self.rows[self.current_idx].file_path
                os.startfile(path)
                self.close()
        elif event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_O:
            self.change_folder()

    def change_folder(self):
        from PyQt5.QtWidgets import QFileDialog
        self.block_close = True
        folder = QFileDialog.getExistingDirectory(self, "Select MD Folder", self.config["md_folder"])
        self.block_close = False
        if folder:
            self.config["md_folder"] = folder
            save_config(self.config)
            self.scan_files()
        self.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("* { border: none; outline: none; }")
    launcher = MDLauncher()
    launcher.show()
    launcher.activateWindow()
    launcher.raise_()
    sys.exit(app.exec_())
