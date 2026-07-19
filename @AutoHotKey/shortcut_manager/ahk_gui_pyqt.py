import sys
import json
import os
import re
import urllib.request
import webbrowser
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

# SVG Collection
SVGS = {
    "PLUS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>',
    "SETTINGS": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>',
    "PALETTE": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a10 10 0 0 0-10 10c0 5.52 4.48 10 10 10a2 2 0 0 0 2-2 2 2 0 0 0-2-2H10a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2 10 10 0 0 0-10-10z"></path><circle cx="7.5" cy="10.5" r=".5"></circle><circle cx="10.5" cy="7.5" r=".5"></circle><circle cx="13.5" cy="7.5" r=".5"></circle><circle cx="16.5" cy="10.5" r=".5"></circle></svg>',
    "RESTART": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>',
    "ROCKET": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path><path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>'
}

class CyberButton(QPushButton):
    """Modern button with SVG icon support and dynamic hover color-switching."""
    def __init__(self, text="", parent=None, color=CP_DIM, is_outlined=False, svg_data=None):
        super().__init__(text, parent)
        self.color = color
        self.is_outlined = is_outlined
        self.svg_data = svg_data
        self.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)
        if svg_data:
            self.update_icon(CP_TEXT if self.color == CP_DIM else CP_BG)
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
            self.update_icon(CP_YELLOW if self.color == CP_DIM else self.color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.svg_data:
            self.update_icon(CP_TEXT if self.color == CP_DIM else CP_BG)
        super().leaveEvent(event)

    def update_style(self):
        # Match guide: Dark gray buttons highlight yellow on hover
        if self.color == CP_DIM:
            self.setStyleSheet(f"""
                QPushButton {{ background-color: {CP_DIM}; color: white; border: 1px solid {CP_DIM}; padding: 6px 12px; border-radius: 0px; }}
                QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
                QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
            """)
        else:
            # Special accent buttons (Add, Generate) still use their specific colors but with sharp corners
            self.setStyleSheet(f"""
                QPushButton {{ background-color: {self.color}; color: {CP_BG}; border: none; padding: 6px 12px; border-radius: 0px; }}
                QPushButton:hover {{ background-color: {CP_BG}; color: {self.color}; border: 1px solid {self.color}; }}
            """)

class ShortcutBuilderPopup(QDialog):
    # AHK modifier symbols: generic, left-specific, right-specific
    # mods dict keys are the AHK prefix strings
    MOD_DEFS = [
        # (generic_sym, left_sym, right_sym, display_name)
        ("^",  "<^", ">^", "Ctrl"),
        ("!",  "<!", ">!", "Alt"),
        ("+",  "<+", ">+", "Shift"),
        ("#",  "<#", ">#", "Win"),
    ]

    KB_ROWS = [
        ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
        ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
        ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
        ["CapsLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
    ]

    KEY_STYLE = """
        QPushButton {{
            background: {bg};
            color: {fg};
            border: 2px solid {border};
            border-radius: 0px;
            font-family: '{font}';
            font-size: 11px;
            font-weight: normal;
            padding: 0px 3px;
            min-height: {h}px;
            min-width: {w}px;
        }}
        QPushButton:hover {{ background: {hover_bg}; border-color: {hover_border}; color: {hover_fg}; }}
        QPushButton:pressed {{ background: {pressed_bg}; }}
    """
    KEY_STYLE_ACTIVE = """
        QPushButton {{
            background: {bg}; color: {fg};
            border: 2px solid {border}; border-radius: 0px;
            font-family: '{font}';
            font-size: 11px; font-weight: normal;
            padding: 0px 3px;
            min-height: {h}px; min-width: {w}px;
        }}
    """
    MOD_STYLE = """
        QPushButton {{
            background: {bg}; color: {fg};
            border: {border}; border-radius: 0px;
            font-family: '{font}';
            font-size: {font_size}px; font-weight: normal;
            padding: 0px 6px;
            min-height: {h}px;
            min-width: {w}px;
        }}
        QPushButton:hover {{ background: {hover_bg}; border: {hover_border}; color: {hover_fg}; }}
    """

    THEMES = {
        "cyberpunk": {
            "win_bg": "#1a1a2e", "win_fg": "#e0e0e0",
            "key_inactive_bg": "#252540", "key_inactive_fg": "#c8d0e0", "key_inactive_border": "#55556a",
            "key_active_bg": "#61dafb", "key_active_fg": "#1a1a2e", "key_active_border": "#61dafb",
            "mod_active_bg": "#61dafb", "mod_active_fg": "#1a1a2e", "mod_active_border": "2px solid #61dafb",
            "mod_inactive_bg": "#1e1e38", "mod_inactive_fg": "#8090a8", "mod_inactive_border": "2px solid #55556a",
            "preview_bg": "#0d0d1a", "preview_border": "1px solid #2a2a4a", "preview_fg": "#61dafb",
            "kb_frame_bg": "#12122a", "lbl_fg": "#505070",
            "cancel_style": "QPushButton { background: #1e1e38; color: #a0a0b0; border: 1px solid #55556a; border-radius: 0px; padding: 8px 18px; } QPushButton:hover { background: #55556a; color: white; }",
            "ok_style": "QPushButton { background: #61dafb; color: #1a1a2e; border-radius: 0px; padding: 8px 24px; font-weight: bold; } QPushButton:hover { background: #4ac8e8; }",
            "key_hover_bg": "#3a4a5a", "key_hover_border": "#61dafb", "key_hover_fg": "#61dafb",
            "key_pressed_bg": "#4a90d9",
            "mod_hover_bg": "#3a4a5a", "mod_hover_border": "2px solid #61dafb", "mod_hover_fg": "#61dafb",
        },
        "black_white": {
            "win_bg": "#000000", "win_fg": "#ffffff",
            "key_inactive_bg": "#1a1a1a", "key_inactive_fg": "#dddddd", "key_inactive_border": "#444444",
            "key_active_bg": "#ffffff", "key_active_fg": "#000000", "key_active_border": "#ffffff",
            "mod_active_bg": "#ffffff", "mod_active_fg": "#000000", "mod_active_border": "2px solid #ffffff",
            "mod_inactive_bg": "#222222", "mod_inactive_fg": "#cccccc", "mod_inactive_border": "2px solid #444444",
            "preview_bg": "#000000", "preview_border": "1px solid #ffffff", "preview_fg": "#ffffff",
            "kb_frame_bg": "#111111", "lbl_fg": "#888888",
            "cancel_style": "QPushButton { background: #222222; color: #cccccc; border: 1px solid #444444; border-radius: 0px; padding: 8px 18px; } QPushButton:hover { background: #444444; color: white; }",
            "ok_style": "QPushButton { background: #ffffff; color: #000000; border-radius: 0px; padding: 8px 24px; font-weight: bold; } QPushButton:hover { background: #e0e0e0; }",
            "key_hover_bg": "#333333", "key_hover_border": "#ffffff", "key_hover_fg": "#ffffff",
            "key_pressed_bg": "#555555",
            "mod_hover_bg": "#333333", "mod_hover_border": "2px solid #ffffff", "mod_hover_fg": "#ffffff",
        },
        "white_black": {
            "win_bg": "#ffffff", "win_fg": "#000000",
            "key_inactive_bg": "#f0f0f0", "key_inactive_fg": "#222222", "key_inactive_border": "#cccccc",
            "key_active_bg": "#000000", "key_active_fg": "#ffffff", "key_active_border": "#000000",
            "mod_active_bg": "#000000", "mod_active_fg": "#ffffff", "mod_active_border": "2px solid #000000",
            "mod_inactive_bg": "#dddddd", "mod_inactive_fg": "#333333", "mod_inactive_border": "2px solid #cccccc",
            "preview_bg": "#ffffff", "preview_border": "1px solid #000000", "preview_fg": "#000000",
            "kb_frame_bg": "#e6e6e6", "lbl_fg": "#666666",
            "cancel_style": "QPushButton { background: #dddddd; color: #333333; border: 1px solid #cccccc; border-radius: 0px; padding: 8px 18px; } QPushButton:hover { background: #cccccc; color: black; }",
            "ok_style": "QPushButton { background: #000000; color: #ffffff; border-radius: 0px; padding: 8px 24px; font-weight: bold; } QPushButton:hover { background: #222222; }",
            "key_hover_bg": "#e0e0e0", "key_hover_border": "#000000", "key_hover_fg": "#000000",
            "key_pressed_bg": "#aaaaaa",
            "mod_hover_bg": "#e0e0e0", "mod_hover_border": "2px solid #000000", "mod_hover_fg": "#000000",
        }
    }

    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.setWindowTitle("⌨  Shortcut Builder")
        self.setModal(True)
        
        # Load theme & font settings
        settings = QSettings("AHKEditor", "ShortcutEditor")
        self.theme_name = settings.value("shortcut_builder_theme", "cyberpunk")
        self.t_config = self.THEMES.get(self.theme_name, self.THEMES["cyberpunk"])
        self.builder_font_family = settings.value("shortcut_builder_font", "Consolas")
        
        self.setStyleSheet(f"QDialog {{ background: {self.t_config['win_bg']}; color: {self.t_config['win_fg']}; }}")
        self.setFont(QFont(self.builder_font_family, 10))
        # mods: key = ahk prefix string (e.g. "^", "<^", ">^"), value = bool
        all_syms = [s for d in self.MOD_DEFS for s in (d[0], d[1], d[2])]
        self.mods = {s: False for s in all_syms}
        self.main_key = ""
        self._key_buttons = {}
        self._mod_buttons = {s: [] for s in all_syms}  # sym -> list of QPushButton
        self.parse_initial(initial_value)
        self.setup_ui()

    def parse_initial(self, value):
        if not value: return
        # Try longest prefixes first (<^, >^, etc.)
        for d in self.MOD_DEFS:
            for sym in (d[1], d[2], d[0]):
                if value.startswith(sym):
                    self.mods[sym] = True
                    value = value[len(sym):]
                    break
        self.main_key = value

    # ── Key button ────────────────────────────────────────────────────
    def _key_btn(self, label, width=34, expand=False, height=32):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if expand:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        elif width > 0:
            btn.setFixedWidth(width)
        active = (label.lower() == self.main_key.lower())
        btn.setChecked(active)
        # Store original custom width & height on button object to prevent style degradation on action
        btn.custom_width = 0 if (expand or width == 0) else width
        btn.custom_height = height
        self._apply_key_style(btn, active)
        btn.clicked.connect(lambda _, k=label: self.select_key(k))
        self._key_buttons[label] = btn
        return btn

    def _apply_key_style(self, btn, active):
        # Retrieve the custom width & height assigned during creation
        w = getattr(btn, "custom_width", 34)
        h = getattr(btn, "custom_height", 32)
        if active:
            btn.setStyleSheet(self.KEY_STYLE_ACTIVE.format(
                bg=self.t_config["key_active_bg"],
                fg=self.t_config["key_active_fg"],
                border=self.t_config["key_active_border"],
                font=self.builder_font_family,
                h=h,
                w=w
            ))
        else:
            btn.setStyleSheet(self.KEY_STYLE.format(
                bg=self.t_config["key_inactive_bg"],
                fg=self.t_config["key_inactive_fg"],
                border=self.t_config["key_inactive_border"],
                hover_bg=self.t_config["key_hover_bg"],
                hover_border=self.t_config["key_hover_border"],
                hover_fg=self.t_config["key_hover_fg"],
                pressed_bg=self.t_config["key_pressed_bg"],
                font=self.builder_font_family,
                h=h,
                w=w
            ))

    # ── Modifier button ───────────────────────────────────────────────
    def _mod_btn(self, sym, label, width=52, expand=False, height=36, font_size=13):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setChecked(self.mods[sym])
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if expand:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        elif width > 0:
            btn.setFixedWidth(width)
        btn.custom_height = height
        btn.custom_font_size = font_size
        self._apply_mod_style(btn, self.mods[sym])
        btn.toggled.connect(lambda checked, s=sym: self.toggle_mod(s, checked))
        self._mod_buttons[sym].append(btn)
        return btn

    def _apply_mod_style(self, btn, active):
        h = getattr(btn, "custom_height", 36)
        fs = getattr(btn, "custom_font_size", 13)
        if active:
            btn.setStyleSheet(self.MOD_STYLE.format(
                bg=self.t_config["mod_active_bg"],
                fg=self.t_config["mod_active_fg"],
                border=self.t_config["mod_active_border"],
                hover_bg=self.t_config["mod_hover_bg"],
                hover_border=self.t_config["mod_hover_border"],
                hover_fg=self.t_config["mod_hover_fg"],
                font=self.builder_font_family,
                font_size=fs,
                h=h,
                w=0
            ))
        else:
            btn.setStyleSheet(self.MOD_STYLE.format(
                bg=self.t_config["mod_inactive_bg"],
                fg=self.t_config["mod_inactive_fg"],
                border=self.t_config["mod_inactive_border"],
                hover_bg=self.t_config["mod_hover_bg"],
                hover_border=self.t_config["mod_hover_border"],
                hover_fg=self.t_config["mod_hover_fg"],
                font=self.builder_font_family,
                font_size=fs,
                h=h,
                w=0
            ))

    def toggle_mod(self, sym, state):
        self.mods[sym] = state
        # If a specific side is turned on, turn off generic; if generic turned on, turn off both sides
        generic_sym = next((d[0] for d in self.MOD_DEFS if sym in (d[0], d[1], d[2])), None)
        left_sym = next((d[1] for d in self.MOD_DEFS if sym in (d[0], d[1], d[2])), None)
        right_sym = next((d[2] for d in self.MOD_DEFS if sym in (d[0], d[1], d[2])), None)
        if state:
            if sym == generic_sym:
                self._set_mod(left_sym, False); self._set_mod(right_sym, False)
            else:
                self._set_mod(generic_sym, False)
        # Sync all buttons for this sym
        for btn in self._mod_buttons[sym]:
            btn.blockSignals(True); btn.setChecked(state); self._apply_mod_style(btn, state); btn.blockSignals(False)
        self.update_preview()

    def _set_mod(self, sym, state):
        if sym is None: return
        self.mods[sym] = state
        for btn in self._mod_buttons[sym]:
            btn.blockSignals(True); btn.setChecked(state); self._apply_mod_style(btn, state); btn.blockSignals(False)

    def select_key(self, key):
        if self.main_key and self.main_key in self._key_buttons:
            old = self._key_buttons[self.main_key]
            old.setChecked(False); self._apply_key_style(old, False)
        self.main_key = "" if key == self.main_key else key
        if self.main_key:
            btn = self._key_buttons.get(self.main_key)
            if btn: btn.setChecked(True); self._apply_key_style(btn, True)
        self.update_preview()

    def update_preview(self):
        self.preview_label.setText(self.get_formatted_preview())

    def get_formatted_preview(self):
        parts = []
        name_map = {}
        for d in self.MOD_DEFS:
            name_map[d[0]] = d[3]; name_map[d[1]] = f"L{d[3]}"; name_map[d[2]] = f"R{d[3]}"
        for sym in ["<^", ">^", "^", "<!", ">!", "!", "<+", ">+", "+", "<#", ">#", "#"]:
            if self.mods.get(sym): parts.append(name_map[sym])
        parts.append(self.main_key if self.main_key else "?")
        return "  +  ".join(parts)

    def get_final_ahk(self):
        res = ""
        for sym in ["<^", ">^", "^", "<!", ">!", "!", "<+", ">+", "+", "<#", ">#", "#"]:
            if self.mods.get(sym): res += sym
        res += self.main_key
        return res

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # ── Preview ───────────────────────────────────────────────────
        preview_frame = QFrame()
        preview_frame.setStyleSheet(f"background: {self.t_config['preview_bg']}; border-radius: 0px; border: {self.t_config['preview_border']};")
        pf = QVBoxLayout(preview_frame); pf.setContentsMargins(10, 8, 10, 8)
        self.preview_label = QLabel(self.get_formatted_preview())
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"font-family: '{self.builder_font_family}'; font-size: 20px; font-weight: bold; color: {self.t_config['preview_fg']}; letter-spacing: 2px; background: transparent; border: none;")
        pf.addWidget(self.preview_label)
        layout.addWidget(preview_frame)

        # ── Keyboard ──────────────────────────────────────────────────
        kb_frame = QFrame()
        kb_frame.setStyleSheet(f"background: {self.t_config['kb_frame_bg']}; border-radius: 10px; padding: 6px;")
        kb_layout = QVBoxLayout(kb_frame)
        kb_layout.setSpacing(4)

        # row index -> index of key that should expand to fill remaining space
        expand_key = {1: 13, 2: 13, 3: 12, 4: 999}  # Backspace, \, Enter, RShift Custom Expand

        row_widths = [
            {0: 40},           # Esc wider
            {13: 68},          # Backspace wider
            {0: 52, 13: 44},   # Tab, backslash
            {0: 58, 12: 68},   # CapsLock, Enter
            {},                # bottom letter row
        ]
        for ri, (keys, overrides) in enumerate(zip(self.KB_ROWS, row_widths)):
            rw = QWidget(); rl = QHBoxLayout(rw); rl.setSpacing(4); rl.setContentsMargins(0,0,0,0)
            if ri == 4:
                rl.addWidget(self._mod_btn("<+", "LShift", 80, height=36, font_size=13))
            for i, k in enumerate(keys):
                should_expand = (expand_key.get(ri) == i)
                rl.addWidget(self._key_btn(k, overrides.get(i, 34), expand=should_expand))
            if ri == 4:
                rl.addWidget(self._mod_btn(">+", "RShift", width=0, expand=True, height=36, font_size=13))
            if ri not in expand_key:
                rl.addStretch(1)
            kb_layout.addWidget(rw)

        # ── Space bar row with L/R modifiers ─────────────────────────
        space_row = QWidget()
        sr = QHBoxLayout(space_row); sr.setSpacing(4); sr.setContentsMargins(0,0,0,0)

        # Left side: LCtrl, LWin, LAlt
        for sym, label in [("<^","LCtrl"), ("<#","LWin"), ("<!","LAlt")]:
            sr.addWidget(self._mod_btn(sym, label, 60))

        sr.addWidget(self._key_btn("Space", 240, height=36))

        # Right side: RAlt, RWin, RCtrl
        for sym, label in [(">!","RAlt"), (">#","RWin"), (">^","RCtrl")]:
            sr.addWidget(self._mod_btn(sym, label, 60))

        kb_layout.addWidget(space_row)

        # ── Nav cluster ───────────────────────────────────────────────
        nav_frame = QFrame()
        nav_frame.setStyleSheet("background: transparent;")
        nav_v = QVBoxLayout(nav_frame); nav_v.setSpacing(4); nav_v.setContentsMargins(0,0,0,0)
        nav_groups = [
            [["PrintScreen","ScrollLock","Pause"]],
            [["Insert","Home","PgUp"], ["Delete","End","PgDn"]],
            [["","Up",""], ["Left","Down","Right"]],
        ]
        for gi, group in enumerate(nav_groups):
            if gi == 2:
                nav_v.addStretch(1)
            elif gi > 0:
                nav_v.addSpacing(12)
            for row in group:
                rw = QWidget(); rl = QHBoxLayout(rw); rl.setSpacing(4); rl.setContentsMargins(0,0,0,0)
                for k in row:
                    if k == "":
                        sp = QWidget(); sp.setFixedWidth(44); rl.addWidget(sp)
                    else:
                        nav_labels = {"PrintScreen":"PrtSc","ScrollLock":"ScrLk",
                                      "Up":"↑","Down":"↓","Left":"←","Right":"→"}
                        btn = self._key_btn(k, 44)
                        if k in nav_labels: btn.setText(nav_labels[k])
                        rl.addWidget(btn)
                nav_v.addWidget(rw)

        # ── Numpad cluster ────────────────────────────────────────────
        numpad_frame = QFrame()
        numpad_frame.setStyleSheet(f"background: {self.t_config['kb_frame_bg']}; border-radius: 8px; padding: 4px;")
        numpad_frame.setMinimumWidth(180)
        num_v = QVBoxLayout(numpad_frame); num_v.setSpacing(4); num_v.setContentsMargins(4,4,4,4)
        lbl_np = QLabel("Numpad"); lbl_np.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_np.setStyleSheet(f"color: {self.t_config['lbl_fg']}; font-size:10px; margin-bottom:2px;")
        num_v.addWidget(lbl_np)

        from PyQt6.QtWidgets import QGridLayout
        grid_w = QWidget()
        grid = QGridLayout(grid_w); grid.setSpacing(4); grid.setContentsMargins(0,0,0,0)
        for r in range(5): grid.setRowStretch(r, 1)
        for c in range(4): grid.setColumnStretch(c, 1)

        def _np(k, display):
            btn = self._key_btn(k, 0); btn.setText(display)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            return btn

        def _np_tall(k, display):
            btn = self._key_btn(k, 0); btn.setText(display)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.setStyleSheet(btn.styleSheet() + " qproperty-alignment: AlignCenter;")
            return btn

        def _np_wide(k, display):
            btn = self._key_btn(k, 0); btn.setText(display)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            return btn

        # row 0: NmLk / * -
        grid.addWidget(_np("NumLock","NmLk"),  0,0)
        grid.addWidget(_np("NumpadDiv","/"),   0,1)
        grid.addWidget(_np("NumpadMult","*"),  0,2)
        grid.addWidget(_np("NumpadSub","-"),   0,3)
        # row 1: 7 8 9  |+| spans rows 1-2
        grid.addWidget(_np("Numpad7","7"),     1,0)
        grid.addWidget(_np("Numpad8","8"),     1,1)
        grid.addWidget(_np("Numpad9","9"),     1,2)
        plus_btn = _np("NumpadAdd","+")
        plus_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        plus_btn.setStyleSheet(plus_btn.styleSheet().replace("min-height: 32px;", "min-height: 32px; padding: 0px;"))
        grid.addWidget(plus_btn, 1,3, 2,1)
        # row 2: 4 5 6
        grid.addWidget(_np("Numpad4","4"),     2,0)
        grid.addWidget(_np("Numpad5","5"),     2,1)
        grid.addWidget(_np("Numpad6","6"),     2,2)
        # row 3: 1 2 3  |Ent| spans rows 3-4
        grid.addWidget(_np("Numpad1","1"),     3,0)
        grid.addWidget(_np("Numpad2","2"),     3,1)
        grid.addWidget(_np("Numpad3","3"),     3,2)
        ent_btn = _np("NumpadEnter","Ent")
        ent_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        ent_btn.setStyleSheet(ent_btn.styleSheet().replace("min-height: 32px;", "min-height: 32px; padding: 0px;"))
        grid.addWidget(ent_btn, 3,3, 2,1)
        # row 4: 0 (wide) .
        grid.addWidget(_np_wide("Numpad0","0"), 4,0, 1,2)
        grid.addWidget(_np("NumpadDot","."),   4,2)

        num_v.addWidget(grid_w)

        # Keyboard + nav + numpad side by side
        kb_nav = QHBoxLayout(); kb_nav.setSpacing(10)
        kb_nav.addWidget(kb_frame); kb_nav.addWidget(nav_frame); kb_nav.addWidget(numpad_frame)
        layout.addLayout(kb_nav)

        # ── Generic modifier strip with OK / Cancel Actions ───────────
        gmod_frame = QFrame()
        gmod_frame.setStyleSheet(f"background: {self.t_config['kb_frame_bg']}; border-radius: 8px; padding: 4px;")
        gmod_l = QHBoxLayout(gmod_frame); gmod_l.setSpacing(6)
        
        lbl = QLabel("Any side:"); lbl.setStyleSheet(f"color: {self.t_config['lbl_fg']}; font-size:11px;")
        gmod_l.addWidget(lbl)
        for sym, _, _, name in self.MOD_DEFS:
            gmod_l.addWidget(self._mod_btn(sym, name, 64))
            
        gmod_l.addStretch(1)
        
        # Right-aligned Cancel and Apply buttons
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.t_config["cancel_style"] + f" QPushButton {{ font-family: '{self.builder_font_family}'; }}")
        ok_btn = QPushButton("  ✓  Apply")
        ok_btn.setStyleSheet(self.t_config["ok_style"] + f" QPushButton {{ font-family: '{self.builder_font_family}'; }}")
        ok_btn.clicked.connect(self.accept); cancel_btn.clicked.connect(self.reject)
        
        # Match standard modifier button height
        cancel_btn.setFixedHeight(36)
        ok_btn.setFixedHeight(36)
        
        gmod_l.addWidget(cancel_btn)
        gmod_l.addWidget(ok_btn)
        
        layout.addWidget(gmod_frame)
        self.adjustSize()

    def filter_keys(self, text): pass  # compat stub

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

