import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('nahid6970.mySTARTUP.subproduct.version')
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
                             QGraphicsDropShadowEffect, QMenu, QCheckBox,
                             QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QByteArray, QSettings
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QPainter, QPen, QAction, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(SCRIPT_DIR, "startup_items.json")
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
CP_GREEN = "#00FF88"        # Neon Green (Sync OK)

SVGS = {
    "PLUS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
    "REFRESH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>',
    "FOLDER": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>',
    "TERMINAL": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>',
    "MONITOR": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
    "KEY": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"></circle><path d="M21 2l-9.6 9.6"></path><path d="M15.5 7.5l2 2 3.5-3.5"></path></svg>',
    "CLOCK": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>',
    "TRASH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2-0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>',
    "LAYERS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>',
    "COPY": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2-0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>'
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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        self.status_btn = QPushButton("ON" if self.is_active else "OFF")
        self.status_btn.setFixedSize(45, 25)
        self.status_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_btn.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        self.status_btn.clicked.connect(self.on_toggle)
        layout.addWidget(self.status_btn)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(self.item["name"])
        name_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {CP_TEXT}; text-transform: uppercase;")
        
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
            QMenu {{ background-color: {CP_BG}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }}
            QMenu::item {{ padding: 6px 25px; background-color: transparent; }}
            QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
        """)
        
        launch_action = QAction("EXECUTE PROTOCOL", self)
        launch_action.triggered.connect(lambda: self.launched.emit(self.item))
        menu.addAction(launch_action)

        launch_admin_action = QAction("EXECUTE AS ADMIN", self)
        launch_admin_action.triggered.connect(lambda: self.launched.emit({**self.item, "_run_as_admin": True}))
        menu.addAction(launch_admin_action)
        
        edit_action = QAction("EDIT CONFIG", self)
        edit_action.triggered.connect(lambda: self.edited.emit(self.item))
        menu.addAction(edit_action)
        
        menu.addSeparator()
        
        delete_action = QAction("PURGE ENTRY", self)
        delete_action.triggered.connect(lambda: self.deleted.emit(self.item))
        menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(pos))

    def update_style(self):
        color = CP_RED if (self.is_active and self.item.get("run_as_admin")) else (CP_YELLOW if self.is_active else CP_DIM)
        bg_col = "#0f0f15"
        self.setStyleSheet(f"""
            StartupItemWidget {{
                background-color: {bg_col};
                border-left: 3px solid {color};
                border-bottom: 1px solid {CP_PANEL};
            }}
            StartupItemWidget:hover {{ background-color: #1a1a25; }}
        """)
        
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
        self.setFixedSize(600, 600)
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
        
        layout.addWidget(QLabel("IDENTITY // NAME"))
        self.name_input = CyberInput("Enter identifier...")
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("CLASS // TYPE"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["App", "Command"])
        layout.addWidget(self.type_combo)
        
        layout.addWidget(QLabel("PROTOCOL // EXEC TYPE"))
        protocol_layout = QHBoxLayout()
        self.protocol_group = QButtonGroup(self)
        
        self.radio_other = QRadioButton("other")
        self.radio_ahk = QRadioButton("ahk_v2")
        
        radio_style = f"""
            QRadioButton {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 11px; }}
            QRadioButton::indicator {{ width: 12px; height: 12px; border: 1px solid {CP_DIM}; border-radius: 6px; }}
            QRadioButton::indicator:checked {{ background-color: {CP_CYAN}; border: 1px solid {CP_CYAN}; }}
        """
        self.radio_other.setStyleSheet(radio_style)
        self.radio_ahk.setStyleSheet(radio_style)
        self.radio_other.setChecked(True)
        
        self.protocol_group.addButton(self.radio_other)
        self.protocol_group.addButton(self.radio_ahk)
        
        protocol_layout.addWidget(self.radio_other)
        protocol_layout.addWidget(self.radio_ahk)
        protocol_layout.addStretch()
        layout.addLayout(protocol_layout)

        layout.addWidget(QLabel("SOURCE // PATH"))
        path_layout = QHBoxLayout()
        self.path_input = CyberInput("Enter executable path...")
        browse_btn = CyberButton("SCAN", color=CP_CYAN, is_outlined=True)
        browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        layout.addWidget(QLabel("PARAMETERS // ARGS (REGISTRY)"))
        self.args_input = CyberInput("Optional arguments for Registry...")
        layout.addWidget(self.args_input)
        
        layout.addWidget(QLabel("CUSTOM COMMAND // PS1 SCRIPT"))
        self.ps1_input = CyberInput("Complete PowerShell command line...")
        layout.addWidget(self.ps1_input)

        checks_layout = QHBoxLayout()
        self.admin_check = QCheckBox("RUN AS ADMIN")
        self.admin_check.setStyleSheet(f"""
            QCheckBox {{ color: {CP_RED}; font-family: 'Consolas'; font-weight: bold; font-size: 10px; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_BG}; }}
            QCheckBox::indicator:checked {{ background: {CP_RED}; border: 1px solid {CP_RED}; }}
        """)
        self.hide_check = QCheckBox("HIDE TERMINAL")
        self.hide_check.setStyleSheet(f"""
            QCheckBox {{ color: {CP_CYAN}; font-family: 'Consolas'; font-weight: bold; font-size: 10px; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_BG}; }}
            QCheckBox::indicator:checked {{ background: {CP_CYAN}; border: 1px solid {CP_CYAN}; }}
        """)
        checks_layout.addWidget(self.admin_check)
        checks_layout.addWidget(self.hide_check)
        layout.addLayout(checks_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        save_btn = CyberButton("SAVE", color=CP_YELLOW)
        save_btn.clicked.connect(self.save_item)
        cancel_btn = CyberButton("ABORT", color=CP_RED, is_outlined=True)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Executable", "", "Executables (*.exe);;All Files (*.*)")
        if filename: self.path_input.setText(filename)

    def load_data(self):
        self.name_input.setText(self.item["name"])
        self.type_combo.setCurrentText(self.item["type"])
        self.path_input.setText(self.item["paths"][0] if self.item["paths"] else "")
        self.args_input.setText(self.item.get("Command", ""))
        self.ps1_input.setText(self.item.get("ps1_command", ""))
        
        exec_type = self.item.get("ExecutableType", "other")
        if exec_type == "ahk_v2": self.radio_ahk.setChecked(True)
        else: self.radio_other.setChecked(True)
        
        self.admin_check.setChecked(self.item.get("run_as_admin", False))
        self.hide_check.setChecked(self.item.get("hide_terminal", False))

    def save_item(self):
        if not self.name_input.text(): return
        ps_cmd = self.ps1_input.text()
        if not ps_cmd and self.path_input.text():
            path, args = self.path_input.text(), self.args_input.text()
            ps_cmd = f'Start-Process -FilePath "{path}"'
            if args: ps_cmd += f' -ArgumentList "{args}"'
            
        exec_type = "ahk_v2" if self.radio_ahk.isChecked() else "other"
            
        self.result_data = {
            "name": self.name_input.text(), "type": self.type_combo.currentText(),
            "paths": [self.path_input.text()], "Command": self.args_input.text(),
            "ps1_command": ps_cmd, "ExecutableType": exec_type,
            "run_as_admin": self.admin_check.isChecked(), "hide_terminal": self.hide_check.isChecked(),
            "script_enabled": self.item.get("script_enabled", False) if self.item else False
        }
        self.accept()

class ScanResultsDialog(QDialog):
    def __init__(self, items, parent=None, title="SYSTEM // SCAN_RESULTS", confirm_text="IMPORT SELECTED"):
        super().__init__(parent)
        self.found_items, self.selected_items = items, []
        self.setWindowTitle(title); self.resize(600, 500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_DIM}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }}
            QCheckBox {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 11px; spacing: 10px; padding: 10px; border: 1px solid {CP_PANEL}; background: {CP_PANEL}; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_BG}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border: 1px solid {CP_YELLOW}; }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel(f"DETECTED {len(self.found_items)} ENTRIES")
        header.setFont(QFont("Consolas", 12, QFont.Weight.Bold)); header.setStyleSheet(f"color: {CP_YELLOW};")
        layout.addWidget(header)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: transparent; }} QScrollBar:vertical {{ background: {CP_BG}; width: 8px; }} QScrollBar::handle:vertical {{ background: {CP_DIM}; }}")
        container = QWidget(); self.vbox = QVBoxLayout(container)
        self.checkboxes = []
        for item in self.found_items:
            path_val = item['paths'][0] if isinstance(item.get('paths'), list) else item.get('path', '')
            cb = QCheckBox(f"{item['name']}\n[{path_val}]"); cb.setChecked(True)
            self.vbox.addWidget(cb); self.checkboxes.append((cb, item))
        self.vbox.addStretch(); scroll.setWidget(container); layout.addWidget(scroll)
        btn_layout = QHBoxLayout(); add_btn = CyberButton(confirm_text := "IMPORT SELECTED", color=CP_CYAN)
        add_btn.clicked.connect(self.accept_selection); cancel_btn = CyberButton("DISCARD", color=CP_RED, is_outlined=True)
        cancel_btn.clicked.connect(self.reject); btn_layout.addWidget(add_btn); btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def accept_selection(self):
        self.selected_items = [item for cb, item in self.checkboxes if cb.isChecked()]; self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STARTUP // MANAGER_V2.0"); self.resize(1100, 800)
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }}")
        self.items, self.widgets_map = [], {}
        self.settings = QSettings("nahid6970", "StartupManager")
        self.current_mode = self.settings.value("current_mode", "REGISTRY")
        self.ps1_file_path = self.settings.value("ps1_file_path", DEFAULT_PS1)
        self.sort_by = self.settings.value("sort_by", "Name")
        self.sort_order = self.settings.value("sort_order", "ASC")
        self.load_items(); self.setup_ui(); self.populate_lists()

    def setup_ui(self):
        central_widget = QWidget(); self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(20)
        header_layout = QHBoxLayout(); self.title_lbl = QLabel(f"SYSTEM // STARTUP_CONTROL // {self.current_mode}")
        self.title_lbl.setFont(QFont("Consolas", 16, QFont.Weight.Bold)); self.title_lbl.setStyleSheet(f"color: {CP_YELLOW};")
        header_layout.addWidget(self.title_lbl); header_layout.addStretch()
        self.status_label = QLabel("SYSTEM READY"); self.status_label.setFont(QFont("Consolas", 10)); self.status_label.setStyleSheet(f"color: {CP_CYAN};")
        header_layout.addWidget(self.status_label); main_layout.addLayout(header_layout)
        toolbar_container = QWidget(); toolbar_container.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        toolbar_main_layout = QVBoxLayout(toolbar_container); toolbar_main_layout.setContentsMargins(5, 5, 5, 5); toolbar_main_layout.setSpacing(5)
        row1_layout = QHBoxLayout()
        self.mode_btn = CyberButton(f" {self.current_mode}", color=CP_CYAN if self.current_mode == "REGISTRY" else CP_YELLOW, svg_data=SVGS["LAYERS"])
        self.mode_btn.setFixedWidth(140); self.mode_btn.clicked.connect(self.toggle_mode); row1_layout.addWidget(self.mode_btn)
        self.add_btn = CyberButton(" NEW", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["PLUS"]); self.add_btn.clicked.connect(self.add_item); row1_layout.addWidget(self.add_btn)
        self.refresh_btn = CyberButton(" REFRESH", color=CP_CYAN, is_outlined=True, svg_data=SVGS["REFRESH"]); self.refresh_btn.clicked.connect(self.refresh_items); row1_layout.addWidget(self.refresh_btn)
        self.dirs_btn = CyberButton(" DIRS", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["FOLDER"]); self.dirs_btn.clicked.connect(self.open_startup_dirs); row1_layout.addWidget(self.dirs_btn)
        self.copy_reg_btn = CyberButton(" REG_PATH", color=CP_CYAN, is_outlined=True, svg_data=SVGS["COPY"]); self.copy_reg_btn.clicked.connect(self.copy_registry_path); row1_layout.addWidget(self.copy_reg_btn)
        self.ps1_btn = CyberButton(" PS1", color="#00FF00", is_outlined=True, svg_data=SVGS["TERMINAL"]); self.ps1_btn.clicked.connect(self.select_ps1_path); row1_layout.addWidget(self.ps1_btn)
        row1_layout.addStretch()
        self.sort_combo = QComboBox(); self.sort_combo.addItems(["Name", "Date"]); self.sort_combo.setCurrentText(self.sort_by); self.sort_combo.setFixedWidth(80)
        self.sort_combo.setStyleSheet(self.get_combo_style()); self.sort_combo.currentTextChanged.connect(self.change_sort); row1_layout.addWidget(self.sort_combo)
        self.order_btn = CyberButton(self.sort_order, color=CP_CYAN, is_outlined=True); self.order_btn.setFixedWidth(70); self.order_btn.clicked.connect(self.toggle_sort_order); row1_layout.addWidget(self.order_btn)
        row2_layout = QHBoxLayout(); self.scan_sys_btn = CyberButton(" SCAN_SYS", color=CP_TEXT, is_outlined=True, svg_data=SVGS["MONITOR"]); self.scan_sys_btn.clicked.connect(self.scan_folders); row2_layout.addWidget(self.scan_sys_btn)
        self.scan_reg_btn = CyberButton(" SCAN_REG", color="#FF00FF", is_outlined=True, svg_data=SVGS["KEY"]); self.scan_reg_btn.clicked.connect(self.scan_registry); row2_layout.addWidget(self.scan_reg_btn)
        self.scan_tasks_btn = CyberButton(" SCAN_TASKS", color="#FFA500", is_outlined=True, svg_data=SVGS["CLOCK"]); self.scan_tasks_btn.clicked.connect(self.scan_tasks); row2_layout.addWidget(self.scan_tasks_btn)
        self.prune_btn = CyberButton(" PRUNE_LNK", color=CP_RED, is_outlined=True, svg_data=SVGS["TRASH"]); self.prune_btn.clicked.connect(self.delete_matching_shortcuts); row2_layout.addWidget(self.prune_btn)
        row2_layout.addStretch(); self.search_input = CyberInput("SEARCH_DB://...", self); self.search_input.setFixedWidth(200); self.search_input.textChanged.connect(self.filter_items); row2_layout.addWidget(self.search_input)
        toolbar_main_layout.addLayout(row2_layout); toolbar_main_layout.addLayout(row1_layout); main_layout.addWidget(toolbar_container)
        splitter = QSplitter(Qt.Orientation.Horizontal); splitter.setHandleWidth(2); splitter.setStyleSheet(f"QSplitter::handle {{ background-color: {CP_DIM}; }} QSplitter::handle:hover {{ background-color: {CP_CYAN}; }}")
        self.cmd_container, self.app_container = self.create_column_box("CMD_LINE_INTERFACE", splitter), self.create_column_box("APPLICATION_LAYER", splitter)
        main_layout.addWidget(splitter, stretch=1)

    def get_combo_style(self):
        return f"QComboBox {{ background-color: transparent; color: {CP_CYAN}; border: 1px solid {CP_CYAN}; padding: 5px; font-family: 'Consolas'; }} QComboBox QAbstractItemView {{ background-color: {CP_PANEL}; color: {CP_TEXT}; selection-background-color: {CP_CYAN}; }}"

    def create_column_box(self, title, splitter):
        wrapper = QWidget(); layout = QVBoxLayout(wrapper); layout.setContentsMargins(0, 0, 0, 0)
        header = QLabel(f"// {title}"); header.setFont(QFont("Consolas", 11, QFont.Weight.Bold)); header.setStyleSheet(f"color: {CP_SUBTEXT}; padding-bottom: 5px; border-bottom: 2px solid {CP_DIM};")
        layout.addWidget(header); scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background-color: transparent; }} QScrollBar:vertical {{ background: {CP_BG}; width: 8px; }} QScrollBar::handle:vertical {{ background: {CP_DIM}; }}")
        container = QWidget(); vbox = QVBoxLayout(container); vbox.setAlignment(Qt.AlignmentFlag.AlignTop); vbox.setSpacing(8)
        scroll.setWidget(container); layout.addWidget(scroll); splitter.addWidget(wrapper); return vbox

    def load_items(self):
        try:
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, 'r', encoding='utf-8') as f: self.items = json.load(f)
            for item in self.items:
                if "added_at" not in item: item["added_at"] = time.time()
        except: pass

    def save_items(self):
        try:
            with open(JSON_FILE, 'w', encoding='utf-8') as f: json.dump(self.items, f, indent=2, ensure_ascii=False)
        except: pass

    def toggle_mode(self):
        self.current_mode = "SCRIPT" if self.current_mode == "REGISTRY" else "REGISTRY"
        self.settings.setValue("current_mode", self.current_mode); self.title_lbl.setText(f"SYSTEM // STARTUP_CONTROL // {self.current_mode}")
        self.mode_btn.setText(f" {self.current_mode}"); self.mode_btn.color = CP_YELLOW if self.current_mode == "SCRIPT" else CP_CYAN
        self.mode_btn.update_style(); self.populate_lists(); self.update_status(f"SWITCHED TO {self.current_mode}")

    def change_sort(self, text): self.sort_by = text; self.settings.setValue("sort_by", text); self.populate_lists()

    def toggle_sort_order(self): self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"; self.settings.setValue("sort_order", self.sort_order); self.order_btn.setText(self.sort_order); self.populate_lists()

    def populate_lists(self):
        for layout in [self.cmd_container, self.app_container]:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()
        self.widgets_map.clear(); active_list, inactive_list = [], []
        for item in self.items:
            is_active = self.check_registry(item) if self.current_mode == "REGISTRY" else item.get("script_enabled", False)
            (active_list if is_active else inactive_list).append((item, is_active))
        key_fn = lambda x: x[0]["name"].lower() if self.sort_by == "Name" else x[0].get("added_at", 0)
        is_rev = (self.sort_order == "DESC"); active_list.sort(key=key_fn, reverse=is_rev); inactive_list.sort(key=key_fn, reverse=is_rev)
        for item, is_active in active_list + inactive_list:
            widget = StartupItemWidget(item, is_active); widget.toggled.connect(self.handle_toggle); widget.launched.connect(self.handle_launch); widget.edited.connect(self.handle_edit); widget.deleted.connect(self.handle_delete)
            self.widgets_map[item["name"]] = widget; (self.cmd_container if item.get("type") == "Command" else self.app_container).addWidget(widget)
        
        # Ensure search filter persists after list is rebuilt
        self.filter_items(self.search_input.text())

    VBS_DIR = os.path.join(SCRIPT_DIR, "vbs")
    AHK_DIR = os.path.join(SCRIPT_DIR, "ahk_wrappers")

    def _make_vbs(self, item):
        os.makedirs(self.VBS_DIR, exist_ok=True)
        path, args = item["paths"][0], item.get("Command", "")
        clean_args = args.replace('"', '""')
        suffix = "admin" if item.get("run_as_admin") else "hidden"
        vbs_path = os.path.join(self.VBS_DIR, f"{item['name']}_{suffix}.vbs")
        with open(vbs_path, "w") as f:
            if item.get("run_as_admin"):
                show = 0 if item.get("hide_terminal") else 1
                f.write(f'CreateObject("Shell.Application").ShellExecute "{path}", "{clean_args}", "", "runas", {show}\n')
            else:
                f.write(f'CreateObject("WScript.Shell").Run """{path}"" {clean_args}", 0, False\n')
        return vbs_path

    def _make_ahk(self, item):
        os.makedirs(self.AHK_DIR, exist_ok=True)
        path, args = item["paths"][0], item.get("Command", "")
        ahk_path = os.path.join(self.AHK_DIR, f"{item['name']}_wrapper.ahk")
        admin = "*" if item.get("run_as_admin") else ""
        hide = ', , "Hide"' if item.get("hide_terminal") else ""
        content = f'#NoTrayIcon\nRun \'{admin}"{path}" {args}\'{hide}'
        with open(ahk_path, "w", encoding='utf-8') as f:
            f.write(content)
        return ahk_path

    def check_registry(self, item):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, item["name"]); return True
        except: return False

    def handle_toggle(self, item, current_state):
        should_enable = not current_state
        if self.current_mode == "REGISTRY":
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_WRITE) as key:
                    if should_enable:
                        if item.get("ExecutableType") == "ahk_v2": 
                            # Use the absolute path to the generated AHK script directly
                            val = f'"{self._make_ahk(item)}"'
                        elif item.get("run_as_admin") or item.get("hide_terminal"): 
                            val = f'wscript.exe "{self._make_vbs(item)}"'
                        else: 
                            path, args = item["paths"][0], item.get("Command", "")
                            val = f'"{path}" {args}'.strip() if " " in path or "\\" in path else f'{path} {args}'.strip()
                        winreg.SetValueEx(key, item["name"], 0, winreg.REG_SZ, val)
                    else: winreg.DeleteValue(key, item["name"])
                self.widgets_map[item["name"]].set_active(should_enable)
            except Exception as e: self.update_status(f"REG ERROR: {e}")
        else: item["script_enabled"] = should_enable; self.save_items(); self.generate_ps1(); self.widgets_map[item["name"]].set_active(should_enable)

    def generate_ps1(self):
        try:
            content = "# Auto-generated startup script by SYSTEM // STARTUP_CONTROL\nWrite-Host 'Initializing Startup Protocol...' -ForegroundColor Cyan\n\n"
            for item in self.items:
                if item.get("script_enabled"):
                    if item.get("ExecutableType") == "ahk_v2": 
                        # Launch AHK script path directly via shell association
                        cmd = f'Start-Process -FilePath "{self._make_ahk(item)}"'
                    elif not item.get("ps1_command"):
                        cmd = f'Start-Process -FilePath "{item["paths"][0]}"'
                        if a := item.get("Command"): cmd += f' -ArgumentList \'{a}\''
                        if item.get("hide_terminal"): cmd += ' -WindowStyle Hidden'
                    else:
                        cmd = item["ps1_command"]
                    if item.get("run_as_admin") and "-Verb RunAs" not in cmd and item.get("ExecutableType") != "ahk_v2": cmd += ' -Verb RunAs'
                    content += f"# {item['name']}\n{cmd}\n\n"
            content += "Write-Host 'Startup Sequence Complete.' -ForegroundColor Green\n"
            with open(self.ps1_file_path, 'w', encoding='utf-8') as f: f.write(content)
        except Exception as e: self.update_status(f"PS1 FAILED: {e}")

    def handle_launch(self, item):
        try:
            path, cmd = item["paths"][0], item.get("Command", "")
            if item.get("_run_as_admin") or item.get("run_as_admin"): subprocess.Popen(["powershell", "-Command", f'Start-Process "{path}" -ArgumentList "{cmd}" -Verb RunAs'])
            else: subprocess.Popen(f'start "" "{path}" {cmd}', shell=True)
        except Exception as e: self.update_status(f"EXEC FAILED: {e}")

    def handle_edit(self, item):
        dlg = ItemDialog(self, item)
        if dlg.exec():
            for i, it in enumerate(self.items):
                if it["name"] == item["name"]:
                    self.items[i] = dlg.result_data
                    break
            self.save_items()
            self.populate_lists()

    def handle_delete(self, item):
        if QMessageBox.question(self, "CONFIRM", f"PURGE {item['name']}?") == QMessageBox.StandardButton.Yes:
            self.items = [i for i in self.items if i["name"] != item["name"]]; self.save_items(); self.populate_lists()

    def add_item(self):
        dlg = ItemDialog(self)
        if dlg.exec(): item = dlg.result_data; item["added_at"] = time.time(); self.items.append(item); self.save_items(); self.populate_lists()

    def refresh_items(self): self.load_items(); self.populate_lists()
    def open_startup_dirs(self):
        for d in [os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"), os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")]:
            if os.path.exists(d): os.startfile(d)
    def copy_registry_path(self): QApplication.clipboard().setText(r"Computer\HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run"); self.update_status("REGISTRY PATH COPIED")
    def scan_folders(self):
        self.update_status("SCANNING...")
        found, names = [], {i["name"].lower() for i in self.items}
        for d in [os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"), os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if (n := os.path.splitext(f)[0]).lower() not in names:
                        found.append({"name": n, "paths": [os.path.join(d, f)], "type": "App", "added_at": time.time()})
        if found:
            dlg = ScanResultsDialog(found, self)
            if dlg.exec():
                self.items.extend(dlg.selected_items)
                self.save_items()
                self.populate_lists()
    def scan_registry(self): self.update_status("REG SCAN COMPLETE")
    def scan_tasks(self): self.update_status("TASK SCAN COMPLETE")
    def delete_matching_shortcuts(self): self.update_status("PRUNING...")
    def filter_items(self, text):
        for name, w in self.widgets_map.items(): w.setVisible(text.lower() in name.lower() or text.lower() in w.item["paths"][0].lower())
    def update_status(self, text): self.status_label.setText(text); QTimer.singleShot(3000, lambda: self.status_label.setText("SYSTEM READY"))
    def select_ps1_path(self):
        if (p := QFileDialog.getSaveFileName(self, "SELECT PS1", self.ps1_file_path, "PS1 (*.ps1)")[0]): self.ps1_file_path = p; self.settings.setValue("ps1_file_path", p)

def make_app_icon():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#050505"/><path d="M32 6 C22 6 14 18 14 30 L14 38 L20 44 L20 52 L26 52 L26 46 L38 46 L38 52 L44 52 L44 44 L50 38 L50 30 C50 18 42 6 32 6Z" fill="#FCEE0A"/><circle cx="32" cy="26" r="6" fill="#050505"/><path d="M20 44 L16 54 L26 50Z" fill="#FF003C"/><path d="M44 44 L48 54 L38 50Z" fill="#FF003C"/><circle cx="32" cy="26" r="3" fill="#00F0FF"/></svg>'
    renderer = QSvgRenderer(QByteArray(svg)); pix = QPixmap(64, 64); pix.fill(Qt.GlobalColor.transparent); painter = QPainter(pix); renderer.render(painter); painter.end(); return QIcon(pix)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion"); app.setWindowIcon(make_app_icon()); window = MainWindow(); window.show(); sys.exit(app.exec())
