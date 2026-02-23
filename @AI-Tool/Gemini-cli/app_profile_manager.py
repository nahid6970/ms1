import sys
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QScrollArea, QFrame, QLineEdit, QFileDialog,
    QMessageBox, QDialog, QCheckBox, QDateTimeEdit, QRadioButton, QButtonGroup, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QDateTime, QDate, QTime
from PyQt6.QtGui import QFont

from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import PBKDF2

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_profiles.json")

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

class ProfileDialog(QDialog):
    def __init__(self, parent=None, profile=None, app_name=None):
        super().__init__(parent)
        self.profile = profile or {
            "name": "", "path": "", "target_path": "", "app_name": app_name or "",
            "is_locked": False, "password": "", "timer_enabled": False, "target_time": None
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Edit Profile" if self.profile["name"] else "Add Profile")
        self.setFixedWidth(500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; color: {CP_TEXT}; }}
            QLabel {{ color: {CP_SUBTEXT}; font-size: 14px; margin-top: 10px; }}
            QLineEdit, QDateTimeEdit, QComboBox {{ 
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; 
                border-radius: 5px; padding: 8px; color: {CP_CYAN}; font-size: 14px; 
            }}
            QLineEdit:focus, QDateTimeEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QCheckBox, QRadioButton {{ color: {CP_TEXT}; font-size: 14px; margin-top: 5px; }}
            QPushButton {{ padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px; }}
            #saveBtn {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
            #saveBtn:hover {{ background-color: {CP_YELLOW}; color: {CP_BG}; }}
            #cancelBtn {{ background-color: {CP_DIM}; color: {CP_TEXT}; }}
            #browseBtn {{ background-color: {CP_DIM}; color: {CP_TEXT}; padding: 8px; }}
            #browseBtn:hover {{ border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(25, 25, 25, 25)

        layout.addWidget(QLabel("Application Name"))
        self.app_input = QLineEdit(self.profile["app_name"])
        layout.addWidget(self.app_input)

        layout.addWidget(QLabel("Profile Name"))
        self.name_input = QLineEdit(self.profile["name"])
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Source Path"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.profile["path"])
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("browseBtn")
        browse_btn.clicked.connect(lambda: self.browse("source"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        layout.addWidget(QLabel("Target Path"))
        target_layout = QHBoxLayout()
        self.target_input = QLineEdit(self.profile["target_path"])
        target_btn = QPushButton("Browse")
        target_btn.setObjectName("browseBtn")
        target_btn.clicked.connect(lambda: self.browse("target"))
        target_layout.addWidget(self.target_input)
        target_layout.addWidget(target_btn)
        layout.addLayout(target_layout)

        self.lock_checkbox = QCheckBox("Files are encrypted (.enc)")
        self.lock_checkbox.setChecked(self.profile["is_locked"])
        layout.addWidget(self.lock_checkbox)

        self.password_label = QLabel("Encryption Password")
        self.password_input = QLineEdit(self.profile["password"])
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.timer_checkbox = QCheckBox("Enable Countdown Timer")
        self.timer_checkbox.setChecked(self.profile["timer_enabled"])
        layout.addWidget(self.timer_checkbox)

        self.timer_frame = QFrame()
        timer_layout = QVBoxLayout(self.timer_frame)
        timer_layout.setContentsMargins(0, 0, 0, 0)

        format_layout = QHBoxLayout()
        self.radio_12h = QRadioButton("12-Hour")
        self.radio_24h = QRadioButton("24-Hour")
        self.radio_24h.setChecked(True)
        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_12h)
        self.radio_group.addButton(self.radio_24h)
        self.radio_group.buttonClicked.connect(self.update_time_format)
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.radio_12h)
        format_layout.addWidget(self.radio_24h)
        format_layout.addStretch()
        timer_layout.addLayout(format_layout)

        timer_layout.addWidget(QLabel("Set Target Date & Time"))
        self.dt_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dt_edit.setCalendarPopup(True)
        if self.profile["target_time"]:
            self.dt_edit.setDateTime(QDateTime.fromString(self.profile["target_time"], Qt.DateFormat.ISODate))
        else:
            self.dt_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        timer_layout.addWidget(self.dt_edit)

        paste_layout = QHBoxLayout()
        paste_layout.addWidget(QLabel("Or paste:"))
        self.paste_input = QLineEdit()
        self.paste_input.setPlaceholderText("e.g., 1/20/2026, 1:49:25 AM")
        paste_layout.addWidget(self.paste_input)
        parse_btn = QPushButton("Apply")
        parse_btn.setObjectName("browseBtn")
        parse_btn.clicked.connect(self.parse_pasted_time)
        paste_layout.addWidget(parse_btn)
        timer_layout.addLayout(paste_layout)

        layout.addWidget(self.timer_frame)

        self.lock_checkbox.toggled.connect(self.toggle_password_fields)
        self.timer_checkbox.toggled.connect(self.toggle_timer_fields)
        self.toggle_password_fields(self.lock_checkbox.isChecked())
        self.toggle_timer_fields(self.timer_checkbox.isChecked())
        self.update_time_format()

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 20, 0, 0)
        save_btn = QPushButton("Save Profile")
        save_btn.setObjectName("saveBtn")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def toggle_password_fields(self, checked):
        self.password_label.setVisible(checked)
        self.password_input.setVisible(checked)
        self.adjustSize()

    def toggle_timer_fields(self, checked):
        self.timer_frame.setVisible(checked)
        self.adjustSize()

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

    def save(self):
        if not all([self.app_input.text(), self.name_input.text(), self.path_input.text(), self.target_input.text()]):
            QMessageBox.warning(self, "Error", "All fields are required!")
            return
        if self.lock_checkbox.isChecked() and not self.password_input.text():
            QMessageBox.warning(self, "Error", "Password required for encrypted files!")
            return

        self.profile.update({
            "app_name": self.app_input.text(),
            "name": self.name_input.text(),
            "path": self.path_input.text(),
            "target_path": self.target_input.text(),
            "is_locked": self.lock_checkbox.isChecked(),
            "password": self.password_input.text() if self.lock_checkbox.isChecked() else "",
            "timer_enabled": self.timer_checkbox.isChecked(),
            "target_time": self.dt_edit.dateTime().toString(Qt.DateFormat.ISODate) if self.timer_checkbox.isChecked() else None
        })
        self.accept()

    def get_data(self):
        return self.profile

