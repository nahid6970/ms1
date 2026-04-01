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
                                 QFrame, QSplitter, QTextEdit, QCheckBox, QColorDialog, QTabWidget, QTabBar)
    from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QTimer, QPoint
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
    "RESTART_APP": "Ctrl+R",
    "CLOSE_TAB": "Ctrl+W"
}

# --- Settings Manager ---
class SettingsManager:
    def __init__(self):
        self.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "editor_settings.json")
        self.settings = {
            "width": 1000,
            "height": 700,
            "theme": "CyberYellow",
            "font_family": "Consolas",
            "font_size": 10,
            "cursor_line_color": "",
            "cursor_color": "",
            "open_files": [],
            "current_tab_index": 0,
            "shortcuts": DEFAULT_SHORTCUTS.copy()
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    if "shortcuts" in data:
                        self.settings["shortcuts"].update(data["shortcuts"])
                        del data["shortcuts"]
                    self.settings.update(data)
            except Exception as e: print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(self.filename, 'w') as f: json.dump(self.settings, f, indent=4)
        except Exception as e: print(f"Error saving settings: {e}")

# --- UI Components ---

class CyberButton(QPushButton):
    def __init__(self, text, accent=CP_YELLOW, parent=None):
        super().__init__(text, parent)
        self.accent = accent; self.setCursor(Qt.CursorShape.PointingHandCursor); self.apply_style()
    def set_accent(self, accent):
        self.accent = accent; self.apply_style()
    def apply_style(self):
        self.setStyleSheet(f"QPushButton {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; font-family: 'Consolas'; font-weight: bold; padding: 6px 12px; border-radius: 0px; }} QPushButton:hover {{ background-color: #1a1a1a; border: 1px solid {self.accent}; color: {self.accent}; }} QPushButton:pressed {{ background-color: {self.accent}; color: black; }}")

class LineNumberArea(QWidget):
    def __init__(self, editor): super().__init__(editor); self.editor = editor
    def sizeHint(self): return QSize(self.editor.line_number_area_width(), 0)
    def paintEvent(self, event): self.editor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    shortcut_triggered = pyqtSignal(str)
    def __init__(self, settings_mgr, accent=CP_YELLOW, file_path=None):
        super().__init__()
        self.mgr = settings_mgr; self.accent = accent; self.file_path = file_path
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.setObjectName("CyberEditorCore")
        self.apply_font() # Load from settings
        self.set_accent(accent); self.update_line_number_area_width(0); self.highlight_current_line()
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap); self.setAcceptDrops(True)
        self.setCursorWidth(0) # Using custom paintEvent caret

    def set_accent(self, accent):
        self.accent = accent; self.highlight_current_line(); self.apply_cursor_color()

    def apply_font(self):
        family = self.mgr.settings.get("font_family", "Consolas")
        size = self.mgr.settings.get("font_size", 10)
        self.setFont(QFont(family, size))

    def apply_cursor_color(self):
        accent_color = THEMES.get(self.mgr.settings.get("theme", "CyberYellow"), THEMES["CyberYellow"])["accent"]
        self.setStyleSheet(f"background-color: {CP_PANEL}; color: {CP_CYAN}; border: none; padding: 8px; selection-background-color: {accent_color}; selection-color: black; font-family: 'Consolas'; font-size: 11pt;")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: super().dragEnterEvent(event)
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: super().dragMoveEvent(event)
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                path = urls[0].toLocalFile()
                if os.path.isfile(path): self.shortcut_triggered.emit(f"LOAD_FILE:{path}")
            event.accept()
        else: super().dropEvent(event)

    def line_number_area_width(self):
        digits, max_num = 1, max(1, self.blockCount())
        while max_num >= 10: max_num //= 10; digits += 1
        return 15 + self.fontMetrics().horizontalAdvance('9') * digits
    def update_line_number_area_width(self, _): self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    def update_line_number_area(self, rect, dy):
        if dy: self.line_number_area.scroll(0, dy)
        else: self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()): self.update_line_number_area_width(0)
    def resizeEvent(self, event):
        super().resizeEvent(event); cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.line_number_area); painter.fillRect(event.rect(), QColor(CP_PANEL))
        block = self.firstVisibleBlock(); block_num = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_num + 1); is_current = (block_num == self.textCursor().blockNumber())
                painter.setPen(QColor(self.accent if is_current else CP_DIM)); f = painter.font(); f.setBold(is_current); painter.setFont(f)
                painter.drawText(0, int(top), self.line_number_area.width() - 5, self.fontMetrics().height(), Qt.AlignmentFlag.AlignRight, number)
            block = block.next(); top = bottom; bottom = top + self.blockBoundingRect(block).height(); block_num += 1

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            custom_hex = self.mgr.settings.get("cursor_line_color", "")
            if custom_hex:
                line_color = QColor(custom_hex)
                if line_color.alpha() == 255: line_color.setAlpha(40)
            else:
                line_color = QColor(self.accent); line_color.setAlpha(25)
            selection.format.setBackground(line_color); selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor(); selection.cursor.clearSelection(); extra_selections.append(selection)
        self.setExtraSelections(extra_selections); self.line_number_area.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.hasFocus() or self.isReadOnly(): return
        if not hasattr(self, '_blink_state'):
            self._blink_state = True; self._blink_timer = QTimer(self); self._blink_timer.timeout.connect(self._toggle_blink); self._blink_timer.start(500)
        if self._blink_state:
            painter = QPainter(self.viewport()); cursor_color = self.mgr.settings.get("cursor_color", "")
            rect = self.cursorRect(); painter.fillRect(rect.left(), rect.top(), 2, rect.height(), QColor(cursor_color if cursor_color else CP_CYAN)); painter.end()
    def _toggle_blink(self): self._blink_state = not self._blink_state; self.viewport().update()

    def keyPressEvent(self, event):
        try: key_str = QKeySequence(event.keyCombination()).toString()
        except:
            mod_val = 0
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier: mod_val |= Qt.Modifier.CTRL
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier: mod_val |= Qt.Modifier.SHIFT
            if event.modifiers() & Qt.KeyboardModifier.AltModifier: mod_val |= Qt.Modifier.ALT
            key_str = QKeySequence(event.key() | mod_val).toString()
        shortcuts = self.mgr.settings["shortcuts"]
        if key_str == shortcuts.get("MOVE_LINE_UP"): self.move_line(-1); event.accept(); return
        elif key_str == shortcuts.get("MOVE_LINE_DOWN"): self.move_line(1); event.accept(); return
        elif key_str == shortcuts.get("DUPLICATE_LINE"): self.duplicate_line(); event.accept(); return
        elif key_str == shortcuts.get("DELETE_LINE"): self.delete_current_line(); event.accept(); return
        elif key_str == shortcuts.get("TOGGLE_SEARCH"): self.shortcut_triggered.emit("TOGGLE_SEARCH"); event.accept(); return
        elif key_str == shortcuts.get("SAVE_FILE"): self.shortcut_triggered.emit("SAVE_FILE"); event.accept(); return
        elif key_str == shortcuts.get("OPEN_FILE"): self.shortcut_triggered.emit("OPEN_FILE"); event.accept(); return
        elif key_str == shortcuts.get("RESTART_APP"): self.shortcut_triggered.emit("RESTART_APP"); event.accept(); return
        elif key_str == shortcuts.get("CLOSE_TAB"): self.shortcut_triggered.emit("CLOSE_TAB"); event.accept(); return
        super().keyPressEvent(event)

    def move_line(self, direction):
        cursor = self.textCursor(); cursor.beginEditBlock(); cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor); line_text = cursor.selectedText(); cursor.removeSelectedText(); cursor.deleteChar()
        if direction == -1:
            if cursor.movePosition(QTextCursor.MoveOperation.Up): cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock); cursor.insertText(line_text + "\n"); cursor.movePosition(QTextCursor.MoveOperation.Up)
            else: cursor.insertText(line_text + "\n"); cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        else:
            if cursor.movePosition(QTextCursor.MoveOperation.Down): cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock); cursor.insertText("\n" + line_text)
            else: cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock); cursor.insertText("\n" + line_text)
        cursor.endEditBlock(); self.setTextCursor(cursor)
    def duplicate_line(self):
        cursor = self.textCursor(); cursor.beginEditBlock(); cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock); cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        line_text = cursor.selectedText(); cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock); cursor.insertText("\n" + line_text); cursor.endEditBlock(); self.setTextCursor(cursor)
    def delete_current_line(self):
        cursor = self.textCursor(); cursor.select(QTextCursor.SelectionType.BlockUnderCursor); cursor.removeSelectedText(); self.setTextCursor(cursor)

