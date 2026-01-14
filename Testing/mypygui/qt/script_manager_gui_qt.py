import sys
import os
import json
import subprocess
import shutil
import psutil
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QMessageBox, QGridLayout, QSizePolicy,
                             QProgressBar, QDialog, QLineEdit, QComboBox, 
                             QCheckBox, QColorDialog, QMenu, QTextEdit, QFormLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QCursor, QColor, QDesktopServices, QAction
from PyQt6.QtCore import QUrl

# -----------------------------------------------------------------------------
# CYBERPUNK THEME PALETTE
# -----------------------------------------------------------------------------
CP_BG = "#050505"           # Main Background
CP_PANEL = "#111111"        # Panel Background
CP_YELLOW = "#FCEE0A"       # Cyber Yellow
CP_CYAN = "#00F0FF"         # Neon Cyan
CP_RED = "#FF003C"          # Neon Red
CP_DIM = "#3a3a3a"          # Dimmed/Inactive
CP_TEXT = "#E0E0E0"         # Main Text
CP_SUBTEXT = "#808080"      # Sub Text
CP_GREEN = "#00ff21"        # Success Green
CP_ORANGE = "#ff934b"       # Warning Orange [RAM]

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_launcher_config.json")

# -----------------------------------------------------------------------------
# WIDGETS
# -----------------------------------------------------------------------------

