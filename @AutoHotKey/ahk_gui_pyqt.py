import sys
import json
import os
import re
import copy
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLineEdit, QCheckBox, QDialog,
    QDialogButtonBox, QLabel, QTextEdit, QComboBox, QMessageBox,
    QSplitter, QTextBrowser, QMenu, QSizePolicy, QScrollArea,
    QFontComboBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings, QUrl, QTimer
from PyQt6.QtGui import (
    QFont, QTextCursor, QTextDocument, QFontDatabase,
    QFontMetrics, QTextCharFormat, QColor, QPalette, QBrush
)

# ─────────────────────────────── paths ───────────────────────────────
SCRIPT_DIR          = os.path.dirname(os.path.abspath(__file__))
AHK_SCRIPT_PATH     = os.path.join(SCRIPT_DIR, "ahk_v2.ahk")
SHORTCUTS_JSON_PATH = os.path.join(SCRIPT_DIR, "ahk_shortcuts.json")

# ══════════════════════════════════════════════════════════════════════
#  THEME  – terminal-noir / cyberpunk
# ══════════════════════════════════════════════════════════════════════
THEME = dict(
    # backgrounds
    bg_deep    = "#0d0d0f",
    bg_base    = "#111114",
    bg_panel   = "#16161a",
    bg_card    = "#1c1c21",
    bg_hover   = "#222228",
    bg_input   = "#1a1a1f",
    bg_sel     = "#0e2233",

    # borders
    border     = "#2a2a32",
    border_hi  = "#00e5ff",

    # accents
    cyan       = "#00e5ff",
    green      = "#00ff9d",
    amber      = "#ffb800",
    red        = "#ff3c5a",
    purple     = "#b06cff",
    muted      = "#4a4a58",

    # text
    txt_hi     = "#f0f0f8",
    txt_mid    = "#9090a8",
    txt_dim    = "#545468",

    # fonts
    font_ui    = "JetBrains Mono",
    font_size  = 13,
)

def _t(key):
    return THEME[key]

# ──────────────────────────────────────────────────────────────────────
#  Global stylesheet
# ──────────────────────────────────────────────────────────────────────
GLOBAL_QSS = f"""
/* ── base ── */
QMainWindow, QDialog, QWidget {{
    background-color: {_t('bg_base')};
    color: {_t('txt_hi')};
    font-family: '{_t('font_ui')}', 'Consolas', monospace;
    font-size: {_t('font_size')}px;
}}
QLabel {{
    color: {_t('txt_mid')};
    background: transparent;
}}

/* ── inputs ── */
QLineEdit, QTextEdit, QComboBox {{
    background-color: {_t('bg_input')};
    border: 1px solid {_t('border')};
    border-radius: 4px;
    padding: 5px 10px;
    color: {_t('txt_hi')};
    selection-background-color: {_t('bg_sel')};
    selection-color: {_t('cyan')};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border-color: {_t('cyan')};
    background-color: {_t('bg_hover')};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 6px;
}}
QComboBox QAbstractItemView {{
    background: {_t('bg_card')};
    border: 1px solid {_t('border_hi')};
    color: {_t('txt_hi')};
    selection-background-color: {_t('bg_sel')};
}}

/* ── buttons ── */
QPushButton {{
    background-color: {_t('bg_card')};
    color: {_t('txt_hi')};
    border: 1px solid {_t('border')};
    border-radius: 4px;
    padding: 5px 14px;
    min-height: 28px;
}}
QPushButton:hover {{
    background-color: {_t('bg_hover')};
    border-color: {_t('cyan')};
    color: {_t('cyan')};
}}
QPushButton:pressed {{
    background-color: {_t('bg_sel')};
}}
QPushButton:checked {{
    background-color: {_t('bg_sel')};
    border-color: {_t('cyan')};
    color: {_t('cyan')};
}}
QPushButton:disabled {{
    color: {_t('muted')};
    border-color: {_t('border')};
}}

/* ── checkboxes ── */
QCheckBox {{
    color: {_t('txt_mid')};
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {_t('border')};
    border-radius: 3px;
    background: {_t('bg_input')};
}}
QCheckBox::indicator:checked {{
    background: {_t('cyan')};
    border-color: {_t('cyan')};
}}

/* ── scrollbars ── */
QScrollBar:vertical {{
    background: {_t('bg_deep')};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {_t('muted')};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {_t('cyan')};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{
    background: {_t('bg_deep')};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {_t('muted')};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{ background: {_t('cyan')}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; }}

/* ── menus ── */
QMenu {{
    background: {_t('bg_card')};
    border: 1px solid {_t('border_hi')};
    border-radius: 4px;
    padding: 4px 0;
    color: {_t('txt_hi')};
}}
QMenu::item {{ padding: 6px 20px; }}
QMenu::item:selected {{
    background: {_t('bg_hover')};
    color: {_t('cyan')};
}}
QMenu::separator {{
    height: 1px;
    background: {_t('border')};
    margin: 4px 0;
}}

/* ── splitter ── */
QSplitter::handle {{
    background: {_t('border')};
}}
QSplitter::handle:hover {{
    background: {_t('cyan')};
}}

/* ── dialog button box ── */
QDialogButtonBox QPushButton {{
    min-width: 80px;
}}

/* ── text browser ── */
QTextBrowser {{
    background: {_t('bg_base')};
    border: none;
    color: {_t('txt_hi')};
}}
"""


