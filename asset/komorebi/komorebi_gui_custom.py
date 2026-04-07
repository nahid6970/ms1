import sys
import os
import json
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea,
                             QCheckBox, QComboBox, QDialog, QFormLayout, QFrame, QMessageBox, QSpinBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

# Optional imports for window info capture
try:
    import win32gui
    import win32process
    import win32api
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

# Use relative path for config
CONFIG_FILENAME = "komorebi.json"
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
KOMOREBI_JSON_PATH = os.path.join(SCRIPT_PATH, CONFIG_FILENAME)

class AddEditDialog(QDialog):
    def __init__(self, parent, item_data=None, initial_kind=None, initial_id=None, is_float=False, is_tray=False):
        super().__init__(parent)
        self.setWindowTitle("EDIT ITEM" if item_data else "ADD ITEM")
        self.setFixedWidth(450)
        self.item_data = item_data
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit, QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 8px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
        """)

        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.kind_combo = QComboBox()
        self.kind_combo.addItems(["Exe", "Class", "Title", "Path"])
        
        self.id_entry = QLineEdit()
        self.id_entry.setPlaceholderText("ID (e.g. notepad.exe)")
        
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Legacy", "Equals", "StartsWith", "EndsWith", "Contains", "Regex",
            "DoesNotEndWith", "DoesNotStartWith", "DoesNotEqual", "DoesNotContain"
        ])
        
        form.addRow("KIND:", self.kind_combo)
        form.addRow("ID:", self.id_entry)
        form.addRow("STRATEGY:", self.strategy_combo)
        layout.addLayout(form)
        
        check_layout = QHBoxLayout()
        self.float_cb = QCheckBox("FLOAT RULE")
        self.tray_cb = QCheckBox("TRAY APP")
        check_layout.addWidget(self.float_cb)
        check_layout.addWidget(self.tray_cb)
        layout.addLayout(check_layout)
        
        if item_data:
            self.kind_combo.setCurrentText(item_data["kind"])
            self.id_entry.setText(item_data["id"])
            self.strategy_combo.setCurrentText(item_data["matching_strategy"])
            self.float_cb.setChecked(item_data["is_float"])
            self.tray_cb.setChecked(item_data["is_tray"])
            btn_text = "UPDATE RULE"
        else:
            self.kind_combo.setCurrentText(initial_kind if initial_kind else "Exe")
            self.id_entry.setText(initial_id if initial_id else "")
            self.float_cb.setChecked(is_float)
            self.tray_cb.setChecked(is_tray)
            btn_text = "ADD TO SYSTEM"
            
        self.submit_btn = QPushButton(btn_text)
        self.submit_btn.clicked.connect(self.accept)
        layout.addWidget(self.submit_btn)

    def get_result(self):
        return {
            "kind": self.kind_combo.currentText(),
            "id": self.id_entry.text().strip(),
            "matching_strategy": self.strategy_combo.currentText(),
            "is_float": self.float_cb.isChecked(),
            "is_tray": self.tray_cb.isChecked()
        }

class CaptureSelectionDialog(QDialog):
    def __init__(self, parent, info):
        super().__init__(parent)
        self.setWindowTitle("SELECT WINDOW DATA")
        self.setFixedWidth(500)
        self.info = info
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_YELLOW}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold; text-align: left; }}
            QPushButton:hover {{ border: 1px solid {CP_CYAN}; color: {CP_CYAN}; }}
            QLabel#header {{ color: {CP_YELLOW}; font-weight: bold; font-size: 12pt; margin-bottom: 10px; }}
        """)

        layout = QVBoxLayout(self)
        header = QLabel("CHOOSE CAPTURED ATTRIBUTE:")
        header.setObjectName("header")
        layout.addWidget(header)
        
        self.selected_kind = None
        self.selected_val = None
        
        for kind, val in [("Exe", info["Exe"]), ("Title", info["Title"]), ("Class", info["Class"]), ("Path", info["Path"])]:
            btn = QPushButton(f"{kind.upper()}: {val}")
            btn.clicked.connect(lambda ch, k=kind, v=val: self.select(k, v))
            layout.addWidget(btn)
            
        layout.addSpacing(20)
        cancel = QPushButton("CANCEL")
        cancel.setStyleSheet(f"color: {CP_RED}; border-color: {CP_RED};")
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

    def select(self, kind, val):
        self.selected_kind = kind
        self.selected_val = val
        self.accept()

