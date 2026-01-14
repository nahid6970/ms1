import sys
import os
import json
import winreg
import subprocess
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QScrollArea, QFrame, QMessageBox, QDialog, 
                             QComboBox, QFileDialog, QSplitter, QGraphicsEffect,
                             QGraphicsDropShadowEffect, QMenu, QCheckBox)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QPainter, QPen, QAction

# Constants
JSON_FILE = os.path.join(os.path.dirname(__file__), "startup_items.json")
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")
DEFAULT_PS1 = os.path.join(os.path.expanduser("~"), "Desktop", "myStartup.ps1")

# Cyberpunk Palette
CP_BG = "#050505"           # Main Background (almost black)
CP_PANEL = "#111111"        # Panel Background
CP_YELLOW = "#FCEE0A"       # Cyber Yellow (Primary Accent)
CP_CYAN = "#00F0FF"         # Neon Cyan (Secondary Accent)
CP_RED = "#FF003C"          # Neon Red (Error/Delete)
CP_DIM = "#3a3a3a"          # Dimmed/Inactive
CP_TEXT = "#E0E0E0"         # Main Text
CP_SUBTEXT = "#808080"      # Sub Text

class CyberButton(QPushButton):
    def __init__(self, text, parent=None, color=CP_YELLOW, is_outlined=False):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        self.update_style()

    def update_style(self):
        if self.is_outlined:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {self.color};
                    border: 2px solid {self.color};
                    padding: 5px 15px;
                    font-family: 'Consolas';
                }}
                QPushButton:hover {{
                    background-color: {self.color};
                    color: {CP_BG};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.color};
                    color: {CP_BG};
                    border: none;
                    padding: 5px 15px;
                    font-family: 'Consolas';
                }}
                QPushButton:hover {{
                    background-color: {CP_BG};
                    color: {self.color};
                    border: 1px solid {self.color};
                }}
            """)

class CyberInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CP_PANEL};
                color: {CP_YELLOW};
                border: 1px solid {CP_DIM};
                padding: 8px;
                font-family: 'Consolas';
            }}
            QLineEdit:focus {{
                border: 1px solid {CP_CYAN};
            }}
        """)

class StartupItemWidget(QFrame):
    toggled = pyqtSignal(dict, bool)
    launched = pyqtSignal(dict)
    edited = pyqtSignal(dict)
    deleted = pyqtSignal(dict)

    def __init__(self, item, is_active=False, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_active = is_active
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Determine border color based on activity
        self.border_color = CP_YELLOW if self.is_active else CP_DIM
        
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        # Status "LED" (Text based for Cyberpunk feel)
        self.status_lbl = QLabel("ACTV" if self.is_active else "OFF")
        self.status_lbl.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.status_lbl.setFixedWidth(40)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.status_btn = QPushButton(self.status_lbl.text())
        self.status_btn.setFixedSize(45, 25)
        self.status_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_btn.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.status_btn.clicked.connect(self.on_toggle)
        layout.addWidget(self.status_btn)

        # Info Area
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(self.item["name"])
        name_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {CP_TEXT}; text-transform: uppercase;")
        
        # Truncate long paths for display
        raw_path = self.item["paths"][0]
        cmd = self.item.get("Command", "")
        full_detail = f"{raw_path} {cmd}".strip()
        
        path_label = QLabel(full_detail)
        path_label.setFont(QFont("Consolas", 8))
        path_label.setStyleSheet(f"color: {CP_SUBTEXT};")
        path_label.setWordWrap(False) 
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(path_label)
        layout.addLayout(info_layout, stretch=1)
        
        # Timeline / Logged Date
        ts = self.item.get("added_at", time.time())
        date_str = time.strftime("%Y-%m-%d", time.localtime(ts))
        time_label = QLabel(f"LOGGED: {date_str}")
        time_label.setFont(QFont("Consolas", 7))
        time_label.setStyleSheet(f"color: {CP_DIM};")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(time_label)
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setFont(QFont("Consolas", 9))
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {CP_BG};
                color: {CP_TEXT};
                border: 1px solid {CP_CYAN};
            }}
            QMenu::item {{
                padding: 6px 25px;
                background-color: transparent;
            }}
            QMenu::item:selected {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
        """)
        
        launch_action = QAction("EXECUTE PROTOCOL", self)
        launch_action.triggered.connect(lambda: self.launched.emit(self.item))
        menu.addAction(launch_action)
        
        edit_action = QAction("EDIT CONFIG", self)
        edit_action.triggered.connect(lambda: self.edited.emit(self.item))
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("PURGE ENTRY", self)
        delete_action.triggered.connect(lambda: self.deleted.emit(self.item))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(pos))

    def update_style(self):
        color = CP_YELLOW if self.is_active else CP_DIM
        bg_col = "#0f0f15"
        self.setStyleSheet(f"""
            StartupItemWidget {{
                background-color: {bg_col};
                border-left: 3px solid {color};
                border-bottom: 1px solid {CP_PANEL};
            }}
            StartupItemWidget:hover {{
                background-color: #1a1a25;
            }}
        """)
        
        # Update status button style
        self.status_btn.setText("ON" if self.is_active else "OFF")
        btn_bg = color if self.is_active else "transparent"
        btn_fg = CP_BG if self.is_active else CP_SUBTEXT
        border = color if self.is_active else CP_DIM
        
        self.status_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_fg};
                border: 1px solid {border};
                border-radius: 0px;
            }}
            QPushButton:hover {{
                border: 1px solid {CP_CYAN};
                color: {CP_CYAN if not self.is_active else CP_BG};
            }}
        """)

    def set_active(self, active):
        self.is_active = active
        self.update_style()
    
    def on_toggle(self):
        self.toggled.emit(self.item, self.is_active)

