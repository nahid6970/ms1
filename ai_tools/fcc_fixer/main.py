"""FCC Fixer - a small Cyberpunk-themed diagnostic and repair GUI.

The application deliberately uses only the Python standard library and PyQt6.
It never prints or displays API-key values. Claude settings are backed up before
the optional Router-conflict repair is applied.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PyQt6.QtCore import QTimer, Qt, QUrl
from PyQt6.QtGui import QColor, QDesktopServices, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"


HOME = Path.home()
CLAUDE_SETTINGS = HOME / ".claude" / "settings.json"
FCC_ENV = HOME / ".fcc" / ".env"
FCC_LOG = HOME / ".fcc" / "logs" / "server.log"
CODEX_CONFIG = HOME / ".codex" / "config.toml"
CODEX_CATALOG = HOME / ".fcc" / "codex-model-catalog.json"

CLAUDE_ROUTER_KEYS = {
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_API_BASE_URL",
    "CLAUDE_AGENT_API_BASE_URL",
}


def local_proxy_url() -> str:
    """Return the browser-friendly FCC URL from the managed env file."""

    values = read_env_file(FCC_ENV)
    host = values.get("HOST", "127.0.0.1").strip() or "127.0.0.1"
    if host in {"0.0.0.0", "::", "[::]"}:
        host = "127.0.0.1"
    port = values.get("PORT", "8082").strip() or "8082"
    return f"http://{host}:{port}"


def read_env_file(path: Path) -> dict[str, str]:
    """Read simple dotenv assignments without exposing values in the UI."""

    result: dict[str, str] = {}
    if not path.is_file():
        return result
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        result[key.strip()] = value.strip().strip("'\"")
    return result


def json_is_valid(path: Path) -> tuple[bool, str]:
    if not path.is_file():
        return False, "missing"
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, str(exc)
    return True, "valid"


def health_check(url: str) -> tuple[bool, str]:
    endpoint = f"{url.rstrip('/')}/health"
    try:
        request = Request(endpoint, method="GET")
        with urlopen(request, timeout=1.5) as response:  # noqa: S310 - local URL
            body = response.read().decode("utf-8", errors="replace")
            if 200 <= response.status < 300:
                return True, f"HTTP {response.status} {body}"
            return False, f"HTTP {response.status}"
    except (OSError, URLError) as exc:
        return False, str(exc)


def port_is_open(url: str) -> bool:
    """Perform a lightweight TCP check for the local proxy port."""

    try:
        parsed = urlsplit(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 8082
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except (IndexError, OSError, ValueError):
        return False


def command_path(name: str) -> str:
    return shutil.which(name) or "not found"


def timestamped_backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}.backup-{stamp}{path.suffix}")
    shutil.copy2(path, backup)
    return backup


def write_json_atomically(path: Path, payload: object) -> None:
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    os.replace(temp_path, path)


class CyberButton(QPushButton):
    """Sharp-edged button styled after the CyberButton guide."""

    def __init__(self, text: str, *, accent: str = CP_YELLOW, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {CP_DIM};
                color: {CP_TEXT};
                border: 1px solid {CP_DIM};
                padding: 7px 10px;
                font-family: Consolas;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
                border: 1px solid {accent};
                color: {accent};
            }}
            QPushButton:pressed {{
                background-color: {accent};
                color: #050505;
            }}
            """
        )


