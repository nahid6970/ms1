#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import time
import urllib.request
import difflib
import shlex
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QScrollArea, QFrame, QMessageBox, QDialog, 
                             QComboBox, QFileDialog, QSplitter, QGraphicsEffect,
                             QGraphicsDropShadowEffect, QMenu, QCheckBox)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QByteArray
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QPainter, QPen, QAction, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer

# Constants
CONFIG_DIR = os.path.expanduser("~/.config/startup_manager")
JSON_FILE = os.path.join(CONFIG_DIR, "startup_items.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
DEFAULT_SH = os.path.join(CONFIG_DIR, "startup.sh")
AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")

CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "startup_manager_linux"

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
    "CLOUD_UP": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 16l-4-4-4 4M12 12v9"></path><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"></path></svg>',
    "CLOUD_DOWN": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 17l4 4 4-4M12 12v9"></path><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"></path></svg>',
    "UPLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',
    "DOWNLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',
    "LAYERS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>',
    "DIFF": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>'
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
        
        self.border_color = CP_RED if (self.is_active and self.item.get("run_as_admin")) else (CP_YELLOW if self.is_active else CP_DIM)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)
        
        self.status_btn = QPushButton("OFF")
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
        
        raw_path = self.item["paths"][0] if self.item.get("paths") else ""
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

        launch_admin_action = QAction("EXECUTE AS ADMIN (ROOT)", self)
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
            StartupItemWidget:hover {{
                background-color: #1a1a25;
            }}
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
        self.exec_type_combo = QComboBox()
        self.exec_type_combo.addItems(["other", "sh", "bash", "python3"])
        layout.addWidget(self.exec_type_combo)

        layout.addWidget(QLabel("SOURCE // PATH OR COMMAND"))
        path_layout = QHBoxLayout()
        self.path_input = CyberInput("Enter executable path or command...")
        browse_btn = CyberButton("SCAN", color=CP_CYAN, is_outlined=True)
        browse_btn.clicked.connect(self.browse_file)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        layout.addWidget(QLabel("PARAMETERS // ARGS"))
        self.args_input = CyberInput("Optional arguments...")
        layout.addWidget(self.args_input)
        
        layout.addWidget(QLabel("CUSTOM COMMAND // SHELL SCRIPT COMMAND"))
        self.sh_input = CyberInput("Complete bash command line...")
        layout.addWidget(self.sh_input)

        self.admin_check = QCheckBox("RUN AS ADMIN (ROOT VIA PKEXEC)")
        self.admin_check.setStyleSheet(f"""
            QCheckBox {{ color: {CP_RED}; font-family: 'Consolas'; font-weight: bold; font-size: 10px; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_BG}; }}
            QCheckBox::indicator:checked {{ background: {CP_RED}; border: 1px solid {CP_RED}; }}
        """)
        layout.addWidget(self.admin_check)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        save_btn = CyberButton("UPLOAD", color=CP_YELLOW)
        save_btn.clicked.connect(self.save_item)
        cancel_btn = CyberButton("ABORT", color=CP_RED, is_outlined=True)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Executable/Script", "/usr/bin", "All Files (*.*)")
        if filename: self.path_input.setText(filename)

    def load_data(self):
        self.name_input.setText(self.item["name"])
        self.type_combo.setCurrentText(self.item["type"])
        self.path_input.setText(self.item["paths"][0] if self.item.get("paths") else "")
        self.args_input.setText(self.item.get("Command", ""))
        self.sh_input.setText(self.item.get("sh_command", ""))
        self.exec_type_combo.setCurrentText(self.item.get("ExecutableType", "other"))
        self.admin_check.setChecked(self.item.get("run_as_admin", False))

    def save_item(self):
        if not self.name_input.text():
            return
        
        sh_cmd = self.sh_input.text()
        if not sh_cmd and self.path_input.text():
            path = self.path_input.text()
            args = self.args_input.text()
            sh_cmd = f'"{path}"'
            if args:
                sh_cmd += f' {args}'

        self.result_data = {
            "name": self.name_input.text(),
            "type": self.type_combo.currentText(),
            "paths": [self.path_input.text()],
            "Command": self.args_input.text(),
            "sh_command": sh_cmd,
            "ExecutableType": self.exec_type_combo.currentText(),
            "run_as_admin": self.admin_check.isChecked(),
            "script_enabled": self.item.get("script_enabled", False) if self.item else False
        }
        self.accept()

