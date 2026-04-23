import sys
import os
import json
import subprocess
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox, 
                             QGridLayout, QScrollArea, QFrame, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal

# PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"

THEME_FILE = r"C:\@delta\db\FZF_launcher\theme.json"

def get_ansi_color_hex(n):
    """Returns a hex color for an ANSI 256 color index."""
    # Standard 16 colors
    standard = [
        "#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
        "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff"
    ]
    if n < 16: return standard[n]
    if n < 232:
        n -= 16
        r = (n // 36) * 51
        g = ((n // 6) % 6) * 51
        b = (n % 6) * 51
        if r > 0: r += 55
        if g > 0: g += 55
        if b > 0: b += 55
        return f"#{min(r, 255):02x}{min(g, 255):02x}{min(b, 255):02x}"
    # Greyscale
    v = (n - 232) * 10 + 8
    return f"#{v:02x}{v:02x}{v:02x}"

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SYSTEM SETTINGS")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)
        
        lbl_title = QLabel("CONFIGURATION MODULES:")
        lbl_title.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        layout.addWidget(QLabel("- Theme Persistence: ACTIVE"))
        layout.addWidget(QLabel("- Path Resolution: LEGACY"))
        layout.addStretch()
        
        btn_close = QPushButton("CLOSE")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        if parent:
            self.setStyleSheet(parent.styleSheet())

class ColorButton(QPushButton):
    clicked_with_index = pyqtSignal(int)
    
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.setFixedSize(25, 25)
        hex_color = get_ansi_color_hex(index)
        self.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #333;")
        self.setToolTip(f"ANSI Index: {index}\n{hex_color}")
        self.clicked.connect(lambda: self.clicked_with_index.emit(self.index))

class ThemeChooser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FZF THEME CHOOSER")
        self.setMinimumSize(600, 750)
        
        self.theme = {
            "folder_normal": 208,
            "folder_bookmark": 51,
            "file_normal": 250,
            "file_bookmark": 121
        }
        self.load_settings()
        
        self.current_editing = "folder_normal"
        
        self.init_ui()
        self.apply_styles()
        self.update_previews()

    def load_settings(self):
        if os.path.exists(THEME_FILE):
            try:
                with open(THEME_FILE, 'r') as f:
                    data = json.load(f)
                    for k in self.theme:
                        if k in data:
                            self.theme[k] = int(data[k])
            except: pass

    def save_settings(self):
        os.makedirs(os.path.dirname(THEME_FILE), exist_ok=True)
        with open(THEME_FILE, 'w') as f:
            json.dump(self.theme, f, indent=4)
        print("Theme saved.")

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("SYSTEM COLOR CONFIGURATION")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 14pt;")
        layout.addWidget(header)
        
        # Selection Buttons
        sel_layout = QGridLayout()
        self.btn_folder_normal = QPushButton("NORMAL FOLDER")
        self.btn_folder_bookmark = QPushButton("BOOKMARK FOLDER")
        self.btn_file_normal = QPushButton("NORMAL FILE")
        self.btn_file_bookmark = QPushButton("BOOKMARK FILE")
        
        btns = [(self.btn_folder_normal, "folder_normal"), 
                (self.btn_folder_bookmark, "folder_bookmark"),
                (self.btn_file_normal, "file_normal"),
                (self.btn_file_bookmark, "file_bookmark")]
        
        for i, (b, key) in enumerate(btns):
            b.setCheckable(True)
            b.clicked.connect(lambda checked, k=key: self.set_editing(k))
            sel_layout.addWidget(b, i // 2, i % 2)
        
        self.btn_folder_normal.setChecked(True)
        layout.addLayout(sel_layout)
        
        # Preview Area
        preview_group = QGroupBox("LIVE PREVIEW")
        preview_layout = QVBoxLayout()
        
        self.lbl_preview_folder_normal = QLabel("  folder_name")
        self.lbl_preview_folder_bookmark = QLabel("* bookmarked_folder")
        self.lbl_preview_file_normal = QLabel("  normal_file.txt")
        self.lbl_preview_file_bookmark = QLabel("* bookmarked_file.txt")
        
        preview_layout.addWidget(self.lbl_preview_folder_normal)
        preview_layout.addWidget(self.lbl_preview_folder_bookmark)
        preview_layout.addWidget(self.lbl_preview_file_normal)
        preview_layout.addWidget(self.lbl_preview_file_bookmark)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Color Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(2)
        
        for i in range(256):
            btn = ColorButton(i)
            btn.clicked_with_index.connect(self.color_selected)
            grid.addWidget(btn, i // 16, i % 16)
            
        scroll.setWidget(grid_widget)
        layout.addWidget(scroll)
        
        # Action Buttons
        act_layout = QHBoxLayout()
        
        btn_settings = QPushButton("⚙ SETTINGS")
        btn_settings.clicked.connect(self.show_settings)
        
        btn_random = QPushButton("🎲 RANDOMIZE")
        btn_random.clicked.connect(self.randomize_colors)
        
        btn_save = QPushButton("SAVE CHANGES")
        btn_save.clicked.connect(self.save_settings)
        btn_save.setStyleSheet(f"background-color: {CP_GREEN}; color: black;")
        
        btn_restart = QPushButton("↺ RESTART")
        btn_restart.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))
        
        act_layout.addWidget(btn_settings)
        act_layout.addWidget(btn_random)
        act_layout.addStretch()
        act_layout.addWidget(btn_save)
        act_layout.addWidget(btn_restart)
        layout.addLayout(act_layout)

    def randomize_colors(self):
        for key in self.theme:
            self.theme[key] = random.randint(0, 255)
        self.update_previews()

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def set_editing(self, key):
        self.current_editing = key
        self.btn_folder_normal.setChecked(key == "folder_normal")
        self.btn_folder_bookmark.setChecked(key == "folder_bookmark")
        self.btn_file_normal.setChecked(key == "file_normal")
        self.btn_file_bookmark.setChecked(key == "file_bookmark")

    def color_selected(self, index):
        self.theme[self.current_editing] = index
        self.update_previews()

    def update_previews(self):
        self.lbl_preview_folder_normal.setStyleSheet(f"color: {get_ansi_color_hex(self.theme['folder_normal'])};")
        self.lbl_preview_folder_bookmark.setStyleSheet(f"color: {get_ansi_color_hex(self.theme['folder_bookmark'])};")
        self.lbl_preview_file_normal.setStyleSheet(f"color: {get_ansi_color_hex(self.theme['file_normal'])};")
        self.lbl_preview_file_bookmark.setStyleSheet(f"color: {get_ansi_color_hex(self.theme['file_bookmark'])};")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 15px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:checked {{
                background-color: {CP_CYAN}; color: black; border: 1px solid {CP_CYAN};
            }}
            
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ThemeChooser()
    window.show()
    sys.exit(app.exec())
