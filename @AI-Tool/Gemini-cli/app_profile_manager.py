import sys
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
    QMessageBox, QDialog, QCheckBox, QDateTimeEdit, QRadioButton, QButtonGroup, QComboBox,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont, QColor

from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# ── PROFESSIONAL SLATE / INDIGO PALETTE ──────────────────────────────────────
BG_DEEP     = "#0D0F14"   # near-black with blue cast
BG_SURFACE  = "#13161E"   # card / panel background
BG_RAISED   = "#1C2030"   # elevated elements
BORDER      = "#252A3A"   # subtle separator
BORDER_FOCUS= "#4F6EF7"   # indigo focus ring

ACCENT      = "#4F6EF7"   # indigo primary
ACCENT_SOFT = "#3B54C0"   # pressed / hover dark
ACCENT_GLOW = "#6B88FF"   # lighter highlight
SUCCESS     = "#34C98E"   # mint green
WARNING     = "#F5A623"   # amber
DANGER      = "#E05A5A"   # muted red

TEXT_PRIMARY  = "#E8EAF0"
TEXT_SECONDARY= "#8B91A8"
TEXT_MUTED    = "#555C73"

FONT_MAIN = "Segoe UI"
FONT_MONO = "Cascadia Code"

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_profiles.json")

# ─────────────────────────────────────────────────────────────────────────────

def derive_key(password, salt, key_length=32):
    return PBKDF2(password.encode(), salt, dkLen=key_length)

def decrypt_file_data(file_path, password):
    try:
        with open(file_path, 'rb') as f:
            salt, tag, nonce, ciphertext = [f.read(x) for x in (16, 16, 16, -1)]
        key = derive_key(password, salt)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
    except (ValueError, KeyError):
        raise Exception("Decryption failed. Incorrect password or corrupted file.")


# ── SHARED STYLESHEET FRAGMENTS ───────────────────────────────────────────────
INPUT_STYLE = f"""
    QLineEdit, QDateTimeEdit, QComboBox {{
        background-color: {BG_DEEP};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 8px 12px;
        color: {TEXT_PRIMARY};
        font-family: '{FONT_MAIN}';
        font-size: 13px;
        selection-background-color: {ACCENT};
        selection-color: #ffffff;
    }}
    QLineEdit:focus, QDateTimeEdit:focus, QComboBox:focus {{
        border: 1px solid {BORDER_FOCUS};
        background-color: {BG_RAISED};
    }}
    QLineEdit:disabled {{
        color: {TEXT_MUTED};
        border-color: {BORDER};
    }}
    QComboBox::drop-down {{ border: none; }}
    QComboBox::down-arrow {{ image: none; width: 0; }}
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
        border-radius: 4px;
        background: {BG_DEEP};
    }}
    QRadioButton::indicator {{ border-radius: 8px; }}
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
            border-radius: 7px;
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
            border-radius: 7px;
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
            border-radius: 6px;
            font-size: 15px;
        }}
        QPushButton:hover {{ background-color: {BG_RAISED}; color: {TEXT_PRIMARY}; }}
        QPushButton:pressed {{ color: {DANGER}; }}
    """)
    return btn


# ── SECTION DIVIDER ───────────────────────────────────────────────────────────
def make_divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"background: {BORDER}; border: none; max-height: 1px;")
    return line