# ── Windows System Defaults Database ──────────────────────────────
WINDOWS_DEFAULTS = [
    {"hotkey": "#e", "name": "Open File Explorer", "description": "Launches the Windows File Explorer", "action": 'Run("explorer.exe")'},
    {"hotkey": "#i", "name": "Open Settings", "description": "Launches the Windows Settings app", "action": 'Run("ms-settings:")'},
    {"hotkey": "#p", "name": "Project Settings / Projection", "description": "Opens the display projection sidebar", "action": 'Run("DisplaySwitch.exe")'},
    {"hotkey": "#+s", "name": "Snipping Tool / Screen Snip", "description": "Initiates a screenshot crop using Snipping Tool", "action": 'Run("ms-screenclip:")'},
    {"hotkey": "#k", "name": "Cast Settings", "description": "Opens the Cast connect flyout", "action": 'Run("ms-settings-connectabledevices:cast")'},
    {"hotkey": "#a", "name": "Action Center / Quick Settings", "description": "Opens the Quick Settings flyout", "action": 'Send("#a")'},
    {"hotkey": "#v", "name": "Clipboard History", "description": "Launches the system clipboard history menu", "action": 'Send("#v")'},
    {"hotkey": "^+Esc", "name": "Task Manager", "description": "Launches the system Task Manager", "action": 'Run("taskmgr.exe")'},
    {"hotkey": "#l", "name": "Lock Computer", "description": "Instantly locks the Windows session", "action": 'DllCall("LockWorkStation")'},
    {"hotkey": "#d", "name": "Toggle Show Desktop", "description": "Minimizes or restores all open windows", "action": 'WinMinimizeAll()'},
    {"hotkey": "#x", "name": "Quick Link / WinX Menu", "description": "Opens the power user start menu", "action": 'Send("#x")'},
    {"hotkey": "#r", "name": "Run Dialog", "description": "Opens the Run command box", "action": 'Send("#r")'},
]

class WindowsDefaultLookupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Windows Default Shortcut")
        self.resize(600, 450)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: white; }
            QLineEdit { background-color: #2d2d2d; color: white; border: 1px solid #444; padding: 6px; }
            QListWidget { background-color: #2b2b2b; color: #e0e0e0; border: 1px solid #444; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #3a3a3a; }
            QListWidget::item:selected { background-color: #00F0FF; color: black; }
        """)
        self.selected_item = None
        self.setup_ui()
        self.populate_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search default shortcuts (e.g., explorer, settings, snip)...")
        self.search_edit.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_edit)
        
        from PyQt6.QtWidgets import QListWidget
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept_selection)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def populate_list(self):
        from PyQt6.QtWidgets import QListWidgetItem
        self.list_widget.clear()
        for item in WINDOWS_DEFAULTS:
            hk_str = item["hotkey"]
            pretty_parts = []
            i = 0
            while i < len(hk_str):
                char = hk_str[i]
                if char == "#":
                    pretty_parts.append("Win")
                    i += 1
                elif char == "^":
                    pretty_parts.append("Ctrl")
                    i += 1
                elif char == "!":
                    pretty_parts.append("Alt")
                    i += 1
                elif char == "+":
                    pretty_parts.append("Shift")
                    i += 1
                else:
                    pretty_parts.append(hk_str[i:])
                    break
            pretty_hk = "+".join(pretty_parts)
            display_text = f"{pretty_hk}  ➔  {item['name']}\n{item['description']}"
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.list_widget.addItem(list_item)

    def filter_list(self, text):
        query = text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            match = (query in data["name"].lower() or 
                     query in data["description"].lower() or 
                     query in data["hotkey"].lower() or 
                     query in item.text().lower())
            item.setHidden(not match)

    def accept_selection(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_item = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()
        else:
            self.reject()


class AddEditShortcutDialog(QDialog):
    def __init__(self, parent, shortcut_type, shortcut_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.shortcut_type = shortcut_type
        self.shortcut_data = shortcut_data

        title_map = {
            "script": "Script Shortcut",
            "context": "Context Shortcut",
            "startup": "Background Script",
            "text": "Text Shortcut",
            "file": "File Shortcut",
            "exclude": "Exclusion Rule",
            "remap": "Key Remap",
            "launcher": "Launcher Shortcut"
        }
        pretty_type = title_map.get(shortcut_type, shortcut_type.capitalize())
        self.setWindowTitle(f"{'Edit' if shortcut_data else 'Add'} {pretty_type}")
        self.setModal(True)
        self.resize(800, 550)
        self.setStyleSheet(f"""
            QDialog {{ background-color: #1e1e1e; color: white; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 0px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
        """)

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
        form_layout.setSpacing(10)
        
        # Row layout helper to place label and field together horizontally
        def _add_row(label_text, widget_or_layout):
            from PyQt6.QtWidgets import QLayout
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet(f"color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold;")
            lbl.setFixedWidth(90)
            row.addWidget(lbl)
            if isinstance(widget_or_layout, QLayout):
                row.addLayout(widget_or_layout)
            else:
                row.addWidget(widget_or_layout)
            form_layout.addLayout(row)

        # ── Initialize Input Fields ───────────────────────────────────
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Open Terminal, Version 1 Text")
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        existing_categories = self.get_existing_categories()
        self.category_combo.addItems(existing_categories)
        self.category_combo.setCurrentText("General")
        
        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Brief description of what this does")
        
        # Enabled checkbox styled exactly like other options for consistent alignment
        self.enabled_checkbox = QCheckBox("Enable Shortcut")
        self.enabled_checkbox.setChecked(True)
        self.enabled_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-family: 'Consolas', 'Segoe UI', sans-serif;
                font-size: 11pt;
                color: {CP_TEXT};
                spacing: 8px;
            }}
        """)

        self.favourite_checkbox = QCheckBox("⭐ Favourite")
        self.favourite_checkbox.setChecked(False)
        self.favourite_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-family: 'Consolas', 'Segoe UI', sans-serif;
                font-size: 11pt;
                color: {CP_YELLOW};
                spacing: 8px;
            }}
        """)

        # Common template helper style for standard recording buttons
        record_style = """
            QPushButton {
                font-family: inherit;
                background-color: #cc2222;
                border: none;
                border-radius: 13px;
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
        """

        # ── Build Layout Fields Sequentially (Flowing Downward) ───────

        # 1. Name Row
        _add_row("Name:", self.name_edit)

        # 2. Shortcut/Trigger Row (Placement immediately below Name)
        if self.shortcut_type in ["script", "context", "launcher"]:
            hotkey_row = QHBoxLayout()
            self.hotkey_edit = HotkeyLineEdit()
            self.hotkey_edit.setPlaceholderText("e.g., !Space, ^!n, #x")
            
            self.record_hotkey_btn = QPushButton("")
            self.record_hotkey_btn.setCheckable(True)
            self.record_hotkey_btn.setFixedSize(26,26)
            self.record_hotkey_btn.setStyleSheet(record_style)
            self.record_hotkey_btn.setToolTip("Open Shortcut Builder")
            self.record_hotkey_btn.clicked.connect(lambda checked: self.hotkey_edit.set_recording(checked))
            self.hotkey_edit.record_button = self.record_hotkey_btn
            
            hotkey_row.addWidget(self.hotkey_edit)
            hotkey_row.addWidget(self.record_hotkey_btn)
            _add_row("Hotkey:", hotkey_row)
            
        elif self.shortcut_type in ["text", "file"]:
            self.trigger_edit = QLineEdit()
            placeholder = "e.g., ;theme, ;file" if self.shortcut_type == "file" else "e.g., ;v1, ;run"
            self.trigger_edit.setPlaceholderText(placeholder)
            _add_row("Trigger:", self.trigger_edit)
            
        elif self.shortcut_type == "remap":
            # Origin Key
            origin_row = QHBoxLayout()
            self.origin_key_edit = HotkeyLineEdit()
            self.origin_key_edit.setPlaceholderText("e.g., CapsLock, F1, ScrollLock")
            
            self.record_origin_btn = QPushButton("")
            self.record_origin_btn.setCheckable(True)
            self.record_origin_btn.setFixedSize(26,26)
            self.record_origin_btn.setStyleSheet(record_style)
            self.record_origin_btn.setToolTip("Open Shortcut Builder")
            self.record_origin_btn.clicked.connect(lambda checked: self.origin_key_edit.set_recording(checked))
            self.origin_key_edit.record_button = self.record_origin_btn
            
            origin_row.addWidget(self.origin_key_edit)
            origin_row.addWidget(self.record_origin_btn)
            _add_row("Origin Key:", origin_row)

            # Destination Key
            dest_row = QHBoxLayout()
            self.destination_key_edit = HotkeyLineEdit()
            self.destination_key_edit.setPlaceholderText("e.g., Backspace, Mute, PageUp")
            
            self.record_dest_btn = QPushButton("")
            self.record_dest_btn.setCheckable(True)
            self.record_dest_btn.setFixedSize(26,26)
            self.record_dest_btn.setStyleSheet(record_style)
            self.record_dest_btn.setToolTip("Open Shortcut Builder")
            self.record_dest_btn.clicked.connect(lambda checked: self.destination_key_edit.set_recording(checked))
            self.destination_key_edit.record_button = self.record_dest_btn
            
            dest_row.addWidget(self.destination_key_edit)
            dest_row.addWidget(self.record_dest_btn)
            _add_row("Dest Key:", dest_row)

        # 3. Category Row (Including nested "🔍 Defaults" selector side-by-side)
        cat_row_layout = QHBoxLayout()
        cat_row_layout.addWidget(self.category_combo)
        if self.shortcut_type in ["script", "context"]:
            self.import_default_btn = QPushButton("🔍 Defaults")
            self.import_default_btn.setFixedWidth(120)
            self.import_default_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {CP_PANEL};
                    border: 1px solid {CP_DIM};
                    color: {CP_CYAN};
                    padding: 6px;
                    font-family: 'Consolas';
                    font-weight: bold;
                    border-radius: 0px;
                }}
                QPushButton:hover {{
                    background-color: {CP_CYAN};
                    color: black;
                }}
            """)
            self.import_default_btn.clicked.connect(self.import_windows_default)
            cat_row_layout.addWidget(self.import_default_btn)
        _add_row("Category:", cat_row_layout)

        # 4. Description Row
        _add_row("Description:", self.description_edit)

        # ── Extra Type-Specific Rows ──
        if self.shortcut_type in ["file", "launcher"]:
            file_row = QHBoxLayout()
            self.file_path_edit = QLineEdit()
            if self.shortcut_type == "file":
                self.file_path_edit.setPlaceholderText("C:\\path\\to\\file.ext or @..\\path")
            else:
                self.file_path_edit.setPlaceholderText("e.g., C:\\path\\to\\script.py, C:\\Windows\\notepad.exe")
            self.browse_btn = QPushButton("Browse")
            from PyQt6.QtWidgets import QFileDialog
            self.browse_btn.clicked.connect(self.browse_file)
            file_row.addWidget(self.file_path_edit)
            file_row.addWidget(self.browse_btn)
            _add_row("Target Path:" if self.shortcut_type == "launcher" else "File Path:", file_row)
            
        elif self.shortcut_type == "startup":
            self.startup_context_mode = QComboBox()
            self.startup_context_mode.addItems(["No context (always run)", "Active in (only these windows)", "Inactive in (exclude these windows)"])
            _add_row("Ctx Mode:", self.startup_context_mode)

        # ── Toggle Buttons (Placed neatly at the bottom) ──────────────
        form_layout.addSpacing(10)
        form_layout.addWidget(self.enabled_checkbox)
        form_layout.addWidget(self.favourite_checkbox)

        if self.shortcut_type == "launcher":
            self.hide_terminal_checkbox = QCheckBox("Hide Terminal Window")
            self.hide_terminal_checkbox.setChecked(True)
            self.hide_terminal_checkbox.setStyleSheet(f"""
                QCheckBox {{
                    font-family: 'Consolas', 'Segoe UI', sans-serif;
                    font-size: 11pt;
                    color: {CP_TEXT};
                    spacing: 8px;
                    margin-top: 5px;
                }}
            """)
            form_layout.addWidget(self.hide_terminal_checkbox)

        if self.shortcut_type == "context":
            self.match_foreground_checkbox = QCheckBox("Match any foreground window (not just focused)")
            self.match_foreground_checkbox.setChecked(False)
            form_layout.addWidget(self.match_foreground_checkbox)

        # Context criteria input groups
        if self.shortcut_type in ["context", "exclude", "startup", "text"]:
            form_layout.addSpacing(10)
            form_layout.addWidget(QLabel("<b>Window Context Matching:</b>"))
            
            def _ctx_row(toggle_attr, edit_attr, label, placeholder):
                row = QHBoxLayout()
                toggle = QCheckBox()
                toggle.setChecked(True)
                toggle.setFixedWidth(24)
                
                edit = QLineEdit()
                edit.setPlaceholderText(placeholder)
                toggle.toggled.connect(edit.setEnabled)
                
                setattr(self, toggle_attr, toggle)
                setattr(self, edit_attr, edit)
                
                # Align elements horizontally
                ctx_lbl = QLabel(label)
                ctx_lbl.setFixedWidth(90)
                ctx_lbl.setStyleSheet("color: #808080; font-family: 'Consolas';")
                
                row.addWidget(toggle)
                row.addWidget(ctx_lbl)
                row.addWidget(edit)
                return row

            if self.shortcut_type in ("context", "text"):
                form_layout.addLayout(_ctx_row('window_title_toggle', 'window_title_edit', 'Window Title:', 'e.g., Gemini, Visual Studio Code'))
                form_layout.addLayout(_ctx_row('process_name_toggle', 'process_name_edit', 'Process Name:', 'e.g., WindowsTerminal.exe'))
                form_layout.addLayout(_ctx_row('window_class_toggle', 'window_class_edit', 'Window Class:', 'e.g., CabinetWClass'))
            elif self.shortcut_type == "exclude":
                form_layout.addLayout(_ctx_row('window_title_toggle', 'window_title_edit', 'Window Title:', 'e.g., Discord, Visual Studio Code'))
                form_layout.addLayout(_ctx_row('process_name_toggle', 'process_name_edit', 'Process Name:', 'e.g., Discord.exe, Code.exe'))
                form_layout.addLayout(_ctx_row('window_class_toggle', 'window_class_edit', 'Window Class:', 'e.g., Chrome_WidgetWin_1'))
            elif self.shortcut_type == "startup":
                form_layout.addLayout(_ctx_row('window_title_toggle', 'startup_window_title', 'Window Title:', 'e.g., Notepad, Chrome'))
                form_layout.addLayout(_ctx_row('process_name_toggle', 'startup_process_name', 'Process Name:', 'e.g., chrome.exe'))
                form_layout.addLayout(_ctx_row('window_class_toggle', 'startup_window_class', 'Window Class:', 'e.g., CabinetWClass'))

        form_layout.addStretch(1)

        # Add form layout to top layout
        top_layout.addLayout(form_layout)
        
        # Right side - action/replacement/remap info layout
        if self.shortcut_type == "remap":
            info_layout = QVBoxLayout()
            info_layout.addWidget(QLabel("ℹ️ Key Remapping Guide:"))
            
            info_browser = QTextBrowser()
            info_browser.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; padding: 10px;")
            info_browser.setHtml(f"""
                <h3 style="color: {CP_CYAN}; margin-top: 0px; font-family: 'Consolas';">How Key Remapping Works</h3>
                <p style="font-family: 'Consolas'; color: {CP_TEXT};">Key Remapping changes a key or combination so that it behaves exactly like a different key.</p>
                <p style="font-family: 'Consolas'; color: {CP_TEXT};"><b>Examples:</b></p>
                <ul style="font-family: 'Consolas'; color: {CP_TEXT};">
                    <li><b>CapsLock ➔ Backspace</b>: Turns your CapsLock key into a Backspace key.</li>
                    <li><b>F1 ➔ Esc</b>: Makes the F1 key trigger the Escape function.</li>
                </ul>
                <p style="font-family: 'Consolas'; color: {CP_SUBTEXT};"><i>Note: Unlike script shortcuts, Key Remaps perform clean 1-to-1 raw key substitutions without executing custom code blocks.</i></p>
            """)
            info_browser.setMinimumHeight(300)
            info_browser.setMinimumWidth(400)
            info_layout.addWidget(info_browser)
            top_layout.addLayout(info_layout)
        elif self.shortcut_type == "launcher":
            info_layout = QVBoxLayout()
            info_layout.addWidget(QLabel("ℹ️ Launcher Guide:"))
            
            info_browser = QTextBrowser()
            info_browser.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; padding: 10px;")
            info_browser.setHtml(f"""
                <h3 style="color: {CP_CYAN}; margin-top: 0px; font-family: 'Consolas';">Launcher Shortcuts</h3>
                <p style="font-family: 'Consolas'; color: {CP_TEXT};">Launchers allow you to directly run any script, application, or file using a hotkey without writing raw AutoHotkey code.</p>
                <p style="font-family: 'Consolas'; color: {CP_TEXT};"><b>How it works:</b></p>
                <ul style="font-family: 'Consolas'; color: {CP_TEXT};">
                    <li><b>Target Path</b>: Select or type the absolute path of the file or application you want to run. You can also append arguments.</li>
                    <li><b>Hide Terminal</b>: If checked, it will execute in the background. For Python scripts (`.py`), this automatically uses <code>pythonw.exe</code>. For console apps/scripts, it runs them hidden.</li>
                </ul>
            """)
            info_browser.setMinimumHeight(300)
            info_browser.setMinimumWidth(400)
            info_layout.addWidget(info_browser)
            top_layout.addLayout(info_layout)
        elif self.shortcut_type in ["script", "startup", "context"]:
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
                    border-radius: 0px;
                }
                QPushButton:hover {
                    background-color: #8250df;
                }
            """)
            help_btn.clicked.connect(self.show_command_reference)
            action_layout.addWidget(help_btn)
            
            action_layout.addWidget(self.action_edit)
            top_layout.addLayout(action_layout)
        elif self.shortcut_type == "exclude":
            excl_layout = QVBoxLayout()
            excl_layout.addWidget(QLabel("Excluded Hotkeys (one per line, blank = exclude all):"))
            self.excluded_hotkeys_edit = QTextEdit()
            self.excluded_hotkeys_edit.setMinimumHeight(300)
            self.excluded_hotkeys_edit.setMinimumWidth(300)
            self.excluded_hotkeys_edit.setPlaceholderText("^r\n^s\n!x\n^+t\n; one hotkey per line\n; leave blank to exclude ALL shortcuts")
            excl_layout.addWidget(self.excluded_hotkeys_edit)
            top_layout.addLayout(excl_layout)
        else: # text
            replacement_layout = QVBoxLayout()
            replacement_layout.addWidget(QLabel("Replacement Text:"))
            self.replacement_edit = QTextEdit()
            self.replacement_edit.setMinimumHeight(300)
            self.replacement_edit.setMinimumWidth(400)
            replacement_layout.addWidget(self.replacement_edit)
            
            # Delivery method dropdown
            delivery_row = QHBoxLayout()
            delivery_label = QLabel("Delivery:")
            delivery_label.setStyleSheet(f"color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold;")
            delivery_label.setFixedWidth(90)
            self.delivery_method_combo = QComboBox()
            self.delivery_method_combo.addItems(["Paste (Clipboard)", "SendText (Typing)", "SendInput (Fast Injection)", "SendEvent (Slow & Reliable)"])
            self.delivery_method_combo.setCurrentIndex(0)
            self.delivery_method_combo.setToolTip(
                "Paste: Fast, uses clipboard (may disturb clipboard history)\n"
                "SendText: Types characters one by one (safer for apps like Notepad++)\n"
                "SendInput: Fast keystroke injection without touching clipboard\n"
                "SendEvent: Slow reliable typing for games/legacy apps"
            )
            delivery_row.addWidget(delivery_label)
            delivery_row.addWidget(self.delivery_method_combo)
            replacement_layout.addSpacing(5)
            replacement_layout.addLayout(delivery_row)

            # Menu toggle
            self.show_as_menu_checkbox = QCheckBox("Show multi-line text as a selection menu")
            self.show_as_menu_checkbox.setChecked(False)
            self.show_as_menu_checkbox.setToolTip("If checked and text has multiple lines, a menu will pop up to let you pick one line.")
            self.show_as_menu_checkbox.setStyleSheet(f"""
                QCheckBox {{
                    font-family: 'Consolas', 'Segoe UI', sans-serif;
                    font-size: 11pt;
                    color: {CP_TEXT};
                    spacing: 8px;
                    margin-top: 5px;
                }}
            """)

            menu_info_btn = QPushButton("ℹ")
            menu_info_btn.setFixedSize(20, 20)
            menu_info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            menu_info_btn.setToolTip("Selection Menu Syntax Help")
            menu_info_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {CP_CYAN};
                    border: none;
                    font-size: 13pt;
                    font-weight: bold;
                    padding: 0px;
                    margin: 0px;
                }}
                QPushButton:hover {{
                    background: {CP_CYAN};
                    color: {CP_BG};
                }}
            """)
            menu_info_btn.clicked.connect(self.show_menu_syntax_help)

            menu_row = QHBoxLayout()
            menu_row.addWidget(self.show_as_menu_checkbox)
            menu_row.addWidget(menu_info_btn)
            menu_row.addStretch()
            replacement_layout.addLayout(menu_row)
            
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
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.launcher_shortcuts + self.parent_window.text_shortcuts + self.parent_window.startup_scripts + self.parent_window.context_shortcuts + self.parent_window.exclusion_rules + self.parent_window.remap_shortcuts:
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

    def show_menu_syntax_help(self):
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Selection Menu Syntax Help")
        help_dialog.setMinimumSize(700, 580)
        help_dialog.setStyleSheet(f"""
            QDialog {{
                background: {CP_BG};
            }}
        """)
        layout = QVBoxLayout(help_dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        browser.setStyleSheet(f"""
            QTextBrowser {{
                background: {CP_PANEL};
                color: {CP_TEXT};
                border: none;
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-size: 10pt;
                padding: 15px;
            }}
        """)
        browser.setHtml(f"""
        <h2 style="color:{CP_CYAN}; margin-bottom:8px;">Selection Menu Syntax</h2>
        <p>Write your replacement text using the syntax below. Each line becomes a menu item.</p>

        <h3 style="color:{CP_YELLOW};">Hierarchy (Dashes)</h3>
        <p>Use leading dashes (<code>-</code>) to create nested submenus:</p>
        <pre style="background:#1a1a1a; padding:8px; border-left:3px solid {CP_CYAN}; margin:6px 0;">
[name:Root Item]
-[name:Level 1 Child]
--[name:Level 2 Child]
---[name:Level 3 Child]</pre>
        <p style="color:{CP_SUBTEXT};">Items with children become expandable submenus (up to 5 levels). Empty lines are skipped.</p>

        <h3 style="color:{CP_YELLOW};">Action Tags</h3>
        <p>Each line can have one or more <code>[key:value]</code> tags:</p>
        <table cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin:6px 0;">
        <tr style="background:#1a1a1a;">
            <td style="color:{CP_CYAN}; font-weight:bold; border-bottom:1px solid {CP_DIM}; width:80px;">Tag</td>
            <td style="color:{CP_TEXT}; border-bottom:1px solid {CP_DIM};">Purpose</td>
        </tr>
        <tr><td style="color:{CP_GREEN};"><code>name</code></td><td>Display label in the menu</td></tr>
        <tr><td style="color:{CP_GREEN};"><code>text</code></td><td>Paste/type the specified text</td></tr>
        <tr><td style="color:{CP_GREEN};"><code>folder</code></td><td>Open folder in File Explorer</td></tr>
        <tr><td style="color:{CP_GREEN};"><code>cmd</code></td><td>Run a shell command</td></tr>
        <tr><td style="color:{CP_ORANGE};"><code>shell</code></td><td>Shell for <code>cmd</code>: <code>cmd</code> (default) or <code>pwsh</code></td></tr>
        <tr><td style="color:{CP_ORANGE};"><code>show</code></td><td>Visibility for <code>cmd</code>: <code>hidden</code> (default) or <code>visible</code></td></tr>
        </table>

        <h3 style="color:{CP_YELLOW};">Examples</h3>
        <pre style="background:#1a1a1a; padding:8px; border-left:3px solid {CP_GREEN}; margin:6px 0;">
<span style="color:{CP_SUBTEXT};"># Paste text</span>
-[name:My Email][text:user@example.com]

<span style="color:{CP_SUBTEXT};"># Open a folder</span>
-[name:Downloads][folder:C:\\Users\\nahid\\Downloads]

<span style="color:{CP_SUBTEXT};"># Run CMD command (hidden)</span>
-[name:Flush DNS][cmd:ipconfig /flushdns]

<span style="color:{CP_SUBTEXT};"># Run CMD command (visible terminal)</span>
-[name:Ping Google][cmd:ping google.com][show:visible]

<span style="color:{CP_SUBTEXT};"># Run PowerShell command</span>
-[name:List Processes][cmd:Get-Process][shell:pwsh][show:visible]

<span style="color:{CP_SUBTEXT};"># Nested submenu</span>
[name:Dev Tools]
-[name:Commands]
--[name:Git Status][cmd:git status][shell:pwsh][show:visible]
--[name:Clear Temp][cmd:Remove-Item $env:TEMP\\* -Recurse -Force][shell:pwsh]
-[name:Folders]
--[name:Project][folder:C:\\myproject]</pre>

        <h3 style="color:{CP_YELLOW};">Defaults</h3>
        <ul>
        <li>If no <code>[name:]</code> is given, the action value is used as the label.</li>
        <li>A tag without a colon like <code>[hello world]</code> defaults to <code>[text:hello world]</code>.</li>
        <li>Plain text without brackets uses the line as both name and text.</li>
        </ul>
        """)
        layout.addWidget(browser)

        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {CP_DIM};
                color: {CP_TEXT};
                border: none;
                padding: 8px 30px;
                font-size: 11pt;
                margin: 8px;
            }}
            QPushButton:hover {{
                background: {CP_CYAN};
                color: {CP_BG};
            }}
        """)
        close_btn.clicked.connect(help_dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        help_dialog.exec()

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Drop")
        if file_path:
            self.file_path_edit.setText(file_path)

    def import_windows_default(self):
        dialog = WindowsDefaultLookupDialog(self)
        if dialog.exec():
            item = dialog.selected_item
            if item:
                self.name_edit.setText(item["name"])
                self.description_edit.setText(item["description"])
                if hasattr(self, "hotkey_edit"):
                    self.hotkey_edit.setText(item["hotkey"])
                if hasattr(self, "action_edit"):
                    self.action_edit.setPlainText(item["action"])
                self.category_combo.setCurrentText("System")


    def populate_fields(self):
        self.name_edit.setText(self.shortcut_data.get("name", ""))
        self.category_combo.setCurrentText(self.shortcut_data.get("category", ""))
        self.description_edit.setText(self.shortcut_data.get("description", ""))
        self.enabled_checkbox.setChecked(self.shortcut_data.get("enabled", True))
        self.favourite_checkbox.setChecked(self.shortcut_data.get("favourite", False))

        if self.shortcut_type == "script":
            self.hotkey_edit.setText(self.shortcut_data.get("hotkey", ""))
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
        elif self.shortcut_type == "context":
            self.hotkey_edit.setText(self.shortcut_data.get("hotkey", ""))
            self.window_title_edit.setText(self.shortcut_data.get("window_title", ""))
            self.process_name_edit.setText(self.shortcut_data.get("process_name", ""))
            self.window_class_edit.setText(self.shortcut_data.get("window_class", ""))
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
            wt_on = self.shortcut_data.get("window_title_enabled", True)
            pn_on = self.shortcut_data.get("process_name_enabled", True)
            wc_on = self.shortcut_data.get("window_class_enabled", True)
            self.window_title_toggle.setChecked(wt_on); self.window_title_edit.setEnabled(wt_on)
            self.process_name_toggle.setChecked(pn_on); self.process_name_edit.setEnabled(pn_on)
            self.window_class_toggle.setChecked(wc_on); self.window_class_edit.setEnabled(wc_on)
            self.match_foreground_checkbox.setChecked(self.shortcut_data.get("match_foreground", False))
        elif self.shortcut_type == "exclude":
            self.window_title_edit.setText(self.shortcut_data.get("window_title", ""))
            self.process_name_edit.setText(self.shortcut_data.get("process_name", ""))
            self.window_class_edit.setText(self.shortcut_data.get("window_class", ""))
            self.excluded_hotkeys_edit.setPlainText(self.shortcut_data.get("excluded_hotkeys", ""))
            wt_on = self.shortcut_data.get("window_title_enabled", True)
            pn_on = self.shortcut_data.get("process_name_enabled", True)
            wc_on = self.shortcut_data.get("window_class_enabled", True)
            self.window_title_toggle.setChecked(wt_on); self.window_title_edit.setEnabled(wt_on)
            self.process_name_toggle.setChecked(pn_on); self.process_name_edit.setEnabled(pn_on)
            self.window_class_toggle.setChecked(wc_on); self.window_class_edit.setEnabled(wc_on)
        elif self.shortcut_type == "startup":
            self.action_edit.setPlainText(self.shortcut_data.get("action", ""))
            mode = self.shortcut_data.get("context_mode", "none")
            self.startup_context_mode.setCurrentIndex({"none": 0, "active": 1, "inactive": 2}.get(mode, 0))
            self.startup_window_title.setText(self.shortcut_data.get("window_title", ""))
            self.startup_process_name.setText(self.shortcut_data.get("process_name", ""))
            self.startup_window_class.setText(self.shortcut_data.get("window_class", ""))
            wt_on = self.shortcut_data.get("window_title_enabled", True)
            pn_on = self.shortcut_data.get("process_name_enabled", True)
            wc_on = self.shortcut_data.get("window_class_enabled", True)
            self.window_title_toggle.setChecked(wt_on); self.startup_window_title.setEnabled(wt_on)
            self.process_name_toggle.setChecked(pn_on); self.startup_process_name.setEnabled(pn_on)
            self.window_class_toggle.setChecked(wc_on); self.startup_window_class.setEnabled(wc_on)
        elif self.shortcut_type == "file":
            self.trigger_edit.setText(self.shortcut_data.get("trigger", ""))
            self.file_path_edit.setText(self.shortcut_data.get("file_path", ""))
        elif self.shortcut_type == "launcher":
            self.hotkey_edit.setText(self.shortcut_data.get("hotkey", ""))
            self.file_path_edit.setText(self.shortcut_data.get("target_path", ""))
            self.hide_terminal_checkbox.setChecked(self.shortcut_data.get("hide_terminal", True))
        elif self.shortcut_type == "remap":
            self.origin_key_edit.setText(self.shortcut_data.get("origin_key", ""))
            self.destination_key_edit.setText(self.shortcut_data.get("destination_key", ""))
        else: # text
            self.trigger_edit.setText(self.shortcut_data.get("trigger", ""))
            self.replacement_edit.setPlainText(self.shortcut_data.get("replacement", ""))
            # Backward compat: old use_clipboard bool -> new delivery_method string
            delivery = self.shortcut_data.get("delivery_method", "")
            if not delivery:
                delivery = "paste" if self.shortcut_data.get("use_clipboard", True) else "sendtext"
            method_map = {"paste": 0, "sendtext": 1, "sendinput": 2, "sendevent": 3}
            self.delivery_method_combo.setCurrentIndex(method_map.get(delivery, 0))
            self.show_as_menu_checkbox.setChecked(self.shortcut_data.get("show_as_menu", False))
            
            self.window_title_edit.setText(self.shortcut_data.get("window_title", ""))
            self.process_name_edit.setText(self.shortcut_data.get("process_name", ""))
            self.window_class_edit.setText(self.shortcut_data.get("window_class", ""))
            
            wt_on = self.shortcut_data.get("window_title_enabled", False)
            pn_on = self.shortcut_data.get("process_name_enabled", False)
            wc_on = self.shortcut_data.get("window_class_enabled", False)
            
            self.window_title_toggle.setChecked(wt_on); self.window_title_edit.setEnabled(wt_on)
            self.process_name_toggle.setChecked(pn_on); self.process_name_edit.setEnabled(pn_on)
            self.window_class_toggle.setChecked(wc_on); self.window_class_edit.setEnabled(wc_on)

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
                border-radius: 0px;
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
                border-radius: 0px;
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
        toc_scroll.setStyleSheet(f"""
            QScrollArea {{ background:#1a1a1a; border:1px solid #444; border-radius:5px; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 0px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
        """)
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
                border-radius: 0px;
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
        favourite = self.favourite_checkbox.isChecked()

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
            
            if not any(part.strip() for part in window_title.split(",")) and not any(part.strip() for part in process_name.split(",")) and not any(part.strip() for part in window_class.split(",")):
                QMessageBox.warning(self, "Warning", "At least one context field must contain a real value.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "hotkey": hotkey,
                "window_title": window_title,
                "process_name": process_name,
                "window_class": window_class,
                "window_title_enabled": self.window_title_toggle.isChecked(),
                "process_name_enabled": self.process_name_toggle.isChecked(),
                "window_class_enabled": self.window_class_toggle.isChecked(),
                "match_foreground": self.match_foreground_checkbox.isChecked(),
                "action": action,
                "enabled": enabled
            }
        elif self.shortcut_type == "exclude":
            window_title = self.window_title_edit.text().strip()
            process_name = self.process_name_edit.text().strip()
            window_class = self.window_class_edit.text().strip()

            if not any(part.strip() for part in window_title.split(",")) and not any(part.strip() for part in process_name.split(",")) and not any(part.strip() for part in window_class.split(",")):
                QMessageBox.warning(self, "Warning", "At least one exclusion field must contain a real value.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "window_title": window_title,
                "process_name": process_name,
                "window_class": window_class,
                "window_title_enabled": self.window_title_toggle.isChecked(),
                "process_name_enabled": self.process_name_toggle.isChecked(),
                "window_class_enabled": self.window_class_toggle.isChecked(),
                "excluded_hotkeys": self.excluded_hotkeys_edit.toPlainText().strip(),
                "enabled": enabled
            }
        elif self.shortcut_type == "startup":
            action = self.action_edit.toPlainText().strip()
            if not action:
                QMessageBox.warning(self, "Warning", "Action code is required.")
                return

            mode_map = {0: "none", 1: "active", 2: "inactive"}
            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "action": action,
                "context_mode": mode_map.get(self.startup_context_mode.currentIndex(), "none"),
                "window_title": self.startup_window_title.text().strip(),
                "process_name": self.startup_process_name.text().strip(),
                "window_class": self.startup_window_class.text().strip(),
                "window_title_enabled": self.window_title_toggle.isChecked(),
                "process_name_enabled": self.process_name_toggle.isChecked(),
                "window_class_enabled": self.window_class_toggle.isChecked(),
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
        elif self.shortcut_type == "launcher":
            hotkey = self.hotkey_edit.text().strip()
            target_path = self.file_path_edit.text().strip()

            if not hotkey or not target_path:
                QMessageBox.warning(self, "Warning", "Both hotkey and target path are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "hotkey": hotkey,
                "target_path": target_path,
                "hide_terminal": self.hide_terminal_checkbox.isChecked(),
                "enabled": enabled
            }
        elif self.shortcut_type == "remap":
            origin_key = self.origin_key_edit.text().strip()
            destination_key = self.destination_key_edit.text().strip()

            if not origin_key or not destination_key:
                QMessageBox.warning(self, "Warning", "Both origin and destination keys are required.")
                return

            shortcut_data = {
                "name": name,
                "category": category,
                "description": description,
                "origin_key": origin_key,
                "destination_key": destination_key,
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
                "delivery_method": ["paste", "sendtext", "sendinput", "sendevent"][self.delivery_method_combo.currentIndex()],
                "show_as_menu": self.show_as_menu_checkbox.isChecked(),
                "window_title": self.window_title_edit.text().strip(),
                "process_name": self.process_name_edit.text().strip(),
                "window_class": self.window_class_edit.text().strip(),
                "window_title_enabled": self.window_title_toggle.isChecked(),
                "process_name_enabled": self.process_name_toggle.isChecked(),
                "window_class_enabled": self.window_class_toggle.isChecked(),
                "enabled": enabled
            }

        shortcut_data['favourite'] = favourite

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
            elif self.shortcut_type == "exclude":
                self.parent_window.exclusion_rules.append(shortcut_data)
            elif self.shortcut_type == "remap":
                self.parent_window.remap_shortcuts.append(shortcut_data)
            elif self.shortcut_type == "launcher":
                self.parent_window.launcher_shortcuts.append(shortcut_data)
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
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.launcher_shortcuts + self.parent_window.text_shortcuts + self.parent_window.context_shortcuts + self.parent_window.remap_shortcuts:
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
        self.resize(450, 300)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; }}
            QComboBox, QSpinBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
                min-height: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                selection-background-color: {CP_CYAN};
                selection-color: {CP_BG};
                border: 1px solid {CP_CYAN};
            }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Font Selection
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Application Font:"))
        
        from PyQt6.QtWidgets import QFontComboBox, QSpinBox
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.parent_window.app_font_family))
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)

        # Font Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 24)
        self.size_spin.setValue(self.parent_window.app_font_size)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        layout.addLayout(size_layout)

        # Theme Selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Shortcut Builder Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Cyberpunk (Default)", "cyberpunk")
        self.theme_combo.addItem("Black & White", "black_white")
        self.theme_combo.addItem("White & Black", "white_black")
        
        # Select current theme
        settings = QSettings("AHKEditor", "ShortcutEditor")
        current_theme = settings.value("shortcut_builder_theme", "cyberpunk")
        index = self.theme_combo.findData(current_theme)
        if index != -1:
            self.theme_combo.setCurrentIndex(index)
            
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Shortcut Preview Font Selection
        pfont_layout = QHBoxLayout()
        pfont_layout.addWidget(QLabel("Shortcut Preview Font:"))
        self.pfont_combo = QFontComboBox()
        current_pfont = settings.value("shortcut_builder_font", "Consolas")
        self.pfont_combo.setCurrentFont(QFont(current_pfont))
        pfont_layout.addWidget(self.pfont_combo)
        layout.addLayout(pfont_layout)

        # Selection Menu Font Selection
        sm_font_layout = QHBoxLayout()
        sm_font_layout.addWidget(QLabel("Selection Menu Font:"))
        self.sm_font_combo = QFontComboBox()
        self.sm_font_combo.setCurrentFont(QFont(self.parent_window.selection_menu_font_family))
        sm_font_layout.addWidget(self.sm_font_combo)
        layout.addLayout(sm_font_layout)

        # Selection Menu Font Size
        sm_size_layout = QHBoxLayout()
        sm_size_layout.addWidget(QLabel("Selection Menu Font Size:"))
        self.sm_size_spin = QSpinBox()
        self.sm_size_spin.setRange(8, 36)
        self.sm_size_spin.setValue(self.parent_window.selection_menu_font_size)
        sm_size_layout.addWidget(self.sm_size_spin)
        sm_size_layout.addStretch()
        layout.addLayout(sm_size_layout)

        layout.addWidget(QLabel("<small><i>Note: Some icons require a Nerd Font (NFP) to display correctly.</i></small>"))

        # Buttons
        buttons = QHBoxLayout()
        save_btn = CyberButton(" SAVE && APPLY", color=CP_GREEN)
        save_btn.clicked.connect(self.save_settings)
        
        close_btn = CyberButton(" CLOSE", color=CP_DIM, is_outlined=True)
        close_btn.clicked.connect(self.close)
        
        buttons.addStretch()
        buttons.addWidget(save_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

    def save_settings(self):
        new_font = self.font_combo.currentFont().family()
        new_size = self.size_spin.value()
        self.parent_window.app_font_family = new_font
        self.parent_window.app_font_size = new_size
        
        self.parent_window.selection_menu_font_family = self.sm_font_combo.currentFont().family()
        self.parent_window.selection_menu_font_size = self.sm_size_spin.value()
        
        # Save shortcut builder theme
        selected_theme = self.theme_combo.currentData()
        
        # Save shortcut builder preview font
        selected_pfont = self.pfont_combo.currentFont().family()
        
        settings = QSettings("AHKEditor", "ShortcutEditor")
        settings.setValue("shortcut_builder_theme", selected_theme)
        settings.setValue("shortcut_builder_font", selected_pfont)
        
        self.parent_window.apply_global_font()
        self.parent_window.save_shortcuts_json()
        self.accept()


class AHKShortcutEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_shortcuts = []
        self.launcher_shortcuts = []
        self.text_shortcuts = []
        self.file_shortcuts = []
        self.startup_scripts = []
        self.context_shortcuts = []
        self.exclusion_rules = []
        self.remap_shortcuts = []
        self.app_font_family = "Consolas" # Default per theme guide
        self.app_font_size = 10
        self.selection_menu_font_family = "Segoe UI"
        self.selection_menu_font_size = 12
        self.category_colors = {
            "System": "#FF6B6B", "Navigation": "#4ECDC4", "Text": "#45B7D1",
            "Media": "#96CEB4", "AutoHotkey": "#FFEAA7", "General": "#DDA0DD",
            "Imported": "#FFA07A", "Tools": "#98D8C8", "Window": "#F7DC6F", "File": "#BB8FCE"
        }
        # Section expanded/collapsed states
        self.section_states = {
            "script": True,
            "launcher": True,
            "context": True,
            "exclude": True,
            "startup": True,
            "text": True,
            "file": True,
            "remap": True
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

        # Apply Global Theme
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: {CP_BG};
            }}
            QWidget {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 10pt;
            }}
            
            QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
                selection-background-color: {CP_CYAN};
                selection-color: #000000;
            }}

            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
                border: 1px solid {CP_CYAN};
            }}

            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px; 
                border: none;
            }}
            
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 0px;
            }}

            QPushButton:hover {{
                background-color: #2a2a2a;
                border: 1px solid {CP_YELLOW};
                color: {CP_YELLOW};
            }}

            QPushButton:pressed {{
                background-color: {CP_YELLOW};
                color: black;
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {CP_YELLOW};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
            
            QCheckBox {{
                spacing: 8px;
                color: {CP_TEXT};
            }}

            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {CP_DIM};
                background: {CP_PANEL};
            }}

            QCheckBox::indicator:checked {{
                background: {CP_YELLOW};
                border-color: {CP_YELLOW};
            }}
            
            QMenu {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_CYAN};
            }}

            QMenu::item:selected {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
            
            QScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                background: {CP_BG};
                width: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {CP_CYAN};
                min-height: 20px;
                border-radius: 0px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}

            QScrollBar:horizontal {{
                background: {CP_BG};
                height: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:horizontal {{
                background: {CP_CYAN};
                min-width: 20px;
                border-radius: 0px;
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
            }}

            QComboBox QAbstractItemView {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                selection-background-color: {CP_CYAN};
                selection-color: {CP_BG};
                border: 1px solid {CP_CYAN};
                outline: none;
            }}
        """)

        # Add button with menu
        self.add_btn = CyberButton(" ADD", color=CP_GREEN, svg_data=SVGS["PLUS"])
        self.add_menu = QMenu()
        self.add_menu.addAction("Script Shortcut", lambda: self.open_add_dialog("script"))
        self.add_menu.addAction("Launcher Shortcut", lambda: self.open_add_dialog("launcher"))
        self.add_menu.addAction("Text Shortcut", lambda: self.open_add_dialog("text"))
        self.add_menu.addAction("File Shortcut", lambda: self.open_add_dialog("file"))
        self.add_menu.addAction("Context Shortcut", lambda: self.open_add_dialog("context"))
        self.add_menu.addAction("Exclusion Rule", lambda: self.open_add_dialog("exclude"))
        self.add_menu.addAction("Key Remap", lambda: self.open_add_dialog("remap"))
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
                color: #00F0FF;
                margin-left: 5px;
                margin-right: 5px;
            }
            QCheckBox::indicator {
                width: 0px;
                height: 0px;
                background: none;
                border: none;
                image: none;
            }
        """)
        top_layout.addWidget(self.category_toggle)

        # Color button
        self.colors_btn = CyberButton(" COLORS", color=CP_ORANGE, is_outlined=True, svg_data=SVGS["PALETTE"])
        self.colors_btn.clicked.connect(self.open_color_dialog)
        top_layout.addWidget(self.colors_btn)

        # Settings button
        self.settings_btn = CyberButton(" SETTINGS", color=CP_TEXT, is_outlined=True, svg_data=SVGS["SETTINGS"])
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        top_layout.addWidget(self.settings_btn)

        # Restart button
        self.restart_btn = CyberButton(" RESTART", color=CP_RED, is_outlined=True, svg_data=SVGS["RESTART"])
        self.restart_btn.clicked.connect(self.restart_app)
        top_layout.addWidget(self.restart_btn)

        # Search box
        self.search_edit = HotkeyLineEdit()
        self.search_edit.setObjectName("search_edit")
        self.search_edit.setPlaceholderText(" Search shortcuts...")
        self.search_edit.textChanged.connect(self.update_display)
        self.search_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_edit.setFixedHeight(34)
        
        self.record_search_btn = QPushButton("")
        self.record_search_btn.setCheckable(True)
        self.record_search_btn.setFixedSize(26,26)
        self.record_search_btn.setStyleSheet(f"""
            QPushButton {{
                font-family: inherit;
                background-color: #cc2222;
                border: none;
                border-radius: 13px;
                color: white;
                font-size: 18px;
            }}
            QPushButton:checked {{
                background-color: {CP_CYAN};
                color: {CP_BG};
                border-color: {CP_CYAN};
            }}
            QPushButton:hover {{
                border-color: {CP_CYAN};
                background-color: #4d4d4d;
            }}
        """)
        self.record_search_btn.clicked.connect(lambda checked: self.search_edit.set_recording(checked))
        self.search_edit.record_button = self.record_search_btn

        top_layout.addWidget(self.search_edit)
        top_layout.addWidget(self.record_search_btn)

        # Generate button
        self.generate_btn = CyberButton(" GENERATE", color=CP_YELLOW, svg_data=SVGS["ROCKET"])
        self.generate_btn.clicked.connect(self.generate_ahk_script)
        top_layout.addWidget(self.generate_btn)

        layout.addLayout(top_layout)

        # Text browser for HTML display
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenLinks(False)
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.anchorClicked.connect(self.handle_click)
        self.text_browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_browser.customContextMenuRequested.connect(self.show_context_menu)
        # Enable mouse tracking for double-click detection
        self.text_browser.setMouseTracking(True)
        self.text_browser.viewport().installEventFilter(self)
        self.text_browser.setStyleSheet(f"background-color: {CP_BG}; border: none;")
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
        """Apply the selected font family and size globally to the application"""
        font = QFont(self.app_font_family, self.app_font_size)
        QApplication.instance().setFont(font)
        # Force update of elements that might have their own font set
        if hasattr(self, 'text_browser'):
            self.update_display() # Refresh HTML with new font
            # Update the base font size in HTML too
            self.text_browser.setStyleSheet(f"background-color: {CP_BG}; border: none; font-size: {self.app_font_size}pt;")

    def restart_app(self):
        """Restart the application to apply changes."""
        os.execv(sys.executable, [sys.executable] + sys.argv)

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
        """Handle clicks on shortcuts and section headers"""
        scheme = url.scheme()
        host = url.host()
        path = url.path().strip('/')

        if scheme == "toggle-section":
            section = host
            if section in self.section_states:
                self.section_states[section] = not self.section_states[section]
                self.update_display()
            return

        if scheme == "select":
            shortcut_type = host
            try:
                index = int(path)
            except ValueError:
                return

            if shortcut_type == "script" and index < len(self.script_shortcuts):
                self.selected_shortcut = self.script_shortcuts[index]
                self.selected_type = "script"
            elif shortcut_type == "launcher" and index < len(self.launcher_shortcuts):
                self.selected_shortcut = self.launcher_shortcuts[index]
                self.selected_type = "launcher"
            elif shortcut_type == "text" and index < len(self.text_shortcuts):
                self.selected_shortcut = self.text_shortcuts[index]
                self.selected_type = "text"
            elif shortcut_type == "file" and index < len(self.file_shortcuts):
                self.selected_shortcut = self.file_shortcuts[index]
                self.selected_type = "file"
            elif shortcut_type == "context" and index < len(self.context_shortcuts):
                self.selected_shortcut = self.context_shortcuts[index]
                self.selected_type = "context"
            elif shortcut_type == "exclude" and index < len(self.exclusion_rules):
                self.selected_shortcut = self.exclusion_rules[index]
                self.selected_type = "exclude"
            elif shortcut_type == "startup" and index < len(self.startup_scripts):
                self.selected_shortcut = self.startup_scripts[index]
                self.selected_type = "startup"
            elif shortcut_type == "remap" and index < len(self.remap_shortcuts):
                self.selected_shortcut = self.remap_shortcuts[index]
                self.selected_type = "remap"

            self.update_display()

        elif scheme == "toggle":
            shortcut_type = host
            try:
                index = int(path)
            except ValueError:
                return

            if shortcut_type == "script" and index < len(self.script_shortcuts):
                self.script_shortcuts[index]["enabled"] = not self.script_shortcuts[index].get("enabled", True)
            elif shortcut_type == "launcher" and index < len(self.launcher_shortcuts):
                self.launcher_shortcuts[index]["enabled"] = not self.launcher_shortcuts[index].get("enabled", True)
            elif shortcut_type == "text" and index < len(self.text_shortcuts):
                self.text_shortcuts[index]["enabled"] = not self.text_shortcuts[index].get("enabled", True)
            elif shortcut_type == "file" and index < len(self.file_shortcuts):
                self.file_shortcuts[index]["enabled"] = not self.file_shortcuts[index].get("enabled", True)
            elif shortcut_type == "context" and index < len(self.context_shortcuts):
                self.context_shortcuts[index]["enabled"] = not self.context_shortcuts[index].get("enabled", True)
            elif shortcut_type == "exclude" and index < len(self.exclusion_rules):
                self.exclusion_rules[index]["enabled"] = not self.exclusion_rules[index].get("enabled", True)
            elif shortcut_type == "startup" and index < len(self.startup_scripts):
                self.startup_scripts[index]["enabled"] = not self.startup_scripts[index].get("enabled", True)
            elif shortcut_type == "remap" and index < len(self.remap_shortcuts):
                self.remap_shortcuts[index]["enabled"] = not self.remap_shortcuts[index].get("enabled", True)

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
                    data = json.load(f)
                    self.script_shortcuts = data.get("script_shortcuts", [])
                    self.launcher_shortcuts = data.get("launcher_shortcuts", [])
                    self.text_shortcuts = data.get("text_shortcuts", [])
                    self.file_shortcuts = data.get("file_shortcuts", [])
                    self.startup_scripts = data.get("startup_scripts", [])
                    self.context_shortcuts = data.get("context_shortcuts", [])
                    self.exclusion_rules = data.get("exclusion_rules", data.get("excluded_contexts", []))
                    self.remap_shortcuts = data.get("remap_shortcuts", [])
                    self.app_font_family = data.get("app_font_family", "Consolas")
                    self.app_font_size = data.get("app_font_size", 10)
                    self.selection_menu_font_family = data.get("selection_menu_font_family", "Segoe UI")
                    self.selection_menu_font_size = data.get("selection_menu_font_size", 12)
                    
                    # Fix-up: Move file shortcuts that were accidentally saved in text_shortcuts
                    to_move = [s for s in self.text_shortcuts if "file_path" in s]
                    for s in to_move:
                        self.text_shortcuts.remove(s)
                        self.file_shortcuts.append(s)
                    
                    # Reverse Fix-up: Restore text shortcuts that were incorrectly moved to exclusion rules
                    to_move_back_text = [s for s in self.exclusion_rules if "trigger" in s and "replacement" in s]
                    for s in to_move_back_text:
                        self.exclusion_rules.remove(s)
                        self.text_shortcuts.append(s)
                    
                    # Fix-up: Move exclusion rules and context shortcuts that were accidentally saved in text_shortcuts
                    to_move_exclude = [s for s in self.text_shortcuts if ("window_title" in s or "process_name" in s or "window_class" in s) and "hotkey" not in s and "trigger" not in s]
                    for s in to_move_exclude:
                        self.text_shortcuts.remove(s)
                        self.exclusion_rules.append(s)
                        
                    to_move_context = [s for s in self.text_shortcuts if ("window_title" in s or "process_name" in s or "window_class" in s) and "hotkey" in s and "trigger" not in s]
                    for s in to_move_context:
                        self.text_shortcuts.remove(s)
                        self.context_shortcuts.append(s)

                    if to_move or to_move_exclude or to_move_context:
                        self.save_shortcuts_json()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load shortcuts JSON: {e}")
                self.create_default_shortcuts()
        else:
            self.create_default_shortcuts()

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
                "launcher_shortcuts": self.launcher_shortcuts, 
                "text_shortcuts": self.text_shortcuts,
                "file_shortcuts": self.file_shortcuts,
                "startup_scripts": self.startup_scripts,
                "context_shortcuts": self.context_shortcuts,
                "exclusion_rules": self.exclusion_rules,
                "remap_shortcuts": self.remap_shortcuts,
                "app_font_family": self.app_font_family,
                "app_font_size": self.app_font_size,
                "selection_menu_font_family": self.selection_menu_font_family,
                "selection_menu_font_size": self.selection_menu_font_size
            }
            with open(SHORTCUTS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shortcuts JSON: {e}")

    def get_category_color(self, category):
        return self.category_colors.get(category, "#B0B0B0")

    def update_display(self):
        if not hasattr(self, 'text_browser'): return

        v_bar = self.text_browser.verticalScrollBar()
        # Capture current state
        scroll_pos = v_bar.value()
        # Use a generous margin for bottom detection to prevent "creeping up"
        at_bottom = v_bar.maximum() > 0 and scroll_pos >= v_bar.maximum() - 15

        search_query = self.search_edit.text().lower()
        group_by_category = self.category_toggle.isChecked()

        # Filter shortcuts
        filtered_script = [s for s in self.script_shortcuts
                          if search_query in f"{s.get('name', '')} {s.get('hotkey', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        filtered_launcher = [s for s in self.launcher_shortcuts
                            if search_query in f"{s.get('name', '')} {s.get('hotkey', '')} {s.get('description', '')} {s.get('category', '')} {s.get('target_path', '')}".lower()]
        filtered_text = [s for s in self.text_shortcuts
                        if search_query in f"{s.get('name', '')} {s.get('trigger', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        filtered_file = [s for s in self.file_shortcuts
                        if search_query in f"{s.get('name', '')} {s.get('trigger', '')} {s.get('description', '')} {s.get('category', '')} {s.get('file_path', '')}".lower()]
        filtered_context = [s for s in self.context_shortcuts
                           if search_query in f"{s.get('name', '')} {s.get('hotkey', '')} {s.get('description', '')} {s.get('category', '')} {s.get('window_title', '')} {s.get('process_name', '')} {s.get('window_class', '')}".lower()]
        filtered_exclusions = [s for s in self.exclusion_rules
                              if search_query in f"{s.get('name', '')} {s.get('description', '')} {s.get('category', '')} {s.get('window_title', '')} {s.get('process_name', '')} {s.get('window_class', '')}".lower()]
        filtered_startup = [s for s in self.startup_scripts
                           if search_query in f"{s.get('name', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        filtered_remap = [s for s in self.remap_shortcuts
                         if search_query in f"{s.get('name', '')} {s.get('origin_key', '')} {s.get('destination_key', '')} {s.get('description', '')} {s.get('category', '')}".lower()]
        
        html = self.generate_html(filtered_script, filtered_launcher, filtered_text, filtered_file, filtered_context, filtered_exclusions, filtered_startup, filtered_remap, group_by_category)
        
        # Block signals and updates to prevent flickering/jumping
        v_bar.blockSignals(True)
        self.text_browser.setUpdatesEnabled(False)
        self.text_browser.setHtml(html)
        
        # Force the document layout to recalculate synchronously
        # Accessing documentSize() triggers the layout engine to update the scrollbar range
        _ = self.text_browser.document().documentLayout().documentSize()
        
        # Immediate restoration
        if at_bottom:
            v_bar.setValue(v_bar.maximum())
        else:
            v_bar.setValue(scroll_pos)
            
        self.text_browser.setUpdatesEnabled(True)
        v_bar.blockSignals(False)

        # Backup restoration in next event loop to handle any delayed layout shifts
        def backup_restore():
            v_bar.blockSignals(True)
            if at_bottom:
                v_bar.setValue(v_bar.maximum())
            else:
                v_bar.setValue(scroll_pos)
            v_bar.blockSignals(False)
        
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, backup_restore)

    def generate_html(self, script_shortcuts, launcher_shortcuts, text_shortcuts, file_shortcuts, context_shortcuts, exclusion_rules, startup_scripts, remap_shortcuts, group_by_category):
        def get_toggle_icon(section):
            return "▾" if self.section_states.get(section, True) else "▸"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Consolas', 'Segoe UI', sans-serif;
                    margin: 10px 20px;
                    background: {CP_BG};
                    color: {CP_TEXT};
                    font-size: {self.app_font_size}pt;
                }}
                .container {{ display: flex; gap: 20px; }}
                .column {{ flex: 1; }}
                .section-title {{
                    font-size: 1.4em;
                    font-weight: bold;
                    margin: 15px 0 5px 0;
                    color: {CP_CYAN};
                }}
                .section-title a {{
                    color: {CP_CYAN};
                    text-decoration: none;
                }}
                .section-title:first-child {{
                    margin-top: 5px;
                }}
                .category-header {{
                    font-size: 1.2em;
                    font-weight: bold;
                    margin: 12px 0 3px 0;
                    padding: 3px 10px;
                    border-radius: 0px;
                    background: {CP_PANEL};
                    border-bottom: 1px solid {CP_DIM};
                }}
                .category-header.first-in-section {{
                    margin-top: 8px;
                }}
                .shortcut-item {{
                    padding: 2px 5px;
                    margin: 2px 0;
                    border-radius: 0px;
                    cursor: pointer;
                    transition: background 0.2s;
                    border-left: 2px solid transparent;
                }}
                .shortcut-item:hover {{
                    background: rgba(0, 240, 255, 0.05);
                    border-left-color: {CP_CYAN};
                }}
                .shortcut-item.selected {{
                    background: rgba(0, 240, 255, 0.15);
                    border-left-color: {CP_CYAN};
                }}
                .shortcut-key {{
                    color: #ffffff;
                    font-weight: bold;
                    white-space: nowrap;
                    padding-right: 15px;
                }}
                .shortcut-separator {{
                    color: {CP_GREEN};
                    font-weight: bold;
                    font-size: 1.1em;
                    vertical-align: middle;
                    white-space: nowrap;
                }}
                .shortcut-name {{
                    color: {CP_TEXT};
                }}
                .shortcut-desc {{
                    color: {CP_SUBTEXT};
                    font-size: 0.85em;
                }}
                .status-enabled {{ color: {CP_GREEN}; }}
                .status-disabled {{ color: {CP_RED}; }}
                
                .indent {{ margin-left: 15px; }}
                a {{ text-decoration: none; color: inherit; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="column">
        """

        # ── FAVOURITE section ──────────────────────────────
        all_shortcuts_with_type = []
        for s in script_shortcuts:
            if s.get('favourite', False):
                idx = self.script_shortcuts.index(s)
                all_shortcuts_with_type.append((s, 'script', idx))
        for s in launcher_shortcuts:
            if s.get('favourite', False):
                idx = self.launcher_shortcuts.index(s)
                all_shortcuts_with_type.append((s, 'launcher', idx))
        for s in remap_shortcuts:
            if s.get('favourite', False):
                idx = self.remap_shortcuts.index(s)
                all_shortcuts_with_type.append((s, 'remap', idx))
        for s in context_shortcuts:
            if s.get('favourite', False):
                idx = self.context_shortcuts.index(s)
                all_shortcuts_with_type.append((s, 'context', idx))
        for s in exclusion_rules:
            if s.get('favourite', False):
                idx = self.exclusion_rules.index(s)
                all_shortcuts_with_type.append((s, 'exclude', idx))
        for s in startup_scripts:
            if s.get('favourite', False):
                idx = self.startup_scripts.index(s)
                all_shortcuts_with_type.append((s, 'startup', idx))
        for s in text_shortcuts:
            if s.get('favourite', False):
                idx = self.text_shortcuts.index(s)
                all_shortcuts_with_type.append((s, 'text', idx))
        for s in file_shortcuts:
            if s.get('favourite', False):
                idx = self.file_shortcuts.index(s)
                all_shortcuts_with_type.append((s, 'file', idx))

        if all_shortcuts_with_type:
            html += f'<div class="section-title"><a href="toggle-section://favourite">{get_toggle_icon("favourite")} ⭐ Favourites</a></div>'
            if self.section_states.get("favourite", True):
                for shortcut, stype, sidx in all_shortcuts_with_type:
                    html += self.generate_shortcut_html(shortcut, stype, sidx, False)

        if script_shortcuts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://script">{get_toggle_icon('script')} Script Shortcuts</a></div>
            """

        if self.section_states.get("script", True):
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

        if launcher_shortcuts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://launcher">{get_toggle_icon('launcher')} Launcher Shortcuts</a></div>
            """

        if self.section_states.get("launcher", True):
            if group_by_category:
                launcher_categories = {}
                for shortcut in launcher_shortcuts:
                    category = shortcut.get('category', 'General')
                    if category not in launcher_categories:
                        launcher_categories[category] = []
                    launcher_categories[category].append(shortcut)

                for i, category in enumerate(sorted(launcher_categories.keys())):
                    color = self.get_category_color(category)
                    first_class = " first-in-section" if i == 0 else ""
                    html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                    for shortcut in sorted(launcher_categories[category], key=lambda x: x.get('hotkey', '').lower()):
                        original_index = self.launcher_shortcuts.index(shortcut)
                        html += self.generate_shortcut_html(shortcut, "launcher", original_index, True)
            else:
                for shortcut in sorted(launcher_shortcuts, key=lambda x: x.get('hotkey', '').lower()):
                    original_index = self.launcher_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "launcher", original_index, False)

        if remap_shortcuts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://remap">{get_toggle_icon('remap')} Key Remaps</a></div>
            """

        if self.section_states.get("remap", True):
            if group_by_category:
                remap_categories = {}
                for shortcut in remap_shortcuts:
                    category = shortcut.get('category', 'General')
                    if category not in remap_categories:
                        remap_categories[category] = []
                    remap_categories[category].append(shortcut)

                for i, category in enumerate(sorted(remap_categories.keys())):
                    color = self.get_category_color(category)
                    first_class = " first-in-section" if i == 0 else ""
                    html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                    for shortcut in sorted(remap_categories[category], key=lambda x: x.get('origin_key', '').lower()):
                        original_index = self.remap_shortcuts.index(shortcut)
                        html += self.generate_shortcut_html(shortcut, "remap", original_index, True)
            else:
                for shortcut in sorted(remap_shortcuts, key=lambda x: x.get('origin_key', '').lower()):
                    original_index = self.remap_shortcuts.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "remap", original_index, False)

        html += f"""
                </div>
                <div class="column">
        """
        if context_shortcuts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://context">{get_toggle_icon('context')} Context Shortcuts</a></div>
            """

        if self.section_states.get("context", True):
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

        if exclusion_rules:
            html += f"""
                    <div class="section-title"><a href="toggle-section://exclude">{get_toggle_icon('exclude')} Exclusion Rules</a></div>
            """

        if self.section_states.get("exclude", True):
            if group_by_category:
                exclusion_categories = {}
                for shortcut in exclusion_rules:
                    category = shortcut.get('category', 'General')
                    if category not in exclusion_categories:
                        exclusion_categories[category] = []
                    exclusion_categories[category].append(shortcut)

                for i, category in enumerate(sorted(exclusion_categories.keys())):
                    color = self.get_category_color(category)
                    first_class = " first-in-section" if i == 0 else ""
                    html += f'<div class="category-header{first_class}" style="color: {color};">📁 {category}</div>'

                    for shortcut in sorted(exclusion_categories[category], key=lambda x: x.get('name', '').lower()):
                        original_index = self.exclusion_rules.index(shortcut)
                        html += self.generate_shortcut_html(shortcut, "exclude", original_index, True)
            else:
                for shortcut in sorted(exclusion_rules, key=lambda x: x.get('name', '').lower()):
                    original_index = self.exclusion_rules.index(shortcut)
                    html += self.generate_shortcut_html(shortcut, "exclude", original_index, False)

        if startup_scripts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://startup">{get_toggle_icon('startup')} Background Scripts</a></div>
            """

        if self.section_states.get("startup", True):
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

        html += f"""
                </div>
                <div class="column">
        """
        if text_shortcuts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://text">{get_toggle_icon('text')} Text Shortcuts</a></div>
            """

        if self.section_states.get("text", True):
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

        if file_shortcuts:
            html += f"""
                    <div class="section-title"><a href="toggle-section://file">{get_toggle_icon('file')} File Shortcuts</a></div>
            """

        if self.section_states.get("file", True):
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
        elif shortcut_type == "launcher":
            key = shortcut.get('hotkey', '')
            key_width = 170
        elif shortcut_type == "remap":
            origin = shortcut.get('origin_key', '')
            dest = shortcut.get('destination_key', '')
            key = f"{origin} ➔ {dest}"
            key_width = 170
        elif shortcut_type == "context":
            key = shortcut.get('hotkey', '')
            window_title = shortcut.get('window_title', '')
            if window_title:
                key = f"{key} [{window_title[:15]}...]" if len(window_title) > 15 else f"{key} [{window_title}]"
            key_width = 220
        elif shortcut_type == "exclude":
            key = "🚫 Exclusion"
            process_name = shortcut.get('process_name', '')
            window_title = shortcut.get('window_title', '')
            excluded_hotkeys = shortcut.get('excluded_hotkeys', '').strip()
            label_parts = []
            if process_name:
                label_parts.append(process_name.split(',')[0].strip())
            elif window_title:
                t = window_title.split(',')[0].strip()
                label_parts.append(t[:12] + '...' if len(t) > 12 else t)
            if excluded_hotkeys:
                hks = [h.strip() for h in excluded_hotkeys.splitlines() if h.strip()]
                label_parts.append(', '.join(hks[:3]) + ('...' if len(hks) > 3 else ''))
            else:
                label_parts.append('all')
            if label_parts:
                key = f"🚫 [{' | '.join(label_parts)}]"
            key_width = 240
        elif shortcut_type == "startup":
            key = "🚀 Startup"
            context_mode = shortcut.get('context_mode', 'none')
            process_name = shortcut.get('process_name', '')
            window_title = shortcut.get('window_title', '')
            if context_mode in ('active', 'inactive') and any([process_name, window_title]):
                label = (process_name or window_title).split(',')[0].strip()
                label = label[:12] + '...' if len(label) > 12 else label
                prefix = '✅' if context_mode == 'active' else '🚫'
                key = f"🚀 {prefix}[{label}]"
            key_width = 200
        else: # text
            key = shortcut.get('trigger', '')
            key_width = 220
        
        # Ensure icon column is stable
        icon_width = 60

        name = shortcut.get('name', 'Unnamed')
        favourite = shortcut.get('favourite', False)
        fav_icon = '<span style="color: #FCEE0A; font-size: 14px;">⭐</span> ' if favourite else ''
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
            <table width="100%" cellpadding="3" cellspacing="0" style="background-color: {bg_color}; border-radius: 0px; border-collapse: separate;">
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
                                    <td style="padding-left: 15px;" class="shortcut-name" valign="middle">{fav_icon}{name}{desc_html}</td>
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
        elif self.selected_type == "launcher":
            duplicated['hotkey'] = ""
            self.launcher_shortcuts.append(duplicated)
        elif self.selected_type == "context":
            self.context_shortcuts.append(duplicated)
        elif self.selected_type == "exclude":
            self.exclusion_rules.append(duplicated)
        elif self.selected_type == "startup":
            self.startup_scripts.append(duplicated)
        elif self.selected_type == "file":
            self.file_shortcuts.append(duplicated)
        elif self.selected_type == "remap":
            duplicated['origin_key'] = ""
            duplicated['destination_key'] = ""
            self.remap_shortcuts.append(duplicated)
        else:
            self.text_shortcuts.append(duplicated)
        
        # Save and update display
        self.save_shortcuts_json()
        self.update_display()
        
        # Select the new duplicate
        self.selected_shortcut = duplicated
        self.update_display()
        
        # Show success message
        follow_up = "Please edit the duplicate to set a unique hotkey/trigger."
        if self.selected_type == "exclude":
            follow_up = "Please edit the duplicate to adjust the excluded window/app match."
        QMessageBox.information(self, "Success", f"Duplicated '{original_name}' as '{duplicated['name']}'.\n\n{follow_up}")

    def remove_selected(self):
        if not self.selected_shortcut or not self.selected_type:
            QMessageBox.warning(self, "Warning", "Please select a shortcut to remove.")
            return

        reply = QMessageBox.question(self, "Confirm", "Are you sure you want to remove this shortcut?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            if self.selected_type == "script":
                self.script_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "launcher":
                self.launcher_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "context":
                self.context_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "exclude":
                self.exclusion_rules.remove(self.selected_shortcut)
            elif self.selected_type == "startup":
                self.startup_scripts.remove(self.selected_shortcut)
            elif self.selected_type == "file":
                self.file_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "remap":
                self.remap_shortcuts.remove(self.selected_shortcut)
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

            # Sanitization helpers for AHK syntax compatibility
            def escape_hotkey(hotkey: str) -> str:
                # Literal backticks must be doubled in AHK v2 hotkey definitions
                escaped = hotkey.replace("`", "``")
                # Semicolons must be escaped to prevent being interpreted as comment lines
                escaped = escaped.replace(";", "`;")
                return escaped

            def escape_ahk_string(s: str) -> str:
                # Escapes characters inside an AHK double-quoted string literal
                escaped = s.replace("`", "``")
                escaped = escaped.replace('"', '`"')
                return escaped

            def split_startup_script(action_code: str):
                lines = action_code.splitlines()
                init_lines = []
                def_lines = []
                in_definitions = False
                brace_depth = 0
                
                for line in lines:
                    stripped = line.strip()
                    if in_definitions:
                        def_lines.append(line)
                        continue
                        
                    # Comments and blank lines go to initialization
                    if not stripped or stripped.startswith(';'):
                        init_lines.append(line)
                        continue
                    
                    initial_brace_depth = brace_depth
                    
                    # Parse character-by-character to track brace depth and ignore braces in strings/comments
                    in_string = False
                    string_char = None
                    is_escaped = False
                    line_comment = False
                    
                    for i, char in enumerate(line):
                        if line_comment:
                            break
                        if is_escaped:
                            is_escaped = False
                            continue
                        if char == '`': # AHK v2 escape character
                            is_escaped = True
                            continue
                        if char in ('"', "'"):
                            if not in_string:
                                in_string = True
                                string_char = char
                            elif string_char == char:
                                in_string = False
                        elif not in_string:
                            if char == ';':
                                # Semi-colon is comment if at start or preceded by space/tab
                                if i == 0 or line[i-1] in (' ', '\t'):
                                    line_comment = True
                                    break
                            elif char == '{':
                                brace_depth += 1
                            elif char == '}':
                                brace_depth = max(0, brace_depth - 1)
                                
                    # If we were at top-level (brace depth 0) at the start of this line, check for hotkeys/hotstrings/returns
                    if initial_brace_depth == 0:
                        is_hotkey_or_hotstring = False
                        if stripped.startswith(':'):
                            # Hotstrings usually start with a colon (e.g., :X:trigger::, ::trigger::)
                            is_hotkey_or_hotstring = True
                        elif '::' in stripped:
                            parts = stripped.split('::', 1)
                            before = parts[0]
                            # Make sure it's not an assignment or inside quotes
                            if '=' not in before and '"' not in before and "'" not in before and ':=' not in before:
                                is_hotkey_or_hotstring = True
                                
                        is_return_or_exit = False
                        lower_stripped = stripped.lower()
                        if lower_stripped in ('return', 'exit') or lower_stripped.startswith(('return ', 'return\t', 'exit ', 'exit\t')):
                            is_return_or_exit = True
                            
                        if is_hotkey_or_hotstring or is_return_or_exit:
                            in_definitions = True
                            def_lines.append(line)
                            continue
                            
                    init_lines.append(line)
                    
                return '\n'.join(init_lines), '\n'.join(def_lines)

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
                "",
                "OpenFolderInTab(path) {",
                "    winTitle := \"ahk_class CabinetWClass\"",
                "    if WinExist(winTitle) {",
                "        WinActivate(winTitle)",
                "        if WinWaitActive(winTitle, , 2) {",
                "            clipSaved := ClipboardAll()",
                "            A_Clipboard := \"\"",
                "            A_Clipboard := path",
                "            if ClipWait(1) {",
                "                Send \"^t\"",
                "                Sleep 300  ; Allow tab to initialize",
                "                Send \"^l\"",
                "                Sleep 150  ; Focus address bar",
                "                Send \"^v\"",
                "                Sleep 150  ; Paste path",
                "                Send \"{Enter}\"",
                "                Sleep 200  ; Wait before restoring clipboard",
                "            }",
                "            A_Clipboard := clipSaved",
                "            return",
                "        }",
                "    }",
                "    Run(\"explorer.exe `\"\" path \"`\"\")",
                "}",
                "",
                "RunCmd(command) {",
                "    Run(A_ComSpec . \" /c \" . command, , \"Hide\")",
                "}",
                "",
                "RunCmdVisible(command) {",
                "    Run(A_ComSpec . \" /k \" . command)",
                "}",
                "",
                "RunPwsh(command) {",
                "    Run(\"pwsh.exe -NoProfile -Command \" . command, , \"Hide\")",
                "}",
                "",
                "RunPwshVisible(command) {",
                "    Run(\"pwsh.exe -NoProfile -NoExit -Command \" . command)",
                "}",
                "",
                "Class CustomMenu {",
                "    items := []",
                "    __New() {",
                "        this.items := []",
                "    }",
                "    Add(label, action) {",
                "        this.items.Push({label: label, action: action})",
                "    }",
                "    Show() {",
                "        CustomMenuGUI.ShowMenu(this)",
                "    }",
                "}",
                "",
                "Class CustomMenuGUI {",
                "    static guiObj := \"\"",
                "    static guiStack := []",
                "    static activeMenu := \"\"",
                "    static selectedIndex := 0",
                "    static buttons := []",
                f"    static fontName := \"{self.selection_menu_font_family}\"",
                f"    static fontSize := {self.selection_menu_font_size}",
                "    static fontColor := \"Black\"",
                "    static bgColor := \"White\"",
                "    static accentColor := \"0078D7\"",
                "    static borderSize := 1",
                "    static hoverSubmenuObj := \"\"",
                "    static hoverTargetCtrl := \"\"",
                "    static hoverTimerActive := false",
                "    static isTransitioning := false",
                "",
                "    static CancelHoverTimer() {",
                "        if CustomMenuGUI.hoverTimerActive {",
                "            SetTimer(CustomMenuGUI_HoverTimer, 0)",
                "            CustomMenuGUI.hoverTimerActive := false",
                "        }",
                "    }",
                "",
                "    static OnHoverTimer() {",
                "        CustomMenuGUI.hoverTimerActive := false",
                "        MouseGetPos(,, &win, &ctrlHwnd, 2)",
                "        if (ctrlHwnd == CustomMenuGUI.hoverTargetCtrl) {",
                "            if (CustomMenuGUI.hoverSubmenuObj) {",
                "                obj := CustomMenuGUI.hoverSubmenuObj",
                "                CustomMenuGUI.hoverSubmenuObj := \"\"",
                "                CustomMenuGUI.hoverTargetCtrl := \"\"",
                "                CustomMenuGUI.EnterSubmenu(obj)",
                "            }",
                "        } else {",
                "            CustomMenuGUI.hoverSubmenuObj := \"\"",
                "            CustomMenuGUI.hoverTargetCtrl := \"\"",
                "        }",
                "    }",
                "",
                "    static ShowMenu(menuObj) {",
                "        CustomMenuGUI.CloseAll()",
                "        CustomMenuGUI.guiStack := []",
                "        CustomMenuGUI.activeMenu := menuObj",
                "        CustomMenuGUI.selectedIndex := 0",
                "        CustomMenuGUI.CreateGUI()",
                "    }",
                "",
                "    static CreateGUI() {",
                "        guiObj := Gui(\"+AlwaysOnTop -Caption +ToolWindow +Border\")",
                "        guiObj.BackColor := CustomMenuGUI.bgColor",
                "        guiObj.SetFont(\"s\" . CustomMenuGUI.fontSize . \" c\" . CustomMenuGUI.fontColor, CustomMenuGUI.fontName)",
                "        guiObj.MarginX := 8",
                "        guiObj.MarginY := 5",
                "",
                "        try guiObj.OnEvent(\"Escape\", (*) => CustomMenuGUI.CloseAll())",
                "        try guiObj.OnEvent(\"Close\", (*) => CustomMenuGUI.CloseAll())",
                "        buttons := []",
                "",
                "        for idx, item in CustomMenuGUI.activeMenu.items {",
                "            label := item.label",
                "            if (IsObject(item.action) && !HasMethod(item.action, \"Call\")) {",
                "                label := label . \"  >\"",
                "            }",
                "            options := (idx == 1) ? \"Left Background\" . CustomMenuGUI.bgColor : \"y+2 Left Background\" . CustomMenuGUI.bgColor",
                "            btn := guiObj.Add(\"Text\", options, \"  \" . label)",
                "            btn.itemIdx := idx",
                "            btn.OnEvent(\"Click\", (ctrl, *) => CustomMenuGUI.OnItemClick(ctrl.itemIdx))",
                "            buttons.Push({ctrl: btn, isBack: false, itemIdx: idx})",
                "        }",
                "",
                "        maxW := 120",
                "        for btnObj in buttons {",
                "            btnObj.ctrl.GetPos(,, &w, &h)",
                "            if (w > maxW) {",
                "                maxW := w",
                "            }",
                "        }",
                "        maxW += 20",
                "",
                "        for btnObj in buttons {",
                "            btnObj.ctrl.Move(,, maxW)",
                "        }",
                "",
                "        CustomMenuGUI.guiObj := guiObj",
                "        CustomMenuGUI.buttons := buttons",
                "",
                "        OnMessage(0x0100, CustomMenuGUI_KeyDown)",
                "        OnMessage(0x0200, CustomMenuGUI_MouseMove)",
                "        OnMessage(0x0006, CustomMenuGUI_Activate)",
                "",
                "        CustomMenuGUI.HighlightItem()",
                "",
                "        try {",
                "            CoordMode \"Mouse\", \"Screen\"",
                "            MouseGetPos(&mX, &mY)",
                "",
                "            monitorCount := MonitorGetCount()",
                "            monL := 0, monT := 0, monR := A_ScreenWidth, monB := A_ScreenHeight",
                "            Loop monitorCount {",
                "                MonitorGetWorkArea(A_Index, &mL, &mT, &mR, &mB)",
                "                if (mX >= mL && mX <= mR && mY >= mT && mY <= mB) {",
                "                    monL := mL, monT := mT, monR := mR, monB := mB",
                "                    break",
                "                }",
                "            }",
                "",
                "            guiObj.Show(\"Hide AutoSize\")",
                "            guiObj.GetPos(,, &gW, &gH)",
                "",
                "            if (CustomMenuGUI.guiStack.Length > 0) {",
                "                parentObj := CustomMenuGUI.guiStack[CustomMenuGUI.guiStack.Length]",
                "                parentGui := parentObj.gui",
                "                parentGui.GetPos(&gX, &gY, &gW_parent, &gH_parent)",
                "                parentBtnObj := parentObj.buttons[parentObj.idx]",
                "                parentBtnObj.ctrl.GetPos(&cX, &cY, &cW, &cH)",
                "                ",
                "                showX := gX + gW_parent - 3",
                "                showY := gY + cY - 3",
                "                ",
                "                if (showX + gW > monR) {",
                "                    showX := gX - gW + 3",
                "                }",
                "                ",
                "                if (showY + gH > monB) {",
                "                    showY := monB - gH",
                "                }",
                "                if (showY < monT) {",
                "                    showY := monT",
                "                }",
                "                ",
                "                guiObj.Show(\"x\" . showX . \" y\" . showY . \" AutoSize\")",
                "            } else {",
                "                showX := mX - 10",
                "                showY := mY - 10",
                "                ",
                "                if (showX + gW > monR) {",
                "                    showX := mX - gW + 10",
                "                }",
                "                if (showX < monL) {",
                "                    showX := monL",
                "                }",
                "                if (showY + gH > monB) {",
                "                    showY := mY - gH + 10",
                "                }",
                "                if (showY < monT) {",
                "                    showY := monT",
                "                }",
                "                ",
                "                guiObj.Show(\"x\" . showX . \" y\" . showY . \" AutoSize\")",
                "            }",
                "        }",

                "        CustomMenuGUI.isTransitioning := false",
                "    }",
                "",
                "    static HighlightItem() {",
                "        for idx, btnObj in CustomMenuGUI.buttons {",
                "            ctrl := btnObj.ctrl",
                "            try {",
                "                if (idx == CustomMenuGUI.selectedIndex) {",
                "                    ctrl.Opt(\"Background\" . CustomMenuGUI.accentColor)",
                "                    ctrl.SetFont(\"cWhite\")",
                "                } else {",
                "                    ctrl.Opt(\"Background\" . CustomMenuGUI.bgColor)",
                "                    ctrl.SetFont(\"c\" . CustomMenuGUI.fontColor)",
                "                }",
                "            }",
                "        }",
                "    }",
                "",
                "    static OnKeyDown(wParam, lParam, msg, hwnd) {",
                "        if (!CustomMenuGUI.guiObj || hwnd != CustomMenuGUI.guiObj.Hwnd)",
                "            return",
                "",
                "        VK_UP := 0x26",
                "        VK_DOWN := 0x28",
                "        VK_RETURN := 0x0D",
                "        VK_SPACE := 0x20",
                "        VK_LEFT := 0x25",
                "        VK_RIGHT := 0x27",
                "        VK_ESCAPE := 0x1B",
                "",
                "        if (wParam == VK_DOWN) {",
                "            CustomMenuGUI.selectedIndex += 1",
                "            if (CustomMenuGUI.selectedIndex > CustomMenuGUI.buttons.Length)",
                "                CustomMenuGUI.selectedIndex := 1",
                "            CustomMenuGUI.HighlightItem()",
                "            return 0",
                "        }",
                "        else if (wParam == VK_UP) {",
                "            CustomMenuGUI.selectedIndex -= 1",
                "            if (CustomMenuGUI.selectedIndex < 1)",
                "                CustomMenuGUI.selectedIndex := CustomMenuGUI.buttons.Length",
                "            CustomMenuGUI.HighlightItem()",
                "            return 0",
                "        }",
                "        else if (wParam == VK_RETURN || wParam == VK_SPACE) {",
                "            if (CustomMenuGUI.selectedIndex >= 1) {",
                "                CustomMenuGUI.SelectCurrent()",
                "            }",
                "            return 0",
                "        }",
                "        else if (wParam == VK_LEFT) {",
                "            if (CustomMenuGUI.guiStack.Length > 0) {",
                "                CustomMenuGUI.GoBack()",
                "                return 0",
                "            }",
                "        }",
                "        else if (wParam == VK_RIGHT) {",
                "            if (CustomMenuGUI.selectedIndex >= 1) {",
                "                btnObj := CustomMenuGUI.buttons[CustomMenuGUI.selectedIndex]",
                "                if (!btnObj.isBack) {",
                "                    item := CustomMenuGUI.activeMenu.items[btnObj.itemIdx]",
                "                    if (IsObject(item.action) && !HasMethod(item.action, \"Call\")) {",
                "                        CustomMenuGUI.EnterSubmenu(item.action)",
                "                        return 0",
                "                    }",
                "                }",
                "            }",
                "        }",
                "        else if (wParam == VK_ESCAPE) {",
                "            CustomMenuGUI.CloseAll()",
                "            return 0",
                "        }",
                "    }",
                "",
                "    static OnMouseMove(wParam, lParam, msg, hwnd) {",
                "        if (!CustomMenuGUI.guiObj)",
                "            return",
                "        try {",
                "            ctrl := GuiCtrlFromHwnd(hwnd)",
                "            if (!ctrl)",
                "                return",
                "            for idx, btnObj in CustomMenuGUI.buttons {",
                "                if (btnObj.ctrl.Hwnd == ctrl.Hwnd) {",
                "                    if (CustomMenuGUI.selectedIndex != idx) {",
                "                        CustomMenuGUI.selectedIndex := idx",
                "                        CustomMenuGUI.HighlightItem()",
                "                        ",
                "                        CustomMenuGUI.CancelHoverTimer()",
                "                        if (!btnObj.isBack) {",
                "                            item := CustomMenuGUI.activeMenu.items[btnObj.itemIdx]",
                "                            if (IsObject(item.action) && !HasMethod(item.action, \"Call\")) {",
                "                                CustomMenuGUI.hoverSubmenuObj := item.action",
                "                                CustomMenuGUI.hoverTargetCtrl := btnObj.ctrl.Hwnd",
                "                                CustomMenuGUI.hoverTimerActive := true",
                "                                SetTimer(CustomMenuGUI_HoverTimer, -400)",
                "                            }",
                "                        }",
                "                    }",
                "                    return",
                "                }",
                "            }",
                "",
                "            if (CustomMenuGUI.guiStack.Length > 0) {",
                "                loopIndex := CustomMenuGUI.guiStack.Length",
                "                while (loopIndex >= 1) {",
                "                    parentObj := CustomMenuGUI.guiStack[loopIndex]",
                "                    for idx, btnObj in parentObj.buttons {",
                "                        if (btnObj.ctrl.Hwnd == ctrl.Hwnd) {",
                "                            if (parentObj.idx == idx) {",
                "                                return",
                "                            }",
                "                            CustomMenuGUI.isTransitioning := true",
                "                            destroyHelper(guiToDestroy) {",
                "                                try guiToDestroy.Destroy()",
                "                            }",
                "                            activeGui := CustomMenuGUI.guiObj",
                "                            try activeGui.Hide()",
                "                            SetTimer(destroyHelper.Bind(activeGui), -1)",
                "                            while (CustomMenuGUI.guiStack.Length > loopIndex) {",
                "                                intermediate := CustomMenuGUI.guiStack.Pop()",
                "                                try intermediate.gui.Hide()",
                "                                SetTimer(destroyHelper.Bind(intermediate.gui), -1)",
                "                            }",
                "                            matchedParent := CustomMenuGUI.guiStack.Pop()",
                "                            CustomMenuGUI.guiObj := matchedParent.gui",
                "                            CustomMenuGUI.activeMenu := matchedParent.menu",
                "                            CustomMenuGUI.buttons := matchedParent.buttons",
                "                            CustomMenuGUI.selectedIndex := idx",
                "                            CustomMenuGUI.HighlightItem()",
                "                            try CustomMenuGUI.guiObj.Show()",
                "                            CustomMenuGUI.isTransitioning := false",
                "                            CustomMenuGUI.CancelHoverTimer()",
                "                            item := CustomMenuGUI.activeMenu.items[btnObj.itemIdx]",
                "                            if (IsObject(item.action) && !HasMethod(item.action, \"Call\")) {",
                "                                CustomMenuGUI.hoverSubmenuObj := item.action",
                "                                CustomMenuGUI.hoverTargetCtrl := btnObj.ctrl.Hwnd",
                "                                CustomMenuGUI.hoverTimerActive := true",
                "                                SetTimer(CustomMenuGUI_HoverTimer, -400)",
                "                            }",
                "                            return",
                "                        }",
                "                    }",
                "                    loopIndex -= 1",
                "                }",
                "            }",
                "        }",
                "    }",
                "",
                "    static OnActivate(wParam, lParam, msg, hwnd) {",
                "        if (CustomMenuGUI.isTransitioning)",
                "            return",
                "        if (wParam == 0) {",
                "            isDeactivatedMenu := false",
                "            if (CustomMenuGUI.guiObj && hwnd == CustomMenuGUI.guiObj.Hwnd) {",
                "                isDeactivatedMenu := true",
                "            }",
                "            if (!isDeactivatedMenu) {",
                "                for parentObj in CustomMenuGUI.guiStack {",
                "                    if (parentObj.gui && hwnd == parentObj.gui.Hwnd) {",
                "                        isDeactivatedMenu := true",
                "                        break",
                "                    }",
                "                }",
                "            }",
                "            if (isDeactivatedMenu) {",
                "                isActivatedMenu := false",
                "                if (CustomMenuGUI.guiObj && lParam == CustomMenuGUI.guiObj.Hwnd) {",
                "                    isActivatedMenu := true",
                "                }",
                "                if (!isActivatedMenu) {",
                "                    for parentObj in CustomMenuGUI.guiStack {",
                "                        if (parentObj.gui && lParam == parentObj.gui.Hwnd) {",
                "                            isActivatedMenu := true",
                "                            break",
                "                        }",
                "                    }",
                "                }",
                "                if (!isActivatedMenu) {",
                "                    CustomMenuGUI.CloseAll()",
                "                }",
                "            }",
                "        }",
                "    }",
                "",
                "    static SelectCurrent() {",
                "        if (CustomMenuGUI.selectedIndex < 1)",
                "            return",
                "        btnObj := CustomMenuGUI.buttons[CustomMenuGUI.selectedIndex]",
                "        if (btnObj.isBack) {",
                "            CustomMenuGUI.GoBack()",
                "        } else {",
                "            CustomMenuGUI.OnItemClick(btnObj.itemIdx)",
                "        }",
                "    }",
                "",
                "    static OnItemClick(itemIdx) {",
                "        item := CustomMenuGUI.activeMenu.items[itemIdx]",
                "        action := item.action",
                "        ",
                "        if (IsObject(action) && !HasMethod(action, \"Call\")) {",
                "            CustomMenuGUI.EnterSubmenu(action)",
                "        } else {",
                "            CustomMenuGUI.CloseAll()",
                "            if (HasMethod(action, \"Call\")) {",
                "                action(item.label, itemIdx, CustomMenuGUI.activeMenu)",
                "            }",
                "        }",
                "    }",
                "",
                "    static EnterSubmenu(submenuObj) {",
                "        CustomMenuGUI.CancelHoverTimer()",
                "        CustomMenuGUI.isTransitioning := true",
                "        currentGui := CustomMenuGUI.guiObj",
                "        CustomMenuGUI.guiStack.Push({gui: currentGui, menu: CustomMenuGUI.activeMenu, idx: CustomMenuGUI.selectedIndex, buttons: CustomMenuGUI.buttons})",
                "",
                "        CustomMenuGUI.activeMenu := submenuObj",
                "        CustomMenuGUI.selectedIndex := 0",
                "        CustomMenuGUI.CreateGUI()",
                "    }",
                "",
                "    static GoBack() {",
                "        CustomMenuGUI.CancelHoverTimer()",
                "        if (CustomMenuGUI.guiStack.Length == 0)",
                "            return",
                "",
                "        CustomMenuGUI.isTransitioning := true",
                "        parentObj := CustomMenuGUI.guiStack.Pop()",
                "        submenuGui := CustomMenuGUI.guiObj",
                "        try submenuGui.Hide()",
                "        ",
                "        destroyHelper(guiToDestroy) {",
                "            try guiToDestroy.Destroy()",
                "        }",
                "        SetTimer(destroyHelper.Bind(submenuGui), -1)",
                "",
                "        CustomMenuGUI.guiObj := parentObj.gui",
                "        CustomMenuGUI.activeMenu := parentObj.menu",
                "        CustomMenuGUI.selectedIndex := parentObj.idx",
                "        CustomMenuGUI.buttons := parentObj.buttons",
                "        ",
                "        try CustomMenuGUI.guiObj.Show()",
                "        CustomMenuGUI.HighlightItem()",
                "        CustomMenuGUI.isTransitioning := false",
                "    }",
                "",
                "    static CloseAll() {",
                "        CustomMenuGUI.CancelHoverTimer()",
                "        CustomMenuGUI.isTransitioning := false",
                "        OnMessage(0x0100, CustomMenuGUI_KeyDown, 0)",
                "        OnMessage(0x0200, CustomMenuGUI_MouseMove, 0)",
                "        OnMessage(0x0006, CustomMenuGUI_Activate, 0)",
                "",
                "        destroyHelper(guiToDestroy) {",
                "            try guiToDestroy.Destroy()",
                "        }",
                "",
                "        if CustomMenuGUI.guiObj {",
                "            g := CustomMenuGUI.guiObj",
                "            CustomMenuGUI.guiObj := \"\"",
                "            try g.Hide()",
                "            SetTimer(destroyHelper.Bind(g), -1)",
                "        }",
                "",
                "        while (CustomMenuGUI.guiStack.Length > 0) {",
                "            parentObj := CustomMenuGUI.guiStack.Pop()",
                "            g := parentObj.gui",
                "            try g.Hide()",
                "            SetTimer(destroyHelper.Bind(g), -1)",
                "        }",
                "    }",
                "}",
                "",
                "CustomMenuGUI_KeyDown(wParam, lParam, msg, hwnd) {",
                "    return CustomMenuGUI.OnKeyDown(wParam, lParam, msg, hwnd)",
                "}",
                "CustomMenuGUI_MouseMove(wParam, lParam, msg, hwnd) {",
                "    return CustomMenuGUI.OnMouseMove(wParam, lParam, msg, hwnd)",
                "}",
                "CustomMenuGUI_Activate(wParam, lParam, msg, hwnd) {",
                "    return CustomMenuGUI.OnActivate(wParam, lParam, msg, hwnd)",
                "}",
                "CustomMenuGUI_HoverTimer() {",
                "    CustomMenuGUI.OnHoverTimer()",
                "}"
                ""
            ])

            def split_context_values(raw_value):
                return [part.strip() for part in raw_value.split(",") if part.strip()]

            def build_condition_clause(raw_value, matcher):
                values = split_context_values(raw_value)
                if not values:
                    return None
                clauses = [matcher(value) for value in values]
                if len(clauses) == 1:
                    return clauses[0]
                return "(" + " || ".join(clauses) + ")"

            def append_context_checker(shortcut, func_name):
                window_title = shortcut.get('window_title', '') if shortcut.get('window_title_enabled', True) else ''
                process_name = shortcut.get('process_name', '') if shortcut.get('process_name_enabled', True) else ''
                window_class = shortcut.get('window_class', '') if shortcut.get('window_class_enabled', True) else ''
                match_foreground = shortcut.get('match_foreground', False)

                conditions = []
                process_clause = build_condition_clause(process_name, lambda value: f'processName = "{value}"')
                title_clause = build_condition_clause(window_title, lambda value: f'InStr(windowTitle, "{value}")')
                class_clause = build_condition_clause(window_class, lambda value: f'windowClass = "{value}"')

                if process_clause:
                    conditions.append(process_clause)
                if title_clause:
                    conditions.append(title_clause)
                if class_clause:
                    conditions.append(class_clause)

                output_lines.append(f"{func_name}() {{")
                output_lines.append("    try {")
                if match_foreground:
                    # Return the hwnd of the first matching window (0 if none)
                    output_lines.append("        for hwnd in WinGetList() {")
                    if process_name:
                        output_lines.append('            processName := WinGetProcessName(hwnd)')
                    if window_title:
                        output_lines.append('            windowTitle := WinGetTitle(hwnd)')
                    if window_class:
                        output_lines.append('            windowClass := WinGetClass(hwnd)')
                    if conditions:
                        output_lines.append("            if (" + " && ".join(conditions) + ")")
                        output_lines.append("                return hwnd")
                    output_lines.append("        }")
                    output_lines.append("        return 0")
                else:
                    if process_name:
                        output_lines.append('        processName := WinGetProcessName("A")')
                    if window_title:
                        output_lines.append('        windowTitle := WinGetTitle("A")')
                    if window_class:
                        output_lines.append('        windowClass := WinGetClass("A")')
                    if conditions:
                        output_lines.append("        return (" + " && ".join(conditions) + ")")
                    else:
                        output_lines.append("        return false")
                output_lines.append("    }")
                output_lines.append("    return " + ("0" if match_foreground else "false"))
                output_lines.append("}")
                output_lines.append("")

            def build_rule_clause(shortcut):
                window_title = shortcut.get('window_title', '') if shortcut.get('window_title_enabled', True) else ''
                process_name = shortcut.get('process_name', '') if shortcut.get('process_name_enabled', True) else ''
                window_class = shortcut.get('window_class', '') if shortcut.get('window_class_enabled', True) else ''

                conditions = []
                process_clause = build_condition_clause(process_name, lambda value: f'processName = "{value}"')
                title_clause = build_condition_clause(window_title, lambda value: f'InStr(windowTitle, "{value}")')
                class_clause = build_condition_clause(window_class, lambda value: f'windowClass = "{value}"')

                if process_clause:
                    conditions.append(process_clause)
                if title_clause:
                    conditions.append(title_clause)
                if class_clause:
                    conditions.append(class_clause)

                if not conditions:
                    return None
                return "(" + " && ".join(conditions) + ")"

            def append_exclusion_checker():
                enabled_exclusions = [s for s in self.exclusion_rules if s.get('enabled', True)]
                rule_clauses = []
                has_title = False
                has_process = False
                has_class = False
                for shortcut in enabled_exclusions:
                    clause = build_rule_clause(shortcut)
                    if clause:
                        rule_clauses.append(clause)
                        if shortcut.get('window_title'):
                            has_title = True
                        if shortcut.get('process_name'):
                            has_process = True
                        if shortcut.get('window_class'):
                            has_class = True

                output_lines.append(";! === EXCLUSION RULES ===")
                output_lines.append("IsShortcutExcluded() {")
                output_lines.append("    try {")
                if has_process:
                    output_lines.append('        processName := WinGetProcessName("A")')
                if has_title:
                    output_lines.append('        windowTitle := WinGetTitle("A")')
                if has_class:
                    output_lines.append('        windowClass := WinGetClass("A")')
                if rule_clauses:
                    output_lines.append("        return " + " || ".join(rule_clauses))
                else:
                    output_lines.append("        return false")
                output_lines.append("    }")
                output_lines.append("    return false")
                output_lines.append("}")
                output_lines.append("")

            # Add Background/Startup Scripts at the top (Auto-execute section)
            enabled_startup = [s for s in self.startup_scripts if s.get('enabled', True)]
            startup_definitions = []
            
            if enabled_startup:
                output_lines.append(";! === BACKGROUND / STARTUP SCRIPTS (INITIALIZATION) ===")
                for shortcut in enabled_startup:
                    action = shortcut.get('action', '')
                    action = action.replace(',,,', ',,')
                    
                    init_part, def_part = split_startup_script(action)
                    
                    # Add initialization part if not empty
                    if init_part.strip():
                        output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                        if shortcut.get('description'):
                            output_lines.append(f";! {shortcut.get('description')}")
                        output_lines.append(init_part)
                        output_lines.append("")
                        
                    # Save definition/hotkey part if not empty
                    if def_part.strip():
                        startup_definitions.append((shortcut, def_part))

            append_exclusion_checker()

            # Add Background/Startup Scripts Hotkeys & Definitions (after the auto-execute section)
            if startup_definitions:
                output_lines.append(";! === BACKGROUND / STARTUP SCRIPTS (DEFINITIONS & HOTKEYS) ===")
                for shortcut, def_part in startup_definitions:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                        
                    context_mode = shortcut.get('context_mode', 'none')
                    window_title = shortcut.get('window_title', '') if shortcut.get('window_title_enabled', True) else ''
                    process_name = shortcut.get('process_name', '') if shortcut.get('process_name_enabled', True) else ''
                    window_class = shortcut.get('window_class', '') if shortcut.get('window_class_enabled', True) else ''
                    has_context = context_mode in ('active', 'inactive') and any([window_title, process_name, window_class])

                    if has_context:
                        safe_name = re.sub(r'[^a-zA-Z0-9]', '', shortcut.get('name', 'Script'))
                        func_name = f"IsStartup{safe_name}Context"
                        append_context_checker(shortcut, func_name)
                        guard = func_name + "()"
                        if context_mode == 'inactive':
                            guard = "!" + guard
                        output_lines.append(f"#HotIf {guard}")

                    output_lines.append(def_part)

                    if has_context:
                        output_lines.append("#HotIf")
                    output_lines.append("")

            # Build exclusion map: which hotkeys are excluded (empty set = all)
            enabled_exclusions = [s for s in self.exclusion_rules if s.get('enabled', True)]
            exclude_all_hotkeys = any(
                not s.get('excluded_hotkeys', '').strip() for s in enabled_exclusions
            )
            specifically_excluded = set()
            for s in enabled_exclusions:
                raw = s.get('excluded_hotkeys', '').strip()
                if raw:
                    for line in raw.splitlines():
                        hk = line.strip()
                        if hk:
                            specifically_excluded.add(hk)

            def needs_exclusion_guard(hotkey):
                return exclude_all_hotkeys or hotkey in specifically_excluded

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
                    action = action.replace(',,,', ',,')

                    guarded = needs_exclusion_guard(hotkey)
                    if guarded:
                        output_lines.append("#HotIf !IsShortcutExcluded()")

                    safe_hotkey = escape_hotkey(hotkey)

                    if '\n' in action:
                        output_lines.append(f"{safe_hotkey}:: {{")
                        lines = [l.strip() for l in action.split('\n') if l.strip()]
                        match = re.search(r"^\s*([a-zA-Z0-9_]+)\s*\([^)]*\)\s*\{", action, re.MULTILINE)
                        if match and len(lines) > 0:
                            func_name = match.group(1)
                            if lines[0].startswith(f"{func_name}(") and not any(l.strip() == f"{func_name}()" for l in lines):
                                output_lines.append(f"    {func_name}()")
                        for line in action.split('\n'):
                            if line.strip():
                                output_lines.append(f"    {line}")
                        output_lines.append("}")
                    else:
                        output_lines.append(f"{safe_hotkey}::{action}")

                    if guarded:
                        output_lines.append("#HotIf")
                    output_lines.append("")
                output_lines.append("")

            # Helper to parse Windows command line arguments robustly
            def parse_windows_command_line(cmd_str):
                cmd_str = cmd_str.strip()
                if not cmd_str:
                    return "", ""
                
                # Unpack outer Run('...') if user accidentally typed or pasted full Run statement
                run_match = re.match(r'^\s*Run\s*\(\s*[\'"](.*?)[\'"]\s*(?:,\s*(.*?)\s*)?(?:,\s*[\'"](.*?)[\'"]\s*)?\)\s*$', cmd_str, re.IGNORECASE)
                if run_match:
                    cmd_str = run_match.group(1).strip()

                # Check if it starts with quote
                if cmd_str.startswith('"'):
                    closing_idx = cmd_str.find('"', 1)
                    if closing_idx != -1:
                        exe_path = cmd_str[1:closing_idx]
                        args = cmd_str[closing_idx+1:].strip()
                        return exe_path, args
                elif cmd_str.startswith("'"):
                    closing_idx = cmd_str.find("'", 1)
                    if closing_idx != -1:
                        exe_path = cmd_str[1:closing_idx]
                        args = cmd_str[closing_idx+1:].strip()
                        return exe_path, args
                        
                if " " not in cmd_str:
                    return cmd_str, ""
                    
                first_part = cmd_str.split(" ", 1)[0].lower()
                if first_part in ("python.exe", "pythonw.exe", "python", "pythonw", "py.exe", "pyw.exe", "py", "pyw", "cmd.exe", "cmd", "powershell.exe", "powershell", "pwsh.exe", "pwsh"):
                    return cmd_str.split(" ", 1)[0], cmd_str.split(" ", 1)[1].strip()
                    
                # Look for known extensions with a trailing boundary (space or end of line)
                # This ensures we don't break mid-path if there's an extension inside the folder name
                for ext in (".pyw", ".py", ".exe", ".bat", ".cmd", ".ps1"):
                    match = re.search(re.escape(ext) + r'(?:\s|$)', cmd_str, re.IGNORECASE)
                    if match:
                        idx = match.end()
                        exe_path = cmd_str[:idx].strip()
                        args = cmd_str[idx:].strip()
                        if (exe_path.startswith('"') and exe_path.endswith('"')) or (exe_path.startswith("'") and exe_path.endswith("'")):
                            exe_path = exe_path[1:-1]
                        return exe_path, args
                        
                parts = cmd_str.split(" ", 1)
                return parts[0], parts[1].strip()

            # Add launcher shortcuts
            enabled_launchers = [s for s in self.launcher_shortcuts if s.get('enabled', True)]
            if enabled_launchers:
                output_lines.append(";! === LAUNCHER SHORTCUTS ===")
                for shortcut in enabled_launchers:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")

                    target_path = shortcut.get('target_path', '')
                    hotkey = shortcut.get('hotkey', '')
                    hide_terminal = shortcut.get('hide_terminal', True)

                    # Extract executable/script and its arguments
                    exe_path, args_part = parse_windows_command_line(target_path)
                    exe_path = exe_path.replace('/', '\\')

                    is_python = False
                    script_path = ""
                    python_interpreter = ""

                    # Detect if explicitly starting with a Python interpreter
                    exe_name = os.path.basename(exe_path).lower()
                    if exe_name in ("python.exe", "pythonw.exe", "python", "pythonw", "py.exe", "pyw.exe", "py", "pyw"):
                        is_python = True
                        python_interpreter = exe_path
                        if args_part:
                            script_match = re.match(r'^\s*"([^"]+)"(.*)$', args_part)
                            if not script_match:
                                script_match = re.match(r'^\s*\'([^\']+)\'(.*)$', args_part)
                            if not script_match:
                                script_match = re.match(r'^\s*([^\s]+)(.*)$', args_part)
                                
                            if script_match:
                                script_path = script_match.group(1).strip()
                                args_part = script_match.group(2).strip()
                            else:
                                script_path = args_part.strip()
                                args_part = ""
                    elif exe_path.lower().endswith(('.py', '.pyw')):
                        is_python = True
                        script_path = exe_path
                        python_interpreter = "pythonw.exe" if hide_terminal else "python.exe"

                    # Determine working directory dynamically
                    path_for_wdir = script_path if script_path else exe_path
                    working_dir = ""
                    if path_for_wdir and ("\\" in path_for_wdir or "/" in path_for_wdir):
                        try:
                            if not path_for_wdir.startswith("@"):
                                working_dir = os.path.dirname(path_for_wdir)
                        except Exception:
                            working_dir = ""

                    # Build Command String
                    if is_python:
                        if "\\" in python_interpreter or "/" in python_interpreter:
                            py_exe = python_interpreter
                            if hide_terminal and py_exe.lower().endswith("python.exe"):
                                py_exe = py_exe[:-10] + "pythonw.exe"
                            elif not hide_terminal and py_exe.lower().endswith("pythonw.exe"):
                                py_exe = py_exe[:-11] + "python.exe"
                        else:
                            py_exe = "pythonw.exe" if hide_terminal else "python.exe"
                        
                        cmd_str = f'{py_exe} "{script_path}"'
                        if args_part:
                            cmd_str += f' {args_part}'
                    elif exe_path.lower().endswith('.ps1'):
                        ps_options = "-WindowStyle Hidden -File" if hide_terminal else "-NoExit -File"
                        cmd_str = f'powershell.exe {ps_options} "{exe_path}"'
                        if args_part:
                            cmd_str += f' {args_part}'
                    else:
                        cmd_str = f'"{exe_path}"'
                        if args_part:
                            cmd_str += f' {args_part}'

                    # Escape and format AHK parameters
                    safe_cmd_str = cmd_str.replace("'", "''")
                    safe_working_dir = working_dir.replace("'", "''") if working_dir else ""
                    
                    # If it is Python and hide_terminal is True, we run the script with pythonw.exe
                    # which naturally suppresses the console window. We omit the "Hide" parameter 
                    # from AHK's Run command so any GUI windows created by the script can be seen.
                    if is_python and hide_terminal:
                        hide_opt = ''
                    else:
                        hide_opt = '"Hide"' if hide_terminal else ''

                    if safe_working_dir:
                        if hide_opt:
                            action = f"Run('{safe_cmd_str}', '{safe_working_dir}', {hide_opt})"
                        else:
                            action = f"Run('{safe_cmd_str}', '{safe_working_dir}')"
                    else:
                        if hide_opt:
                            action = f"Run('{safe_cmd_str}', , {hide_opt})"
                        else:
                            action = f"Run('{safe_cmd_str}')"

                    guarded = needs_exclusion_guard(hotkey)
                    if guarded:
                        output_lines.append("#HotIf !IsShortcutExcluded()")

                    safe_hotkey = escape_hotkey(hotkey)
                    output_lines.append(f"{safe_hotkey}::{action}")

                    if guarded:
                        output_lines.append("#HotIf")
                    output_lines.append("")
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
                    
                    # Generate unique function name
                    func_name = f"Is{re.sub(r'[^a-zA-Z0-9]', '', shortcut.get('name', 'Context'))}Context"
                    match_foreground = shortcut.get('match_foreground', False)
                    # Context is active if at least one field is enabled and non-empty
                    has_context_fields = any([
                        shortcut.get('window_title_enabled', True) and shortcut.get('window_title', ''),
                        shortcut.get('process_name_enabled', True) and shortcut.get('process_name', ''),
                        shortcut.get('window_class_enabled', True) and shortcut.get('window_class', ''),
                    ])
                    if has_context_fields:
                        append_context_checker(shortcut, func_name)

                    hotkey = shortcut.get('hotkey', '')
                    action = shortcut.get('action', '')
                    action = action.replace(',,,', ',,')

                    safe_hotkey = escape_hotkey(hotkey)

                    if match_foreground and has_context_fields:
                        # Strip outer braces if action is wrapped in them
                        stripped = action.strip()
                        if stripped.startswith('{') and stripped.endswith('}'):
                            action_lines = stripped[1:-1].strip().splitlines()
                        else:
                            action_lines = action.splitlines()
                        # Global hotkey: find matching window, activate it, then run action
                        output_lines.append(f"{safe_hotkey}:: {{")
                        output_lines.append(f"    hwnd := {func_name}()")
                        output_lines.append("    if hwnd {")
                        output_lines.append("        WinActivate(hwnd)")
                        output_lines.append("        Sleep(100)")
                        for line in action_lines:
                            if line.strip():
                                output_lines.append(f"        {line.strip()}")
                        output_lines.append("    } else {")
                        # Hotkey syntax -> Send syntax: bare keys need {}, modifier prefixes don't
                        if hotkey and hotkey[0] in ('^', '!', '+', '#'):
                            send_key = hotkey
                        else:
                            send_key = '{' + hotkey + '}'
                        
                        safe_hotkey_str = escape_ahk_string(hotkey)
                        safe_send_key_str = escape_ahk_string(send_key)

                        output_lines.append(f'        Hotkey "{safe_hotkey_str}", "Off"')
                        output_lines.append(f'        Send("{safe_send_key_str}")')
                        output_lines.append(f'        Hotkey "{safe_hotkey_str}", "On"')
                        output_lines.append("    }")
                        output_lines.append("}")
                    else:
                        # Normal #HotIf approach
                        if has_context_fields:
                            if needs_exclusion_guard(hotkey):
                                output_lines.append(f"#HotIf {func_name}() && !IsShortcutExcluded()")
                            else:
                                output_lines.append(f"#HotIf {func_name}()")
                        elif needs_exclusion_guard(hotkey):
                            output_lines.append(f"#HotIf !IsShortcutExcluded()")
                        hotif_opened = has_context_fields or needs_exclusion_guard(hotkey)
                        output_lines.append("")

                        if '\n' in action:
                            output_lines.append(f"{safe_hotkey}:: {{")
                            for line in action.split('\n'):
                                if line.strip():
                                    output_lines.append(f"    {line}")
                            output_lines.append("}")
                        else:
                            output_lines.append(f"{safe_hotkey}::{action}")
                        output_lines.append("")
                        if hotif_opened:
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
                    # Resolve delivery method (backward compat with use_clipboard)
                    delivery_method = shortcut.get('delivery_method', '')
                    if not delivery_method:
                        delivery_method = 'paste' if shortcut.get('use_clipboard', True) else 'sendtext'
                    
                    # Handle Context if specified
                    func_name = f"Is{re.sub(r'[^a-zA-Z0-9]', '', shortcut.get('name', 'Text'))}Context"
                    has_context_fields = any([
                        shortcut.get('window_title_enabled', False) and shortcut.get('window_title', ''),
                        shortcut.get('process_name_enabled', False) and shortcut.get('process_name', ''),
                        shortcut.get('window_class_enabled', False) and shortcut.get('window_class', ''),
                    ])
                    
                    if has_context_fields:
                        append_context_checker(shortcut, func_name)
                        output_lines.append(f"#HotIf {func_name}()")

                    show_as_menu = shortcut.get('show_as_menu', False)

                    # Determine if the trigger is a hotkey or a hotstring
                    is_hotkey = False
                    if trigger:
                        if any(trigger.startswith(c) for c in ['^', '!', '+', '#', '*', '~', '$', '<', '>']) or ' & ' in trigger:
                            is_hotkey = True
                        else:
                            common_hotkey_words = ['ctrl', 'alt', 'shift', 'win', 'scrolllock', 'printscreen', 'capslock', 'numlock']
                            if any(word in trigger.lower() for word in common_hotkey_words):
                                is_hotkey = True

                    safe_trigger = escape_hotkey(trigger)
                    prefix_x = "" if is_hotkey else ":X:"

                    if show_as_menu and '\n' in replacement:
                        output_lines.append(f"{prefix_x}{safe_trigger}:: {{")
                        output_lines.append("    m := CustomMenu()")
                        
                        paste_func_map = {"paste": "Paste", "sendtext": "SendText", "sendinput": "SendInput", "sendevent": "SendEvent"}
                        paste_func = paste_func_map.get(delivery_method, "Paste")
                        
                        # Parsing logic for hierarchical options with brackets [name:X][text:Y][folder:Z]
                        raw_lines = replacement.split('\n')
                        parsed_items = []
                        for line in raw_lines:
                            if not line.strip():
                                continue
                            
                            # Count leading dashes for submenu level (clamp at 5)
                            stripped = line.lstrip('-')
                            level = len(line) - len(stripped)
                            level = min(level, 5)
                            stripped = stripped.strip()
                            
                            # Extract all bracketed tags [key:value] or [value]
                            blocks = re.findall(r'\[([^\]]*)\]', stripped)
                            
                            tags = {}
                            if not blocks:
                                # Backward compatibility: treat the non-empty stripped line as both name and text
                                if stripped:
                                    tags['name'] = stripped
                                    tags['text'] = stripped
                            else:
                                for block in blocks:
                                    if ':' in block:
                                        k, v = block.split(':', 1)
                                        k = k.strip().lower()
                                        v = v.strip()
                                        tags[k] = v
                                    else:
                                        # Default to text action if no colon
                                        tags['text'] = block.strip()
                                
                                # Default name if not specified
                                if 'name' not in tags:
                                    if 'text' in tags:
                                        tags['name'] = tags['text']
                                    elif 'folder' in tags:
                                        tags['name'] = f"Open {tags['folder']}"
                                    elif 'cmd' in tags:
                                        tags['name'] = tags['cmd']
                                    elif tags:
                                        tags['name'] = list(tags.values())[0]
                                    else:
                                        tags['name'] = "Unnamed"
                            
                            if tags:
                                parsed_items.append((level, tags))
                        
                        # Build the hierarchical tree
                        root_nodes = []
                        active_nodes = { -1: None }
                        for lvl, tags in parsed_items:
                            node = {
                                'level': lvl,
                                'tags': tags,
                                'children': [],
                                'parent': None
                            }
                            parent_lvl = lvl - 1
                            parent_node = active_nodes.get(parent_lvl)
                            if parent_node is not None:
                                parent_node['children'].append(node)
                                node['parent'] = parent_node
                            else:
                                root_nodes.append(node)
                            
                            active_nodes[lvl] = node
                            # Clear deeper levels
                            for l in list(active_nodes.keys()):
                                if l > lvl:
                                    del active_nodes[l]
                        
                        menu_counter = 0
                        
                        def get_modular_action_code(tags, p_func):
                            if 'folder' in tags:
                                safe_folder = escape_ahk_string(tags['folder'])
                                return f'OpenFolderInTab("{safe_folder}")'
                            elif 'cmd' in tags:
                                safe_cmd = escape_ahk_string(tags['cmd'])
                                show_mode = tags.get('show', '').lower()
                                shell = tags.get('shell', '').lower()
                                if shell in ('pwsh', 'powershell'):
                                    if show_mode == 'visible':
                                        return f'RunPwshVisible("{safe_cmd}")'
                                    return f'RunPwsh("{safe_cmd}")'
                                else:
                                    if show_mode == 'visible':
                                        return f'RunCmdVisible("{safe_cmd}")'
                                    return f'RunCmd("{safe_cmd}")'
                            elif 'text' in tags:
                                safe_text = escape_ahk_string(tags['text'])
                                return f'{p_func}("{safe_text}")'
                            return 'return'

                        def generate_menu_node(node, parent_menu_var):
                            nonlocal menu_counter
                            if node['children']:
                                menu_counter += 1
                                submenu_var = f"m_{menu_counter}"
                                output_lines.append(f"    {submenu_var} := CustomMenu()")
                                
                                added_names = set()
                                for child in node['children']:
                                    display_name = child['tags'].get('name', 'Unnamed')
                                    while display_name in added_names:
                                        display_name += " "
                                    added_names.add(display_name)
                                    safe_display = escape_ahk_string(display_name)
                                    
                                    if child['children']:
                                        child_menu_var = generate_menu_node(child, submenu_var)
                                        output_lines.append(f'    {submenu_var}.Add("{safe_display}", {child_menu_var})')
                                    else:
                                        action_code = get_modular_action_code(child['tags'], paste_func)
                                        output_lines.append(f'    {submenu_var}.Add("{safe_display}", (ItemName, ItemPos, MyMenu) => {action_code})')
                                return submenu_var
                            return None

                        added_names = set()
                        for node in root_nodes:
                            display_name = node['tags'].get('name', 'Unnamed')
                            while display_name in added_names:
                                display_name += " "
                            added_names.add(display_name)
                            safe_display = escape_ahk_string(display_name)
                            
                            if node['children']:
                                submenu_var = generate_menu_node(node, "m")
                                output_lines.append(f'    m.Add("{safe_display}", {submenu_var})')
                            else:
                                action_code = get_modular_action_code(node['tags'], paste_func)
                                output_lines.append(f'    m.Add("{safe_display}", (ItemName, ItemPos, MyMenu) => {action_code})')
                        
                        output_lines.append("    m.Show()")
                        output_lines.append("}")
                    else:
                        if delivery_method == 'paste':
                            if '\n' in replacement:
                                output_lines.append(f"{prefix_x}{safe_trigger}::Paste(\"")
                                output_lines.append("(") 
                                lines = replacement.split('\n')
                                for line in lines:
                                    if line.strip().startswith(")"):
                                        output_lines.append("`" + line)
                                    else:
                                        output_lines.append(line)
                                output_lines.append(")\")")
                            else:
                                safe_replacement = replacement.replace("'", "''")
                                output_lines.append(f"{prefix_x}{safe_trigger}::Paste('{safe_replacement}')")
                        elif delivery_method == 'sendinput':
                            safe_replacement = replacement.replace('"', '""').replace('`', '``')
                            if '\n' in replacement:
                                output_lines.append(f"{prefix_x}{safe_trigger}:: {{")
                                output_lines.append('    old := A_SendMode')
                                output_lines.append('    SendMode("Input")')
                                output_lines.append(f'    SendText("')
                                output_lines.append("(")
                                lines = replacement.split('\n')
                                for line in lines:
                                    l = "`" + line if line.strip().startswith(")") else line
                                    output_lines.append(l)
                                output_lines.append(')")')
                                output_lines.append('    SendMode(old)')
                                output_lines.append("}")
                            else:
                                output_lines.append(f"{prefix_x}{safe_trigger}:: {{")
                                output_lines.append('    old := A_SendMode')
                                output_lines.append('    SendMode("Input")')
                                output_lines.append(f'    SendText("{safe_replacement}")')
                                output_lines.append('    SendMode(old)')
                                output_lines.append("}")
                        elif delivery_method == 'sendevent':
                            safe_replacement = replacement.replace('"', '""').replace('`', '``')
                            if '\n' in replacement:
                                output_lines.append(f"{prefix_x}{safe_trigger}:: {{")
                                output_lines.append('    old := A_SendMode')
                                output_lines.append('    SendMode("Event")')
                                output_lines.append('    oldDelay := A_KeyDelay')
                                output_lines.append('    SetKeyDelay(10, 10)')
                                output_lines.append(f'    SendText("')
                                output_lines.append("(")
                                lines = replacement.split('\n')
                                for line in lines:
                                    l = "`" + line if line.strip().startswith(")") else line
                                    output_lines.append(l)
                                output_lines.append(')")')
                                output_lines.append('    SetKeyDelay(oldDelay)')
                                output_lines.append('    SendMode(old)')
                                output_lines.append("}")
                            else:
                                output_lines.append(f"{prefix_x}{safe_trigger}:: {{")
                                output_lines.append('    old := A_SendMode')
                                output_lines.append('    SendMode("Event")')
                                output_lines.append('    oldDelay := A_KeyDelay')
                                output_lines.append('    SetKeyDelay(10, 10)')
                                output_lines.append(f'    SendText("{safe_replacement}")')
                                output_lines.append('    SetKeyDelay(oldDelay)')
                                output_lines.append('    SendMode(old)')
                                output_lines.append("}")
                        else:
                            # Default: SendText (typing mode)
                            safe_replacement = replacement.replace('"', '""').replace('`', '``')
                            if '\n' in replacement:
                                output_lines.append(f"{prefix_x}{safe_trigger}::SendText(\"")
                                output_lines.append("(")
                                lines = replacement.split('\n')
                                for i, line in enumerate(lines):
                                    l = "`" + line if line.strip().startswith(")") else line
                                    output_lines.append(l)
                                output_lines.append(")\")")
                            else:
                                output_lines.append(f'{prefix_x}{safe_trigger}::SendText("{safe_replacement}")')
                    
                    if has_context_fields:
                        output_lines.append("#HotIf")
                    output_lines.append("")
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
                output_lines.append("")

            # Add key remaps
            enabled_remaps = [s for s in self.remap_shortcuts if s.get('enabled', True)]
            if enabled_remaps:
                output_lines.append(";! === KEY REMAPS ===")
                for shortcut in enabled_remaps:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")
                    
                    origin = shortcut.get('origin_key', '')
                    dest = shortcut.get('destination_key', '')
                    
                    safe_origin = escape_hotkey(origin)
                    safe_dest = escape_hotkey(dest)
                    
                    output_lines.append(f"{safe_origin}::{safe_dest}")
                    output_lines.append("")
                output_lines.append("")

            output_dir = SCRIPT_DIR
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
