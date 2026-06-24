import sys
import os
import json
import subprocess
import shutil

# Suppress Qt font warnings
os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false"

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea,
                             QFormLayout, QFrame, QColorDialog, QDialog, QTextEdit, QListWidget, QListWidgetItem,
                             QComboBox, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QByteArray, QRectF
from PyQt6.QtGui import QColor, QPainter, QImage
from PyQt6.QtSvg import QSvgRenderer

# CYBERPUNK THEME PALETTE (from THEME_GUIDE.md)
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

# Relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LEGACY_CONFIG_FILE = os.path.join(SCRIPT_DIR, "ahk_config.json")
DEFAULT_PROFILE_NAME = "Default"
ACTION_OPTIONS = [
    ("send_text", "Send Text"),
    ("copy_text", "Copy Text"),
    ("no_action", "No Action"),
]
TRIGGER_OPTIONS = [
    ("click", "Left Click"),
    ("context_menu", "Right Click"),
    ("double_click", "Double Click"),
]


def sanitize_profile_name(name):
    cleaned = "".join(ch for ch in name.strip() if ch not in r'<>:"/\|?*')
    return cleaned.strip(" .")


def profile_dir(profile_name):
    return os.path.join(SCRIPT_DIR, profile_name)


def profile_config_path(profile_name):
    return os.path.join(profile_dir(profile_name), "ahk_config.json")


def profile_ahk_path(profile_name):
    return os.path.join(profile_dir(profile_name), "generate_Button_AHK.ahk")


def profile_assets_dir(profile_name):
    return os.path.join(profile_dir(profile_name), "assets")


def profile_exists(profile_name):
    return os.path.isdir(profile_dir(profile_name)) and os.path.exists(profile_config_path(profile_name))


def list_profile_names():
    names = []
    for entry in sorted(os.listdir(SCRIPT_DIR), key=str.lower):
        path = os.path.join(SCRIPT_DIR, entry)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "ahk_config.json")):
            names.append(entry)
    return names


def combo_set_code(combo, code, fallback_index=0):
    for i in range(combo.count()):
        if combo.itemData(i) == code:
            combo.setCurrentIndex(i)
            return
    if combo.count():
        combo.setCurrentIndex(fallback_index)


def combo_add_options(combo, options):
    for code, label in options:
        combo.addItem(label, code)


def ahk_escape(value):
    return (value or "").replace('"', '""')


def trigger_to_event(trigger_code):
    return {
        "click": "Click",
        "context_menu": "ContextMenu",
        "double_click": "DoubleClick",
    }.get(trigger_code, "Click")


def action_to_ahk(action_code, payload):
    payload = ahk_escape(payload)
    if action_code == "copy_text":
        return f'A_Clipboard := "{payload}"'
    if action_code == "send_text":
        return f'SendText("{payload}")'
    return None

class ReorderDialog(QDialog):
    def __init__(self, rows, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reorder Rows (Drag & Drop)")
        self.resize(400, 500)
        self.layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.setStyleSheet(f"background-color: #1a1a1a; color: {CP_CYAN}; font-family: 'Consolas'; font-size: 11pt;")
        
        for row in rows:
            title = row.title_input.text() or "Untitled Row"
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, row)
            self.list_widget.addItem(item)
            
        self.layout.addWidget(self.list_widget)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("SAVE ORDER")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        self.layout.addLayout(btns)

    def get_new_order(self):
        new_order = []
        for i in range(self.list_widget.count()):
            new_order.append(self.list_widget.item(i).data(Qt.ItemDataRole.UserRole))
        return new_order

