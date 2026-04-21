import sys
import json
import os
import re
import urllib.request
import webbrowser
import difflib
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLineEdit, QCheckBox, QDialog,
                            QDialogButtonBox, QLabel, QTextEdit, QComboBox, QMessageBox,
                            QSplitter, QFrame, QTextBrowser, QMenu, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QPoint, QSize, QByteArray
from PyQt6.QtGui import QFont, QTextCursor, QKeySequence, QTextDocument, QFontDatabase, QFontMetrics, QTextCharFormat, QColor, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AHK_SCRIPT_PATH = os.path.join(SCRIPT_DIR, "ahk_v2.ahk")
SHORTCUTS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ahk_shortcuts.json")
# Ensure directory exists
os.makedirs(os.path.dirname(SHORTCUTS_JSON_PATH), exist_ok=True)

# Convex Config Backup Settings
CONVEX_URL = "https://different-gnat-734.convex.cloud"
SCRIPT_NAME = "ahk_manager"

# Cyberpunk-style colors for Convex dialogs
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_GREEN = "#00ff21"
CP_SUBTEXT = "#888888"

# SVG Collection
SVGS = {
    "UPLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>',        
    "DOWNLOAD": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>',   
    "TRASH": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2-0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2-0 0 1 2 2v2"></path></svg>',
    "EYE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>',
    "DIFF": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>'
}

