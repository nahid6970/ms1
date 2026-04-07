import sys
import os
import json
import urllib.request
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QPlainTextEdit, QFrame, QScrollArea, QSplitter,
                             QMessageBox, QDialog, QFormLayout, QLineEdit, QGroupBox)
from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

CONVEX_URL = "https://different-gnat-734.convex.cloud"

SVGS = {
    "RESTART": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"></path><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>',
    "SETTINGS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    "LEFT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>',
    "RIGHT": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>'
}

class CyberButton(QPushButton):
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
                QPushButton {{ background-color: transparent; color: {self.color}; border: 2px solid {self.color}; padding: 5px 10px; font-family: 'Consolas'; }}
                QPushButton:hover {{ background-color: {self.color}; color: {CP_BG}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{ background-color: {self.color}; color: {CP_BG}; border: none; padding: 5px 15px; font-family: 'Consolas'; }}
                QPushButton:hover {{ background-color: {CP_BG}; color: {self.color}; border: 1px solid {self.color}; }}
            """)

class SettingsPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        layout = QVBoxLayout(self)
        title = QLabel("SETTINGS (EMPTY)")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(title)
        layout.addStretch()
        self.hide()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CONVEX BACKUP EXPLORER")
        self.resize(1100, 750)
        self.backups = []
        self.current_index = -1
        
        # Apply Theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QComboBox::drop-down {{ border: none; }}
            QPlainTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px; font-family: 'Consolas'; font-size: 10pt;
            }}
            QLabel {{ color: {CP_TEXT}; }}
            QScrollBar:vertical {{
                background: {CP_BG}; width: 10px; margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM}; min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # TOP BAR
        top_bar = QHBoxLayout()
        self.script_combo = QComboBox()
        self.script_combo.setPlaceholderText("SELECT SCRIPT...")
        self.script_combo.setMinimumWidth(300)
        self.script_combo.currentIndexChanged.connect(self.on_script_changed)
        top_bar.addWidget(self.script_combo)

        self.refresh_btn = CyberButton("RELOAD", color=CP_CYAN, is_outlined=True)
        self.refresh_btn.clicked.connect(self.load_scripts)
        top_bar.addWidget(self.refresh_btn)

        top_bar.addStretch()

        self.restart_btn = CyberButton("", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["RESTART"])
        self.restart_btn.setToolTip("Restart Application")
        self.restart_btn.clicked.connect(self.restart_app)
        top_bar.addWidget(self.restart_btn)

        self.settings_btn = CyberButton("", color=CP_DIM, is_outlined=True, svg_data=SVGS["SETTINGS"])
        self.settings_btn.clicked.connect(self.toggle_settings)
        top_bar.addWidget(self.settings_btn)

        main_layout.addLayout(top_bar)

        # CONTENT AREA
        content_layout = QHBoxLayout()
        
        # NAVIGATION LEFT (TO RECENT)
        self.recent_btn = CyberButton("", color=CP_CYAN, is_outlined=True, svg_data=SVGS["LEFT"])
        self.recent_btn.setFixedSize(40, 40)
        self.recent_btn.setToolTip("Show more recent version")
        self.recent_btn.clicked.connect(self.show_newer)
        content_layout.addWidget(self.recent_btn)

        # CENTER CODE VIEW
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        
        self.info_lbl = QLabel("SELECT A SCRIPT TO BEGIN")
        self.info_lbl.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        self.info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.info_lbl)

        self.code_edit = QPlainTextEdit()
        self.code_edit.setReadOnly(True)
        center_layout.addWidget(self.code_edit)
        
        content_layout.addWidget(center_widget, stretch=1)

        # NAVIGATION RIGHT (TO PAST)
        self.past_btn = CyberButton("", color=CP_CYAN, is_outlined=True, svg_data=SVGS["RIGHT"])
        self.past_btn.setFixedSize(40, 40)
        self.past_btn.setToolTip("Show older version")
        self.past_btn.clicked.connect(self.show_older)
        content_layout.addWidget(self.past_btn)

        main_layout.addLayout(content_layout)
        
        # SETTINGS PANEL (INITIALLY HIDDEN)
        self.settings_panel = SettingsPanel(self)
        main_layout.addWidget(self.settings_panel)

        self.load_scripts()

    def _convex_call(self, endpoint, payload):
        try:
            url = f"{CONVEX_URL.rstrip('/')}/api/{endpoint}"
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"CONVEX ERROR: {e}")
            return None

    def load_scripts(self):
        res = self._convex_call("query", {"path": "functions:listScripts", "args": {}})
        if res and "value" in res:
            self.script_combo.clear()
            self.script_combo.addItems(res["value"])
            self.script_combo.setCurrentIndex(-1)
            self.script_combo.setPlaceholderText("SELECT SCRIPT...")

    def on_script_changed(self):
        script_name = self.script_combo.currentText()
        if not script_name: return
        
        res = self._convex_call("query", {"path": "functions:list", "args": {"scriptName": script_name}})
        if res and "value" in res:
            self.backups = res["value"] # Already sorted newest first
            self.current_index = 0
            self.load_backup_data()
        else:
            self.backups = []
            self.current_index = -1
            self.code_edit.setPlainText("No backups found.")

    def load_backup_data(self):
        if not self.backups or self.current_index < 0:
            return
        
        backup = self.backups[self.current_index]
        res = self._convex_call("query", {"path": "functions:get", "args": {"id": backup["id"]}})
        
        dt = datetime.datetime.fromtimestamp(backup["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M:%p")
        self.info_lbl.setText(f"VERSION {len(self.backups) - self.current_index} / {len(self.backups)}  |  {dt}  |  {backup['label']}")
        
        if res and "value" in res:
            self.code_edit.setPlainText(json.dumps(res["value"], indent=2))
        else:
            self.code_edit.setPlainText("Error loading backup data.")
            
        self.update_nav_buttons()

    def update_nav_buttons(self):
        # Index 0 is most recent.
        self.past_btn.setEnabled(self.current_index < len(self.backups) - 1)
        self.recent_btn.setEnabled(self.current_index > 0)

    def show_older(self):
        if self.current_index < len(self.backups) - 1:
            self.current_index += 1
            self.load_backup_data()

    def show_newer(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_backup_data()

    def toggle_settings(self):
        if self.settings_panel.isVisible():
            self.settings_panel.hide()
        else:
            self.settings_panel.show()

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
