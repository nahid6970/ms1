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
            self.update_icon(CP_YELLOW if self.color == CP_DIM else CP_BG)
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
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
    ]

    KEY_STYLE = """
        QPushButton {{
            background: {bg};
            color: {fg};
            border: 2px solid {border};
            border-radius: 0px;
            font-size: 11px;
            font-weight: normal;
            padding: 0px;
            min-height: 32px;
            min-width: {w}px;
        }}
        QPushButton:hover {{ background: #3a4a5a; border-color: #61dafb; color: #61dafb; }}
        QPushButton:pressed {{ background: #4a90d9; }}
    """
    KEY_STYLE_ACTIVE = """
        QPushButton {{
            background: #61dafb; color: #1a1a2e;
            border: 2px solid #61dafb; border-radius: 0px;
            font-size: 11px; font-weight: normal;
            padding: 0px;
            min-height: 32px; min-width: {w}px;
        }}
    """
    MOD_STYLE = """
        QPushButton {{
            background: {bg}; color: {fg};
            border: {border}; border-radius: 0px;
            font-size: 13px; font-weight: normal;
            padding: 0px 6px;
            min-height: 36px;
            min-width: {w}px;
        }}
        QPushButton:hover {{ background: #3a4a5a; border: 2px solid #61dafb; color: #61dafb; }}
    """

    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.setWindowTitle("⌨  Shortcut Builder")
        self.setModal(True)
        self.setStyleSheet("QDialog { background: #1a1a2e; color: #e0e0e0; }")
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
    def _key_btn(self, label, width=34, expand=False):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if expand:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        elif width > 0:
            btn.setFixedWidth(width)
        active = (label.lower() == self.main_key.lower())
        btn.setChecked(active)
        self._apply_key_style(btn, active, 0 if (expand or width == 0) else width)
        btn.clicked.connect(lambda _, k=label: self.select_key(k))
        self._key_buttons[label] = btn
        return btn

    def _apply_key_style(self, btn, active, width=34):
        if active:
            btn.setStyleSheet(self.KEY_STYLE_ACTIVE.format(w=width))
        else:
            btn.setStyleSheet(self.KEY_STYLE.format(bg="#252540", fg="#c8d0e0", border="#55556a", w=width))

    # ── Modifier button ───────────────────────────────────────────────
    def _mod_btn(self, sym, label, width=52):
        btn = QPushButton(label)
        btn.setCheckable(True)
        btn.setChecked(self.mods[sym])
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn.setFixedWidth(width)
        self._apply_mod_style(btn, self.mods[sym])
        btn.toggled.connect(lambda checked, s=sym: self.toggle_mod(s, checked))
        self._mod_buttons[sym].append(btn)
        return btn

    def _apply_mod_style(self, btn, active):
        if active:
            btn.setStyleSheet(self.MOD_STYLE.format(bg="#61dafb", fg="#1a1a2e", border="2px solid #61dafb", fw="normal", w=0))
        else:
            btn.setStyleSheet(self.MOD_STYLE.format(bg="#1e1e38", fg="#8090a8", border="2px solid #55556a", fw="normal", w=0))

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
        preview_frame.setStyleSheet("background: #0d0d1a; border-radius: 8px; border: 1px solid #2a2a4a;")
        pf = QVBoxLayout(preview_frame); pf.setContentsMargins(10, 8, 10, 8)
        self.preview_label = QLabel(self.get_formatted_preview())
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #61dafb; letter-spacing: 2px; background: transparent; border: none;")
        pf.addWidget(self.preview_label)
        layout.addWidget(preview_frame)

        # ── Keyboard ──────────────────────────────────────────────────
        kb_frame = QFrame()
        kb_frame.setStyleSheet("background: #12122a; border-radius: 10px; padding: 6px;")
        kb_layout = QVBoxLayout(kb_frame)
        kb_layout.setSpacing(4)

        # row index -> index of key that should expand to fill remaining space
        expand_key = {1: 13, 2: 13, 3: 11}  # Backspace, \, Enter

        row_widths = [
            {0: 40},           # Esc wider
            {13: 68},          # Backspace wider
            {0: 52, 13: 44},   # Tab, backslash
            {11: 68},          # Enter
            {},                # bottom letter row
        ]
        for ri, (keys, overrides) in enumerate(zip(self.KB_ROWS, row_widths)):
            rw = QWidget(); rl = QHBoxLayout(rw); rl.setSpacing(4); rl.setContentsMargins(0,0,0,0)
            for i, k in enumerate(keys):
                should_expand = (expand_key.get(ri) == i)
                rl.addWidget(self._key_btn(k, overrides.get(i, 34), expand=should_expand))
            if ri not in expand_key:
                rl.addStretch(1)
            kb_layout.addWidget(rw)

        # ── Space bar row with L/R modifiers ─────────────────────────
        space_row = QWidget()
        sr = QHBoxLayout(space_row); sr.setSpacing(4); sr.setContentsMargins(0,0,0,0)

        # Left side: LCtrl, LWin, LAlt
        for sym, label in [("<^","LCtrl"), ("<#","LWin"), ("<!","LAlt")]:
            sr.addWidget(self._mod_btn(sym, label, 80))

        sr.addWidget(self._key_btn("Space", 120))

        # Right side: RAlt, RWin, RCtrl
        for sym, label in [(">!","RAlt"), (">#","RWin"), (">^","RCtrl")]:
            sr.addWidget(self._mod_btn(sym, label, 80))

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
            if gi > 0:
                nav_v.addSpacing(12)
            for row in group:
                rw = QWidget(); rl = QHBoxLayout(rw); rl.setSpacing(4); rl.setContentsMargins(0,0,0,0)
                for k in row:
                    if k == "":
                        sp = QWidget(); sp.setFixedWidth(38); rl.addWidget(sp)
                    else:
                        nav_labels = {"PrintScreen":"PrtSc","ScrollLock":"ScrLk",
                                      "Up":"↑","Down":"↓","Left":"←","Right":"→"}
                        btn = self._key_btn(k, 38)
                        if k in nav_labels: btn.setText(nav_labels[k])
                        rl.addWidget(btn)
                nav_v.addWidget(rw)

        # ── Numpad cluster ────────────────────────────────────────────
        numpad_frame = QFrame()
        numpad_frame.setStyleSheet("background: #12122a; border-radius: 8px; padding: 4px;")
        numpad_frame.setMinimumWidth(180)
        num_v = QVBoxLayout(numpad_frame); num_v.setSpacing(4); num_v.setContentsMargins(4,4,4,4)
        lbl_np = QLabel("Numpad"); lbl_np.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_np.setStyleSheet("color:#505070; font-size:10px; margin-bottom:2px;")
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

        # ── Generic modifier strip (Ctrl / Alt / Shift / Win) ────────
        # Useful when user doesn't care about L/R
        gmod_frame = QFrame()
        gmod_frame.setStyleSheet("background: #12122a; border-radius: 8px; padding: 2px;")
        gmod_l = QHBoxLayout(gmod_frame); gmod_l.setSpacing(6)
        lbl = QLabel("Any side:"); lbl.setStyleSheet("color:#505070; font-size:11px;")
        gmod_l.addWidget(lbl)
        for sym, _, _, name in self.MOD_DEFS:
            gmod_l.addWidget(self._mod_btn(sym, name, 64))
        gmod_l.addStretch()
        layout.addWidget(gmod_frame)

        # ── OK / Cancel ───────────────────────────────────────────────
        btn_row = QHBoxLayout(); btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("QPushButton { background: #1e1e38; color: #a0a0b0; border: 1px solid #55556a; border-radius: 0px; padding: 8px 18px; } QPushButton:hover { background: #55556a; color: white; }")
        ok_btn = QPushButton("  ✓  Apply")
        ok_btn.setStyleSheet("QPushButton { background: #61dafb; color: #1a1a2e; border-radius: 0px; padding: 8px 24px; font-weight: bold; } QPushButton:hover { background: #4ac8e8; }")
        ok_btn.clicked.connect(self.accept); cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn); btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
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
        }
        pretty_type = title_map.get(shortcut_type, shortcut_type.capitalize())
        self.setWindowTitle(f"{'Edit' if shortcut_data else 'Add'} {pretty_type}")
        self.setModal(True)
        self.resize(500, 400)
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
            
            self.record_hotkey_btn = QPushButton("")
            self.record_hotkey_btn.setCheckable(True)
            self.record_hotkey_btn.setFixedSize(26,26)
            self.record_hotkey_btn.setStyleSheet("""
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
            
            self.record_hotkey_btn = QPushButton("")
            self.record_hotkey_btn.setCheckable(True)
            self.record_hotkey_btn.setFixedSize(26,26)
            self.record_hotkey_btn.setStyleSheet("""
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
            """)
            self.record_hotkey_btn.setToolTip("Open Shortcut Builder")
            self.record_hotkey_btn.clicked.connect(lambda checked: self.hotkey_edit.set_recording(checked))
            self.hotkey_edit.record_button = self.record_hotkey_btn
            
            hotkey_row.addWidget(self.hotkey_edit)
            hotkey_row.addWidget(self.record_hotkey_btn)
            form_layout.addLayout(hotkey_row)
            
            # Context fields — checkbox + input on same row
            def _ctx_row(toggle_attr, edit_attr, label, placeholder):
                row = QHBoxLayout()
                toggle = QCheckBox(label)
                toggle.setChecked(True)
                toggle.setFixedWidth(160)
                edit = QLineEdit()
                edit.setPlaceholderText(placeholder)
                toggle.toggled.connect(edit.setEnabled)
                setattr(self, toggle_attr, toggle)
                setattr(self, edit_attr, edit)
                row.addWidget(toggle)
                row.addWidget(edit)
                return row

            form_layout.addLayout(_ctx_row('window_title_toggle', 'window_title_edit', 'Window Title:', 'e.g., Gemini, Visual Studio Code'))
            form_layout.addLayout(_ctx_row('process_name_toggle', 'process_name_edit', 'Process Name:', 'e.g., WindowsTerminal.exe'))
            form_layout.addLayout(_ctx_row('window_class_toggle', 'window_class_edit', 'Window Class:', 'e.g., CabinetWClass'))
        elif self.shortcut_type == "exclude":
            form_layout.addWidget(QLabel("This rule blocks shortcuts when matched."))

            def _excl_row(toggle_attr, edit_attr, label, placeholder):
                row = QHBoxLayout()
                toggle = QCheckBox(label)
                toggle.setChecked(True)
                toggle.setFixedWidth(160)
                edit = QLineEdit()
                edit.setPlaceholderText(placeholder)
                toggle.toggled.connect(edit.setEnabled)
                setattr(self, toggle_attr, toggle)
                setattr(self, edit_attr, edit)
                row.addWidget(toggle)
                row.addWidget(edit)
                return row

            form_layout.addLayout(_excl_row('window_title_toggle', 'window_title_edit', 'Window Title:', 'e.g., Discord, Visual Studio Code'))
            form_layout.addLayout(_excl_row('process_name_toggle', 'process_name_edit', 'Process Name:', 'e.g., Discord.exe, Code.exe'))
            form_layout.addLayout(_excl_row('window_class_toggle', 'window_class_edit', 'Window Class:', 'e.g., Chrome_WidgetWin_1'))
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
        elif self.shortcut_type == "startup":
            form_layout.addWidget(QLabel("Context Mode:"))
            self.startup_context_mode = QComboBox()
            self.startup_context_mode.addItems(["No context (always run)", "Active in (only these windows)", "Inactive in (exclude these windows)"])
            form_layout.addWidget(self.startup_context_mode)

            def _startup_row(toggle_attr, edit_attr, label, placeholder):
                row = QHBoxLayout()
                toggle = QCheckBox(label)
                toggle.setChecked(True)
                toggle.setFixedWidth(160)
                edit = QLineEdit()
                edit.setPlaceholderText(placeholder)
                toggle.toggled.connect(edit.setEnabled)
                setattr(self, toggle_attr, toggle)
                setattr(self, edit_attr, edit)
                row.addWidget(toggle)
                row.addWidget(edit)
                return row

            form_layout.addLayout(_startup_row('window_title_toggle', 'startup_window_title', 'Window Title:', 'e.g., Notepad, Chrome'))
            form_layout.addLayout(_startup_row('process_name_toggle', 'startup_process_name', 'Process Name:', 'e.g., chrome.exe'))
            form_layout.addLayout(_startup_row('window_class_toggle', 'startup_window_class', 'Window Class:', 'e.g., CabinetWClass'))
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
        for shortcut in self.parent_window.script_shortcuts + self.parent_window.text_shortcuts + self.parent_window.startup_scripts + self.parent_window.context_shortcuts + self.parent_window.exclusion_rules:
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
            wt_on = self.shortcut_data.get("window_title_enabled", True)
            pn_on = self.shortcut_data.get("process_name_enabled", True)
            wc_on = self.shortcut_data.get("window_class_enabled", True)
            self.window_title_toggle.setChecked(wt_on); self.window_title_edit.setEnabled(wt_on)
            self.process_name_toggle.setChecked(pn_on); self.process_name_edit.setEnabled(pn_on)
            self.window_class_toggle.setChecked(wc_on); self.window_class_edit.setEnabled(wc_on)
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
            elif self.shortcut_type == "exclude":
                self.parent_window.exclusion_rules.append(shortcut_data)
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
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: {CP_DIM};
                border-left-style: solid;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-top: 5px solid {CP_CYAN};
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                margin-top: 2px;
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
        self.parent_window.apply_global_font()
        self.parent_window.save_shortcuts_json()
        QMessageBox.information(self, "Success", f"Settings updated and applied!")


class AHKShortcutEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_shortcuts = []
        self.text_shortcuts = []
        self.file_shortcuts = []
        self.startup_scripts = []
        self.context_shortcuts = []
        self.exclusion_rules = []
        self.app_font_family = "Consolas" # Default per theme guide
        self.app_font_size = 10
        self.category_colors = {
            "System": "#FF6B6B", "Navigation": "#4ECDC4", "Text": "#45B7D1",
            "Media": "#96CEB4", "AutoHotkey": "#FFEAA7", "General": "#DDA0DD",
            "Imported": "#FFA07A", "Tools": "#98D8C8", "Window": "#F7DC6F", "File": "#BB8FCE"
        }
        # Section expanded/collapsed states
        self.section_states = {
            "script": True,
            "context": True,
            "exclude": True,
            "startup": True,
            "text": True,
            "file": True
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

            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
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

            /* Specialized ComboBox dropdown styling */
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: {CP_DIM};
                border-left-style: solid;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-top: 5px solid {CP_CYAN};
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                margin-top: 2px;
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
        self.add_menu.addAction("Text Shortcut", lambda: self.open_add_dialog("text"))
        self.add_menu.addAction("File Shortcut", lambda: self.open_add_dialog("file"))
        self.add_menu.addAction("Context Shortcut", lambda: self.open_add_dialog("context"))
        self.add_menu.addAction("Exclusion Rule", lambda: self.open_add_dialog("exclude"))
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
            QCheckBox::indicator { width: 0px; height: 0px; }
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

            self.update_display()

        elif scheme == "toggle":
            shortcut_type = host
            try:
                index = int(path)
            except ValueError:
                return

            if shortcut_type == "script" and index < len(self.script_shortcuts):
                self.script_shortcuts[index]["enabled"] = not self.script_shortcuts[index].get("enabled", True)
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
                    self.text_shortcuts = data.get("text_shortcuts", [])
                    self.file_shortcuts = data.get("file_shortcuts", [])
                    self.startup_scripts = data.get("startup_scripts", [])
                    self.context_shortcuts = data.get("context_shortcuts", [])
                    self.exclusion_rules = data.get("exclusion_rules", data.get("excluded_contexts", []))
                    self.app_font_family = data.get("app_font_family", "Consolas")
                    self.app_font_size = data.get("app_font_size", 10)
                    
                    # Fix-up: Move file shortcuts that were accidentally saved in text_shortcuts
                    to_move = [s for s in self.text_shortcuts if "file_path" in s]
                    for s in to_move:
                        self.text_shortcuts.remove(s)
                        self.file_shortcuts.append(s)
                    
                    # Fix-up: Move exclusion rules and context shortcuts that were accidentally saved in text_shortcuts
                    to_move_exclude = [s for s in self.text_shortcuts if ("window_title" in s or "process_name" in s or "window_class" in s) and "hotkey" not in s]
                    for s in to_move_exclude:
                        self.text_shortcuts.remove(s)
                        self.exclusion_rules.append(s)
                        
                    to_move_context = [s for s in self.text_shortcuts if ("window_title" in s or "process_name" in s or "window_class" in s) and "hotkey" in s]
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
                "text_shortcuts": self.text_shortcuts,
                "file_shortcuts": self.file_shortcuts,
                "startup_scripts": self.startup_scripts,
                "context_shortcuts": self.context_shortcuts,
                "exclusion_rules": self.exclusion_rules,
                "app_font_family": self.app_font_family,
                "app_font_size": self.app_font_size
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
        
        html = self.generate_html(filtered_script, filtered_text, filtered_file, filtered_context, filtered_exclusions, filtered_startup, group_by_category)
        
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

    def generate_html(self, script_shortcuts, text_shortcuts, file_shortcuts, context_shortcuts, exclusion_rules, startup_scripts, group_by_category):
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

        html += f"""
                </div>
                <div class="column">
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
        elif self.selected_type == "exclude":
            self.exclusion_rules.append(duplicated)
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
            elif self.selected_type == "context":
                self.context_shortcuts.remove(self.selected_shortcut)
            elif self.selected_type == "exclude":
                self.exclusion_rules.remove(self.selected_shortcut)
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
                output_lines.append("    return false")
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
            if enabled_startup:
                output_lines.append(";! === BACKGROUND / STARTUP SCRIPTS ===")
                for shortcut in enabled_startup:
                    output_lines.append(f";! {shortcut.get('name', 'Unnamed')}")
                    if shortcut.get('description'):
                        output_lines.append(f";! {shortcut.get('description')}")

                    action = shortcut.get('action', '')
                    action = action.replace(',,,', ',,')

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

                    output_lines.append(action)

                    if has_context:
                        output_lines.append("#HotIf")
                    output_lines.append("")

            append_exclusion_checker()

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

                    if '\n' in action:
                        output_lines.append(f"{hotkey}:: {{")
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
                        output_lines.append(f"{hotkey}::{action}")

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
                    # Context is active if at least one field is enabled and non-empty
                    has_context_fields = any([
                        shortcut.get('window_title_enabled', True) and shortcut.get('window_title', ''),
                        shortcut.get('process_name_enabled', True) and shortcut.get('process_name', ''),
                        shortcut.get('window_class_enabled', True) and shortcut.get('window_class', ''),
                    ])
                    if has_context_fields:
                        append_context_checker(shortcut, func_name)

                    # Add #HotIf directive
                    hotkey = shortcut.get('hotkey', '')
                    if has_context_fields:
                        if needs_exclusion_guard(hotkey):
                            output_lines.append(f"#HotIf {func_name}() && !IsShortcutExcluded()")
                        else:
                            output_lines.append(f"#HotIf {func_name}()")
                    elif needs_exclusion_guard(hotkey):
                        output_lines.append(f"#HotIf !IsShortcutExcluded()")
                    hotif_opened = has_context_fields or needs_exclusion_guard(hotkey)
                    output_lines.append("")
                    
                    action = shortcut.get('action', '')
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
