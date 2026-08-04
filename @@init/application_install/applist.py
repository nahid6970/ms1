# Type1: Global
import sys
import os
import json
import ctypes
import subprocess
import webbrowser

UTILITY_PATH = r"C:\@delta\ms1"
if UTILITY_PATH not in sys.path:
    sys.path.append(UTILITY_PATH)

import install_deps

install_deps.bootstrap(__file__)

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QFormLayout,
)


def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


set_console_title("App List")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "data.json")


def normalize_link(link):
    link = (link or "").strip()
    if not link:
        return ""
    if link.startswith(("http://", "https://", "mailto:", "file:", "ftp://")):
        return link
    return f"https://{link}"


def load_applications():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        apps = json.load(f)

    apps.sort(key=lambda x: x.get("name", "").lower())
    for app in apps:
        if app.get("scoop_name") and not app.get("scoop_path"):
            app["scoop_path"] = os.path.join(
                os.path.expanduser("~"),
                "scoop",
                "apps",
                app["scoop_name"],
                "current",
            )
    return apps


def save_applications(apps):
    serializable_apps = []
    for app in apps:
        scoop_path = app.get("scoop_path", "")
        if not scoop_path and app.get("scoop_name"):
            scoop_path = os.path.join(
                os.path.expanduser("~"),
                "scoop",
                "apps",
                app["scoop_name"],
                "current",
            )
            app["scoop_path"] = scoop_path

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

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_apps, f, indent=4)


def open_application_link(link, parent=None):
    normalized_link = normalize_link(link)
    if normalized_link:
        webbrowser.open_new_tab(normalized_link)


def run_shell_command(command):
    subprocess.Popen(f'start pwsh -NoExit -Command "{command}"', shell=True)


def choice_dialog(title, options, parent=None):
    if not options:
        return
    if len(options) == 1:
        options[0]["command"]()
        return

    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setModal(True)
    dialog.setMinimumWidth(360)

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)

    label = QLabel(title)
    label.setStyleSheet("font-size: 16px; font-weight: 700;")
    layout.addWidget(label)

    row = QHBoxLayout()
    row.setSpacing(8)
    layout.addLayout(row)

    for option in options:
        btn = QPushButton(option["text"])
        btn.clicked.connect(lambda checked=False, cmd=option["command"], d=dialog: (cmd(), d.accept()))
        row.addWidget(btn)

    dialog.exec()