class ItemDialog(QDialog):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item
        self.result_data = None
        self.setWindowTitle("SYSTEM // EDIT" if item else "SYSTEM // NEW")
        self.setFixedSize(600, 600) # Increased size
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_DIM}; }}
            QLabel {{ color: {CP_CYAN}; font-family: 'Consolas'; font-weight: bold; font-size: 12px; }}
            QComboBox {{
                background-color: {CP_PANEL};
                color: {CP_YELLOW};
                border: 1px solid {CP_DIM};
                padding: 5px;
                font-family: 'Consolas';
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        self.setup_ui()
        if item: self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Name
        layout.addWidget(QLabel("IDENTITY // NAME"))
        self.name_input = CyberInput("Enter identifier...")
        layout.addWidget(self.name_input)

        # Type
        layout.addWidget(QLabel("CLASS // TYPE"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["App", "Command"])
        layout.addWidget(self.type_combo)
        
        # Exec Type
        layout.addWidget(QLabel("PROTOCOL // EXEC TYPE"))
        self.exec_type_combo = QComboBox()
        self.exec_type_combo.addItems(["other", "pythonw", "pwsh", "cmd", "powershell", "ahk_v2"])
        self.exec_type_combo.currentTextChanged.connect(self.on_exec_type_changed)
        layout.addWidget(self.exec_type_combo)

        # Path
        layout.addWidget(QLabel("SOURCE // PATH"))
        path_layout = QHBoxLayout()
        self.path_input = CyberInput("Enter executable path...")
        browse_btn = CyberButton("SCAN", color=CP_CYAN, is_outlined=True)
        browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Args
        layout.addWidget(QLabel("PARAMETERS // ARGS (REGISTRY)"))
        self.args_input = CyberInput("Optional arguments for Registry...")
        layout.addWidget(self.args_input)
        
        # PS1 Command
        layout.addWidget(QLabel("CUSTOM COMMAND // PS1 SCRIPT"))
        self.ps1_input = CyberInput("Complete PowerShell command line...")
        layout.addWidget(self.ps1_input)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = CyberButton("UPLOAD", color=CP_YELLOW)
        save_btn.clicked.connect(self.save_item)
        cancel_btn = CyberButton("ABORT", color=CP_RED, is_outlined=True)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Executable", "", "Executables (*.exe);;All Files (*.*)")
        if filename: self.path_input.setText(filename)

    def on_exec_type_changed(self, text):
        common_paths = {
            "pythonw": r"C:\Users\nahid\scoop\apps\python312\current\pythonw.exe",
            "pwsh": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "ahk_v2": r"C:\Program Files\AutoHotkey\v2\AutoHotkey.exe"
        }
        if text in common_paths:
            self.path_input.setText(common_paths[text])

    def load_data(self):
        self.name_input.setText(self.item["name"])
        self.type_combo.setCurrentText(self.item["type"])
        self.path_input.setText(self.item["paths"][0] if self.item["paths"] else "")
        self.args_input.setText(self.item.get("Command", ""))
        self.ps1_input.setText(self.item.get("ps1_command", ""))
        self.exec_type_combo.setCurrentText(self.item.get("ExecutableType", "other"))

    def save_item(self):
        if not self.name_input.text():
            return
        
        # Default ps1 command if empty
        ps_cmd = self.ps1_input.text()
        if not ps_cmd and self.path_input.text():
            path = self.path_input.text()
            args = self.args_input.text()
            ps_cmd = f'Start-Process -FilePath "{path}"'
            if args:
                ps_cmd += f' -ArgumentList "{args}"'

        self.result_data = {
            "name": self.name_input.text(),
            "type": self.type_combo.currentText(),
            "paths": [self.path_input.text()],
            "Command": self.args_input.text(),
            "ps1_command": ps_cmd,
            "ExecutableType": self.exec_type_combo.currentText(),
            "script_enabled": self.item.get("script_enabled", False) if self.item else False
        }
        self.accept()

class ScanResultsDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.found_items = items
        self.selected_items = []
        self.setWindowTitle("SYSTEM // SCAN_RESULTS")
        self.resize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_DIM}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }}
            QCheckBox {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 11px;
                spacing: 10px;
                padding: 10px;
                border: 1px solid {CP_PANEL};
                background: {CP_PANEL};
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {CP_DIM};
                background: {CP_BG};
            }}
            QCheckBox::indicator:checked {{
                background: {CP_YELLOW};
                border: 1px solid {CP_YELLOW};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {CP_CYAN};
            }}
            QCheckBox:hover {{
                border: 1px solid {CP_DIM};
                background: #1a1a25;
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel(f"DETECTED {len(self.found_items)} NEW ENTRIES")
        header.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {CP_YELLOW};")
        layout.addWidget(header)
        
        sub_header = QLabel("SELECT ITEMS TO IMPORT:")
        sub_header.setStyleSheet(f"color: {CP_SUBTEXT};")
        layout.addWidget(sub_header)
        
        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ border: none; background: transparent; }}
            QWidget {{ background: transparent; }}
            QScrollBar:vertical {{
                background: {CP_BG};
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM};
            }}
        """)
        
        container = QWidget()
        self.vbox = QVBoxLayout(container)
        self.vbox.setSpacing(5)
        self.vbox.setContentsMargins(0, 0, 5, 0)
        
        self.checkboxes = []
        for item in self.found_items:
            path_display = item['paths'][0]
            if len(path_display) > 60: path_display = "..." + path_display[-57:]
            
            cb = QCheckBox(f"{item['name']}\n[{path_display}]")
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setChecked(True) # Default all selected
            self.vbox.addWidget(cb)
            self.checkboxes.append((cb, item))
        
        self.vbox.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = CyberButton("IMPORT SELECTED", color=CP_CYAN)
        add_btn.clicked.connect(self.accept_selection)
        
        cancel_btn = CyberButton("DISCARD", color=CP_RED, is_outlined=True)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def accept_selection(self):
        self.selected_items = [item for cb, item in self.checkboxes if cb.isChecked()]
        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STARTUP // MANAGER_V2.0")
        self.resize(1100, 800)
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }}")
        
        self.items = []
        self.widgets_map = {}
        self.current_mode = "REGISTRY"
        self.ps1_file_path = DEFAULT_PS1
        self.sort_by = "Name" # or "Date"
        self.sort_order = "ASC" # or "DESC"
        
        self.load_items()
        self.setup_ui()
        self.populate_lists() # Populate after UI is ready
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header / Status Bar
        header_layout = QHBoxLayout()
        self.title_lbl = QLabel(f"SYSTEM // STARTUP_CONTROL // {self.current_mode}")
        self.title_lbl.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {CP_YELLOW}; letter-spacing: 2px;")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setFont(QFont("Consolas", 10))
        self.status_label.setStyleSheet(f"color: {CP_CYAN};")
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        # Toolbar Container
        toolbar_container = QWidget()
        toolbar_container.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        toolbar_main_layout = QVBoxLayout(toolbar_container)
        toolbar_main_layout.setContentsMargins(5, 5, 5, 5)
        toolbar_main_layout.setSpacing(5)

        # Row 1: Core Actions
        row1_layout = QHBoxLayout()
        row1_layout.setContentsMargins(5, 5, 5, 5)
        
        # Mode Toggle - color based on loaded mode
        mode_color = CP_CYAN if self.current_mode == "REGISTRY" else CP_YELLOW
        self.mode_btn = CyberButton(f"MODE: {self.current_mode}", color=mode_color, parent=self, is_outlined=False)
        self.mode_btn.setFixedWidth(160)
        self.mode_btn.clicked.connect(self.toggle_mode)
        row1_layout.addWidget(self.mode_btn)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet(f"color: {CP_DIM};")
        row1_layout.addWidget(sep)

        row1_layout.addWidget(CyberButton("NEW_ENTRY", color=CP_YELLOW, parent=self, is_outlined=True))
        row1_layout.itemAt(2).widget().clicked.connect(self.add_item)
        
        row1_layout.addWidget(CyberButton("REFRESH", color=CP_CYAN, parent=self, is_outlined=True))
        row1_layout.itemAt(3).widget().clicked.connect(self.refresh_items)

        row1_layout.addWidget(CyberButton("OPEN_DIRS", color=CP_YELLOW, parent=self, is_outlined=True))
        row1_layout.itemAt(4).widget().clicked.connect(self.open_startup_dirs)
        
        row1_layout.addWidget(CyberButton("PS1_PATH", color="#00FF00", parent=self, is_outlined=True))
        row1_layout.itemAt(5).widget().clicked.connect(self.select_ps1_path)

        row1_layout.addStretch()
        
        self.search_input = CyberInput("SEARCH_DB://...", self)
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_items)
        row1_layout.addWidget(self.search_input)
        # Row 2: Scan & Maintenance (Calculated first to be placed ABOVE)
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(5, 5, 5, 5)
        
        row2_layout.addWidget(CyberButton("SCAN_SYS", color=CP_TEXT, parent=self, is_outlined=True))
        row2_layout.itemAt(0).widget().clicked.connect(self.scan_folders)
        
        row2_layout.addWidget(CyberButton("SCAN_REG", color="#FF00FF", parent=self, is_outlined=True))
        row2_layout.itemAt(1).widget().clicked.connect(self.scan_registry)
        
        row2_layout.addWidget(CyberButton("SCAN_TASKS", color="#FFA500", parent=self, is_outlined=True))
        row2_layout.itemAt(2).widget().clicked.connect(self.scan_tasks)
        
        row2_layout.addWidget(CyberButton("PRUNE_LNK", color=CP_RED, parent=self, is_outlined=True))
        row2_layout.itemAt(3).widget().clicked.connect(self.delete_matching_shortcuts)
        
        row2_layout.addStretch()

        # Sorting Controls
        row2_layout.addWidget(QLabel("// SORT: "))
        row2_layout.itemAt(5).widget().setStyleSheet(f"color: {CP_SUBTEXT}; font-family: Consolas; font-size: 10px;")
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Date"])
        self.sort_combo.setCurrentText(self.sort_by)
        self.sort_combo.setFixedWidth(80)
        self.sort_combo.setFixedHeight(30)
        self.sort_combo.setStyleSheet(self.get_combo_style())
        self.sort_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_combo.currentTextChanged.connect(self.change_sort)
        row2_layout.addWidget(self.sort_combo)

        self.order_btn = CyberButton(self.sort_order, color=CP_CYAN, parent=self, is_outlined=True)
        self.order_btn.setFixedWidth(50)
        self.order_btn.setFixedHeight(30)
        self.order_btn.clicked.connect(self.toggle_sort_order)
        row2_layout.addWidget(self.order_btn)

        # Add rows to toolbar - SCAN ROW GOES ON TOP
        toolbar_main_layout.addLayout(row2_layout)
        toolbar_main_layout.addLayout(row1_layout)
        
        main_layout.addWidget(toolbar_container)

        # Splitter for lists
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{ 
                background-color: {CP_DIM}; 
            }}
            QSplitter::handle:hover {{ 
                background-color: {CP_CYAN}; 
            }}
        """)

        # Items Containers
        self.cmd_container = self.create_column_box("CMD_LINE_INTERFACE", splitter)
        self.app_container = self.create_column_box("APPLICATION_LAYER", splitter)
        
        main_layout.addWidget(splitter, stretch=1)

    # ... (other methods)

    def scan_registry(self):
        self.update_status("SCANNING REGISTRY...")
        found_items = []
        names = {i["name"].lower() for i in self.items}

        reg_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
        ]

        for hkey, path in reg_paths:
            try:
                with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                    count = winreg.QueryInfoKey(key)[1]
                    for i in range(count):
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            if name.lower() in names: continue
                            
                            # Simple parsing of command line to get path + args
                            # This is heuristic; value might be quoted path + args or just path
                            cmd = str(value)
                            path_extracted = cmd
                            args_extracted = ""
                            
                            if cmd.startswith('"'):
                                # Quoted path
                                close_quote = cmd.find('"', 1)
                                if close_quote != -1:
                                    path_extracted = cmd[1:close_quote]
                                    args_extracted = cmd[close_quote+1:].strip()
                            else:
                                # Space separated? hard to tell without checking file existence
                                # We'll assume the first token is path if it ends in .exe, else keep as is
                                parts = cmd.split(' ', 1)
                                if parts[0].lower().endswith('.exe'):
                                    path_extracted = parts[0]
                                    args_extracted = parts[1] if len(parts) > 1 else ""
                            
                            ps1_cmd = f'Start-Process -FilePath "{path_extracted}"'
                            if args_extracted:
                                ps1_cmd += f' -ArgumentList "{args_extracted}"'
                                
                            found_items.append({
                                "name": name,
                                "type": "App" if path_extracted.lower().endswith(".exe") else "Command",
                                "paths": [path_extracted],
                                "Command": args_extracted,
                                "ps1_command": ps1_cmd,
                                "ExecutableType": "other",
                                "added_at": time.time()
                            })
                        except:
                            continue
            except:
                continue

        if found_items:
            dialog = ScanResultsDialog(found_items, self)
            if dialog.exec():
                selected = dialog.selected_items
                if selected:
                    self.items.extend(selected)
                    self.save_items()
                    self.populate_lists()
                    self.update_status(f"IMPORTED {len(selected)} REGISTRY ENTRIES")
                else:
                    self.update_status("IMPORT CANCELLED")
        else:
            self.update_status("REGISTRY SCAN COMPLETE: NO NEW ENTRIES")

    def select_ps1_path(self):
        new_path, _ = QFileDialog.getSaveFileName(self, "SELECT PS1 LOCATION", self.ps1_file_path, "PowerShell Script (*.ps1)")
        if new_path:
            self.ps1_file_path = new_path
            self.save_items()
            self.update_status(f"PATH UPDATED: {os.path.basename(new_path)}")

    def open_ps1_file(self):
        if os.path.exists(self.ps1_file_path):
            os.startfile(self.ps1_file_path)
            self.update_status("PS1 SCRIPT OPENED")
        else:
            self.update_status("PS1 NOT FOUND - GENERATING...")
            self.generate_ps1()
            if os.path.exists(self.ps1_file_path): os.startfile(self.ps1_file_path)

    def open_startup_dirs(self):
        # 1. Open common startup folders
        folders = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        ]
        for f in folders:
            try:
                if os.path.exists(f): os.startfile(f)
            except: pass
        
        # 2. Open Registry Editor to the Startup path
        # Note: Computer\ prefix exists in modern Windows, but HKEY_CURRENT_USER works too.
        reg_target = r"Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            # Kill current regedit so it re-reads the registry on next start
            subprocess.run('taskkill /F /IM regedit.exe', shell=True, capture_output=True)
            
            # Update LastKey so it opens at our target path
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Applets\Regedit", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "LastKey", 0, winreg.REG_SZ, reg_target)
            
            # Launch regedit using the Windows 'start' command for best compatibility
            subprocess.Popen('start regedit.exe', shell=True)
        except Exception as e:
            print(f"DEBUG: Registry open failed: {e}")

        self.update_status("FS & REGISTRY SYNCED")

    def create_column_box(self, title, splitter):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel(f"// {title}")
        header.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {CP_SUBTEXT}; padding-bottom: 5px; border-bottom: 2px solid {CP_DIM};")
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; }}
            QWidget {{ background-color: transparent; }}
            QScrollBar:vertical {{
                background: {CP_BG};
                width: 8px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM};
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CP_CYAN};
            }}
        """)
        
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        vbox.setSpacing(8)
        vbox.setContentsMargins(0, 10, 0, 0)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        splitter.addWidget(wrapper)
        
        return vbox # Return the layout to add items to

    def load_items(self):
        try:
            # Load items
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            else:
                self.items = []
                
            # Load settings
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_mode = settings.get("current_mode", "REGISTRY")
                    self.ps1_file_path = settings.get("ps1_file_path", DEFAULT_PS1)
                    self.sort_by = settings.get("sort_by", "Name")
                    self.sort_order = settings.get("sort_order", "ASC")

            # Ensure every item has an added_at timestamp
            changed = False
            now = time.time()
            for item in self.items:
                if "added_at" not in item:
                    item["added_at"] = now
                    changed = True
            if changed:
                self.save_items()
            
            # Since setup_ui might not have been called yet in __init__, we don't populate here if we call this from __init__
            # Actually, I swapped the order in __init__ so I MUST be careful.
        except:
            pass

    def save_items(self):
        try:
            # Save items
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            
            # Save settings
            settings = {
                "current_mode": self.current_mode,
                "ps1_file_path": self.ps1_file_path,
                "sort_by": self.sort_by,
                "sort_order": self.sort_order
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except:
            pass

    def toggle_mode(self):
        if self.current_mode == "REGISTRY":
            self.current_mode = "SCRIPT"
            color = CP_YELLOW
        else:
            self.current_mode = "REGISTRY"
            color = CP_CYAN
            
        self.save_items() # Save the new mode
        self.title_lbl.setText(f"SYSTEM // STARTUP_CONTROL // {self.current_mode}")
        self.mode_btn.setText(f"MODE: {self.current_mode}")
        self.mode_btn.color = color 
        self.mode_btn.update_style()
        self.populate_lists() # Reload widgets with new active state
        self.update_status(f"SWITCHED TO {self.current_mode} MODE")

    def change_sort(self, text):
        self.sort_by = text
        self.save_items()
        self.populate_lists()
        self.update_status(f"SORTED BY {text.upper()}")

    def toggle_sort_order(self):
        self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"
        self.order_btn.setText(self.sort_order)
        self.save_items()
        self.populate_lists()

    def get_combo_style(self):
        return f"""
            QComboBox {{
                background-color: transparent;
                color: {CP_CYAN};
                border: 1px solid {CP_CYAN};
                padding: 5px 15px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 9pt;
            }}
            QComboBox:hover {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
            QComboBox::drop-down {{
                border: 0px;
                width: 0px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                selection-background-color: {CP_CYAN};
                selection-color: {CP_BG};
                border: 1px solid {CP_CYAN};
                outline: none;
            }}
        """

    def populate_lists(self):
        # Clear existing
        while self.cmd_container.count():
            child = self.cmd_container.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        while self.app_container.count():
            child = self.app_container.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        self.widgets_map.clear()

        # Sorting logic
        sorted_items = sorted(self.items, 
                            key=lambda x: x["name"].lower() if self.sort_by == "Name" else x.get("added_at", 0),
                            reverse=(self.sort_order == "DESC"))

        for item in sorted_items:
            is_active = False
            if self.current_mode == "REGISTRY":
                is_active = self.check_registry(item)
            else:
                is_active = item.get("script_enabled", False)

            widget = StartupItemWidget(item, is_active)
            widget.toggled.connect(self.handle_toggle)
            widget.launched.connect(self.handle_launch)
            widget.edited.connect(self.handle_edit)
            widget.deleted.connect(self.handle_delete)
            
            self.widgets_map[item["name"]] = widget
            
            if item.get("type") == "Command":
                self.cmd_container.addWidget(widget)
            else:
                self.app_container.addWidget(widget)

    def check_registry(self, item):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as reg_key:
                winreg.QueryValueEx(reg_key, item["name"])
                return True
        except:
            return False

    def handle_toggle(self, item, current_state):
        should_enable = not current_state
        
        if self.current_mode == "REGISTRY":
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                if should_enable:
                     with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as reg_key:
                        path = item["paths"][0]
                        command = item.get("Command", "")
                        full = f'"{path}" {command}' if command else f'"{path}"'
                        winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, full)
                else:
                     with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_WRITE) as reg_key:
                        winreg.DeleteValue(reg_key, item["name"])
                
                self.widgets_map[item["name"]].set_active(should_enable)
                self.update_status(f"REGISTRY UPDATED: {item['name']} -> {'ON' if should_enable else 'OFF'}")
            except Exception as e:
                self.update_status(f"REGISTRY ERROR: {str(e)}")
        else:
            # SCRIPT MODE
            # We need to find the item in self.items to update it, as item is a dict copy? 
            # Actually item passed from widget is likely the one in self.items if passed by ref.
            # But let's be safe and update self.items then save.
            
            # Update the item active state
            item["script_enabled"] = should_enable 
            self.save_items()
            self.generate_ps1()
            
            # The widget holds the item dict, so if it's the same ref, it's fine.
            self.widgets_map[item["name"]].set_active(should_enable)
            self.update_status(f"SCRIPT UPDATED: {item['name']} -> {'ON' if should_enable else 'OFF'}")

    def generate_ps1(self):
        try:
            content = "# Auto-generated startup script by SYSTEM // STARTUP_CONTROL\n"
            content += "Write-Host 'Initializing Startup Protocol...' -ForegroundColor Cyan\n\n"
            
            enabled_count = 0
            for item in self.items:
                if item.get("script_enabled", False):
                    name = item["name"]
                    cmd = item.get("ps1_command", "")
                    
                    # Fallback generation if ps1_command empty
                    if not cmd:
                         path = item["paths"][0]
                         args = item.get("Command", "")
                         cmd = f'Start-Process -FilePath "{path}"'
                         if args: cmd += f' -ArgumentList "{args}"'
                    
                    content += f"# {name}\n"
                    content += "try {\n"
                    content += f'    Write-Host "Exec: {name}..." -ForegroundColor Yellow\n'
                    content += f'    {cmd}\n'
                    content += "    Write-Host '  [OK]' -ForegroundColor Green\n"
                    content += "} catch {\n"
                    content += f"    Write-Host '  [FAILED] ' $_ -ForegroundColor Red\n"
                    content += "}\n\n"
                    enabled_count += 1
            
            content += "Write-Host 'Startup Sequence Complete.' -ForegroundColor Green\n"
            content += "Start-Sleep -Seconds 3\n"
            
            with open(self.ps1_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.update_status(f"PS1 GENERATED: {enabled_count} ACTIVE ITEMS")
        except Exception as e:
            self.update_status(f"PS1 GENERATION FAILED: {str(e)}")

    def handle_launch(self, item):
        try:
             path = item["paths"][0]
             cmd = item.get("Command", "")
             full = f'"{path}" {cmd}' if cmd else f'"{path}"'
             subprocess.Popen(f'start "" {full}', shell=True)
             self.update_status(f"EXECUTING: {item['name']}")
        except Exception as e:
            self.update_status(f"EXEC FACTOR FAILED: {str(e)}")

    def handle_edit(self, item):
        dialog = ItemDialog(self, item)
        if dialog.exec():
            # Find and replace
            for i, it in enumerate(self.items):
                if it["name"] == item["name"]:
                    self.items[i] = dialog.result_data
                    break
            self.save_items()
            self.populate_lists()
            self.update_status("DATABASE UPDATED")

    def handle_delete(self, item):
        if QMessageBox.question(self, "CONFIRM DELETE", f"PURGE {item['name']}?") == QMessageBox.StandardButton.Yes:
            if self.check_registry(item):
                self.handle_toggle(item, True) # Turn off
            self.items = [i for i in self.items if i["name"] != item["name"]]
            self.save_items()
            self.populate_lists()
            self.update_status("ENTRY PURGED")

    def add_item(self):
        dialog = ItemDialog(self)
        if dialog.exec():
            item = dialog.result_data
            item["added_at"] = time.time()
            self.items.append(item)
            self.save_items()
            self.populate_lists()
            self.update_status("NEW ENTRY LOGGED")

    def refresh_items(self):
        self.load_items()
        self.update_status("RELOAD COMPLETE")

    def resolve_shortcut(self, path):
        try:
            cmd = f"powershell -NoProfile -Command \"(New-Object -ComObject WScript.Shell).CreateShortcut('{path}').TargetPath\""
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, startupinfo=startupinfo)
            stdout, _ = process.communicate()
            result = stdout.strip()
            return result if result else path
        except:
            return path

    def scan_folders(self):
        self.update_status("SCANNING DIRECTORIES...")
        start_folders = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        ]
        found_items = []
        names = {i["name"].lower() for i in self.items}
        
        for d in start_folders:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.lower().endswith(('.exe', '.lnk', '.bat', '.cmd', '.url')):
                        name = os.path.splitext(f)[0]
                        if name.lower() in names: continue
                            
                        full_path = os.path.join(d, f)
                        real_path = full_path
                        
                        if f.lower().endswith('.lnk'):
                            resolved = self.resolve_shortcut(full_path)
                            if resolved and os.path.exists(resolved):
                                real_path = resolved
                        
                        ps1_cmd = f'Start-Process -FilePath "{real_path}"'
                        found_items.append({
                            "name": name,
                            "type": "App" if real_path.lower().endswith(".exe") else "Command",
                            "paths": [real_path],
                            "Command": "", 
                            "ps1_command": ps1_cmd,
                            "ExecutableType": "other",
                            "added_at": time.time()
                        })
        
        if found_items:
            dialog = ScanResultsDialog(found_items, self)
            if dialog.exec():
                selected = dialog.selected_items
                if selected:
                    self.items.extend(selected)
                    self.save_items()
                    
                    # Logic to disable imported tasks
                    for item in selected:
                        if item.get("origin") == "TaskScheduler":
                            task_name = item.get("original_name")
                            try:
                                subprocess.run(f'schtasks /Change /TN "{task_name}" /DISABLE', shell=True, check=True)
                                self.update_status(f"DISABLED TASK: {task_name}")
                            except:
                                self.update_status(f"FAILED TO DISABLE TASK: {task_name}")

                    self.populate_lists()
                    self.update_status(f"IMPORTED {len(selected)} NEW ENTRIES")
                else:
                    self.update_status("IMPORT CANCELLED")
        else:
            self.update_status("SCAN COMPLETE: NO NEW ENTRIES")

    def scan_tasks(self):
        self.update_status("SCANNING TASK SCHEDULER...")
        # Force UI update
        QApplication.processEvents()
        
        found_items = []
        names = {i["name"].lower() for i in self.items}
        
        try:
            # Robust PowerShell command to get ALL enabled tasks with actions
            # We filter in Python to avoid PowerShell pipeline complexity issues
            ps_cmd = """
            Get-ScheduledTask | Where-Object { $_.State -ne 'Disabled' } | ForEach-Object {
                $t = $_
                $action = $t.Actions[0]
                if ($action.Execute) {
                    $isLogon = $false
                    foreach ($trig in $t.Triggers) {
                        if ($trig.ToString() -match 'Logon' -or $trig.Id -eq 'LogonTrigger') { 
                            $isLogon = $true 
                        }
                    }
                    
                    if ($isLogon) {
                        [PSCustomObject]@{
                            TaskName = $t.TaskName
                            Execute = $action.Execute
                            Arguments = $action.Arguments
                        }
                    }
                }
            } | ConvertTo-Json -Compress
            """
            
            # Use specific encoding handling for PowerShell output
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_cmd], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                     text=True, startupinfo=startupinfo)
            stdout, stderr = process.communicate()
            
            if stderr and not stdout:
                print(f"PS Error: {stderr}")
                self.update_status("TASK SCAN ERROR: PS EXEC FAILED")
                return

            # Handle case where ConvertTo-Json returns a single object (dict) or list (list)
            # PowerShell's ConvertTo-Json has a quirk where single items aren't wrapped in a list
            data = []
            cleaned_out = stdout.strip()
            if cleaned_out:
                try:
                    parsed = json.loads(cleaned_out)
                    if isinstance(parsed, dict):
                        data = [parsed]
                    elif isinstance(parsed, list):
                        data = parsed
                except json.JSONDecodeError:
                    # sometimes header noise or multiple JSON blobs
                    self.update_status("TASK SCAN ERROR: INVALID JSON")
                    return

            count_found = 0
            for task in data:
                task_name = task.get("TaskName", "")
                exe_path = task.get("Execute", "")
                args = task.get("Arguments", "")
                
                if not exe_path: continue
                
                # Cleanup path (unquote if needed)
                exe_path = exe_path.strip('"')
                
                # Determine simple name
                simple_name = task_name.split('\\')[-1]
                
                # Filter duplicates
                if simple_name.lower() in names: continue
                
                # Build PS command
                ps1_cmd = f'Start-Process -FilePath "{exe_path}"'
                if args:
                     ps1_cmd += f' -ArgumentList "{args}"'
                
                found_items.append({
                    "name": simple_name,
                    "type": "App" if exe_path.lower().endswith(".exe") else "Command",
                    "paths": [exe_path],
                    "Command": args if args else "",
                    "ps1_command": ps1_cmd,
                    "ExecutableType": "other",
                    "origin": "TaskScheduler",
                    "original_name": task_name,
                    "added_at": time.time()
                })
                count_found += 1

            if found_items:
                dialog = ScanResultsDialog(found_items, self)
                if dialog.exec():
                    selected = dialog.selected_items
                    if selected:
                        self.items.extend(selected)
                        self.save_items()
                        
                        # Logic to disable imported tasks
                        disabled_count = 0
                        for item in selected:
                            if item.get("origin") == "TaskScheduler":
                                origin_name = item.get("original_name")
                                try:
                                    # Use schtasks to disable
                                    subprocess.run(f'schtasks /Change /TN "{origin_name}" /DISABLE', 
                                                 shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    disabled_count += 1
                                except:
                                    pass

                        self.populate_lists()
                        self.update_status(f"IMPORTED {len(selected)} TASKS ({disabled_count} DISABLED IN OS)")
                    else:
                        self.update_status("IMPORT CANCELLED")
            else:
                self.update_status(f"TASK SCAN: 0 NEW (Found {len(data)} total)")
                    
        except Exception as e:
             self.update_status(f"TASK SCAN EXCEPTION: {str(e)}")

    def delete_matching_shortcuts(self):
         start_folders = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        ]
         deleted = 0
         names = {i["name"].lower() for i in self.items}
         for d in start_folders:
             if os.path.exists(d):
                 for f in os.listdir(d):
                     if f.lower().endswith('.lnk'):
                         name = os.path.splitext(f)[0]
                         if name.lower() in names:
                             try:
                                 os.remove(os.path.join(d, f))
                                 deleted += 1
                             except: pass
         self.update_status(f"PRUNE: {deleted} SHORTCUTS ELIMINATED")

    def filter_items(self, text):
        text = text.lower()
        for name, w in self.widgets_map.items():
            visible = text in name.lower() or text in w.item["paths"][0].lower()
            w.setVisible(visible)

    def update_status(self, text):
        self.status_label.setText(text)
        QTimer.singleShot(3000, lambda: self.status_label.setText("SYSTEM READY"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())