class ScanResultsDialog(QDialog):
    def __init__(self, items, parent=None, title="SYSTEM // SCAN_RESULTS", confirm_text="IMPORT SELECTED"):
        super().__init__(parent)
        self.found_items = items
        self.selected_items = []
        self.dialog_title = title
        self.confirm_text = confirm_text
        self.setWindowTitle(title)
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
        
        header = QLabel(f"DETECTED {len(self.found_items)} ENTRIES")
        header.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {CP_YELLOW};")
        layout.addWidget(header)
        
        sub_header = QLabel(f"{self.dialog_title} - SELECT ITEMS:")
        sub_header.setStyleSheet(f"color: {CP_SUBTEXT};")
        layout.addWidget(sub_header)

        self.search_input = CyberInput("FILTER_RESULTS://...", self)
        self.search_input.textChanged.connect(self.filter_results)
        layout.addWidget(self.search_input)
        
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
            path_val = item['paths'][0] if isinstance(item.get('paths'), list) and item.get('paths') else item.get('path', '')
            path_display = path_val
            if len(path_display) > 60: path_display = "..." + path_display[-57:]
            
            cb = QCheckBox(f"{item['name']}\n[{path_display}]")
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setChecked(True)
            self.vbox.addWidget(cb)
            self.checkboxes.append((cb, item))
        
        self.vbox.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        add_btn = CyberButton(self.confirm_text, color=CP_CYAN)
        add_btn.clicked.connect(self.accept_selection)
        
        cancel_btn = CyberButton("DISCARD", color=CP_RED, is_outlined=True)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def accept_selection(self):
        self.selected_items = [item for cb, item in self.checkboxes if cb.isChecked()]
        self.accept()

    def filter_results(self, text):
        text = text.lower()
        for cb, item in self.checkboxes:
            path_val = item['paths'][0] if isinstance(item.get('paths'), list) and item.get('paths') else item.get('path', '')
            visible = text in item['name'].lower() or text in path_val.lower()
            cb.setVisible(visible)