class SVGInputDialog(QDialog):
    def __init__(self, initial_code="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("SVG Code Editor")
        self.resize(500, 400)
        self.layout = QVBoxLayout(self)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("<svg ...> ... </svg>")
        self.editor.setPlainText(initial_code)
        self.editor.setStyleSheet(f"background-color: #1a1a1a; color: {CP_CYAN}; font-family: 'Consolas';")
        self.layout.addWidget(self.editor)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("SAVE")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        self.layout.addLayout(btns)

    def get_code(self):
        return self.editor.toPlainText().strip()

class RowWidget(QFrame):
    def __init__(self, data=None, on_remove=None, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"border: 1px solid {CP_DIM}; background-color: {CP_PANEL}; margin-bottom: 5px;")
        self.on_remove = on_remove
        
        self.layout = QVBoxLayout(self)
        
        # Header: Title and Remove Row
        header_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Row Title (e.g., Name/Label)")
        self.title_input.setText(data.get("title", "") if data else "")
        self.title_color = data.get("title_color", "FFCC00") if data else "FFCC00"
        self.title_text_color = data.get("title_text_color", "000000") if data else "000000"
        self.title_color_btn = QPushButton()
        self.title_color_btn.setFixedSize(50, 24)
        self.title_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_color_btn.clicked.connect(self._pick_title_color)
        self.title_text_color_btn = QPushButton()
        self.title_text_color_btn.setFixedSize(50, 24)
        self.title_text_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_text_color_btn.clicked.connect(self._pick_title_text_color)
        self._update_title_color_btn()
        self._update_title_text_color_btn()
        header_layout.addWidget(QLabel("TITLE:"))
        header_layout.addWidget(self.title_input)
        header_layout.addWidget(self.title_color_btn)
        header_layout.addWidget(self.title_text_color_btn)

        self.title_action_combo = QComboBox()
        combo_add_options(self.title_action_combo, ACTION_OPTIONS)
        combo_set_code(self.title_action_combo, data.get("title_action", "send_text") if data else "send_text")
        self.title_action_combo.setFixedWidth(110)

        self.title_trigger_combo = QComboBox()
        combo_add_options(self.title_trigger_combo, TRIGGER_OPTIONS)
        combo_set_code(self.title_trigger_combo, data.get("title_trigger", "click") if data else "click")
        self.title_trigger_combo.setFixedWidth(110)

        header_layout.addWidget(self.title_action_combo)
        header_layout.addWidget(self.title_trigger_combo)
        
        remove_row_btn = QPushButton("×")
        remove_row_btn.setFixedWidth(30)
        remove_row_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; font-weight: bold;")
        remove_row_btn.clicked.connect(self.remove_self)
        header_layout.addWidget(remove_row_btn)
        self.layout.addLayout(header_layout)

        # Buttons Area
        self.btns_container = QWidget()
        self.btns_layout = QVBoxLayout(self.btns_container)
        self.layout.addWidget(self.btns_container)
        
        add_btn_btn = QPushButton("+ ADD ACTION BUTTON")
        add_btn_btn.clicked.connect(lambda: self.add_button_ui())
        self.layout.addWidget(add_btn_btn)

        if data and "buttons" in data:
            for b in data["buttons"]:
                self.add_button_ui(b)
        else:
            # Default empty button
            self.add_button_ui()

    def _update_title_color_btn(self):
        c = self.title_color
        r, g, b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
        fg = "black" if (r*299+g*587+b*114)/1000 > 128 else "white"
        self.title_color_btn.setText(f"#{c}")
        self.title_color_btn.setStyleSheet(f"background-color: #{c}; color: {fg}; border: 1px solid #888; font-size: 7pt; font-weight: bold; padding: 0;")

    def _pick_title_color(self):
        color = QColorDialog.getColor(QColor(f"#{self.title_color}"))
        if color.isValid():
            self.title_color = color.name().upper().strip("#")
            self._update_title_color_btn()

    def _update_title_text_color_btn(self):
        c = self.title_text_color
        r, g, b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
        fg = "black" if (r*299+g*587+b*114)/1000 > 128 else "white"
        self.title_text_color_btn.setText(f"#{c}")
        self.title_text_color_btn.setStyleSheet(f"background-color: #{c}; color: {fg}; border: 1px solid #888; font-size: 7pt; font-weight: bold; padding: 0;")

    def _pick_title_text_color(self):
        color = QColorDialog.getColor(QColor(f"#{self.title_text_color}"))
        if color.isValid():
            self.title_text_color = color.name().upper().strip("#")
            self._update_title_text_color_btn()

    def refresh_widths(self):
        if not self.parent_app: return
        try:
            lw = int(self.parent_app.settings_panel.ui_label_w.text())
            tw = int(self.parent_app.settings_panel.ui_text_w.text())
            for i in range(self.btns_layout.count()):
                btn_frame = self.btns_layout.itemAt(i).widget()
                if btn_frame:
                    inputs = btn_frame.findChildren(QLineEdit)
                    if len(inputs) >= 2:
                        inputs[0].setFixedWidth(lw)
                        inputs[1].setFixedWidth(tw)
        except: pass

    def add_button_ui(self, b_data=None):
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.Shape.Panel)
        btn_frame.setStyleSheet(f"border: 1px dashed {CP_DIM}; padding: 2px;")
        blayout = QHBoxLayout(btn_frame)
        blayout.setContentsMargins(0, 0, 0, 0)
        blayout.setSpacing(4)
        
        label_input = QLineEdit()
        label_input.setPlaceholderText("Label")
        label_input.setText(b_data.get("label", "") if b_data else "")
        
        text_input = QLineEdit()
        text_input.setPlaceholderText("Text")
        text_input.setText(b_data.get("text", "") if b_data else "")

        action_combo = QComboBox()
        combo_add_options(action_combo, ACTION_OPTIONS)
        combo_set_code(action_combo, b_data.get("action", "send_text") if b_data else "send_text")
        action_combo.setFixedWidth(110)

        trigger_combo = QComboBox()
        combo_add_options(trigger_combo, TRIGGER_OPTIONS)
        combo_set_code(trigger_combo, b_data.get("trigger", "click") if b_data else "click")
        trigger_combo.setFixedWidth(110)

        # SVG Code Storage
        btn_frame.svg_code = b_data.get("svg_code", "") if b_data else ""
        
        svg_btn = QPushButton("SVG")
        svg_btn.setFixedWidth(50)
        def open_svg_dialog():
            dlg = SVGInputDialog(btn_frame.svg_code, self)
            if dlg.exec():
                btn_frame.svg_code = dlg.get_code()
                svg_btn.setStyleSheet(f"background-color: {CP_CYAN if btn_frame.svg_code else CP_DIM}; color: black;")
        
        svg_btn.clicked.connect(open_svg_dialog)
        if btn_frame.svg_code:
            svg_btn.setStyleSheet(f"background-color: {CP_CYAN}; color: black;")

        # BG Color Picker Button
        bg_btn = QPushButton("BG")
        bg_btn.setObjectName("bg_btn")
        bg_btn.setFixedWidth(35)
        bg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bg_btn.color_val = b_data.get("color", "00CCFF") if b_data else "00CCFF"

        # TX Color Picker Button
        tx_btn = QPushButton("TX")
        tx_btn.setObjectName("tx_btn")
        tx_btn.setFixedWidth(35)
        tx_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tx_btn.color_val = b_data.get("text_color", "000000") if b_data else "000000"

        def update_styles():
            bg_btn.setStyleSheet(f"background-color: #{bg_btn.color_val}; color: {'white' if bg_btn.color_val == '000000' else 'black'}; border: 1px solid white; font-size: 8pt; font-weight: bold;")
            tx_btn.setStyleSheet(f"background-color: #{tx_btn.color_val}; color: {'white' if tx_btn.color_val == '000000' else 'black'}; border: 1px solid white; font-size: 8pt; font-weight: bold;")
        
        def pick_bg():
            color = QColorDialog.getColor(QColor(f"#{bg_btn.color_val}"))
            if color.isValid():
                bg_btn.color_val = color.name().upper().strip("#")
                update_styles()

        def pick_tx():
            color = QColorDialog.getColor(QColor(f"#{tx_btn.color_val}"))
            if color.isValid():
                tx_btn.color_val = color.name().upper().strip("#")
                update_styles()

        bg_btn.clicked.connect(pick_bg)
        tx_btn.clicked.connect(pick_tx)
        update_styles()

        rem_btn = QPushButton("-")
        rem_btn.setFixedWidth(25)
        rem_btn.clicked.connect(lambda: btn_frame.deleteLater())

        label_tag = QLabel("L:")
        label_tag.setFixedWidth(20)
        label_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_tag.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        blayout.addWidget(label_tag)
        blayout.addWidget(label_input)
        text_tag = QLabel("T:")
        text_tag.setFixedWidth(20)
        text_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_tag.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        blayout.addWidget(text_tag)
        blayout.addWidget(text_input)
        blayout.addWidget(action_combo)
        blayout.addWidget(trigger_combo)
        blayout.addWidget(svg_btn)
        blayout.addWidget(bg_btn)
        blayout.addWidget(tx_btn)
        blayout.addWidget(rem_btn)
        
        self.btns_layout.addWidget(btn_frame)
        self.refresh_widths()

    def remove_self(self):
        if self.on_remove:
            self.on_remove(self)

    def get_data(self):
        row_data = {
            "title": self.title_input.text(),
            "title_color": self.title_color,
            "title_text_color": self.title_text_color,
            "title_action": self.title_action_combo.currentData(),
            "title_trigger": self.title_trigger_combo.currentData(),
            "buttons": []
        }
        for i in range(self.btns_layout.count()):
            btn_frame = self.btns_layout.itemAt(i).widget()
            if btn_frame:
                inputs = btn_frame.findChildren(QLineEdit)
                bg = btn_frame.findChild(QPushButton, "bg_btn").color_val
                tx = btn_frame.findChild(QPushButton, "tx_btn").color_val
                combos = btn_frame.findChildren(QComboBox)
                row_data["buttons"].append({
                    "label": inputs[0].text(),
                    "text": inputs[1].text(),
                    "svg_code": getattr(btn_frame, "svg_code", ""),
                    "color": bg,
                    "text_color": tx,
                    "action": combos[0].currentData() if len(combos) > 0 else "send_text",
                    "trigger": combos[1].currentData() if len(combos) > 1 else "click"
                })
        return row_data

    def matches(self, search_text):
        if not search_text: return True
        search_text = search_text.lower()
        if search_text in self.title_input.text().lower(): return True
        for i in range(self.btns_layout.count()):
            btn_frame = self.btns_layout.itemAt(i).widget()
            if btn_frame:
                inputs = btn_frame.findChildren(QLineEdit)
                for inp in inputs:
                    if search_text in inp.text().lower(): return True
        return False

