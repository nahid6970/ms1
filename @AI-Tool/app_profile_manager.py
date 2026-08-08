import sys
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
    QMessageBox, QDialog, QCheckBox, QDateTimeEdit, QRadioButton, QButtonGroup,
    QListWidget, QListWidgetItem, QAbstractItemView, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QDate, QTime, QSize, QByteArray
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap, QIcon
from PyQt6.QtSvg import QSvgRenderer

from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# ── CYBERPUNK THEME PALETTE ──────────────────────────────────────────────────
CP_BG      = "#050505"  # Main Window Background
CP_PANEL   = "#111111"  # Panel/Input Background
CP_YELLOW  = "#FCEE0A"  # Accent: Yellow
CP_CYAN    = "#00F0FF"  # Accent: Cyan
CP_RED     = "#FF003C"  # Accent: Red
CP_GREEN   = "#00FF21"  # Accent: Green
CP_ORANGE  = "#FF934B"  # Accent: Orange
CP_DIM     = "#3A3A3A"  # Dimmed/Borders/Inactive
CP_TEXT    = "#E0E0E0"  # Primary Text
CP_SUBTEXT = "#808080"  # Secondary Text

FONT_MAIN  = "Consolas"

# ── RELATIVE PATH INITIALIZATION ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "app_profiles.json")
PROFILE_DATA_DIR = os.path.join(BASE_DIR, "profile_data")

os.makedirs(PROFILE_DATA_DIR, exist_ok=True)

# ── INLINE VECTOR SVG DEFINITIONS ────────────────────────────────────────────
SVG_RESTART = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>"""

SVG_SETTINGS = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>"""

SVG_CONFIG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>"""

SVG_BACK = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>"""

SVG_EDIT = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>"""

SVG_DELETE = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>"""

SVG_CHEVRON = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>"""

SVG_LOCK = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>"""

SVG_DIAMOND = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 22 12 12 22 2 12 12 2"/></svg>"""

# ── SVG ICON GENERATION ───────────────────────────────────────────────────────
def make_svg_icon(svg_str, normal_color=CP_TEXT, hover_color=CP_CYAN, size=24):
    icon = QIcon()
    
    # Normal State
    pix1 = QPixmap(size, size)
    pix1.fill(Qt.GlobalColor.transparent)
    p1 = QPainter(pix1)
    r1 = QSvgRenderer(QByteArray(svg_str.replace("currentColor", normal_color).encode('utf-8')))
    r1.render(p1)
    p1.end()
    icon.addPixmap(pix1, QIcon.Mode.Normal, QIcon.State.Off)
    
    # Active/Hover State
    pix2 = QPixmap(size, size)
    pix2.fill(Qt.GlobalColor.transparent)
    p2 = QPainter(pix2)
    r2 = QSvgRenderer(QByteArray(svg_str.replace("currentColor", hover_color).encode('utf-8')))
    r2.render(p2)
    p2.end()
    icon.addPixmap(pix2, QIcon.Mode.Active, QIcon.State.Off)
    
    return icon

def render_svg_pixmap(svg_str, color=CP_CYAN, size=18):
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    r = QSvgRenderer(QByteArray(svg_str.replace("currentColor", color).encode('utf-8')))
    r.render(p)
    p.end()
    return pix


# ── CRYPTOGRAPHY HELPERS ──────────────────────────────────────────────────────
def derive_key(password, salt, key_length=32):
    return PBKDF2(password.encode('utf-8'), salt, dkLen=key_length)

def encrypt_file_data(data_bytes, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
    return salt + tag + cipher.nonce + ciphertext

def decrypt_file_data(encrypted_bytes, password):
    if len(encrypted_bytes) < 48:
        raise Exception("Corrupted or invalid encrypted file data.")
    salt = encrypted_bytes[:16]
    tag = encrypted_bytes[16:32]
    nonce = encrypted_bytes[32:48]
    ciphertext = encrypted_bytes[48:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    try:
        return cipher.decrypt_and_verify(ciphertext, tag)
    except (ValueError, KeyError):
        raise Exception("Decryption failed. Incorrect password or corrupted file.")

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()


# ── GLOBAL QSS STYLESHEET ─────────────────────────────────────────────────────
GLOBAL_STYLE = f"""
    QMainWindow, QDialog {{
        background-color: {CP_BG};
    }}
    QWidget {{
        color: {CP_TEXT};
        font-family: '{FONT_MAIN}', monospace;
        font-size: 10pt;
    }}
    QLineEdit, QDateTimeEdit, QListWidget {{
        background-color: {CP_PANEL};
        color: {CP_CYAN};
        border: 1px solid {CP_DIM};
        padding: 6px 10px;
        selection-background-color: {CP_CYAN};
        selection-color: #000000;
    }}
    QLineEdit:focus, QDateTimeEdit:focus, QListWidget:focus {{
        border: 1px solid {CP_CYAN};
    }}
    QLineEdit:disabled {{
        color: {CP_SUBTEXT};
        border-color: {CP_DIM};
    }}
    QListWidget::item {{
        padding: 6px;
        color: {CP_TEXT};
    }}
    QListWidget::item:hover {{
        background-color: #1A1A1A;
        color: {CP_CYAN};
    }}
    QListWidget::indicator {{
        width: 14px; height: 14px;
        border: 1px solid {CP_DIM};
        background-color: {CP_PANEL};
    }}
    QListWidget::indicator:checked {{
        background-color: {CP_YELLOW};
        border-color: {CP_YELLOW};
    }}
    QCheckBox, QRadioButton {{
        spacing: 8px;
        color: {CP_TEXT};
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 14px; height: 14px;
        border: 1px solid {CP_DIM};
        background: {CP_PANEL};
    }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background: {CP_YELLOW};
        border-color: {CP_YELLOW};
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
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
        background: none;
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
    QMessageBox {{
        background-color: {CP_PANEL};
        color: {CP_TEXT};
    }}
"""


def make_label(text, size=10, color=CP_TEXT, bold=False):
    lbl = QLabel(text)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(
        f"color: {color}; font-family: '{FONT_MAIN}', monospace; font-size: {size}pt; font-weight: {weight}; background: transparent;"
    )
    return lbl


def make_primary_btn(text, min_width=110):
    btn = QPushButton(text)
    btn.setMinimumWidth(min_width)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {CP_DIM};
            border: 1px solid {CP_CYAN};
            color: {CP_CYAN};
            padding: 7px 14px;
            font-weight: bold;
            font-family: '{FONT_MAIN}', monospace;
        }}
        QPushButton:hover {{
            background-color: {CP_CYAN};
            color: #000000;
            border: 1px solid {CP_CYAN};
        }}
        QPushButton:pressed {{
            background-color: {CP_YELLOW};
            color: #000000;
        }}
    """)
    return btn


def make_secondary_btn(text, min_width=90):
    btn = QPushButton(text)
    btn.setMinimumWidth(min_width)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {CP_PANEL};
            border: 1px solid {CP_DIM};
            color: {CP_TEXT};
            padding: 6px 12px;
            font-weight: bold;
            font-family: '{FONT_MAIN}', monospace;
        }}
        QPushButton:hover {{
            background-color: #2A2A2A;
            border: 1px solid {CP_YELLOW};
            color: {CP_YELLOW};
        }}
        QPushButton:pressed {{
            background-color: {CP_YELLOW};
            color: #000000;
        }}
    """)
    return btn