class ProfileCard(QFrame):
    clicked = pyqtSignal(dict)
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(dict)

    def __init__(self, profile):
        super().__init__()
        self.profile = profile
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.init_ui()
        if self.profile.get("timer_enabled"):
            self.timer.start(1000)
            self.update_countdown()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("profileCard")
        self.update_style()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        info_layout = QVBoxLayout()
        name_row = QHBoxLayout()
        self.name_label = QLabel(self.profile["name"])
        self.name_label.setObjectName("nameLabel")
        name_row.addWidget(self.name_label)

        if self.profile.get("is_locked"):
            name_row.addWidget(QLabel("🔒"))

        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setVisible(False)
        name_row.addWidget(self.countdown_label)
        name_row.addStretch()

        self.path_label = QLabel(self.profile["path"])
        self.path_label.setObjectName("pathLabel")

        info_layout.addLayout(name_row)
        info_layout.addWidget(self.path_label)
        layout.addLayout(info_layout, 1)

        if self.profile.get("active", False):
            status_label = QLabel("ACTIVE")
            status_label.setObjectName("statusLabel")
            layout.addWidget(status_label)
        else:
            activate_btn = QPushButton("Activate")
            activate_btn.setObjectName("activateBtn")
            activate_btn.clicked.connect(lambda: self.clicked.emit(self.profile))
            layout.addWidget(activate_btn)

        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("actionBtn")
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.profile))
        delete_btn = QPushButton("✕")
        delete_btn.setObjectName("actionBtn")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.profile))
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)

    def update_countdown(self):
        target_str = self.profile.get("target_time")
        if not target_str:
            self.countdown_label.setVisible(False)
            return

        target_dt = QDateTime.fromString(target_str, Qt.DateFormat.ISODate)
        secs_left = QDateTime.currentDateTime().secsTo(target_dt)

        if secs_left > 0:
            days, hours, minutes = secs_left // 86400, (secs_left % 86400) // 3600, (secs_left % 3600) // 60
            time_str = f"{days}d " if days > 0 else ""
            time_str += f"{hours}h " if hours > 0 else ""
            time_str += f"{minutes}m" if time_str or minutes > 0 else "< 1m"
            self.countdown_label.setText(f"⏳ {time_str.strip()}")
            self.countdown_label.setVisible(True)
            self.update_style(active_timer=True)
        else:
            self.countdown_label.setText("⏰ Expired")
            self.countdown_label.setVisible(True)
            self.update_style(active_timer=False)
            self.timer.stop()

    def update_style(self, active_timer=False):
        is_active = self.profile.get("active", False)
        if is_active:
            style = f"#profileCard {{ background-color: {CP_PANEL}; border: 2px solid {CP_CYAN}; border-radius: 8px; }}"
        elif active_timer:
            style = f"#profileCard {{ background-color: {CP_PANEL}; border: 1px solid {CP_RED}; border-radius: 8px; }} #profileCard:hover {{ border: 1px solid {CP_YELLOW}; }}"
        else:
            style = f"#profileCard {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; border-radius: 8px; }} #profileCard:hover {{ border: 1px solid {CP_YELLOW}; }}"

        self.setStyleSheet(style + f"""
            QLabel#nameLabel {{ color: {CP_YELLOW}; font-size: 16px; font-weight: bold; }}
            QLabel#pathLabel {{ color: {CP_SUBTEXT}; font-size: 12px; }}
            QLabel#countdownLabel {{ color: {CP_RED}; font-weight: bold; font-size: 13px; margin-left: 10px; 
                background-color: {CP_BG}; padding: 2px 6px; border-radius: 4px; }}
            QPushButton#actionBtn {{ background-color: transparent; color: {CP_SUBTEXT}; border: none; font-size: 14px; }}
            QPushButton#actionBtn:hover {{ color: {CP_YELLOW}; }}
            QPushButton#activateBtn {{ background-color: {CP_CYAN}; color: {CP_BG}; border-radius: 6px; 
                padding: 8px 15px; font-weight: bold; }}
            QPushButton#activateBtn:hover {{ background-color: {CP_YELLOW}; }}
            #statusLabel {{ color: {CP_GREEN}; font-weight: bold; font-size: 12px; }}
        """)

class AppProfileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.load_profiles()
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

    def init_ui(self):
        self.setWindowTitle("Application Profile Manager")
        self.setMinimumSize(700, 750)
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QScrollArea {{ border: none; background-color: transparent; }}
            #scrollWidget {{ background-color: transparent; }}
            QScrollBar:vertical {{ border: none; background: {CP_BG}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {CP_DIM}; min-height: 20px; border-radius: 5px; }}
            #headerLabel {{ color: {CP_YELLOW}; font-size: 24px; font-weight: bold; padding: 20px; }}
            #addBtn {{ background-color: {CP_CYAN}; color: {CP_BG}; border-radius: 8px; 
                padding: 10px 20px; font-weight: bold; margin: 20px; }}
            #addBtn:hover {{ background-color: {CP_YELLOW}; }}
            #restartBtn {{ background-color: {CP_DIM}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; 
                border-radius: 8px; padding: 10px 20px; font-weight: bold; margin: 20px; }}
            #restartBtn:hover {{ border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QComboBox {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; border-radius: 5px; 
                padding: 8px; color: {CP_CYAN}; font-size: 14px; min-width: 150px; }}
            QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        header_layout = QHBoxLayout()
        header_label = QLabel("Profiles")
        header_label.setObjectName("headerLabel")

        self.app_filter = QComboBox()
        self.app_filter.currentTextChanged.connect(self.refresh_list)

        add_btn = QPushButton("+ Add Profile")
        add_btn.setObjectName("addBtn")
        add_btn.clicked.connect(self.add_profile)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        restart_btn = QPushButton("⟳ Restart")
        restart_btn.setObjectName("restartBtn")
        restart_btn.clicked.connect(self.restart_app)
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        header_layout.addWidget(header_label)
        header_layout.addWidget(QLabel("Filter:"))
        header_layout.addWidget(self.app_filter)
        header_layout.addStretch()
        header_layout.addWidget(restart_btn)
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("scrollWidget")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_layout.setSpacing(15)
        self.scroll.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll)

        self.refresh_list()

    def refresh_list(self):
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        apps = sorted(set(p["app_name"] for p in self.profiles if p.get("app_name")))
        self.app_filter.blockSignals(True)
        current = self.app_filter.currentText()
        self.app_filter.clear()
        self.app_filter.addItem("All Applications")
        self.app_filter.addItems(apps)
        if current in [self.app_filter.itemText(i) for i in range(self.app_filter.count())]:
            self.app_filter.setCurrentText(current)
        self.app_filter.blockSignals(False)

        filter_app = self.app_filter.currentText()
        filtered = [p for p in self.profiles if filter_app == "All Applications" or p.get("app_name") == filter_app]

        if not filtered:
            empty_label = QLabel("No profiles. Click '+ Add Profile' to start.")
            empty_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-style: italic; margin-top: 50px;")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for profile in filtered:
            card = ProfileCard(profile)
            card.clicked.connect(self.activate_profile)
            card.edit_clicked.connect(self.edit_profile)
            card.delete_clicked.connect(self.delete_profile)
            self.scroll_layout.addWidget(card)

    def add_profile(self):
        dialog = ProfileDialog(self)
        if dialog.exec():
            new_profile = dialog.get_data()
            new_profile["active"] = False
            self.profiles.append(new_profile)
            self.save_profiles()
            self.refresh_list()

    def edit_profile(self, profile):
        dialog = ProfileDialog(self, profile.copy())
        if dialog.exec():
            updated = dialog.get_data()
            self.profiles[self.profiles.index(profile)] = updated
            self.save_profiles()
            self.refresh_list()

    def delete_profile(self, profile):
        reply = QMessageBox.question(self, 'Delete Profile', 
                                    f"Delete '{profile['name']}'?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
            QMessageBox.information(self, "Success", f"Profile '{profile['name']}' activated!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Activation failed: {str(e)}")

    def execute_activation(self, profile):
        source_path = profile["path"]
        target_dir = profile["target_path"]
        is_locked = profile.get("is_locked", False)
        password = profile.get("password", "")

        if not os.path.exists(source_path):
            raise Exception(f"Source path does not exist: {source_path}")

        os.makedirs(target_dir, exist_ok=True)

        for item in os.listdir(source_path):
            s = os.path.join(source_path, item)
            d_name = item[:-4] if is_locked and item.endswith(".enc") else item
            d = os.path.join(target_dir, d_name)

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
    app.setFont(QFont("Segoe UI", 10))
    window = AppProfileManager()
    window.show()
    sys.exit(app.exec())
