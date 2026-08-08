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
    QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont, QColor

from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# ── CATPPUCCIN MOCHA PALETTE ─────────────────────────────────────────────────
BG_DEEP      = "#1E1E2E"  # base
BG_SURFACE   = "#181825"  # mantle
BG_RAISED    = "#313244"  # surface0
BORDER       = "#45475A"  # surface1
BORDER_FOCUS = "#89B4FA"  # blue

ACCENT       = "#89B4FA"  # blue
ACCENT_SOFT  = "#74C7EC"  # sapphire
ACCENT_GLOW  = "#B4BEFE"  # lavender
SUCCESS      = "#A6E3A1"  # green
WARNING      = "#F9E2AF"  # yellow
DANGER       = "#F38BA8"  # red

TEXT_PRIMARY   = "#CDD6F4"  # text
TEXT_SECONDARY = "#BAC2DE"  # subtext1
TEXT_MUTED     = "#585B70"  # surface2

FONT_MAIN = "Segoe UI"
FONT_MONO = "Cascadia Code"

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(DATA_DIR, "app_profiles.json")
PROFILE_DATA_DIR = os.path.join(DATA_DIR, "profile_data")

os.makedirs(PROFILE_DATA_DIR, exist_ok=True)

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

# ── SHARED STYLESHEET FRAGMENTS ───────────────────────────────────────────────
INPUT_STYLE = f"""
    QLineEdit, QDateTimeEdit, QListWidget {{
        background-color: {BG_DEEP};
        border: 1px solid {BORDER};
        border-radius: 0px;
        padding: 8px 12px;
        color: {TEXT_PRIMARY};
        font-family: '{FONT_MAIN}';
        font-size: 13px;
        selection-background-color: {ACCENT};
        selection-color: #ffffff;
    }}
    QLineEdit:focus, QDateTimeEdit:focus, QListWidget:focus {{
        border: 1px solid {BORDER_FOCUS};
        background-color: {BG_RAISED};
    }}
    QLineEdit:disabled {{
        color: {TEXT_MUTED};
        border-color: {BORDER};
    }}
    QListWidget::item {{
        padding: 6px 8px;
        color: {TEXT_PRIMARY};
    }}
    QListWidget::item:hover {{
        background-color: {BG_RAISED};
    }}
    QListWidget::indicator {{
        width: 16px;
        height: 16px;
        border: 1px solid {BORDER};
        background-color: {BG_DEEP};
    }}
    QListWidget::indicator:checked {{
        background-color: {ACCENT};
        border-color: {ACCENT};
    }}
    QDateTimeEdit::up-button, QDateTimeEdit::down-button {{
        background: {BG_RAISED}; border: none; width: 18px;
    }}
"""

CHECKBOX_STYLE = f"""
    QCheckBox, QRadioButton {{
        color: {TEXT_SECONDARY};
        font-family: '{FONT_MAIN}';
        font-size: 13px;
        spacing: 8px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 16px; height: 16px;
        border: 1px solid {BORDER};
        border-radius: 0px;
        background: {BG_DEEP};
    }}
    QRadioButton::indicator {{ border-radius: 0px; }}
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background: {ACCENT};
        border-color: {ACCENT};
        image: none;
    }}
    QCheckBox:hover, QRadioButton:hover {{ color: {TEXT_PRIMARY}; }}
"""


def make_label(text, size=13, color=TEXT_SECONDARY, bold=False):
    lbl = QLabel(text)
    weight = "bold" if bold else "normal"
    lbl.setStyleSheet(
        f"color: {color}; font-family: '{FONT_MAIN}'; font-size: {size}px; font-weight: {weight}; background: transparent;"
    )
    return lbl


def make_primary_btn(text, min_width=120):
    btn = QPushButton(text)
    btn.setMinimumWidth(min_width)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {ACCENT};
            color: #ffffff;
            border: none;
            border-radius: 0px;
            padding: 9px 20px;
            font-family: '{FONT_MAIN}';
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover  {{ background-color: {ACCENT_GLOW}; }}
        QPushButton:pressed {{ background-color: {ACCENT_SOFT}; }}
    """)
    return btn


def make_secondary_btn(text, min_width=100):
    btn = QPushButton(text)
    btn.setMinimumWidth(min_width)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {BG_RAISED};
            color: {TEXT_SECONDARY};
            border: 1px solid {BORDER};
            border-radius: 0px;
            padding: 9px 20px;
            font-family: '{FONT_MAIN}';
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover  {{ border-color: {ACCENT}; color: {ACCENT_GLOW}; background-color: {BG_RAISED}; }}
        QPushButton:pressed {{ background-color: {BG_DEEP}; }}
    """)
    return btn