def make_svg_button(svg_xml, tooltip="", size=34, icon_size=16, normal_color=CP_TEXT, hover_color=CP_CYAN):
    btn = QPushButton()
    btn.setFixedSize(size, size)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if tooltip:
        btn.setToolTip(tooltip)
    
    icon = make_svg_icon(svg_xml, normal_color=normal_color, hover_color=hover_color, size=icon_size)
    btn.setIcon(icon)
    btn.setIconSize(QSize(icon_size, icon_size))
    
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {CP_PANEL};
            border: 1px solid {CP_DIM};
            padding: 0px;
        }}
        QPushButton:hover {{
            background-color: #2A2A2A;
            border: 1px solid {CP_CYAN};
        }}
        QPushButton:pressed {{
            background-color: {CP_YELLOW};
        }}
    """)
    return btn


def make_card_svg_button(svg_xml, tooltip="", size=28, icon_size=14, normal_color=CP_SUBTEXT, hover_color=CP_CYAN):
    btn = QPushButton()
    btn.setFixedSize(size, size)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if tooltip:
        btn.setToolTip(tooltip)
    
    icon = make_svg_icon(svg_xml, normal_color=normal_color, hover_color=hover_color, size=icon_size)
    btn.setIcon(icon)
    btn.setIconSize(QSize(icon_size, icon_size))
    
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {CP_BG};
            border: 1px solid {CP_DIM};
            padding: 0px;
        }}
        QPushButton:hover {{
            background-color: {CP_PANEL};
            border: 1px solid {CP_CYAN};
        }}
        QPushButton:pressed {{
            border-color: {CP_RED};
        }}
    """)
    return btn


def make_divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"background: {CP_DIM}; border: none; max-height: 1px;")
    return line


