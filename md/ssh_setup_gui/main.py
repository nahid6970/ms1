from __future__ import annotations

import base64
import getpass
import os
import re
import socket
import subprocess
import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

APP_DIR = Path(__file__).resolve().parent
ADMIN_SCRIPT = APP_DIR / "admin_setup.ps1"

ANDROID_KEY_COMMAND = """mkdir -p ~/.ssh
if [ ! -f ~/.ssh/id_ed25519_windows_pc ]; then
  ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_windows_pc -N ""
fi
cat ~/.ssh/id_ed25519_windows_pc.pub"""


def run_powershell(command: str) -> str:
    completed = subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        capture_output=True,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        check=False,
    )
    return completed.stdout.strip()


def get_lan_ip() -> str:
    script = (
        "$r = Get-NetRoute -AddressFamily IPv4 -DestinationPrefix '0.0.0.0/0' "
        "| Where-Object { $_.InterfaceAlias -notmatch 'Tailscale|Loopback' } "
        "| Sort-Object RouteMetric | Select-Object -First 1; "
        "if ($r) { Get-NetIPAddress -AddressFamily IPv4 -InterfaceIndex $r.InterfaceIndex "
        "| Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*' } "
        "| Select-Object -First 1 -ExpandProperty IPAddress }"
    )
    ip = run_powershell(script)
    if ip:
        return ip.splitlines()[0].strip()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("192.0.2.1", 1))
            return sock.getsockname()[0]
    except OSError:
        return ""


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        note = QLabel("Settings are reserved for future setup options.")
        note.setWordWrap(True)
        layout.addWidget(note)
        close_button = QPushButton("CLOSE")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)


class SshSetupWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.username = getpass.getuser()
        self.ip_address = ""
        self.setWindowTitle("SSH Setup Wizard")
        self.resize(980, 900)
        self.setMinimumSize(760, 700)
        self.setStyleSheet(self.stylesheet())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        root = QWidget()
        self.layout = QVBoxLayout(root)
        self.layout.setContentsMargins(28, 22, 28, 24)
        self.layout.setSpacing(14)
        scroll.setWidget(root)
        self.setCentralWidget(scroll)

        self.build_header()
        self.build_pc_panel()
        self.build_android_panel()
        self.build_key_panel()
        self.build_test_panel()
        self.build_footer()
        self.refresh_pc_info()

    @staticmethod
    def stylesheet() -> str:
        return f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
            QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 10px; padding: 14px 12px 12px 12px;
                         font-weight: bold; color: {CP_YELLOW}; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }}
            QPlainTextEdit {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM};
                              padding: 8px; selection-background-color: {CP_CYAN}; selection-color: #000; }}
            QPushButton {{ background: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
                           padding: 8px 12px; font-weight: bold; }}
            QPushButton:hover {{ background: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:disabled {{ color: {CP_SUBTEXT}; border-color: #222; background: #171717; }}
            QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 22px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """

    def build_header(self) -> None:
        title_row = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel("SSH SETUP WIZARD")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-size: 21pt; font-weight: bold;")
        subtitle = QLabel("ANDROID TERMUX  →  WINDOWS PC  /  KEY-BASED LOGIN")
        subtitle.setStyleSheet(f"color: {CP_CYAN}; font-size: 9pt; letter-spacing: 1px;")
        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        title_row.addLayout(title_block)
        title_row.addStretch()
        settings_button = QPushButton("⚙ SETTINGS")
        settings_button.clicked.connect(lambda: SettingsDialog(self).exec())
        restart_button = QPushButton("↺ RESTART")
        restart_button.clicked.connect(self.restart_app)
        title_row.addWidget(settings_button)
        title_row.addWidget(restart_button)
        self.layout.addLayout(title_row)

        intro = QLabel(
            "Follow the steps below. The private key stays on Android; this app only installs the public key on Windows."
        )
        intro.setWordWrap(True)
        intro.setStyleSheet(f"color: {CP_SUBTEXT}; padding: 2px 0 8px 0;")
        self.layout.addWidget(intro)

    def panel(self, number: str, title: str) -> tuple[QGroupBox, QVBoxLayout]:
        group = QGroupBox(f"{number}  {title}")
        content = QVBoxLayout(group)
        content.setSpacing(9)
        self.layout.addWidget(group)
        return group, content

    def build_pc_panel(self) -> None:
        _, box = self.panel("01", "THIS WINDOWS PC")
        self.pc_info = QLabel()
        self.pc_info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.pc_info.setStyleSheet(f"color: {CP_CYAN}; line-height: 1.5;")
        box.addWidget(self.pc_info)
        row = QHBoxLayout()
        self.service_status = QLabel("SSH service: checking…")
        self.firewall_status = QLabel("Firewall: checking…")
        row.addWidget(self.service_status)
        row.addStretch()
        row.addWidget(self.firewall_status)
        box.addLayout(row)
        actions = QHBoxLayout()
        refresh_button = QPushButton("REFRESH PC INFO")
        refresh_button.clicked.connect(self.refresh_pc_info)
        setup_button = QPushButton("PREPARE WINDOWS SSH (ADMIN)")
        setup_button.setStyleSheet(f"QPushButton {{ border-color: {CP_CYAN}; color: {CP_CYAN}; }}")
        setup_button.clicked.connect(self.prepare_server)
        actions.addWidget(refresh_button)
        actions.addStretch()
        actions.addWidget(setup_button)
        box.addLayout(actions)

    def build_android_panel(self) -> None:
        _, box = self.panel("02", "RUN THIS COMMAND IN ANDROID TERMUX")
        note = QLabel(
            "It creates an Ed25519 key only if one does not exist, then prints the public key. "
            "The command sets an empty passphrase so SSH will not ask for one."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {CP_SUBTEXT};")
        box.addWidget(note)
        self.android_command = QPlainTextEdit(ANDROID_KEY_COMMAND)
        self.android_command.setReadOnly(True)
        self.android_command.setMaximumHeight(92)
        box.addWidget(self.android_command)
        copy_button = QPushButton("COPY ANDROID COMMAND")
        copy_button.clicked.connect(lambda: self.copy_text(ANDROID_KEY_COMMAND, "Android command copied."))
        box.addWidget(copy_button, alignment=Qt.AlignmentFlag.AlignRight)

    def build_key_panel(self) -> None:
        _, box = self.panel("03", "PASTE THE ANDROID PUBLIC KEY")
        note = QLabel(
            "Copy the entire line beginning with ssh-ed25519 from Termux and paste it below. "
            "The public key is safe to share; never paste or transfer id_ed25519_windows_pc (the private key)."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {CP_SUBTEXT};")
        box.addWidget(note)
        self.public_key = QPlainTextEdit()
        self.public_key.setPlaceholderText("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAA… optional-comment")
        self.public_key.setMaximumHeight(86)
        box.addWidget(self.public_key)
        self.install_button = QPushButton("INSTALL KEY + PREPARE PC (ADMIN)")
        self.install_button.clicked.connect(self.install_key)
        box.addWidget(self.install_button, alignment=Qt.AlignmentFlag.AlignRight)

    def build_test_panel(self) -> None:
        _, box = self.panel("04", "TEST KEY LOGIN, THEN TURN OFF SSH PASSWORDS")
        note = QLabel("Run this test command from Termux. Do not disable password login until the key connection succeeds.")
        note.setWordWrap(True)
        note.setStyleSheet(f"color: {CP_SUBTEXT};")
        box.addWidget(note)
        self.test_command = QPlainTextEdit()
        self.test_command.setReadOnly(True)
        self.test_command.setMaximumHeight(48)
        box.addWidget(self.test_command)
        copy_test_button = QPushButton("COPY TEST COMMAND")
        copy_test_button.clicked.connect(self.copy_test_command)
        box.addWidget(copy_test_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.tested_checkbox = QCheckBox("I successfully connected from Android using the key")
        self.tested_checkbox.stateChanged.connect(self.update_disable_button)
        box.addWidget(self.tested_checkbox)
        self.disable_button = QPushButton("DISABLE SSH PASSWORD LOGIN (ADMIN)")
        self.disable_button.setEnabled(False)
        self.disable_button.setStyleSheet(f"QPushButton {{ border-color: {CP_RED}; color: {CP_RED}; }}")
        self.disable_button.clicked.connect(self.disable_password_login)
        box.addWidget(self.disable_button, alignment=Qt.AlignmentFlag.AlignRight)

    def build_footer(self) -> None:
        footer = QLabel(
            "LOCAL NETWORK ONLY  •  Windows inbound SSH is restricted to the local subnet. "
            "A router DHCP reservation can keep this PC's LAN address stable."
        )
        footer.setWordWrap(True)
        footer.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt; padding-top: 5px;")
        self.layout.addWidget(footer)

    def refresh_pc_info(self) -> None:
        self.username = getpass.getuser()
        self.ip_address = get_lan_ip()
        self.pc_info.setText(
            f"PC name: {socket.gethostname()}\n"
            f"Windows user: {self.username}\n"
            f"LAN IP: {self.ip_address or 'not detected'}\n"
            "SSH port: 22"
        )
        self.test_command.setPlainText(
            f"ssh -i ~/.ssh/id_ed25519_windows_pc -p 22 {self.username}@{self.ip_address or '<pc-ip>'}"
        )
        service = run_powershell(
            "$s = Get-Service sshd -ErrorAction SilentlyContinue; "
            "if ($s) { \"$($s.Status)|$($s.StartType)\" } else { 'Missing' }"
        )
        if service.startswith("Running"):
            self.service_status.setText("SSH service: RUNNING")
            self.service_status.setStyleSheet(f"color: {CP_GREEN};")
        elif service.startswith("Stopped"):
            self.service_status.setText("SSH service: STOPPED")
            self.service_status.setStyleSheet(f"color: {CP_RED};")
        else:
            self.service_status.setText("SSH service: not detected")
            self.service_status.setStyleSheet(f"color: {CP_RED};")
        firewall = run_powershell(
            "$r = Get-NetFirewallRule -Name 'SSHSetupWizard-In-TCP' -ErrorAction SilentlyContinue; "
            "if ($r -and $r.Enabled) { 'READY' } else { 'NOT PREPARED' }"
        )
        self.firewall_status.setText(f"Firewall: {firewall or 'unknown'}")
        self.firewall_status.setStyleSheet(f"color: {CP_GREEN if firewall == 'READY' else CP_SUBTEXT};")

    def invoke_admin_action(self, action: str, public_key: str = "") -> bool:
        key_b64 = base64.b64encode(public_key.encode("utf-8")).decode("ascii") if public_key else ""
        script_path = str(ADMIN_SCRIPT).replace("'", "''")
        username = self.username.replace("'", "''")
        command = f"& '{script_path}' -Action {action} -UserName '{username}'"
        if key_b64:
            command += f" -PublicKeyBase64 '{key_b64}'"
        completed = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
        log_path = Path(os.environ.get("TEMP", str(Path.home() / "AppData/Local/Temp"))) / "ssh-setup-wizard.log"
        log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        if completed.returncode != 0:
            QMessageBox.critical(
                self,
                "Setup did not complete",
                log_text.strip() or completed.stderr.strip() or "Administrator setup failed or was cancelled.",
            )
            return False
        QMessageBox.information(self, "Setup complete", log_text.strip() or "The Windows SSH setup completed.")
        self.refresh_pc_info()
        return True

    def prepare_server(self) -> None:
        self.invoke_admin_action("Prepare")

    def install_key(self) -> None:
        public_key = self.public_key.toPlainText().strip()
        match = re.fullmatch(
            r"(ssh-ed25519|ecdsa-sha2-nistp256|ssh-rsa)\s+([A-Za-z0-9+/=]+)(?:\s+[^\r\n]*)?",
            public_key,
        )
        if not match:
            QMessageBox.warning(self, "Public key needed", "Paste the complete single-line .pub key from Android Termux.")
            return
        try:
            base64.b64decode(match.group(2), validate=True)
        except ValueError:
            QMessageBox.warning(self, "Invalid public key", "The public key data is not valid Base64.")
            return
        if self.invoke_admin_action("InstallKey", public_key):
            self.tested_checkbox.setChecked(False)

    def update_disable_button(self) -> None:
        self.disable_button.setEnabled(self.tested_checkbox.isChecked())

    def disable_password_login(self) -> None:
        answer = QMessageBox.warning(
            self,
            "Disable SSH password login?",
            "This turns off password authentication for SSH on Windows. Continue only if you already tested key login from Android.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.invoke_admin_action("DisablePassword")

    def copy_test_command(self) -> None:
        command = self.test_command.toPlainText().strip()
        if command:
            self.copy_text(command, "Android SSH test command copied.")

    def copy_text(self, text: str, message: str) -> None:
        QApplication.clipboard().setText(text)
        self.statusBar().showMessage(message, 4000)

    @staticmethod
    def restart_app() -> None:
        os.execv(sys.executable, [sys.executable] + sys.argv)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SshSetupWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