class CyberButton(QPushButton):
    def __init__(self, text, parent=None, color=CP_YELLOW, is_outlined=False, font_size=10, is_folder=False, script_data=None):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.is_folder = is_folder
        self.script_data = script_data
        
        self.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(45)
        
        # Enable Right Click
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.update_style()

    def update_style(self):
        if self.is_folder:
            bg_color = CP_PANEL
            border_str = f"1px solid {self.color}"
            text_color = self.color
        else:
            if self.is_outlined:
                bg_color = "transparent"
                border_str = f"2px solid {self.color}"
                text_color = self.color
            else:
                bg_color = self.color
                border_str = "none"
                text_color = CP_BG

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: {border_str};
                padding: 10px;
                font-family: 'Consolas';
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {CP_BG if not self.is_outlined else self.color};
                color: {self.color if not self.is_outlined else CP_BG};
                border: 1px solid {self.color};
            }}
        """)

class StatWidget(QFrame):
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        self.setFixedWidth(140)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Header
        self.lbl_title = QLabel(label)
        self.lbl_title.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.lbl_title.setStyleSheet(f"color: {CP_SUBTEXT};")
        layout.addWidget(self.lbl_title)
        
        # Value
        self.lbl_val = QLabel("0%")
        self.lbl_val.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.lbl_val.setStyleSheet(f"color: {color};")
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_val)
        
        # Bar
        self.bar = QProgressBar()
        self.bar.setFixedHeight(4)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {CP_DIM};
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        layout.addWidget(self.bar)

    def set_value(self, val, text=None):
        self.bar.setValue(int(val))
        self.lbl_val.setText(text if text else f"{val}%")

class EditDialog(QDialog):
    def __init__(self, script_data, parent=None):
        super().__init__(parent)
        self.script = script_data
        self.setWindowTitle(f"EDIT // {self.script.get('name', 'UNKNOWN')}")
        self.resize(500, 600)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_YELLOW}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }}
            QLineEdit, QTextEdit {{ 
                background-color: {CP_PANEL}; 
                color: {CP_YELLOW}; 
                border: 1px solid {CP_DIM}; 
                padding: 5px; 
                font-family: 'Consolas';
            }}
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QCheckBox {{ color: {CP_TEXT}; font-family: 'Consolas'; }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.inp_name = QLineEdit(self.script.get("name", ""))
        form.addRow("Name:", self.inp_name)
        
        self.inp_path = QLineEdit(self.script.get("path", ""))
        fsbox = QHBoxLayout()
        fsbox.addWidget(self.inp_name)


        if self.script.get("type") != "folder":
            form.addRow("Path:", self.inp_path)
            
            self.chk_hide = QCheckBox("Hide Terminal")
            self.chk_hide.setChecked(self.script.get("hide_terminal", False))
            form.addRow("", self.chk_hide)
            
            self.chk_keep = QCheckBox("Keep Open")
            self.chk_keep.setChecked(self.script.get("keep_open", False))
            form.addRow("", self.chk_keep)

            self.inp_ctrl_left = QLineEdit(self.script.get("ctrl_left_cmd", ""))
            form.addRow("Ctrl+Left Cmd:", self.inp_ctrl_left)

        # Style options
        self.btn_color = QPushButton("Pick Color")
        self.btn_color.setStyleSheet(f"background-color: {self.script.get('color', CP_YELLOW)}; color: black;")
        self.btn_color.clicked.connect(self.pick_color)
        form.addRow("Color:", self.btn_color)

        layout.addLayout(form)
        
        # Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton("SAVE")
        save_btn.setStyleSheet(f"background-color: {CP_YELLOW}; color: black; font-weight: bold; padding: 10px;")
        save_btn.clicked.connect(self.save)
        
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; padding: 10px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.script.get("color", CP_YELLOW)), self)
        if color.isValid():
            self.script["color"] = color.name()
            self.btn_color.setStyleSheet(f"background-color: {color.name()}; color: black;")

    def save(self):
        self.script["name"] = self.inp_name.text()
        if self.script.get("type") != "folder":
            self.script["path"] = self.inp_path.text()
            self.script["hide_terminal"] = self.chk_hide.isChecked()
            self.script["keep_open"] = self.chk_keep.isChecked()
            self.script["ctrl_left_cmd"] = self.inp_ctrl_left.text()
        self.accept()

# -----------------------------------------------------------------------------
# MAIN WINDOW
# -----------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCRIPT // MANAGER_V3.0")
        self.resize(1100, 800)
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }}")
        
        self.config = {}
        self.view_stack = [] 
        
        self.load_config()
        self.setup_ui()
        self.refresh_grid()
        
        # Timer for System Stats
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000) # Update every 2s

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding='utf-8') as f:
                    self.config = json.load(f)
            except: self.config = {"scripts": []}
        else:
            self.config = {"scripts": []}
            
    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            self.refresh_grid()
        except Exception as e:
            print(f"Save failed: {e}")

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # 1. HEADER
        header = QHBoxLayout()
        
        self.back_btn = CyberButton("<<", color=CP_RED, is_outlined=True)
        self.back_btn.setFixedSize(50, 40)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.hide()
        
        self.title_lbl = QLabel("SCRIPT MANAGER // ROOT")
        self.title_lbl.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {CP_YELLOW};")
        
        header.addWidget(self.back_btn)
        header.addWidget(self.title_lbl)
        header.addStretch()
        
        stg_btn = CyberButton("SETTINGS", color=CP_DIM, is_outlined=True)
        stg_btn.setFixedSize(100, 40)
        stg_btn.clicked.connect(lambda: QMessageBox.information(self, "Info", "Global Settings Not Implemented Yet"))
        header.addWidget(stg_btn)
        
        self.main_layout.addLayout(header)

        # 2. DASHBOARD (Stats + Widgets)
        dash_frame = QFrame()
        dash_frame.setFixedHeight(80)
        dash_layout = QHBoxLayout(dash_frame)
        dash_layout.setContentsMargins(0,0,0,0)
        
        # Stats
        self.stat_cpu = StatWidget("CPU", CP_CYAN)
        self.stat_ram = StatWidget("RAM", CP_ORANGE)
        self.stat_disk = StatWidget("SSD", CP_GREEN)
        
        dash_layout.addWidget(self.stat_cpu)
        dash_layout.addWidget(self.stat_ram)
        dash_layout.addWidget(self.stat_disk)
        
        # Github / Rclone (Static Text for now as placeholders)
        self.lbl_status = QLabel("  GITHUB: OK  |  RCLONE: IDLE  ")
        self.lbl_status.setFont(QFont("Consolas", 10))
        self.lbl_status.setStyleSheet(f"color: {CP_SUBTEXT}; background: {CP_PANEL}; border: 1px solid {CP_DIM}; padding: 10px;")
        dash_layout.addWidget(self.lbl_status)
        
        dash_layout.addStretch()
        self.main_layout.addWidget(dash_frame)

        # 3. GRID AREA
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: transparent; border: none;")
        
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(15)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.grid_container)
        self.main_layout.addWidget(scroll)

    def update_stats(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage('C://').percent
            
            self.stat_cpu.set_value(cpu)
            self.stat_ram.set_value(ram)
            self.stat_disk.set_value(disk)
        except: pass

    def refresh_grid(self):
        # Clear
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        # Get Items
        if self.view_stack:
            folder = self.view_stack[-1]
            scripts = folder.get("scripts", [])
            self.title_lbl.setText(f"SCRIPT MANAGER // {folder.get('name', '').upper()}")
            self.back_btn.show()
        else:
            scripts = self.config.get("scripts", [])
            self.title_lbl.setText("SCRIPT MANAGER // ROOT")
            self.back_btn.hide()

        # Populate
        cols = 5
        row, col = 0, 0
        
        for script in scripts:
            name = script.get("name", "Unnamed")
            # Default colors
            color = script.get("color", CP_YELLOW if script.get("type") != "folder" else CP_CYAN)
            if not color.startswith("#"): color = CP_YELLOW
            
            btn = CyberButton(name, color=color, is_folder=(script.get("type") == "folder"), script_data=script)
            btn.clicked.connect(partial(self.handle_click, script))
            btn.customContextMenuRequested.connect(partial(self.show_context_menu, btn, script))
            
            # Grid logic
            colspan = 1
            if col + colspan > cols:
                row += 1
                col = 0
            
            self.grid.addWidget(btn, row, col)
            col += 1
            if col >= cols:
                row += 1
                col = 0

    def handle_click(self, script):
        if script.get("type") == "folder":
            self.view_stack.append(script)
            self.refresh_grid()
        else:
            self.launch_script(script)

    def launch_script(self, script):
        path = os.path.expandvars(script.get("path", ""))
        hide = script.get("hide_terminal", False)
        
        cwd = os.path.dirname(path) if os.path.isfile(path) else None
        
        try:
            if path.endswith(".py"):
                exe = "pythonw" if hide else "python"
                subprocess.Popen([exe, path], cwd=cwd)
                print(f"Launched Python: {path}")
            elif path.endswith(".ps1"):
                cmd = ["pwsh", "-File", path] if shutil.which("pwsh") else ["powershell", "-File", path]
                if hide: cmd.insert(1, "-WindowStyle"); cmd.insert(2, "Hidden")
                subprocess.Popen(cmd, cwd=cwd)
                print(f"Launched PS1: {path}")
            else:
                subprocess.Popen(path, shell=True, cwd=cwd)
                print(f"Launched EXE: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_back(self):
        if self.view_stack:
            self.view_stack.pop()
            self.refresh_grid()

    def show_context_menu(self, btn, script, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }}
            QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
        """)
        
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.open_edit(script))
        menu.addAction(edit_action)
        
        del_action = QAction("Delete", self)
        del_action.triggered.connect(lambda: self.delete_item(script))
        menu.addAction(del_action)
        
        menu.exec(btn.mapToGlobal(pos))

    def open_edit(self, script):
        dlg = EditDialog(script, self)
        if dlg.exec():
            self.save_config()

    def delete_item(self, script):
        confirm = QMessageBox.question(self, "Confirm", f"Delete {script['name']}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            # Locate and remove
            target_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            if script in target_list:
                target_list.remove(script)
                self.save_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