# ── MASTER PASSWORD DIALOG ──────────────────────────────────────────────────
class MasterPasswordDialog(QDialog):
    def __init__(self, parent=None, current_password=""):
        super().__init__(parent)
        self.current_password = current_password
        self.init_ui()

    def init_ui(self):
        title = "CHANGE MASTER PASSWORD" if self.current_password else "SET MASTER PASSWORD"
        self.setWindowTitle(title)
        self.setFixedWidth(440)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.addWidget(make_label(f"// {title}", size=12, color=CP_YELLOW, bold=True))
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet(f"background: {CP_BG};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        info_text = "Master password will automatically lock/encrypt session files across all applications."
        layout.addWidget(make_label(info_text, size=9, color=CP_SUBTEXT))

        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter master password...")
        layout.addWidget(make_label("Master Password", size=10, color=CP_CYAN))
        layout.addWidget(self.pwd_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm master password...")
        layout.addWidget(make_label("Confirm Password", size=10, color=CP_CYAN))
        layout.addWidget(self.confirm_input)

        root.addWidget(body)

        footer = QFrame()
        footer.setStyleSheet(f"background: {CP_PANEL}; border-top: 1px solid {CP_DIM};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 12, 20, 12)
        f_layout.setSpacing(10)
        f_layout.addStretch()

        if self.current_password:
            cancel_btn = make_secondary_btn("CANCEL", min_width=80)
            cancel_btn.clicked.connect(self.reject)
            f_layout.addWidget(cancel_btn)

        save_btn = make_primary_btn("SAVE PASSWORD", min_width=120)
        save_btn.clicked.connect(self.save)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    def save(self):
        p1 = self.pwd_input.text()
        p2 = self.confirm_input.text()
        if not p1:
            QMessageBox.warning(self, "Validation Error", "Master password cannot be empty.")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return
        self.master_password = p1
        self.accept()


# ── EXTENSIBLE SETTINGS DIALOG ───────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, parent=None, master_password="", auto_capture=True):
        super().__init__(parent)
        self.master_password = master_password
        self.auto_capture = auto_capture
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("SETTINGS")
        self.setFixedWidth(460)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.addWidget(make_label("// GLOBAL CONFIGURATION", size=12, color=CP_YELLOW, bold=True))
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet(f"background: {CP_BG};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        # Security Box
        sec_box = QGroupBox("SECURITY & ENCRYPTION")
        sec_layout = QVBoxLayout(sec_box)
        sec_layout.setSpacing(10)

        pwd_row = QHBoxLayout()
        pwd_row.setSpacing(8)
        self.pwd_input = QLineEdit(self.master_password)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        pwd_btn = make_secondary_btn("Update", min_width=70)
        pwd_btn.clicked.connect(self.update_password_dialog)
        pwd_row.addWidget(self.pwd_input)
        pwd_row.addWidget(pwd_btn)

        sec_layout.addWidget(make_label("Master Encryption Password:", size=9, color=CP_SUBTEXT))
        sec_layout.addLayout(pwd_row)
        layout.addWidget(sec_box)

        # Preferences Box
        pref_box = QGroupBox("PREFERENCES")
        pref_layout = QVBoxLayout(pref_box)
        pref_layout.setSpacing(10)

        self.auto_capture_cb = QCheckBox("Auto-capture session files when adding new account")
        self.auto_capture_cb.setChecked(self.auto_capture)
        pref_layout.addWidget(self.auto_capture_cb)

        layout.addWidget(pref_box)
        root.addWidget(body)

        # Footer
        footer = QFrame()
        footer.setStyleSheet(f"background: {CP_PANEL}; border-top: 1px solid {CP_DIM};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 12, 20, 12)
        f_layout.setSpacing(10)
        f_layout.addStretch()

        cancel_btn = make_secondary_btn("CANCEL", min_width=80)
        save_btn = make_primary_btn("SAVE SETTINGS", min_width=120)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save)
        f_layout.addWidget(cancel_btn)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    def update_password_dialog(self):
        dialog = MasterPasswordDialog(self, current_password=self.master_password)
        if dialog.exec():
            self.master_password = dialog.master_password
            self.pwd_input.setText(self.master_password)

    def save(self):
        self.master_password = self.pwd_input.text().strip()
        self.auto_capture = self.auto_capture_cb.isChecked()
        self.accept()


# ── APPLICATION DIALOG ───────────────────────────────────────────────────────
class AppDialog(QDialog):
    def __init__(self, parent=None, app_name="", app_config=None):
        super().__init__(parent)
        self.app_name_orig = app_name
        self.app_config = app_config or {
            "target_path": "",
            "sync_items": [],
            "is_locked": True
        }
        self.init_ui()
        if self.app_config.get("target_path"):
            self.populate_target_items()

    def init_ui(self):
        title = f"APP SETTINGS ({self.app_name_orig})" if self.app_name_orig else "NEW APPLICATION"
        self.setWindowTitle(title)
        self.setFixedWidth(560)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet(f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 18, 24, 18)
        h_layout.addWidget(make_label(f"// {title}", size=12, color=CP_YELLOW, bold=True))
        root.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet(f"background: {CP_BG};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # App Name
        self.app_input = QLineEdit(self.app_name_orig)
        self.app_input.setPlaceholderText("e.g. Discord, Stable Diffusion, Steam")
        layout.addWidget(make_label("Application Name", size=10, color=CP_CYAN))
        layout.addWidget(self.app_input)

        # Target Path
        tgt_row = QHBoxLayout()
        tgt_row.setSpacing(8)
        self.target_input = QLineEdit(self.app_config.get("target_path", ""))
        self.target_input.setPlaceholderText("Select main App target directory path...")
        self.target_input.editingFinished.connect(self.populate_target_items)

        tgt_browse = make_secondary_btn("Browse", min_width=80)
        tgt_browse.setFixedHeight(34)
        tgt_browse.clicked.connect(self.browse_target)
        tgt_row.addWidget(self.target_input)
        tgt_row.addWidget(tgt_browse)
        layout.addWidget(make_label("Target Application Directory Path", size=10, color=CP_CYAN))
        layout.addLayout(tgt_row)

        layout.addWidget(make_divider())

        # Auto-Scanned Files/Folders Checklist
        layout.addWidget(make_label("Check Files & Folders to Sync / Swap with Profile:", size=10, color=CP_YELLOW))
        self.items_list = QListWidget()
        self.items_list.setFixedHeight(140)

        items_btn_row = QHBoxLayout()
        items_btn_row.setSpacing(8)
        
        select_all_btn = make_secondary_btn("Select All", min_width=85)
        deselect_all_btn = make_secondary_btn("Deselect All", min_width=85)
        rescan_btn = make_secondary_btn("Rescan Path", min_width=95)

        select_all_btn.clicked.connect(self.select_all_items)
        deselect_all_btn.clicked.connect(self.deselect_all_items)
        rescan_btn.clicked.connect(self.populate_target_items)

        items_btn_row.addWidget(select_all_btn)
        items_btn_row.addWidget(deselect_all_btn)
        items_btn_row.addWidget(rescan_btn)

        layout.addWidget(self.items_list)
        layout.addLayout(items_btn_row)

        layout.addWidget(make_divider())

        # Encryption Checkbox
        self.lock_checkbox = QCheckBox("Encrypt stored profile files using Master Password (.enc)")
        self.lock_checkbox.setChecked(self.app_config.get("is_locked", True))
        layout.addWidget(self.lock_checkbox)

        root.addWidget(body)

        # Footer
        footer = QFrame()
        footer.setStyleSheet(f"background: {CP_PANEL}; border-top: 1px solid {CP_DIM};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 14, 24, 14)
        f_layout.setSpacing(10)
        f_layout.addStretch()
        cancel_btn = make_secondary_btn("CANCEL", min_width=90)
        save_btn   = make_primary_btn("SAVE APP SETTINGS", min_width=140)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save)
        f_layout.addWidget(cancel_btn)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    def browse_target(self):
        path = QFileDialog.getExistingDirectory(self, "Select Target Application Directory")
        if path:
            norm_path = os.path.normpath(path)
            self.target_input.setText(norm_path)
            self.populate_target_items()

    def populate_target_items(self):
        target_dir = self.target_input.text().strip()
        if not target_dir or not os.path.exists(target_dir) or not os.path.isdir(target_dir):
            return

        saved_sync = set(self.app_config.get("sync_items", []))
        is_default_check = len(saved_sync) == 0 or "*" in saved_sync

        self.items_list.clear()

        try:
            entries = sorted(os.listdir(target_dir))
        except Exception:
            return

        for entry in entries:
            full_path = os.path.join(target_dir, entry)
            is_dir = os.path.isdir(full_path)
            display_name = entry + ("/" if is_dir else "")
            clean_name = entry

            item = QListWidgetItem(display_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)

            if is_default_check or clean_name in saved_sync or display_name in saved_sync:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)

            self.items_list.addItem(item)

    def select_all_items(self):
        for i in range(self.items_list.count()):
            self.items_list.item(i).setCheckState(Qt.CheckState.Checked)

    def deselect_all_items(self):
        for i in range(self.items_list.count()):
            self.items_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def save(self):
        app_name = self.app_input.text().strip()
        target_path = self.target_input.text().strip()
        if not app_name or not target_path:
            QMessageBox.warning(self, "Validation Error", "Application Name and Target Path are required.")
            return

        sync_items = []
        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                clean_text = item.text().rstrip('/')
                sync_items.append(clean_text)

        if not sync_items:
            sync_items = ["*"]

        self.app_name = app_name
        self.app_config = {
            "target_path": target_path,
            "sync_items": sync_items,
            "is_locked": self.lock_checkbox.isChecked()
        }
        self.accept()


# ── ACCOUNT / PROFILE DIALOG ──────────────────────────────────────────────────
class AccountDialog(QDialog):
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile or {
            "name": "", "timer_enabled": False, "target_time": None
        }
        self.capture_now = True
        self.init_ui()

    def init_ui(self):
        is_edit = bool(self.profile.get("name"))
        title = "EDIT ACCOUNT" if is_edit else "NEW ACCOUNT"
        self.setWindowTitle(title)
        self.setFixedWidth(480)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 18, 24, 18)
        h_layout.addWidget(make_label(f"// {title}", size=12, color=CP_YELLOW, bold=True))
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet(f"background: {CP_BG};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self.name_input = QLineEdit(self.profile["name"])
        self.name_input.setPlaceholderText("e.g. Account 1, Main, Work Account")
        layout.addWidget(make_label("Account Name", size=10, color=CP_CYAN))
        layout.addWidget(self.name_input)

        if not is_edit:
            layout.addWidget(make_divider())
            layout.addWidget(make_label("Initial Action:", size=10, color=CP_YELLOW, bold=True))
            self.radio_capture = QRadioButton("Automatically capture current target app files right now")
            self.radio_empty = QRadioButton("Create empty profile without copying now")
            self.radio_capture.setChecked(True)
            layout.addWidget(self.radio_capture)
            layout.addWidget(self.radio_empty)

        layout.addWidget(make_divider())

        # Timer Box
        timer_box = QGroupBox("COUNTDOWN TIMER")
        tb_layout = QVBoxLayout(timer_box)
        tb_layout.setSpacing(10)

        self.timer_checkbox = QCheckBox("Enable Countdown Timer")
        self.timer_checkbox.setChecked(self.profile.get("timer_enabled", False))
        tb_layout.addWidget(self.timer_checkbox)

        self.timer_frame = QWidget()
        tf_layout = QVBoxLayout(self.timer_frame)
        tf_layout.setContentsMargins(0, 5, 0, 0)
        tf_layout.setSpacing(10)

        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(12)
        fmt_row.addWidget(make_label("Format:", size=9, color=CP_SUBTEXT))
        self.radio_12h = QRadioButton("12-Hour")
        self.radio_24h = QRadioButton("24-Hour")
        self.radio_24h.setChecked(True)
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_12h)
        self.radio_group.addButton(self.radio_24h)
        self.radio_group.buttonClicked.connect(self.update_time_format)
        fmt_row.addWidget(self.radio_12h)
        fmt_row.addWidget(self.radio_24h)
        fmt_row.addStretch()
        tf_layout.addLayout(fmt_row)

        tf_layout.addWidget(make_label("Target Date & Time", size=9, color=CP_SUBTEXT))
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_edit.setCalendarPopup(True)
        if self.profile.get("target_time"):
            self.dt_edit.setDateTime(QDateTime.fromString(self.profile["target_time"], Qt.DateFormat.ISODate))
        else:
            self.dt_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        tf_layout.addWidget(self.dt_edit)

        paste_row = QHBoxLayout()
        paste_row.setSpacing(8)
        self.paste_input = QLineEdit()
        self.paste_input.setPlaceholderText("Paste time string...")
        parse_btn = make_secondary_btn("Apply", min_width=70)
        parse_btn.setFixedHeight(32)
        parse_btn.clicked.connect(self.parse_pasted_time)
        paste_row.addWidget(self.paste_input)
        paste_row.addWidget(parse_btn)
        tf_layout.addLayout(paste_row)

        tb_layout.addWidget(self.timer_frame)
        layout.addWidget(timer_box)

        self.timer_checkbox.toggled.connect(self.toggle_timer_fields)
        self.toggle_timer_fields(self.timer_checkbox.isChecked())
        self.update_time_format()

        root.addWidget(body)

        footer = QFrame()
        footer.setStyleSheet(f"background: {CP_PANEL}; border-top: 1px solid {CP_DIM};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 14, 24, 14)
        f_layout.setSpacing(10)
        f_layout.addStretch()
        cancel_btn = make_secondary_btn("CANCEL", min_width=90)
        save_btn   = make_primary_btn("SAVE ACCOUNT", min_width=120)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save)
        f_layout.addWidget(cancel_btn)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    def toggle_timer_fields(self, checked):
        self.timer_frame.setVisible(checked)

    def update_time_format(self):
        fmt = "dd MMM yyyy h:mm ap" if self.radio_12h.isChecked() else "dd MMM yyyy HH:mm"
        self.dt_edit.setDisplayFormat(fmt)

    def parse_pasted_time(self):
        text = self.paste_input.text().strip()
        if not text:
            return
        formats = ["%m/%d/%Y, %I:%M:%S %p", "%m/%d/%Y, %I:%M %p", "%m/%d/%Y %I:%M:%S %p",
                   "%m/%d/%Y %I:%M %p", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
        for fmt in formats:
            try:
                parsed_dt = datetime.strptime(text, fmt)
                qdt = QDateTime(QDate(parsed_dt.year, parsed_dt.month, parsed_dt.day),
                                QTime(parsed_dt.hour, parsed_dt.minute, parsed_dt.second))
                self.dt_edit.setDateTime(qdt)
                self.paste_input.clear()
                return
            except ValueError:
                continue
        QMessageBox.warning(self, "Parse Error", f"Could not parse time string: '{text}'")

    def save(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Account Name is required.")
            return

        self.profile.update({
            "name":          self.name_input.text().strip(),
            "timer_enabled": self.timer_checkbox.isChecked(),
            "target_time":   self.dt_edit.dateTime().toString(Qt.DateFormat.ISODate)
                             if self.timer_checkbox.isChecked() else None
        })
        if hasattr(self, 'radio_capture'):
            self.capture_now = self.radio_capture.isChecked()
        self.accept()


# ── APP CARD ──────────────────────────────────────────────────────────────────
class AppCard(QFrame):
    clicked        = pyqtSignal(str)
    settings_click = pyqtSignal(str)
    delete_click   = pyqtSignal(str)

    def __init__(self, app_name, app_config, profile_count):
        super().__init__()
        self.app_name = app_name
        self.app_config = app_config
        self.profile_count = profile_count
        self.init_ui()

    def init_ui(self):
        self.setObjectName("appCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            #appCard {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
            }}
            #appCard:hover {{
                background-color: #1A1A1A;
                border-color: {CP_CYAN};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        icon_lbl = QLabel()
        icon_svg = SVG_LOCK if self.app_config.get("is_locked") else SVG_DIAMOND
        icon_lbl.setPixmap(render_svg_pixmap(icon_svg, color=CP_CYAN, size=18))
        icon_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        name_lbl = make_label(self.app_name, size=11, color=CP_YELLOW, bold=True)
        
        path_str = self.app_config.get("target_path", "")
        if len(path_str) > 50:
            path_str = "..." + path_str[-47:]
        path_lbl = QLabel(f"Target: {path_str}")
        path_lbl.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: '{FONT_MAIN}', monospace; font-size: 8pt; background: transparent;")

        count_lbl = make_label(
            f"{self.profile_count} account{'s' if self.profile_count != 1 else ''}",
            size=9, color=CP_CYAN
        )

        sub_row = QHBoxLayout()
        sub_row.setSpacing(12)
        sub_row.addWidget(count_lbl)
        sub_row.addWidget(path_lbl)
        sub_row.addStretch()

        text_col.addWidget(name_lbl)
        text_col.addLayout(sub_row)
        layout.addLayout(text_col, 1)

        edit_btn = make_card_svg_button(SVG_CONFIG, tooltip="Configure Application")
        delete_btn = make_card_svg_button(SVG_DELETE, tooltip="Delete Application")

        edit_btn.clicked.connect(lambda: self.settings_click.emit(self.app_name))
        delete_btn.clicked.connect(lambda: self.delete_click.emit(self.app_name))

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

        chevron_lbl = QLabel()
        chevron_lbl.setPixmap(render_svg_pixmap(SVG_CHEVRON, color=CP_SUBTEXT, size=16))
        chevron_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(chevron_lbl)

    def mousePressEvent(self, event):
        child = self.childAt(event.position().toPoint())
        if isinstance(child, QPushButton):
            return
        self.clicked.emit(self.app_name)


# ── PROFILE / ACCOUNT CARD ────────────────────────────────────────────────────
class ProfileCard(QFrame):
    clicked        = pyqtSignal(dict)
    update_click   = pyqtSignal(dict)
    edit_clicked   = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, profile, app_config):
        super().__init__()
        self.profile = profile
        self.app_config = app_config
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.init_ui()
        if self.profile.get("timer_enabled"):
            self.timer.start(1000)
            self.update_countdown()

    def init_ui(self):
        self.setObjectName("profileCard")
        self._apply_style()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        row = QHBoxLayout()
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(12)
        row.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_label = make_label(self.profile["name"], size=11, color=CP_TEXT, bold=True)
        name_row.addWidget(self.name_label)

        if self.app_config.get("is_locked"):
            lock_lbl = QLabel()
            lock_lbl.setPixmap(render_svg_pixmap(SVG_LOCK, color=CP_CYAN, size=14))
            lock_lbl.setStyleSheet("background: transparent;")
            name_row.addWidget(lock_lbl)

        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet(
            f"color: {CP_YELLOW}; background: transparent; font-family: '{FONT_MAIN}', monospace; font-size: 9pt;"
        )
        self.countdown_label.setVisible(False)
        name_row.addWidget(self.countdown_label)
        name_row.addStretch()

        store_path = self.profile.get("storage_path", "")
        if len(store_path) > 55:
            store_path = "..." + store_path[-52:]
        self.path_label = QLabel(f"Stored: {store_path}")
        self.path_label.setStyleSheet(
            f"color: {CP_SUBTEXT}; font-family: '{FONT_MAIN}', monospace; font-size: 8pt; background: transparent;"
        )

        info_col.addLayout(name_row)
        info_col.addWidget(self.path_label)
        row.addLayout(info_col, 1)

        # Update Session Button
        update_btn = make_secondary_btn("UPDATE", min_width=75)
        update_btn.setToolTip("Overwrite backup with current target directory state")
        update_btn.setFixedHeight(30)
        update_btn.clicked.connect(lambda: self.update_click.emit(self.profile))
        row.addWidget(update_btn)

        if self.profile.get("active", False):
            status = make_label("● ACTIVE", size=9, color=CP_GREEN, bold=True)
            status.setStyleSheet(
                f"color: {CP_GREEN}; font-size: 9pt; font-weight: bold; background: transparent; letter-spacing: 1px;"
            )
            row.addWidget(status)
        else:
            act_btn = make_primary_btn("ACTIVATE", min_width=85)
            act_btn.setFixedHeight(30)
            act_btn.clicked.connect(lambda: self.clicked.emit(self.profile))
            row.addWidget(act_btn)

        edit_btn   = make_card_svg_button(SVG_EDIT, tooltip="Edit Account")
        delete_btn = make_card_svg_button(SVG_DELETE, tooltip="Delete Account")
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.profile))
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.profile))
        row.addWidget(edit_btn)
        row.addWidget(delete_btn)

        outer.addLayout(row)

    def _apply_style(self, expired=False):
        is_active = self.profile.get("active", False)
        if is_active:
            border = CP_GREEN
        elif expired:
            border = CP_RED
        elif self.profile.get("timer_enabled"):
            border = CP_YELLOW
        else:
            border = CP_DIM

        self.setStyleSheet(f"""
            #profileCard {{
                background-color: {CP_PANEL};
                border: 1px solid {border};
            }}
            #profileCard:hover {{
                background-color: #1A1A1A;
            }}
        """)

    def update_countdown(self):
        target_str = self.profile.get("target_time")
        if not target_str:
            self.countdown_label.setVisible(False)
            return

        target_dt = QDateTime.fromString(target_str, Qt.DateFormat.ISODate)
        secs_left = QDateTime.currentDateTime().secsTo(target_dt)

        if secs_left > 0:
            d = secs_left // 86400
            h = (secs_left % 86400) // 3600
            m = (secs_left % 3600) // 60
            s = secs_left % 60
            parts = []
            if d: parts.append(f"{d}d")
            if h: parts.append(f"{h}h")
            if m or not parts: parts.append(f"{m}m")
            if not d: parts.append(f"{s:02d}s")
            self.countdown_label.setText(f"⏱ {' '.join(parts)}")
            self.countdown_label.setStyleSheet(
                f"color: {CP_YELLOW}; font-family: '{FONT_MAIN}', monospace; font-size: 9pt; background: transparent;"
            )
            self.countdown_label.setVisible(True)
        else:
            self.countdown_label.setText("⏰ Expired")
            self.countdown_label.setStyleSheet(
                f"color: {CP_RED}; font-family: '{FONT_MAIN}', monospace; font-size: 9pt; background: transparent;"
            )
            self.countdown_label.setVisible(True)
            self._apply_style(expired=True)
            self.timer.stop()