class AppFormDialog(QDialog):
    def __init__(self, title, submit_text, app_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(540)
        self.setStyleSheet(
            """
            QDialog { background: #232323; color: #f0f0f0; }
            QGroupBox {
                background: #2b2b2b;
                border: 1px solid #3c3c3c;
                border-radius: 10px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                font-weight: 700;
            }
            QLabel { color: #f0f0f0; }
            QLineEdit {
                background: #2a2f36;
                border: 1px solid #565a61;
                border-radius: 6px;
                padding: 7px 10px;
                color: #f0f0f0;
            }
            QLineEdit:focus { border: 1px solid #5da9ff; }
            QDialogButtonBox QPushButton {
                min-width: 110px;
                padding: 7px 12px;
                border-radius: 6px;
            }
            """
        )

        self.fields = {}
        self._build_ui(title, submit_text)
        if app_data:
            self._load_values(app_data)

    def _line_edit(self, placeholder=""):
        widget = QLineEdit()
        widget.setPlaceholderText(placeholder)
        return widget

    def _build_ui(self, title, submit_text):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        header = QLabel(title)
        header.setStyleSheet("font-size: 22px; font-weight: 700;")
        sub = QLabel("Add a package source or a direct website link.")
        sub.setStyleSheet("color: #b8b8b8; font-size: 12px;")
        outer.addWidget(header)
        outer.addWidget(sub)

        app_group = QGroupBox("App Details")
        app_layout = QFormLayout(app_group)
        app_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.fields["name"] = self._line_edit("Display name")
        app_layout.addRow("App Name", self.fields["name"])
        outer.addWidget(app_group)

        source_group = QGroupBox("Package Sources")
        source_layout = QGridLayout(source_group)
        source_layout.setHorizontalSpacing(12)
        source_layout.setVerticalSpacing(8)

        self.fields["scoop_name"] = self._line_edit("scoop package")
        self.fields["winget_name"] = self._line_edit("winget package id")
        self.fields["scoop_path"] = self._line_edit("Executable or folder path")
        self.fields["winget_path"] = self._line_edit("Executable path")

        source_layout.addWidget(QLabel("Scoop Name"), 0, 0)
        source_layout.addWidget(QLabel("Winget Name"), 0, 1)
        source_layout.addWidget(self.fields["scoop_name"], 1, 0)
        source_layout.addWidget(self.fields["winget_name"], 1, 1)
        source_layout.addWidget(QLabel("Scoop Path"), 2, 0)
        source_layout.addWidget(QLabel("Winget Path"), 2, 1)
        source_layout.addWidget(self.fields["scoop_path"], 3, 0)
        source_layout.addWidget(self.fields["winget_path"], 3, 1)
        outer.addWidget(source_group)

        link_group = QGroupBox("Website Link")
        link_layout = QFormLayout(link_group)
        self.fields["link"] = self._line_edit("https://...")
        link_layout.addRow("Link", self.fields["link"])
        outer.addWidget(link_group)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText(submit_text)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        outer.addWidget(buttons)

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


class DragBar(QWidget):
    def __init__(self, window, parent=None):
        super().__init__(parent)
        self._window = window
        self._drag_pos = None
        self.setFixedHeight(26)
        self.setObjectName("dragBar")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()


class AppRowWidget(QFrame):
    def __init__(self, app_data, callbacks, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.callbacks = callbacks
        self.actions_visible = False
        self.setObjectName("appRow")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self._build_ui()
        self.refresh_status()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        self.checkbox = QCheckBox(self.app_data.get("name", ""))
        self.checkbox.setObjectName("appCheck")
        self.checkbox.stateChanged.connect(self.refresh_status)
        header.addWidget(self.checkbox, 1)

        self.status_badge = QLabel()
        self.status_badge.setFixedHeight(22)
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_badge.setStyleSheet(
            "padding: 0 10px; border-radius: 11px; font-weight: 700;"
        )
        header.addWidget(self.status_badge, 0)

        self.expand_btn = QToolButton()
        self.expand_btn.setText("▾")
        self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_btn.clicked.connect(self.toggle_actions)
        header.addWidget(self.expand_btn, 0)

        outer.addLayout(header)

        self.actions_panel = QFrame()
        actions = QGridLayout(self.actions_panel)
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setHorizontalSpacing(6)
        actions.setVerticalSpacing(6)

        self.install_btn = QPushButton("Install")
        self.uninstall_btn = QPushButton("Uninstall")
        self.open_btn = QPushButton("Open Path")
        self.link_btn = QPushButton("Link")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        self.install_btn.clicked.connect(self._install)
        self.uninstall_btn.clicked.connect(self._uninstall)
        self.open_btn.clicked.connect(self._open_location)
        self.link_btn.clicked.connect(self._open_link)
        self.edit_btn.clicked.connect(self._edit)
        self.delete_btn.clicked.connect(self._delete)

        buttons = [
            self.install_btn,
            self.uninstall_btn,
            self.open_btn,
            self.link_btn,
            self.edit_btn,
            self.delete_btn,
        ]

        for index, button in enumerate(buttons):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(30)
            actions.addWidget(button, 0, index)

        self.link_btn.setVisible(bool(self.app_data.get("link", "").strip()))
        self.actions_panel.setVisible(False)
        outer.addWidget(self.actions_panel)

        self.setStyleSheet(
            """
            QFrame#appRow {
                background: #20242b;
                border: 1px solid #2d323b;
                border-radius: 10px;
            }
            QCheckBox {
                color: #f0f0f0;
                font-weight: 700;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
            }
            QToolButton {
                background: transparent;
                border: none;
                color: #cfcfcf;
                font-size: 16px;
                padding: 0 4px;
            }
            QPushButton {
                background: #2f3640;
                color: #f0f0f0;
                border: 1px solid #424a55;
                border-radius: 6px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background: #3b4451;
            }
            """
        )

    def toggle_actions(self):
        self.actions_visible = not self.actions_visible
        self.actions_panel.setVisible(self.actions_visible)
        self.expand_btn.setText("▴" if self.actions_visible else "▾")

    def matches(self, query):
        query = (query or "").strip().lower()
        return not query or query in self.app_data.get("name", "").lower()

    def refresh_status(self):
        scoop_path = self.app_data.get("scoop_path", "")
        winget_path = self.app_data.get("winget_path", "")
        scoop_installed = os.path.exists(scoop_path)
        winget_installed = os.path.exists(winget_path)
        installed = scoop_installed or winget_installed
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(installed)
        self.checkbox.blockSignals(False)

        if scoop_installed:
            badge = "[S]"
            badge_style = "background: #2d4b35; color: #ffffff;"
        elif winget_installed:
            badge = "[W]"
            badge_style = "background: #224d77; color: #d9ecff;"
        else:
            badge = "[X]"
            badge_style = "background: #5a2222; color: #ffd6d6;"

        self.status_badge.setText(badge)
        self.status_badge.setStyleSheet(
            f"padding: 0 10px; border-radius: 11px; font-weight: 700; {badge_style}"
        )

    def _install(self):
        options = []
        if self.app_data.get("winget_name"):
            options.append(
                {
                    "text": "Winget",
                    "command": lambda: run_shell_command(
                        f"winget install {self.app_data['winget_name']}"
                    ),
                }
            )
        if self.app_data.get("scoop_name"):
            options.append(
                {
                    "text": "Scoop",
                    "command": lambda: run_shell_command(
                        f"scoop install {self.app_data['scoop_name']}"
                    ),
                }
            )
        choice_dialog("Select Source", options, self)

    def _uninstall(self):
        options = []
        if self.app_data.get("winget_name"):
            options.append(
                {
                    "text": "Winget",
                    "command": lambda: run_shell_command(
                        f"winget uninstall {self.app_data['winget_name']}"
                    ),
                }
            )
        if self.app_data.get("scoop_name"):
            options.append(
                {
                    "text": "Scoop",
                    "command": lambda: run_shell_command(
                        f"scoop uninstall {self.app_data['scoop_name']}"
                    ),
                }
            )
        choice_dialog("Select Source", options, self)

    def _open_location(self):
        options = []
        if self.app_data.get("winget_path"):
            options.append(
                {
                    "text": "Winget",
                    "command": lambda: subprocess.Popen(
                        f'explorer /select,"{self.app_data["winget_path"]}"',
                        shell=True,
                    ),
                }
            )
        if self.app_data.get("scoop_path"):
            options.append(
                {
                    "text": "Scoop",
                    "command": lambda: subprocess.Popen(
                        f'explorer /select,"{self.app_data["scoop_path"]}"',
                        shell=True,
                    ),
                }
            )
        choice_dialog("Select Source", options, self)

    def _open_link(self):
        open_application_link(self.app_data.get("link", ""), self)

    def _edit(self):
        self.callbacks["edit"](self.app_data)

    def _delete(self):
        self.callbacks["delete"](self.app_data)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.applications = []
        self.rows = []
        self.setWindowTitle("Folder")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setMinimumSize(520, 680)
        self.resize(560, 760)
        self._build_ui()
        self.reload_applications()

    def _build_ui(self):
        root = QFrame()
        root.setObjectName("rootFrame")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(1, 1, 1, 1)
        root_layout.setSpacing(0)

        outer_border = QFrame()
        outer_border.setObjectName("outerBorder")
        outer_layout = QVBoxLayout(outer_border)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        root_layout.addWidget(outer_border)

        self.drag_bar = DragBar(self, outer_border)
        self.drag_bar.setStyleSheet("background: #1d2027;")
        drag_layout = QHBoxLayout(self.drag_bar)
        drag_layout.setContentsMargins(10, 0, 10, 0)
        drag_layout.setSpacing(8)

        drag_spacer = QWidget()
        drag_spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        drag_layout.addWidget(drag_spacer)

        close_btn = QToolButton()
        close_btn.setText("✕")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(
            "QToolButton { color: #ff6b6b; border: none; font-size: 15px; padding: 0 4px; }"
            "QToolButton:hover { color: #ffffff; }"
        )
        drag_layout.addWidget(close_btn)
        outer_layout.addWidget(self.drag_bar)

        body = QFrame()
        body.setObjectName("bodyFrame")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(14, 12, 14, 14)
        body_layout.setSpacing(12)
        outer_layout.addWidget(body, 1)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        body_layout.addLayout(top_row)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search apps...")
        self.search.textChanged.connect(self.filter_rows)
        self.search.setMinimumHeight(34)
        top_row.addWidget(self.search, 1)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(QSize(36, 34))
        add_btn.clicked.connect(self.add_app)
        top_row.addWidget(add_btn, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        body_layout.addWidget(self.scroll, 1)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch(1)
        self.scroll.setWidget(self.list_container)

        self.setStyleSheet(
            """
            QMainWindow { background: #d32f2f; }
            QFrame#outerBorder { background: #1d2027; border: 1px solid #d32f2f; }
            QFrame#bodyFrame { background: #1d2027; }
            QLineEdit {
                background: #2a2f36;
                color: #f0f0f0;
                border: 1px solid #565a61;
                border-radius: 8px;
                padding: 7px 10px;
            }
            QLineEdit:focus { border: 1px solid #5da9ff; }
            QPushButton {
                background: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 12px;
                font-weight: 700;
            }
            QPushButton:hover { background: #0056b3; }
            QScrollArea { background: transparent; }
            """
        )

        quit_action = QAction(self)
        quit_action.setShortcut(QKeySequence.StandardKey.Close)
        quit_action.triggered.connect(self.close)
        self.addAction(quit_action)

    def reload_applications(self):
        self.applications = load_applications()
        self._rebuild_rows()

    def _rebuild_rows(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.rows = []
        callbacks = {"edit": self.edit_app, "delete": self.delete_app}
        for app in self.applications:
            row = AppRowWidget(app, callbacks, self.list_container)
            self.list_layout.addWidget(row)
            self.rows.append(row)

        self.list_layout.addStretch(1)
        self.filter_rows()

    def filter_rows(self):
        query = self.search.text()
        for row in self.rows:
            row.setVisible(row.matches(query))

    def add_app(self):
        dialog = AppFormDialog("Add New Application", "Save App", parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.applications.append(dialog.get_data())
            save_applications(self.applications)
            self.reload_applications()

    def edit_app(self, app_data):
        dialog = AppFormDialog("Edit Application", "Save Changes", app_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            app_data.update(dialog.get_data())
            save_applications(self.applications)
            self.reload_applications()

    def delete_app(self, app_data):
        reply = QMessageBox.question(
            self,
            "Delete Application",
            f"Delete {app_data.get('name', 'this app')}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.applications = [app for app in self.applications if app != app_data]
            save_applications(self.applications)
            self.reload_applications()


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    screen = app.primaryScreen().availableGeometry()
    x = screen.width() - window.width() - 12
    y = (screen.height() - window.height()) // 2
    window.move(max(0, x), max(0, y))
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
