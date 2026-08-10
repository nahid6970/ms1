# Type1: Global
import sys, os
UTILITY_PATH = r"C:\@delta\ms1"
if UTILITY_PATH not in sys.path: sys.path.append(UTILITY_PATH)
import install_deps
install_deps.bootstrap(__file__)

import json
import subprocess
import ctypes
import webbrowser

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QCursor, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QFrame,
    QMessageBox,
    QCheckBox,
    QDialogButtonBox,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "data.json")
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "settings.json")

# THEME PALETTE (MATCHING ORIGINAL DESIGN)
BG_MAIN = "#1d2027"
BORDER_RED = "#d32f2f"
TEXT_WHITE = "#FFFFFF"
TEXT_RED = "#FF3333"
TEXT_BLUE = "#41ABFF"
TEXT_GREEN = "#00FF00"
ACCENT_BLUE = "#007BFF"


def set_console_title(title):
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    except Exception:
        pass


set_console_title("App List")


def normalize_link(link):
    link = (link or "").strip()
    if not link:
        return ""
    if link.startswith(("http://", "https://", "mailto:", "file:", "ftp://")):
        return link
    return f"https://{link}"


def load_settings():
    default_settings = {"always_on_top": True, "confirm_delete": True}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_settings.update(data)
        except Exception:
            pass
    return default_settings


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")


def load_applications():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                apps = json.load(f)
                apps.sort(key=lambda x: x.get("name", "").lower())
                for app in apps:
                    if app.get("scoop_name") and not app.get("scoop_path"):
                        app["scoop_path"] = os.path.join(
                            os.path.expanduser("~"), "scoop", "apps", app["scoop_name"], "current"
                        )
                return apps
        except Exception as e:
            print(f"Error loading applications: {e}")
    return []


def save_applications(apps):
    serializable_apps = []
    for app in apps:
        scoop_path = app.get("scoop_path", "")
        if not scoop_path and app.get("scoop_name"):
            scoop_path = os.path.join(
                os.path.expanduser("~"), "scoop", "apps", app["scoop_name"], "current"
            )

        serializable_apps.append(
            {
                "name": app.get("name", ""),
                "scoop_name": app.get("scoop_name", ""),
                "scoop_path": scoop_path,
                "winget_name": app.get("winget_name", ""),
                "winget_path": app.get("winget_path", ""),
                "link": app.get("link", ""),
            }
        )
    serializable_apps.sort(key=lambda x: x.get("name", "").lower())
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable_apps, f, indent=4)
    except Exception as e:
        print(f"Error saving applications: {e}")


def apply_dialog_stylesheet(target_widget):
    target_widget.setStyleSheet(
        f"""
        QDialog {{
            background-color: #232323;
            color: #f0f0f0;
        }}
        QWidget {{
            color: #f0f0f0;
            font-family: 'Consolas', 'Segoe UI', monospace;
            font-size: 10pt;
        }}
        QLineEdit {{
            background-color: #2a2f36;
            border: 1px solid #565a61;
            border-radius: 6px;
            padding: 7px 10px;
            color: #f0f0f0;
        }}
        QLineEdit:focus {{
            border: 1px solid #5da9ff;
        }}
        QGroupBox {{
            background-color: #2b2b2b;
            border: 1px solid #3c3c3c;
            border-radius: 8px;
            margin-top: 10px;
            padding: 10px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 4px;
            color: #5da9ff;
        }}
        QPushButton {{
            background-color: #383e47;
            border: 1px solid #565a61;
            border-radius: 6px;
            color: white;
            padding: 6px 14px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #4a525d;
            border-color: #007bff;
        }}
        QCheckBox {{
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid #565a61;
            background: #2a2f36;
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            background: #007bff;
            border-color: #007bff;
        }}
        """
    )


