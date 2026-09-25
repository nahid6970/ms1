import sys
import os
import json
import time
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, 
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QLayout,
    QDialog, QMessageBox, QFileDialog, QMenu, QStyle, QSlider, QSpinBox, QCheckBox,
    QListWidget, QListWidgetItem, QInputDialog
)
from PyQt6.QtCore import Qt, QSize, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QAction, QFontMetrics

# --- CONFIGURATION & CONSTANTS ---
DATA_FILE = "launcher_data.json"

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_ORANGE = "#ff934b"       # Accent: Orange
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

# --- UTILITIES ---
def get_data_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)

def load_data():
    path = get_data_path()
    if not os.path.exists(path):
        return {
            "directories": [],
            "commands": [
                {"name": "GEMINI", "template": 'wt -d "{path}" powershell -NoExit -Command gemini', "category": "System"},
                {"name": "GEMINI RESUME", "template": 'wt -d "{path}" powershell -NoExit -Command "gemini --resume"', "category": "System"},
                {"name": "Open in Explorer", "template": 'explorer "{path}"', "category": "System"},
                {"name": "Open in VS Code", "template": 'code "{path}"', "category": "System"},
                {"name": "Open in Terminal", "template": 'wt -d "{path}"', "category": "System"}
            ],
            "settings": {}
        }
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return {"directories": [], "commands": [], "settings": {}}

def save_data(data):
    try:
        with open(get_data_path(), 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

def restart_app():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# --- CUSTOM UI COMPONENTS ---

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, hspacing=-1, vspacing=-1):
        super(FlowLayout, self).__init__(parent)
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []
        self.setContentsMargins(margin, margin, margin, margin)

    def __del__(self):
        del self._items[:]

    def addItem(self, item):
        self._items.append(item)

    def horizontalSpacing(self):
        if self._hspacing >= 0:
            return self._hspacing
        else:
            return self.smartSpacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self._vspacing >= 0:
            return self._vspacing
        else:
            return self.smartSpacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self.getContentsMargins()
        size += QSize(left + right, top + bottom)
        return size

    def smartSpacing(self, pm):
        parent = self.parent()
        if parent is None:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        else:
            return parent.spacing()

    def doLayout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(+left, +top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._items:
            widget = item.widget()
            space_x = self.horizontalSpacing()
            if space_x == -1: space_x = 10
            space_y = self.verticalSpacing()
            if space_y == -1: space_y = 10
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom

class CyberCard(QPushButton):
    def __init__(self, name, path, category, last_used=0, settings=None, parent=None):
        super().__init__(parent)
        self.name = name or os.path.basename(path.rstrip(os.sep))
        self.path = path
        self.category = category
        self.last_used = last_used
        
        settings = settings or {}
        name_font_size = settings.get("name_font_size", 11)
        name_bold = settings.get("name_bold", True)
        show_category = settings.get("show_category", True)
        
        self.setFixedSize(200, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Path: {path}\nLast Used: {time.ctime(last_used) if last_used else 'Never'}")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.cat_label = QLabel(f"[{category.upper()}]")
        self.cat_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 8pt; border: none; background: transparent;")
        self.cat_label.setVisible(show_category)
        
        self.name_label = QLabel(self.name)
        weight = "bold" if name_bold else "normal"
        self.name_label.setStyleSheet(f"color: {CP_TEXT}; font-weight: {weight}; font-size: {name_font_size}pt; border: none; background: transparent;")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.path_label = QLabel()
        self.path_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 7pt; border: none; background: transparent;")
        
        metrics = QFontMetrics(QFont("Consolas", 7))
        elided_path = metrics.elidedText(path, Qt.TextElideMode.ElideRight, 180)
        self.path_label.setText(elided_path)
        self.path_label.setWordWrap(False)
        
        self.layout.addWidget(self.cat_label)
        self.layout.addStretch()
        self.layout.addWidget(self.name_label)
        self.layout.addStretch()
        self.layout.addWidget(self.path_label)
        
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #1a1a1a;
                border: 1px solid {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW};
            }}
        """)

class AddCard(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.layout = QVBoxLayout(self)
        self.plus_label = QLabel("+")
        self.plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.plus_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 40pt; font-weight: bold; border: none; background: transparent;")
        
        self.text_label = QLabel("ADD DIRECTORY")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 10pt; font-weight: bold; border: none; background: transparent;")
        
        self.layout.addStretch()
        self.layout.addWidget(self.plus_label)
        self.layout.addWidget(self.text_label)
        self.layout.addStretch()
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_BG};
                border: 2px dashed {CP_DIM};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #111111;
                border: 2px dashed {CP_CYAN};
            }}
        """)

# --- MAIN WINDOW ---

class CardLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Card Launcher")
        self.data = load_data()
        
        # Migration: Ensure Gemini commands exist in the list
        existing_names = [c.get("name") for c in self.data.get("commands", [])]
        if "GEMINI" not in existing_names:
            self.data.setdefault("commands", []).insert(0, {"name": "GEMINI", "template": 'wt -d "{path}" powershell -NoExit -Command gemini', "category": "System"})
        if "GEMINI RESUME" not in existing_names:
            self.data.setdefault("commands", []).insert(1, {"name": "GEMINI RESUME", "template": 'wt -d "{path}" powershell -NoExit -Command "gemini --resume"', "category": "System"})
        save_data(self.data)
        
        saved_width = self.data.get("settings", {}).get("window_width", 900)
        self.setMinimumSize(800, 600)
        self.resize(saved_width, 600)
        
        self.init_ui()
        self.apply_theme()
        self.refresh_cards()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QScrollArea {{ background: transparent; border: none; }}
            QLineEdit, QPlainTextEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search directories...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.textChanged.connect(self.filter_cards)
        
        self.restart_btn = QPushButton("RESTART")
        self.restart_btn.clicked.connect(restart_app)
        self.restart_btn.setStyleSheet(f"color: {CP_RED}; border: 1px solid {CP_RED};")
        
        self.settings_btn = QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(self.show_settings)
        
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(self.restart_btn)
        header_layout.addWidget(self.settings_btn)
        self.main_layout.addLayout(header_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.card_container = QWidget()
        self.flow_layout = FlowLayout(self.card_container, margin=20, hspacing=20, vspacing=20)
        self.scroll.setWidget(self.card_container)
        self.main_layout.addWidget(self.scroll)
        
        self.status_bar = QLabel("SYSTEM READY")
        self.status_bar.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        self.main_layout.addWidget(self.status_bar)

    def refresh_cards(self):
        self.setUpdatesEnabled(False)
        try:
            while self.flow_layout.count():
                item = self.flow_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Sort directories by last_used (descending)
            sorted_dirs = sorted(self.data.get("directories", []), key=lambda x: x.get("last_used", 0), reverse=True)
            
            # Add Directory Cards
            settings = self.data.get("settings", {})
            for d in sorted_dirs:
                card = CyberCard(d.get("name"), d.get("path"), d.get("category", "General"), d.get("last_used", 0), settings=settings)
                card.clicked.connect(lambda checked, arg=d: self.on_card_clicked(arg))
                card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                card.customContextMenuRequested.connect(lambda pos, arg=d: self.show_context_menu(pos, arg))
                self.flow_layout.addWidget(card)

            # Add "Add Card" last
            add_btn = AddCard()
            add_btn.clicked.connect(self.add_directory)
            self.flow_layout.addWidget(add_btn)
        finally:
            self.setUpdatesEnabled(True)

    def filter_cards(self, text):
        text = text.lower()
        for i in range(self.flow_layout.count()):
            widget = self.flow_layout.itemAt(i).widget()
            if isinstance(widget, CyberCard):
                visible = (text in widget.name.lower() or text in widget.path.lower() or text in widget.category.lower())
                widget.setVisible(visible)

    def on_card_clicked(self, dir_obj):
        dir_obj["last_used"] = time.time()
        save_data(self.data)
        self.show_actions(dir_obj)

    def show_actions(self, dir_obj):
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}")
        path = dir_obj.get("path")
        for cmd in self.data.get("commands", []):
            action = QAction(cmd.get("name"), self)
            action.triggered.connect(lambda checked, t=cmd.get("template"), p=path: self.execute_command(t, p))
            menu.addAction(action)
        menu.exec(QCursor.pos())

    def execute_command(self, template, path):
        final_cmd = template.replace("{path}", path)
        try:
            subprocess.Popen(final_cmd, shell=True, creationflags=0x08000000)
            self.status_bar.setText(f"EXECUTED: {final_cmd}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

    def add_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            if any(d["path"] == path for d in self.data["directories"]):
                QMessageBox.warning(self, "Warning", "Directory already in launcher.")
                return
            name, ok = self.get_input("Directory Name", "Enter a display name (optional):")
            category, ok2 = self.get_input("Category", "Enter category (default 'General'):")
            if not category: category = "General"
            new_entry = {"path": path, "name": name, "category": category, "last_used": time.time()}
            self.data["directories"].append(new_entry)
            save_data(self.data)
            self.refresh_cards()

    def get_input(self, title, label):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(label))
        edit = QLineEdit()
        layout.addWidget(edit)
        btns = QHBoxLayout()
        ok_btn = QPushButton("OK"); ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("CANCEL"); cancel_btn.clicked.connect(dialog.reject)
        btns.addWidget(ok_btn); btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        if dialog.exec() == QDialog.DialogCode.Accepted: return edit.text(), True
        return "", False

    def show_context_menu(self, pos, dir_obj):
        card = self.sender()
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}")
        edit_action = QAction("Edit", self); edit_action.triggered.connect(lambda: self.edit_directory(dir_obj))
        remove_action = QAction("Remove", self); remove_action.triggered.connect(lambda: self.remove_directory(dir_obj))
        menu.addAction(edit_action); menu.addAction(remove_action)
        menu.exec(card.mapToGlobal(pos))

    def edit_directory(self, dir_obj):
        name, ok = self.get_input("Edit Name", f"Current: {dir_obj.get('name')}")
        if ok:
            dir_obj["name"] = name
            save_data(self.data)
            self.refresh_cards()

    def remove_directory(self, dir_obj):
        reply = QMessageBox.question(self, "Remove", f"Remove '{dir_obj.get('name') or dir_obj.get('path')}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.data["directories"].remove(dir_obj)
            save_data(self.data)
            self.refresh_cards()

    def update_setting(self, key, value):
        if "settings" not in self.data: self.data["settings"] = {}
        self.data["settings"][key] = value
        save_data(self.data)
        self.refresh_cards()

    def update_window_width(self, width):
        self.resize(width, self.height())
        if "settings" not in self.data: self.data["settings"] = {}
        self.data["settings"]["window_width"] = width
        save_data(self.data)

    def add_custom_command(self, list_widget):
        name, ok = QInputDialog.getText(self, "Add Command", "Command Name:")
        if not ok or not name: return
        template, ok = QInputDialog.getText(self, "Add Command", 'Command Template ({path} for folder):')
        if not ok or not template: return
        self.data.setdefault("commands", []).append({"name": name, "template": template, "category": "Custom"})
        save_data(self.data)
        list_widget.addItem(f"{name} | {template}")

    def remove_custom_command(self, list_widget):
        current_item = list_widget.currentItem()
        if not current_item: return
        index = list_widget.row(current_item)
        if 0 <= index < len(self.data.get("commands", [])):
            self.data["commands"].pop(index)
            save_data(self.data)
            list_widget.takeItem(index)

    def edit_custom_command(self, list_widget):
        current_item = list_widget.currentItem()
        if not current_item: return
        index = list_widget.row(current_item)
        if 0 <= index < len(self.data.get("commands", [])):
            cmd = self.data["commands"][index]
            
            new_name, ok1 = QInputDialog.getText(self, "Edit Command", "Command Name:", text=cmd["name"])
            if not ok1 or not new_name: return
            
            new_template, ok2 = QInputDialog.getText(self, "Edit Command", "Command Template:", text=cmd["template"])
            if not ok2 or not new_template: return
            
            self.data["commands"][index] = {"name": new_name, "template": new_template, "category": cmd.get("category", "Custom")}
            save_data(self.data)
            current_item.setText(f"{new_name} | {new_template}")

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("SETTINGS")
        dialog.setMinimumSize(500, 600)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("--- UI CONFIGURATION ---"))
        settings = self.data.get("settings", {})
        
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Window Width:"))
        width_slider = QSlider(Qt.Orientation.Horizontal); width_slider.setRange(800, 1920); width_slider.setValue(self.width())
        width_spin = QSpinBox(); width_spin.setRange(800, 1920); width_spin.setValue(self.width())
        width_slider.valueChanged.connect(width_spin.setValue); width_spin.valueChanged.connect(width_slider.setValue); width_slider.valueChanged.connect(self.update_window_width)
        width_layout.addWidget(width_slider); width_layout.addWidget(width_spin)
        layout.addLayout(width_layout)
        
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Name Font Size:"))
        font_spin = QSpinBox(); font_spin.setRange(6, 24); font_spin.setValue(settings.get("name_font_size", 11))
        font_spin.valueChanged.connect(lambda val: self.update_setting("name_font_size", val))
        font_layout.addWidget(font_spin)
        layout.addLayout(font_layout)
        
        bold_check = QCheckBox("Bold Project Name"); bold_check.setChecked(settings.get("name_bold", True))
        bold_check.toggled.connect(lambda checked: self.update_setting("name_bold", checked))
        layout.addWidget(bold_check)
        
        cat_check = QCheckBox("Show Category Label"); cat_check.setChecked(settings.get("show_category", True))
        cat_check.toggled.connect(lambda checked: self.update_setting("show_category", checked))
        layout.addWidget(cat_check)
        
        layout.addWidget(QLabel("\n--- COMMAND MANAGEMENT ---"))
        cmd_list = QListWidget()
        cmd_list.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM};")
        for cmd in self.data.get("commands", []): cmd_list.addItem(f"{cmd['name']} | {cmd['template']}")
        layout.addWidget(cmd_list)
        
        cmd_btns = QHBoxLayout()
        add_cmd_btn = QPushButton("ADD"); add_cmd_btn.clicked.connect(lambda: self.add_custom_command(cmd_list))
        edit_cmd_btn = QPushButton("EDIT"); edit_cmd_btn.clicked.connect(lambda: self.edit_custom_command(cmd_list))
        remove_cmd_btn = QPushButton("REMOVE"); remove_cmd_btn.clicked.connect(lambda: self.remove_custom_command(cmd_list))
        cmd_btns.addWidget(add_cmd_btn); cmd_btns.addWidget(edit_cmd_btn); cmd_btns.addWidget(remove_cmd_btn)
        layout.addLayout(cmd_btns)
        
        layout.addStretch()
        close_btn = QPushButton("CLOSE"); close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = CardLauncher()
    window.show()
    sys.exit(app.exec())