class SettingsPanel(QGroupBox):
    def __init__(self, update_callback):
        super().__init__("SETTINGS")
        self.setVisible(False)
        self.layout = QFormLayout(self)
        
        self.auto_hide = QLineEdit("True")
        self.sleep_delay = QLineEdit("200")
        self.font_size = QLineEdit("12")
        self.ui_label_w = QLineEdit("80")
        self.ui_text_w = QLineEdit("200")
        self.title_h = QLineEdit("30")
        self.title_w = QLineEdit("200")
        self.btn_h = QLineEdit("30")
        self.btn_w = QLineEdit("100")
        self.win_w = QLineEdit("1000")
        self.win_h = QLineEdit("800")
        
        self.ui_label_w.textChanged.connect(update_callback)
        self.ui_text_w.textChanged.connect(update_callback)
        self.win_w.textChanged.connect(update_callback)
        self.win_h.textChanged.connect(update_callback)

        def row(field1, *pairs):
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
            h.addWidget(field1)
            for lbl, field in pairs:
                h.addWidget(QLabel(lbl)); h.addWidget(field)
            return w

        self.layout.addRow("Auto-Hide / Sleep (ms):", row(self.auto_hide, ("Sleep:", self.sleep_delay)))
        self.layout.addRow("Font Size:", self.font_size)
        self.layout.addRow("UI Label / Text Width:", row(self.ui_label_w, ("T:", self.ui_text_w)))
        self.layout.addRow("Title H / W:", row(self.title_h, ("W:", self.title_w)))
        self.layout.addRow("Button H / W:", row(self.btn_h, ("W:", self.btn_w)))
        self.layout.addRow("Window W / H:", row(self.win_w, ("H:", self.win_h)))

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberAHK Generator")
        self.resize(1000, 800)
        self.rows = []
        self.current_profile_name = None
        self._loading_profile = False

        self._ensure_profile_storage()

        # Global Theme Application
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QScrollArea {{ background: transparent; border: none; }}
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 3px 6px;
            }}
            QComboBox::drop-down {{ border: 0px; width: 18px; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)

        # Toolbar
        toolbar = QHBoxLayout()
        self.profile_combo = QComboBox()
        self.profile_combo.setFixedWidth(180)
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        toolbar.addWidget(QLabel("PROFILE:"))
        toolbar.addWidget(self.profile_combo)

        new_profile_btn = QPushButton("+ NEW PROFILE")
        new_profile_btn.clicked.connect(self.create_profile)
        toolbar.addWidget(new_profile_btn)

        add_row_btn = QPushButton("+ NEW ROW")
        add_row_btn.clicked.connect(self.add_row)

        reorder_btn = QPushButton("REORDER")
        reorder_btn.clicked.connect(self.open_reorder_dialog)
        
        gen_btn = QPushButton("GENERATE AHK")
        gen_btn.setStyleSheet(f"background-color: {CP_GREEN}; color: black;")
        gen_btn.clicked.connect(self.generate_ahk)

        restart_btn = QPushButton("RESTART APP")
        restart_btn.clicked.connect(self.restart_app)

        settings_btn = QPushButton("SETTINGS")
        settings_btn.clicked.connect(self.toggle_settings)

        toolbar.addWidget(add_row_btn)
        toolbar.addWidget(reorder_btn)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search Rows/Buttons...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.filter_rows)
        toolbar.addWidget(self.search_input)

        toolbar.addStretch()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-size: 9pt;")
        toolbar.addWidget(self.status_label)
        toolbar.addWidget(settings_btn)
        toolbar.addWidget(restart_btn)
        toolbar.addWidget(gen_btn)
        self.main_layout.addLayout(toolbar)

        # Settings Panel (Hidden by default)
        self.settings_panel = SettingsPanel(self.update_ui_widths)
        self.main_layout.addWidget(self.settings_panel)

        # Content Area (Scrollable)
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.rows_layout = QVBoxLayout(self.scroll_content)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll)

        self.load_config()

    def update_ui_widths(self):
        try:
            ww = int(self.settings_panel.win_w.text())
            wh = int(self.settings_panel.win_h.text())
            self.resize(ww, wh)
        except: pass
        for row in self.rows:
            row.refresh_widths()

    def open_reorder_dialog(self):
        dlg = ReorderDialog(self.rows, self)
        if dlg.exec():
            new_order = dlg.get_new_order()
            self.apply_reorder(new_order)

    def apply_reorder(self, new_order):
        # Update internal list
        self.rows = new_order
        
        # Refresh UI layout
        # 1. Remove all from layout
        for r in self.rows:
            self.rows_layout.removeWidget(r)
            
        # 2. Add back in new order
        for r in self.rows:
            self.rows_layout.addWidget(r)

    def filter_rows(self, text):
        for row in self.rows:
            row.setVisible(row.matches(text))

    def add_row(self, data=None):
        row = RowWidget(data, on_remove=self.remove_row, parent_app=self)
        self.rows.append(row)
        self.rows_layout.addWidget(row)
        row.setVisible(row.matches(self.search_input.text()))

    def remove_row(self, row_widget):
        self.rows.remove(row_widget)
        row_widget.deleteLater()

    def toggle_settings(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())

    def restart_app(self):
        self.save_config()
        os.execv(sys.executable, ['python'] + sys.argv)

    def _ensure_profile_storage(self):
        if os.path.exists(LEGACY_CONFIG_FILE) and not list_profile_names():
            default_dir = profile_dir(DEFAULT_PROFILE_NAME)
            os.makedirs(default_dir, exist_ok=True)
            shutil.copy2(LEGACY_CONFIG_FILE, profile_config_path(DEFAULT_PROFILE_NAME))

    def refresh_profile_list(self, select_name=None):
        profiles = list_profile_names()
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        self.profile_combo.addItems(profiles)
        if select_name and select_name in profiles:
            self.profile_combo.setCurrentText(select_name)
        self.profile_combo.blockSignals(False)
        if select_name and select_name in profiles:
            self.current_profile_name = select_name
            self.status_label.setText(f"Profile: {select_name}")

    def current_config_file(self):
        if not self.current_profile_name:
            return None
        return profile_config_path(self.current_profile_name)

    def current_ahk_file(self):
        if not self.current_profile_name:
            return None
        return profile_ahk_path(self.current_profile_name)

    def current_assets_dir(self):
        if not self.current_profile_name:
            return None
        return profile_assets_dir(self.current_profile_name)

    def clear_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        self.rows = []

    def load_profile(self, profile_name):
        if not profile_name:
            return
        self._loading_profile = True
        try:
            self.clear_rows()
            self.current_profile_name = profile_name
            self.status_label.setText(f"Profile: {profile_name}")
            config_file = self.current_config_file()
            if config_file and os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    QMessageBox.warning(self, "Load Error", f"Could not load profile '{profile_name}': {e}")
                    data = None

                if data is not None:
                    rows_data = []
                    if isinstance(data, dict):
                        if "settings" in data:
                            s = data["settings"]
                            if "auto_hide" in s: self.settings_panel.auto_hide.setText(s["auto_hide"])
                            if "sleep_delay" in s: self.settings_panel.sleep_delay.setText(s["sleep_delay"])
                            if "font_size" in s: self.settings_panel.font_size.setText(s["font_size"])
                            if "ui_label_w" in s: self.settings_panel.ui_label_w.setText(s["ui_label_w"])
                            if "ui_text_w" in s: self.settings_panel.ui_text_w.setText(s["ui_text_w"])
                            if "title_h" in s: self.settings_panel.title_h.setText(s["title_h"])
                            if "title_w" in s: self.settings_panel.title_w.setText(s["title_w"])
                            if "btn_h" in s: self.settings_panel.btn_h.setText(s["btn_h"])
                            if "btn_w" in s: self.settings_panel.btn_w.setText(s["btn_w"])
                            if "win_w" in s: self.settings_panel.win_w.setText(s["win_w"])
                            if "win_h" in s: self.settings_panel.win_h.setText(s["win_h"])
                        rows_data = data.get("rows", [])
                    else:
                        rows_data = data

                    for r_data in rows_data:
                        self.add_row(r_data)
                    self.update_ui_widths()
            else:
                self.add_row({"title": "Example Name", "buttons": [{"label": "en", "text": "Hello", "color": "00CCFF"}]})
        finally:
            self._loading_profile = False

    def load_config(self):
        self.refresh_profile_list()
        if self.profile_combo.count() == 0:
            self.create_profile(DEFAULT_PROFILE_NAME)
            return
        first_profile = self.profile_combo.currentText() or self.profile_combo.itemText(0)
        self.load_profile(first_profile)

    def save_config(self):
        if not self.current_profile_name:
            return
        os.makedirs(profile_dir(self.current_profile_name), exist_ok=True)
        data = {
            "settings": {
                "auto_hide": self.settings_panel.auto_hide.text(),
                "sleep_delay": self.settings_panel.sleep_delay.text(),
                "font_size": self.settings_panel.font_size.text(),
                "ui_label_w": self.settings_panel.ui_label_w.text(),
                "ui_text_w": self.settings_panel.ui_text_w.text(),
                "title_h": self.settings_panel.title_h.text(),
                "title_w": self.settings_panel.title_w.text(),
                "btn_h": self.settings_panel.btn_h.text(),
                "btn_w": self.settings_panel.btn_w.text(),
                "win_w": self.settings_panel.win_w.text(),
                "win_h": self.settings_panel.win_h.text()
            },
            "rows": [r.get_data() for r in self.rows]
        }
        with open(self.current_config_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def create_profile(self, checked=False, profile_name=None):
        if isinstance(checked, str) and profile_name is None:
            profile_name = checked
            checked = False

        if profile_name is None:
            profile_name, ok = QInputDialog.getText(self, "New Profile", "Profile name:")
            if not ok:
                return

        profile_name = sanitize_profile_name(profile_name)
        if not profile_name:
            QMessageBox.warning(self, "Invalid Name", "Profile name cannot be empty.")
            return
        if profile_exists(profile_name):
            QMessageBox.information(self, "Profile Exists", f"Profile '{profile_name}' already exists.")
            return

        os.makedirs(profile_dir(profile_name), exist_ok=True)
        template = {
            "settings": {
                "auto_hide": self.settings_panel.auto_hide.text(),
                "sleep_delay": self.settings_panel.sleep_delay.text(),
                "font_size": self.settings_panel.font_size.text(),
                "ui_label_w": self.settings_panel.ui_label_w.text(),
                "ui_text_w": self.settings_panel.ui_text_w.text(),
                "title_h": self.settings_panel.title_h.text(),
                "title_w": self.settings_panel.title_w.text(),
                "btn_h": self.settings_panel.btn_h.text(),
                "btn_w": self.settings_panel.btn_w.text(),
                "win_w": self.settings_panel.win_w.text(),
                "win_h": self.settings_panel.win_h.text()
            },
            "rows": []
        }
        with open(profile_config_path(profile_name), "w", encoding="utf-8") as f:
            json.dump(template, f, indent=4)

        self.refresh_profile_list(profile_name)
        self.profile_combo.setCurrentText(profile_name)
        self.load_profile(profile_name)

    def on_profile_changed(self, profile_name):
        if self._loading_profile or not profile_name:
            return
        if profile_name == self.current_profile_name:
            return
        if self.current_profile_name:
            self.save_config()
        self.load_profile(profile_name)

    def generate_ahk(self):
        self.save_config()
        data = [r.get_data() for r in self.rows]
        
        # Setup assets directory
        assets_dir = self.current_assets_dir() or os.path.join(SCRIPT_DIR, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        ahk_code = [
            "#Requires AutoHotkey v2.0",
            "",
            'myGui := Gui("+AlwaysOnTop", "Generated Keyboard")',
            'myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")',
            "myGui.MarginX := 20",
            "myGui.MarginY := 20",
            ""
        ]

        for i, row in enumerate(data):
            y_pos = "ym" if i == 0 else "y+5"
            title = row["title"]
            ahk_code.append(f'; {title}')
            
            # Title button/label
            tc = row.get("title_color", "FFCC00")
            ttc = row.get("title_text_color", "000000")
            title_action = row.get("title_action", "send_text")
            title_trigger = row.get("title_trigger", "click")
            ahk_code.append(f'myGui.SetFont("s12 Bold c{ttc}", "Jetbrainsmono nfp")')
            th = self.settings_panel.title_h.text() or "30"
            tw = self.settings_panel.title_w.text() or "200"
            bh = self.settings_panel.btn_h.text() or "30"
            bw = self.settings_panel.btn_w.text() or "100"
            ahk_code.append(f'titleCtrl := myGui.Add("Button", "xm {y_pos} w{tw} h{th} +Border Center Background{tc}", "{ahk_escape(title)}")')
            title_action_line = action_to_ahk(title_action, title)
            if title_action_line:
                ahk_code.append(f'titleCtrl.OnEvent("{trigger_to_event(title_trigger)}", (*) => {title_action_line})')
            ahk_code.append(f'myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")')
            
            for j, btn in enumerate(row["buttons"]):
                label = btn["label"]
                text = btn["text"]
                bg = btn.get("color", "00CCFF")
                fg = btn.get("text_color", "000000")
                svg_code = btn.get("svg_code", "")
                action_code = btn.get("action", "send_text")
                trigger_code = btn.get("trigger", "click")
                action_line = action_to_ahk(action_code, text)

                if svg_code:
                    # Priority 1: SVG Code (Render to PNG for AHK compatibility)
                    png_filename = f"btn_{i}_{j}.png"
                    png_path = os.path.join(assets_dir, png_filename)
                    
                    # Target dimensions from settings
                    target_w = int(self.settings_panel.btn_w.text() or "100")
                    target_h = int(self.settings_panel.btn_h.text() or "30")
                    image = QImage(target_w, target_h, QImage.Format.Format_ARGB32)
                    image.fill(Qt.GlobalColor.transparent)
                    
                    painter = QPainter(image)
                    try:
                        renderer = QSvgRenderer(QByteArray(svg_code.encode("utf-8")))
                        # Calculate aspect ratio to prevent stretching
                        svg_size = renderer.defaultSize()
                        if not svg_size.isEmpty():
                            ratio = min(target_w / svg_size.width(), target_h / svg_size.height())
                            # Padding: 90% of max size to leave small margin
                            fit_w = float(svg_size.width() * ratio * 0.9)
                            fit_h = float(svg_size.height() * ratio * 0.9)
                            
                            # Center the rect
                            x = float(target_w - fit_w) / 2.0
                            y = float(target_h - fit_h) / 2.0
                            renderer.render(painter, QRectF(x, y, fit_w, fit_h))
                        else:
                            renderer.render(painter)
                    except Exception as e:
                        print(f"SVG Render Error: {e}")
                    finally:
                        painter.end()

                    image.save(png_path, "PNG")
                    ahk_img_path = f"assets\\{png_filename}"
                    ahk_code.append(f'btn := myGui.Add("Picture", "x+5 yp w{bw} h{bh} +Border Background{bg}", "{ahk_img_path}")')
                else:
                    # Priority 2: Text Label
                    ahk_code.append(f'btn := myGui.Add("Button", "x+5 yp w{bw} h{bh} +Border Center Background{bg}", "{ahk_escape(label)}")')
                    ahk_code.append(f'btn.SetFont("c{fg}")')
                
                if action_line:
                    ahk_code.append(f'btn.OnEvent("{trigger_to_event(trigger_code)}", (*) => {action_line})')
            
            ahk_code.append("")

        ahk_code.extend([
            "myGui.Show()",
            'myGui.OnEvent("Close", (*) => ExitApp())',
            "",
            "; Function to send text and briefly hide the GUI",
            "SendText(text) {",
            "    myGui.Hide()",
            "    Sleep(200)",
            "    Send(text)",
            "    Sleep(200)",
            "    myGui.Show()",
            "}"
        ])

        with open(self.current_ahk_file(), "w", encoding="utf-8-sig") as f:
            f.write("\n".join(ahk_code))
        
        self.status_label.setText("✔ Generated")
        QTimer.singleShot(1000, lambda: self.status_label.setText(""))

    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
