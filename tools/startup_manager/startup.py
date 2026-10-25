"""Cyberpunk startup-item manager GUI."""
from __future__ import annotations

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "PyQt6",
# ]
# ///

import importlib.util
import ctypes
import os
import json
import shutil
import subprocess
import sys
import time


DEPENDENCIES = (
    ("PyQt6", "PyQt6"),
)


def ensure_dependencies() -> None:
    """Install missing packages into the interpreter running this script."""
    missing = sorted({
        package
        for module, package in DEPENDENCIES
        if importlib.util.find_spec(module) is None
    })
    if not missing:
        return

    uv = shutil.which("uv")
    if uv:
        command = [uv, "pip", "install", "--python", sys.executable, *missing]
    else:
        command = [sys.executable, "-m", "pip", "install", *missing]

    try:
        subprocess.check_call(command)
    except (OSError, subprocess.CalledProcessError) as exc:
        packages = ", ".join(missing)
        raise RuntimeError(
            f"Dependency installation failed for {packages} "
            f"using interpreter {sys.executable}."
        ) from exc


ensure_dependencies()

import PyQt6

# Fix for Qt platform plugin issue
qt_plugin_path = os.path.join(os.path.dirname(PyQt6.__file__), "Qt6", "plugins")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugin_path

import winreg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QScrollArea, QFrame, QMessageBox, QDialog, 
                             QComboBox, QFileDialog, QSplitter, QGraphicsEffect,
                             QGraphicsDropShadowEffect, QMenu, QCheckBox,
                             QRadioButton, QButtonGroup, QListWidget, QPlainTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QByteArray, QSettings, QThread
from PyQt6.QtGui import QFont, QColor, QPalette, QCursor, QPainter, QPen, QAction, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from gemini_credentials import load_gemini_api_key, save_gemini_api_key, delete_gemini_api_key
from gemini_support import GeminiApiError, GeminiClient

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


