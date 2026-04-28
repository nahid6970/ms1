import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QScrollArea, QLineEdit, QPushButton, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QMimeData, QUrl
from PyQt5.QtGui import QFont, QDrag

CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "md_launcher_config.json")

def load_config():
    default = {"folders": ["C:/@delta/ms1/md"], "window_width_percent": 0.4}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                # migrate old single-folder config
                if "md_folder" in data and "folders" not in data:
                    data["folders"] = [data["md_folder"]]
                return {**default, **data}
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
        layout.setSpacing(0)

        self.name_label = QLabel(self.file_name)
        self.name_label.setFont(QFont("Consolas", 9))
        self.name_label.setStyleSheet(f"background: transparent; color: {CP_TEXT}; border: none;")

        layout.addWidget(self.name_label)
        layout.addStretch()
        self._set_style(False)

    def _set_style(self, selected):
        if selected:
            self.setStyleSheet(f"QWidget#row {{ background: #1a1a1a; border-left: 2px solid {CP_YELLOW}; }} QLabel {{ background: transparent; border: none; }}")
        else:
            self.setStyleSheet(f"QWidget#row {{ background: transparent; border-left: 2px solid transparent; }} QLabel {{ background: transparent; border: none; }}")

    def set_selected(self, s): self._set_style(s)

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


class SettingsPanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setObjectName("settings")
        self.setStyleSheet(f"QWidget#settings {{ background: {CP_PANEL}; border-top: 1px solid {CP_DIM}; }} QLabel {{ border: none; background: transparent; color: {CP_TEXT}; }}")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 6, 8, 6)
        self.layout.setSpacing(4)

        # Add folder button
        add_btn = QPushButton("+ Add Folder")
        add_btn.setFont(QFont("Consolas", 9))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {CP_CYAN}; border: none; text-align: left; padding: 2px 4px; }} QPushButton:hover {{ color: {CP_YELLOW}; }}")
        add_btn.clicked.connect(self.add_folder)
        self.layout.addWidget(add_btn)

        self.folder_list_layout = QVBoxLayout()
        self.folder_list_layout.setSpacing(2)
        self.layout.addLayout(self.folder_list_layout)

        self.refresh_list()

    def refresh_list(self):
        # Clear
        while self.folder_list_layout.count():
            w = self.folder_list_layout.takeAt(0).widget()
            if w: w.deleteLater()

        for folder in self.config.get("folders", []):
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(6)

            lbl = QLabel(folder)
            lbl.setFont(QFont("Consolas", 8))
            lbl.setStyleSheet(f"color: {CP_SUBTEXT}; border: none; background: transparent;")

            rm = QPushButton("✕")
            rm.setFixedSize(18, 18)
            rm.setCursor(Qt.PointingHandCursor)
            rm.setStyleSheet(f"QPushButton {{ background: transparent; color: {CP_DIM}; border: none; font-size: 10px; }} QPushButton:hover {{ color: {CP_RED}; }}")
            rm.clicked.connect(lambda _, f=folder: self.remove_folder(f))

            rl.addWidget(lbl, 1)
            rl.addWidget(rm)
            self.folder_list_layout.addWidget(row)

    def add_folder(self):
        parent_win = self.window()
        if hasattr(parent_win, 'block_close'): parent_win.block_close = True
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if hasattr(parent_win, 'block_close'): parent_win.block_close = False
        if folder:
            folder = folder.replace("\\", "/")
            if folder not in self.config["folders"]:
                self.config["folders"].append(folder)
                save_config(self.config)
                self.refresh_list()
                self.changed.emit()
        parent_win.activateWindow()

    def remove_folder(self, folder):
        if folder in self.config["folders"]:
            self.config["folders"].remove(folder)
            save_config(self.config)
            self.refresh_list()
            self.changed.emit()


CP_SUBTEXT = "#808080"

class MDLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.block_close = False
        self.all_files = []
        self.rows = []
        self.current_idx = 0
        self.settings_visible = False

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.win_w = int(screen.width() * self.config.get("window_width_percent", 0.4))
        self.setGeometry((screen.width() - self.win_w) // 2, 10, self.win_w, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setStyleSheet(f"background: {CP_BG}; border: 1px solid {CP_DIM};")

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Search row
        search_row = QWidget()
        search_row.setStyleSheet(f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};")
        sr_layout = QHBoxLayout(search_row)
        sr_layout.setContentsMargins(0, 0, 0, 0)
        sr_layout.setSpacing(0)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search files...")
        self.search.setFont(QFont("Consolas", 10))
        self.search.setFixedHeight(36)
        self.search.setStyleSheet(f"background: transparent; color: {CP_CYAN}; border: none; padding: 0 12px;")
        self.search.textChanged.connect(self.filter_files)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(36, 36)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {CP_DIM}; border: none; font-size: 14px; }} QPushButton:hover {{ color: {CP_YELLOW}; }}")
        self.settings_btn.clicked.connect(self.toggle_settings)

        sr_layout.addWidget(self.search)
        sr_layout.addWidget(self.settings_btn)
        main_layout.addWidget(search_row)

        # Settings panel (hidden by default)
        self.settings_panel = SettingsPanel(self.config)
        self.settings_panel.changed.connect(self.scan_files)
        self.settings_panel.setVisible(False)
        main_layout.addWidget(self.settings_panel)

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
        main_layout.addWidget(self.scroll)

        self.scan_files()

        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus)
        QTimer.singleShot(500, lambda: self.focus_timer.start(100))

    def toggle_settings(self):
        self.settings_visible = not self.settings_visible
        self.settings_panel.setVisible(self.settings_visible)
        self.settings_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {CP_YELLOW if self.settings_visible else CP_DIM}; border: none; font-size: 14px; }} QPushButton:hover {{ color: {CP_YELLOW}; }}"
        )
        self._resize()

    def scan_files(self):
        self.all_files = []
        for folder in self.config.get("folders", []):
            os.makedirs(folder, exist_ok=True)
            for root, _, files in os.walk(folder):
                for f in files:
                    if f.endswith(".md"):
                        self.all_files.append(os.path.join(root, f))
        self.filter_files(self.search.text())

    def filter_files(self, query=""):
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

        self._resize()

    def _resize(self):
        settings_h = self.settings_panel.sizeHint().height() if self.settings_visible else 0
        h = 36 + settings_h + min(len(self.rows), 12) * 36 + 4
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
                os.startfile(self.rows[self.current_idx].file_path)
                self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("* { border: none; outline: none; }")
    launcher = MDLauncher()
    launcher.show()
    launcher.activateWindow()
    launcher.raise_()
    sys.exit(app.exec_())