# ══════════════════════════════════════════════════════════════════════
#  ShortcutBuilderPopup
# ══════════════════════════════════════════════════════════════════════
class ShortcutBuilderPopup(QDialog):
    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.setWindowTitle("Shortcut Builder")
        self.setModal(True)
        self.setFixedWidth(440)
        self.result_hotkey = initial_value
        self.mods = {"^": False, "!": False, "+": False, "#": False}
        self.main_key = ""
        self._parse_initial(initial_value)
        self._setup_ui()

    def _parse_initial(self, value):
        if not value:
            return
        for mod in self.mods:
            if mod in value:
                self.mods[mod] = True
                value = value.replace(mod, "")
        self.main_key = value

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── preview badge ──
        self.preview = QLabel(self._fmt_preview())
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet(f"""
            QLabel {{
                font-size: 26px;
                font-weight: bold;
                color: {_t('cyan')};
                background: {_t('bg_deep')};
                border: 1px solid {_t('cyan')};
                border-radius: 6px;
                padding: 12px 16px;
                letter-spacing: 2px;
            }}
        """)
        layout.addWidget(self.preview)

        # ── modifier row ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background:{_t('border')}; max-height:1px;")
        layout.addWidget(sep)

        mod_lbl = QLabel("MODIFIERS")
        mod_lbl.setStyleSheet(f"color:{_t('muted')}; font-size:10px; letter-spacing:2px;")
        layout.addWidget(mod_lbl)

        mod_row = QHBoxLayout()
        mod_row.setSpacing(8)
        self.mod_btns = {}
        for sym, name in [("^", "CTRL"), ("!", "ALT"), ("+", "SHIFT"), ("#", "WIN")]:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setChecked(self.mods[sym])
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    padding: 8px 0;
                    border-radius: 4px;
                    background: {_t('bg_input')};
                    border: 1px solid {_t('border')};
                    color: {_t('txt_mid')};
                }}
                QPushButton:checked {{
                    background: {_t('bg_sel')};
                    border-color: {_t('cyan')};
                    color: {_t('cyan')};
                }}
                QPushButton:hover {{
                    border-color: {_t('cyan')};
                    color: {_t('cyan')};
                }}
            """)
            btn.toggled.connect(lambda chk, s=sym: self._update_mod(s, chk))
            mod_row.addWidget(btn)
            self.mod_btns[sym] = btn
        layout.addLayout(mod_row)

        # ── key selector ──
        key_lbl = QLabel("MAIN KEY")
        key_lbl.setStyleSheet(f"color:{_t('muted')}; font-size:10px; letter-spacing:2px;")
        layout.addWidget(key_lbl)

        self.key_search = QLineEdit()
        self.key_search.setPlaceholderText("Type to filter keys…")
        self.key_search.textChanged.connect(self._filter_keys)
        layout.addWidget(self.key_search)

        self.key_combo = QComboBox()
        self.key_combo.setEditable(True)
        self._all_keys = [
            "a","b","c","d","e","f","g","h","i","j","k","l","m",
            "n","o","p","q","r","s","t","u","v","w","x","y","z",
            "0","1","2","3","4","5","6","7","8","9",
            "F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12",
            "Space","Enter","Tab","Esc","Backspace","Delete","Insert",
            "Home","End","PgUp","PgDn","Up","Down","Left","Right",
            "LButton","RButton","MButton","WheelUp","WheelDown",
            "[","]",";","'",",",".","/","\\","-","=","`"
        ]
        self.key_combo.addItems(self._all_keys)
        if self.main_key:
            self.key_combo.setCurrentText(self.main_key)
        self.key_combo.currentTextChanged.connect(self._update_key)
        layout.addWidget(self.key_combo)

        # ── quick keys ──
        quick_lbl = QLabel("QUICK KEYS")
        quick_lbl.setStyleSheet(f"color:{_t('muted')}; font-size:10px; letter-spacing:2px;")
        layout.addWidget(quick_lbl)

        quick_row = QHBoxLayout()
        quick_row.setSpacing(6)
        for k in ["Space", "Enter", "Tab", "Esc", "Up", "Down"]:
            btn = QPushButton(k)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 11px;
                    padding: 5px 8px;
                    background: {_t('bg_card')};
                    border: 1px solid {_t('border')};
                    border-radius: 3px;
                    color: {_t('amber')};
                }}
                QPushButton:hover {{
                    border-color: {_t('amber')};
                    background: {_t('bg_hover')};
                }}
            """)
            btn.clicked.connect(lambda _, v=k: self.key_combo.setCurrentText(v))
            quick_row.addWidget(btn)
        layout.addLayout(quick_row)

        # ── buttons ──
        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

    # ── helpers ──
    def _update_mod(self, sym, state):
        self.mods[sym] = state
        self.preview.setText(self._fmt_preview())

    def _update_key(self, key):
        self.main_key = key
        self.preview.setText(self._fmt_preview())

    def _fmt_preview(self):
        parts = []
        if self.mods["^"]: parts.append("Ctrl")
        if self.mods["!"]: parts.append("Alt")
        if self.mods["+"]: parts.append("Shift")
        if self.mods["#"]: parts.append("Win")
        parts.append(self.main_key if self.main_key else "?")
        return " + ".join(parts)

    def get_final_ahk(self):
        res = ""
        for s in ["^", "!", "+", "#"]:
            if self.mods[s]:
                res += s
        return res + self.main_key

    def _filter_keys(self, text):
        text = text.lower().strip()
        if not text:
            return
        matches = [k for k in self._all_keys if text in k.lower()]
        if matches:
            best = next((k for k in matches if k.lower().startswith(text)), matches[0])
            self.key_combo.setCurrentText(best)


# ══════════════════════════════════════════════════════════════════════
#  HotkeyLineEdit
# ══════════════════════════════════════════════════════════════════════
class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.record_button = None

    def set_recording(self, state):
        if not state:
            return
        dlg = ShortcutBuilderPopup(self, self.text())
        if dlg.exec():
            self.setText(dlg.get_final_ahk())
        if self.record_button:
            self.record_button.setChecked(False)