class SettingsDialog(QDialog):
    """Extensible settings shell required by the theme guide."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("FCC FIXER // SETTINGS")
        self.setMinimumWidth(460)
        layout = QVBoxLayout(self)
        group = QGroupBox("APP SETTINGS")
        group_layout = QVBoxLayout(group)
        label = QLabel(
            "No local application settings are required yet.\n"
            "This panel is reserved for future FCC Fixer preferences."
        )
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {CP_SUBTEXT}; padding: 10px;")
        group_layout.addWidget(label)
        layout.addWidget(group)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FCC FIXER // Claude + Codex Recovery Console")
        self.resize(1180, 760)
        self.setMinimumSize(960, 620)
        self.apply_theme()
        self.build_ui()
        self.refresh_diagnostics()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_diagnostics)
        self.refresh_timer.start(5000)

    def apply_theme(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{
                color: {CP_TEXT};
                font-family: Consolas, monospace;
                font-size: 10pt;
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 12px;
                font-weight: bold;
                color: {CP_YELLOW};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
            }}
            QPlainTextEdit, QListWidget {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                selection-background-color: {CP_CYAN};
                selection-color: {CP_BG};
            }}
            QListWidget::item {{ padding: 7px; }}
            QListWidget::item:selected {{ background-color: #17363a; color: {CP_CYAN}; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QSplitter::handle {{ background-color: {CP_DIM}; }}
            """
        )

    def build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("FCC // RECOVERY CONSOLE")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-size: 18pt; font-weight: bold;")
        subtitle = QLabel("CLAUDE + CODEX LOCAL PROXY DIAGNOSTICS")
        subtitle.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        header_left = QVBoxLayout()
        header_left.addWidget(title)
        header_left.addWidget(subtitle)
        header.addLayout(header_left)
        header.addStretch()
        self.system_status = QLabel("● SCANNING")
        self.system_status.setStyleSheet(f"color: {CP_ORANGE}; font-weight: bold;")
        header.addWidget(self.system_status, alignment=Qt.AlignmentFlag.AlignTop)
        root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self.build_actions_panel())
        splitter.addWidget(self.build_monitor_panel())
        splitter.setSizes([300, 820])
        root.addWidget(splitter, stretch=1)

        footer = QHBoxLayout()
        self.footer_status = QLabel("Ready.")
        self.footer_status.setStyleSheet(f"color: {CP_SUBTEXT};")
        footer.addWidget(self.footer_status)
        footer.addStretch()
        restart = CyberButton("↺ RESTART", accent=CP_ORANGE)
        restart.clicked.connect(self.restart_app)
        settings = CyberButton("⚙ SETTINGS", accent=CP_CYAN)
        settings.clicked.connect(self.open_settings)
        footer.addWidget(settings)
        footer.addWidget(restart)
        root.addLayout(footer)

    def build_actions_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)

        actions = QGroupBox("ACTIONS")
        action_layout = QVBoxLayout(actions)
        self.refresh_button = CyberButton("⟳ REFRESH DIAGNOSTICS", accent=CP_CYAN)
        self.refresh_button.clicked.connect(self.refresh_diagnostics)
        action_layout.addWidget(self.refresh_button)

        start_server = CyberButton("▶ START FCC SERVER", accent=CP_GREEN)
        start_server.clicked.connect(self.start_server)
        action_layout.addWidget(start_server)

        claude_fix = CyberButton("⚡ FIX CLAUDE ROUTER CONFLICT", accent=CP_YELLOW)
        claude_fix.clicked.connect(self.fix_claude_router_conflict)
        action_layout.addWidget(claude_fix)

        open_claude = CyberButton("OPEN CLAUDE SETTINGS", accent=CP_CYAN)
        open_claude.clicked.connect(lambda: self.open_path(CLAUDE_SETTINGS))
        action_layout.addWidget(open_claude)

        open_codex = CyberButton("OPEN CODEX CONFIG", accent=CP_CYAN)
        open_codex.clicked.connect(lambda: self.open_path(CODEX_CONFIG))
        action_layout.addWidget(open_codex)

        open_env = CyberButton("OPEN FCC ENV", accent=CP_ORANGE)
        open_env.clicked.connect(lambda: self.open_path(FCC_ENV))
        action_layout.addWidget(open_env)

        commands = QGroupBox("QUICK COMMANDS")
        command_layout = QVBoxLayout(commands)
        command_layout.addWidget(QLabel("FCC Claude"))
        command_layout.addWidget(self.command_label("fcc-claude"))
        command_layout.addWidget(QLabel("FCC Codex"))
        command_layout.addWidget(self.command_label("fcc-codex"))
        command_layout.addWidget(QLabel("Normal OpenAI Codex"))
        command_layout.addWidget(self.command_label("codex"))

        layout.addWidget(actions)
        layout.addWidget(commands)
        layout.addStretch()
        return panel

    def command_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet(f"color: {CP_CYAN}; padding: 3px 0 7px 8px;")
        return label

    def build_monitor_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 0, 0, 0)

        overview = QGroupBox("SYSTEM STATUS")
        grid = QGridLayout(overview)
        self.status_values: dict[str, QLabel] = {}
        rows = [
            ("FCC endpoint", "endpoint"),
            ("FCC health", "health"),
            ("FCC server command", "server_cmd"),
            ("fcc-claude command", "claude_cmd"),
            ("fcc-codex command", "fcc_codex_cmd"),
            ("normal codex command", "codex_cmd"),
            ("Claude settings", "claude_settings"),
            ("Codex config", "codex_config"),
        ]
        for row, (caption, key) in enumerate(rows):
            name = QLabel(caption.upper())
            name.setStyleSheet(f"color: {CP_SUBTEXT};")
            value = QLabel("--")
            value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.status_values[key] = value
            grid.addWidget(name, row, 0)
            grid.addWidget(value, row, 1)
        grid.setColumnStretch(1, 1)

        model_group = QGroupBox("MODEL ROUTING SNAPSHOT")
        model_layout = QVBoxLayout(model_group)
        self.model_list = QListWidget()
        self.model_list.setMinimumHeight(150)
        model_layout.addWidget(self.model_list)

        log_group = QGroupBox("DIAGNOSTIC OUTPUT")
        log_layout = QVBoxLayout(log_group)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.output.setMinimumHeight(180)
        log_layout.addWidget(self.output)

        layout.addWidget(overview)
        layout.addWidget(model_group)
        layout.addWidget(log_group, stretch=1)
        return panel

    def set_status(self, key: str, value: str, color: str = CP_TEXT) -> None:
        label = self.status_values[key]
        label.setText(value)
        label.setStyleSheet(f"color: {color};")

    def refresh_diagnostics(self) -> None:
        url = local_proxy_url()
        healthy, health_detail = health_check(url)
        self.set_status("endpoint", url, CP_CYAN)
        self.set_status("health", "HEALTHY" if healthy else "OFFLINE", CP_GREEN if healthy else CP_RED)
        self.set_status("server_cmd", command_path("fcc-server"), CP_GREEN if shutil.which("fcc-server") else CP_RED)
        self.set_status("claude_cmd", command_path("fcc-claude"), CP_GREEN if shutil.which("fcc-claude") else CP_RED)
        self.set_status("fcc_codex_cmd", command_path("fcc-codex"), CP_GREEN if shutil.which("fcc-codex") else CP_RED)
        self.set_status("codex_cmd", command_path("codex"), CP_GREEN if shutil.which("codex") else CP_RED)

        valid, detail = json_is_valid(CLAUDE_SETTINGS)
        self.set_status("claude_settings", "VALID" if valid else f"{detail.upper()}", CP_GREEN if valid else CP_RED)
        self.set_status("codex_config", "PRESENT" if CODEX_CONFIG.is_file() else "MISSING", CP_GREEN if CODEX_CONFIG.is_file() else CP_ORANGE)

        env = read_env_file(FCC_ENV)
        self.model_list.clear()
        model_keys = ["MODEL", "MODEL_FABLE", "MODEL_OPUS", "MODEL_SONNET", "MODEL_HAIKU"]
        for key in model_keys:
            value = env.get(key, "").strip()
            if value:
                item = QListWidgetItem(f"{key:<12} {value}")
                item.setForeground(QColor(CP_GREEN if key == "MODEL" else CP_CYAN))
                self.model_list.addItem(item)
        if self.model_list.count() == 0:
            self.model_list.addItem("No MODEL entries found in .fcc/.env")

        warnings: list[str] = []
        if valid:
            try:
                settings = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))
                if "apiKeyHelper" in settings:
                    warnings.append("Claude: apiKeyHelper is still configured")
                settings_env = settings.get("env", {})
                router_keys = sorted(CLAUDE_ROUTER_KEYS.intersection(settings_env)) if isinstance(settings_env, dict) else []
                if router_keys:
                    warnings.append("Claude: old Router endpoint keys: " + ", ".join(router_keys))
            except (OSError, json.JSONDecodeError):
                warnings.append("Claude: settings could not be inspected")

        if CODEX_CONFIG.is_file():
            try:
                codex_text = CODEX_CONFIG.read_text(encoding="utf-8").lower()
                if any(token in codex_text for token in ("model_provider", "model_catalog_json", "gemini", "fcc")):
                    warnings.append("Codex: inspect config.toml for persistent FCC/provider overrides")
            except OSError:
                warnings.append("Codex: config.toml could not be read")

        output_lines = [
            f"Proxy health: {health_detail}",
            f"FCC env: {FCC_ENV}",
            f"Server log: {FCC_LOG if FCC_LOG.is_file() else 'not found'}",
            f"FCC catalog: {CODEX_CATALOG if CODEX_CATALOG.is_file() else 'not generated yet'}",
        ]
        if warnings:
            output_lines.append("\nWARNINGS:")
            output_lines.extend(f"- {warning}" for warning in warnings)
            self.system_status.setText("● ATTENTION")
            self.system_status.setStyleSheet(f"color: {CP_ORANGE}; font-weight: bold;")
        else:
            output_lines.append("\nNo common configuration conflicts detected.")
            self.system_status.setText("● SYSTEM READY")
            self.system_status.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
        self.output.setPlainText("\n".join(output_lines))
        self.footer_status.setText(datetime.now().strftime("Last scan: %Y-%m-%d %H:%M:%S"))

    def start_server(self) -> None:
        if port_is_open(local_proxy_url()):
            QMessageBox.information(self, "FCC SERVER", "FCC already has an open listening port.")
            self.refresh_diagnostics()
            return
        try:
            flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            subprocess.Popen(["fcc-server"], cwd=str(HOME), creationflags=flags)
            self.footer_status.setText("FCC server launch requested; scan will update automatically.")
        except OSError as exc:
            QMessageBox.critical(self, "FCC SERVER", f"Could not start fcc-server:\n{exc}")

    def fix_claude_router_conflict(self) -> None:
        if not CLAUDE_SETTINGS.is_file():
            QMessageBox.warning(self, "CLAUDE SETTINGS", f"File not found:\n{CLAUDE_SETTINGS}")
            return
        try:
            settings = json.loads(CLAUDE_SETTINGS.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            QMessageBox.critical(self, "CLAUDE SETTINGS", f"Cannot read valid JSON:\n{exc}")
            return

        env = settings.get("env")
        found = "apiKeyHelper" in settings
        if isinstance(env, dict):
            found = found or bool(CLAUDE_ROUTER_KEYS.intersection(env))
        if not found:
            QMessageBox.information(self, "CLAUDE SETTINGS", "No old Claude Code Router entries were found.")
            return

        answer = QMessageBox.question(
            self,
            "BACKUP AND REPAIR",
            "Back up settings.json and remove the old Router authentication/endpoint entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            backup = timestamped_backup(CLAUDE_SETTINGS)
            settings.pop("apiKeyHelper", None)
            if isinstance(env, dict):
                for key in CLAUDE_ROUTER_KEYS:
                    env.pop(key, None)
            write_json_atomically(CLAUDE_SETTINGS, settings)
        except (OSError, TypeError) as exc:
            QMessageBox.critical(self, "REPAIR FAILED", str(exc))
            return

        QMessageBox.information(
            self,
            "REPAIR COMPLETE",
            f"Removed the conflicting Router entries.\n\nBackup:\n{backup}\n\nRestart Claude Code for the change to apply.",
        )
        self.refresh_diagnostics()

    def open_path(self, path: Path) -> None:
        if not path.exists():
            QMessageBox.warning(self, "FILE NOT FOUND", str(path))
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):
            QMessageBox.warning(self, "OPEN FAILED", str(path))

    def open_settings(self) -> None:
        SettingsDialog(self).exec()

    def restart_app(self) -> None:
        os.execv(sys.executable, [sys.executable, *sys.argv])


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("FCC Fixer")
    app.setStyle("Fusion")
    app.setFont(QFont("Consolas", 10))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
