import sys
import os
import json
import subprocess
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QGroupBox, 
                             QGridLayout, QScrollArea, QFrame, QDialog, 
                             QPlainTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QListWidget, QListWidgetItem, QLineEdit, QFileDialog)
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
        layout.addWidget(QLabel("- Visibility Logic: CHECKLIST"))
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

class ConfiguratorGUI(QMainWindow):
    def __init__(self, start_tab=0):
        super().__init__()
        self.setWindowTitle("FZF SYSTEM CONFIGURATOR")
        self.setMinimumSize(800, 850)
        
        # Default config
        self.config = {
            "theme": {
                "folder_normal": 208,
                "folder_bookmark": 51,
                "file_normal": 250,
                "file_bookmark": 121
            },
            "visibility": {
                ".git": False, "__pycache__": False, "node_modules": False, ".venv": False,
                ".vscode": False, "obj": False, "bin": False
            },
            "search_roots": {
                r"C:\@delta\ms1": True,
                r"C:\@delta\db": True,
                r"C:\@delta\msBackups": True,
                r"C:\Users\nahid\Pictures": True,
                "D:\\": True
            }
        }
        self.load_settings()
        self.current_editing = "folder_normal"
        self.init_ui(start_tab)
        self.apply_styles()
        self.update_previews()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    if "theme" in data: self.config["theme"].update(data["theme"])
                    if "visibility" in data: self.config["visibility"] = data["visibility"]
                    if "search_roots" in data: self.config["search_roots"] = data["search_roots"]
            except: pass

    def save_settings(self):
        # Update visibility from checklist
        self.config["visibility"] = {}
        for i in range(self.visibility_list.count()):
            item = self.visibility_list.item(i)
            self.config["visibility"][item.text()] = (item.checkState() == Qt.CheckState.Checked)
        
        # Update search roots from checklist
        self.config["search_roots"] = {}
        for i in range(self.roots_list.count()):
            item = self.roots_list.item(i)
            self.config["search_roots"][item.text()] = (item.checkState() == Qt.CheckState.Checked)
            
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
        
        # --- Tab 1: Search Roots ---
        roots_tab = QWidget()
        roots_layout = QVBoxLayout(roots_tab)
        roots_layout.addWidget(QLabel("SEARCH DIRECTORIES (Root paths to crawl):"))
        self.roots_list = QListWidget()
        for path, enabled in sorted(self.config["search_roots"].items()):
            self.add_root_item(path, enabled)
        roots_layout.addWidget(self.roots_list)
        
        root_btn_layout = QHBoxLayout()
        btn_add_root = QPushButton("+ ADD DIRECTORY")
        btn_add_root.clicked.connect(self.browse_root)
        btn_remove_root = QPushButton("- REMOVE SELECTED")
        btn_remove_root.clicked.connect(self.remove_root)
        root_btn_layout.addWidget(btn_add_root)
        root_btn_layout.addWidget(btn_remove_root)
        roots_layout.addLayout(root_btn_layout)
        self.tabs.addTab(roots_tab, "📂 SEARCH DIRS")

        # --- Tab 2: Colors ---
        color_tab = QWidget()
        color_layout = QVBoxLayout(color_tab)
        sel_layout = QGridLayout()
        btns = [("NORMAL FOLDER", "folder_normal"), ("BOOKMARK FOLDER", "folder_bookmark"),
                ("NORMAL FILE", "file_normal"), ("BOOKMARK FILE", "file_bookmark")]
        self.color_btns = {}
        for i, (lbl, key) in enumerate(btns):
            b = QPushButton(lbl)
            b.setCheckable(True)
            b.clicked.connect(lambda checked, k=key: self.set_editing(k))
            sel_layout.addWidget(b, i // 2, i % 2)
            self.color_btns[key] = b
        self.color_btns["folder_normal"].setChecked(True)
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

        # --- Tab 3: Visibility (Ignore) ---
        visibility_tab = QWidget()
        visibility_layout = QVBoxLayout(visibility_tab)
        visibility_layout.addWidget(QLabel("FOLDER VISIBILITY (Internal folder names to hide):"))
        self.visibility_list = QListWidget()
        for folder, is_visible in sorted(self.config["visibility"].items()):
            self.add_visibility_item(folder, is_visible)
        visibility_layout.addWidget(self.visibility_list)
        
        add_vis_layout = QHBoxLayout()
        self.new_folder_input = QLineEdit()
        self.new_folder_input.setPlaceholderText("Enter folder name (e.g. node_modules)...")
        btn_add_vis = QPushButton("+ ADD")
        btn_add_vis.clicked.connect(self.add_new_visibility)
        add_vis_layout.addWidget(self.new_folder_input)
        add_vis_layout.addWidget(btn_add_vis)
        visibility_layout.addLayout(add_vis_layout)
        self.tabs.addTab(visibility_tab, "👁 VISIBILITY")

        # --- Tab 4: Shortcuts ---
        shortcuts_tab = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_tab)
        shortcut_table = QTableWidget(14, 2)
        shortcut_table.setHorizontalHeaderLabels(["KEY", "ACTION"])
        shortcut_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        shortcut_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        data = [("Enter", "Action Menu"), ("Tab", "Multi-select"), ("F2", "Image Mode"), ("F3", "Path vs Name"),
                ("F4", "Refresh"), ("F5", "Bookmark"), ("F6", "Rename"), ("F7", "Open System Configuration"),
                ("Ctrl-C", "Copy Path"), ("Ctrl-H", "Full Help GUI"),
                ("Ctrl-O", "Explorer"), ("Ctrl-P", "Preview"), ("Alt-Up/Down", "Order")]
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

    def add_root_item(self, path, enabled):
        item = QListWidgetItem(path)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if enabled else Qt.CheckState.Unchecked)
        self.roots_list.addItem(item)

    def browse_root(self):
        path = QFileDialog.getExistingDirectory(self, "Select Search Directory")
        if path:
            path = os.path.normpath(path)
            # Check if exists
            for i in range(self.roots_list.count()):
                if self.roots_list.item(i).text().lower() == path.lower(): return
            self.add_root_item(path, True)

    def remove_root(self):
        for item in self.roots_list.selectedItems():
            self.roots_list.takeItem(self.roots_list.row(item))

    def add_visibility_item(self, folder, is_visible):
        item = QListWidgetItem(folder)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked if is_visible else Qt.CheckState.Unchecked)
        self.visibility_list.addItem(item)

    def add_new_visibility(self):
        name = self.new_folder_input.text().strip()
        if name:
            for i in range(self.visibility_list.count()):
                if self.visibility_list.item(i).text() == name: return
            self.add_visibility_item(name, True)
            self.new_folder_input.clear()

    def set_editing(self, key):
        self.current_editing = key
        for k, b in self.color_btns.items(): b.setChecked(k == key)

    def color_selected(self, index):
        self.config["theme"][self.current_editing] = index
        self.update_previews()

    def randomize_colors(self):
        for key in self.config["theme"]: self.config["theme"][key] = random.randint(0, 255)
        self.update_previews()

    def update_previews(self):
        t = self.config["theme"]
        self.lbl_preview_folder_normal.setStyleSheet(f"color: {get_ansi_color_hex(t['folder_normal'])};")
        self.lbl_preview_folder_bookmark.setStyleSheet(f"color: {get_ansi_color_hex(t['folder_bookmark'])};")
        self.lbl_preview_file_normal.setStyleSheet(f"color: {get_ansi_color_hex(t['file_normal'])};")
        self.lbl_preview_file_bookmark.setStyleSheet(f"color: {get_ansi_color_hex(t['file_bookmark'])};")

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
            QLineEdit, QPlainTextEdit, QListWidget, QTableWidget {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; }}
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
        if sys.argv[1] == "--ignore": start_tab = 2
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h": start_tab = 3
    window = ConfiguratorGUI(start_tab)
    window.show()
    sys.exit(app.exec())