# ══════════════════════════════════════════════════════════════════════
#  AddEditShortcutDialog
# ══════════════════════════════════════════════════════════════════════
class AddEditShortcutDialog(QDialog):
    def __init__(self, parent, shortcut_type, shortcut_data=None):
        super().__init__(parent)
        self.pw           = parent
        self.shortcut_type = shortcut_type
        self.shortcut_data = shortcut_data
        verb = "Edit" if shortcut_data else "Add"
        self.setWindowTitle(f"{verb} {shortcut_type.capitalize()} Shortcut")
        self.setModal(True)
        self.resize(820, 560)
        self._build_ui()
        if shortcut_data:
            self._populate()

    # ── ui ──
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # header bar
        hdr = QWidget()
        hdr.setFixedHeight(46)
        hdr.setStyleSheet(f"background:{_t('bg_deep')}; border-bottom:1px solid {_t('border')};")
        hdr_l = QHBoxLayout(hdr)
        hdr_l.setContentsMargins(16, 0, 16, 0)
        t_lbl = QLabel(self.windowTitle().upper())
        t_lbl.setStyleSheet(f"color:{_t('cyan')}; font-weight:bold; letter-spacing:2px; font-size:12px;")
        hdr_l.addWidget(t_lbl)
        hdr_l.addStretch()
        root.addWidget(hdr)

        # body
        body = QWidget()
        body.setStyleSheet(f"background:{_t('bg_panel')};")
        body_l = QHBoxLayout(body)
        body_l.setContentsMargins(16, 16, 16, 16)
        body_l.setSpacing(16)

        # left form
        form_w = QWidget()
        form_w.setMinimumWidth(280)
        form_l = QVBoxLayout(form_w)
        form_l.setSpacing(10)
        form_l.setContentsMargins(0, 0, 0, 0)

        def field_lbl(text):
            l = QLabel(text)
            l.setStyleSheet(f"color:{_t('muted')}; font-size:10px; letter-spacing:1px; margin-bottom:2px;")
            return l

        form_l.addWidget(field_lbl("NAME"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Open Terminal")
        form_l.addWidget(self.name_edit)

        form_l.addWidget(field_lbl("CATEGORY"))
        self.cat_combo = QComboBox()
        self.cat_combo.setEditable(True)
        self.cat_combo.addItems(self._get_categories())
        self.cat_combo.setCurrentText("General")
        form_l.addWidget(self.cat_combo)

        form_l.addWidget(field_lbl("DESCRIPTION"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Brief description")
        form_l.addWidget(self.desc_edit)

        self.enabled_cb = QCheckBox("Enabled")
        self.enabled_cb.setChecked(True)
        self.enabled_cb.setStyleSheet(f"color:{_t('green')}; font-size:12px; margin-top:4px;")
        form_l.addWidget(self.enabled_cb)

        # ── type-specific left fields ──
        st = self.shortcut_type
        if st in ("script", "context"):
            form_l.addWidget(field_lbl("HOTKEY"))
            hk_row = QHBoxLayout()
            hk_row.setSpacing(6)
            self.hotkey_edit = HotkeyLineEdit()
            self.hotkey_edit.setPlaceholderText("e.g., ^!n, !Space")
            self.rec_btn = self._make_rec_btn()
            self.rec_btn.clicked.connect(lambda chk: self.hotkey_edit.set_recording(chk))
            self.hotkey_edit.record_button = self.rec_btn
            hk_row.addWidget(self.hotkey_edit)
            hk_row.addWidget(self.rec_btn)
            form_l.addLayout(hk_row)

        if st == "context":
            for lbl_txt, attr, ph in [
                ("WINDOW TITLE (contains)", "wt_edit", "e.g., Gemini, Visual Studio Code"),
                ("PROCESS NAME (optional)", "pn_edit", "e.g., Code.exe"),
                ("WINDOW CLASS (optional)", "wc_edit", "e.g., CabinetWClass"),
            ]:
                form_l.addWidget(field_lbl(lbl_txt))
                w = QLineEdit(); w.setPlaceholderText(ph)
                setattr(self, attr, w)
                form_l.addWidget(w)

        if st == "text":
            form_l.addWidget(field_lbl("TRIGGER (without ::)"))
            self.trigger_edit = QLineEdit()
            self.trigger_edit.setPlaceholderText("e.g., ;v1, ;run")
            form_l.addWidget(self.trigger_edit)

        form_l.addStretch()
        body_l.addWidget(form_w)

        # ── divider ──
        div = QFrame()
        div.setFrameShape(QFrame.Shape.VLine)
        div.setStyleSheet(f"background:{_t('border')}; max-width:1px;")
        body_l.addWidget(div)

        # ── right: code / text editor ──
        code_w = QWidget()
        code_l = QVBoxLayout(code_w)
        code_l.setSpacing(8)
        code_l.setContentsMargins(0, 0, 0, 0)

        code_hdr = QHBoxLayout()
        code_title = field_lbl("ACTION CODE" if st != "text" else "REPLACEMENT TEXT")
        code_hdr.addWidget(code_title)
        code_hdr.addStretch()

        if st in ("script", "startup", "context"):
            ref_btn = QPushButton("📖 Reference")
            ref_btn.setStyleSheet(f"""
                QPushButton {{
                    background:{_t('bg_card')};
                    border:1px solid {_t('purple')};
                    color:{_t('purple')};
                    font-size:11px;
                    padding:3px 10px;
                    border-radius:3px;
                }}
                QPushButton:hover {{
                    background:{_t('bg_hover')};
                    color:{_t('txt_hi')};
                    border-color:{_t('txt_hi')};
                }}
            """)
            ref_btn.clicked.connect(self._show_reference)
            code_hdr.addWidget(ref_btn)

        code_l.addLayout(code_hdr)

        if st in ("script", "startup", "context"):
            self.action_edit = QTextEdit()
            self.action_edit.setStyleSheet(f"""
                QTextEdit {{
                    background:{_t('bg_deep')};
                    border:1px solid {_t('border')};
                    border-radius:4px;
                    color:{_t('green')};
                    font-family:'{_t('font_ui')}','Consolas',monospace;
                    font-size:13px;
                    padding:8px;
                }}
                QTextEdit:focus {{ border-color:{_t('cyan')}; }}
            """)
            self.action_edit.setPlaceholderText(
                "Run(\"notepad.exe\")\nSend(\"^c\")\nSendText(\"hello world\")"
            )
            code_l.addWidget(self.action_edit)
        else:
            self.replacement_edit = QTextEdit()
            self.replacement_edit.setStyleSheet(f"""
                QTextEdit {{
                    background:{_t('bg_deep')};
                    border:1px solid {_t('border')};
                    border-radius:4px;
                    color:{_t('amber')};
                    font-family:'{_t('font_ui')}','Consolas',monospace;
                    font-size:13px;
                    padding:8px;
                }}
                QTextEdit:focus {{ border-color:{_t('cyan')}; }}
            """)
            code_l.addWidget(self.replacement_edit)

        body_l.addWidget(code_w, stretch=1)
        root.addWidget(body, stretch=1)

        # ── footer / button bar ──
        footer = QWidget()
        footer.setFixedHeight(54)
        footer.setStyleSheet(f"background:{_t('bg_deep')}; border-top:1px solid {_t('border')};")
        foot_l = QHBoxLayout(footer)
        foot_l.setContentsMargins(16, 0, 16, 0)
        foot_l.addStretch()

        cancel_btn = QPushButton("Cancel")
        ok_btn     = QPushButton("Save")
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background:{_t('cyan')};
                color:{_t('bg_deep')};
                font-weight:bold;
                border:none;
                padding:6px 22px;
                border-radius:4px;
            }}
            QPushButton:hover {{
                background:{_t('green')};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        ok_btn.clicked.connect(self._accept)
        foot_l.addWidget(cancel_btn)
        foot_l.addWidget(ok_btn)
        root.addWidget(footer)

    # ── helpers ──
    def _make_rec_btn(self):
        btn = QPushButton("⌨")
        btn.setCheckable(True)
        btn.setFixedWidth(34)
        btn.setToolTip("Open Shortcut Builder")
        btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                background:{_t('bg_input')};
                border:1px solid {_t('border')};
                border-radius:4px;
                color:{_t('txt_mid')};
            }}
            QPushButton:checked {{
                background:{_t('bg_sel')};
                border-color:{_t('cyan')};
                color:{_t('cyan')};
            }}
            QPushButton:hover {{
                border-color:{_t('cyan')};
            }}
        """)
        return btn

    def _get_categories(self):
        cats = set()
        for s in (self.pw.script_shortcuts + self.pw.text_shortcuts +
                  self.pw.startup_scripts + self.pw.context_shortcuts):
            c = s.get("category", "").strip()
            if c:
                cats.add(c)
        base = ["System","Navigation","Text","Media","AutoHotkey","General"]
        result = [c for c in base if c in cats]
        result += sorted(cats - set(base))
        for c in base:
            if c not in result:
                result.append(c)
        return list(dict.fromkeys(result))

    def _populate(self):
        d = self.shortcut_data
        self.name_edit.setText(d.get("name", ""))
        self.cat_combo.setCurrentText(d.get("category", ""))
        self.desc_edit.setText(d.get("description", ""))
        self.enabled_cb.setChecked(d.get("enabled", True))
        st = self.shortcut_type
        if st in ("script", "context"):
            self.hotkey_edit.setText(d.get("hotkey", ""))
        if st == "context":
            self.wt_edit.setText(d.get("window_title", ""))
            self.pn_edit.setText(d.get("process_name", ""))
            self.wc_edit.setText(d.get("window_class", ""))
        if st in ("script", "startup", "context"):
            self.action_edit.setPlainText(d.get("action", ""))
        if st == "text":
            self.trigger_edit.setText(d.get("trigger", ""))
            self.replacement_edit.setPlainText(d.get("replacement", ""))

    def _show_reference(self):
        """Show README.md in a styled reference dialog."""
        dlg = QDialog(self)
        dlg.setWindowTitle("AutoHotkey Reference")
        dlg.resize(1100, 800)
        dlg_l = QVBoxLayout(dlg)
        dlg_l.setContentsMargins(0, 0, 0, 0)
        dlg_l.setSpacing(0)

        # search bar
        search_bar = QWidget()
        search_bar.setFixedHeight(46)
        search_bar.setStyleSheet(f"background:{_t('bg_deep')}; border-bottom:1px solid {_t('border')};")
        sb_l = QHBoxLayout(search_bar)
        sb_l.setContentsMargins(12, 0, 12, 0)
        sb_l.setSpacing(8)
        search_lbl = QLabel("SEARCH")
        search_lbl.setStyleSheet(f"color:{_t('muted')}; font-size:10px; letter-spacing:2px;")
        sb_l.addWidget(search_lbl)
        search_input = QLineEdit()
        search_input.setPlaceholderText("Find in documentation…")
        sb_l.addWidget(search_input)
        next_btn = QPushButton("Next ↓")
        next_btn.setFixedWidth(80)
        sb_l.addWidget(next_btn)
        close_top = QPushButton("✕")
        close_top.setFixedWidth(34)
        close_top.clicked.connect(dlg.close)
        close_top.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:none;
                color:{_t('txt_mid')}; font-size:16px;
            }}
            QPushButton:hover {{ color:{_t('red')}; }}
        """)
        sb_l.addWidget(close_top)
        dlg_l.addWidget(search_bar)

        # content area: toc + browser
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # toc
        toc_scroll = QScrollArea()
        toc_scroll.setWidgetResizable(True)
        toc_scroll.setStyleSheet(f"background:{_t('bg_deep')}; border:none;")
        toc_widget = QWidget()
        toc_widget.setStyleSheet(f"background:{_t('bg_deep')};")
        toc_vl = QVBoxLayout(toc_widget)
        toc_vl.setContentsMargins(8, 12, 8, 12)
        toc_vl.setSpacing(1)
        toc_vl.setAlignment(Qt.AlignmentFlag.AlignTop)
        toc_lbl = QLabel("CONTENTS")
        toc_lbl.setStyleSheet(f"color:{_t('cyan')}; font-size:10px; letter-spacing:2px; margin-bottom:6px;")
        toc_vl.addWidget(toc_lbl)
        toc_scroll.setWidget(toc_widget)

        # browser
        browser = QTextBrowser()
        browser.setOpenLinks(False)
        browser.setStyleSheet(f"""
            QTextBrowser {{
                background:{_t('bg_panel')};
                color:{_t('txt_hi')};
                border:none;
                padding:20px;
                font-family:'{_t('font_ui')}','Consolas',monospace;
                font-size:13px;
                line-height:1.5;
            }}
        """)

        ref_file = os.path.join(SCRIPT_DIR, "README.md")
        toc_entries = []
        if os.path.exists(ref_file):
            try:
                with open(ref_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                clean = re.sub(r'<a name="[^"]+">\s*</a>\n?', '', content, flags=re.IGNORECASE)
                clean = re.sub(r'## Table of Contents.*?\n---', '', clean, flags=re.DOTALL)
                browser.setMarkdown(clean)
                in_code = False
                for line in content.splitlines():
                    if line.startswith("```"):
                        in_code = not in_code; continue
                    if in_code or line.strip().startswith("<"): continue
                    m = re.match(r'^(#{1,3})\s+(.*)', line)
                    if m and 'table of contents' not in m.group(2).lower():
                        toc_entries.append((len(m.group(1)), m.group(2).strip()))
            except Exception as e:
                browser.setPlainText(f"Error loading README.md: {e}")
        else:
            browser.setPlainText("README.md not found.")

        def make_jump(txt):
            def jump():
                c = browser.textCursor()
                c.movePosition(QTextCursor.MoveOperation.Start)
                browser.setTextCursor(c)
                browser.find(txt)
                browser.ensureCursorVisible()
            return jump

        for lvl, title in toc_entries:
            indent = "  " * (lvl - 1)
            btn = QPushButton(indent + title)
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            c = _t('cyan') if lvl == 1 else _t('txt_mid')
            fw = 'bold' if lvl == 1 else 'normal'
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align:left;
                    color:{c}; font-weight:{fw};
                    font-size:12px;
                    padding:3px 6px;
                    border:none;
                    background:transparent;
                    border-radius:3px;
                }}
                QPushButton:hover {{
                    color:{_t('txt_hi')};
                    background:{_t('bg_hover')};
                }}
            """)
            btn.clicked.connect(make_jump(title))
            toc_vl.addWidget(btn)

        toc_scroll.setMinimumWidth(200)
        toc_scroll.setMaximumWidth(300)
        splitter.addWidget(toc_scroll)
        splitter.addWidget(browser)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        dlg_l.addWidget(splitter, stretch=1)

        # search wiring
        def do_search():
            txt = search_input.text()
            if not txt: return
            found = browser.find(txt)
            if not found:
                c = browser.textCursor()
                c.movePosition(QTextCursor.MoveOperation.Start)
                browser.setTextCursor(c)
                browser.find(txt)
            browser.ensureCursorVisible()

        search_input.returnPressed.connect(do_search)
        next_btn.clicked.connect(do_search)
        dlg.exec()

    def _accept(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Required", "Name cannot be empty.")
            return
        cat  = self.cat_combo.currentText().strip() or "General"
        desc = self.desc_edit.text().strip()
        ena  = self.enabled_cb.isChecked()
        st   = self.shortcut_type

        if st == "script":
            hk  = self.hotkey_edit.text().strip()
            act = self.action_edit.toPlainText().strip()
            if not hk or not act:
                QMessageBox.warning(self, "Required", "Hotkey and action are required.")
                return
            new = {"name":name,"category":cat,"description":desc,"hotkey":hk,"action":act,"enabled":ena}

        elif st == "context":
            hk  = self.hotkey_edit.text().strip()
            act = self.action_edit.toPlainText().strip()
            wt  = self.wt_edit.text().strip()
            pn  = self.pn_edit.text().strip()
            wc  = self.wc_edit.text().strip()
            if not hk or not act:
                QMessageBox.warning(self, "Required", "Hotkey and action are required.")
                return
            if not wt and not pn and not wc:
                QMessageBox.warning(self, "Required", "At least one context field is required.")
                return
            new = {"name":name,"category":cat,"description":desc,
                   "hotkey":hk,"window_title":wt,"process_name":pn,
                   "window_class":wc,"action":act,"enabled":ena}

        elif st == "startup":
            act = self.action_edit.toPlainText().strip()
            if not act:
                QMessageBox.warning(self, "Required", "Action code is required.")
                return
            new = {"name":name,"category":cat,"description":desc,"action":act,"enabled":ena}

        else:  # text
            trig = self.trigger_edit.text().strip()
            repl = self.replacement_edit.toPlainText().strip()
            if not trig or not repl:
                QMessageBox.warning(self, "Required", "Trigger and replacement are required.")
                return
            new = {"name":name,"category":cat,"description":desc,
                   "trigger":trig,"replacement":repl,"enabled":ena}

        if self.shortcut_data:
            self.shortcut_data.update(new)
        else:
            lists = {
                "script":  self.pw.script_shortcuts,
                "context": self.pw.context_shortcuts,
                "startup": self.pw.startup_scripts,
                "text":    self.pw.text_shortcuts,
            }
            lists[st].append(new)

        self.pw.save_shortcuts_json()
        self.pw.update_display()
        self.accept()


# ══════════════════════════════════════════════════════════════════════
#  CategoryColorDialog
# ══════════════════════════════════════════════════════════════════════
class CategoryColorDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.pw = parent
        self.setWindowTitle("Category Colors")
        self.setModal(True)
        self.resize(420, 520)
        self._build_ui()

    def _build_ui(self):
        l = QVBoxLayout(self)
        l.setSpacing(12)
        lbl = QLabel("CATEGORY COLORS")
        lbl.setStyleSheet(f"color:{_t('cyan')}; font-size:11px; letter-spacing:2px; font-weight:bold;")
        l.addWidget(lbl)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_l = QVBoxLayout(inner)
        inner_l.setSpacing(8)

        all_cats = set(self.pw.category_colors.keys())
        for s in (self.pw.script_shortcuts + self.pw.text_shortcuts + self.pw.context_shortcuts):
            c = s.get("category", "General")
            if c: all_cats.add(c)

        self.color_edits = {}
        for cat in sorted(all_cats):
            row = QHBoxLayout()
            lbl2 = QLabel(f"▸  {cat}")
            lbl2.setStyleSheet(f"color:{_t('txt_hi')}; min-width:140px;")
            row.addWidget(lbl2)
            ce = QLineEdit(self.pw.get_category_color(cat))
            ce.setPlaceholderText("#RRGGBB")
            ce.setMaximumWidth(110)
            row.addWidget(ce)
            swatch = QLabel("  ")
            swatch.setFixedSize(24, 24)
            swatch.setStyleSheet(f"background:{self.pw.get_category_color(cat)}; border-radius:3px;")
            row.addWidget(swatch)
            row.addStretch()
            inner_l.addLayout(row)
            self.color_edits[cat] = (ce, swatch)

        scroll.setWidget(inner)
        l.addWidget(scroll, stretch=1)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(f"background:{_t('cyan')}; color:{_t('bg_deep')}; font-weight:bold; border:none;")
        save_btn.clicked.connect(self._save)
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.clicked.connect(self._reset)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        for b in [save_btn, reset_btn, close_btn]:
            btn_row.addWidget(b)
        l.addLayout(btn_row)

    def _save(self):
        for cat, (ce, swatch) in self.color_edits.items():
            c = ce.text().strip()
            if c:
                self.pw.category_colors[cat] = c
                swatch.setStyleSheet(f"background:{c}; border-radius:3px;")
        self.pw.update_display()
        QMessageBox.information(self, "Saved", "Category colors updated.")

    def _reset(self):
        defaults = {
            "System": "#ff4f6d", "Navigation": "#00e5ff", "Text": "#45b7d1",
            "Media": "#00ff9d", "AutoHotkey": "#ffb800", "General": "#b06cff",
            "Imported": "#ff7f50", "Tools": "#98d8c8", "Window": "#f7dc6f", "File": "#bb8fce"
        }
        self.pw.category_colors.update(defaults)
        self.close()
        CategoryColorDialog(self.pw).exec()


# ══════════════════════════════════════════════════════════════════════
#  SettingsDialog
# ══════════════════════════════════════════════════════════════════════
class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.pw = parent
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(380, 160)
        l = QVBoxLayout(self)
        l.setSpacing(14)

        lbl = QLabel("APPLICATION FONT")
        lbl.setStyleSheet(f"color:{_t('muted')}; font-size:10px; letter-spacing:2px;")
        l.addWidget(lbl)

        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self.pw.app_font_family))
        l.addWidget(self.font_combo)

        note = QLabel("Tip: Nerd Fonts (NFP) render icons correctly.")
        note.setStyleSheet(f"color:{_t('txt_dim')}; font-size:11px; font-style:italic;")
        l.addWidget(note)

        row = QHBoxLayout()
        row.addStretch()
        save_btn = QPushButton("Apply")
        save_btn.setStyleSheet(f"background:{_t('cyan')}; color:{_t('bg_deep')}; font-weight:bold; border:none; padding:6px 18px;")
        save_btn.clicked.connect(self._save)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        row.addWidget(save_btn)
        row.addWidget(close_btn)
        l.addLayout(row)

    def _save(self):
        self.pw.app_font_family = self.font_combo.currentFont().family()
        self.pw.apply_global_font()
        self.pw.save_shortcuts_json()
        QMessageBox.information(self, "Applied", f"Font set to '{self.pw.app_font_family}'.")


# ══════════════════════════════════════════════════════════════════════
#  AHKShortcutEditor  (main window)
# ══════════════════════════════════════════════════════════════════════
class AHKShortcutEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.script_shortcuts  = []
        self.text_shortcuts    = []
        self.startup_scripts   = []
        self.context_shortcuts = []
        self.app_font_family   = "JetBrains Mono"
        self.category_colors   = {
            "System": "#ff4f6d", "Navigation": "#00e5ff", "Text": "#45b7d1",
            "Media": "#00ff9d", "AutoHotkey": "#ffb800", "General": "#b06cff",
            "Imported": "#ff7f50", "Tools": "#98d8c8", "Window": "#f7dc6f", "File": "#bb8fce"
        }
        self.settings         = QSettings("AHKEditor", "ShortcutEditor")
        self.selected_shortcut = None
        self.selected_type     = None

        self.load_shortcuts_json()
        self._build_ui()
        self._load_settings()
        self.apply_global_font()
        self.update_display()

    # ══ UI BUILD ══════════════════════════════════════════════════════
    def _build_ui(self):
        self.setWindowTitle("AutoHotkey Script Editor")
        self.setGeometry(80, 80, 1340, 820)
        self.setStyleSheet(GLOBAL_QSS)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── title bar ──
        title_bar = QWidget()
        title_bar.setFixedHeight(48)
        title_bar.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {_t('bg_deep')},
                stop:0.5 #0d1622,
                stop:1 {_t('bg_deep')}
            );
            border-bottom: 1px solid {_t('border')};
        """)
        tb_l = QHBoxLayout(title_bar)
        tb_l.setContentsMargins(16, 0, 16, 0)
        tb_l.setSpacing(12)

        logo = QLabel("⌨")
        logo.setStyleSheet(f"color:{_t('cyan')}; font-size:22px;")
        tb_l.addWidget(logo)

        title_lbl = QLabel("AHK SCRIPT EDITOR")
        title_lbl.setStyleSheet(f"""
            color: {_t('cyan')};
            font-size: 13px;
            font-weight: bold;
            letter-spacing: 3px;
        """)
        tb_l.addWidget(title_lbl)

        sep_v = QFrame()
        sep_v.setFrameShape(QFrame.Shape.VLine)
        sep_v.setStyleSheet(f"background:{_t('border')}; max-width:1px; margin:10px 0;")
        tb_l.addWidget(sep_v)

        # ── add button ──
        self.add_btn = QPushButton("＋  ADD")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background:{_t('cyan')};
                color:{_t('bg_deep')};
                font-weight:bold;
                font-size:12px;
                letter-spacing:1px;
                border:none;
                padding:5px 16px;
                border-radius:4px;
            }}
            QPushButton:hover {{
                background:{_t('green')};
            }}
            QPushButton::menu-indicator {{ image: none; }}
        """)
        add_menu = QMenu(self)
        for label, stype in [
            ("Script Shortcut",   "script"),
            ("Text Shortcut",     "text"),
            ("Context Shortcut",  "context"),
            ("Background Script", "startup"),
        ]:
            add_menu.addAction(label, lambda _, t=stype: self.open_add_dialog(t))
        self.add_btn.setMenu(add_menu)
        tb_l.addWidget(self.add_btn)

        # ── category toggle ──
        self.cat_toggle = QCheckBox("GROUP")
        self.cat_toggle.setChecked(True)
        self.cat_toggle.toggled.connect(self._on_cat_toggle)
        self.cat_toggle.setStyleSheet(f"""
            QCheckBox {{
                color:{_t('cyan')};
                font-size:11px;
                letter-spacing:1px;
            }}
            QCheckBox::indicator {{
                width:16px; height:16px;
                border:1px solid {_t('cyan')};
                border-radius:3px;
                background:{_t('bg_input')};
            }}
            QCheckBox::indicator:checked {{
                background:{_t('cyan')};
            }}
        """)
        tb_l.addWidget(self.cat_toggle)

        # ── colors ──
        colors_btn = QPushButton("🎨 Colors")
        colors_btn.setStyleSheet(f"""
            QPushButton {{
                background:{_t('bg_card')};
                border:1px solid {_t('purple')};
                color:{_t('purple')};
                font-size:12px;
                padding:4px 12px;
                border-radius:4px;
            }}
            QPushButton:hover {{
                background:{_t('bg_hover')};
                color:{_t('txt_hi')};
                border-color:{_t('txt_hi')};
            }}
        """)
        colors_btn.clicked.connect(self.open_color_dialog)
        tb_l.addWidget(colors_btn)

        # ── settings ──
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedWidth(34)
        settings_btn.setToolTip("Settings")
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background:{_t('bg_card')};
                border:1px solid {_t('border')};
                color:{_t('txt_mid')};
                font-size:16px;
                border-radius:4px;
            }}
            QPushButton:hover {{
                border-color:{_t('cyan')};
                color:{_t('cyan')};
            }}
        """)
        settings_btn.clicked.connect(lambda: SettingsDialog(self).exec())
        tb_l.addWidget(settings_btn)

        # ── search ──
        tb_l.addSpacing(8)
        self.search_edit = HotkeyLineEdit()
        self.search_edit.setPlaceholderText("⌕  Filter shortcuts…")
        self.search_edit.textChanged.connect(self.update_display)
        self.search_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_edit.setFixedHeight(30)
        self.search_edit.setStyleSheet(f"""
            QLineEdit {{
                background:{_t('bg_deep')};
                border:1px solid {_t('border')};
                border-radius:15px;
                padding:0 14px;
                color:{_t('txt_hi')};
                font-size:13px;
            }}
            QLineEdit:focus {{
                border-color:{_t('cyan')};
                background:{_t('bg_input')};
            }}
        """)

        self.rec_search_btn = QPushButton("⌨")
        self.rec_search_btn.setCheckable(True)
        self.rec_search_btn.setFixedSize(30, 30)
        self.rec_search_btn.setStyleSheet(f"""
            QPushButton {{
                font-size:15px;
                background:{_t('bg_deep')};
                border:1px solid {_t('border')};
                border-radius:15px;
                color:{_t('txt_dim')};
            }}
            QPushButton:checked {{
                background:{_t('bg_sel')};
                border-color:{_t('cyan')};
                color:{_t('cyan')};
            }}
            QPushButton:hover {{ border-color:{_t('cyan')}; }}
        """)
        self.rec_search_btn.clicked.connect(lambda chk: self.search_edit.set_recording(chk))
        self.search_edit.record_button = self.rec_search_btn
        tb_l.addWidget(self.search_edit)
        tb_l.addWidget(self.rec_search_btn)
        tb_l.addSpacing(8)

        # ── generate ──
        gen_btn = QPushButton("🚀  GENERATE")
        gen_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #005fa3, stop:1 #0080cc);
                color: white;
                font-weight:bold;
                font-size:12px;
                letter-spacing:1px;
                border:none;
                padding:5px 16px;
                border-radius:4px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0070bb, stop:1 #0099e6);
            }}
        """)
        gen_btn.clicked.connect(self.generate_ahk_script)
        tb_l.addWidget(gen_btn)
        root.addWidget(title_bar)

        # ── text browser ──
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.anchorClicked.connect(self._handle_click)
        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self._show_ctx_menu)
        self.browser.viewport().installEventFilter(self)
        root.addWidget(self.browser, stretch=1)

        # ── status bar ──
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background:{_t('bg_deep')};
                border-top:1px solid {_t('border')};
                color:{_t('txt_dim')};
                font-size:11px;
                padding:0 10px;
            }}
        """)

        # right-click menu
        self.ctx_menu = QMenu(self)
        self.act_edit  = self.ctx_menu.addAction("✏  Edit")
        self.act_dupe  = self.ctx_menu.addAction("⧉  Duplicate")
        self.ctx_menu.addSeparator()
        self.act_del   = self.ctx_menu.addAction("✕  Remove")
        self.act_edit.triggered.connect(self.edit_selected)
        self.act_dupe.triggered.connect(self.duplicate_selected)
        self.act_del.triggered.connect(self.remove_selected)

    # ══ FONT ══════════════════════════════════════════════════════════
    def apply_global_font(self):
        QApplication.instance().setFont(QFont(self.app_font_family, _t('font_size')))
        if hasattr(self, 'browser'):
            self.update_display()

    # ══ SETTINGS ══════════════════════════════════════════════════════
    def _load_settings(self):
        self.cat_toggle.setChecked(self.settings.value("group_by_category", True, type=bool))

    def _save_settings(self):
        self.settings.setValue("group_by_category", self.cat_toggle.isChecked())

    def _on_cat_toggle(self):
        self._save_settings()
        self.update_display()

    def closeEvent(self, event):
        self._save_settings()
        event.accept()

    # ══ DATA I/O ══════════════════════════════════════════════════════
    def load_shortcuts_json(self):
        if os.path.exists(SHORTCUTS_JSON_PATH):
            try:
                with open(SHORTCUTS_JSON_PATH, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                self.script_shortcuts  = d.get("script_shortcuts", [])
                self.text_shortcuts    = d.get("text_shortcuts", [])
                self.startup_scripts   = d.get("startup_scripts", [])
                self.context_shortcuts = d.get("context_shortcuts", [])
                self.app_font_family   = d.get("app_font_family", "JetBrains Mono")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))
                self._create_defaults()
        else:
            self._create_defaults()

    def _create_defaults(self):
        self.script_shortcuts = [{
            "name": "Open Terminal", "category": "System",
            "description": "Opens PowerShell as admin",
            "hotkey": "!x", "enabled": True,
            "action": 'RunWait("pwsh -Command `"Start-Process pwsh -Verb RunAs`"",,"Hide")'
        }]
        self.text_shortcuts = [
            {"name": "AHK v2 Header", "category": "AutoHotkey", "description": "v2 require line",
             "trigger": ";v2", "replacement": "#Requires AutoHotkey v2.0", "enabled": True},
        ]

    def save_shortcuts_json(self):
        try:
            with open(SHORTCUTS_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump({
                    "script_shortcuts":  self.script_shortcuts,
                    "text_shortcuts":    self.text_shortcuts,
                    "startup_scripts":   self.startup_scripts,
                    "context_shortcuts": self.context_shortcuts,
                    "app_font_family":   self.app_font_family,
                }, f, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def get_category_color(self, cat):
        return self.category_colors.get(cat, "#7070a0")

    # ══ DISPLAY ═══════════════════════════════════════════════════════
    def update_display(self):
        sb  = self.browser.verticalScrollBar()
        pos = sb.value()
        q   = self.search_edit.text().lower()
        grp = self.cat_toggle.isChecked()

        def filt(lst, keys):
            return [s for s in lst if q in " ".join(s.get(k,"") for k in keys).lower()]

        fs = filt(self.script_shortcuts,  ["name","hotkey","description","category"])
        ft = filt(self.text_shortcuts,    ["name","trigger","description","category"])
        fc = filt(self.context_shortcuts, ["name","hotkey","description","category","window_title"])
        fu = filt(self.startup_scripts,   ["name","description","category"])

        self.browser.setHtml(self._gen_html(fs, ft, fc, fu, grp))
        sb.setValue(pos)
        QTimer.singleShot(1, lambda: sb.setValue(pos))

    def _gen_html(self, scripts, texts, contexts, startups, grouped):
        f = self.app_font_family
        c = _t

        html = f"""<!DOCTYPE html><html><head><style>
        * {{ box-sizing:border-box; margin:0; padding:0; }}
        body {{
            font-family:'{f}','Consolas',monospace;
            background:{c('bg_base')};
            color:{c('txt_hi')};
            font-size:14px;
            padding:10px 14px;
        }}
        .grid {{ display:flex; gap:14px; align-items:flex-start; }}
        .col {{ flex:1; min-width:0; }}
        .sec-hdr {{
            font-size:11px;
            font-weight:bold;
            letter-spacing:3px;
            color:{c('cyan')};
            padding:6px 10px 4px 10px;
            margin-bottom:4px;
            border-bottom:1px solid {c('border')};
            text-transform:uppercase;
        }}
        .cat-hdr {{
            font-size:11px;
            letter-spacing:1px;
            font-weight:bold;
            padding:8px 10px 3px 10px;
            margin-top:6px;
            color:#888;
        }}
        .item {{
            display:flex;
            align-items:center;
            padding:4px 8px;
            border-radius:4px;
            border-left:2px solid transparent;
            margin:1px 0;
            cursor:pointer;
        }}
        .item:hover {{ background:{c('bg_hover')}; border-left-color:{c('cyan')}; }}
        .item.sel {{ background:{c('bg_sel')}; border-left-color:{c('cyan')}; }}
        .item.dis {{ opacity:0.45; }}
        .tog {{ width:22px; flex-shrink:0; text-align:center; font-size:13px; }}
        .key {{
            font-weight:bold;
            color:{c('amber')};
            white-space:nowrap;
            padding-right:10px;
            min-width:120px;
            font-size:13px;
        }}
        .arrow {{ color:{c('green')}; padding:0 6px; font-size:15px; font-weight:bold; }}
        .nm {{ color:{c('txt_hi')}; font-size:13px; }}
        .dsc {{ color:{c('txt_dim')}; font-size:11px; margin-left:6px; }}
        a {{ text-decoration:none; color:inherit; display:contents; }}
        </style></head><body><div class="grid">
        """

        def col_open(title):
            return f'<div class="col"><div class="sec-hdr">{title}</div>'

        def col_close():
            return '</div>'

        def item_html(s, stype, idx, indented):
            enabled = s.get("enabled", True)
            is_sel  = (self.selected_shortcut is s and self.selected_type == stype)
            cls     = "item" + (" sel" if is_sel else "") + ("" if enabled else " dis")
            bg      = f'background:{_t("bg_sel")};' if is_sel else ""
            tog_ic  = "●" if enabled else "○"
            tog_col = _t('green') if enabled else _t('red')

            if stype == "script":
                key = s.get("hotkey", "")
            elif stype == "context":
                key = s.get("hotkey", "")
                wt  = s.get("window_title", "")
                if wt:
                    key += f" [{wt[:12]}…]" if len(wt) > 12 else f" [{wt}]"
            elif stype == "startup":
                key = "▶ startup"
            else:
                key = s.get("trigger", "")

            nm   = s.get("name","Unnamed")
            desc = s.get("description","")
            dsc_html = f'<span class="dsc">({desc[:28]}{"…" if len(desc)>28 else ""})</span>' if desc else ""

            return f"""
            <div class="{cls}" style="{bg}">
                <a href="toggle://{stype}/{idx}">
                    <span class="tog" style="color:{tog_col}">{tog_ic}</span>
                </a>
                <a href="select://{stype}/{idx}" style="display:flex;align-items:center;flex:1;min-width:0;">
                    <span class="key">{key}</span>
                    <span class="arrow">›</span>
                    <span class="nm">{nm}</span>
                    {dsc_html}
                </a>
            </div>"""

        def render_section(items_list, master_list, stype, sort_key):
            items = sorted(items_list, key=lambda x: x.get(sort_key,"").lower())
            html_out = ""
            if grouped:
                cats = {}
                for s in items:
                    cats.setdefault(s.get("category","General"), []).append(s)
                for cat in sorted(cats):
                    color = self.get_category_color(cat)
                    html_out += f'<div class="cat-hdr" style="color:{color}">▸ {cat}</div>'
                    for s in sorted(cats[cat], key=lambda x: x.get(sort_key,"").lower()):
                        idx = master_list.index(s)
                        html_out += item_html(s, stype, idx, True)
            else:
                for s in items:
                    idx = master_list.index(s)
                    html_out += item_html(s, stype, idx, False)
            return html_out

        # col 1: Script shortcuts
        html += col_open("Script Shortcuts")
        html += render_section(scripts, self.script_shortcuts, "script", "hotkey")
        html += col_close()

        # col 2: Context + Background
        html += col_open("Context Shortcuts")
        html += render_section(contexts, self.context_shortcuts, "context", "hotkey")
        html += '<div class="sec-hdr" style="margin-top:16px;">Background Scripts</div>'
        html += render_section(startups, self.startup_scripts, "startup", "name")
        html += col_close()

        # col 3: Text shortcuts
        html += col_open("Text Shortcuts")
        html += render_section(texts, self.text_shortcuts, "text", "trigger")
        html += col_close()

        html += "</div></body></html>"
        return html

    # ══ INTERACTION ═══════════════════════════════════════════════════
    def _handle_click(self, url):
        s = url.toString()

        if s.startswith("select://"):
            parts = s.replace("select://","").split("/")
            if len(parts) == 2:
                stype, idx = parts[0], int(parts[1])
                lst = {"script":self.script_shortcuts,"text":self.text_shortcuts,
                       "context":self.context_shortcuts,"startup":self.startup_scripts}.get(stype,[])
                if idx < len(lst):
                    self.selected_shortcut = lst[idx]
                    self.selected_type     = stype
            self.update_display()

        elif s.startswith("toggle://"):
            parts = s.replace("toggle://","").split("/")
            if len(parts) == 2:
                stype, idx = parts[0], int(parts[1])
                lst = {"script":self.script_shortcuts,"text":self.text_shortcuts,
                       "context":self.context_shortcuts,"startup":self.startup_scripts}.get(stype,[])
                if idx < len(lst):
                    lst[idx]["enabled"] = not lst[idx].get("enabled", True)
            self.save_shortcuts_json()
            self.update_display()

    def _show_ctx_menu(self, pos):
        if self.selected_shortcut and self.selected_type:
            self.ctx_menu.exec(self.browser.mapToGlobal(pos))

    def eventFilter(self, obj, event):
        if (obj == self.browser.viewport() and
                event.type() == event.Type.MouseButtonDblClick and
                event.button() == Qt.MouseButton.LeftButton):
            anchor = self.browser.anchorAt(event.pos())
            if anchor:
                self._handle_click(QUrl(anchor))
                self.edit_selected()
            return True
        return super().eventFilter(obj, event)

    # ══ ACTIONS ═══════════════════════════════════════════════════════
    def open_add_dialog(self, stype):
        AddEditShortcutDialog(self, stype).exec()

    def edit_selected(self):
        if not self.selected_shortcut:
            QMessageBox.warning(self, "No Selection", "Click a shortcut first.")
            return
        AddEditShortcutDialog(self, self.selected_type, self.selected_shortcut).exec()

    def duplicate_selected(self):
        if not self.selected_shortcut:
            QMessageBox.warning(self, "No Selection", "Click a shortcut first.")
            return
        duped = copy.deepcopy(self.selected_shortcut)
        orig  = duped.get("name","Unnamed")
        duped["name"] = f"{orig} (Copy)"
        if self.selected_type in ("script","context"):
            duped["hotkey"] = ""
        elif self.selected_type == "text":
            duped["trigger"] = ""
        lst_map = {
            "script": self.script_shortcuts, "context": self.context_shortcuts,
            "startup": self.startup_scripts, "text": self.text_shortcuts
        }
        lst_map[self.selected_type].append(duped)
        self.selected_shortcut = duped
        self.save_shortcuts_json()
        self.update_display()
        QMessageBox.information(self, "Duplicated",
            f"'{orig}' copied as '{duped['name']}'.\nEdit the duplicate to set a unique hotkey/trigger.")

    def remove_selected(self):
        if not self.selected_shortcut:
            QMessageBox.warning(self, "No Selection", "Click a shortcut first.")
            return
        if QMessageBox.question(self,"Confirm Remove",
            f"Remove '{self.selected_shortcut.get('name','?')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            lst_map = {
                "script": self.script_shortcuts, "context": self.context_shortcuts,
                "startup": self.startup_scripts, "text": self.text_shortcuts
            }
            lst_map[self.selected_type].remove(self.selected_shortcut)
            self.selected_shortcut = None
            self.selected_type     = None
            self.save_shortcuts_json()
            self.update_display()

    def open_color_dialog(self):
        CategoryColorDialog(self).exec()

    # ══ AHK GENERATOR ════════════════════════════════════════════════
    def generate_ahk_script(self):
        try:
            lines = [
                "#Requires AutoHotkey v2.0", "#SingleInstance", "Persistent", "",
                "Paste(text) {",
                "    Old := A_Clipboard",
                "    A_Clipboard := \"\"",
                "    A_Clipboard := text",
                "    if !ClipWait(1)",
                "        return",
                "    SendInput \"^v\"",
                "    Sleep 250",
                "    A_Clipboard := Old",
                "}", "",
            ]

            def clean(action):
                return action.replace(',,,', ',,')

            # Startup
            enabled_su = [s for s in self.startup_scripts if s.get("enabled", True)]
            if enabled_su:
                lines.append(";! === BACKGROUND / STARTUP SCRIPTS ===")
                for s in enabled_su:
                    lines += [f";! {s.get('name','')}", clean(s.get("action","")), ""]

            # Script shortcuts
            enabled_sc = [s for s in self.script_shortcuts if s.get("enabled", True)]
            if enabled_sc:
                lines.append(";! === SCRIPT SHORTCUTS ===")
                for s in enabled_sc:
                    lines.append(f";! {s.get('name','')}")
                    if s.get('description'): lines.append(f";! {s['description']}")
                    hk  = s.get("hotkey","")
                    act = clean(s.get("action",""))
                    if '\n' in act:
                        lines.append(f"{hk}:: {{")
                        for ln in act.split('\n'):
                            if ln.strip(): lines.append(f"    {ln}")
                        lines.append("}")
                    else:
                        lines.append(f"{hk}::{act}")
                    lines.append("")

            # Context shortcuts
            enabled_cx = [s for s in self.context_shortcuts if s.get("enabled", True)]
            if enabled_cx:
                lines.append(";! === CONTEXT SHORTCUTS ===")
                for s in enabled_cx:
                    lines.append(f";! {s.get('name','')}")
                    wt = s.get("window_title","")
                    pn = s.get("process_name","")
                    wc = s.get("window_class","")
                    fn = f"Is{''.join(w.capitalize() for w in s.get('name','Context').split())}Ctx"
                    conds = []
                    if pn: conds.append(f'processName = "{pn}"')
                    if wt: conds.append(f'InStr(windowTitle,"{wt}")')
                    if wc: conds.append(f'windowClass = "{wc}"')
                    cond = " && ".join(conds)
                    lines += [f"{fn}() {{", "    try {"]
                    if pn: lines.append('        processName := WinGetProcessName("A")')
                    if wt: lines.append('        windowTitle := WinGetTitle("A")')
                    if wc: lines.append('        windowClass := WinGetClass("A")')
                    lines += [f"        if ({cond}) {{","            return true","        }","    }","    return false","}", ""]
                    lines.append(f"#HotIf {fn}()")
                    act = clean(s.get("action",""))
                    hk  = s.get("hotkey","")
                    if '\n' in act:
                        lines.append(f"{hk}:: {{")
                        for ln in act.split('\n'):
                            if ln.strip(): lines.append(f"    {ln}")
                        lines += ["}",""]
                    else:
                        lines += [f"{hk}::{act}",""]
                    lines += ["#HotIf",""]

            # Text shortcuts
            enabled_tx = [s for s in self.text_shortcuts if s.get("enabled", True)]
            if enabled_tx:
                lines.append(";! === TEXT SHORTCUTS ===")
                for s in enabled_tx:
                    lines.append(f";! {s.get('name','')}")
                    trig = s.get("trigger","")
                    repl = s.get("replacement","")
                    if '\n' in repl:
                        safe = repl.replace('"','""')
                        lines.append(f':X:{trig}::Paste("')
                        lines.append("(")
                        for ln in safe.split('\n'):
                            lines.append("`" + ln if ln.strip().startswith(")") else ln)
                        lines += [')")', ""]
                    else:
                        safe = repl.replace("'","''")
                        lines += [f":X:{trig}::Paste('{safe}')", ""]

            out = os.path.join(SCRIPT_DIR, "generated_shortcuts.ahk")
            with open(out, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            self.statusBar().showMessage(f"✔  Generated → {out}", 4000)

        except Exception as e:
            QMessageBox.critical(self, "Generate Error", str(e))


# ══════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark Fusion palette to prevent white flash before QSS kicks in
    pal = QPalette()
    dark = QColor(_t('bg_base'))
    pal.setColor(QPalette.ColorRole.Window,          dark)
    pal.setColor(QPalette.ColorRole.WindowText,      QColor(_t('txt_hi')))
    pal.setColor(QPalette.ColorRole.Base,            QColor(_t('bg_input')))
    pal.setColor(QPalette.ColorRole.AlternateBase,   QColor(_t('bg_panel')))
    pal.setColor(QPalette.ColorRole.ToolTipBase,     QColor(_t('bg_card')))
    pal.setColor(QPalette.ColorRole.ToolTipText,     QColor(_t('txt_hi')))
    pal.setColor(QPalette.ColorRole.Text,            QColor(_t('txt_hi')))
    pal.setColor(QPalette.ColorRole.Button,          QColor(_t('bg_card')))
    pal.setColor(QPalette.ColorRole.ButtonText,      QColor(_t('txt_hi')))
    pal.setColor(QPalette.ColorRole.BrightText,      QColor(_t('cyan')))
    pal.setColor(QPalette.ColorRole.Highlight,       QColor(_t('bg_sel')))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(_t('cyan')))
    app.setPalette(pal)

    window = AHKShortcutEditor()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