class ModelTestWorker(QThread):
    model_result = pyqtSignal(str, bool, str)
    completed = pyqtSignal(list, str)

    def __init__(self, api_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key

    def run(self):
        try:
            client = GeminiClient(self.api_key)
            models = client.list_generation_models()
            if not models:
                self.completed.emit([], "No models with text generation are available for this key.")
                return
            working = []
            for model in models:
                name = model.get("name", "")
                if not name:
                    continue
                try:
                    client.test_model(name)
                    model_id = name.removeprefix("models/")
                    working.append(model_id)
                    self.model_result.emit(model_id, True, "Responded successfully")
                except Exception as exc:
                    self.model_result.emit(name.removeprefix("models/"), False, str(exc))
            self.completed.emit(working, "Model check finished.")
        except Exception as exc:
            self.completed.emit([], str(exc))


class GeminiAnalysisWorker(QThread):
    completed = pyqtSignal(object, str)

    def __init__(self, api_key, model, item, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.item = item

    def run(self):
        try:
            result = GeminiClient(self.api_key).analyze_startup_item(self.model, self.item)
            self.completed.emit(result, "")
        except Exception as exc:
            self.completed.emit(None, str(exc))


class GeminiSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.worker = None
        self.setWindowTitle("GEMINI // API AND MODEL SETTINGS")
        self.resize(700, 560)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_DIM}; }} QLabel {{ color: {CP_CYAN}; font-family: 'Consolas'; }} QListWidget {{ background: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; font-family: 'Consolas'; }}")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("GEMINI API KEY // STORED IN WINDOWS CREDENTIAL MANAGER"))
        self.key_input = CyberInput("Paste API key; leave blank to keep the saved key...")
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.key_input)
        self.key_status = QLabel("A key is saved." if load_gemini_api_key() else "No key saved yet.")
        layout.addWidget(self.key_status)

        model_row = QHBoxLayout()
        model_row.addWidget(QLabel("DEFAULT MODEL"))
        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(f"QComboBox {{ background: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; padding: 5px; }}")
        saved_model = str(self.settings.value("gemini_model", ""))
        if saved_model:
            self.model_combo.addItem(saved_model)
        model_row.addWidget(self.model_combo, stretch=1)
        layout.addLayout(model_row)

        self.test_button = CyberButton("TEST AVAILABLE MODELS", color=CP_CYAN, is_outlined=True)
        self.test_button.clicked.connect(self.test_models)
        layout.addWidget(self.test_button)
        self.results_list = QListWidget()
        layout.addWidget(self.results_list, stretch=1)
        self.status_label = QLabel("Model tests make a short request to each generation-capable model returned for your key.")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        buttons = QHBoxLayout()
        self.delete_key_button = CyberButton("DELETE SAVED KEY", color=CP_RED, is_outlined=True)
        self.delete_key_button.clicked.connect(self.delete_key)
        self.save_button = CyberButton("SAVE SETTINGS", color=CP_YELLOW)
        self.save_button.clicked.connect(self.save_settings)
        self.close_button = CyberButton("CLOSE", color=CP_RED, is_outlined=True)
        self.close_button.clicked.connect(self.reject)
        buttons.addWidget(self.delete_key_button)
        buttons.addStretch()
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def test_models(self):
        api_key = self.key_input.text().strip() or load_gemini_api_key()
        if not api_key:
            QMessageBox.warning(self, "API KEY REQUIRED", "Enter your Gemini API key first.")
            return
        if self.key_input.text().strip():
            try:
                save_gemini_api_key(api_key)
                self.key_input.clear()
                self.key_status.setText("API key saved securely in Windows Credential Manager.")
            except Exception as exc:
                QMessageBox.critical(self, "KEY SAVE FAILED", str(exc))
                return
        self.results_list.clear()
        self.model_combo.clear()
        self.status_label.setText("Loading models and sending a short test prompt to each; Google API usage may be billed.")
        self.test_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.delete_key_button.setEnabled(False)
        self.close_button.setEnabled(False)
        self.worker = ModelTestWorker(api_key, self)
        self.worker.model_result.connect(self.show_model_result)
        self.worker.completed.connect(self.finish_model_test)
        self.worker.start()

    def show_model_result(self, model, success, detail):
        label = "WORKS" if success else "FAILED"
        self.results_list.addItem(f"[{label}] {model} — {detail}")

    def finish_model_test(self, working_models, message):
        previous = self.settings.value("gemini_model", "")
        self.model_combo.clear()
        self.model_combo.addItems(working_models)
        if previous in working_models:
            self.model_combo.setCurrentText(previous)
        elif working_models:
            self.model_combo.setCurrentIndex(0)
        self.status_label.setText(f"{message} {len(working_models)} model(s) responded successfully.")
        self.test_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.delete_key_button.setEnabled(True)
        self.close_button.setEnabled(True)

    def save_settings(self):
        if self.key_input.text().strip():
            try:
                save_gemini_api_key(self.key_input.text())
                self.key_input.clear()
                self.key_status.setText("API key saved securely in Windows Credential Manager.")
            except Exception as exc:
                QMessageBox.critical(self, "KEY SAVE FAILED", str(exc))
                return
        model = self.model_combo.currentText().strip()
        if model:
            self.settings.setValue("gemini_model", model.removeprefix("models/"))
        self.accept()

    def delete_key(self):
        try:
            delete_gemini_api_key()
            self.key_input.clear()
            self.key_status.setText("Saved API key deleted.")
        except Exception as exc:
            QMessageBox.critical(self, "KEY DELETE FAILED", str(exc))

    def reject(self):
        if self.worker and self.worker.isRunning():
            self.status_label.setText("Wait for the model check to finish before closing.")
            return
        super().reject()

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            event.ignore()
            self.status_label.setText("Wait for the model check to finish before closing.")
            return
        super().closeEvent(event)


