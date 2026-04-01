import sys
import os
import json
import subprocess
import ctypes
import tempfile
from datetime import datetime

# --- PyQt6 Imports ---
try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPlainTextEdit, QLabel, QPushButton, QFileDialog, QDialog,
                                 QFormLayout, QLineEdit, QComboBox, QStatusBar, QMessageBox,
                                 QFrame, QSplitter, QTextEdit, QCheckBox)
    from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QTimer
    from PyQt6.QtGui import (QPainter, QTextFormat, QColor, QFont, QAction, QIcon,
                             QTextCursor, QKeySequence, QPalette, QTextDocument)
except ImportError:
    print("PyQt6 is required. Please install it using 'pip install PyQt6'")
    sys.exit(1)

# --- THEME CONSTANTS (From THEME_GUIDE.md) ---
CP_BG = "#050505"           # Main Background
CP_PANEL = "#111111"        # Input background
CP_YELLOW = "#FCEE0A"       # Accent Yellow
CP_CYAN = "#00F0FF"         # Accent Cyan
CP_RED = "#FF003C"          # Accent Red
CP_GREEN = "#00ff21"        # Accent Green
CP_DIM = "#3a3a3a"          # Borders/Dimmed text
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

THEMES = {
    "CyberYellow": {"accent": CP_YELLOW, "name": "Cyber Yellow"},
    "CyberCyan":   {"accent": CP_CYAN,   "name": "Cyber Cyan"},
    "CyberRed":    {"accent": CP_RED,    "name": "Cyber Red"}
}

DEFAULT_SHORTCUTS = {
    "MOVE_LINE_UP": "Alt+Up",
    "MOVE_LINE_DOWN": "Alt+Down",
    "DUPLICATE_LINE": "Ctrl+D",
    "DELETE_LINE": "Ctrl+Shift+K",
    "TOGGLE_SEARCH": "Ctrl+F",
    "SAVE_FILE": "Ctrl+S",
    "OPEN_FILE": "Ctrl+O",
    "RESTART_APP": "Ctrl+R"
}