class CyberButton(QPushButton):
    """Modern button with SVG icon support and dynamic hover color-switching."""
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
        # Inject color into SVG currentColor placeholder
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
                QPushButton {{ background-color: transparent; color: {self.color}; border: 2px solid {self.color}; padding: 5px 15px; font-family: 'Consolas'; }}
                QPushButton:hover {{ background-color: {self.color}; color: {CP_BG}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{ background-color: {self.color}; color: {CP_BG}; border: none; padding: 5px 15px; font-family: 'Consolas'; }}
                QPushButton:hover {{ background-color: {CP_BG}; color: {self.color}; border: 1px solid {self.color}; }}
            """)

class DiffDialog(QDialog):
    """GitHub-style color-coded comparison view."""
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

        # Fix floats in both for accurate comparison
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
    """Backup label dialog with inline CHECK button to compare local vs latest backup."""
    def __init__(self, parent=None, convex_call_fn=None, config_data=None):
        super().__init__(parent)
        self.setWindowTitle("BACKUP LABEL")
        self.setFixedWidth(420)
        self._convex_call = convex_call_fn
        self._config_data = config_data or {}
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
        
        self.diff_btn = CyberButton("DIFF", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["DIFF"])
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
            remote_raw = self._convex_call("query", {"path": "functions:get", "args": {"id": latest["id"]}}).get("value", {})
            
            def fix(obj):
                if isinstance(obj, dict): return {k: fix(v) for k, v in obj.items()}
                if isinstance(obj, list): return [fix(i) for i in obj]
                if isinstance(obj, float) and obj.is_integer(): return int(obj)
                return obj
            
            self._remote_data = fix(remote_raw)
            skip = {"$schema", "gui_settings"}
            local_cmp = {k: v for k, v in self._config_data.items() if k not in skip}
            remote_cmp = {k: v for k, v in self._remote_data.items() if k not in skip}
            
            dirty = json.dumps(local_cmp, sort_keys=True) != json.dumps(remote_cmp, sort_keys=True)
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
    """Shows list of backups and lets user pick one to restore or delete."""
    def __init__(self, backups, convex_call_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RESTORE FROM BACKUP")
        self.setFixedWidth(520)
        self.selected_id = None
        self._convex_call = convex_call_fn
        self._backups = list(backups)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_YELLOW}; font-family: 'Consolas'; font-size: 10pt; }} QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }} QPushButton {{ font-family: 'Consolas'; font-size: 10pt; font-weight: bold; }}")
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(QLabel("Select a backup to restore:"))
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("background: transparent; border: 1px solid #3a3a3a;")
        self._scroll.setFixedHeight(300)
        self._layout.addWidget(self._scroll)
        
        cancel = CyberButton("ABORT", color=CP_DIM, is_outlined=True)
        cancel.clicked.connect(self.reject)
        self._layout.addWidget(cancel)
        self._render_list()

    def _render_list(self):
        import datetime
        inner = QWidget()
        inner.setStyleSheet(f"background: {CP_PANEL};")
        vbox = QVBoxLayout(inner)
        vbox.setSpacing(4)
        for b in self._backups:
            # 12-hour format: %I:%M %p
            dt = datetime.datetime.fromtimestamp(b["createdAt"] / 1000).strftime("%Y-%m-%d %I:%M %p")
            row = QHBoxLayout()

            # Separator: ->
            btn = QPushButton(f"  {dt}  ->  {b['label']}")
            btn.setStyleSheet(f"text-align: left; padding: 8px; background: {CP_BG}; color: {CP_TEXT}; border: 1px solid #2a2a2a;")
            btn.clicked.connect(lambda checked, bid=b["id"]: self._select(bid))

            # Delete button with SVG icon
            del_btn = QPushButton()
            del_btn.setFixedSize(32, 32)
            del_btn.setStyleSheet("background: transparent; border: 1px solid #2a2a2a; padding: 3px;")

            # Render TRASH icon with RED color
            renderer = QSvgRenderer(QByteArray(SVGS["TRASH"].replace('currentColor', CP_RED).encode()))
            pix = QPixmap(22, 22)
            pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pix)
            renderer.render(painter)
            painter.end()
            del_btn.setIcon(QIcon(pix))
            del_btn.clicked.connect(lambda checked, bid=b["id"]: self._delete(bid))

            # Diff button with DIFF SVG
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
            diff_btn.clicked.connect(lambda checked, bid=b["id"], lbl=b["label"]: self._diff_check(bid, lbl))

            row.addWidget(btn)
            row.addWidget(diff_btn)
            row.addWidget(del_btn)
            vbox.addLayout(row)
        vbox.addStretch()
        self._scroll.setWidget(inner)

    def _diff_check(self, backup_id, label):
        try:
            remote = self._convex_call("query", {"path": "functions:get", "args": {"id": backup_id}}).get("value", {})
            # Local config from parent
            parent = self.parent()
            local_config = {
                "script_shortcuts": parent.script_shortcuts,
                "text_shortcuts": parent.text_shortcuts,
                "startup_scripts": parent.startup_scripts,
                "context_shortcuts": parent.context_shortcuts,
                "app_font_family": parent.app_font_family
            }
            
            DiffDialog(local_config, remote, title=f"DIFF // {label}", parent=self).exec()
        except Exception as e:
            QMessageBox.critical(self, "DIFF FAILED", str(e))

    def _delete(self, backup_id):
        try:
            self._convex_call("mutation", {"path": "functions:remove", "args": {"id": backup_id}})
            self._backups = [b for b in self._backups if b["id"] != backup_id]
            self._render_list()
        except Exception as e:
            QMessageBox.critical(self, "DELETE FAILED", str(e))

    def _select(self, backup_id):
        self.selected_id = backup_id
        self.accept()

class ShortcutBuilderPopup(QDialog):
    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.setWindowTitle("Shortcut Builder")
        self.setModal(True)
        self.setFixedWidth(400)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        self.result_hotkey = initial_value
        self.mods = {"^": False, "!": False, "+": False, "#": False}
        self.main_key = ""
        
        self.parse_initial(initial_value)
        self.setup_ui()

    def parse_initial(self, value):
        if not value: return
        
        # Extract modifiers
        for mod in self.mods:
            if mod in value:
                self.mods[mod] = True
                value = value.replace(mod, "")
        
        self.main_key = value

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Preview
        self.preview_label = QLabel(self.get_formatted_preview())
        self.preview_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #61dafb; margin: 10px; qproperty-alignment: AlignCenter;")
        layout.addWidget(self.preview_label)
        
        # Modifiers
        mod_layout = QHBoxLayout()
        self.mod_buttons = {}
        mod_info = [("^", "Ctrl"), ("!", "Alt"), ("+", "Shift"), ("#", "Win")]
        for symbol, name in mod_info:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setChecked(self.mods[symbol])
            btn.setStyleSheet("""
                QPushButton { background: #3d3d3d; border: 1px solid #555; padding: 10px; border-radius: 5px; }
                QPushButton:checked { background: #61dafb; color: black; border-color: #61dafb; }
            """)
            btn.toggled.connect(lambda checked, s=symbol: self.update_mod(s, checked))
            mod_layout.addWidget(btn)
            self.mod_buttons[symbol] = btn
        layout.addLayout(mod_layout)
        
        # Key Selector
        layout.addWidget(QLabel("Select Main Key:"))
        self.key_list = QComboBox()
        self.key_list.setEditable(True)
        self.common_keys = [
            "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", 
            "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "Space", "Enter", "Tab", "Esc", "Backspace", "Delete", "Insert", "Home", "End", "PgUp", "PgDn",
            "Up", "Down", "Left", "Right", "LButton", "RButton", "MButton", "WheelUp", "WheelDown",
            "[", "]", ";", "'", ",", ".", "/", "\\", "-", "=", "`"
        ]
        self.key_list.addItems(self.common_keys)
        
        # Search Box
        self.key_search = QLineEdit()
        self.key_search.setPlaceholderText("Search keys (e.g. 'space', 'f1', 'x')...")
        self.key_search.textChanged.connect(self.filter_keys)
        # Style search box
        self.key_search.setStyleSheet("padding: 8px; border-radius: 5px; background: #3d3d3d;")
        layout.addWidget(self.key_search)
        
        if self.main_key:
            self.key_list.setCurrentText(self.main_key)
        self.key_list.currentTextChanged.connect(self.update_key)
        layout.addWidget(self.key_list)
        
        # Quick access area (Flow layout style)
        layout.addWidget(QLabel("Quick Keys:"))
        quick_grid = QWidget()
        quick_layout = QHBoxLayout(quick_grid)
        quick_layout.setContentsMargins(0, 0, 0, 0)
        for k in ["Space", "Enter", "Tab", "Esc", "Up", "Down"]:
            btn = QPushButton(k)
            btn.setStyleSheet("padding: 5px; font-size: 12px;")
            btn.clicked.connect(lambda checked, val=k: self.key_list.setCurrentText(val))
            quick_layout.addWidget(btn)
        layout.addWidget(quick_grid)

        # OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_mod(self, symbol, state):
        self.mods[symbol] = state
        self.update_preview()

    def update_key(self, key):
        self.main_key = key
        self.update_preview()

    def update_preview(self):
        self.preview_label.setText(self.get_formatted_preview())

    def get_formatted_preview(self):
        res = ""
        if self.mods["^"]: res += "Ctrl+"
        if self.mods["!"]: res += "Alt+"
        if self.mods["+"]: res += "Shift+"
        if self.mods["#"]: res += "Win+"
        res += self.main_key if self.main_key else "?"
        return res

    def get_final_ahk(self):
        res = ""
        if self.mods["^"]: res += "^"
        if self.mods["!"]: res += "!"
        if self.mods["+"]: res += "+"
        if self.mods["#"]: res += "#"
        res += self.main_key
        return res

    def filter_keys(self, text):
        text = text.lower().strip()
        if not text:
            # If search is cleared, don't change current selection unless it's empty
            return

        # Find all matching keys
        matches = [k for k in self.common_keys if text in k.lower()]
        
        if matches:
            # Automatically pick the best match (starts with text is better than just contains)
            best_match = next((k for k in matches if k.lower().startswith(text)), matches[0])
            self.key_list.setCurrentText(best_match)

class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.record_button = None

    def set_recording(self, state):
        if not state:
            return
            
        # Instead of recording, show the builder
        builder = ShortcutBuilderPopup(self, self.text())
        if builder.exec():
            self.setText(builder.get_final_ahk())
        
        # Always uncheck the button after the dialog closes
        if self.record_button:
            self.record_button.setChecked(False)

    def keyPressEvent(self, event):
        # We might still want to capture normal typing for manual entry
        super().keyPressEvent(event)

class AddEditShortcutDialog(QDialog):
    def __init__(self, parent, shortcut_type, shortcut_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.shortcut_type = shortcut_type
        self.shortcut_data = shortcut_data

        self.setWindowTitle(f"{'Edit' if shortcut_data else 'Add'} {shortcut_type.capitalize()} Shortcut")
        self.setModal(True)
        self.resize(500, 400)

        self.setup_ui()
        if shortcut_data:
            self.populate_fields()

    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        
        # Create top layout for name, category, description
        top_layout = QHBoxLayout()
        
        # Left side - form fields
        form_layout = QVBoxLayout()
        
        # Name
        form_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Open Terminal, Version 1 Text")
        form_layout.addWidget(self.name_edit)
        
        # Category
        form_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        existing_categories = self.get_existing_categories()
        self.category_combo.addItems(existing_categories)
        self.category_combo.setCurrentText("General")
        form_layout.addWidget(self.category_combo)
        
        # Description
        form_layout.addWidget(QLabel("Description:"))
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Brief description of what this does")
        form_layout.addWidget(self.description_edit)
        
        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Enabled (include in generated script)")
        self.enabled_checkbox.setChecked(True)
        form_layout.addWidget(self.enabled_checkbox)
        
        if self.shortcut_type == "script":
            hotkey_row = QHBoxLayout()
            self.hotkey_edit = HotkeyLineEdit()
            self.hotkey_edit.setPlaceholderText("e.g., !Space, ^!n, #x")
            
            self.record_hotkey_btn = QPushButton("⌨")
            self.record_hotkey_btn.setCheckable(True)
            self.record_hotkey_btn.setFixedWidth(40)
            self.record_hotkey_btn.setStyleSheet("""
                QPushButton {
                    font-family: inherit;
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    border-radius: 5px;
                    color: white;
                    font-size: 18px;
                }
                QPushButton:checked {
                    background-color: #61dafb;
                    color: black;
                    border-color: #61dafb;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    border-color: #61dafb;
                }
            """)
            self.record_hotkey_btn.setToolTip("Open Shortcut Builder")
            self.record_hotkey_btn.clicked.connect(lambda checked: self.hotkey_edit.set_recording(checked))
            self.hotkey_edit.record_button = self.record_hotkey_btn
            
            hotkey_row.addWidget(self.hotkey_edit)
            hotkey_row.addWidget(self.record_hotkey_btn)
            form_layout.addLayout(hotkey_row)
        elif self.shortcut_type == "context":
            # Context shortcuts have both hotkey and context fields
            form_layout.addWidget(QLabel("Hotkey:"))
            hotkey_row = QHBoxLayout()
            self.hotkey_edit = HotkeyLineEdit()
            self.hotkey_edit.setPlaceholderText("e.g., ^s, ^r")
            
            self.record_hotkey_btn = QPushButton("⌨")
            self.record_hotkey_btn.setCheckable(True)
            self.record_hotkey_btn.setFixedWidth(40)
            self.record_hotkey_btn.setStyleSheet("""
                QPushButton {
                    font-family: inherit;
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    border-radius: 5px;
                    color: white;
                    font-size: 18px;
                }
                QPushButton:checked {
                    background-color: #61dafb;
                    color: black;
                    border-color: #61dafb;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                    border-color: #61dafb;
                }
            """)
            self.record_hotkey_btn.setToolTip("Open Shortcut Builder")
            self.record_hotkey_btn.clicked.connect(lambda checked: self.hotkey_edit.set_recording(checked))
            self.hotkey_edit.record_button = self.record_hotkey_btn
            
            hotkey_row.addWidget(self.hotkey_edit)
            hotkey_row.addWidget(self.record_hotkey_btn)
            form_layout.addLayout(hotkey_row)
            
            # Context fields
            form_layout.addWidget(QLabel("Window Title (contains):"))
            self.window_title_edit = QLineEdit()
            self.window_title_edit.setPlaceholderText("e.g., Gemini, Visual Studio Code")
            form_layout.addWidget(self.window_title_edit)
            
            form_layout.addWidget(QLabel("Process Name (optional):"))
            self.process_name_edit = QLineEdit()
            self.process_name_edit.setPlaceholderText("e.g., WindowsTerminal.exe, Code.exe")
            form_layout.addWidget(self.process_name_edit)
            
            form_layout.addWidget(QLabel("Window Class (optional):"))
            self.window_class_edit = QLineEdit()
            self.window_class_edit.setPlaceholderText("e.g., CabinetWClass")
            form_layout.addWidget(self.window_class_edit)
        elif self.shortcut_type == "text":
            # Trigger
            form_layout.addWidget(QLabel("Trigger (without ::):"))
            self.trigger_edit = QLineEdit()
            self.trigger_edit.setPlaceholderText("e.g., ;v1, ;run")
            form_layout.addWidget(self.trigger_edit)
        elif self.shortcut_type == "file":
            # Trigger
            form_layout.addWidget(QLabel("Trigger (without ::):"))
            self.trigger_edit = QLineEdit()
            self.trigger_edit.setPlaceholderText("e.g., ;theme, ;file")
            form_layout.addWidget(self.trigger_edit)
            
            # File Path
            form_layout.addWidget(QLabel("File Path:"))
            file_row = QHBoxLayout()
            self.file_path_edit = QLineEdit()
            self.file_path_edit.setPlaceholderText("C:\\path\\to\\file.ext or @..\\path")
            self.browse_btn = QPushButton("Browse")
            from PyQt6.QtWidgets import QFileDialog
            self.browse_btn.clicked.connect(self.browse_file)
            file_row.addWidget(self.file_path_edit)
            file_row.addWidget(self.browse_btn)
            form_layout.addLayout(file_row)
        # Background script type has no hotkey/trigger
        
        # Add form layout to top layout
        top_layout.addLayout(form_layout)
        
        # Right side - action/replacement with bigger height and width
        if self.shortcut_type in ["script", "startup", "context"]:
            # Action
            action_layout = QVBoxLayout()
            action_layout.addWidget(QLabel("Script/Action Code:"))
            self.action_edit = QTextEdit()
            self.action_edit.setMinimumHeight(300)  # Bigger height
            self.action_edit.setMinimumWidth(400)   # Bigger width
            
            # Add helpful placeholder text based on shortcut type
            if self.shortcut_type == "context":
                placeholder = """Examples:

; Send text (for terminal commands)
SendText("/chat save")
SendText("ls -la")

; Send keys
Send("^c")  ; Ctrl+C
Send("{Enter}")
Send("!{F4}")  ; Alt+F4

; Run programs
Run("notepad.exe")
Run("C:\\path\\to\\program.exe")

; Show message
MsgBox("Hello!")

; Multiple actions
SendText("cd Documents")
Send("{Enter}")
Sleep(100)
SendText("dir")
Send("{Enter}")

; Get clipboard
text := A_Clipboard
MsgBox(text)

; Set clipboard
A_Clipboard := "New text"

; Window operations
WinMaximize("A")  ; Maximize active window
WinMinimize("A")  ; Minimize active window
WinClose("A")     ; Close active window"""
            elif self.shortcut_type == "startup":
                placeholder = """Examples:

; Background script that runs on startup
; No hotkey needed - runs automatically

; Register shell hook
DllCall("RegisterShellHookWindow", "Ptr", A_ScriptHwnd)

; Set timer
SetTimer(MyFunction, 1000)  ; Run every 1 second

; Monitor clipboard
OnClipboardChange(MyClipFunction)

; Watch for window events
SetTimer(CheckWindow, 500)"""
            else:  # script
                placeholder = """Examples:

; Simple action
Run("notepad.exe")

; Multiple lines
{
    MsgBox("Starting...")
    Run("notepad.exe")
    Sleep(1000)
    WinActivate("Untitled - Notepad")
}

; Function definition
MyFunction() {
    MsgBox("Hello!")
    Send("^c")
}

; Send keys
Send("^c")  ; Ctrl+C
Send("{Enter}")
SendText("Hello World")"""
            
            self.action_edit.setPlaceholderText(placeholder)
            
            # Add help button for command reference
            help_btn = QPushButton("📖 Command Reference")
            help_btn.setStyleSheet("""
                QPushButton {
                    background-color: #6f42c1;
                    color: white;
                    border: 1px solid #5a32a3;
                    padding: 5px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #8250df;
                }
            """)
            help_btn.clicked.connect(self.show_command_reference)
            action_layout.addWidget(help_btn)
            
            action_layout.addWidget(self.action_edit)
            top_layout.addLayout(action_layout)
        else:
            # Replacement
            replacement_layout = QVBoxLayout()
            replacement_layout.addWidget(QLabel("Replacement Text:"))
            self.replacement_edit = QTextEdit()
            self.replacement_edit.setMinimumHeight(300)  # Bigger height
            self.replacement_edit.setMinimumWidth(400)   # Bigger width
            replacement_layout.addWidget(self.replacement_edit)
            top_layout.addLayout(replacement_layout)
        
        layout.addLayout(top_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_existing_categories(self):
        categories = set()
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.text_shortcuts + self.parent_window.startup_scripts + self.parent_window.context_shortcuts:
            category = shortcut.get('category', '').strip()
            if category:
                categories.add(category)

        common_categories = ["System", "Navigation", "Text", "Media", "AutoHotkey", "General"]
        existing_sorted = sorted(categories)

        result = []
        for cat in common_categories:
            if cat in existing_sorted:
                result.append(cat)
                existing_sorted.remove(cat)
        result.extend(existing_sorted)
        return result

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Drop")
        if file_path:
            self.file_path_edit.setText(file_path)

    def populate_fields(self):
        self.name_edit.setText(self.shortcut_data.get("name", ""))
        self.category_combo.setCurrentText(self.shortcut_data.get("category", ""))
        self.description_edit.setText(self.shortcut_data.get("description", ""))
        self.enabled_checkbox.setChecked(self.shortcut_data.get("enabled", True))

        if self.shortcut_type == "script":
            self.hotkey_edit.setText(self.shortcut_data.get("hotkey", ""))
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
        elif self.shortcut_type == "context":
            self.hotkey_edit.setText(self.shortcut_data.get("hotkey", ""))
            self.window_title_edit.setText(self.shortcut_data.get("window_title", ""))
            self.process_name_edit.setText(self.shortcut_data.get("process_name", ""))
            self.window_class_edit.setText(self.shortcut_data.get("window_class", ""))
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
        elif self.shortcut_type == "startup":
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
        elif self.shortcut_type == "file":
            self.trigger_edit.setText(self.shortcut_data.get("trigger", ""))
            self.file_path_edit.setText(self.shortcut_data.get("file_path", ""))
        else: # text
            self.trigger_edit.setText(self.shortcut_data.get("trigger", ""))
            self.replacement_edit.setPlainText(self.shortcut_data.get("replacement", ""))

    def show_command_reference(self):
        """Show AutoHotkey command reference in a dialog"""
        ref_dialog = QDialog(self)
        ref_dialog.setWindowTitle("AutoHotkey Command Reference")
        ref_dialog.resize(1100, 850)
        ref_dialog.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        # Use the application's current font
        app_font = self.parent_window.app_font_family
        _fnt = QFont(app_font, 10)
        _fnt.setFamilies([app_font, "JetBrainsMono NFP", "Segoe UI", "Consolas", "monospace"])
        ref_dialog.setFont(_fnt)
        
        layout = QVBoxLayout(ref_dialog)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Search Bar
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search in documentation (Press Enter for next)...")
        search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                border-radius: 5px;
                background: #2d2d2d;
                border: 1px solid #444;
                color: white;
                font-size: 14px;
                font-family: '{app_font}';
            }}
            QLineEdit:focus {{ border-color: #61dafb; }}
        """)
        
        search_btn = QPushButton("Next")
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #3d3d3d;
                border: 1px solid #555;
                padding: 8px 15px;
                border-radius: 5px;
                font-family: '{app_font}';
            }}
            QPushButton:hover {{
                background-color: #4d4d4d;
                border-color: #61dafb;
            }}
        """)
        
        search_layout.addWidget(QLabel("🔍 Search:"))
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Create text browser with anchor-click override
        class AnchorBrowser(QTextBrowser):
            def mousePressEvent(self, e):
                anchor = self.anchorAt(e.pos())
                if anchor and anchor.startswith('#'):
                    self._jump_to(anchor[1:])
                    return
                super().mousePressEvent(e)
            def _jump_to(self, fragment):
                amap = getattr(self, '_anchor_map', {})
                text = amap.get(fragment, fragment.replace('-', ' '))
                c = self.textCursor()
                c.movePosition(QTextCursor.MoveOperation.Start)
                self.setTextCursor(c)
                self.find(text)
                self.ensureCursorVisible()
        
        browser = AnchorBrowser()
        browser.setOpenLinks(False)
        browser.setOpenExternalLinks(False)
        browser.setFont(_fnt)
        browser.document().setDocumentMargin(15)
        browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: #2b2b2b;
                color: #e0e0e0;
                border: none;
                padding: 0px;
                font-family: '{app_font}', 'JetBrainsMono NFP', 'Consolas', monospace;
                font-size: 13px;
            }}
        """)
        
        # Load the reference content
        ref_file = os.path.join(SCRIPT_DIR, "README.md")
        if os.path.exists(ref_file):
            try:
                with open(ref_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Build anchor->heading map from <a name="x"> tags
                anchor_map = {}
                lines = content.split('\n')
                pending_anchor = None
                for line in lines:
                    am = re.match(r'<a name="([^"]+)"', line.strip(), re.IGNORECASE)
                    if am:
                        pending_anchor = am.group(1)
                    elif pending_anchor:
                        hm = re.match(r'^#{1,6}\s+(.*)', line)
                        if hm:
                            anchor_map[pending_anchor] = hm.group(1).strip()
                        pending_anchor = None

                # Strip <a name> lines and TOC section so setMarkdown works cleanly
                clean = re.sub(r'<a name="[^"]+">\s*</a>\n?', '', content, flags=re.IGNORECASE)
                clean = re.sub(r'## Table of Contents.*?\n---', '', clean, flags=re.DOTALL)
                browser.setMarkdown(clean)
                browser._anchor_map = anchor_map
            except Exception as e:
                browser.setPlainText(f"Error loading reference: {e}")
        else:
            browser.setPlainText("Command reference file not found (README.md).")
        
        # TOC sidebar + browser in a splitter
        from PyQt6.QtWidgets import QScrollArea
        toc_scroll = QScrollArea()
        toc_scroll.setWidgetResizable(True)
        toc_scroll.setStyleSheet('QScrollArea { background:#1a1a1a; border:1px solid #444; border-radius:5px; }')
        toc_widget = QWidget()
        toc_widget.setStyleSheet('background:#1a1a1a;')
        toc_layout = QVBoxLayout(toc_widget)
        toc_layout.setContentsMargins(2, 5, 2, 5)
        toc_layout.setSpacing(0)
        toc_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        toc_layout.addWidget(QLabel(f'<b style="color:#61dafb; font-size:13px; font-family:\'{app_font}\'; padding-left:5px;">Contents</b>'))

        # Extract headings from markdown for TOC
        toc_entries = []
        if os.path.exists(ref_file):
            with open(ref_file, 'r', encoding='utf-8') as _f:
                _in_code = False
                for _line in _f:
                    if _line.startswith('```'): _in_code = not _in_code; continue
                    if _in_code or _line.strip().startswith('<'): continue
                    _hm = re.match(r'^(#{1,3})\s+(.*)', _line)
                    if _hm and 'table of contents' not in _hm.group(2).lower(): toc_entries.append((len(_hm.group(1)), _hm.group(2).strip()))

        def make_jump(heading_text):
            def jump():
                c = browser.textCursor()
                c.movePosition(QTextCursor.MoveOperation.Start)
                browser.setTextCursor(c)
                browser.find(heading_text)
                browser.ensureCursorVisible()
            return jump

        # Dynamic width calculation
        fm_lvl1 = QFontMetrics(QFont(app_font, 12, QFont.Weight.Bold))
        fm_lvlN = QFontMetrics(QFont(app_font, 11))
        max_toc_w = 180

        for level, title in toc_entries:
            display_text = ('  ' * (level-1)) + title
            btn = QPushButton(display_text)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Use smaller fonts for more compact look
            f_size = '12px' if level==1 else '11px'
            f_weight = 'bold' if level==1 else 'normal'
            color = '#61dafb' if level==1 else '#ccc'
            
            btn.setStyleSheet(f"""
                QPushButton {{ text-align:left; color:{color};
                    font-family:'{app_font}', 'JetBrainsMono NFP', 'Consolas', monospace; 
                    font-size:{f_size}; font-weight:{f_weight};
                    padding:2px 6px; border:none; background:transparent; }}
                QPushButton:hover {{ color:white; background:#2d2d2d; border-radius:3px; }}
            """)
            btn.clicked.connect(make_jump(title))
            toc_layout.addWidget(btn)
            
            # Calculate width needed
            w = (fm_lvl1 if level == 1 else fm_lvlN).horizontalAdvance(display_text)
            max_toc_w = max(max_toc_w, w + 35)

        max_toc_w = min(max_toc_w, 450) # Cap at 450px
        toc_scroll.setMinimumWidth(max_toc_w)
        toc_scroll.setWidget(toc_widget)

        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(2)
        content_splitter.setContentsMargins(0,0,0,0)
        content_splitter.setStyleSheet("QSplitter::handle { background:#444; }")
        content_splitter.addWidget(toc_scroll)
        content_splitter.addWidget(browser)
        content_splitter.setStretchFactor(0, 0)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setSizes([max_toc_w, 1100 - max_toc_w])
        layout.addWidget(content_splitter)
        
        # Search functionality
        def clear_highlights():
            browser.setExtraSelections([])

        def do_search():
            text = search_input.text()
            if not text:
                clear_highlights()
                return

            # Find all occurrences for highlighting
            extra_selections = []
            
            # Format for ALL matches
            fmt = QTextCharFormat()
            fmt.setBackground(QColor("#555500")) # Dim yellow for all matches
            
            # Format for CURRENT selection
            current_fmt = QTextCharFormat()
            current_fmt.setBackground(QColor("#ffff00")) # Bright yellow for current
            current_fmt.setForeground(QColor("black"))

            # First, find the next occurrence to scroll to it
            found = browser.find(text)
            if not found:
                # Wrap around
                cursor = browser.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                browser.setTextCursor(cursor)
                found = browser.find(text)

            if found:
                # Store the current selection to highlight it differently later
                current_selection_cursor = browser.textCursor()

                # Search all matches to highlight them
                doc = browser.document()
                highlight_cursor = QTextCursor(doc)
                while True:
                    highlight_cursor = doc.find(text, highlight_cursor)
                    if highlight_cursor.isNull():
                        break
                    
                    selection = QTextEdit.ExtraSelection()
                    # Check if this match is the currently selected one
                    if highlight_cursor.selectionStart() == current_selection_cursor.selectionStart():
                        selection.format = current_fmt
                    else:
                        selection.format = fmt
                        
                    selection.cursor = highlight_cursor
                    extra_selections.append(selection)

                browser.setExtraSelections(extra_selections)
            else:
                clear_highlights()
        
        search_input.textChanged.connect(lambda t: clear_highlights() if not t else None)
        search_input.returnPressed.connect(do_search)
        search_btn.clicked.connect(do_search)
        
        # Close button
        button_box = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.setFixedWidth(120)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #444;
                padding: 10px;
                border-radius: 5px;
                font-family: '{app_font}';
            }}
            QPushButton:hover {{
                background-color: #555;
            }}
        """)
        close_btn.clicked.connect(ref_dialog.close)
        button_box.addStretch()
        button_box.addWidget(close_btn)
        layout.addLayout(button_box)
        
        ref_dialog.exec()

    def accept_dialog(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Name is required.")
            return

        category = self.category_combo.currentText().strip() or "General"
        description = self.description_edit.text().strip()
        enabled = self.enabled_checkbox.isChecked()

        if self.shortcut_type == "script":
            hotkey = self.hotkey_edit.text().strip()
            action = self.action_edit.toPlainText().strip()

            if not hotkey or not action:
                QMessageBox.warning(self, "Warning", "Both hotkey and action are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "hotkey": hotkey,
                "action": action,
                "enabled": enabled
            }
        elif self.shortcut_type == "context":
            hotkey = self.hotkey_edit.text().strip()
            action = self.action_edit.toPlainText().strip()
            window_title = self.window_title_edit.text().strip()
            process_name = self.process_name_edit.text().strip()
            window_class = self.window_class_edit.text().strip()

            if not hotkey or not action:
                QMessageBox.warning(self, "Warning", "Hotkey and action are required.")
                return
            
            if not window_title and not process_name and not window_class:
                QMessageBox.warning(self, "Warning", "At least one context field (Window Title, Process Name, or Window Class) is required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "hotkey": hotkey,
                "window_title": window_title,
                "process_name": process_name,
                "window_class": window_class,
                "action": action,
                "enabled": enabled
            }
        elif self.shortcut_type == "startup":
            action = self.action_edit.toPlainText().strip()
            if not action:
                QMessageBox.warning(self, "Warning", "Action code is required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "action": action,
                "enabled": enabled
            }
        elif self.shortcut_type == "file":
            trigger = self.trigger_edit.text().strip()
            file_path = self.file_path_edit.text().strip()

            if not trigger or not file_path:
                QMessageBox.warning(self, "Warning", "Both trigger and file path are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "trigger": trigger,
                "file_path": file_path,
                "enabled": enabled
            }
        else: # self.shortcut_type == "text"
            trigger = self.trigger_edit.text().strip()
            replacement = self.replacement_edit.toPlainText().strip()

            if not trigger or not replacement:
                QMessageBox.warning(self, "Warning", "Both trigger and replacement are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "trigger": trigger,
                "replacement": replacement,
                "enabled": enabled
            }

        if self.shortcut_data:
            # Edit existing
            self.shortcut_data.update(shortcut_data)
        else:
            # Add new
            if self.shortcut_type == "script":
                self.parent_window.script_shortcuts.append(shortcut_data)
            elif self.shortcut_type == "context":
                self.parent_window.context_shortcuts.append(shortcut_data)
            elif self.shortcut_type == "startup":
                self.parent_window.startup_scripts.append(shortcut_data)
            elif self.shortcut_type == "file":
                self.parent_window.file_shortcuts.append(shortcut_data)
            else:
                self.parent_window.text_shortcuts.append(shortcut_data)

        self.parent_window.save_shortcuts_json()
        self.parent_window.update_display()
        self.accept()


class CategoryColorDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Category Colors")
        self.setModal(True)
        self.resize(400, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Category Colors"))

        # Color entries will be added dynamically
        self.color_entries = {}
        self.populate_colors(layout)

        # Buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Save Colors")
        save_btn.clicked.connect(self.save_colors)
        button_layout.addWidget(save_btn)

        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_colors)
        button_layout.addWidget(reset_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_colors(self, layout):
        # Get all categories
        all_categories = set()
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.text_shortcuts + self.parent_window.context_shortcuts:
            category = shortcut.get('category', 'General')
            if category:
                all_categories.add(category)

        for default_cat in self.parent_window.category_colors.keys():
            all_categories.add(default_cat)

        for category in sorted(all_categories):
            cat_layout = QHBoxLayout()

            current_color = self.parent_window.get_category_color(category)
            cat_label = QLabel(f"📁 {category}")
            cat_layout.addWidget(cat_label)

            color_edit = QLineEdit(current_color)
            color_edit.setPlaceholderText("e.g., #FF6B6B")
            cat_layout.addWidget(color_edit)

            self.color_entries[category] = color_edit
            layout.addLayout(cat_layout)

    def save_colors(self):
        for category, entry in self.color_entries.items():
            color = entry.text().strip()
            if color:
                self.parent_window.category_colors[category] = color

        self.parent_window.update_display()
        QMessageBox.information(self, "Success", "Category colors updated!")

    def reset_colors(self):
        default_colors = {
            "System": "#FF6B6B", "Navigation": "#4ECDC4", "Text": "#45B7D1",
            "Media": "#96CEB4", "AutoHotkey": "#FFEAA7", "General": "#DDA0DD",
            "Imported": "#FFA07A", "Tools": "#98D8C8", "Window": "#F7DC6F", "File": "#BB8FCE"
        }
        self.parent_window.category_colors.update(default_colors)
        self.close()
        CategoryColorDialog(self.parent_window).exec()


class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Font Selection
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Application Font:"))
        
        from PyQt6.QtWidgets import QFontComboBox
        self.font_combo = QFontComboBox()
        
        # Try to find the current font in the list
        current_font = self.parent_window.app_font_family
        self.font_combo.setCurrentFont(QFont(current_font))
        
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)

        layout.addWidget(QLabel("<small><i>Note: Some icons require a Nerd Font (NFP) to display correctly.</i></small>"))

        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save && Apply")
        save_btn.setStyleSheet("background-color: #2ea44f; color: white; font-weight: bold;")
        save_btn.clicked.connect(self.save_settings)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        
        buttons.addStretch()
        buttons.addWidget(save_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def save_settings(self):
        new_font = self.font_combo.currentFont().family()
        self.parent_window.app_font_family = new_font
        self.parent_window.apply_global_font()
        self.parent_window.save_shortcuts_json()
        QMessageBox.information(self, "Success", f"Font updated to '{new_font}' and applied!")


class AHKShortcutEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_shortcuts = []
        self.text_shortcuts = []
        self.file_shortcuts = []
        self.startup_scripts = []
        self.context_shortcuts = []
        self.app_font_family = "JetBrains Mono" # Default
        self.category_colors = {
            "System": "#FF6B6B", "Navigation": "#4ECDC4", "Text": "#45B7D1",
            "Media": "#96CEB4", "AutoHotkey": "#FFEAA7", "General": "#DDA0DD",
            "Imported": "#FFA07A", "Tools": "#98D8C8", "Window": "#F7DC6F", "File": "#BB8FCE"
        }

        # Settings for remembering preferences
        self.settings = QSettings("AHKEditor", "ShortcutEditor")

        self.load_shortcuts_json()
        self.setup_ui()
        self.load_settings()
        self.apply_global_font()
        self.update_display()

    def setup_ui(self):
        self.setWindowTitle("AutoHotkey Script Editor")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Top controls
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(10, 5, 10, 5)

        # Better styling for the whole app
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QPushButton {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                border-radius: 6px;
                padding: 6px 12px;
                height: 28px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 0px 10px;  /* Reduced vertical padding to match fixed height */
                color: #ffffff;
                font-size: 14px;
                height: 28px;
            }
            QLineEdit:focus {
                border-color: #61dafb;
            }
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """)

        # Add button with menu
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ea44f;
                color: white;
                font-weight: bold;
                border: 1px solid #288f44;
            }
            QPushButton:hover {
                background-color: #34bc5a;
            }
            QPushButton::menu-indicator { image: none; }
        """)
        self.add_menu = QMenu()
        self.add_menu.addAction("Script Shortcut", lambda: self.open_add_dialog("script"))
        self.add_menu.addAction("Text Shortcut", lambda: self.open_add_dialog("text"))
        self.add_menu.addAction("File Shortcut", lambda: self.open_add_dialog("file"))
        self.add_menu.addAction("Context Shortcut", lambda: self.open_add_dialog("context"))
        self.add_menu.addAction("Background Script", lambda: self.open_add_dialog("startup"))
        self.add_btn.setMenu(self.add_menu)
        top_layout.addWidget(self.add_btn)

        # Category toggle as a modern switch style
        self.category_toggle = QCheckBox("\uf205")
        self.category_toggle.setChecked(True)
        self.category_toggle.toggled.connect(self.on_category_toggle)
        self.category_toggle.setToolTip("Group by Category")
        self.category_toggle.setStyleSheet("""
            QCheckBox {
                font-family: 'Segoe UI', sans-serif;
                font-size: 24px;
                color: #61dafb;
                margin-left: 5px;
                margin-right: 5px;
            }
            QCheckBox::indicator { width: 0px; height: 0px; }
        """)
        top_layout.addWidget(self.category_toggle)

        # Color button
        self.colors_btn = QPushButton("🎨 Colors")
        self.colors_btn.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                border: 1px solid #5a32a3;
            }
            QPushButton:hover {
                background-color: #8250df;
            }
        """)
        self.colors_btn.clicked.connect(self.open_color_dialog)
        top_layout.addWidget(self.colors_btn)

        # Settings button
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #555;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        top_layout.addWidget(self.settings_btn)

        # Backup button (Cyan Upload)
        self.backup_btn = CyberButton("", color=CP_CYAN, is_outlined=True, svg_data=SVGS["UPLOAD"])
        self.backup_btn.setToolTip("Backup config to Convex cloud")
        self.backup_btn.clicked.connect(self.backup_to_convex)
        top_layout.addWidget(self.backup_btn)

        # Restore button (Yellow Download)
        self.restore_btn = CyberButton("", color=CP_YELLOW, is_outlined=True, svg_data=SVGS["DOWNLOAD"])
        self.restore_btn.setToolTip("Restore config from Convex cloud")
        self.restore_btn.clicked.connect(self.restore_from_convex)
        top_layout.addWidget(self.restore_btn)

        # Search box
        self.search_edit = HotkeyLineEdit()
        self.search_edit.setObjectName("search_edit")
        self.search_edit.setPlaceholderText(" Search shortcuts...")
        self.search_edit.textChanged.connect(self.update_display)
        self.search_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_edit.setStyleSheet("font-family: 'Segoe UI', sans-serif;")
        
        self.record_search_btn = QPushButton("⌨")
        self.record_search_btn.setCheckable(True)
        self.record_search_btn.setFixedWidth(40)
        self.record_search_btn.setStyleSheet("""
            QPushButton {
                font-family: 'Segoe UI', sans-serif;
                background-color: #2d2d2d;
                border: 1px solid #444;
                color: #888;
                font-size: 18px;
            }
            QPushButton:checked {
                background-color: #61dafb;
                color: black;
                border-color: #61dafb;
            }
            QPushButton:hover {
                border-color: #61dafb;
            }
        """)
        self.record_search_btn.clicked.connect(lambda checked: self.search_edit.set_recording(checked))
        self.search_edit.record_button = self.record_search_btn

        top_layout.addWidget(self.search_edit)
        top_layout.addWidget(self.record_search_btn)

        # Removed the addStretch() to let the search bar expand

        # Generate button
        generate_btn = QPushButton("🚀 Generate AHK")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2188ff;
                color: white;
                font-weight: bold;
                border: 1px solid #1c73d9;
            }
            QPushButton:hover {
                background-color: #3b9bff;
            }
        """)
        generate_btn.clicked.connect(self.generate_ahk_script)
        top_layout.addWidget(generate_btn)

        layout.addLayout(top_layout)

        # Text browser for HTML display
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.anchorClicked.connect(self.handle_click)
        self.text_browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_browser.customContextMenuRequested.connect(self.show_context_menu)
        # Enable mouse tracking for double-click detection
        self.text_browser.setMouseTracking(True)
        self.text_browser.viewport().installEventFilter(self)
        layout.addWidget(self.text_browser)

        # Context menu for shortcuts
        self.context_menu = QMenu(self)
        self.edit_action = self.context_menu.addAction("Edit")
        self.duplicate_action = self.context_menu.addAction("Duplicate")
        self.context_menu.addSeparator()
        self.remove_action = self.context_menu.addAction("Remove")
        self.edit_action.triggered.connect(self.edit_selected)
        self.duplicate_action.triggered.connect(self.duplicate_selected)
        self.remove_action.triggered.connect(self.remove_selected)

        central_widget.setLayout(layout)

        self.selected_shortcut = None
        self.selected_type = None

    def apply_global_font(self):
        """Apply the selected font family globally to the application"""
        font = QFont(self.app_font_family, 10)
        QApplication.instance().setFont(font)
        # Force update of elements that might have their own font set
        if hasattr(self, 'text_browser'):
            self.update_display() # Refresh HTML with new font

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def load_settings(self):
        """Load saved settings"""
        group_by_category = self.settings.value("group_by_category", True, type=bool)
        self.category_toggle.setChecked(group_by_category)

    def save_settings(self):
        """Save current settings"""
        self.settings.setValue("group_by_category", self.category_toggle.isChecked())

    def on_category_toggle(self):
        """Handle category toggle change"""
        # Update icon based on state
        if self.category_toggle.isChecked():
            self.category_toggle.setText("\uf205")  # Enabled icon
        else:
            self.category_toggle.setText("\uf204")  # Disabled icon

        self.save_settings()
        self.update_display()

    def closeEvent(self, event):
        """Save settings when closing"""
        self.save_settings()
        event.accept()

    def handle_click(self, url):
        """Handle clicks on shortcuts"""
        url_str = url.toString()
        if url_str.startswith("select://"):
            parts = url_str.replace("select://", "").split("/")
            if len(parts) == 2:
                shortcut_type, index = parts
                index = int(index)

                if shortcut_type == "script" and index < len(self.script_shortcuts):
                    self.selected_shortcut = self.script_shortcuts[index]
                    self.selected_type = "script"
                elif shortcut_type == "text" and index < len(self.text_shortcuts):
                    self.selected_shortcut = self.text_shortcuts[index]
                    self.selected_type = "text"
                elif shortcut_type == "file" and index < len(self.file_shortcuts):
                    self.selected_shortcut = self.file_shortcuts[index]
                    self.selected_type = "file"
                elif shortcut_type == "context" and index < len(self.context_shortcuts):
                    self.selected_shortcut = self.context_shortcuts[index]
                    self.selected_type = "context"
                elif shortcut_type == "startup" and index < len(self.startup_scripts):
                    self.selected_shortcut = self.startup_scripts[index]
                    self.selected_type = "startup"

                # Update display to show selection
                self.update_display()

        elif url_str.startswith("toggle://"):
            parts = url_str.replace("toggle://", "").split("/")
            if len(parts) == 2:
                shortcut_type, index = parts
                index = int(index)

                # Toggle the enabled state
                if shortcut_type == "script" and index < len(self.script_shortcuts):
                    self.script_shortcuts[index]["enabled"] = not self.script_shortcuts[index].get("enabled", True)
                elif shortcut_type == "text" and index < len(self.text_shortcuts):
                    self.text_shortcuts[index]["enabled"] = not self.text_shortcuts[index].get("enabled", True)
                elif shortcut_type == "file" and index < len(self.file_shortcuts):
                    self.file_shortcuts[index]["enabled"] = not self.file_shortcuts[index].get("enabled", True)
                elif shortcut_type == "context" and index < len(self.context_shortcuts):
                    self.context_shortcuts[index]["enabled"] = not self.context_shortcuts[index].get("enabled", True)
                elif shortcut_type == "startup" and index < len(self.startup_scripts):
                    self.startup_scripts[index]["enabled"] = not self.startup_scripts[index].get("enabled", True)

                self.save_shortcuts_json()
                self.update_display()

    def show_context_menu(self, position):
        """Show context menu on right-click"""
        # Only show context menu if a shortcut is selected
        if self.selected_shortcut and self.selected_type:
            # Enable/disable actions based on selection
            self.edit_action.setEnabled(True)
            self.duplicate_action.setEnabled(True)
            self.remove_action.setEnabled(True)
            self.context_menu.exec(self.text_browser.mapToGlobal(position))
        else:
            # Optionally show a disabled menu or no menu at all
            self.edit_action.setEnabled(False)
            self.duplicate_action.setEnabled(False)
            self.remove_action.setEnabled(False)
            # For a cleaner UX, we won't show the menu if nothing is selected

    def eventFilter(self, obj, event):
        """Handle double-click events on the text browser"""
        if obj == self.text_browser.viewport() and event.type() == event.Type.MouseButtonDblClick:
            if event.button() == Qt.MouseButton.LeftButton:
                # Get the position of the click
                pos = event.pos()
                # Get the anchor at the click position
                anchor = self.text_browser.anchorAt(pos)
                
                if anchor:
                    # Handle the click to select the item first
                    from PyQt6.QtCore import QUrl
                    self.handle_click(QUrl(anchor))
                    # Then open the edit dialog
                    self.edit_selected()
                    
                return True  # Event handled
        return super().eventFilter(obj, event)

    def load_shortcuts_json(self):
        if os.path.exists(SHORTCUTS_JSON_PATH):
            try:
                with open(SHORTCUTS_JSON_PATH, 'r', encoding='utf-8') as f:
                    data = self._fix_floats(json.load(f))
                    self.script_shortcuts = data.get("script_shortcuts", [])
                    self.text_shortcuts = data.get("text_shortcuts", [])
                    self.file_shortcuts = data.get("file_shortcuts", [])
                    self.startup_scripts = data.get("startup_scripts", [])
                    self.context_shortcuts = data.get("context_shortcuts", [])
                    self.app_font_family = data.get("app_font_family", "JetBrains Mono")
                    
                    # Fix-up: Move file shortcuts that were accidentally saved in text_shortcuts
                    to_move = [s for s in self.text_shortcuts if "file_path" in s]
                    for s in to_move:
                        self.text_shortcuts.remove(s)
                        self.file_shortcuts.append(s)
                    if to_move:
                        self.save_shortcuts_json()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load shortcuts JSON: {e}")
                self.create_default_shortcuts()
        else:
            self.create_default_shortcuts()

    # -------------------------------------------------------------------------
    # CONVEX BACKUP / RESTORE
    # -------------------------------------------------------------------------
    def _fix_floats(self, obj):
        """Recursively convert float values that should be ints (whole numbers)."""
        if isinstance(obj, dict):
            return {k: self._fix_floats(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._fix_floats(i) for i in obj]
        if isinstance(obj, float) and obj.is_integer():
            return int(obj)
        return obj

    def _convex_call(self, endpoint, payload):
        """Generic Convex HTTP API call. Returns parsed JSON or raises."""
        if not CONVEX_URL:
            raise RuntimeError("CONVEX_URL is not set in the script.")
        url = f"{CONVEX_URL.rstrip('/')}/api/{endpoint}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def backup_to_convex(self):
        if not CONVEX_URL:
            QMessageBox.warning(self, "CONVEX", "Set CONVEX_URL in the script first.")
            return
            
        # Prepare data for backup
        backup_data = {
            "script_shortcuts": self.script_shortcuts,
            "text_shortcuts": self.text_shortcuts,
            "file_shortcuts": self.file_shortcuts,
            "startup_scripts": self.startup_scripts,
            "context_shortcuts": self.context_shortcuts,
            "app_font_family": self.app_font_family
        }

        label, ok = ConvexLabelDialog.get_label(self, convex_call_fn=self._convex_call, config_data=backup_data)
        if not ok or not label.strip():
            return
        
        try:
            res = self._convex_call("mutation", {
                "path": "functions:save",
                "args": {"scriptName": SCRIPT_NAME, "label": label.strip(), "data": backup_data}
            })
            if res.get("status") == "success":
                QMessageBox.information(self, "BACKUP", f'Config backed up: "{label.strip()}"')
            else:
                QMessageBox.warning(self, "BACKUP ERROR", str(res))
        except Exception as e:
            QMessageBox.critical(self, "BACKUP FAILED", str(e))

    def restore_from_convex(self):
        if not CONVEX_URL:
            QMessageBox.warning(self, "CONVEX", "Set CONVEX_URL in the script first.")
            return
        try:
            result = self._convex_call("query", {
                "path": "functions:list",
                "args": {"scriptName": SCRIPT_NAME}
            })
            backups = result.get("value", [])
            if not backups:
                QMessageBox.information(self, "RESTORE", "No backups found for this script.")
                return
            dlg = RestoreDialog(backups, self._convex_call, self)
            if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_id:
                data = self._convex_call("query", {
                    "path": "functions:get",
                    "args": {"id": dlg.selected_id}
                }).get("value")
                if data is None:
                    QMessageBox.critical(self, "RESTORE", "Could not fetch backup data.")
                    return
                
                # Convex returns numbers as floats; convert them back
                data = self._fix_floats(data)
                
                self.script_shortcuts = data.get("script_shortcuts", [])
                self.text_shortcuts = data.get("text_shortcuts", [])
                self.file_shortcuts = data.get("file_shortcuts", [])
                self.startup_scripts = data.get("startup_scripts", [])
                self.context_shortcuts = data.get("context_shortcuts", [])
                self.app_font_family = data.get("app_font_family", "JetBrains Mono")
                
                self.save_shortcuts_json()
                self.update_display()
                QMessageBox.information(self, "RESTORE", "Config restored successfully.")
        except Exception as e:
            QMessageBox.critical(self, "RESTORE FAILED", str(e))

    def create_default_shortcuts(self):
        self.script_shortcuts = [{
            "name": "Open Terminal", "category": "System", "description": "Opens PowerShell as admin",
            "hotkey": "!x", "enabled": True,
            "action": 'RunWait("pwsh -Command `"cd $env:USERPROFILE; Start-Process pwsh -Verb RunAs`"", , "Hide")'
        }]
        self.text_shortcuts = [
            {"name": "AHK Version 1", "category": "AutoHotkey", "description": "AutoHotkey v1 header",
             "trigger": ";v1", "replacement": "#Requires AutoHotkey v1.0", "enabled": True},
            {"name": "AHK Version 2", "category": "AutoHotkey", "description": "AutoHotkey v2 header",
             "trigger": ";v2", "replacement": "#Requires AutoHotkey v2.0", "enabled": True}
        ]
        self.file_shortcuts = []

    def save_shortcuts_json(self):
        try:
            data = {
                "script_shortcuts": self.script_shortcuts, 
                "text_shortcuts": self.text_shortcuts,
                "file_shortcuts": self.file_shortcuts,
                "startup_scripts": self.startup_scripts,
                "context_shortcuts": self.context_shortcuts,
                "app_font_family": self.app_font_family
            }
            with open(SHORTCUTS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shortcuts JSON: {e}")

    def get_category_color(self, category):
        return self.category_colors.get(category, "#B0B0B0")

    def update_display(self):
        scrollbar = self.text_browser.verticalScrollBar()
        scroll_position = scrollbar.value()

        search_query = self.search_edit.text().lower()
        group_by_category = self.category_toggle.isChecked()

        # Filter shortcuts
        filtered_script = [s for s in self.script_shortcuts
                          if search_query in f"{s.get('name', '')} {s.get('hotkey', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        filtered_text = [s for s in self.text_shortcuts
                        if search_query in f"{s.get('name', '')} {s.get('trigger', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        filtered_file = [s for s in self.file_shortcuts
                        if search_query in f"{s.get('name', '')} {s.get('trigger', '')} {s.get('description', '')} {s.get('category', '')} {s.get('file_path', '')}".lower()]
        filtered_context = [s for s in self.context_shortcuts
                           if search_query in f"{s.get('name', '')} {s.get('hotkey', '')} {s.get('description', '')} {s.get('category', '')} {s.get('window_title', '')}".lower()]
        filtered_startup = [s for s in self.startup_scripts
                           if search_query in f"{s.get('name', '')} {s.get('description', '')} {s.get('category', '')}".lower()]

        html = self.generate_html(filtered_script, filtered_text, filtered_file, filtered_context, filtered_startup, group_by_category)
        
        # Only set HTML if it changed or it's an interaction
        self.text_browser.setHtml(html)
        scrollbar.setValue(scroll_position)
        # Second pass restoration for dynamic heights
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1, lambda: scrollbar.setValue(scroll_position))

    def generate_html(self, script_shortcuts, text_shortcuts, file_shortcuts, context_shortcuts, startup_scripts, group_by_category):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: '{self.app_font_family}', 'Segoe UI', sans-serif;
                    margin: 10px 20px;
                    background: #2b2b2b;
                    color: #ffffff;
                    font-size: 18px; /* High visibility base size */
                }}
                .container {{ display: flex; gap: 20px; }}
                .column {{ flex: 1; }}
                .section-title {{
                    font-size: 24px;
                    font-weight: bold;
                    margin: 15px 0 5px 0;
                    color: #61dafb;
                }}
                .section-title:first-child {{
                    margin-top: 5px;
                }}
                .category-header {{
                    font-size: 22px;
                    font-weight: bold;
                    margin: 12px 0 3px 0;
                    padding: 3px 10px;
                    border-radius: 5px;
                    background: #404040;
                }}
                .category-header.first-in-section {{
                    margin-top: 8px;
                }}
                .shortcut-item {{
                    padding: 2px 10px;
                    margin: 1px 0;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.2s;
                    border-left: 3px solid transparent;
                }}
                .shortcut-item:hover {{
                    background: rgba(255,255,255,0.05);
                    border-left-color: #61dafb;
                }}
                .shortcut-item.selected {{
                    background: rgba(97, 218, 251, 0.2);
                    border-left-color: #61dafb;
                }}
                .shortcut-key {{
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 18px;
                    white-space: nowrap;
                    padding-right: 15px;
                }}
                .shortcut-separator {{
                    color: #32CD32;
                    font-weight: bold;
                    font-size: 22px;
                    vertical-align: middle;
                    white-space: nowrap;
                }}
                .shortcut-name {{
                    color: #ffffff;
                    font-size: 18px;
                }}
                .shortcut-desc {{
                    color: #888;
                    font-size: 15px;
                }}
                .status-enabled {{ color: #27ae60; }}
                .status-disabled {{ color: #ff5555; }}
                
                .indent {{ margin-left: 20px; }}
                a {{ text-decoration: none; color: inherit; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="column">
                    <div class="section-title">Script Shortcuts</div>
        """

        if group_by_category:
            # Group script shortcuts by category
            script_categories = {}
            for shortcut in script_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in script_categories:
                    script_categories[category] = []
                script_categories[category].append(shortcut)

            for i, category in enumerate(sorted(script_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(script_categories[category], key=lambda x: x.get('hotkey', '').lower()):
                    original_index = self.script_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "script", original_index, True)
        else:
            # Flat list
            for shortcut in sorted(script_shortcuts, key=lambda x: x.get('hotkey', '').lower()):
                original_index = self.script_shortcuts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "script", original_index, False)

        html += """
                </div>
                <div class="column">
                    <div class="section-title">Context Shortcuts</div>
        """

        if group_by_category:
            context_categories = {}
            for shortcut in context_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in context_categories:
                    context_categories[category] = []
                context_categories[category].append(shortcut)

            for i, category in enumerate(sorted(context_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(context_categories[category], key=lambda x: x.get('hotkey', '').lower()):
                    original_index = self.context_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "context", original_index, True)
        else:
            for shortcut in sorted(context_shortcuts, key=lambda x: x.get('hotkey', '').lower()):
                original_index = self.context_shortcuts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "context", original_index, False)

        html += """
                    <div class="section-title">Background Scripts</div>
        """

        if group_by_category:
            startup_categories = {}
            for shortcut in startup_scripts:
                category = shortcut.get('category', 'General')
                if category not in startup_categories:
                    startup_categories[category] = []
                startup_categories[category].append(shortcut)

            for i, category in enumerate(sorted(startup_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(startup_categories[category], key=lambda x: x.get('name', '').lower()):
                    original_index = self.startup_scripts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "startup", original_index, True)
        else:
            for shortcut in sorted(startup_scripts, key=lambda x: x.get('name', '').lower()):
                original_index = self.startup_scripts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "startup", original_index, False)

        html += """
                </div>
                <div class="column">
                    <div class="section-title">Text Shortcuts</div>
        """

        if group_by_category:
            # Group text shortcuts by category
            text_categories = {}
            for shortcut in text_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in text_categories:
                    text_categories[category] = []
                text_categories[category].append(shortcut)

            for i, category in enumerate(sorted(text_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(text_categories[category], key=lambda x: x.get('trigger', '').lower()):
                    original_index = self.text_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "text", original_index, True)
        else:
            # Flat list
            for shortcut in sorted(text_shortcuts, key=lambda x: x.get('trigger', '').lower()):
                original_index = self.text_shortcuts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "text", original_index, False)

        html += """
                    <div class="section-title">File Shortcuts</div>
        """

        if group_by_category:
            # Group file shortcuts by category
            file_categories = {}
            for shortcut in file_shortcuts:
                category = shortcut.get('category', 'General')
                if category not in file_categories:
                    file_categories[category] = []
                file_categories[category].append(shortcut)

            for i, category in enumerate(sorted(file_categories.keys())):
                color = self.get_category_color(category)
                first_class = " first-in-section" if i == 0 else ""
                html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                for shortcut in sorted(file_categories[category], key=lambda x: x.get('trigger', '').lower()):
                    original_index = self.file_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "file", original_index, True)
        else:
            # Flat list
            for shortcut in sorted(file_shortcuts, key=lambda x: x.get('trigger', '').lower()):
                original_index = self.file_shortcuts.index(shortcut)
                html += self.generate_shortcut_html(shortcut, "file", original_index, False)

        html += """
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def generate_shortcut_html(self, shortcut, shortcut_type, index, indented):
        enabled = shortcut.get('enabled', True)
        status = "✅" if enabled else "❌"
        status_class = "status-enabled" if enabled else "status-disabled"
        indent_class = "indent" if indented else ""

        # Check if this is the selected shortcut
        is_selected = (self.selected_shortcut == shortcut and self.selected_type == shortcut_type)
        selected_class = "selected" if is_selected else ""

        if shortcut_type == "script":
            key = shortcut.get('hotkey', '')
            key_width = 170
        elif shortcut_type == "context":
            key = shortcut.get('hotkey', '')
            window_title = shortcut.get('window_title', '')
            if window_title:
                key = f"{key} [{window_title[:15]}...]" if len(window_title) > 15 else f"{key} [{window_title}]"
            key_width = 220
        elif shortcut_type == "startup":
            key = "🚀 Startup"
            key_width = 170
        else: # text
            key = shortcut.get('trigger', '')
            key_width = 220
        
        # Ensure icon column is stable
        icon_width = 60

        name = shortcut.get('name', 'Unnamed')
        description = shortcut.get('description', '')
        desc_html = f' <span class="shortcut-desc">({description[:25]}...)</span>' if len(description) > 25 else f' <span class="shortcut-desc">({description})</span>' if description else ''

        # Calculate background color inline for best QTextBrowser compatibility
        bg_color = "transparent"
        if is_selected:
            bg_color = "#4a5b6e" # Lighter blue for selection
        elif not enabled:
            bg_color = "#5a3434" # Lighter red for disabled

        text_style = 'style="color: #888;"' if not enabled else ""

        return f'''
        <div class="shortcut-item {indent_class}">
            <table width="100%" cellpadding="3" cellspacing="0" style="background-color: {bg_color}; border-radius: 5px; border-collapse: separate;">
                <tr>
                    <td width="40" valign="middle">
                        <a href="toggle://{shortcut_type}/{index}" style="text-decoration: none;">
                            <span class="{status_class}" style="font-size: 18px;">{status}</span>
                        </a>
                    </td>
                    <td valign="middle">
                        <a href="select://{shortcut_type}/{index}" style="text-decoration: none; color: inherit;">
                            <table cellpadding="0" cellspacing="0" width="100%">
                                <tr {text_style}>
                                    <td width="{key_width}" class="shortcut-key" valign="middle" style="white-space: nowrap;">{key}</td>
                                    <td width="{icon_width}" class="shortcut-separator" valign="middle" align="center">󰌌</td>
                                    <td style="padding-left: 15px;" class="shortcut-name" valign="middle">{name}{desc_html}</td>
                                </tr>
                            </table>
                        </a>
                    </td>
                </tr>
            </table>
        </div>
        '''

    def open_add_dialog(self, shortcut_type):
        dialog = AddEditShortcutDialog(self, shortcut_type)
        dialog.exec()

    def edit_selected(self):
        if not self.selected_shortcut or not self.selected_type:
            QMessageBox.warning(self, "Warning", "Please select a shortcut to edit.")
            return

        dialog = AddEditShortcutDialog(self, self.selected_type, self.selected_shortcut)
        dialog.exec()

    def duplicate_selected(self):
        if not self.selected_shortcut or not self.selected_type:
            QMessageBox.warning(self, "Warning", "Please select a shortcut to duplicate.")
            return

        # Create a copy of the selected shortcut
        import copy
        duplicated = copy.deepcopy(self.selected_shortcut)
        
        # Modify the name to indicate it's a copy
        original_name = duplicated.get('name', 'Unnamed')
        duplicated['name'] = f"{original_name} (Copy)"
        
        # For script and context shortcuts, clear the hotkey to avoid conflicts
        if self.selected_type in ["script", "context"]:
            duplicated['hotkey'] = ""
        # For text and file shortcuts, clear the trigger
        elif self.selected_type in ["text", "file"]:
            duplicated['trigger'] = ""
        
        # Add to the appropriate list
        if self.selected_type == "script":
            self.script_shortcuts.append(duplicated)
        elif self.selected_type == "context":
            self.context_shortcuts.append(duplicated)
        elif self.selected_type == "startup":
            self.startup_scripts.append(duplicated)
        elif self.selected_type == "file":
            self.file_shortcuts.append(duplicated)
        else:
            self.text_shortcuts.append(duplicated)
        
        # Save and update display
        self.save_shortcuts_json()
        self.update_display()
        
        # Select the new duplicate
        self.selected_shortcut = duplicated
        self.update_display()
        
        # Show success message
        QMessageBox.information(self, "Success", f"Duplicated '{original_name}' as '{duplicated['name']}'.\n\nPlease edit the duplicate to set a unique hotkey/trigger.")

    def remove_selected(self):
        if not self.selected_shortcut or not self.selected_type:
            QMessageBox.warning(self, "Warning", "Please select a shortcut to remove.")
            return

        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to remove this shortcut?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.selected_type == "script":
                self.script_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "context":
                self.context_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "startup":
                self.startup_scripts.remove(self.selected_shortcut)
            elif self.selected_type == "file":
                self.file_shortcuts.remove(self.selected_shortcut)
            else:
                self.text_shortcuts.remove(self.selected_shortcut)

            self.selected_shortcut = None
            self.selected_type = None
            self.save_shortcuts_json()
            self.update_display()

    def open_color_dialog(self):
        dialog = CategoryColorDialog(self)
        dialog.exec()

    def generate_ahk_script(self):
        try:
            output_lines = ["#Requires AutoHotkey v2.0", "#SingleInstance", "Persistent", ""]

            # Add helper function for fast pasting
            output_lines.extend([
                "Paste(text) {",
                "    Old := A_Clipboard",
                "    A_Clipboard := \"\"  ; Clear clipboard first",
                "    A_Clipboard := text",
                "    if !ClipWait(1)",
                "        return",
                "    SendInput \"^v\"",
                "    Sleep 250  ; Wait for paste to complete before restoring clipboard",
                "    A_Clipboard := Old",
                "}",
                "",
                "SetClipboardFiles(files) {",
                "    Static CF_HDROP := 15",
                "    If !IsObject(files)",
                "        files := [files]",
                "    ",
                "    size := 20",
                "    for file in files",
                "        size += (StrLen(file) + 1) * 2",
                "    size += 2",
                "    ",
                "    hGlobal := DllCall(\"GlobalAlloc\", \"uint\", 0x42, \"ptr\", size, \"ptr\")",
                "    pDrop := DllCall(\"GlobalLock\", \"ptr\", hGlobal, \"ptr\")",
                "    ",
                "    NumPut(\"uint\", 20, pDrop + 0)",
                "    NumPut(\"uint\", 1, pDrop + 16)",
                "    ",
                "    offset := 20",
                "    for file in files {",
                "        StrPut(file, pDrop + offset, \"UTF-16\")",
                "        offset += (StrLen(file) + 1) * 2",
                "    }",
                "    NumPut(\"ushort\", 0, pDrop + offset)",
                "    ",
                "    DllCall(\"GlobalUnlock\", \"ptr\", hGlobal)",
                "    DllCall(\"OpenClipboard\", \"ptr\", 0)",
                "    DllCall(\"EmptyClipboard\")",
                "    DllCall(\"SetClipboardData\", \"uint\", CF_HDROP, \"ptr\", hGlobal)",
                "    DllCall(\"CloseClipboard\")",
                "}",
                "",
                "PasteFile(filePath) {",
                "    ; Resolve relative path if it starts with @",
                "    if SubStr(filePath, 1, 1) = \"@\" {",
                "        pathOnly := SubStr(filePath, 2)",
                "        filePath := A_ScriptDir \"\\\" pathOnly",
                "    }",
                "    ",
                "    if !FileExist(filePath) {",
                "        ToolTip \"File not found: \" filePath",
                "        SetTimer () => ToolTip(), -3000",
                "        return",
                "    }",
                "    ",
                "    Old := ClipboardAll()",
                "    SetClipboardFiles(filePath)",
                "    Sleep 50  ; Wait for hotstring backspacing to finish",
                "    Send \"^v\"",
                "    Sleep 500",
                "    A_Clipboard := Old",
                "}",
                ""
            ])

            # Add Background/Startup Scripts at the top (Auto-execute section)
            enabled_startup = [s for s in self.startup_scripts if s.get('enabled', True)]
            if enabled_startup:
                output_lines.append(";! === BACKGROUND / STARTUP SCRIPTS ===")
                for shortcut in enabled_startup:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    action = shortcut.get('action', '')
                    # Cleanup parameters
                    action = action.replace(',,,', ',,')
                    
                    output_lines.append(action)
                    output_lines.append("")

            # Add script shortcuts
            enabled_scripts = [s for s in self.script_shortcuts if s.get('enabled', True)]
            if enabled_scripts:
                output_lines.append(";! === SCRIPT SHORTCUTS ===")
                for shortcut in enabled_scripts:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")

                    action = shortcut.get('action', '')
                    hotkey = shortcut.get('hotkey', '')

                    # Cleanup: Fix common "Too many parameters" error like Run("...", , , "Hide") 
                    # by reducing triple commas to double (v2 standard for skipping 1 param)
                    action = action.replace(',,,', ',,')

                    if '\n' in action:
                        output_lines.append(f"{hotkey}:: {{")
                        
                        # Smart Function Calling:
                        # Detect if the action starts with a function definition and call it if missing
                        lines = [l.strip() for l in action.split('\n') if l.strip()]
                        match = re.search(r"^\s*([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{", action, re.MULTILINE)
                        
                        if match and len(lines) > 0:
                            func_name = match.group(1)
                            # If first line is a definition and NO other line calls it, inject the call
                            if lines[0].startswith(f"{func_name}(") and not any(l.strip() == f"{func_name}()" for l in lines):
                                output_lines.append(f"    {func_name}()")
                                
                        for line in action.split('\n'):
                            if line.strip():
                                output_lines.append(f"    {line}")
                        output_lines.append("}")
                    else:
                        output_lines.append(f"{hotkey}::{action}")
                    output_lines.append("")

            # Add context shortcuts with #HotIf directives
            enabled_context = [s for s in self.context_shortcuts if s.get('enabled', True)]
            if enabled_context:
                output_lines.append(";! === CONTEXT SHORTCUTS ===")
                
                # Group by context to minimize #HotIf blocks
                for shortcut in enabled_context:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    # Generate context check function
                    window_title = shortcut.get('window_title', '')
                    process_name = shortcut.get('process_name', '')
                    window_class = shortcut.get('window_class', '')
                    
                    # Build condition
                    conditions = []
                    if process_name:
                        conditions.append(f'processName = "{process_name}"')
                    if window_title:
                        conditions.append(f'InStr(windowTitle, "{window_title}")')
                    if window_class:
                        conditions.append(f'windowClass = "{window_class}"')
                    
                    condition_str = " && ".join(conditions)
                    
                    # Generate unique function name
                    func_name = f"Is{shortcut.get('name', 'Context').replace(' ', '')}Context"
                    
                    output_lines.append(f"{func_name}() {{")
                    output_lines.append("    try {")
                    if process_name:
                        output_lines.append('        processName := WinGetProcessName("A")')
                    if window_title:
                        output_lines.append('        windowTitle := WinGetTitle("A")')
                    if window_class:
                        output_lines.append('        windowClass := WinGetClass("A")')
                    output_lines.append(f"        if ({condition_str}) {{")
                    output_lines.append("            return true")
                    output_lines.append("        }")
                    output_lines.append("    }")
                    output_lines.append("    return false")
                    output_lines.append("}")
                    output_lines.append("")
                    
                    # Add #HotIf directive
                    output_lines.append(f"#HotIf {func_name}()")
                    output_lines.append("")
                    
                    action = shortcut.get('action', '')
                    hotkey = shortcut.get('hotkey', '')
                    action = action.replace(',,,', ',,')
                    
                    if '\n' in action:
                        output_lines.append(f"{hotkey}:: {{")
                        for line in action.split('\n'):
                            if line.strip():
                                output_lines.append(f"    {line}")
                        output_lines.append("}")
                    else:
                        output_lines.append(f"{hotkey}::{action}")
                    output_lines.append("")
                    output_lines.append("#HotIf")
                    output_lines.append("")

            # Add enabled text shortcuts
            enabled_texts = [s for s in self.text_shortcuts if s.get('enabled', True)]
            if enabled_texts:
                output_lines.append(";! === TEXT SHORTCUTS ===")
                for shortcut in enabled_texts:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    replacement = shortcut.get('replacement', '')
                    trigger = shortcut.get('trigger', '')
                    
                    if '\n' in replacement:
                        # Multiline: Use AHK v2 continuation section (must use double quotes for string wrapper)
                        safe_replacement = replacement.replace('"', '""')
                        
                        output_lines.append(f":X:{trigger}::Paste(\"")
                        output_lines.append("(") 
                        
                        lines = safe_replacement.split('\n')
                        for line in lines:
                            # AHK v2 Continuation: escape lines starting with ) or , with backtick
                            # Although only ) is strictly needed for closing, safety first
                            if line.strip().startswith(")"):
                                output_lines.append("`" + line)
                            else:
                                output_lines.append(line)
                                
                        output_lines.append(")\")")
                    else:
                        # Single line: Use single quotes to robustly handle double quotes in content
                        safe_replacement = replacement.replace("'", "''")
                        output_lines.append(f":X:{trigger}::Paste('{safe_replacement}')")
                    output_lines.append("")

            # Add enabled file shortcuts
            enabled_files = [s for s in self.file_shortcuts if s.get('enabled', True)]
            if enabled_files:
                output_lines.append(";! === FILE SHORTCUTS ===")
                for shortcut in enabled_files:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    trigger = shortcut.get('trigger', '')
                    file_path = shortcut.get('file_path', '')
                    
                    # Escape single quotes in path
                    safe_path = file_path.replace("'", "''")
                    output_lines.append(f":X:{trigger}::PasteFile('{safe_path}')")
                    output_lines.append("")

            output_dir = r"C:\@delta\output\ahk"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "generated_shortcuts.ahk")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))

            self.statusBar().showMessage(f"🚀 Success: AHK script generated as '{output_file}'", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate AHK script: {e}")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look

    window = AHKShortcutEditor()
    # Font is applied inside AHKShortcutEditor via load_shortcuts_json -> apply_global_font
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