# ─────────────────────────────────────────────────────────────────────────────
class ProfileDialog(QDialog):
    def __init__(self, parent=None, profile=None, app_name=None, saved_targets=None):
        super().__init__(parent)
        self.saved_targets = saved_targets or {}
        self.remember_target = False
        self.profile = profile or {
            "name": "", "path": "", "target_path": "", "app_name": app_name or "",
            "is_locked": False, "password": "", "timer_enabled": False, "target_time": None
        }
        if app_name and app_name in self.saved_targets and not self.profile.get("target_path"):
            self.profile["target_path"] = self.saved_targets[app_name]
        self.init_ui()

    def init_ui(self):
        title = "Edit Profile" if self.profile["name"] else "New Profile"
        self.setWindowTitle(title)
        self.setFixedWidth(520)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {BG_SURFACE};
                color: {TEXT_PRIMARY};
            }}
            {INPUT_STYLE}
            {CHECKBOX_STYLE}
            QScrollBar:vertical {{ border: none; background: {BG_DEEP}; width: 6px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 3px; min-height: 30px; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Dialog header
        header = QFrame()
        header.setStyleSheet(f"background: {BG_RAISED}; border-bottom: 1px solid {BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 18, 24, 18)
        h_label = make_label(title, size=16, color=TEXT_PRIMARY, bold=True)
        h_layout.addWidget(h_label)
        root.addWidget(header)

        # ── Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body = QWidget()
        body.setStyleSheet(f"background: {BG_SURFACE};")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        def field(label_text, widget):
            grp = QVBoxLayout()
            grp.setSpacing(5)
            grp.addWidget(make_label(label_text, size=12))
            grp.addWidget(widget)
            layout.addLayout(grp)

        self.app_input = QLineEdit(self.profile["app_name"])
        self.app_input.setPlaceholderText("e.g. Stable Diffusion")
        self.app_input.textChanged.connect(self.on_app_name_changed)
        field("Application Name", self.app_input)

        self.name_input = QLineEdit(self.profile["name"])
        self.name_input.setPlaceholderText("e.g. Portrait Mode")
        field("Profile Name", self.name_input)

        layout.addWidget(make_divider())

        def path_row(placeholder):
            row = QHBoxLayout()
            row.setSpacing(8)
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            browse = make_secondary_btn("Browse")
            browse.setMinimumWidth(80)
            browse.setFixedHeight(36)
            row.addWidget(inp)
            row.addWidget(browse)
            return row, inp, browse

        src_row, self.path_input, src_browse = path_row("Select source directory…")
        self.path_input.setText(self.profile["path"])
        src_browse.clicked.connect(lambda: self.browse("source"))
        grp = QVBoxLayout(); grp.setSpacing(5)
        grp.addWidget(make_label("Source Path", size=12))
        grp.addLayout(src_row)
        layout.addLayout(grp)

        tgt_row, self.target_input, tgt_browse = path_row("Select target directory…")
        self.target_input.setText(self.profile["target_path"])
        tgt_browse.clicked.connect(lambda: self.browse("target"))
        grp2 = QVBoxLayout(); grp2.setSpacing(5)
        grp2.addWidget(make_label("Target Path", size=12))
        grp2.addLayout(tgt_row)
        layout.addLayout(grp2)

        self.remember_target_checkbox = QCheckBox("Remember target path for this application")
        layout.addWidget(self.remember_target_checkbox)

        layout.addWidget(make_divider())

        # Encryption
        self.lock_checkbox = QCheckBox("Files are encrypted  (.enc)")
        self.lock_checkbox.setChecked(self.profile["is_locked"])
        layout.addWidget(self.lock_checkbox)

        self.password_label = make_label("Encryption Password", size=12)
        self.password_input = QLineEdit(self.profile["password"])
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter decryption password…")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        layout.addWidget(make_divider())

        # Timer
        self.timer_checkbox = QCheckBox("Enable Countdown Timer")
        self.timer_checkbox.setChecked(self.profile["timer_enabled"])
        layout.addWidget(self.timer_checkbox)

        self.timer_frame = QFrame()
        self.timer_frame.setStyleSheet(f"""
            QFrame {{ background: {BG_RAISED}; border: 1px solid {BORDER}; border-radius: 8px; }}
        """)
        tf_layout = QVBoxLayout(self.timer_frame)
        tf_layout.setContentsMargins(16, 14, 16, 14)
        tf_layout.setSpacing(10)

        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(16)
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
        self.dt_edit.setStyleSheet(f"""
            QDateTimeEdit {{
                background: {BG_DEEP}; border: 1px solid {BORDER}; border-radius: 6px;
                padding: 7px 10px; color: {TEXT_PRIMARY}; font-size: 13px;
            }}
            QDateTimeEdit:focus {{ border-color: {BORDER_FOCUS}; }}
        """)
        if self.profile["target_time"]:
            self.dt_edit.setDateTime(QDateTime.fromString(self.profile["target_time"], Qt.DateFormat.ISODate))
        else:
            self.dt_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        tf_layout.addWidget(self.dt_edit)

        paste_row = QHBoxLayout()
        paste_row.setSpacing(8)
        self.paste_input = QLineEdit()
        self.paste_input.setPlaceholderText("e.g. 1/20/2026, 1:49:25 AM")
        parse_btn = make_secondary_btn("Apply")
        parse_btn.setFixedHeight(36)
        parse_btn.setMinimumWidth(70)
        parse_btn.clicked.connect(self.parse_pasted_time)
        paste_row.addWidget(self.paste_input)
        paste_row.addWidget(parse_btn)
        tf_layout.addLayout(paste_row)

        layout.addWidget(self.timer_frame)

        self.lock_checkbox.toggled.connect(self.toggle_password_fields)
        self.timer_checkbox.toggled.connect(self.toggle_timer_fields)
        self.toggle_password_fields(self.lock_checkbox.isChecked())
        self.toggle_timer_fields(self.timer_checkbox.isChecked())
        self.update_time_format()

        scroll.setWidget(body)
        root.addWidget(scroll)

        # ── Footer buttons
        footer = QFrame()
        footer.setStyleSheet(f"background: {BG_RAISED}; border-top: 1px solid {BORDER};")
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 14, 24, 14)
        f_layout.setSpacing(10)
        f_layout.addStretch()
        cancel_btn = make_secondary_btn("Cancel", min_width=90)
        save_btn   = make_primary_btn("Save Profile", min_width=120)
        cancel_btn.clicked.connect(self.reject)
        save_btn.clicked.connect(self.save)
        f_layout.addWidget(cancel_btn)
        f_layout.addWidget(save_btn)
        root.addWidget(footer)

    def toggle_password_fields(self, checked):
        self.password_label.setVisible(checked)
        self.password_input.setVisible(checked)

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
        QMessageBox.warning(self, "Parse Error", f"Could not parse: '{text}'")

    def browse(self, mode):
        path = QFileDialog.getExistingDirectory(self, f"Select {mode.title()} Directory")
        if path:
            (self.path_input if mode == "source" else self.target_input).setText(path)

    def on_app_name_changed(self):
        app_name = self.app_input.text().strip()
        if app_name in self.saved_targets:
            self.target_input.setText(self.saved_targets[app_name])

    def save(self):
        if not all([self.app_input.text(), self.name_input.text(),
                    self.path_input.text(), self.target_input.text()]):
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return
        if self.lock_checkbox.isChecked() and not self.password_input.text():
            QMessageBox.warning(self, "Validation Error", "A password is required for encrypted files.")
            return

        self.profile.update({
            "app_name":      self.app_input.text(),
            "name":          self.name_input.text(),
            "path":          self.path_input.text(),
            "target_path":   self.target_input.text(),
            "is_locked":     self.lock_checkbox.isChecked(),
            "password":      self.password_input.text() if self.lock_checkbox.isChecked() else "",
            "timer_enabled": self.timer_checkbox.isChecked(),
            "target_time":   self.dt_edit.dateTime().toString(Qt.DateFormat.ISODate)
                             if self.timer_checkbox.isChecked() else None
        })
        self.remember_target = self.remember_target_checkbox.isChecked()
        self.accept()

    def get_data(self):
        return self.profile


# ── APP CARD ──────────────────────────────────────────────────────────────────
class AppCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, app_name, profile_count):
        super().__init__()
        self.app_name = app_name
        self.profile_count = profile_count
        self.init_ui()

    def init_ui(self):
        self.setObjectName("appCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(80)
        self.setStyleSheet(f"""
            #appCard {{
                background-color: {BG_SURFACE};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
            #appCard:hover {{
                background-color: {BG_RAISED};
                border-color: {ACCENT};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(14)

        # Icon blob
        icon = QLabel("◈")
        icon.setStyleSheet(f"""
            color: {ACCENT};
            font-size: 22px;
            background: transparent;
        """)
        layout.addWidget(icon)

        # Text block
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        name_lbl = make_label(self.app_name, size=14, color=TEXT_PRIMARY, bold=True)
        count_lbl = make_label(
            f"{self.profile_count} profile{'s' if self.profile_count != 1 else ''}",
            size=12, color=TEXT_MUTED
        )
        text_col.addWidget(name_lbl)
        text_col.addWidget(count_lbl)
        layout.addLayout(text_col)
        layout.addStretch()

        chevron = make_label("›", size=20, color=TEXT_MUTED)
        layout.addWidget(chevron)

    def mousePressEvent(self, event):
        self.clicked.emit(self.app_name)


# ── PROFILE CARD ──────────────────────────────────────────────────────────────
class ProfileCard(QFrame):
    clicked        = pyqtSignal(dict)
    edit_clicked   = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, profile):
        super().__init__()
        self.profile = profile
        self.timer   = QTimer(self)
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
        outer.setSpacing(0)

        # ── Main row
        row = QHBoxLayout()
        row.setContentsMargins(18, 14, 14, 14)
        row.setSpacing(12)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)
        self.name_label = make_label(self.profile["name"], size=14, color=TEXT_PRIMARY, bold=True)
        name_row.addWidget(self.name_label)

        if self.profile.get("is_locked"):
            lock_badge = make_label("🔒", size=12)
            name_row.addWidget(lock_badge)

        self.countdown_label = make_label("", size=12, color=WARNING)
        self.countdown_label.setStyleSheet(f"""
            color: {WARNING};
            background: transparent;
            font-family: '{FONT_MONO}';
            font-size: 12px;
        """)
        self.countdown_label.setVisible(False)
        name_row.addWidget(self.countdown_label)
        name_row.addStretch()

        self.path_label = make_label(self.profile["path"], size=11, color=TEXT_MUTED)
        self.path_label.setStyleSheet(f"""
            color: {TEXT_MUTED};
            font-family: '{FONT_MONO}';
            font-size: 11px;
            background: transparent;
        """)

        info_col.addLayout(name_row)
        info_col.addWidget(self.path_label)
        row.addLayout(info_col, 1)

        # Action area
        if self.profile.get("active", False):
            status = make_label("● ACTIVE", size=11, color=SUCCESS, bold=True)
            status.setStyleSheet(f"color: {SUCCESS}; font-size: 11px; font-weight: bold; background: transparent; letter-spacing: 1px;")
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
                border-radius: 10px;
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

        target_dt  = QDateTime.fromString(target_str, Qt.DateFormat.ISODate)
        secs_left  = QDateTime.currentDateTime().secsTo(target_dt)

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
            self.countdown_label.setStyleSheet(f"color: {WARNING}; font-family: '{FONT_MONO}'; font-size: 12px; background: transparent;")
            self.countdown_label.setVisible(True)
        else:
            self.countdown_label.setText("⏰ Expired")
            self.countdown_label.setStyleSheet(f"color: {DANGER}; font-family: '{FONT_MONO}'; font-size: 12px; background: transparent;")
            self.countdown_label.setVisible(True)
            self._apply_style(expired=True)
            self.timer.stop()


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────
class AppProfileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profiles      = []
        self.saved_targets = {}
        self.current_app   = None
        self.load_profiles()
        self.load_saved_targets()
        self.init_ui()

    def load_profiles(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r') as f:
                    self.profiles = json.load(f)
            except:
                self.profiles = []

    def save_profiles(self):
        with open(JSON_FILE, 'w') as f:
            json.dump(self.profiles, f, indent=4)

    def load_saved_targets(self):
        targets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_targets.json")
        if os.path.exists(targets_file):
            try:
                with open(targets_file, 'r') as f:
                    self.saved_targets = json.load(f)
            except:
                self.saved_targets = {}

    def save_saved_targets(self):
        targets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_targets.json")
        with open(targets_file, 'w') as f:
            json.dump(self.saved_targets, f, indent=4)

    def init_ui(self):
        self.setWindowTitle("Profile Manager")
        self.setMinimumSize(720, 680)

        # ── Global stylesheet
        self.setStyleSheet(f"""
            QMainWindow, QWidget#central {{
                background-color: {BG_DEEP};
            }}
            QScrollArea {{ border: none; background: transparent; }}
            QWidget#scrollContent {{ background: transparent; }}
            QScrollBar:vertical {{
                border: none; background: {BG_DEEP}; width: 6px; margin: 4px 0;
            }}
            QScrollBar::handle:vertical {{
                background: {BORDER}; border-radius: 3px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QMessageBox {{
                background: {BG_SURFACE};
                color: {TEXT_PRIMARY};
            }}
        """)

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"""
            QFrame {{
                background: {BG_SURFACE};
                border-bottom: 1px solid {BORDER};
            }}
        """)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(24, 0, 16, 0)
        tb_layout.setSpacing(12)

        self.back_btn = make_secondary_btn("← Back", min_width=80)
        self.back_btn.setFixedHeight(34)
        self.back_btn.clicked.connect(self.show_apps)
        self.back_btn.setVisible(False)
        tb_layout.addWidget(self.back_btn)

        self.header_label = make_label("Applications", size=16, color=TEXT_PRIMARY, bold=True)
        tb_layout.addWidget(self.header_label)
        tb_layout.addStretch()

        restart_btn = make_secondary_btn("⟳ Restart", min_width=90)
        restart_btn.setFixedHeight(34)
        restart_btn.clicked.connect(self.restart_app)

        self.add_btn = make_primary_btn("+ Add App", min_width=100)
        self.add_btn.setFixedHeight(34)
        self.add_btn.clicked.connect(self.add_profile)

        tb_layout.addWidget(restart_btn)
        tb_layout.addWidget(self.add_btn)
        root.addWidget(topbar)

        # ── Content area
        content = QWidget()
        content.setStyleSheet(f"background: {BG_DEEP};")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(0)

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
        self.add_btn.setText("+ Add App")
        self._clear_scroll()

        app_counts = {}
        for p in self.profiles:
            n = p.get("app_name", "Unknown")
            app_counts[n] = app_counts.get(n, 0) + 1

        if not app_counts:
            empty = make_label("No applications yet. Click  + Add App  to get started.",
                               size=13, color=TEXT_MUTED)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setContentsMargins(0, 60, 0, 0)
            self.scroll_layout.addWidget(empty)
            return

        for app_name in sorted(app_counts.keys()):
            card = AppCard(app_name, app_counts[app_name])
            card.clicked.connect(self.show_profiles)
            self.scroll_layout.addWidget(card)

    def show_profiles(self, app_name):
        self.current_app = app_name
        self.header_label.setText(app_name)
        self.back_btn.setVisible(True)
        self.add_btn.setText("+ Add Profile")
        self._clear_scroll()

        filtered = [p for p in self.profiles if p.get("app_name") == app_name]

        if not filtered:
            empty = make_label("No profiles for this application.", size=13, color=TEXT_MUTED)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setContentsMargins(0, 60, 0, 0)
            self.scroll_layout.addWidget(empty)
            return

        for profile in filtered:
            card = ProfileCard(profile)
            card.clicked.connect(self.activate_profile)
            card.edit_clicked.connect(self.edit_profile)
            card.delete_clicked.connect(self.delete_profile)
            self.scroll_layout.addWidget(card)

    def refresh_list(self):
        if self.current_app:
            self.show_profiles(self.current_app)
        else:
            self.show_apps()

    def add_profile(self):
        dialog = ProfileDialog(self, app_name=self.current_app, saved_targets=self.saved_targets)
        if dialog.exec():
            new_profile = dialog.get_data()
            new_profile["active"] = False
            self.profiles.append(new_profile)
            self.save_profiles()
            if dialog.remember_target:
                self.saved_targets[new_profile["app_name"]] = new_profile["target_path"]
                self.save_saved_targets()
            self.refresh_list()

    def edit_profile(self, profile):
        dialog = ProfileDialog(self, profile.copy(), saved_targets=self.saved_targets)
        if dialog.exec():
            updated = dialog.get_data()
            self.profiles[self.profiles.index(profile)] = updated
            self.save_profiles()
            if dialog.remember_target:
                self.saved_targets[updated["app_name"]] = updated["target_path"]
                self.save_saved_targets()
            self.refresh_list()

    def delete_profile(self, profile):
        reply = QMessageBox.question(
            self, 'Delete Profile',
            f"Delete  \"{profile['name']}\"?  This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.profiles.remove(profile)
            self.save_profiles()
            self.refresh_list()

    def restart_app(self):
        QApplication.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def activate_profile(self, profile):
        try:
            self.execute_activation(profile)
            for p in self.profiles:
                p["active"] = (p["app_name"] == profile["app_name"] and p == profile)
            self.save_profiles()
            self.refresh_list()
            QMessageBox.information(self, "Activated",
                                    f"Profile  \"{profile['name']}\"  is now active.")
        except Exception as e:
            QMessageBox.critical(self, "Activation Failed", str(e))

    def execute_activation(self, profile):
        source_path = profile["path"]
        target_dir  = profile["target_path"]
        is_locked   = profile.get("is_locked", False)
        password    = profile.get("password", "")

        if not os.path.exists(source_path):
            raise Exception(f"Source path does not exist:\n{source_path}")

        os.makedirs(target_dir, exist_ok=True)

        for item in os.listdir(source_path):
            s      = os.path.join(source_path, item)
            d_name = item[:-4] if is_locked and item.endswith(".enc") else item
            d      = os.path.join(target_dir, d_name)

            if os.path.isfile(s):
                if is_locked and item.endswith(".enc"):
                    with open(d, 'wb') as f:
                        f.write(decrypt_file_data(s, password))
                else:
                    shutil.copy2(s, d)
            elif os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont(FONT_MAIN, 10))
    window = AppProfileManager()
    window.show()
    sys.exit(app.exec())