# --- Dialogs ---

class SettingsDialog(QDialog):
    def __init__(self, parent, mgr):
        super().__init__(parent); self.mgr = mgr; self.setWindowTitle("SYSTEM_SETTINGS"); self.setModal(True)
        self.temp_cursor_line_color = self.mgr.settings.get("cursor_line_color", ""); self.temp_cursor_color = self.mgr.settings.get("cursor_color", ""); self.setup_ui(); self.apply_theme()
    def setup_ui(self):
        self.setMinimumWidth(450); layout = QVBoxLayout(self); form = QFormLayout()
        self.w_edit = QLineEdit(str(self.mgr.settings.get("width", 1000))); self.h_edit = QLineEdit(str(self.mgr.settings.get("height", 700)))
        
        self.font_sel = QComboBox()
        from PyQt6.QtGui import QFontDatabase
        all_fonts = sorted(QFontDatabase.families())
        self.font_sel.addItems(all_fonts)
        curr_fam = self.mgr.settings.get("font_family", "Consolas")
        idx = self.font_sel.findText(curr_fam)
        self.font_sel.setCurrentIndex(max(0, idx))
        
        self.size_edit = QLineEdit(str(self.mgr.settings.get("font_size", 10)))
        
        self.theme_sel = QComboBox(); [self.theme_sel.addItem(t_info["name"], t_id) for t_id, t_info in THEMES.items()]
        self.theme_sel.setCurrentIndex(max(0, self.theme_sel.findData(self.mgr.settings.get("theme", "CyberYellow"))))
        
        self.line_color_btn = QPushButton("PICK_HL_COLOR"); self.line_color_btn.clicked.connect(self.pick_line_color)
        self.cur_line_label = QLabel(self.temp_cursor_line_color if self.temp_cursor_line_color else "AUTO")
        self.cursor_color_btn = QPushButton("PICK_INSERT_COLOR"); self.cursor_color_btn.clicked.connect(self.pick_cursor_color)
        self.cur_cursor_label = QLabel(self.temp_cursor_color if self.temp_cursor_color else "AUTO")
        
        form.addRow("UI_WIDTH:", self.w_edit); form.addRow("UI_HEIGHT:", self.h_edit)
        form.addRow("FONT_FAM:", self.font_sel); form.addRow("FONT_SIZE:", self.size_edit)
        form.addRow("COLOR_THEME:", self.theme_sel)
        form.addRow("LINE_HL:", self.line_color_btn); form.addRow("VAL:", self.cur_line_label); form.addRow("CURSOR_COLOR:", self.cursor_color_btn); form.addRow("VAL:", self.cur_cursor_label)
        layout.addLayout(form); self.more_box = QFrame(); self.more_box.setFrameShape(QFrame.Shape.StyledPanel); more_layout = QVBoxLayout(self.more_box); more_layout.addWidget(QLabel("// Future modules reserved...")); layout.addWidget(self.more_box)
        btns = QHBoxLayout(); theme_accent = THEMES.get(self.mgr.settings.get("theme", "CyberYellow"), THEMES["CyberYellow"])["accent"]
        self.save_btn = CyberButton("APPLY & SAVE", accent=theme_accent); self.save_btn.clicked.connect(self.do_save)
        self.cancel_btn = CyberButton("ABORT", accent=CP_RED); self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.save_btn); btns.addWidget(self.cancel_btn); layout.addLayout(btns)
    def pick_line_color(self):
        cur = QColor(self.temp_cursor_line_color) if self.temp_cursor_line_color else QColor(CP_CYAN)
        color = QColorDialog.getColor(cur, self, "SELECT_LINE_HL_COLOR", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid(): self.temp_cursor_line_color = color.name(QColor.NameFormat.HexArgb); self.cur_line_label.setText(self.temp_cursor_line_color); self.cur_line_label.setStyleSheet(f"color: {color.name()};")
    def pick_cursor_color(self):
        cur = QColor(self.temp_cursor_color) if self.temp_cursor_color else QColor(CP_CYAN)
        color = QColorDialog.getColor(cur, self, "SELECT_INSERTION_MARKER_COLOR")
        if color.isValid(): self.temp_cursor_color = color.name(); self.cur_cursor_label.setText(self.temp_cursor_color); self.cur_cursor_label.setStyleSheet(f"color: {self.temp_cursor_color};")
    def apply_theme(self):
        accent = THEMES.get(self.mgr.settings.get("theme", "CyberYellow"), THEMES["CyberYellow"])["accent"]
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 2px solid {accent}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; text-transform: uppercase; }}
            QLineEdit, QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px; font-family: 'Consolas'; }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {accent}; }}
            
            QPushButton {{ background-color: {CP_DIM}; color: white; border: 1px solid {CP_DIM}; padding: 4px; font-family: 'Consolas'; }}
            QPushButton:hover {{ border: 1px solid {accent}; color: {accent}; }}
            QFrame {{ border: 1px dashed {CP_DIM}; margin: 10px 0; }}
        """)
    def do_save(self):
        try:
            self.mgr.settings["width"] = int(self.w_edit.text()); self.mgr.settings["height"] = int(self.h_edit.text())
            self.mgr.settings["font_family"] = self.font_sel.currentText()
            self.mgr.settings["font_size"] = int(self.size_edit.text())
            self.mgr.settings["theme"] = self.theme_sel.currentData()
            self.mgr.settings["cursor_line_color"] = self.temp_cursor_line_color; self.mgr.settings["cursor_color"] = self.temp_cursor_color; self.mgr.save(); self.accept()
        except Exception as e: QMessageBox.critical(self, "SYSTEM_ERR", f"INVALID: {e}")

class KeybindDialog(QDialog):
    def __init__(self, parent, mgr):
        super().__init__(parent); self.mgr = mgr; self.setWindowTitle("KEYBIND_CONFIG"); self.setModal(True); self.edits = {}; self.setup_ui(); self.apply_theme()
    def setup_ui(self):
        layout = QVBoxLayout(self); form = QFormLayout()
        for action, key in self.mgr.settings["shortcuts"].items():
            le = QLineEdit(key); self.edits[action] = le; form.addRow(f"{action}:", le)
        layout.addLayout(form); btns = QHBoxLayout(); save_btn = CyberButton("APPLY", accent=THEMES[self.mgr.settings["theme"]]["accent"]); save_btn.clicked.connect(self.do_save)
        cancel_btn = CyberButton("ABORT", accent=CP_RED); cancel_btn.clicked.connect(self.reject); btns.addWidget(save_btn); btns.addWidget(cancel_btn); layout.addLayout(btns)
    def apply_theme(self):
        accent = THEMES[self.mgr.settings["theme"]]["accent"]
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {accent}; }} QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; }} QLineEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; font-family: 'Consolas'; }} QLineEdit:focus {{ border: 1px solid {accent}; }}")
    def do_save(self):
        for action, le in self.edits.items(): self.mgr.settings["shortcuts"][action] = le.text()
        self.mgr.save(); self.accept()

# --- Search Panel ---

class SearchPanel(QFrame):
    def __init__(self, parent=None): super().__init__(parent); self.setVisible(False); self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(5, 5, 5, 5)
        row1 = QHBoxLayout(); self.search_input = QLineEdit(); self.btn_next = QPushButton("NEXT"); self.btn_prev = QPushButton("PREV"); self.btn_close = QPushButton("X"); self.btn_close.setFixedWidth(30)
        row1.addWidget(QLabel("FIND:")); row1.addWidget(self.search_input); row1.addWidget(self.btn_prev); row1.addWidget(self.btn_next); row1.addWidget(self.btn_close)
        row2 = QHBoxLayout(); self.replace_input = QLineEdit(); self.btn_replace = QPushButton("REPL"); self.btn_replace_all = QPushButton("ALL")
        row2.addWidget(QLabel("REPL:")); row2.addWidget(self.replace_input); row2.addWidget(self.btn_replace); row2.addWidget(self.btn_replace_all); row2.addStretch(); layout.addLayout(row1); layout.addLayout(row2)
    def apply_theme(self, accent):
        self.setStyleSheet(f"SearchPanel {{ background-color: {CP_PANEL}; border: 1px solid {accent}; border-radius: 4px; }} QLineEdit {{ background-color: #0c0c0c; color: {CP_CYAN}; border: 1px solid {CP_DIM}; font-family: 'Consolas'; padding: 2px; }} QPushButton {{ background-color: {CP_DIM}; color: white; border: none; padding: 2px 8px; font-family: 'Consolas'; font-size: 9pt; }} QPushButton:hover {{ background-color: {accent}; color: black; }} QLabel {{ color: {accent}; font-weight: bold; font-family: 'Consolas'; }}")

# --- Main Window ---

class MainWindow(QMainWindow):
    def __init__(self, initial_file=None, buffer_file=None):
        super().__init__(); self.mgr = SettingsManager(); self.is_admin = self.check_admin(); self.setup_ui(); self.apply_theme_global()
        self.restore_session(initial_file, buffer_file)

    def check_admin(self):
        try: return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except: return False

    def setup_ui(self):
        self.setWindowTitle(f"CYBER_EDITOR // {'[SUPERUSER]' if self.is_admin else '[USER]'}")
        self.resize(self.mgr.settings.get("width", 1000), self.mgr.settings.get("height", 700))
        central = QWidget(); self.setCentralWidget(central); self.main_layout = QVBoxLayout(central); self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.nav_layout = QHBoxLayout()
        self.btn_open = CyberButton("OPEN_FILE"); self.btn_save = CyberButton("SAVE"); self.btn_restart = CyberButton("RELOAD"); self.btn_keybinds = CyberButton("KEYS"); self.btn_settings = CyberButton("CFG")
        self.btn_open.clicked.connect(self.on_open); self.btn_save.clicked.connect(self.on_save); self.btn_restart.clicked.connect(self.on_restart); self.btn_keybinds.clicked.connect(self.on_keybinds); self.btn_settings.clicked.connect(self.on_settings)
        self.nav_layout.addWidget(self.btn_open); self.nav_layout.addWidget(self.btn_save); self.nav_layout.addStretch()
        if not self.is_admin: self.btn_elevate = CyberButton("ELEVATE", accent=CP_RED); self.btn_elevate.clicked.connect(self.on_elevate); self.nav_layout.addWidget(self.btn_elevate)
        self.nav_layout.addWidget(self.btn_keybinds); self.nav_layout.addWidget(self.btn_restart); self.nav_layout.addWidget(self.btn_settings); self.main_layout.addLayout(self.nav_layout)
        
        self.search_panel = SearchPanel(self); self.search_panel.btn_close.clicked.connect(lambda: self.toggle_search(False))
        self.search_panel.btn_next.clicked.connect(self.search_next); self.search_panel.btn_prev.clicked.connect(self.search_prev)
        self.search_panel.btn_replace.clicked.connect(self.do_replace); self.search_panel.btn_replace_all.clicked.connect(self.do_replace_all)
        self.search_panel.search_input.textChanged.connect(self.search_next); self.main_layout.addWidget(self.search_panel)
        
        # Tab Widget
        self.tabs = QTabWidget(); self.tabs.setTabsClosable(True); self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.main_layout.addWidget(self.tabs)
        
        self.setStatusBar(QStatusBar()); self.statusBar().showMessage("SYSTEM READY...")

    def apply_theme_global(self):
        theme_key = self.mgr.settings.get("theme", "CyberYellow"); accent = THEMES[theme_key]["accent"]
        self.search_panel.apply_theme(accent)
        for b in [self.btn_open, self.btn_save, self.btn_restart, self.btn_keybinds, self.btn_settings]: b.set_accent(accent)
        if not self.is_admin: self.btn_elevate.set_accent(CP_RED)
        
        # Style Tabs & Scrollbars
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {CP_DIM}; background: {CP_BG}; top: -1px; }}
            QTabBar::tab {{
                background: {CP_PANEL}; color: {CP_SUBTEXT}; border: 1px solid {CP_DIM};
                border-bottom: none; padding: 6px 8px 6px 15px; margin-right: 2px;
                font-family: 'Consolas'; font-weight: bold;
            }}
            QTabBar::tab:selected {{ background: {CP_BG}; color: {accent}; border-top: 2px solid {accent}; }}
            QTabBar::tab:hover {{ background: #1a1a1a; color: {accent}; }}
            
            QTabBar::close-button {{
                image: none;
                width: 0px; height: 0px; /* Hide the native one completely */
            }}

            QScrollBar:vertical {{
                background: {CP_BG}; width: 12px; margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM}; min-height: 20px; border: 1px solid {CP_PANEL};
            }}
            QScrollBar::handle:vertical:hover {{ background: {accent}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none; height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background: {CP_BG}; height: 12px; margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {CP_DIM}; min-width: 20px; border: 1px solid {CP_PANEL};
            }}
            QScrollBar::handle:horizontal:hover {{ background: {accent}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal, QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none; width: 0px;
            }}
        """)
        
        # Update each open editor
        for i in range(self.tabs.count()):
            editor = self.tabs.widget(i)
            if isinstance(editor, CodeEditor):
                editor.set_accent(accent)
                editor.apply_font()

        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }} QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }} QStatusBar {{ background: {CP_PANEL}; color: {CP_SUBTEXT}; border-top: 1px solid {CP_DIM}; }}")

    def restore_session(self, initial_file, buffer_file):
        # Open saved files
        files = self.mgr.settings.get("open_files", [])
        if not files and not initial_file:
            self.add_new_tab() # Blank tab if nothing
        else:
            for f_path in files:
                if os.path.exists(f_path): self.add_new_tab(f_path)
            if initial_file: self.add_new_tab(initial_file)
        
        # Handle Buffer
        if buffer_file and os.path.exists(buffer_file):
            try:
                with open(buffer_file, 'r', encoding='utf-8') as f:
                    editor = self.current_editor()
                    if editor: editor.setPlainText(f.read())
                os.remove(buffer_file)
            except: pass
        
        # Restore index
        idx = self.mgr.settings.get("current_tab_index", 0)
        self.tabs.setCurrentIndex(min(max(0, idx), self.tabs.count()-1))

    def current_editor(self):
        return self.tabs.currentWidget()

    def add_new_tab(self, path=None):
        for i in range(self.tabs.count()):
            if self.tabs.widget(i).file_path == path and path is not None:
                self.tabs.setCurrentIndex(i); return
        
        theme_key = self.mgr.settings.get("theme", "CyberYellow")
        accent = THEMES[theme_key]["accent"]
        editor = CodeEditor(self.mgr, accent, path)
        editor.shortcut_triggered.connect(self.handle_shortcut)
        
        name = os.path.basename(path) if path else "UNTITLED.txt"
        idx = self.tabs.addTab(editor, name)
        
        # Proper Close Button X - Integrated Look (1-char gap)
        close_btn = QPushButton("x")
        close_btn.setFixedSize(14, 14)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{ 
                background: none; color: {CP_SUBTEXT}; border: none; 
                font-size: 11px; font-weight: bold; font-family: 'Arial';
                padding: 0px; margin-left: 5px; /* Exactly 1 space gap */
            }}
            QPushButton:hover {{ color: {CP_RED}; }}
        """)
        close_btn.clicked.connect(lambda: self.close_tab(self.tabs.indexOf(editor)))
        self.tabs.tabBar().setTabButton(idx, QTabBar.ButtonPosition.RightSide, close_btn)

        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f: editor.setPlainText(f.read())
            except: pass
        self.tabs.setCurrentIndex(idx); self.save_session_state()

    def close_tab(self, index):
        self.tabs.removeTab(index)
        if self.tabs.count() == 0: self.add_new_tab()
        self.save_session_state()

    def tab_changed(self, index): self.save_session_state()

    def save_session_state(self):
        files = []
        for i in range(self.tabs.count()):
            path = self.tabs.widget(i).file_path
            if path: files.append(path)
        self.mgr.settings["open_files"] = files
        self.mgr.settings["current_tab_index"] = self.tabs.currentIndex()
        self.mgr.save()

    def on_open(self):
        path, _ = QFileDialog.getOpenFileName(self, "OPEN", "", "All Files (*)")
        if path: self.add_new_tab(path)

    def on_save(self):
        editor = self.current_editor()
        if not editor: return
        
        path = editor.file_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "SAVE", "", "All Files (*)")
            if not path: return
            editor.file_path = path
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.basename(path))
            
        try:
            with open(path, 'w', encoding='utf-8') as f: f.write(editor.toPlainText())
            self.statusBar().showMessage(f"SAVED: {path}")
            self.save_session_state()
        except Exception as e: QMessageBox.warning(self, "ERR", str(e))

    def handle_shortcut(self, action):
        if action.startswith("LOAD_FILE:"): self.add_new_tab(action[len("LOAD_FILE:"):])
        elif action == "CLOSE_TAB": self.close_tab(self.tabs.currentIndex())
        elif action == "TOGGLE_SEARCH": self.toggle_search()
        elif action == "SAVE_FILE": self.on_save()
        elif action == "OPEN_FILE": self.on_open()
        elif action == "RESTART_APP": self.on_restart()

    def toggle_search(self, force=None):
        visible = not self.search_panel.isVisible() if force is None else force
        self.search_panel.setVisible(visible)
        if visible:
            self.search_panel.search_input.setFocus()
            self.search_panel.search_input.selectAll()

    def search_next(self):
        editor = self.current_editor()
        if not editor: return
        query = self.search_panel.search_input.text()
        if not query: return
        if not editor.find(query):
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            editor.setTextCursor(cursor)
            editor.find(query)

    def search_prev(self):
        editor = self.current_editor()
        if not editor: return
        query = self.search_panel.search_input.text()
        if not query: return
        if not editor.find(query, QTextDocument.FindFlag.FindBackward):
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            editor.setTextCursor(cursor)
            editor.find(query, QTextDocument.FindFlag.FindBackward)

    def do_replace(self):
        editor = self.current_editor()
        if not editor: return
        cursor = editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.search_panel.replace_input.text())
            self.search_next()

    def do_replace_all(self):
        editor = self.current_editor()
        if not editor: return
        query = self.search_panel.search_input.text()
        repl = self.search_panel.replace_input.text()
        if not query: return
        editor.setPlainText(editor.toPlainText().replace(query, repl))

    def on_restart(self):
        QApplication.quit()
        subprocess.Popen([sys.executable] + sys.argv)

    def on_keybinds(self):
        KeybindDialog(self, self.mgr).exec()
    def on_settings(self):
        if SettingsDialog(self, self.mgr).exec():
            self.apply_theme_global()
            self.resize(self.mgr.settings["width"], self.mgr.settings["height"])

    def on_elevate(self):
        buf_path = os.path.join(tempfile.gettempdir(), "cyber_edit_lock.tmp")
        try:
            editor = self.current_editor()
            content = editor.toPlainText() if editor else ""
            with open(buf_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            script = os.path.abspath(sys.argv[0])
            params = f'"{script}" --buffer "{buf_path}"'
            if editor and editor.file_path:
                params += f' --file "{editor.file_path}"'
            
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            if ret > 32:
                QApplication.quit()
        except Exception as e:
            QMessageBox.critical(self, "ERR", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    initial_file, buffer_file, i = None, None, 0
    args = sys.argv[1:]
    while i < len(args):
        if args[i] == "--file" and i + 1 < len(args):
            initial_file = args[i+1]
            i += 2
        elif args[i] == "--buffer" and i + 1 < len(args):
            buffer_file = args[i+1]
            i += 2
        else:
            if not initial_file:
                initial_file = args[i]
            i += 1
            
    window = MainWindow(initial_file, buffer_file)
    window.show()
    sys.exit(app.exec())