# --- Settings Manager ---
class SettingsManager:
    def __init__(self):
        self.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor_settings.json")
        self.settings = {
            "width": 1000,
            "height": 700,
            "theme": "CyberYellow",
            "font_size": 10,
            "last_file": "",
            "shortcuts": DEFAULT_SHORTCUTS.copy()
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Deep merge for shortcuts
                    if "shortcuts" in data:
                        self.settings["shortcuts"].update(data["shortcuts"])
                        del data["shortcuts"]
                    self.settings.update(data)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

# --- UI Components ---

class CyberButton(QPushButton):
    """Premium Styled Button as per GUIDE"""
    def __init__(self, text, accent=CP_YELLOW, parent=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.apply_style()

    def set_accent(self, accent):
        self.accent = accent
        self.apply_style()

    def apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_DIM};
                font-family: 'Consolas';
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 0px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1a1a1a;
                border: 1px solid {self.accent};
                color: {self.accent};
            }}
            QPushButton:pressed {{
                background-color: {self.accent};
                color: black;
            }}
        """)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    """Enhanced Editor with Line Numbers, Highlighting and Shortcuts"""
    shortcut_triggered = pyqtSignal(str)

    def __init__(self, settings_mgr, accent=CP_YELLOW):
        super().__init__()
        self.mgr = settings_mgr
        self.accent = accent
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.set_accent(accent)
        self.update_line_number_area_width(0)
        self.highlight_current_line()

        self.setFont(QFont('Consolas', 10))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
    def set_accent(self, accent):
        self.accent = accent
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        return 15 + self.fontMetrics().horizontalAdvance('9') * digits

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(CP_PANEL))

        block = self.firstVisibleBlock()
        block_num = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_num + 1)
                is_current = (block_num == self.textCursor().blockNumber())
                painter.setPen(QColor(self.accent if is_current else CP_DIM))
                
                f = painter.font()
                f.setBold(is_current)
                painter.setFont(f)

                painter.drawText(0, int(top), self.line_number_area.width() - 5, 
                                 self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_num += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(self.accent)
            line_color.setAlpha(25)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)
        self.line_number_area.update()

    def keyPressEvent(self, event):
        # Correctly get key + modifiers for PyQt6
        try:
            # We explicitly handle the modifier to avoid int() issues with enums
            key = event.key()
            modifiers = event.modifiers()
            
            # Use QKeySequence to represent the combination
            # event.keyCombination() is the most robust if available
            try:
                key_combo = event.keyCombination()
                key_str = QKeySequence(key_combo).toString()
            except:
                # Manual decomposition if needed
                mod_val = 0
                if modifiers & Qt.KeyboardModifier.ControlModifier: mod_val |= Qt.Modifier.CTRL
                if modifiers & Qt.KeyboardModifier.ShiftModifier: mod_val |= Qt.Modifier.SHIFT
                if modifiers & Qt.KeyboardModifier.AltModifier: mod_val |= Qt.Modifier.ALT
                key_str = QKeySequence(key | mod_val).toString()
                
            shortcuts = self.mgr.settings["shortcuts"]
            
            if key_str == shortcuts.get("MOVE_LINE_UP"):
                self.move_line(-1)
                event.accept()
                return
            elif key_str == shortcuts.get("MOVE_LINE_DOWN"):
                self.move_line(1)
                event.accept()
                return
            elif key_str == shortcuts.get("DUPLICATE_LINE"):
                self.duplicate_line()
                event.accept()
                return
            elif key_str == shortcuts.get("DELETE_LINE"):
                self.delete_current_line()
                event.accept()
                return
            elif key_str == shortcuts.get("TOGGLE_SEARCH"):
                self.shortcut_triggered.emit("TOGGLE_SEARCH")
                event.accept()
                return
            elif key_str == shortcuts.get("SAVE_FILE"):
                self.shortcut_triggered.emit("SAVE_FILE")
                event.accept()
                return
            elif key_str == shortcuts.get("OPEN_FILE"):
                self.shortcut_triggered.emit("OPEN_FILE")
                event.accept()
                return
            elif key_str == shortcuts.get("RESTART_APP"):
                self.shortcut_triggered.emit("RESTART_APP")
                event.accept()
                return
        except Exception as e:
            print(f"Key event error: {e}")

        super().keyPressEvent(event)

    def move_line(self, direction):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        
        # Select current line
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        
        # Delete line
        cursor.removeSelectedText()
        cursor.deleteChar() # Remove the newline if it's there
        
        if direction == -1: # Up
            if cursor.movePosition(QTextCursor.MoveOperation.Up):
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                cursor.insertText(line_text + "\n")
                cursor.movePosition(QTextCursor.MoveOperation.Up)
            else:
                # Top of file, put it back
                cursor.insertText(line_text + "\n")
                cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        else: # Down
            if cursor.movePosition(QTextCursor.MoveOperation.Down):
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                cursor.insertText("\n" + line_text)
            else:
                # Bottom of file, put it back
                cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
                cursor.insertText("\n" + line_text)
                
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def duplicate_line(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText()
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        cursor.insertText("\n" + line_text)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def delete_current_line(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        self.setTextCursor(cursor)

# --- Dialogs ---

class SettingsDialog(QDialog):
    def __init__(self, parent, mgr):
        super().__init__(parent)
        self.mgr = mgr
        self.setWindowTitle("SYSTEM_SETTINGS")
        self.setModal(True)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        self.w_edit = QLineEdit(str(self.mgr.settings.get("width", 1000)))
        self.h_edit = QLineEdit(str(self.mgr.settings.get("height", 700)))
        
        self.theme_sel = QComboBox()
        for t_id, t_info in THEMES.items():
            self.theme_sel.addItem(t_info["name"], t_id)
        
        idx = self.theme_sel.findData(self.mgr.settings.get("theme", "CyberYellow"))
        self.theme_sel.setCurrentIndex(max(0, idx))
        
        form.addRow("UI_WIDTH:", self.w_edit)
        form.addRow("UI_HEIGHT:", self.h_edit)
        form.addRow("COLOR_THEME:", self.theme_sel)
        
        layout.addLayout(form)
        
        self.more_box = QFrame()
        self.more_box.setFrameShape(QFrame.Shape.StyledPanel)
        more_layout = QVBoxLayout(self.more_box)
        more_layout.addWidget(QLabel("// Reserved for future modules..."))
        layout.addWidget(self.more_box)

        btns = QHBoxLayout()
        theme_accent = THEMES.get(self.mgr.settings.get("theme", "CyberYellow"), THEMES["CyberYellow"])["accent"]
        self.save_btn = CyberButton("APPLY & SAVE", accent=theme_accent)
        self.save_btn.clicked.connect(self.do_save)
        self.cancel_btn = CyberButton("ABORT", accent=CP_RED)
        self.cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(self.save_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

    def apply_theme(self):
        accent = THEMES.get(self.mgr.settings.get("theme", "CyberYellow"), THEMES["CyberYellow"])["accent"]
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 2px solid {accent}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; text-transform: uppercase; }}
            QLineEdit, QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px;
                font-family: 'Consolas'; font-size: 11pt;
            }}
            QLineEdit:focus {{ border: 1px solid {accent}; }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL}; color: {CP_TEXT}; selection-background-color: {accent}; selection-color: black;
            }}
            QFrame {{ border: 1px dashed {CP_DIM}; margin: 10px 0; }}
        """)

    def do_save(self):
        try:
            self.mgr.settings["width"] = int(self.w_edit.text())
            self.mgr.settings["height"] = int(self.h_edit.text())
            self.mgr.settings["theme"] = self.theme_sel.currentData()
            self.mgr.save()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "SYSTEM_ERR", f"INVALID INPUT: {e}")

