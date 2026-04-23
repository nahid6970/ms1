import sys
import os
import json
import subprocess
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox, 
                             QGridLayout, QScrollArea, QFrame, QDialog, 
                             QPlainTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView)
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

CONFIG_FILE = r"C:\@delta\db\FZF_launcher\config.json"

def get_ansi_color_hex(n):
    """Returns a hex color for an ANSI 256 color index."""
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
        layout.addWidget(QLabel("- Ignore Logic: PRUNING"))
        layout.addStretch()
        btn_close = QPushButton("CLOSE")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        if parent: self.setStyleSheet(parent.styleSheet())

class ColorButton(QPushButton):
    clicked_with_index = pyqtSignal(int)
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.setFixedSize(25, 25)
        self.setStyleSheet(f"background-color: {get_ansi_color_hex(index)}; border: 1px solid #333;")
        self.clicked.connect(lambda: self.clicked_with_index.emit(self.index))

class ThemeChooser(QMainWindow):
    def __init__(self, start_tab=0):
        super().__init__()
        self.setWindowTitle("FZF SYSTEM CONFIGURATOR")
        self.setMinimumSize(700, 850)
        
        self.config = {
            "theme": {
                "folder_normal": 208,
                "folder_bookmark": 51,
                "file_normal": 250,
                "file_bookmark": 121
            },
            "ignore_list": [".git", "__pycache__", "node_modules", ".venv", ".vscode", "obj", "bin"]
        }
        self.load_settings()
        self.current_editing = "folder_normal"
        self.init_ui(start_tab)
        self.apply_styles()
        self.update_previews()

    def load_settings(self):
        legacy_file = r"C:\@delta\db\FZF_launcher\theme.json"
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    if "theme" in data: self.config["theme"].update(data["theme"])
                    if "ignore_list" in data: self.config["ignore_list"] = data["ignore_list"]
            except: pass
        elif os.path.exists(legacy_file):
            try:
                with open(legacy_file, 'r') as f:
                    self.config["theme"].update(json.load(f))
            except: pass

    def save_settings(self):
        lines = self.ignore_edit.toPlainText().split('\n')
        self.config["ignore_list"] = [l.strip() for l in lines if l.strip()]
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)
        print("Configuration saved.")

    def init_ui(self, start_tab=0):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        header = QLabel("SYSTEM CONFIGURATION")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 14pt;")
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        
        # --- Tab 1: Colors ---
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
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
        color_layout.addLayout(sel_layout)
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
        color_layout.addWidget(preview_group)
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
        color_layout.addWidget(scroll)
        self.tabs.addTab(color_tab, "🎨 COLORS")

        # --- Tab 2: Ignore List ---
        ignore_tab = QWidget()
        ignore_layout = QVBoxLayout(ignore_tab)
        ignore_layout.addWidget(QLabel("EXCLUDE PATHS/FOLDERS (One per line):"))
        self.ignore_edit = QPlainTextEdit()
        self.ignore_edit.setPlainText('\n'.join(self.config["ignore_list"]))
        ignore_layout.addWidget(self.ignore_edit)
        ignore_layout.addWidget(QLabel("Files or folders containing these strings will be hidden."))
        self.tabs.addTab(ignore_tab, "🚫 IGNORE LIST")

        # --- Tab 3: Shortcuts ---
        shortcuts_tab = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_tab)
        
        shortcut_table = QTableWidget(14, 2)
        shortcut_table.setHorizontalHeaderLabels(["KEY", "ACTION"])
        shortcut_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        shortcut_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        shortcut_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        data = [
            ("Enter", "Action Menu (Editor/Folder/Run/Copy)"),
            ("Tab", "Multi-select files"),
            ("F2", "Toggle Image Preview Mode"),
            ("F3", "Toggle View Mode (Path vs Name)"),
            ("F4", "Refresh File List"),
            ("F5", "Toggle Bookmark (Set Name)"),
            ("F6", "Rename Bookmark"),
            ("F7", "Open Color Theme GUI"),
            ("F8", "Open Ignore List Manager"),
            ("Ctrl-C", "Copy path to clipboard"),
            ("Ctrl-O", "Open location in Explorer"),
            ("Ctrl-P", "Toggle Preview Window"),
            ("Alt-Up/Down", "Move Bookmark order"),
            ("?", "Toggle Terminal Help Header"),
        ]
        
        for i, (key, action) in enumerate(data):
            shortcut_table.setItem(i, 0, QTableWidgetItem(key))
            shortcut_table.setItem(i, 1, QTableWidgetItem(action))
            
        shortcuts_layout.addWidget(shortcut_table)
        self.tabs.addTab(shortcuts_tab, "⌨ SHORTCUTS")

        self.tabs.setCurrentIndex(start_tab)
        main_layout.addWidget(self.tabs)
        
        # Action Buttons
        act_layout = QHBoxLayout()
        btn_settings = QPushButton("⚙ SETTINGS")
        btn_settings.clicked.connect(self.show_settings)
        btn_random = QPushButton("🎲 RANDOMIZE")
        btn_random.clicked.connect(self.randomize_colors)
        btn_save = QPushButton("SAVE CONFIG")
        btn_save.clicked.connect(self.save_settings)
        btn_save.setStyleSheet(f"background-color: {CP_GREEN}; color: black;")
        btn_restart = QPushButton("↺ RESTART")
        btn_restart.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))
        act_layout.addWidget(btn_settings)
        act_layout.addWidget(btn_random)
        act_layout.addStretch()
        act_layout.addWidget(btn_save)
        act_layout.addWidget(btn_restart)
        main_layout.addLayout(act_layout)

    def set_editing(self, key):
        self.current_editing = key
        self.btn_folder_normal.setChecked(key == "folder_normal")
        self.btn_folder_bookmark.setChecked(key == "folder_bookmark")
        self.btn_file_normal.setChecked(key == "file_normal")
        self.btn_file_bookmark.setChecked(key == "file_bookmark")

    def color_selected(self, index):
        self.config["theme"][self.current_editing] = index
        self.update_previews()

    def randomize_colors(self):
        for key in self.config["theme"]:
            self.config["theme"][key] = random.randint(0, 255)
        self.update_previews()

    def update_previews(self):
        theme = self.config["theme"]
        self.lbl_preview_folder_normal.setStyleSheet(f"color: {get_ansi_color_hex(theme['folder_normal'])};")
        self.lbl_preview_folder_bookmark.setStyleSheet(f"color: {get_ansi_color_hex(theme['folder_bookmark'])};")
        self.lbl_preview_file_normal.setStyleSheet(f"color: {get_ansi_color_hex(theme['file_normal'])};")
        self.lbl_preview_file_bookmark.setStyleSheet(f"color: {get_ansi_color_hex(theme['file_bookmark'])};")

    def show_settings(self):
        SettingsDialog(self).exec()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QTabWidget::pane {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}
            QTabBar::tab {{ background: {CP_PANEL}; padding: 8px 20px; border: 1px solid {CP_DIM}; margin-right: 2px; }}
            QTabBar::tab:selected {{ background: {CP_DIM}; color: {CP_CYAN}; border-bottom: 2px solid {CP_CYAN}; }}
            QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 15px; padding-top: 15px; font-weight: bold; color: {CP_YELLOW}; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            QLineEdit, QPlainTextEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:checked {{ background-color: {CP_CYAN}; color: black; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QTableWidget {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; gridline-color: {CP_DIM}; }}
            QHeaderView::section {{ background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 4px; border: 1px solid {CP_BG}; font-weight: bold; }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    start_tab = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ignore": start_tab = 1
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h": start_tab = 2
    window = ThemeChooser(start_tab)
    window.show()
    sys.exit(app.exec())