# ── MAIN APPLICATION CONTROLLER ───────────────────────────────────────────────
class AppProfileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.apps = {}
        self.profiles = []
        self.master_password = ""
        self.auto_capture = True
        self.current_app = None
        self.load_data()
        self.init_ui()
        QTimer.singleShot(100, self.ensure_master_password)

    def load_data(self):
        self.apps = {}
        self.profiles = []
        self.master_password = ""
        self.auto_capture = True
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.apps = data.get("apps", {})
                    self.profiles = data.get("profiles", [])
                    self.master_password = data.get("master_password", "")
                    self.auto_capture = data.get("auto_capture", True)
                elif isinstance(data, list):
                    for p in data:
                        app_name = p.get("app_name", "Default App")
                        if app_name not in self.apps:
                            self.apps[app_name] = {
                                "target_path": p.get("target_path", ""),
                                "sync_items": ["*"],
                                "is_locked": True
                            }
                        if p.get("password") and not self.master_password:
                            self.master_password = p.get("password")
                        self.profiles.append({
                            "app_name": app_name,
                            "name": p.get("name", "Account"),
                            "storage_path": p.get("path", ""),
                            "active": p.get("active", False),
                            "timer_enabled": p.get("timer_enabled", False),
                            "target_time": p.get("target_time", None)
                        })
                    self.save_data()
            except Exception as e:
                print(f"Error loading JSON data: {e}")

    def save_data(self):
        with open(JSON_FILE, 'w') as f:
            json.dump({
                "master_password": self.master_password,
                "auto_capture": self.auto_capture,
                "apps": self.apps,
                "profiles": self.profiles
            }, f, indent=4)

    def ensure_master_password(self):
        if not self.master_password:
            dialog = MasterPasswordDialog(self, current_password="")
            if dialog.exec():
                self.master_password = dialog.master_password
                self.save_data()
            else:
                QMessageBox.warning(self, "Password Required", "A Master Password is required for encryption functionality.")

    def open_settings(self):
        dialog = SettingsDialog(self, master_password=self.master_password, auto_capture=self.auto_capture)
        if dialog.exec():
            self.master_password = dialog.master_password
            self.auto_capture = dialog.auto_capture
            self.save_data()

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def init_ui(self):
        self.setWindowTitle("CYBERPUNK APP PROFILE MANAGER")
        self.setMinimumSize(820, 680)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Topbar
        topbar = QFrame()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet(f"QFrame {{ background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM}; }}")
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(16, 0, 16, 0)
        tb_layout.setSpacing(8)
        tb_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.back_btn = make_svg_button(SVG_BACK, tooltip="Back to Applications list")
        self.back_btn.clicked.connect(self.show_apps)
        self.back_btn.setVisible(False)
        tb_layout.addWidget(self.back_btn)

        self.header_label = make_label("APPLICATIONS", size=11, color=CP_YELLOW, bold=True)
        tb_layout.addWidget(self.header_label)
        tb_layout.addStretch()

        restart_btn = make_svg_button(SVG_RESTART, tooltip="Restart Application")
        restart_btn.clicked.connect(self.restart_app)
        tb_layout.addWidget(restart_btn)

        settings_btn = make_svg_button(SVG_SETTINGS, tooltip="Global Settings & Encryption")
        settings_btn.clicked.connect(self.open_settings)
        tb_layout.addWidget(settings_btn)

        self.app_settings_btn = make_svg_button(SVG_CONFIG, tooltip="Configure Current App")
        self.app_settings_btn.clicked.connect(self.edit_current_app)
        self.app_settings_btn.setVisible(False)
        tb_layout.addWidget(self.app_settings_btn)

        self.action_btn = make_primary_btn("+ ADD APP", min_width=110)
        self.action_btn.setFixedHeight(34)
        self.action_btn.clicked.connect(self.on_action_clicked)
        tb_layout.addWidget(self.action_btn)

        root.addWidget(topbar)

        # Content
        content = QWidget()
        content.setStyleSheet(f"background: {CP_BG};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollContent")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.scroll_widget)
        content_layout.addWidget(self.scroll)

        root.addWidget(content, 1)
        self.show_apps()

    def _clear_scroll(self):
        for i in reversed(range(self.scroll_layout.count())):
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

    def show_apps(self):
        self.current_app = None
        self.header_label.setText("APPLICATIONS")
        self.back_btn.setVisible(False)
        self.app_settings_btn.setVisible(False)
        self.action_btn.setText("+ ADD APP")
        self._clear_scroll()

        if not self.apps:
            empty = make_label("SYSTEM READY... No applications added. Click '+ ADD APP' to configure.",
                               size=10, color=CP_SUBTEXT)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setContentsMargins(0, 60, 0, 0)
            self.scroll_layout.addWidget(empty)
            return

        for app_name in sorted(self.apps.keys()):
            app_cfg = self.apps[app_name]
            p_count = sum(1 for p in self.profiles if p.get("app_name") == app_name)
            card = AppCard(app_name, app_cfg, p_count)
            card.clicked.connect(self.show_profiles)
            card.settings_click.connect(self.edit_app_by_name)
            card.delete_click.connect(self.delete_app)
            self.scroll_layout.addWidget(card)

    def show_profiles(self, app_name):
        self.current_app = app_name
        self.header_label.setText(f"ACCOUNTS // {app_name}")
        self.back_btn.setVisible(True)
        self.app_settings_btn.setVisible(True)
        self.action_btn.setText("+ ADD ACCOUNT")
        self._clear_scroll()

        filtered = [p for p in self.profiles if p.get("app_name") == app_name]
        app_cfg = self.apps.get(app_name, {})

        if not filtered:
            empty = make_label("NO ACCOUNTS STORED FOR THIS APPLICATION.", size=10, color=CP_SUBTEXT)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setContentsMargins(0, 60, 0, 0)
            self.scroll_layout.addWidget(empty)
            return

        for profile in filtered:
            card = ProfileCard(profile, app_cfg)
            card.clicked.connect(self.activate_profile)
            card.update_click.connect(self.update_account_session)
            card.edit_clicked.connect(self.edit_account)
            card.delete_clicked.connect(self.delete_account)
            self.scroll_layout.addWidget(card)

    def on_action_clicked(self):
        if self.current_app:
            self.add_account()
        else:
            self.add_app()

    def add_app(self):
        dialog = AppDialog(self)
        if dialog.exec():
            app_name = dialog.app_name
            self.apps[app_name] = dialog.app_config
            self.save_data()
            self.show_profiles(app_name)

    def edit_current_app(self):
        if self.current_app:
            self.edit_app_by_name(self.current_app)

    def edit_app_by_name(self, app_name):
        app_cfg = self.apps.get(app_name, {})
        dialog = AppDialog(self, app_name=app_name, app_config=app_cfg.copy())
        if dialog.exec():
            new_app_name = dialog.app_name
            new_cfg = dialog.app_config

            if new_app_name != app_name:
                self.apps[new_app_name] = new_cfg
                del self.apps[app_name]
                for p in self.profiles:
                    if p.get("app_name") == app_name:
                        p["app_name"] = new_app_name
                if self.current_app == app_name:
                    self.current_app = new_app_name
            else:
                self.apps[app_name] = new_cfg

            self.save_data()
            if self.current_app:
                self.show_profiles(self.current_app)
            else:
                self.show_apps()

    def delete_app(self, app_name):
        reply = QMessageBox.question(
            self, 'Delete Application',
            f"Delete application '{app_name}' and all associated accounts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.apps[app_name]
            self.profiles = [p for p in self.profiles if p.get("app_name") != app_name]
            self.save_data()
            if self.current_app == app_name:
                self.show_apps()
            else:
                self.show_apps()

    def add_account(self):
        if not self.current_app:
            return
        dialog = AccountDialog(self)
        if dialog.exec():
            profile = dialog.profile
            profile["app_name"] = self.current_app
            profile["active"] = False

            acc_dir = os.path.join(PROFILE_DATA_DIR, sanitize_filename(self.current_app), sanitize_filename(profile["name"]))
            profile["storage_path"] = acc_dir

            self.profiles.append(profile)
            self.save_data()

            if dialog.capture_now:
                try:
                    self.capture_account_files(profile)
                    QMessageBox.information(self, "Account Created", f"Account '{profile['name']}' created & captured!")
                except Exception as e:
                    QMessageBox.warning(self, "Capture Failed", f"Account created, but capture failed:\n{e}")

            self.show_profiles(self.current_app)

    def edit_account(self, profile):
        dialog = AccountDialog(self, profile=profile.copy())
        if dialog.exec():
            idx = self.profiles.index(profile)
            updated = dialog.profile
            self.profiles[idx] = updated
            self.save_data()
            self.show_profiles(self.current_app)

    def delete_account(self, profile):
        reply = QMessageBox.question(
            self, 'Delete Account',
            f"Delete account '{profile['name']}'? Backup files will be removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if profile.get("storage_path") and os.path.exists(profile["storage_path"]):
                try:
                    shutil.rmtree(profile["storage_path"])
                except Exception:
                    pass
            self.profiles.remove(profile)
            self.save_data()
            self.show_profiles(self.current_app)

    def update_account_session(self, profile):
        reply = QMessageBox.question(
            self, 'Update Session',
            f"Overwrite backup for '{profile['name']}' with current live session files?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.capture_account_files(profile)
                QMessageBox.information(self, "Success", f"Session updated for '{profile['name']}'.")
            except Exception as e:
                QMessageBox.critical(self, "Update Failed", str(e))

    def capture_account_files(self, profile):
        app_name = profile["app_name"]
        app_cfg = self.apps.get(app_name)
        if not app_cfg:
            raise Exception("App configuration not found.")

        target_dir = app_cfg.get("target_path", "")
        if not target_dir or not os.path.exists(target_dir):
            raise Exception(f"Target directory does not exist:\n{target_dir}")

        storage_dir = profile.get("storage_path")
        if not storage_dir:
            storage_dir = os.path.join(PROFILE_DATA_DIR, sanitize_filename(app_name), sanitize_filename(profile["name"]))
            profile["storage_path"] = storage_dir

        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)
        os.makedirs(storage_dir, exist_ok=True)

        is_locked = app_cfg.get("is_locked", True)
        if is_locked and not self.master_password:
            self.ensure_master_password()
            if not self.master_password:
                raise Exception("Master password required for encrypted capture.")

        sync_items = app_cfg.get("sync_items", ["*"])

        if not sync_items or "*" in sync_items:
            for item in os.listdir(target_dir):
                src_path = os.path.join(target_dir, item)
                self._copy_recursive(src_path, target_dir, storage_dir, is_locked, self.master_password)
        else:
            for rel_path in sync_items:
                src_path = os.path.normpath(os.path.join(target_dir, rel_path))
                if os.path.exists(src_path):
                    self._copy_recursive(src_path, target_dir, storage_dir, is_locked, self.master_password)

    def _copy_recursive(self, src_path, base_target, base_storage, is_locked, password):
        if os.path.isfile(src_path):
            rel = os.path.relpath(src_path, base_target)
            dest = os.path.join(base_storage, rel)
            if is_locked:
                dest += ".enc"
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(src_path, 'rb') as f:
                data = f.read()
            if is_locked:
                data = encrypt_file_data(data, password)
            with open(dest, 'wb') as f:
                f.write(data)
        elif os.path.isdir(src_path):
            for root, _, files in os.walk(src_path):
                for file in files:
                    full_src = os.path.join(root, file)
                    rel = os.path.relpath(full_src, base_target)
                    dest = os.path.join(base_storage, rel)
                    if is_locked:
                        dest += ".enc"
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with open(full_src, 'rb') as f:
                        data = f.read()
                    if is_locked:
                        data = encrypt_file_data(data, password)
                    with open(dest, 'wb') as f:
                        f.write(data)

    def activate_profile(self, profile):
        try:
            self.restore_account_files(profile)
            for p in self.profiles:
                if p.get("app_name") == profile["app_name"]:
                    p["active"] = (p == profile)
            self.save_data()
            self.show_profiles(profile["app_name"])
            QMessageBox.information(self, "Account Activated", f"Account '{profile['name']}' is now ACTIVE.")
        except Exception as e:
            QMessageBox.critical(self, "Activation Failed", str(e))

    def restore_account_files(self, profile):
        app_name = profile["app_name"]
        app_cfg = self.apps.get(app_name)
        if not app_cfg:
            raise Exception("App configuration not found.")

        target_dir = app_cfg.get("target_path", "")
        if not target_dir:
            raise Exception("Target directory is not configured.")
        os.makedirs(target_dir, exist_ok=True)

        storage_dir = profile.get("storage_path")
        if not storage_dir or not os.path.exists(storage_dir):
            raise Exception(f"Stored profile directory not found:\n{storage_dir}")

        is_locked = app_cfg.get("is_locked", True)
        if is_locked and not self.master_password:
            self.ensure_master_password()
            if not self.master_password:
                raise Exception("Master password required for decryption.")

        for root, _, files in os.walk(storage_dir):
            for file in files:
                full_src = os.path.join(root, file)
                rel = os.path.relpath(full_src, storage_dir)

                if rel.endswith(".enc"):
                    rel_dest = rel[:-4]
                    dest_path = os.path.normpath(os.path.join(target_dir, rel_dest))
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    with open(full_src, 'rb') as f:
                        enc_bytes = f.read()
                    data = decrypt_file_data(enc_bytes, self.master_password)
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                else:
                    dest_path = os.path.normpath(os.path.join(target_dir, rel))
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(full_src, dest_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(GLOBAL_STYLE)
    app.setFont(QFont(FONT_MAIN, 10))
    window = AppProfileManager()
    window.show()
    sys.exit(app.exec())