class KeybindDialog(QDialog):
    def __init__(self, parent, mgr):
        super().__init__(parent)
        self.mgr = mgr
        self.setWindowTitle("KEYBIND_CONFIG")
        self.setModal(True)
        self.edits = {}
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        shortcuts = self.mgr.settings["shortcuts"]
        for action, key in shortcuts.items():
            le = QLineEdit(key)
            le.setPlaceholderText("e.g., Ctrl+S")
            self.edits[action] = le
            form.addRow(f"{action}:", le)
            
        layout.addLayout(form)
        
        instr = QLabel("TYPE KEY COMBINATIONS (e.g. Ctrl+Shift+S)\nSAVE TO APPLY CHANGES.")
        instr.setStyleSheet("color: #808080; font-size: 8pt;")
        layout.addWidget(instr)

        btns = QHBoxLayout()
        save_btn = CyberButton("APPLY", accent=THEMES[self.mgr.settings["theme"]]["accent"])
        save_btn.clicked.connect(self.do_save)
        cancel_btn = CyberButton("ABORT", accent=CP_RED)
        cancel_btn.clicked.connect(self.reject)
        
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def apply_theme(self):
        accent = THEMES[self.mgr.settings["theme"]]["accent"]
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 2px solid {accent}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; }}
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
                font-family: 'Consolas';
            }}
            QLineEdit:focus {{ border: 1px solid {accent}; }}
        """)

    def do_save(self):
        for action, le in self.edits.items():
            self.mgr.settings["shortcuts"][action] = le.text()
        self.mgr.save()
        self.accept()

# --- Search Panel ---

class SearchPanel(QFrame):
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Search Row
        row1 = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("SEARCH_QUERY...")
        
        self.btn_next = QPushButton("NEXT")
        self.btn_prev = QPushButton("PREV")
        self.btn_close = QPushButton("X")
        self.btn_close.setFixedWidth(30)
        
        row1.addWidget(QLabel("FIND:"))
        row1.addWidget(self.search_input)
        row1.addWidget(self.btn_prev)
        row1.addWidget(self.btn_next)
        row1.addWidget(self.btn_close)
        
        # Replace Row
        row2 = QHBoxLayout()
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("REPLACE_WITH...")
        
        self.btn_replace = QPushButton("REPLACE")
        self.btn_replace_all = QPushButton("ALL")
        
        row2.addWidget(QLabel("REPL:"))
        row2.addWidget(self.replace_input)
        row2.addWidget(self.btn_replace)
        row2.addWidget(self.btn_replace_all)
        row2.addStretch()
        
        layout.addLayout(row1)
        layout.addLayout(row2)

    def apply_theme(self, accent):
        self.setStyleSheet(f"""
            SearchPanel {{
                background-color: {CP_PANEL};
                border: 1px solid {accent};
                border-radius: 4px;
            }}
            QLineEdit {{
                background-color: #0c0c0c; color: {CP_CYAN}; border: 1px solid {CP_DIM};
                font-family: 'Consolas'; padding: 2px;
            }}
            QPushButton {{
                background-color: {CP_DIM}; color: white; border: none; padding: 2px 8px;
                font-family: 'Consolas'; font-size: 9pt;
            }}
            QPushButton:hover {{ background-color: {accent}; color: black; }}
            QLabel {{ color: {accent}; font-weight: bold; font-family: 'Consolas'; }}
        """)

# --- Main Window ---

class MainWindow(QMainWindow):
    def __init__(self, initial_file=None, buffer_file=None):
        super().__init__()
        self.mgr = SettingsManager()
        self.current_file = initial_file
        self.is_admin = self.check_admin()
        
        self.setup_ui()
        self.apply_theme_global()
        
        if initial_file:
            self.load_file(initial_file)
            if buffer_file and os.path.exists(buffer_file):
                try:
                    with open(buffer_file, 'r', encoding='utf-8') as f:
                        self.editor.setPlainText(f.read())
                    os.remove(buffer_file)
                except: pass

    def check_admin(self):
        try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except: return False

    def setup_ui(self):
        self.setWindowTitle(f"CYBER_EDITOR // {'[SUPERUSER]' if self.is_admin else '[USER]'}")
        self.resize(self.mgr.settings.get("width", 1000), self.mgr.settings.get("height", 700))
        
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Nav Bar
        self.nav_layout = QHBoxLayout()
        self.btn_open = CyberButton("OPEN_FILE")
        self.btn_save = CyberButton("SAVE_CACHE")
        self.btn_restart = CyberButton("RELOAD_APP")
        self.btn_keybinds = CyberButton("KEYBINDS")
        self.btn_settings = CyberButton("SYSTEM_CFG")
        
        self.btn_open.clicked.connect(self.on_open)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_restart.clicked.connect(self.on_restart)
        self.btn_keybinds.clicked.connect(self.on_keybinds)
        self.btn_settings.clicked.connect(self.on_settings)
        
        self.nav_layout.addWidget(self.btn_open)
        self.nav_layout.addWidget(self.btn_save)
        self.nav_layout.addStretch()
        
        if not self.is_admin:
            self.btn_elevate = CyberButton("ELEVATE", accent=CP_RED)
            self.btn_elevate.clicked.connect(self.on_elevate)
            self.nav_layout.addWidget(self.btn_elevate)
            
        self.nav_layout.addWidget(self.btn_keybinds)
        self.nav_layout.addWidget(self.btn_restart)
        self.nav_layout.addWidget(self.btn_settings)
        
        self.main_layout.addLayout(self.nav_layout)
        
        # Search Panel (Overlay-ish)
        self.search_panel = SearchPanel(self)
        self.search_panel.btn_close.clicked.connect(lambda: self.toggle_search(False))
        self.search_panel.btn_next.clicked.connect(self.search_next)
        self.search_panel.btn_prev.clicked.connect(self.search_prev)
        self.search_panel.btn_replace.clicked.connect(self.do_replace)
        self.search_panel.btn_replace_all.clicked.connect(self.do_replace_all)
        self.search_panel.search_input.textChanged.connect(self.search_next)
        
        self.main_layout.addWidget(self.search_panel)
        
        # Editor
        self.editor = CodeEditor(self.mgr)
        self.editor.shortcut_triggered.connect(self.handle_shortcut)
        self.main_layout.addWidget(self.editor)
        
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("SYSTEM READY...")

    def apply_theme_global(self):
        theme_key = self.mgr.settings.get("theme", "CyberYellow")
        accent = THEMES[theme_key]["accent"]
        
        self.editor.set_accent(accent)
        self.search_panel.apply_theme(accent)
        
        btns = [self.btn_open, self.btn_save, self.btn_restart, self.btn_keybinds, self.btn_settings]
        for b in btns: b.set_accent(accent)
        if not self.is_admin: self.btn_elevate.set_accent(CP_RED)

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QPlainTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 8px;
                selection-background-color: {accent}; selection-color: black;
                font-family: 'Consolas'; font-size: 11pt;
            }}
            QPlainTextEdit:focus {{
                border: 1px solid {accent};
            }}
            QStatusBar {{ background: {CP_PANEL}; color: {CP_SUBTEXT}; border-top: 1px solid {CP_DIM}; }}
        """)

    def handle_shortcut(self, action):
        if action == "TOGGLE_SEARCH":
            self.toggle_search()
        elif action == "SAVE_FILE":
            self.on_save()
        elif action == "OPEN_FILE":
            self.on_open()
        elif action == "RESTART_APP":
            self.on_restart()

    def toggle_search(self, force=None):
        visible = not self.search_panel.isVisible() if force is None else force
        self.search_panel.setVisible(visible)
        if visible:
            self.search_panel.search_input.setFocus()
            self.search_panel.search_input.selectAll()

    def search_next(self):
        query = self.search_panel.search_input.text()
        if not query: return
        if not self.editor.find(query):
            # Wrap around
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.editor.setTextCursor(cursor)
            self.editor.find(query)

    def search_prev(self):
        query = self.search_panel.search_input.text()
        if not query: return
        if not self.editor.find(query, QTextDocument.FindFlag.FindBackward):
            cursor = self.editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.editor.setTextCursor(cursor)
            self.editor.find(query, QTextDocument.FindFlag.FindBackward)

    def do_replace(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.search_panel.replace_input.text())
            self.search_next()

    def do_replace_all(self):
        query = self.search_panel.search_input.text()
        repl = self.search_panel.replace_input.text()
        if not query: return
        
        text = self.editor.toPlainText()
        new_text = text.replace(query, repl)
        self.editor.setPlainText(new_text)

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "OPEN_FILE", "", "All Files (*)")
        if path: self.load_file(path)

    def load_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.current_file = path
            self.setWindowTitle(f"CYBER_EDITOR // {os.path.basename(path)}")
            self.statusBar().showMessage(f"LOADED: {path}")
        except Exception as e:
            QMessageBox.critical(self, "ERR", str(e))

    def on_save(self):
        if not self.current_file:
            path, _ = QFileDialog.getSaveFileName(self, "SAVE_FILE", "", "All Files (*)")
            if not path: return
            self.current_file = path
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.statusBar().showMessage(f"SAVED: {self.current_file}")
        except Exception as e:
            QMessageBox.warning(self, "ERR", f"PERMISSION DENIED? {e}")

    def on_restart(self):
        QApplication.quit()
        subprocess.Popen([sys.executable] + sys.argv)

    def on_keybinds(self):
        dlg = KeybindDialog(self, self.mgr)
        if dlg.exec():
            self.statusBar().showMessage("KEYBINDS UPDATED.")

    def on_settings(self):
        dlg = SettingsDialog(self, self.mgr)
        if dlg.exec():
            self.apply_theme_global()
            self.resize(self.mgr.settings["width"], self.mgr.settings["height"])

    def on_elevate(self):
        buf_path = os.path.join(tempfile.gettempdir(), "cyber_edit_lock.tmp")
        try:
            with open(buf_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            script = os.path.abspath(sys.argv[0])
            params = f'"{script}" --buffer "{buf_path}"'
            if self.current_file: params += f' --file "{self.current_file}"'
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            if ret > 32: QApplication.quit()
        except Exception as e:
            QMessageBox.critical(self, "ERR", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Simple Arg Parsing
    initial_file = None
    buffer_file = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--file" and i + 1 < len(args):
            initial_file = args[i+1]; i += 2
        elif args[i] == "--buffer" and i + 1 < len(args):
            buffer_file = args[i+1]; i += 2
        else:
            if not initial_file: initial_file = args[i]
            i += 1

    window = MainWindow(initial_file, buffer_file)
    window.show()
    sys.exit(app.exec())