def make_ghost_btn(text):
    btn = QPushButton(text)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedSize(32, 32)
    btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {TEXT_MUTED};
            border: none;
            border-radius: 0px;
            font-size: 15px;
        }}
        QPushButton:hover {{ background-color: {BG_RAISED}; color: {TEXT_PRIMARY}; }}
        QPushButton:pressed {{ color: {DANGER}; }}
    """)
    return btn


def make_divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
    return line


# ── MASTER PASSWORD DIALOG ──────────────────────────────────────────────────
class MasterPasswordDialog(QDialog):
    def __init__(self, parent=None, current_password=""):
        super().__init__(parent)
        self.current_password = current_password
        self.init_ui()

    def init_ui(self):
        title = "Change Master Password" if self.current_password else "Set Master Password"
        self.setWindowTitle(title)
        self.setFixedWidth(420)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_SURFACE}; color: {TEXT_PRIMARY}; }}
            {INPUT_STYLE}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background: {BG_RAISED}; border-bottom: 1px solid {BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)
        h_layout.addWidget(make_label(title, size=15, color=TEXT_PRIMARY, bold=True))
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet(f"background: {BG_SURFACE};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        info_text = "This master password will be used automatically to encrypt and lock stored session data across all applications."
        layout.addWidget(make_label(info_text, size=12, color=TEXT_SECONDARY))

        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("Enter master password...")
        layout.addWidget(make_label("Master Password", size=12))
        layout.addWidget(self.pwd_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setPlaceholderText("Confirm master password...")
        layout.addWidget(make_label("Confirm Password", size=12))
        layout.addWidget(self.confirm_input)

        root.addWidget(body)

        footer = QFrame()
        footer.setStyleSheet(f"background: {BG_RAISED}; border-top: 1px solid {BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 12, 20, 12)
        f_layout.setSpacing(10)
        f_layout.addStretch()

        if self.current_password:
            cancel_btn = make_secondary_btn("Cancel", min_width=80)
            cancel_btn.clicked.connect(self.reject)
            f_layout.addWidget(cancel_btn)

        save_btn = make_primary_btn("Save Password", min_width=110)
        save_btn.clicked.connect(self.save)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    def save(self):
        p1 = self.pwd_input.text()
        p2 = self.confirm_input.text()
        if not p1:
            QMessageBox.warning(self, "Validation Error", "Password cannot be empty.")
            return
        if p1 != p2:
            QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
            return
        self.master_password = p1
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
        title = f"App Settings ({self.app_name_orig})" if self.app_name_orig else "New Application"
        self.setWindowTitle(title)
        self.setFixedWidth(560)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_SURFACE}; color: {TEXT_PRIMARY}; }}
            {INPUT_STYLE}
            {CHECKBOX_STYLE}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet(f"background: {BG_RAISED}; border-bottom: 1px solid {BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 18, 24, 18)
        h_layout.addWidget(make_label(title, size=16, color=TEXT_PRIMARY, bold=True))
        root.addWidget(header)

        # Body
        body = QWidget()
        body.setStyleSheet(f"background: {BG_SURFACE};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # App Name
        self.app_input = QLineEdit(self.app_name_orig)
        self.app_input.setPlaceholderText("e.g. Discord, Stable Diffusion, Steam")
        layout.addWidget(make_label("Application Name", size=12))
        layout.addWidget(self.app_input)

        # Target Path
        tgt_row = QHBoxLayout()
        tgt_row.setSpacing(8)
        self.target_input = QLineEdit(self.app_config.get("target_path", ""))
        self.target_input.setPlaceholderText("Select main App target directory path...")
        self.target_input.editingFinished.connect(self.populate_target_items)

        tgt_browse = make_secondary_btn("Browse", min_width=80)
        tgt_browse.setFixedHeight(36)
        tgt_browse.clicked.connect(self.browse_target)
        tgt_row.addWidget(self.target_input)
        tgt_row.addWidget(tgt_browse)
        layout.addWidget(make_label("Target Application Directory Path", size=12))
        layout.addLayout(tgt_row)

        layout.addWidget(make_divider())

        # Auto-Scanned Files/Folders Checklist
        layout.addWidget(make_label("Check Files & Folders to Sync / Swap with Profile:", size=12))
        self.items_list = QListWidget()
        self.items_list.setFixedHeight(150)

        items_btn_row = QHBoxLayout()
        items_btn_row.setSpacing(8)
        
        select_all_btn = make_secondary_btn("Select All", min_width=85)
        deselect_all_btn = make_secondary_btn("Deselect All", min_width=85)
        rescan_btn = make_secondary_btn("🔄 Rescan Path", min_width=100)

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
        footer.setStyleSheet(f"background: {BG_RAISED}; border-top: 1px solid {BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 14, 24, 14)
        f_layout.setSpacing(10)
        f_layout.addStretch()
        cancel_btn = make_secondary_btn("Cancel", min_width=90)
        save_btn   = make_primary_btn("Save App Settings", min_width=140)
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
        title = "Edit Account" if is_edit else "New Account"
        self.setWindowTitle(title)
        self.setFixedWidth(480)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_SURFACE}; color: {TEXT_PRIMARY}; }}
            {INPUT_STYLE}
            {CHECKBOX_STYLE}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background: {BG_RAISED}; border-bottom: 1px solid {BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 18, 24, 18)
        h_layout.addWidget(make_label(title, size=16, color=TEXT_PRIMARY, bold=True))
        root.addWidget(header)

        body = QWidget()
        body.setStyleSheet(f"background: {BG_SURFACE};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        self.name_input = QLineEdit(self.profile["name"])
        self.name_input.setPlaceholderText("e.g. Account 1, Main, Work Account")
        layout.addWidget(make_label("Account Name", size=12))
        layout.addWidget(self.name_input)

        if not is_edit:
            layout.addWidget(make_divider())
            layout.addWidget(make_label("Initial Action:", size=12, bold=True))
            self.radio_capture = QRadioButton("Automatically capture current target app files right now")
            self.radio_empty = QRadioButton("Create empty profile without copying now")
            self.radio_capture.setChecked(True)
            layout.addWidget(self.radio_capture)
            layout.addWidget(self.radio_empty)

        layout.addWidget(make_divider())

        # Timer
        self.timer_checkbox = QCheckBox("Enable Countdown Timer")
        self.timer_checkbox.setChecked(self.profile.get("timer_enabled", False))
        layout.addWidget(self.timer_checkbox)

        self.timer_frame = QFrame()
        self.timer_frame.setStyleSheet(f"QFrame {{ background: {BG_RAISED}; border: 1px solid {BORDER}; }}")
        tf_layout = QVBoxLayout(self.timer_frame)
        tf_layout.setContentsMargins(14, 12, 14, 12)
        tf_layout.setSpacing(10)

        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(12)
        fmt_row.addWidget(make_label("Format:", size=12))
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

        tf_layout.addWidget(make_label("Target Date & Time", size=12))
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
        parse_btn.setFixedHeight(34)
        parse_btn.clicked.connect(self.parse_pasted_time)
        paste_row.addWidget(self.paste_input)
        paste_row.addWidget(parse_btn)
        tf_layout.addLayout(paste_row)

        layout.addWidget(self.timer_frame)

        self.timer_checkbox.toggled.connect(self.toggle_timer_fields)
        self.toggle_timer_fields(self.timer_checkbox.isChecked())
        self.update_time_format()

        root.addWidget(body)

        footer = QFrame()
        footer.setStyleSheet(f"background: {BG_RAISED}; border-top: 1px solid {BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 14, 24, 14)
        f_layout.setSpacing(10)
        f_layout.addStretch()
        cancel_btn = make_secondary_btn("Cancel", min_width=90)
        save_btn   = make_primary_btn("Save Account", min_width=120)
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
        self.setFixedHeight(85)
        self.setStyleSheet(f"""
            #appCard {{
                background-color: {BG_SURFACE};
                border: 1px solid {BORDER};
            }}
            #appCard:hover {{
                background-color: {BG_RAISED};
                border-color: {ACCENT};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 14, 0)
        layout.setSpacing(14)

        icon = QLabel("🔒" if self.app_config.get("is_locked") else "◈")
        icon.setStyleSheet(f"color: {ACCENT}; font-size: 20px; background: transparent;")
        layout.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        name_lbl = make_label(self.app_name, size=15, color=TEXT_PRIMARY, bold=True)
        
        path_str = self.app_config.get("target_path", "")
        if len(path_str) > 50:
            path_str = "..." + path_str[-47:]
        path_lbl = QLabel(f"Target: {path_str}")
        path_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-family: '{FONT_MONO}'; font-size: 11px; background: transparent;")

        count_lbl = make_label(
            f"{self.profile_count} account{'s' if self.profile_count != 1 else ''}",
            size=12, color=ACCENT_SOFT
        )

        sub_row = QHBoxLayout()
        sub_row.setSpacing(12)
        sub_row.addWidget(count_lbl)
        sub_row.addWidget(path_lbl)
        sub_row.addStretch()

        text_col.addWidget(name_lbl)
        text_col.addLayout(sub_row)
        layout.addLayout(text_col, 1)

        edit_btn = make_ghost_btn("⚙")
        delete_btn = make_ghost_btn("✕")
        edit_btn.setToolTip("App Settings")
        delete_btn.setToolTip("Delete App")

        edit_btn.clicked.connect(lambda: self.settings_click.emit(self.app_name))
        delete_btn.clicked.connect(lambda: self.delete_click.emit(self.app_name))

        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

        chevron = make_label("›", size=22, color=TEXT_MUTED)
        layout.addWidget(chevron)

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
        row.setContentsMargins(18, 14, 14, 14)
        row.setSpacing(12)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_label = make_label(self.profile["name"], size=14, color=TEXT_PRIMARY, bold=True)
        name_row.addWidget(self.name_label)

        if self.app_config.get("is_locked"):
            name_row.addWidget(make_label("🔒", size=12))

        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet(
            f"color: {WARNING}; background: transparent; font-family: '{FONT_MONO}'; font-size: 12px;"
        )
        self.countdown_label.setVisible(False)
        name_row.addWidget(self.countdown_label)
        name_row.addStretch()

        store_path = self.profile.get("storage_path", "")
        if len(store_path) > 55:
            store_path = "..." + store_path[-52:]
        self.path_label = QLabel(f"Stored: {store_path}")
        self.path_label.setStyleSheet(
            f"color: {TEXT_MUTED}; font-family: '{FONT_MONO}'; font-size: 11px; background: transparent;"
        )

        info_col.addLayout(name_row)
        info_col.addWidget(self.path_label)
        row.addLayout(info_col, 1)

        # Update Session Button
        update_btn = make_secondary_btn("🔄 Update", min_width=85)
        update_btn.setToolTip("Overwrite this account's backup with current target directory state")
        update_btn.setFixedHeight(32)
        update_btn.clicked.connect(lambda: self.update_click.emit(self.profile))
        row.addWidget(update_btn)

        if self.profile.get("active", False):
            status = make_label("● ACTIVE", size=11, color=SUCCESS, bold=True)
            status.setStyleSheet(
                f"color: {SUCCESS}; font-size: 11px; font-weight: bold; background: transparent; letter-spacing: 1px;"
            )
            row.addWidget(status)
        else:
            act_btn = make_primary_btn("Activate", min_width=85)
            act_btn.setFixedHeight(32)
            act_btn.clicked.connect(lambda: self.clicked.emit(self.profile))
            row.addWidget(act_btn)

        edit_btn   = make_ghost_btn("✎")
        delete_btn = make_ghost_btn("✕")
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.profile))
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.profile))
        row.addWidget(edit_btn)
        row.addWidget(delete_btn)

        outer.addLayout(row)

    def _apply_style(self, expired=False):
        is_active = self.profile.get("active", False)
        if is_active:
            border = SUCCESS
        elif expired:
            border = DANGER
        elif self.profile.get("timer_enabled"):
            border = WARNING
        else:
            border = BORDER

        self.setStyleSheet(f"""
            #profileCard {{
                background-color: {BG_SURFACE};
                border: 1px solid {border};
            }}
            #profileCard:hover {{
                background-color: {BG_RAISED};
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
                f"color: {WARNING}; font-family: '{FONT_MONO}'; font-size: 12px; background: transparent;"
            )
            self.countdown_label.setVisible(True)
        else:
            self.countdown_label.setText("⏰ Expired")
            self.countdown_label.setStyleSheet(
                f"color: {DANGER}; font-family: '{FONT_MONO}'; font-size: 12px; background: transparent;"
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
        self.current_app = None
        self.load_data()
        self.init_ui()
        QTimer.singleShot(100, self.ensure_master_password)

    def load_data(self):
        self.apps = {}
        self.profiles = []
        self.master_password = ""
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r') as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.apps = data.get("apps", {})
                    self.profiles = data.get("profiles", [])
                    self.master_password = data.get("master_password", "")
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

    def change_master_password(self):
        dialog = MasterPasswordDialog(self, current_password=self.master_password)
        if dialog.exec():
            self.master_password = dialog.master_password
            self.save_data()
            QMessageBox.information(self, "Password Updated", "Master Password updated successfully.")

    def init_ui(self):
        self.setWindowTitle("App Profile Manager")
        self.setMinimumSize(750, 680)

        self.setStyleSheet(f"""
            QMainWindow, QWidget#central {{ background-color: {BG_DEEP}; }}
            QScrollArea {{ border: none; background: transparent; }}
            QWidget#scrollContent {{ background: transparent; }}
            QScrollBar:vertical {{
                border: none; background: {BG_DEEP}; width: 6px; margin: 4px 0;
            }}
            QScrollBar::handle:vertical {{ background: {BORDER}; min-height: 30px; }}
            QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QMessageBox {{ background: {BG_SURFACE}; color: {TEXT_PRIMARY}; }}
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Topbar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"QFrame {{ background: {BG_SURFACE}; border-bottom: 1px solid {BORDER}; }}")
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 0, 16, 0)
        tb_layout.setSpacing(10)

        self.back_btn = make_secondary_btn("← Applications", min_width=110)
        self.back_btn.setFixedHeight(34)
        self.back_btn.clicked.connect(self.show_apps)
        self.back_btn.setVisible(False)
        tb_layout.addWidget(self.back_btn)

        self.header_label = make_label("Applications", size=16, color=TEXT_PRIMARY, bold=True)
        tb_layout.addWidget(self.header_label)
        tb_layout.addStretch()

        self.pwd_btn = make_secondary_btn("🔑 Master Password", min_width=130)
        self.pwd_btn.setFixedHeight(34)
        self.pwd_btn.clicked.connect(self.change_master_password)
        tb_layout.addWidget(self.pwd_btn)

        self.app_settings_btn = make_secondary_btn("⚙ App Settings", min_width=110)
        self.app_settings_btn.setFixedHeight(34)
        self.app_settings_btn.clicked.connect(self.edit_current_app)
        self.app_settings_btn.setVisible(False)
        tb_layout.addWidget(self.app_settings_btn)

        self.action_btn = make_primary_btn("+ Add App", min_width=110)
        self.action_btn.setFixedHeight(34)
        self.action_btn.clicked.connect(self.on_action_clicked)
        tb_layout.addWidget(self.action_btn)

        root.addWidget(topbar)

        # Content
        content = QWidget()
        content.setStyleSheet(f"background: {BG_DEEP};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)

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
        self.header_label.setText("Applications")
        self.back_btn.setVisible(False)
        self.app_settings_btn.setVisible(False)
        self.action_btn.setText("+ Add App")
        self._clear_scroll()

        if not self.apps:
            empty = make_label("No applications added yet. Click '+ Add App' to configure an app.",
                               size=13, color=TEXT_MUTED)
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
        self.header_label.setText(f"Accounts : {app_name}")
        self.back_btn.setVisible(True)
        self.app_settings_btn.setVisible(True)
        self.action_btn.setText("+ Add Account")
        self._clear_scroll()

        filtered = [p for p in self.profiles if p.get("app_name") == app_name]
        app_cfg = self.apps.get(app_name, {})

        if not filtered:
            empty = make_label("No accounts created for this application yet.", size=13, color=TEXT_MUTED)
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
            f"Delete application '{app_name}' and all its accounts?",
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
                    QMessageBox.information(self, "Account Added", f"Account '{profile['name']}' created and session captured successfully!")
                except Exception as e:
                    QMessageBox.warning(self, "Capture Warning", f"Account created, but capture failed:\n{e}")

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
            f"Delete account '{profile['name']}'? Local backup data will also be deleted.",
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
            f"Overwrite saved session for '{profile['name']}' with current files from target directory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.capture_account_files(profile)
                QMessageBox.information(self, "Success", f"Session files updated for '{profile['name']}'.")
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
                raise Exception("Master password is required for encrypted capture.")

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
            QMessageBox.information(self, "Account Activated", f"Account '{profile['name']}' activated successfully.")
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
                raise Exception("Master password is required for decryption.")

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
    app.setFont(QFont(FONT_MAIN, 10))
    window = AppProfileManager()
    window.show()
    sys.exit(app.exec())