class GeminiReviewDialog(QDialog):
    def __init__(self, current, result, parent=None):
        super().__init__(parent)
        self.suggested = result["suggested"]
        self.setWindowTitle("GEMINI // REVIEW COMMAND FIXES")
        self.resize(850, 620)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_DIM}; }} QLabel {{ color: {CP_CYAN}; font-family: 'Consolas'; }} QTableWidget {{ background: {CP_PANEL}; color: {CP_TEXT}; gridline-color: {CP_DIM}; font-family: 'Consolas'; }}")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("ISSUES FOUND"))
        issues = QPlainTextEdit("\n".join(result.get("issues", [])) or "No clear issues found.")
        issues.setReadOnly(True)
        issues.setMaximumHeight(100)
        layout.addWidget(issues)
        explanation = QPlainTextEdit(result.get("explanation", ""))
        explanation.setReadOnly(True)
        explanation.setMaximumHeight(80)
        layout.addWidget(explanation)

        keys = ["name", "type", "exec_type", "path", "arguments", "ps1_command"]
        self.table = QTableWidget(len(keys), 3)
        self.table.setHorizontalHeaderLabels(["FIELD", "CURRENT", "SUGGESTED"])
        self.table.verticalHeader().hide()
        self.table.setWordWrap(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for row, key in enumerate(keys):
            self.table.setItem(row, 0, QTableWidgetItem(key.upper()))
            self.table.setItem(row, 1, QTableWidgetItem(str(current.get(key, ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(self.suggested.get(key, ""))))
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.resizeRowsToContents()
        layout.addWidget(self.table, stretch=1)
        note = QLabel("Nothing changes until you choose APPLY SUGGESTED FIXES.")
        layout.addWidget(note)
        buttons = QHBoxLayout()
        apply_button = CyberButton("APPLY SUGGESTED FIXES", color=CP_GREEN)
        apply_button.clicked.connect(self.accept)
        cancel_button = CyberButton("KEEP CURRENT COMMAND", color=CP_RED, is_outlined=True)
        cancel_button.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(apply_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

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
        self.analysis_worker = None
        self.setWindowTitle("SYSTEM // EDIT" if item else "SYSTEM // NEW")
        self.setFixedSize(600, 650)
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
        
        command_heading = QHBoxLayout()
        command_heading.addWidget(QLabel("CUSTOM COMMAND // PS1 SCRIPT"))
        command_heading.addStretch()
        self.gemini_analyze_button = CyberButton("GEMINI // ANALYZE", color=CP_CYAN, is_outlined=True)
        self.gemini_analyze_button.clicked.connect(self.analyze_with_gemini)
        command_heading.addWidget(self.gemini_analyze_button)
        layout.addLayout(command_heading)
        self.ps1_input = CyberInput("Complete PowerShell command line...")
        layout.addWidget(self.ps1_input)
        self.gemini_status = QLabel("")
        self.gemini_status.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: 'Consolas'; font-size: 9px;")
        layout.addWidget(self.gemini_status)

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
        self.save_button = CyberButton("SAVE", color=CP_YELLOW)
        self.save_button.clicked.connect(self.save_item)
        self.cancel_button = CyberButton("ABORT", color=CP_RED, is_outlined=True)
        self.cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Executable", "", "Executables (*.exe);;All Files (*.*)")
        if filename: self.path_input.setText(filename)

    def analyze_with_gemini(self):
        api_key = load_gemini_api_key()
        settings = self.parent().settings if hasattr(self.parent(), "settings") else QSettings("nahid6970", "StartupManager")
        model = str(settings.value("gemini_model", "")).strip()
        if not api_key or not model:
            QMessageBox.information(
                self,
                "GEMINI SETUP REQUIRED",
                "Add your Gemini API key and test/select a working model in GEMINI settings first.",
            )
            settings_dialog = GeminiSettingsDialog(settings, self)
            settings_dialog.exec()
            return

        item = {
            "name": self.name_input.text(),
            "type": self.type_combo.currentText(),
            "ExecutableType": "ahk_v2" if self.radio_ahk.isChecked() else "other",
            "paths": [self.path_input.text()],
            "Command": self.args_input.text(),
            "ps1_command": self.ps1_input.text(),
        }
        self.gemini_analyze_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.gemini_status.setText(f"Analyzing with {model}...")
        self.analysis_worker = GeminiAnalysisWorker(api_key, model, item, self)
        self.analysis_worker.completed.connect(lambda result, error: self.finish_gemini_analysis(item, result, error))
        self.analysis_worker.start()

    def finish_gemini_analysis(self, current, result, error):
        self.gemini_analyze_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        if error:
            self.gemini_status.setText("Gemini analysis failed.")
            QMessageBox.warning(self, "GEMINI ANALYSIS FAILED", error)
            return
        review = GeminiReviewDialog(current, result, self)
        if review.exec() == QDialog.DialogCode.Accepted:
            suggested = review.suggested
            self.name_input.setText(suggested["name"])
            self.type_combo.setCurrentText(suggested["type"])
            self.path_input.setText(suggested["path"])
            self.args_input.setText(suggested["arguments"])
            self.ps1_input.setText(suggested["ps1_command"])
            self.radio_ahk.setChecked(suggested["exec_type"] == "ahk_v2")
            self.radio_other.setChecked(suggested["exec_type"] != "ahk_v2")
            self.gemini_status.setText("Suggested fields applied. Review them before saving.")
        else:
            self.gemini_status.setText("Current command kept unchanged.")

    def reject(self):
        if self.analysis_worker and self.analysis_worker.isRunning():
            return
        super().reject()

    def closeEvent(self, event):
        if self.analysis_worker and self.analysis_worker.isRunning():
            event.ignore()
            return
        super().closeEvent(event)

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
        self.gemini_btn = CyberButton(" GEMINI", color=CP_CYAN, is_outlined=True); self.gemini_btn.clicked.connect(self.open_gemini_settings); row1_layout.addWidget(self.gemini_btn)
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
        admin = "*RunAs " if item.get("run_as_admin") else ""
        hide = ', , "Hide"' if item.get("hide_terminal") else ""
        content = f'#NoTrayIcon\nRun \'{admin}"{path}" {args}\'{hide}'
        with open(ahk_path, "w", encoding='utf-8') as f:
            f.write(content)
        return ahk_path

    def check_registry(self, item):
        hive = item.get("registry_hive", "HKCU")
        key_path = item.get("registry_key_path", r"Software\Microsoft\Windows\CurrentVersion\Run")
        hkey = winreg.HKEY_LOCAL_MACHINE if hive == "HKLM" else winreg.HKEY_CURRENT_USER
        try:
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, item["name"]); return True
        except: return False

    def handle_toggle(self, item, current_state):
        should_enable = not current_state
        if self.current_mode == "REGISTRY":
            hive = item.get("registry_hive", "HKCU")
            key_path = item.get("registry_key_path", r"Software\Microsoft\Windows\CurrentVersion\Run")
            hkey = winreg.HKEY_LOCAL_MACHINE if hive == "HKLM" else winreg.HKEY_CURRENT_USER
            try:
                with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_WRITE) as key:
                    if should_enable:
                        if item.get("ExecutableType") == "ahk_v2": 
                            val = f'"{self._make_ahk(item)}"'
                        elif item.get("run_as_admin") or item.get("hide_terminal"): 
                            val = f'wscript.exe "{self._make_vbs(item)}"'
                        else: 
                            path, args = item["paths"][0], item.get("Command", "")
                            val = f'"{path}" {args}'.strip() if " " in path or "\\" in path else f'{path} {args}'.strip()
                        winreg.SetValueEx(key, item["name"], 0, winreg.REG_SZ, val)
                    else: winreg.DeleteValue(key, item["name"])
                self.widgets_map[item["name"]].set_active(should_enable)
            except Exception as e: self.update_status(f"REG ERROR: {e}. Try running as Admin.")
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
            # Check options, overriding if custom admin run was requested
            run_as_admin = item.get("_run_as_admin") or item.get("run_as_admin", False)
            hide_terminal = item.get("hide_terminal", False)
            exec_type = item.get("ExecutableType", "other")
            path, cmd = item["paths"][0], item.get("Command", "")
            
            # Temporary item representation with target admin status
            temp_item = {**item, "run_as_admin": run_as_admin}
            
            if self.current_mode == "REGISTRY":
                if exec_type == "ahk_v2":
                    ahk_file = self._make_ahk(temp_item)
                    subprocess.Popen(f'start "" "{ahk_file}"', shell=True)
                elif run_as_admin or hide_terminal:
                    vbs_file = self._make_vbs(temp_item)
                    subprocess.Popen(f'wscript.exe "{vbs_file}"', shell=True)
                else:
                    if run_as_admin:
                        subprocess.Popen(["powershell", "-Command", f'Start-Process "{path}" -ArgumentList "{cmd}" -Verb RunAs'])
                    else:
                        subprocess.Popen(f'start "" "{path}" {cmd}', shell=True)
            else:
                # SCRIPT (PowerShell) mode
                if exec_type == "ahk_v2":
                    ahk_file = self._make_ahk(temp_item)
                    ps_cmd = f'Start-Process -FilePath "{ahk_file}"'
                elif not temp_item.get("ps1_command"):
                    ps_cmd = f'Start-Process -FilePath "{path}"'
                    if cmd:
                        ps_cmd += f' -ArgumentList \'{cmd}\''
                    if hide_terminal:
                        ps_cmd += ' -WindowStyle Hidden'
                else:
                    ps_cmd = temp_item["ps1_command"]
                
                if run_as_admin and "-Verb RunAs" not in ps_cmd and exec_type != "ahk_v2":
                    ps_cmd += ' -Verb RunAs'
                
                subprocess.Popen(["powershell", "-Command", ps_cmd])
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
    def scan_registry(self):
        self.update_status("SCANNING REGISTRY...")
        found, names = [], {i["name"].lower() for i in self.items}
        targets = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run", "HKLM")
        ]
        for hkey, key_path, hive_name in targets:
            try:
                with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ) as key:
                    info = winreg.QueryInfoKey(key)
                    for i in range(info[1]):
                        name, val, val_type = winreg.EnumValue(key, i)
                        if name.lower() not in names:
                            val_str = str(val).strip()
                            path = ""
                            args = ""
                            if val_str.startswith('"'):
                                end_quote = val_str.find('"', 1)
                                if end_quote != -1:
                                    path = val_str[1:end_quote]
                                    args = val_str[end_quote+1:].strip()
                                else:
                                    path = val_str
                            else:
                                parts = val_str.split(' ', 1)
                                path = parts[0]
                                if len(parts) > 1:
                                    args = parts[1]
                            
                            found.append({
                                "name": name,
                                "paths": [path],
                                "Command": args,
                                "type": "App" if path.lower().endswith(".exe") else "Command",
                                "added_at": time.time(),
                                "registry_hive": hive_name,
                                "registry_key_path": key_path
                            })
            except Exception as e:
                print(f"Skipped key {hive_name}\\{key_path}: {e}")
        if found:
            dlg = ScanResultsDialog(found, self, title="SYSTEM // REGISTRY_SCAN_RESULTS", confirm_text="IMPORT SELECTED")
            if dlg.exec():
                self.items.extend(dlg.selected_items)
                self.save_items()
                self.populate_lists()
        else:
            self.update_status("NO NEW REGISTRY ENTRIES")
    def scan_tasks(self):
        self.update_status("SCANNING TASKS...")
        found, names = [], {i["name"].lower() for i in self.items}
        ps_cmd = (
            "Get-ScheduledTask | "
            "Where-Object { $_.State -ne 'Disabled' -and $_.TaskPath -notlike '\\Microsoft\\*' } | "
            "ForEach-Object { [PSCustomObject]@{ Name = $_.TaskName; Path = $_.TaskPath; "
            "Action = ($_.Actions | Select-Object -First 1).Execute; "
            "Arguments = ($_.Actions | Select-Object -First 1).Argument } } | "
            "ConvertTo-Json"
        )
        try:
            res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if res.returncode == 0 and res.stdout.strip():
                import json
                tasks_data = json.loads(res.stdout)
                if isinstance(tasks_data, dict):
                    tasks_data = [tasks_data]
                for t in tasks_data:
                    name = t.get("Name")
                    action = t.get("Action")
                    args = t.get("Arguments") or ""
                    if name and name.lower() not in names:
                        if action:
                            found.append({
                                "name": name,
                                "paths": [action],
                                "Command": args,
                                "type": "App" if action.lower().endswith(".exe") else "Command",
                                "added_at": time.time(),
                                "origin": "TaskScheduler"
                            })
        except Exception as e:
            self.update_status(f"TASK SCAN FAILED: {e}")
            return
            
        if found:
            dlg = ScanResultsDialog(found, self, title="SYSTEM // TASK_SCAN_RESULTS", confirm_text="IMPORT SELECTED")
            if dlg.exec():
                self.items.extend(dlg.selected_items)
                self.save_items()
                self.populate_lists()
        else:
            self.update_status("NO NEW TASK ENTRIES")
    def delete_matching_shortcuts(self):
        self.update_status("PRUNING...")
        pruned_count = 0
        names = {i["name"].lower() for i in self.items}
        dirs = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs\Startup"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        ]
        for d in dirs:
            if not os.path.exists(d): continue
            for f in os.listdir(d):
                name_without_ext = os.path.splitext(f)[0].lower()
                if name_without_ext in names:
                    filepath = os.path.join(d, f)
                    try:
                        os.remove(filepath)
                        pruned_count += 1
                    except Exception as e:
                        print(f"Failed to delete {filepath}: {e}")
        if pruned_count > 0:
            self.update_status(f"PRUNED {pruned_count} SHORTCUTS")
        else:
            self.update_status("NO MATCHES TO PRUNE")
    def filter_items(self, text):
        for name, w in self.widgets_map.items(): w.setVisible(text.lower() in name.lower() or text.lower() in w.item["paths"][0].lower())
    def update_status(self, text): self.status_label.setText(text); QTimer.singleShot(3000, lambda: self.status_label.setText("SYSTEM READY"))
    def select_ps1_path(self):
        if (p := QFileDialog.getSaveFileName(self, "SELECT PS1", self.ps1_file_path, "PS1 (*.ps1)")[0]): self.ps1_file_path = p; self.settings.setValue("ps1_file_path", p)

    def open_gemini_settings(self):
        dialog = GeminiSettingsDialog(self.settings, self)
        dialog.exec()

def make_app_icon():
    svg = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#050505"/><path d="M32 6 C22 6 14 18 14 30 L14 38 L20 44 L20 52 L26 52 L26 46 L38 46 L38 52 L44 52 L44 44 L50 38 L50 30 C50 18 42 6 32 6Z" fill="#FCEE0A"/><circle cx="32" cy="26" r="6" fill="#050505"/><path d="M20 44 L16 54 L26 50Z" fill="#FF003C"/><path d="M44 44 L48 54 L38 50Z" fill="#FF003C"/><circle cx="32" cy="26" r="3" fill="#00F0FF"/></svg>'
    renderer = QSvgRenderer(QByteArray(svg)); pix = QPixmap(64, 64); pix.fill(Qt.GlobalColor.transparent); painter = QPainter(pix); renderer.render(painter); painter.end(); return QIcon(pix)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion"); app.setWindowIcon(make_app_icon()); window = MainWindow(); window.show(); sys.exit(app.exec())