class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedWidth(360)
        self.settings = settings.copy()
        apply_dialog_stylesheet(self)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        grp = QGroupBox("PREFERENCES")
        form = QVBoxLayout(grp)
        form.setSpacing(10)

        self.chk_topmost = QCheckBox("Keep Window Always on Top")
        self.chk_topmost.setChecked(self.settings.get("always_on_top", True))
        form.addWidget(self.chk_topmost)

        self.chk_confirm = QCheckBox("Confirm before deletion")
        self.chk_confirm.setChecked(self.settings.get("confirm_delete", True))
        form.addWidget(self.chk_confirm)

        layout.addWidget(grp)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save_and_accept(self):
        self.settings["always_on_top"] = self.chk_topmost.isChecked()
        self.settings["confirm_delete"] = self.chk_confirm.isChecked()
        save_settings(self.settings)
        self.accept()


class AppFormDialog(QDialog):
    def __init__(self, window_title, submit_text, app_to_edit=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setMinimumWidth(500)
        self.app_to_edit = app_to_edit
        self.fields = {}
        apply_dialog_stylesheet(self)
        self._build_ui(window_title, submit_text)

        if app_to_edit:
            self._load_values(app_to_edit)

    def _build_ui(self, title_text, submit_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffffff;")
        subtitle = QLabel("Add a package source or a direct website link.")
        subtitle.setStyleSheet("color: #b8b8b8; font-size: 9pt;")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        app_group = QGroupBox("App Details")
        app_layout = QFormLayout(app_group)
        self.fields["name"] = QLineEdit()
        self.fields["name"].setPlaceholderText("Display name")
        app_layout.addRow("App Name:", self.fields["name"])
        layout.addWidget(app_group)

        source_group = QGroupBox("Package Sources")
        source_layout = QFormLayout(source_group)
        self.fields["scoop_name"] = QLineEdit()
        self.fields["scoop_name"].setPlaceholderText("scoop package")
        self.fields["scoop_path"] = QLineEdit()
        self.fields["scoop_path"].setPlaceholderText("Executable or folder path")

        self.fields["winget_name"] = QLineEdit()
        self.fields["winget_name"].setPlaceholderText("winget package id")
        self.fields["winget_path"] = QLineEdit()
        self.fields["winget_path"].setPlaceholderText("Executable path")

        source_layout.addRow("Scoop Name:", self.fields["scoop_name"])
        source_layout.addRow("Scoop Path:", self.fields["scoop_path"])
        source_layout.addRow("Winget Name:", self.fields["winget_name"])
        source_layout.addRow("Winget Path:", self.fields["winget_path"])
        layout.addWidget(source_group)

        link_group = QGroupBox("Website Link")
        link_layout = QFormLayout(link_group)
        self.fields["link"] = QLineEdit()
        self.fields["link"].setPlaceholderText("https://...")
        link_layout.addRow("Link:", self.fields["link"])
        layout.addWidget(link_group)

        btn_box = QDialogButtonBox()
        save_btn = btn_box.addButton(submit_text, QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_btn = btn_box.addButton("Cancel", QDialogButtonBox.ButtonRole.RejectRole)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _load_values(self, data):
        self.fields["name"].setText(data.get("name", ""))
        self.fields["scoop_name"].setText(data.get("scoop_name", ""))
        self.fields["scoop_path"].setText(data.get("scoop_path", ""))
        self.fields["winget_name"].setText(data.get("winget_name", ""))
        self.fields["winget_path"].setText(data.get("winget_path", ""))
        self.fields["link"].setText(data.get("link", ""))

    def get_data(self):
        return {
            "name": self.fields["name"].text().strip(),
            "scoop_name": self.fields["scoop_name"].text().strip(),
            "scoop_path": self.fields["scoop_path"].text().strip(),
            "winget_name": self.fields["winget_name"].text().strip(),
            "winget_path": self.fields["winget_path"].text().strip(),
            "link": self.fields["link"].text().strip(),
        }


class SourceActionDialog(QDialog):
    """Pops up when user clicks Install / Uninstall / Open, offering Winget, Scoop, AND Website Link options together."""

    def __init__(self, mode, app_data, parent=None):
        super().__init__(parent)
        self.mode = mode
        self.app_data = app_data
        self.setWindowTitle("Select Source")
        self.setFixedWidth(320)
        apply_dialog_stylesheet(self)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl_title = QLabel(f"{self.mode.upper()} - {self.app_data.get('name', '')}")
        lbl_title.setStyleSheet("color: #ffffff; font-size: 11pt; font-weight: bold;")
        layout.addWidget(lbl_title)

        grp_layout = QHBoxLayout()
        grp_layout.setSpacing(10)

        options_count = 0
        winget_name = self.app_data.get("winget_name", "")
        winget_path = self.app_data.get("winget_path", "")
        scoop_name = self.app_data.get("scoop_name", "")
        scoop_path = self.app_data.get("scoop_path", "")
        link = normalize_link(self.app_data.get("link", ""))

        if self.mode == "install":
            if winget_name:
                btn_w = QPushButton("Winget")
                btn_w.setStyleSheet(
                    "background-color: #0078D7; border: 1px solid #005a9e; color: #FFFFFF; font-weight: bold; padding: 8px 14px;"
                )
                btn_w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_w.clicked.connect(lambda: self._run_winget_install(winget_name))
                grp_layout.addWidget(btn_w)
                options_count += 1

            if scoop_name:
                btn_s = QPushButton("Scoop")
                btn_s.setStyleSheet(
                    "background-color: #FFFFFF; border: 1px solid #cccccc; color: #000000; font-weight: bold; padding: 8px 14px;"
                )
                btn_s.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_s.clicked.connect(lambda: self._run_scoop_install(scoop_name))
                grp_layout.addWidget(btn_s)
                options_count += 1

            if link:
                btn_l = QPushButton("Website Link")
                btn_l.setStyleSheet(
                    "background-color: #28a745; border: 1px solid #1e7e34; color: #FFFFFF; font-weight: bold; padding: 8px 14px;"
                )
                btn_l.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_l.clicked.connect(lambda: self._open_url(link))
                grp_layout.addWidget(btn_l)
                options_count += 1

        elif self.mode == "uninstall":
            if winget_name:
                btn_w = QPushButton("Winget")
                btn_w.setStyleSheet(
                    "background-color: #0078D7; border: 1px solid #005a9e; color: #FFFFFF; font-weight: bold; padding: 8px 14px;"
                )
                btn_w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_w.clicked.connect(lambda: self._run_winget_uninstall(winget_name))
                grp_layout.addWidget(btn_w)
                options_count += 1

            if scoop_name:
                btn_s = QPushButton("Scoop")
                btn_s.setStyleSheet(
                    "background-color: #FFFFFF; border: 1px solid #cccccc; color: #000000; font-weight: bold; padding: 8px 14px;"
                )
                btn_s.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_s.clicked.connect(lambda: self._run_scoop_uninstall(scoop_name))
                grp_layout.addWidget(btn_s)
                options_count += 1

        elif self.mode == "open":
            if winget_path:
                btn_w = QPushButton("Winget Path")
                btn_w.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_w.clicked.connect(lambda: self._open_explorer(winget_path))
                grp_layout.addWidget(btn_w)
                options_count += 1

            if scoop_path:
                btn_s = QPushButton("Scoop Path")
                btn_s.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn_s.clicked.connect(lambda: self._open_explorer(scoop_path))
                grp_layout.addWidget(btn_s)
                options_count += 1

        if options_count == 0:
            lbl_none = QLabel("No source or link specified.")
            lbl_none.setStyleSheet("color: #ff3333;")
            layout.addWidget(lbl_none)
        else:
            layout.addLayout(grp_layout)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)

    def _run_winget_install(self, name):
        subprocess.Popen(
            f'start pwsh -NoExit -Command "winget install {name}"', shell=True
        )
        self.accept()

    def _run_scoop_install(self, name):
        subprocess.Popen(
            f'start pwsh -NoExit -Command "scoop install {name}"', shell=True
        )
        self.accept()

    def _run_winget_uninstall(self, name):
        subprocess.Popen(
            f'start pwsh -NoExit -Command "winget uninstall {name}"', shell=True
        )
        self.accept()

    def _run_scoop_uninstall(self, name):
        subprocess.Popen(
            f'start pwsh -NoExit -Command "scoop uninstall {name}"', shell=True
        )
        self.accept()

    def _open_url(self, url):
        webbrowser.open_new_tab(url)
        self.accept()

    def _open_explorer(self, path):
        subprocess.Popen(f'explorer /select,"{path}"')
        self.accept()


class AppRowWidget(QWidget):
    """Clean, unboxed application list row matching original UI aesthetic."""

    def __init__(self, app_data, on_edit, on_delete, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.on_edit_cb = on_edit
        self.on_delete_cb = on_delete
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 2, 0, 2)
        main_layout.setSpacing(2)

        # Main Row Widget (Clickable Header)
        self.row_widget = QWidget()
        self.row_widget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        row_layout = QHBoxLayout(self.row_widget)
        row_layout.setContentsMargins(6, 2, 6, 2)
        row_layout.setSpacing(8)

        # Installation Status Calculation
        scoop_path = self.app_data.get("scoop_path", "")
        winget_path = self.app_data.get("winget_path", "")
        scoop_installed = os.path.exists(scoop_path) if scoop_path else False
        winget_installed = os.path.exists(winget_path) if winget_path else False
        is_installed = scoop_installed or winget_installed

        # Custom Styled Checkbox Indicator
        self.chk = QCheckBox()
        self.chk.setChecked(is_installed)
        self.chk.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.chk.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.chk.setStyleSheet(
            f"""
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid #565a61;
                background-color: {BG_MAIN};
            }}
            QCheckBox::indicator:checked {{
                background-color: #ffffff;
                border: 1px solid #ffffff;
                image: none;
            }}
            """
        )

        # Label formatting: App Name
        app_name = self.app_data.get("name", "Unnamed")
        if scoop_installed:
            text_color = TEXT_WHITE
        elif winget_installed:
            text_color = TEXT_BLUE
        else:
            text_color = TEXT_RED

        self.lbl_text = QLabel(app_name)
        self.lbl_text.setStyleSheet(
            f"font-family: 'JetBrainsMono NF', 'Consolas', monospace; font-size: 11pt; font-weight: bold; color: {text_color};"
        )

        row_layout.addWidget(self.chk)
        row_layout.addWidget(self.lbl_text, stretch=1)

        main_layout.addWidget(self.row_widget)

        # Expandable Actions Panel
        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget)
        actions_layout.setContentsMargins(30, 2, 0, 4)
        actions_layout.setSpacing(10)

        # Minimalist Circular / Icon Buttons matching original style
        btn_style_common = (
            "QPushButton { background: transparent; border: none; font-size: 11pt; font-weight: bold; font-family: 'JetBrainsMono NF', 'Consolas'; padding: 0px; } "
        )

        btn_ins = QPushButton("☉")
        btn_ins.setToolTip("Install")
        btn_ins.setStyleSheet(btn_style_common + "QPushButton { color: #00FF00; } QPushButton:hover { color: #88FF88; }")
        btn_ins.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ins.clicked.connect(self._on_install_clicked)

        btn_unins = QPushButton("☉")
        btn_unins.setToolTip("Uninstall")
        btn_unins.setStyleSheet(btn_style_common + "QPushButton { color: #FF0000; } QPushButton:hover { color: #FF6666; }")
        btn_unins.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_unins.clicked.connect(self._on_uninstall_clicked)

        btn_open = QPushButton("☉")
        btn_open.setToolTip("Open Location")
        btn_open.setStyleSheet(btn_style_common + "QPushButton { color: #EAC353; } QPushButton:hover { color: #FFEE88; }")
        btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_open.clicked.connect(self._on_open_clicked)

        actions_layout.addWidget(btn_ins)
        actions_layout.addWidget(btn_unins)
        actions_layout.addWidget(btn_open)

        link = normalize_link(self.app_data.get("link", ""))
        if link:
            btn_link = QPushButton("Link")
            btn_link.setToolTip("Open Website Link")
            btn_link.setStyleSheet(btn_style_common + "QPushButton { color: #FFFFFF; font-size: 10pt; } QPushButton:hover { color: #007BFF; }")
            btn_link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_link.clicked.connect(lambda: webbrowser.open_new_tab(link))
            actions_layout.addWidget(btn_link)

        btn_edit = QPushButton("📝")
        btn_edit.setToolTip("Edit")
        btn_edit.setStyleSheet(btn_style_common + "QPushButton { color: #007BFF; font-size: 10pt; } QPushButton:hover { color: #5DA9FF; }")
        btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_edit.clicked.connect(lambda: self.on_edit_cb(self.app_data))

        btn_del = QPushButton("☉")
        btn_del.setToolTip("Delete")
        btn_del.setStyleSheet(btn_style_common + "QPushButton { color: #DC3545; } QPushButton:hover { color: #FF6666; }")
        btn_del.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_del.clicked.connect(lambda: self.on_delete_cb(self.app_data))

        actions_layout.addWidget(btn_edit)
        actions_layout.addWidget(btn_del)
        actions_layout.addStretch()

        main_layout.addWidget(self.actions_widget)
        self.actions_widget.hide()

        # Connect click event on row to toggle actions frame
        self.row_widget.mousePressEvent = self._toggle_actions

    def _toggle_actions(self, event):
        if self.actions_widget.isVisible():
            self.actions_widget.hide()
        else:
            self.actions_widget.show()

    def _on_install_clicked(self):
        dlg = SourceActionDialog("install", self.app_data, self.window())
        dlg.exec()

    def _on_uninstall_clicked(self):
        dlg = SourceActionDialog("uninstall", self.app_data, self.window())
        dlg.exec()

    def _on_open_clicked(self):
        winget_path = self.app_data.get("winget_path", "")
        scoop_path = self.app_data.get("scoop_path", "")

        if winget_path and scoop_path:
            dlg = SourceActionDialog("open", self.app_data, self.window())
            dlg.exec()
        elif winget_path:
            subprocess.Popen(f'explorer /select,"{winget_path}"')
        elif scoop_path:
            subprocess.Popen(f'explorer /select,"{scoop_path}"')
        else:
            QMessageBox.information(
                self, "Open Location", "No valid Scoop or Winget path configured."
            )


class TitleBar(QWidget):
    """Clean Top Header Drag Bar matching original look with Close '✕' button."""

    def __init__(
        self,
        on_restart,
        on_settings,
        on_close,
        parent=None,
    ):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = QPoint()

        self.setFixedHeight(26)
        self.setStyleSheet(f"background-color: {BG_MAIN};")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 4, 0)
        layout.setSpacing(6)

        btn_restart = QPushButton("↺")
        btn_restart.setToolTip("Quick Restart Script")
        btn_restart.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: #888888; font-size: 10pt; font-weight: bold; }} "
            f"QPushButton:hover {{ color: {TEXT_WHITE}; }}"
        )
        btn_restart.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_restart.clicked.connect(on_restart)

        btn_settings = QPushButton("⚙")
        btn_settings.setToolTip("Settings")
        btn_settings.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: #888888; font-size: 10pt; font-weight: bold; }} "
            f"QPushButton:hover {{ color: {TEXT_WHITE}; }}"
        )
        btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_settings.clicked.connect(on_settings)

        btn_close = QPushButton("✕")
        btn_close.setToolTip("Close Window")
        btn_close.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {TEXT_RED}; font-size: 11pt; font-weight: bold; }} "
            f"QPushButton:hover {{ color: #FF6666; }}"
        )
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.clicked.connect(on_close)

        layout.addStretch()
        layout.addWidget(btn_restart)
        layout.addWidget(btn_settings)
        layout.addWidget(btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.parent_window.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.parent_window.move(
                event.globalPosition().toPoint() - self.drag_position
            )
            event.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.applications = load_applications()
        self.row_widgets = []

        self._apply_window_flags()
        self._setup_geometry()
        self._build_ui()

    def _apply_window_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        if self.settings.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

    def _setup_geometry(self):
        screen = QApplication.primaryScreen().geometry()
        width, height = 430, 600
        x = screen.width() - width - 20
        y = (screen.height() - height) // 2
        self.setGeometry(x, y, width, height)

    def _build_ui(self):
        # Red Bordered Container Frame
        border_frame = QFrame()
        border_frame.setStyleSheet(
            f"QFrame {{ background-color: {BG_MAIN}; border: 1px solid {BORDER_RED}; }}"
        )
        self.setCentralWidget(border_frame)

        main_layout = QVBoxLayout(border_frame)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(0)

        # Header Drag Bar
        title_bar = TitleBar(
            on_restart=self.restart_app,
            on_settings=self.open_settings,
            on_close=self.close,
            parent=self,
        )
        main_layout.addWidget(title_bar)

        # Controls Area: Search Entry + Add Button
        controls_widget = QWidget()
        controls_widget.setStyleSheet("border: none;")
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(16, 4, 16, 10)
        controls_layout.setSpacing(10)

        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search apps...")
        self.search_entry.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: #2a2f36;
                color: {TEXT_WHITE};
                border: 1px solid #565a61;
                border-radius: 6px;
                padding: 6px 10px;
                font-family: 'Calibri', 'Segoe UI', sans-serif;
                font-size: 11pt;
            }}
            QLineEdit:focus {{
                border: 1px solid #007bff;
            }}
            """
        )
        self.search_entry.textChanged.connect(self.filter_apps)

        btn_add = QPushButton("+")
        btn_add.setToolTip("Add New Application")
        btn_add.setFixedSize(32, 32)
        btn_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_add.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {ACCENT_BLUE};
                color: {TEXT_WHITE};
                border: none;
                border-radius: 6px;
                font-family: 'Calibri', sans-serif;
                font-size: 16pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0056b3;
            }}
            """
        )
        btn_add.clicked.connect(self.add_application)

        controls_layout.addWidget(self.search_entry, stretch=1)
        controls_layout.addWidget(btn_add)

        main_layout.addWidget(controls_widget)

        # Scroll Area for Application Rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.verticalScrollBar().setSingleStep(15)
        self.scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                background-color: {BG_MAIN};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {BG_MAIN};
                width: 8px;
                margin: 0px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: #565a61;
                min-height: 25px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #007bff;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
                border: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            """
        )

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet(f"background-color: {BG_MAIN}; border: none;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setContentsMargins(10, 0, 10, 0)
        self.scroll_layout.setSpacing(2)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        self.refresh_app_list()

    def refresh_app_list(self):
        self.applications = load_applications()

        # Clear existing row widgets
        for row in self.row_widgets:
            row.deleteLater()
        self.row_widgets.clear()

        # Re-populate
        for app in self.applications:
            row = AppRowWidget(
                app_data=app,
                on_edit=self.edit_application,
                on_delete=self.delete_application,
                parent=self.scroll_widget,
            )
            self.scroll_layout.addWidget(row)
            self.row_widgets.append(row)

        self.filter_apps()

    def filter_apps(self):
        query = self.search_entry.text().lower().strip()
        for row in self.row_widgets:
            name = row.app_data.get("name", "").lower()
            if query in name:
                row.show()
            else:
                row.hide()

    def add_application(self):
        dlg = AppFormDialog("Add New Application", "Save App", parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            data = dlg.get_data()
            if data.get("name"):
                self.applications.append(data)
                save_applications(self.applications)
                self.refresh_app_list()

    def edit_application(self, app_to_edit):
        dlg = AppFormDialog(
            "Edit Application", "Save Changes", app_to_edit=app_to_edit, parent=self
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            updated_data = dlg.get_data()
            if updated_data.get("name"):
                app_to_edit.update(updated_data)
                save_applications(self.applications)
                self.refresh_app_list()

    def delete_application(self, app_to_delete):
        if self.settings.get("confirm_delete", True):
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete '{app_to_delete.get('name', '')}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.applications = [a for a in self.applications if a != app_to_delete]
        save_applications(self.applications)
        self.refresh_app_list()

    def open_settings(self):
        dlg = SettingsDialog(self.settings, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.settings = load_settings()
            self._apply_window_flags()
            self.show()

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
