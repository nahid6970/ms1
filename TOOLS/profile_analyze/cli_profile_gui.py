import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QPlainTextEdit, QLabel,
    QGroupBox, QFormLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

# ---------------------------------------------------------------------------
# CYBERPUNK THEME PALETTE
# ---------------------------------------------------------------------------
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

GLOBAL_QSS = f"""
    QMainWindow, QDialog {{
        background-color: {CP_BG};
    }}
    QWidget {{
        color: {CP_TEXT};
        font-family: 'Consolas';
        font-size: 10pt;
        background-color: {CP_BG};
    }}
    QLineEdit, QComboBox, QPlainTextEdit {{
        background-color: {CP_PANEL};
        color: {CP_CYAN};
        border: 1px solid {CP_DIM};
        padding: 4px;
        selection-background-color: {CP_CYAN};
        selection-color: #000000;
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        border: 1px solid {CP_CYAN};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}
    QComboBox::down-arrow {{
        width: 10px;
        height: 10px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {CP_PANEL};
        color: {CP_CYAN};
        border: 1px solid {CP_CYAN};
        selection-background-color: {CP_CYAN};
        selection-color: #000000;
    }}
    QPushButton {{
        background-color: {CP_DIM};
        border: 1px solid {CP_DIM};
        color: white;
        padding: 6px 14px;
        font-weight: bold;
        font-family: 'Consolas';
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
    QPushButton:disabled {{
        background-color: #1a1a1a;
        color: {CP_DIM};
        border: 1px solid #1e1e1e;
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
        padding: 0 6px;
    }}
    QLabel {{
        color: {CP_TEXT};
        background-color: transparent;
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
"""

# ---------------------------------------------------------------------------
# KNOWN BROWSER PATHS
# ---------------------------------------------------------------------------
BROWSER_PATHS = {
    "none": None,
    "chrome": [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ],
    "helium": [
        Path(os.environ.get("LOCALAPPDATA", "")) / "imput/Helium/Application/chrome.exe",
    ],
}

