import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QScrollArea, QLineEdit, QPushButton, QFileDialog, QDialog, QSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QMimeData, QUrl
from PyQt5.QtGui import QFont, QDrag

CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "md_launcher_config.json")

def load_config():
    default = {"folders": ["C:/@delta/ms1/md"], "win_w": 600, "win_h": 400}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if "md_folder" in data and "folders" not in data:
                    data["folders"] = [data["md_folder"]]
                return {**default, **data}
    except: pass
    return default

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


BTN_STYLE = f"""
    QPushButton {{ background: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; padding: 4px 12px; font-family: Consolas; font-size: 9pt; }}
    QPushButton:hover {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}
    QPushButton:pressed {{ background: {CP_CYAN}; color: {CP_BG}; }}
"""

class SettingsDialog(QDialog):
    applied = pyqtSignal()

    def __init__(self, config, parent=None):
        super().__init__(parent, Qt.WindowStaysOnTopHint)
        self.config = config
        self.setWindowTitle("Settings")
        self.setModal(False)
        self.setMinimumWidth(420)
        self.setStyleSheet(f"""
            QDialog {{ background: {CP_BG}; color: {CP_TEXT}; font-family: Consolas; }}
            QLabel {{ color: {CP_TEXT}; background: transparent; border: none; }}
            QSpinBox {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 2px 6px; font-family: Consolas; }}
            QSpinBox:focus {{ border-color: {CP_CYAN}; }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0; border: none; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # --- Window Size ---
        layout.addWidget(self._section("WINDOW SIZE"))

        size_row = QHBoxLayout()
        size_row.setSpacing(12)

        self.w_spin = self._spinbox(config.get("win_w", 600), 200, 3840)
        self.h_spin = self._spinbox(config.get("win_h", 400), 100, 2160)

        size_row.addWidget(QLabel("Width:"))
        size_row.addWidget(self.w_spin)
        size_row.addSpacing(16)
        size_row.addWidget(QLabel("Height:"))
        size_row.addWidget(self.h_spin)
        size_row.addStretch()
        layout.addLayout(size_row)

        # --- Folders ---
        layout.addWidget(self._section("FOLDERS"))

        self.folder_layout = QVBoxLayout()
        self.folder_layout.setSpacing(4)
        layout.addLayout(self.folder_layout)
        self._refresh_folders()

        add_btn = QPushButton("+ Add Folder")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {CP_CYAN}; border: none; text-align: left; padding: 2px 0; font-family: Consolas; font-size: 9pt; }} QPushButton:hover {{ color: {CP_YELLOW}; }}")
        add_btn.clicked.connect(self._add_folder)
        layout.addWidget(add_btn)

        layout.addStretch()

        # --- Apply / Close ---
        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet(BTN_STYLE)
        apply_btn.clicked.connect(self._apply)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet(BTN_STYLE)
        close_btn.clicked.connect(self.close)

        btn_row.addStretch()
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _section(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont("Consolas", 8, QFont.Bold))
        lbl.setStyleSheet(f"color: {CP_YELLOW}; background: transparent; border: none;")
        return lbl

    def _spinbox(self, value, min_, max_):
        sb = QSpinBox()
        sb.setRange(min_, max_)
        sb.setValue(value)
        sb.setFixedWidth(80)
        return sb

    def _refresh_folders(self):
        while self.folder_layout.count():
            item = self.folder_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for folder in self.config.get("folders", []):
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(8)

            lbl = QLabel(folder)
            lbl.setFont(QFont("Consolas", 8))
            lbl.setStyleSheet(f"color: {CP_SUBTEXT}; border: none; background: transparent;")

            rm = QPushButton("✕")
            rm.setFixedSize(20, 20)
            rm.setCursor(Qt.PointingHandCursor)
            rm.setStyleSheet(f"QPushButton {{ background: transparent; color: {CP_DIM}; border: none; }} QPushButton:hover {{ color: {CP_RED}; }}")
            rm.clicked.connect(lambda _, f=folder: self._remove_folder(f))

            rl.addWidget(lbl, 1)
            rl.addWidget(rm)
            self.folder_layout.addWidget(row)

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            folder = folder.replace("\\", "/")
            if folder not in self.config["folders"]:
                self.config["folders"].append(folder)
                save_config(self.config)
                self._refresh_folders()
                self.applied.emit()

    def _remove_folder(self, folder):
        if folder in self.config["folders"]:
            self.config["folders"].remove(folder)
            save_config(self.config)
            self._refresh_folders()
            self.applied.emit()

    def _apply(self):
        self.config["win_w"] = self.w_spin.value()
        self.config["win_h"] = self.h_spin.value()
        save_config(self.config)
        self.applied.emit()


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


class MDLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.block_close = False
        self.all_files = []
        self.rows = []
        self.current_idx = 0
        self._settings_dialog = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        w = self.config.get("win_w", 600)
        h = self.config.get("win_h", 400)
        self.setGeometry((screen.width() - w) // 2, 10, w, h)

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

        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(36, 36)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: {CP_DIM}; border: none; font-size: 14px; }} QPushButton:hover {{ color: {CP_YELLOW}; }}")
        settings_btn.clicked.connect(self.open_settings)

        sr_layout.addWidget(self.search)
        sr_layout.addWidget(settings_btn)
        main_layout.addWidget(search_row)

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

    def open_settings(self):
        if self._settings_dialog and self._settings_dialog.isVisible():
            self._settings_dialog.raise_()
            self._settings_dialog.activateWindow()
            return
        self.block_close = True
        dlg = SettingsDialog(self.config, self)
        dlg.applied.connect(self._on_settings_applied)
        dlg.finished.connect(lambda: setattr(self, 'block_close', False))
        self._settings_dialog = dlg
        dlg.show()

    def _on_settings_applied(self):
        w = self.config.get("win_w", 600)
        h = self.config.get("win_h", 400)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry((screen.width() - w) // 2, 10, w, h)
        self.scan_files()

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

    def set_index(self, idx):
        if not self.rows: return
        if 0 <= self.current_idx < len(self.rows):
            self.rows[self.current_idx].set_selected(False)
        self.current_idx = max(0, min(idx, len(self.rows) - 1))
        self.rows[self.current_idx].set_selected(True)

    def check_focus(self):
        if self.block_close: return
        if not self.isActiveWindow():
            if self._settings_dialog and self._settings_dialog.isVisible():
                return
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