class DiffDialog(QDialog):
    def __init__(self, local_data, remote_data, title="SYSTEM // DIFF_VIEW", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(900, 700)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }}")
        
        layout = QVBoxLayout(self)
        
        header = QLabel("COMPARISON: REMOTE (RED) vs LOCAL (GREEN)")
        header.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {CP_YELLOW}; padding: 5px;")
        layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ border: 1px solid {CP_DIM}; background-color: {CP_PANEL}; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {CP_DIM}; }}
        """)
        
        content = QWidget()
        content.setStyleSheet(f"background-color: {CP_PANEL};")
        vbox = QVBoxLayout(content)
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 5, 5, 5)

        def fix(obj):
            if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
            if isinstance(obj, list): return [fix(i) for i in obj]
            if isinstance(obj, float) and obj.is_integer(): return int(obj)
            return obj

        local_str = json.dumps(fix(local_data), indent=2, sort_keys=True).splitlines()
        remote_str = json.dumps(fix(remote_data), indent=2, sort_keys=True).splitlines()
        
        diff = list(difflib.unified_diff(remote_str, local_str, fromfile='Backup', tofile='Local', lineterm=''))
        
        if not diff:
            lbl = QLabel("No differences detected.")
            lbl.setStyleSheet(f"color: {CP_GREEN}; font-family: 'Consolas'; padding: 10px;")
            vbox.addWidget(lbl)
        else:
            for line in diff:
                lbl = QLabel(line)
                lbl.setFont(QFont("Consolas", 9))
                if line.startswith('+'):
                    lbl.setStyleSheet("background-color: #12261e; color: #3fb950; padding: 1px 4px;")
                elif line.startswith('-'):
                    lbl.setStyleSheet("background-color: #2c1619; color: #f85149; padding: 1px 4px;")
                elif line.startswith('@@'):
                    lbl.setStyleSheet(f"background-color: #0d1117; color: {CP_CYAN}; padding: 1px 4px;")
                else:
                    lbl.setStyleSheet(f"color: {CP_TEXT}; padding: 1px 4px;")
                vbox.addWidget(lbl)
        
        vbox.addStretch()
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)
        
        close = CyberButton("CLOSE PROTOCOL", color=CP_DIM, is_outlined=True)
        close.clicked.connect(self.accept)
        layout.addWidget(close)

class ConvexLabelDialog(QDialog):
    def __init__(self, parent=None, convex_call_fn=None, config_data=None):
        super().__init__(parent)
        self.setWindowTitle("BACKUP LABEL")
        self.setFixedWidth(420)
        self._convex_call = convex_call_fn
        self._config_data = config_data or []
        self._remote_data = None
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_CYAN}; }} QLabel {{ color: {CP_TEXT}; }} QLineEdit {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px; font-family: Consolas; }}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter a label for this backup:"))
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("e.g. before v2 update")
        layout.addWidget(self.inp)

        self.status_lbl = QLabel("")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setStyleSheet("font-family: Consolas; font-size: 9pt; padding: 4px;")
        layout.addWidget(self.status_lbl)

        btns = QHBoxLayout()
        ok = CyberButton("BACKUP", color=CP_CYAN)
        ok.clicked.connect(self.accept)
        self.check_btn = CyberButton("CHECK", color=CP_YELLOW, is_outlined=True)
        self.check_btn.clicked.connect(self._check_sync)
        
        self.diff_btn = CyberButton("SHOW DIFF", color=CP_YELLOW, is_outlined=True)
        self.diff_btn.clicked.connect(self._show_diff)
        self.diff_btn.hide()

        cancel = CyberButton("CANCEL", color=CP_DIM, is_outlined=True)
        cancel.clicked.connect(self.reject)
        
        btns.addWidget(ok); btns.addWidget(self.check_btn); btns.addWidget(self.diff_btn); btns.addWidget(cancel)
        layout.addLayout(btns)

    def _show_diff(self):
        if self._remote_data is not None:
            DiffDialog(self._config_data, self._remote_data, parent=self).exec()

    def _check_sync(self):
        if not self._convex_call:
            self.status_lbl.setText("No connection available.")
            return
        try:
            self.check_btn.setEnabled(False)
            self.status_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: Consolas; font-size: 9pt; padding: 4px;")
            self.status_lbl.setText("Checking...")
            QApplication.processEvents()
            result = self._convex_call("query", {"path": "functions:list", "args": {"scriptName": SCRIPT_NAME}})
            backups = result.get("value", [])
            if not backups:
                self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText("⚠ No backups found — backup recommended!")
                return
            latest = max(backups, key=lambda b: b["createdAt"])
            remote_raw = self._convex_call("query", {"path": "functions:get", "args": {"id": latest["id"]}}).get("value", [])
            
            def fix(obj):
                if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
                if isinstance(obj, list): return [fix(i) for i in obj]
                if isinstance(obj, float) and obj.is_integer(): return int(obj)
                return obj
            
            self._remote_data = fix(remote_raw)
            dirty = json.dumps(self._config_data, sort_keys=True) != json.dumps(self._remote_data, sort_keys=True)
            
            if dirty:
                self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText(f"⚠ OUT OF SYNC with '{latest['label']}' — backup recommended!")
                self.diff_btn.show()
            else:
                self.status_lbl.setStyleSheet(f"color: {CP_GREEN}; font-family: Consolas; font-size: 9pt; padding: 4px;")
                self.status_lbl.setText(f"✔ In sync with '{latest['label']}' — no backup needed.")
                self.diff_btn.hide()
        except Exception as e:
            self.status_lbl.setStyleSheet(f"color: {CP_RED}; font-family: Consolas; font-size: 9pt; padding: 4px;")
            self.status_lbl.setText(f"Error: {e}")
        finally:
            self.check_btn.setEnabled(True)

    @staticmethod
    def get_label(parent=None, convex_call_fn=None, config_data=None):
        dlg = ConvexLabelDialog(parent, convex_call_fn=convex_call_fn, config_data=config_data)
        ok = dlg.exec() == QDialog.DialogCode.Accepted
        return dlg.inp.text(), ok

class RestoreDialog(QDialog):
    def __init__(self, backups, convex_call_fn, local_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RESTORE FROM BACKUP")
        self.setFixedWidth(550)
        self.selected_id = None
        self._convex_call = convex_call_fn
        self._backups = list(backups)
        self._local_data = local_data
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_YELLOW}; }} QLabel {{ color: {CP_TEXT}; }} QPushButton {{ background: {CP_DIM}; color: white; padding: 6px 14px; border: 1px solid {CP_DIM}; }} QPushButton:hover {{ border: 1px solid {CP_YELLOW}; }}")
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(QLabel("Select a backup to restore:"))
        
        self.search_input = CyberInput("FILTER_BACKUPS://...", self)
        self.search_input.textChanged.connect(self.filter_backups)
        self._layout.addWidget(self.search_input)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: 1px solid #3a3a3a;")
        self._scroll.setFixedHeight(300)
        self._layout.addWidget(self._scroll)
        cancel = QPushButton("CANCEL")
        cancel.clicked.connect(self.reject)
        self._layout.addWidget(cancel)
        self._rows = []
        self._render_list()

    def _render_list(self):
        import datetime
        inner = QWidget()
        inner.setStyleSheet(f"background: {CP_PANEL};")
        vbox = QVBoxLayout(inner)
        vbox.setSpacing(4)
        vbox.setContentsMargins(4, 4, 4, 4)
        self._rows.clear()
        for b in self._backups:
            dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M %p")
            
            row_widget = QWidget()
            row = QHBoxLayout(row_widget)
            row.setSpacing(4)
            row.setContentsMargins(0, 0, 0, 0)

            btn = QPushButton(f"  {dt}  ->  {b['label']}")
            btn.setStyleSheet(f"text-align: left; padding: 8px; background: {CP_BG}; color: {CP_TEXT}; border: 1px solid #2a2a2a; font-family: 'Consolas'; font-size: 10pt; font-weight: bold;")
            btn.clicked.connect(lambda checked, bid=b["id"]: self._select(bid))

            diff_btn = QPushButton()
            diff_btn.setFixedSize(32, 32)
            diff_btn.setToolTip("Compare with local config")
            diff_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")

            renderer_diff = QSvgRenderer(QByteArray(SVGS["DIFF"].replace('currentColor', CP_YELLOW).encode()))
            pix_diff = QPixmap(22, 22)
            pix_diff.fill(Qt.GlobalColor.transparent)
            painter_diff = QPainter(pix_diff)
            renderer_diff.render(painter_diff)
            painter_diff.end()
            diff_btn.setIcon(QIcon(pix_diff))
            diff_btn.clicked.connect(lambda checked, bid=b["id"]: self._diff(bid))

            del_btn = QPushButton()
            del_btn.setFixedSize(32, 32)
            del_btn.setToolTip("Delete this backup")
            del_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")

            renderer = QSvgRenderer(QByteArray(SVGS["TRASH"].replace('currentColor', CP_RED).encode()))
            pix = QPixmap(22, 22)
            pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pix)
            renderer.render(painter)
            painter.end()
            del_btn.setIcon(QIcon(pix))
            del_btn.clicked.connect(lambda checked, bid=b["id"]: self._delete(bid))

            row.addWidget(btn)
            row.addWidget(diff_btn)
            row.addWidget(del_btn)
            vbox.addWidget(row_widget)
            self._rows.append((row_widget, b, dt))
        vbox.addStretch()
        self._scroll.setWidget(inner)

    def filter_backups(self, text):
        text = text.lower()
        for widget, b, dt in self._rows:
            visible = text in b['label'].lower() or text in dt.lower()
            widget.setVisible(visible)

    def _select(self, bid):
        self.selected_id = bid
        self.accept()

    def _diff(self, backup_id):
        try:
            data = self._convex_call("query", {
                "path": "functions:get",
                "args": {"id": backup_id}
            }).get("value")
            if data:
                DiffDialog(self._local_data, data, parent=self).exec()
        except Exception as e:
            QMessageBox.critical(self, "DIFF FAILED", str(e))

    def _delete(self, backup_id):
        if QMessageBox.question(self, "DELETE BACKUP", "Permanently delete this backup?") == QMessageBox.StandardButton.Yes:
            try:
                self._convex_call("mutation", {
                    "path": "functions:deleteBackup",
                    "args": {"id": backup_id}
                })
                self._backups = [b for b in self._backups if b["id"] != backup_id]
                self._render_list()
            except Exception as e:
                QMessageBox.critical(self, "DELETE FAILED", str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SYSTEM // STARTUP_CONTROL")
        self.resize(1100, 750)
        self.items = []
        self.widgets_map = {}
        
        # Default modes and paths
        self.current_mode = "AUTOSTART" # "AUTOSTART" or "SCRIPT"
        self.sh_file_path = DEFAULT_SH
        self.sort_by = "Name"
        self.sort_order = "ASC"
        
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(AUTOSTART_DIR, exist_ok=True)
        
        self.load_items()
        self.setup_ui()
        self.populate_lists()
        self.update_status("SYSTEM ONLINE")

    def setup_ui(self):
        # Palette setup
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(CP_BG))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(CP_TEXT))
        self.setPalette(palette)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header bar
        header_layout = QHBoxLayout()
        self.title_lbl = QLabel(f"SYSTEM // STARTUP_CONTROL // {self.current_mode}")
        self.title_lbl.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color: {CP_YELLOW}; letter-spacing: 2px;")
        header_layout.addWidget(self.title_lbl)
        
        header_layout.addStretch()
        
        # Backup / Restore / Sync
        backup_btn = CyberButton("BACKUP", color=CP_CYAN, is_outlined=True, svg_data=SVGS["CLOUD_UP"])
        backup_btn.clicked.connect(self.backup_to_convex)
        restore_btn = CyberButton("RESTORE", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["CLOUD_DOWN"])
        restore_btn.clicked.connect(self.restore_from_convex)
        header_layout.addWidget(backup_btn)
        header_layout.addWidget(restore_btn)
        
        main_layout.addLayout(header_layout)

        # Toolbar
        toolbar_container = QFrame()
        toolbar_container.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        toolbar_main_layout = QVBoxLayout(toolbar_container)
        toolbar_main_layout.setContentsMargins(15, 10, 15, 10)
        toolbar_main_layout.setSpacing(8)

        # Toolbar Row 1: Core actions
        row1_layout = QHBoxLayout()
        
        add_btn = CyberButton("NEW ENTRY", color=CP_YELLOW, svg_data=SVGS["PLUS"])
        add_btn.clicked.connect(self.add_item)
        row1_layout.addWidget(add_btn)

        # Scan button menu
        scan_btn = CyberButton("SCAN SYSTEM", color=CP_CYAN, is_outlined=True, svg_data=SVGS["REFRESH"])
        scan_menu = QMenu(self)
        scan_menu.setFont(QFont("Consolas", 9))
        scan_menu.setStyleSheet(f"QMenu {{ background-color: {CP_BG}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}")
        
        scan_autostart_act = QAction("Scan Autostart Desktop Files", self)
        scan_autostart_act.triggered.connect(self.scan_autostart_dirs)
        scan_menu.addAction(scan_autostart_act)

        scan_systemd_act = QAction("Scan Systemd Services", self)
        scan_systemd_act.triggered.connect(self.scan_systemd_services)
        scan_menu.addAction(scan_systemd_act)

        scan_btn.setMenu(scan_menu)
        row1_layout.addWidget(scan_btn)

        # Folder sync menu
        folder_btn = CyberButton("SYSTEM DIRS", color=CP_CYAN, is_outlined=True, svg_data=SVGS["FOLDER"])
        folder_menu = QMenu(self)
        folder_menu.setFont(QFont("Consolas", 9))
        folder_menu.setStyleSheet(f"QMenu {{ background-color: {CP_BG}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}")
        
        open_autostart_act = QAction("Open Autostart Folder", self)
        open_autostart_act.triggered.connect(self.open_autostart_dir)
        folder_menu.addAction(open_autostart_act)
        
        open_settings_act = QAction("Open KDE Autostart Settings", self)
        open_settings_act.triggered.connect(self.open_kde_settings)
        folder_menu.addAction(open_settings_act)

        folder_btn.setMenu(folder_menu)
        row1_layout.addWidget(folder_btn)

        row1_layout.addStretch()

        # Mode toggle
        mode_label = QLabel("MODE:")
        mode_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        mode_label.setStyleSheet(f"color: {CP_SUBTEXT};")
        row1_layout.addWidget(mode_label)

        self.mode_btn = CyberButton(f" {self.current_mode}", color=CP_CYAN, is_outlined=True, svg_data=SVGS["LAYERS"])
        self.mode_btn.clicked.connect(self.toggle_mode)
        row1_layout.addWidget(self.mode_btn)

        # Script actions (visible in SCRIPT mode)
        self.script_actions_widget = QWidget()
        script_act_layout = QHBoxLayout(self.script_actions_widget)
        script_act_layout.setContentsMargins(0, 0, 0, 0)
        script_act_layout.setSpacing(5)
        
        sh_path_btn = CyberButton("SH PATH", color=CP_YELLOW, is_outlined=True)
        sh_path_btn.clicked.connect(self.select_sh_path)
        script_act_layout.addWidget(sh_path_btn)

        open_sh_btn = CyberButton("OPEN SH", color=CP_CYAN, is_outlined=True)
        open_sh_btn.clicked.connect(self.open_sh_file)
        script_act_layout.addWidget(open_sh_btn)

        row1_layout.addWidget(self.script_actions_widget)
        if self.current_mode != "SCRIPT":
            self.script_actions_widget.hide()

        # Toolbar Row 2: Sorting, Filter
        row2_layout = QHBoxLayout()
        
        sort_lbl = QLabel("SORT:")
        sort_lbl.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        sort_lbl.setStyleSheet(f"color: {CP_SUBTEXT};")
        row2_layout.addWidget(sort_lbl)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Date Added"])
        self.sort_combo.setCurrentText(self.sort_by)
        self.sort_combo.setStyleSheet(self.get_combo_style())
        self.sort_combo.currentTextChanged.connect(self.change_sort)
        row2_layout.addWidget(self.sort_combo)

        self.order_btn = CyberButton(self.sort_order, color=CP_CYAN, is_outlined=True)
        self.order_btn.setFixedWidth(50)
        self.order_btn.clicked.connect(self.toggle_sort_order)
        row2_layout.addWidget(self.order_btn)

        row2_layout.addStretch()

        self.search_input = CyberInput("SEARCH_DB://...", self)
        self.search_input.setFixedWidth(200)
        self.search_input.textChanged.connect(self.filter_items)
        row2_layout.addWidget(self.search_input)

        toolbar_main_layout.addLayout(row2_layout)
        toolbar_main_layout.addLayout(row1_layout)
        
        main_layout.addWidget(toolbar_container)

        # Splitter for list views
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"""
            QSplitter::handle {{ background-color: {CP_DIM}; }}
            QSplitter::handle:hover {{ background-color: {CP_CYAN}; }}
        """)

        self.cmd_container = self.create_column_box("SHELL_COMMANDS", splitter)
        self.app_container = self.create_column_box("APPLICATIONS", splitter)
        
        main_layout.addWidget(splitter, stretch=1)

        # Footer Status bar
        self.status_label = QLabel("SYSTEM READY")
        self.status_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"color: {CP_CYAN}; padding: 5px; border-top: 1px solid {CP_DIM};")
        main_layout.addWidget(self.status_label)

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
            QScrollBar:vertical {{ background: {CP_BG}; width: 8px; }}
            QScrollBar::handle:vertical {{ background: {CP_DIM}; }}
            QScrollBar::handle:vertical:hover {{ background: {CP_CYAN}; }}
        """)
        
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        vbox.setSpacing(8)
        vbox.setContentsMargins(0, 10, 0, 0)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        splitter.addWidget(wrapper)
        return vbox

    def load_items(self):
        try:
            if os.path.exists(JSON_FILE):
                with open(JSON_FILE, 'r', encoding='utf-8') as f:
                    self.items = json.load(f)
            else:
                self.items = []
                
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_mode = settings.get("current_mode", "AUTOSTART")
                    self.sh_file_path = settings.get("sh_file_path", DEFAULT_SH)
                    self.sort_by = settings.get("sort_by", "Name")
                    self.sort_order = settings.get("sort_order", "ASC")

            changed = False
            now = time.time()
            for item in self.items:
                if "added_at" not in item:
                    item["added_at"] = now
                    changed = True
            if changed:
                self.save_items()
        except:
            pass

    def save_items(self):
        try:
            with open(JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, indent=2, ensure_ascii=False)
            
            settings = {
                "current_mode": self.current_mode,
                "sh_file_path": self.sh_file_path,
                "sort_by": self.sort_by,
                "sort_order": self.sort_order
            }
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except:
            pass

    def toggle_mode(self):
        if self.current_mode == "AUTOSTART":
            self.current_mode = "SCRIPT"
            color = CP_YELLOW
            self.script_actions_widget.show()
        else:
            self.current_mode = "AUTOSTART"
            color = CP_CYAN
            self.script_actions_widget.hide()
            
        self.save_items()
        self.title_lbl.setText(f"SYSTEM // STARTUP_CONTROL // {self.current_mode}")
        self.mode_btn.setText(f" {self.current_mode}")
        self.mode_btn.color = color 
        self.mode_btn.update_icon(CP_BG)
        self.mode_btn.update_style()
        self.populate_lists()
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
            QComboBox:hover {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
            QComboBox::drop-down {{ border: 0px; width: 0px; }}
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
        while self.cmd_container.count():
            child = self.cmd_container.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        while self.app_container.count():
            child = self.app_container.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        self.widgets_map.clear()

        sorted_items = sorted(self.items, 
                            key=lambda x: x["name"].lower() if self.sort_by == "Name" else x.get("added_at", 0),
                            reverse=(self.sort_order == "DESC"))

        for item in sorted_items:
            is_active = False
            if self.current_mode == "AUTOSTART":
                is_active = self.check_autostart_active(item)
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

        self.filter_items(self.search_input.text())

    def check_autostart_active(self, item):
        # Active if a desktop entry file exists and does NOT contain Hidden=true
        filename = f"{item['name'].lower().replace(' ', '_')}.desktop"
        path = os.path.join(AUTOSTART_DIR, filename)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return "Hidden=true" not in content
            except:
                return False
        return False

    def handle_toggle(self, item, current_state):
        should_enable = not current_state
        
        if self.current_mode == "AUTOSTART":
            filename = f"{item['name'].lower().replace(' ', '_')}.desktop"
            path = os.path.join(AUTOSTART_DIR, filename)
            try:
                if should_enable:
                    # Write .desktop file
                    exec_cmd = item.get("sh_command", "")
                    if not exec_cmd and item.get("paths"):
                        exec_cmd = item["paths"][0]
                        if item.get("Command"):
                            exec_cmd += f" {item['Command']}"
                    
                    if item.get("run_as_admin"):
                        exec_cmd = f"pkexec {exec_cmd}"
                        
                    content = f"""[Desktop Entry]
Type=Application
Name={item['name']}
Exec={exec_cmd}
Hidden=false
X-KDE-AutostartScript=true
"""
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    # Disable it
                    if os.path.exists(path):
                        # Simply delete it or set Hidden=true
                        os.remove(path)
                
                self.widgets_map[item["name"]].set_active(should_enable)
                self.update_status(f"AUTOSTART UPDATED: {item['name']} -> {'ON' if should_enable else 'OFF'}")
            except Exception as e:
                self.update_status(f"AUTOSTART ERROR: {str(e)}")
        else:
            # SCRIPT MODE
            item["script_enabled"] = should_enable 
            self.save_items()
            self.generate_sh()
            self.widgets_map[item["name"]].set_active(should_enable)
            self.update_status(f"SCRIPT UPDATED: {item['name']} -> {'ON' if should_enable else 'OFF'}")

    def generate_sh(self):
        try:
            content = "#!/bin/bash\n# Auto-generated startup script by SYSTEM // STARTUP_CONTROL\n\n"
            content += 'echo "Initializing Startup Protocol..."\n\n'
            
            enabled_count = 0
            for item in self.items:
                if item.get("script_enabled", False):
                    name = item["name"]
                    cmd = item.get("sh_command", "")
                    
                    if not cmd:
                        path = item["paths"][0]
                        args = item.get("Command", "")
                        cmd = f'"{path}"'
                        if args: cmd += f' {args}'
                    
                    if item.get("run_as_admin"):
                        cmd = f"pkexec {cmd}"
                    
                    content += f"# {name}\n"
                    content += "echo \"Exec: {name}...\"\n"
                    content += f"({cmd}) &\n\n"
                    enabled_count += 1
            
            content += "echo \"Startup Sequence Complete.\"\n"
            
            with open(self.sh_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            os.chmod(self.sh_file_path, 0o755)

            # Ensure script itself starts up via .desktop file
            script_desktop = os.path.join(AUTOSTART_DIR, "startup_manager_script.desktop")
            if enabled_count > 0:
                with open(script_desktop, 'w', encoding='utf-8') as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Name=Startup Manager Custom Script
Exec=/bin/bash {self.sh_file_path}
Hidden=false
X-KDE-AutostartScript=true
""")
            else:
                if os.path.exists(script_desktop):
                    os.remove(script_desktop)
                
            self.update_status(f"SH GENERATED: {enabled_count} ACTIVE ITEMS")
        except Exception as e:
            self.update_status(f"SH GENERATION FAILED: {str(e)}")

    def handle_launch(self, item):
        try:
            cmd = item.get("sh_command", "")
            if not cmd and item.get("paths"):
                cmd = item["paths"][0]
                if item.get("Command"):
                    cmd += f" {item['Command']}"
            
            run_as_admin = item.get("_run_as_admin") or item.get("run_as_admin", False)
            if run_as_admin:
                cmd = f"pkexec {cmd}"
            
            subprocess.Popen(cmd, shell=True)
            self.update_status(f"EXECUTING: {item['name']}")
        except Exception as e:
            self.update_status(f"EXEC PROTOCOL FAILED: {str(e)}")

    def handle_edit(self, item):
        dialog = ItemDialog(self, item)
        if dialog.exec():
            for i, it in enumerate(self.items):
                if it["name"] == item["name"]:
                    self.items[i] = dialog.result_data
                    break
            self.save_items()
            self.populate_lists()
            self.update_status("DATABASE UPDATED")

    def handle_delete(self, item):
        if QMessageBox.question(self, "CONFIRM DELETE", f"PURGE {item['name']}?") == QMessageBox.StandardButton.Yes:
            if self.check_autostart_active(item):
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

    def select_sh_path(self):
        new_path, _ = QFileDialog.getSaveFileName(self, "SELECT SH LOCATION", self.sh_file_path, "Shell Script (*.sh)")
        if new_path:
            self.sh_file_path = new_path
            self.save_items()
            self.update_status(f"PATH UPDATED: {os.path.basename(new_path)}")

    def open_sh_file(self):
        if os.path.exists(self.sh_file_path):
            subprocess.run(["xdg-open", self.sh_file_path])
            self.update_status("SH SCRIPT OPENED")
        else:
            self.update_status("SH NOT FOUND - GENERATING...")
            self.generate_sh()
            if os.path.exists(self.sh_file_path):
                subprocess.run(["xdg-open", self.sh_file_path])

    def open_autostart_dir(self):
        if os.path.exists(AUTOSTART_DIR):
            subprocess.run(["xdg-open", AUTOSTART_DIR])
            self.update_status("AUTOSTART DIRECTORY OPENED")

    def open_kde_settings(self):
        # Open KDE autostart system settings panel if possible
        try:
            subprocess.Popen(["kcmshell6", "kcm_autostart"])
        except:
            try:
                subprocess.Popen(["kcmshell5", "kcm_autostart"])
            except:
                try:
                    subprocess.Popen(["systemsettings"])
                except Exception as e:
                    self.update_status("COULD NOT LAUNCH SYSTEM SETTINGS")
                    return
        self.update_status("KDE SETTINGS PROTOCOL LAUNCHED")

    def scan_autostart_dirs(self):
        self.update_status("SCANNING AUTOSTART DIRECTORIES...")
        QApplication.processEvents()
        
        found_items = []
        names = {i["name"].lower() for i in self.items}
        
        dirs = [AUTOSTART_DIR, "/etc/xdg/autostart"]
        for d in dirs:
            if not os.path.exists(d): continue
            for f in os.listdir(d):
                if f.endswith(".desktop"):
                    filepath = os.path.join(d, f)
                    try:
                        # Simple desktop file parser
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                            lines = file_obj.readlines()
                        
                        entry_name = ""
                        exec_cmd = ""
                        is_hidden = False
                        
                        in_section = False
                        for line in lines:
                            line = line.strip()
                            if line == "[Desktop Entry]":
                                in_section = True
                                continue
                            elif line.startswith("[") and line.endswith("]"):
                                in_section = False
                            
                            if in_section and "=" in line:
                                k, v = line.split("=", 1)
                                k, v = k.strip(), v.strip()
                                if k == "Name":
                                    entry_name = v
                                elif k == "Exec":
                                    exec_cmd = v
                                elif k == "Hidden":
                                    is_hidden = v.lower() == "true"
                        
                        if entry_name and exec_cmd:
                            if entry_name.lower() in names: continue
                            
                            found_items.append({
                                "name": entry_name,
                                "type": "App" if "/" in exec_cmd or exec_cmd.startswith(("exec", "env")) else "Command",
                                "paths": [exec_cmd.split()[0] if exec_cmd else ""],
                                "Command": " ".join(exec_cmd.split()[1:]) if exec_cmd and len(exec_cmd.split()) > 1 else "",
                                "sh_command": exec_cmd,
                                "ExecutableType": "other",
                                "added_at": time.time(),
                                "run_as_admin": False
                            })
                    except Exception as e:
                        print("Error parsing desktop file:", filepath, e)
                        
        if found_items:
            dialog = ScanResultsDialog(found_items, self, title="SYSTEM // SCAN_AUTOSTART")
            if dialog.exec():
                selected = dialog.selected_items
                if selected:
                    self.items.extend(selected)
                    self.save_items()
                    self.populate_lists()
                    self.update_status(f"IMPORTED {len(selected)} AUTOSTART ENTRIES")
        else:
            self.update_status("AUTOSTART SCAN: 0 NEW")

    def scan_systemd_services(self):
        self.update_status("SCANNING SYSTEMD SERVICES...")
        QApplication.processEvents()
        
        found_items = []
        names = {i["name"].lower() for i in self.items}

        # Check systemd user and system services
        commands = [
            ("systemctl --user list-unit-files --type=service --no-legend", "User"),
            ("systemctl list-unit-files --type=service --no-legend", "System")
        ]

        for cmd_str, scope in commands:
            try:
                res = subprocess.run(shlex.split(cmd_str), capture_output=True, text=True)
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        parts = line.split()
                        if len(parts) >= 2:
                            unit_name = parts[0]
                            state = parts[1]
                            
                            # Only suggest if enabled or user might want to control it
                            if state == "enabled":
                                if unit_name.lower() in names: continue
                                
                                # Command to manage this service
                                sh_cmd = f"systemctl {'--user' if scope == 'User' else ''} start {unit_name}"
                                
                                found_items.append({
                                    "name": f"{unit_name} ({scope})",
                                    "type": "Command",
                                    "paths": ["systemctl"],
                                    "Command": f"{'--user' if scope == 'User' else ''} start {unit_name}",
                                    "sh_command": sh_cmd,
                                    "ExecutableType": "other",
                                    "added_at": time.time(),
                                    "run_as_admin": scope == "System"
                                })
            except Exception as e:
                print(f"Systemd scan failed for {scope}: {e}")

        if found_items:
            dialog = ScanResultsDialog(found_items, self, title="SYSTEM // SCAN_SYSTEMD")
            if dialog.exec():
                selected = dialog.selected_items
                if selected:
                    self.items.extend(selected)
                    self.save_items()
                    self.populate_lists()
                    self.update_status(f"IMPORTED {len(selected)} SYSTEMD SERVICES")
        else:
            self.update_status("SYSTEMD SCAN: 0 NEW")

    def filter_items(self, text):
        text = text.lower()
        for name, w in self.widgets_map.items():
            path_val = w.item["paths"][0] if w.item.get("paths") else ""
            visible = text in name.lower() or text in path_val.lower()
            w.setVisible(visible)

    def update_status(self, text):
        self.status_label.setText(text)
        QTimer.singleShot(3000, lambda: self.status_label.setText("SYSTEM READY"))

    def _fix_floats(self, obj):
        if isinstance(obj, dict):
            return {k: self._fix_floats(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._fix_floats(i) for i in obj]
        if isinstance(obj, float) and obj.is_integer():
            return int(obj)
        return obj

    def _convex_call(self, endpoint, payload):
        url = f"{CONVEX_URL.rstrip('/')}/api/{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def backup_to_convex(self):
        label, ok = ConvexLabelDialog.get_label(self, convex_call_fn=self._convex_call, config_data=self.items)
        if not ok or not label.strip(): return
        try:
            self._convex_call("mutation", {
                "path": "functions:save",
                "args": {"scriptName": SCRIPT_NAME, "label": label.strip(), "data": self.items}
            })
            QMessageBox.information(self, "BACKUP", f'Config backed up: "{label.strip()}"')
        except Exception as e:
            QMessageBox.critical(self, "BACKUP FAILED", str(e))

    def restore_from_convex(self):
        try:
            result = self._convex_call("query", {
                "path": "functions:list",
                "args": {"scriptName": SCRIPT_NAME}
            })
            backups = result.get("value", [])
            if not backups:
                QMessageBox.information(self, "RESTORE", "No backups found.")
                return

            dlg = RestoreDialog(backups, self._convex_call, local_data=self.items, parent=self)
            if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_id:
                data = self._convex_call("query", {
                    "path": "functions:get",
                    "args": {"id": dlg.selected_id}
                }).get("value")

                if data:
                    self.items = self._fix_floats(data)
                    self.save_items()
                    self.populate_lists()
                    QMessageBox.information(self, "RESTORE", "Restored successfully.")
        except Exception as e:
            QMessageBox.critical(self, "RESTORE FAILED", str(e))

def make_app_icon():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#050505"/><path d="M32 6 C22 6 14 18 14 30 L14 38 L20 44 L20 52 L26 52 L26 46 L38 46 L38 52 L44 52 L44 44 L50 38 L50 30 C50 18 42 6 32 6Z" fill="#FCEE0A"/><circle cx="32" cy="26" r="6" fill="#050505"/><path d="M20 44 L16 54 L26 50Z" fill="#FF003C"/><path d="M44 44 L48 54 L38 50Z" fill="#FF003C"/><circle cx="32" cy="26" r="3" fill="#00F0FF"/></svg>'
    renderer = QSvgRenderer(QByteArray(svg))
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(make_app_icon())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