# ---------------------------------------------------------------------------
# WORKER THREAD — runs the shell so the GUI stays responsive
# ---------------------------------------------------------------------------
class ProfileWorker(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool)  # True = success

    def __init__(self, profile_name: str, shell: str, browser: str):
        super().__init__()
        self.profile_name = profile_name
        self.shell = shell
        self.browser = browser

    def run(self):
        try:
            profile_name = self.profile_name
            profiles_base_dir = Path.home() / "CLI_Profiles"
            profile_dir = profiles_base_dir / profile_name
            appdata_roaming = profile_dir / "AppData" / "Roaming"
            appdata_local   = profile_dir / "AppData" / "Local"

            appdata_roaming.mkdir(parents=True, exist_ok=True)
            appdata_local.mkdir(parents=True, exist_ok=True)

            self.log.emit(f"[+] Profile: {profile_name}")
            self.log.emit(f"[+] Path:    {profile_dir}")

            env = os.environ.copy()
            env["USERPROFILE"]   = str(profile_dir)
            env["HOMEDRIVE"]     = profile_dir.drive
            env["HOMEPATH"]      = str(profile_dir)[len(profile_dir.drive):]
            env["APPDATA"]       = str(appdata_roaming)
            env["LOCALAPPDATA"]  = str(appdata_local)
            env["HOME"]          = str(profile_dir)
            env["XDG_CONFIG_HOME"] = str(appdata_roaming)
            env["XDG_DATA_HOME"]   = str(appdata_local)

            programdata_dir = profile_dir / "ProgramData"
            programdata_dir.mkdir(parents=True, exist_ok=True)
            env["PROGRAMDATA"]    = str(programdata_dir)
            env["ALLUSERSPROFILE"] = str(programdata_dir)

            # Launch browser (no isolation — keeps default profile + extensions)
            if self.browser != "none":
                candidates = BROWSER_PATHS.get(self.browser, [])
                exe = next((p for p in candidates if p and p.exists()), None)
                if exe:
                    self.log.emit(f"[+] Launching {self.browser.capitalize()} (default profile)...")
                    subprocess.Popen(
                        [str(exe)],
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    self.log.emit(f"[!] Browser '{self.browser}' not found — skipping.")

            # Launch shell
            self.log.emit(f"[+] Launching shell: {self.shell}")
            if self.shell == "cmd":
                subprocess.run(
                    ["cmd.exe", "/k", f"title Profile: {profile_name}"],
                    env=env, cwd=str(profile_dir)
                )
            elif self.shell == "powershell":
                subprocess.run(
                    ["powershell.exe", "-NoExit", "-Command",
                     f"$Host.UI.RawUI.WindowTitle = 'Profile: {profile_name}'"],
                    env=env, cwd=str(profile_dir)
                )
            else:
                subprocess.run(
                    ["pwsh.exe", "-NoExit", "-Command",
                     f"$Host.UI.RawUI.WindowTitle = 'Profile: {profile_name}'"],
                    env=env, cwd=str(profile_dir)
                )

            self.log.emit(f"[✓] Shell session for '{profile_name}' closed.")
            self.finished.emit(True)

        except FileNotFoundError as e:
            self.log.emit(f"[✗] Shell not found: {e}")
            self.finished.emit(False)
        except Exception as e:
            self.log.emit(f"[✗] Error: {e}")
            self.finished.emit(False)


# ---------------------------------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------------------------------
class ProfileLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLI PROFILE LAUNCHER")
        self.setMinimumSize(560, 440)
        self.resize(620, 480)
        self.setStyleSheet(GLOBAL_QSS)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # ── HEADER ──────────────────────────────────────────────────────────
        header = QLabel("◈  CLI  PROFILE  LAUNCHER  ◈")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {CP_YELLOW}; font-size: 13pt; font-weight: bold; letter-spacing: 3px;")
        root.addWidget(header)

        divider = QLabel("─" * 80)
        divider.setStyleSheet(f"color: {CP_DIM}; font-size: 7pt;")
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(divider)

        # ── CONFIG GROUP ─────────────────────────────────────────────────────
        grp = QGroupBox("PROFILE CONFIG")
        form = QFormLayout()
        form.setSpacing(10)
        form.setContentsMargins(12, 16, 12, 12)

        # Profile name
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("e.g. work, personal, client-x")
        self.profile_input.setClearButtonEnabled(True)
        form.addRow(self._label("PROFILE NAME:"), self.profile_input)

        # Shell selector
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["pwsh", "cmd", "powershell"])
        self.shell_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        form.addRow(self._label("SHELL:"), self.shell_combo)

        # Browser selector
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["none", "chrome", "helium"])
        self.browser_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        form.addRow(self._label("BROWSER:"), self.browser_combo)

        grp.setLayout(form)
        root.addWidget(grp)

        # ── LAUNCH BUTTON ─────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.launch_btn = QPushButton("▶  LAUNCH PROFILE")
        self.launch_btn.setMinimumHeight(38)
        self.launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.launch_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_CYAN};
                color: {CP_CYAN};
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #1a1a1a;
                border: 1px solid {CP_YELLOW};
                color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_CYAN};
                color: black;
            }}
            QPushButton:disabled {{
                background-color: #1a1a1a;
                color: {CP_DIM};
                border: 1px solid #1e1e1e;
            }}
        """)
        self.launch_btn.clicked.connect(self._launch)

        clear_btn = QPushButton("⌫  CLEAR LOG")
        clear_btn.setMinimumHeight(38)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._clear_log)

        restart_btn = QPushButton("↺  RESTART")
        restart_btn.setMinimumHeight(38)
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self._restart)

        btn_row.addWidget(self.launch_btn, stretch=3)
        btn_row.addWidget(clear_btn, stretch=1)
        btn_row.addWidget(restart_btn, stretch=1)
        root.addLayout(btn_row)

        # ── LOG OUTPUT ───────────────────────────────────────────────────
        log_grp = QGroupBox("OUTPUT LOG")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(8, 12, 8, 8)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(120)
        self.log_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {CP_PANEL};
                color: {CP_GREEN};
                border: 1px solid {CP_DIM};
                font-family: 'Consolas';
                font-size: 9pt;
                padding: 6px;
            }}
        """)
        self.log_output.setPlaceholderText("// awaiting launch...")

        log_layout.addWidget(self.log_output)
        log_grp.setLayout(log_layout)
        root.addWidget(log_grp)

        # ── STATUS BAR ───────────────────────────────────────────────────
        self.status_label = QLabel("● READY")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-size: 8pt;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(self.status_label)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold; background: transparent;")
        return lbl

    def _log(self, msg: str):
        self.log_output.appendPlainText(msg)

    def _clear_log(self):
        self.log_output.clear()

    def _restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # ── Launch ──────────────────────────────────────────────────────────────

    def _launch(self):
        profile_name = self.profile_input.text().strip()
        if not profile_name:
            self._log("[!] Profile name cannot be empty.")
            self.status_label.setText("● ERROR: no profile name")
            self.status_label.setStyleSheet(f"color: {CP_RED}; font-size: 8pt;")
            return

        # Sanitize: no spaces or path separators
        if any(c in profile_name for c in r'\/:*?"<>|'):
            self._log("[!] Profile name contains invalid characters.")
            return

        shell   = self.shell_combo.currentText()
        browser = self.browser_combo.currentText()

        self._log(f"\n{'─'*48}")
        self._log(f"  Activating profile: {profile_name}")
        self._log(f"  Shell: {shell}  |  Browser: {browser}")
        self._log(f"{'─'*48}")

        self.launch_btn.setEnabled(False)
        self.status_label.setText("● RUNNING")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-size: 8pt;")

        self._worker = ProfileWorker(profile_name, shell, browser)
        self._worker.log.connect(self._log)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, success: bool):
        self.launch_btn.setEnabled(True)
        if success:
            self.status_label.setText("● READY")
            self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-size: 8pt;")
        else:
            self.status_label.setText("● ERROR")
            self.status_label.setStyleSheet(f"color: {CP_RED}; font-size: 8pt;")


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette baseline so native widgets inherit correctly
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor(CP_BG))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor(CP_TEXT))
    palette.setColor(QPalette.ColorRole.Base,            QColor(CP_PANEL))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor(CP_PANEL))
    palette.setColor(QPalette.ColorRole.Text,            QColor(CP_CYAN))
    palette.setColor(QPalette.ColorRole.Button,          QColor(CP_DIM))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor(CP_TEXT))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor(CP_CYAN))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    app.setPalette(palette)

    window = ProfileLauncher()
    window.show()
    sys.exit(app.exec())