class RuleWidget(QFrame):
    def __init__(self, data, parent):
        super().__init__()
        self.data = data
        self.parent_app = parent
        self.setObjectName("RuleWidget")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        info_label = QLabel(f"{data['id']} [{data['kind']}]")
        info_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        if data['is_float']:
            tag = QLabel(" FLOAT ")
            tag.setStyleSheet(f"background-color: #1f538d; color: white; border-radius: 3px; font-size: 8pt; font-weight: bold;")
            layout.addWidget(tag)
        
        if data['is_tray']:
            tag = QLabel(" TRAY ")
            tag.setStyleSheet(f"background-color: #22733d; color: white; border-radius: 3px; font-size: 8pt; font-weight: bold;")
            layout.addWidget(tag)

    def mousePressEvent(self, event):
        self.parent_app.select_item(self)
        
    def mouseDoubleClickEvent(self, event):
        self.parent_app.open_edit_dialog(self.data)

class KomorebiApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KOMOREBI CONFIG PRO")
        self.resize(1000, 800)
        
        self.config_data = self.load_config()
        self.selected_widget = None
        self.is_capturing = False
        
        self.init_ui()
        self.apply_theme()
        self.refresh_list()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Top Bar: Search & Restart & Settings
        top_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("SEARCH RULES [EXE, CLASS, TITLE]...")
        self.search_input.textChanged.connect(self.refresh_list)
        top_bar.addWidget(self.search_input, 4)
        
        self.restart_btn = QPushButton("RESTART")
        self.restart_btn.setFixedWidth(100)
        self.restart_btn.clicked.connect(self.restart_app)
        self.restart_btn.setStyleSheet(f"color: {CP_ORANGE}; border-color: {CP_ORANGE};")
        top_bar.addWidget(self.restart_btn)
        
        self.settings_btn = QPushButton("SETTINGS")
        self.settings_btn.setFixedWidth(100)
        self.settings_btn.clicked.connect(self.toggle_settings)
        top_bar.addWidget(self.settings_btn)
        
        main_layout.addLayout(top_bar)
        
        # Content Area (List + Settings Panel)
        self.content_stack = QHBoxLayout()
        
        # List Area
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0,0,0,0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        list_layout.addWidget(self.scroll)
        
        self.content_stack.addWidget(list_container, 3)
        
        # Settings Panel (Hidden by default)
        self.settings_panel = QGroupBox("SYSTEM SETTINGS")
        self.settings_panel.setFixedWidth(300)
        self.settings_panel.setVisible(False)
        settings_layout = QVBoxLayout(self.settings_panel)
        
        # Timeout Setting
        settings_layout.addWidget(QLabel("CAPTURE TIMEOUT (SEC):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(self.config_data.get("gui_settings", {}).get("capture_timeout", 3))
        self.timeout_spin.valueChanged.connect(self.update_gui_settings)
        settings_layout.addWidget(self.timeout_spin)
        
        settings_layout.addSpacing(10)
        
        # Strategy Setting
        settings_layout.addWidget(QLabel("CAPTURE STRATEGY:"))
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(["Hover (Mouse)", "Focus (Active)"])
        current_strategy = self.config_data.get("gui_settings", {}).get("capture_strategy", "Hover (Mouse)")
        self.strategy_combo.setCurrentText(current_strategy)
        self.strategy_combo.currentTextChanged.connect(self.update_gui_settings)
        settings_layout.addWidget(self.strategy_combo)
        
        settings_layout.addStretch()
        self.content_stack.addWidget(self.settings_panel)
        
        main_layout.addLayout(self.content_stack)
        
        # Bottom Bar: Actions
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("ADD NEW RULE")
        self.add_btn.clicked.connect(self.open_add_dialog)
        
        self.get_info_btn = QPushButton("GET ITEM INFO")
        self.get_info_btn.clicked.connect(self.start_capture)
        
        self.remove_btn = QPushButton("REMOVE SELECTED")
        self.remove_btn.setStyleSheet(f"color: {CP_RED}; border-color: {CP_DIM};")
        self.remove_btn.clicked.connect(self.remove_selected)
        
        self.save_btn = QPushButton("SAVE TO JSON")
        self.save_btn.setStyleSheet(f"background-color: {CP_DIM}; border: 2px solid {CP_GREEN}; color: {CP_GREEN};")
        self.save_btn.clicked.connect(self.save_config)
        
        for b in [self.add_btn, self.get_info_btn, self.remove_btn, self.save_btn]:
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_layout.addWidget(b)
            
        main_layout.addLayout(btn_layout)

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 15px; padding-top: 15px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; }}
            QScrollArea {{ background: transparent; border: none; }}
            #RuleWidget {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; margin-bottom: 2px;
            }}
            #RuleWidget[selected="true"] {{
                border: 1px solid {CP_CYAN}; background-color: #002b36;
            }}
        """)

    def load_config(self):
        if not os.path.exists(KOMOREBI_JSON_PATH):
            return {"ignore_rules": [], "tray_and_multi_window_applications": [], "gui_settings": {}}
        try:
            with open(KOMOREBI_JSON_PATH, 'r') as f:
                return json.load(f)
        except: return {"ignore_rules": [], "tray_and_multi_window_applications": [], "gui_settings": {}}

    def save_config(self):
        try:
            if hasattr(self, "timeout_spin"):
                self.update_gui_settings()
            with open(KOMOREBI_JSON_PATH, 'w') as f:
                json.dump(self.config_data, f, indent=4)
            QMessageBox.information(self, "SUCCESS", "CONFIG SAVED TO SYSTEM.")
        except Exception as e:
            QMessageBox.critical(self, "ERROR", f"SAVE FAILED: {e}")

    def update_gui_settings(self):
        if "gui_settings" not in self.config_data:
            self.config_data["gui_settings"] = {}
        self.config_data["gui_settings"]["capture_timeout"] = self.timeout_spin.value()
        self.config_data["gui_settings"]["capture_strategy"] = self.strategy_combo.currentText()

    def refresh_list(self):
        # Clear list
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        self.selected_widget = None
        query = self.search_input.text().lower()
        
        # Unify data for display
        unified = {}
        for r in self.config_data.get("ignore_rules", []):
            k = (r["kind"], r["id"], r.get("matching_strategy", "Equals"))
            unified[k] = {**r, "is_float": True, "is_tray": False, "matching_strategy": k[2]}
            
        for a in self.config_data.get("tray_and_multi_window_applications", []):
            k = (a["kind"], a["id"], a.get("matching_strategy", "Equals"))
            if k in unified: unified[k]["is_tray"] = True
            else: unified[k] = {**a, "is_float": False, "is_tray": True, "matching_strategy": k[2]}
            
        items = sorted(unified.values(), key=lambda x: x["id"].lower())
        for data in items:
            if query and query not in f"{data['id']} {data['kind']}".lower():
                continue
            widget = RuleWidget(data, self)
            self.scroll_layout.addWidget(widget)

    def select_item(self, widget):
        if self.selected_widget:
            self.selected_widget.setProperty("selected", False)
            self.selected_widget.style().unpolish(self.selected_widget)
            self.selected_widget.style().polish(self.selected_widget)
            
        self.selected_widget = widget
        widget.setProperty("selected", True)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def open_add_dialog(self, initial_kind=None, initial_id=None, is_float=True, is_tray=False):
        dialog = AddEditDialog(self, initial_kind=initial_kind, initial_id=initial_id, is_float=is_float, is_tray=is_tray)
        if dialog.exec():
            res = dialog.get_result()
            self.apply_result(res)

    def open_edit_dialog(self, val):
        dialog = AddEditDialog(self, item_data=val)
        if dialog.exec():
            # Remove old
            self.remove_item_internal(val)
            # Add new
            res = dialog.get_result()
            self.apply_result(res)

    def apply_result(self, res):
        base = {"kind": res["kind"], "id": res["id"], "matching_strategy": res["matching_strategy"]}
        
        float_added = False
        tray_added = False
        
        if res["is_float"]:
            if base not in self.config_data.setdefault("ignore_rules", []):
                self.config_data["ignore_rules"].append(base)
                float_added = True
                
        if res["is_tray"]:
            if base not in self.config_data.setdefault("tray_and_multi_window_applications", []):
                self.config_data["tray_and_multi_window_applications"].append(base)
                tray_added = True
        
        # If the user selected a type but it wasn't added because it already exists
        if (res["is_float"] and not float_added) or (res["is_tray"] and not tray_added):
            QMessageBox.information(self, "DUPLICATE", "SOME OR ALL SELECTED RULES ALREADY EXIST AND WERE IGNORED.")
            
        self.refresh_list()

    def remove_selected(self):
        if not self.selected_widget:
            QMessageBox.warning(self, "WARNING", "NO ITEM SELECTED.")
            return
        self.remove_item_internal(self.selected_widget.data)
        self.refresh_list()

    def remove_item_internal(self, val):
        base = {"kind": val["kind"], "id": val["id"], "matching_strategy": val["matching_strategy"]}
        if base in self.config_data.get("ignore_rules", []):
            self.config_data["ignore_rules"].remove(base)
        if base in self.config_data.get("tray_and_multi_window_applications", []):
            self.config_data["tray_and_multi_window_applications"].remove(base)

    def start_capture(self):
        if not PYWIN32_AVAILABLE:
            QMessageBox.critical(self, "ERROR", "PYWIN32 NOT INSTALLED.")
            return

        timeout = self.config_data.get("gui_settings", {}).get("capture_timeout", 3)

        msg = QMessageBox(self)
        msg.setWindowTitle("CAPTURE MODE")
        msg.setText("CHOOSE HOW TO CAPTURE WINDOW INFO:")
        msg.setStyleSheet(f"QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas'; }} QPushButton {{ background-color: {CP_DIM}; color: white; padding: 8px; min-width: 100px; }}")
        
        click_btn = msg.addButton("CLICK MODE", QMessageBox.ButtonRole.ActionRole)
        time_btn = msg.addButton(f"TIMEOUT ({timeout})", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("CANCEL", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        if msg.clickedButton() == click_btn:
            self.start_click_capture()
        elif msg.clickedButton() == time_btn:
            self.start_timeout_capture(timeout)

    def start_click_capture(self):
        self.get_info_btn.setText("CLICK TARGET WINDOW...")
        self.get_info_btn.setStyleSheet(f"background-color: {CP_ORANGE}; color: black;")
        
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.poll_capture)
        self.capture_timer.start(50)
        self.waiting_for_release = True

    def start_timeout_capture(self, seconds):
        self.remaining_time = seconds
        self.get_info_btn.setStyleSheet(f"background-color: {CP_RED}; color: white;")
        
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.poll_timeout)
        self.capture_timer.start(1000)
        self.update_timeout_button()

    def poll_timeout(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.capture_timer.stop()
            self.finish_capture()
        else:
            self.update_timeout_button()

    def update_timeout_button(self):
        self.get_info_btn.setText(f"CAPTURING IN {self.remaining_time}...")

    def poll_capture(self):
        lbutton = win32api.GetAsyncKeyState(0x01)
        if self.waiting_for_release:
            if lbutton == 0: self.waiting_for_release = False
        else:
            if lbutton < 0:
                self.capture_timer.stop()
                QTimer.singleShot(150, self.finish_capture)

    def finish_capture(self):
        self.get_info_btn.setText("GET ITEM INFO")
        self.get_info_btn.setStyleSheet("")
        self.apply_theme() # Reset colors
        
        strategy = self.config_data.get("gui_settings", {}).get("capture_strategy", "Hover (Mouse)")
        
        if strategy == "Hover (Mouse)":
            pos = win32api.GetCursorPos()
            hwnd = win32gui.WindowFromPoint(pos)
        else:
            hwnd = win32gui.GetForegroundWindow()

        if not hwnd: return
        hwnd = win32gui.GetAncestor(hwnd, 2)
        
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            h = win32api.OpenProcess(0x0400 | 0x0010, False, pid)
            path = win32process.GetModuleFileNameEx(h, 0)
            exe = os.path.basename(path)
            win32api.CloseHandle(h)
        except: path, exe = "Unknown", "Unknown"
        
        sel = CaptureSelectionDialog(self, {"Exe": exe, "Title": title, "Class": cls, "Path": path})
        if sel.exec():
            self.open_add_dialog(initial_kind=sel.selected_kind, initial_id=sel.selected_val)

    def toggle_settings(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())

    def restart_app(self):
        os.execl(sys.executable, sys.executable, *sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KomorebiApp()
    window.show()
    sys.exit(app.exec())
