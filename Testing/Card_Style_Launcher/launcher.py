import sys
import os
import json
import time
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, 
    QScrollArea, QFrame, QGridLayout, QSizePolicy, QLayout,
    QDialog, QMessageBox, QFileDialog, QMenu, QStyle
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
    # Use relative path as requested
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)

def load_data():
    path = get_data_path()
    if not os.path.exists(path):
        return {
            "directories": [],
            "commands": [
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
    """Restarts the current Python script."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

# --- CUSTOM UI COMPONENTS ---

class FlowLayout(QLayout):
    """
    Standard FlowLayout implementation for Qt.
    Useful for creating a grid of cards that wraps.
    """
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
    """
    A card-style button for a directory.
    """
    def __init__(self, name, path, category, last_used=0, parent=None):
        super().__init__(parent)
        self.name = name or os.path.basename(path.rstrip(os.sep))
        self.path = path
        self.category = category
        self.last_used = last_used
        
        self.setFixedSize(200, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"Path: {path}\nLast Used: {time.ctime(last_used) if last_used else 'Never'}")
        
        # Simple HTML-like content using layout and labels is better for interactivity, 
        # but for a simple "CyberCard" we can use a layout inside the button or just style it.
        # Since it's a QPushButton, we can't easily add sub-widgets that handle clicks, 
        # but we can set a layout on it.
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.cat_label = QLabel(f"[{category.upper()}]")
        self.cat_label.setStyleSheet(f"color: {CP_CYAN}; font-size: 8pt; border: none; background: transparent;")
        
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold; font-size: 11pt; border: none; background: transparent;")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.path_label = QLabel()
        self.path_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 7pt; border: none; background: transparent;")
        
        # Elide the path if it's too long for the card (card width 200 - padding 20)
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
    """
    Special card for adding a new directory.
    """
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
        self.setMinimumSize(900, 600)
        self.data = load_data()
        
        self.init_ui()
        self.apply_theme()
        self.refresh_cards()

    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}

            QScrollArea {{ background: transparent; border: none; }}
            
            QLineEdit, QPlainTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;       
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}

            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
        """)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("CARD STYLE LAUNCHER")
        title_label.setStyleSheet(f"color: {CP_YELLOW}; font-size: 18pt; font-weight: bold;")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search directories...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.textChanged.connect(self.filter_cards)
        
        self.restart_btn = QPushButton("RESTART")
        self.restart_btn.clicked.connect(restart_app)
        self.restart_btn.setStyleSheet(f"color: {CP_RED}; border: 1px solid {CP_RED};")
        
        self.settings_btn = QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(self.show_settings)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(self.restart_btn)
        header_layout.addWidget(self.settings_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Scroll Area for Cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.card_container = QWidget()
        self.flow_layout = FlowLayout(self.card_container, margin=20, hspacing=20, vspacing=20)
        self.scroll.setWidget(self.card_container)
        
        self.main_layout.addWidget(self.scroll)
        
        # Status Bar
        self.status_bar = QLabel("SYSTEM READY")
        self.status_bar.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        self.main_layout.addWidget(self.status_bar)

    def refresh_cards(self):
        # Clear existing
        while self.flow_layout.count():
            item = self.flow_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Sort directories by last_used (descending)
        sorted_dirs = sorted(
            self.data.get("directories", []), 
            key=lambda x: x.get("last_used", 0), 
            reverse=True
        )
        
        # Add "Add Card" first
        add_btn = AddCard()
        add_btn.clicked.connect(self.add_directory)
        self.flow_layout.addWidget(add_btn)
        
        # Add Directory Cards
        for d in sorted_dirs:
            card = CyberCard(
                d.get("name"), 
                d.get("path"), 
                d.get("category", "General"),
                d.get("last_used", 0)
            )
            card.clicked.connect(lambda checked, arg=d: self.on_card_clicked(arg))
            card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            card.customContextMenuRequested.connect(lambda pos, arg=d: self.show_context_menu(pos, arg))
            self.flow_layout.addWidget(card)

    def filter_cards(self, text):
        text = text.lower()
        for i in range(self.flow_layout.count()):
            widget = self.flow_layout.itemAt(i).widget()
            if isinstance(widget, CyberCard):
                visible = (text in widget.name.lower() or text in widget.path.lower() or text in widget.category.lower())
                widget.setVisible(visible)

    def on_card_clicked(self, dir_obj):
        # Update last_used
        dir_obj["last_used"] = time.time()
        save_data(self.data)
        
        # Show actions
        self.show_actions(dir_obj)
        
        # Refresh to update sort
        self.refresh_cards()

    def show_actions(self, dir_obj):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }}
            QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
        """)
        
        path = dir_obj.get("path")
        
        # Add commands from data
        for cmd in self.data.get("commands", []):
            action = QAction(cmd.get("name"), self)
            action.triggered.connect(lambda checked, t=cmd.get("template"), p=path: self.execute_command(t, p))
            menu.addAction(action)
            
        menu.exec(QCursor.pos())

    def execute_command(self, template, path):
        final_cmd = template.replace("{path}", path)
        try:
            subprocess.Popen(final_cmd, shell=True)
            self.status_bar.setText(f"EXECUTED: {final_cmd}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to execute command: {e}")

    def add_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            # Check if exists
            if any(d["path"] == path for d in self.data["directories"]):
                QMessageBox.warning(self, "Warning", "Directory already in launcher.")
                return
                
            name, ok = self.get_input("Directory Name", "Enter a display name (optional):")
            category, ok2 = self.get_input("Category", "Enter category (default 'General'):")
            if not category: category = "General"
            
            new_entry = {
                "path": path,
                "name": name,
                "category": category,
                "last_used": time.time()
            }
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
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(dialog.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return edit.text(), True
        return "", False

    def show_context_menu(self, pos, dir_obj):
        card = self.sender()
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }}
            QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
        """)
        
        edit_action = QAction("Edit", self)
        edit_action.triggered.connect(lambda: self.edit_directory(dir_obj))
        
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(lambda: self.remove_directory(dir_obj))
        
        menu.addAction(edit_action)
        menu.addAction(remove_action)
        menu.exec(card.mapToGlobal(pos))

    def edit_directory(self, dir_obj):
        name, ok = self.get_input("Edit Name", f"Current: {dir_obj.get('name')}")
        if ok:
            dir_obj["name"] = name
            save_data(self.data)
            self.refresh_cards()

    def remove_directory(self, dir_obj):
        reply = QMessageBox.question(self, "Remove", f"Remove '{dir_obj.get('name') or dir_obj.get('path')}'?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.data["directories"].remove(dir_obj)
            save_data(self.data)
            self.refresh_cards()

    def show_settings(self):
        # Setting button and setting panel as requested
        # By default keep it empty
        dialog = QDialog(self)
        dialog.setWindowTitle("SETTINGS")
        dialog.setMinimumSize(400, 300)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("--- SETTINGS PANEL ---"))
        layout.addWidget(QLabel("Configuration options will appear here."))
        layout.addStretch()
        
        close_btn = QPushButton("CLOSE")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Better base for custom styling
    window = CardLauncher()
    window.show()
    sys.exit(app.exec())
