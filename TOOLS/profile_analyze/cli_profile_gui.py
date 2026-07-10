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
# WORKER THREAD — streams output of a single command
# ---------------------------------------------------------------------------
class CommandWorker(QThread):
    log    = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, command: str, env: dict, cwd: str):
        super().__init__()
        self.command = command
        self.env     = env
        self.cwd     = cwd

    def run(self):
        try:
            proc = subprocess.Popen(
                self.command,
                shell=True,
                env=self.env,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for line in proc.stdout:
                self.log.emit(line.rstrip())
            proc.wait()
            if proc.returncode != 0:
                self.log.emit(f"[!] Exit code: {proc.returncode}")
            self.finished.emit(proc.returncode == 0)
        except Exception as e:
            self.log.emit(f"[✗] {e}")
            self.finished.emit(False)


# ---------------------------------------------------------------------------
# MAIN WINDOW
# ---------------------------------------------------------------------------
class ProfileLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CLI PROFILE LAUNCHER")
        self.setMinimumSize(560, 540)
        self.resize(680, 600)
        self.setStyleSheet(GLOBAL_QSS)
        self._worker     = None
        self._cmd_worker = None
        self._active_env = None   # set when profile is activated
        self._active_cwd = None
        self._cmd_history: list[str] = []
        self._hist_idx = -1
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
        self.log_output.setMinimumHeight(140)
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

        # ── COMMAND RUNNER ───────────────────────────────────────────────
        cmd_grp = QGroupBox("COMMAND RUNNER  [ activate a profile first ]")
        cmd_grp.setObjectName("cmd_grp")
        cmd_layout = QVBoxLayout()
        cmd_layout.setContentsMargins(8, 12, 8, 8)
        cmd_layout.setSpacing(6)

        cmd_row = QHBoxLayout()
        cmd_row.setSpacing(6)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g.  aws s3 ls   |   gh auth status   |   dir")
        self.cmd_input.setEnabled(False)
        self.cmd_input.returnPressed.connect(self._run_command)
        self.cmd_input.installEventFilter(self)   # ↑↓ history navigation

        self.run_btn = QPushButton("▶  RUN")
        self.run_btn.setMinimumHeight(30)
        self.run_btn.setEnabled(False)
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_GREEN};
                color: {CP_GREEN};
                font-weight: bold;
                padding: 4px 14px;
            }}
            QPushButton:hover {{
                border: 1px solid {CP_YELLOW};
                color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_GREEN};
                color: black;
            }}
            QPushButton:disabled {{
                background-color: #1a1a1a;
                color: {CP_DIM};
                border: 1px solid #1e1e1e;
            }}
        """)
        self.run_btn.clicked.connect(self._run_command)

        # Activate button — bakes the profile env without opening a shell window
        self.activate_btn = QPushButton("⚡  ACTIVATE")
        self.activate_btn.setMinimumHeight(30)
        self.activate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.activate_btn.setToolTip("Set up profile env vars for the command runner without opening a shell window")
        self.activate_btn.clicked.connect(self._activate_profile)

        cmd_row.addWidget(self.cmd_input, stretch=5)
        cmd_row.addWidget(self.run_btn, stretch=1)
        cmd_layout.addLayout(cmd_row)

        activate_row = QHBoxLayout()
        activate_row.setSpacing(6)
        self.active_label = QLabel("◌  No profile activated")
        self.active_label.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        activate_row.addWidget(self.active_label)
        activate_row.addStretch()
        activate_row.addWidget(self.activate_btn)
        cmd_layout.addLayout(activate_row)

        cmd_grp.setLayout(cmd_layout)
        root.addWidget(cmd_grp)

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
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def _clear_log(self):
        self.log_output.clear()

    def _restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # ── Activate profile (env only, no shell window) ─────────────────────

    def _activate_profile(self):
        profile_name = self.profile_input.text().strip()
        if not profile_name:
            self._log("[!] Enter a profile name first.")
            return
        if any(c in profile_name for c in r'\/:*?"<>|'):
            self._log("[!] Profile name contains invalid characters.")
            return

        profiles_base_dir = Path.home() / "CLI_Profiles"
        profile_dir = profiles_base_dir / profile_name
        appdata_roaming = profile_dir / "AppData" / "Roaming"
        appdata_local   = profile_dir / "AppData" / "Local"
        programdata_dir = profile_dir / "ProgramData"

        appdata_roaming.mkdir(parents=True, exist_ok=True)
        appdata_local.mkdir(parents=True, exist_ok=True)
        programdata_dir.mkdir(parents=True, exist_ok=True)

        env = os.environ.copy()
        env["USERPROFILE"]     = str(profile_dir)
        env["HOMEDRIVE"]       = profile_dir.drive
        env["HOMEPATH"]        = str(profile_dir)[len(profile_dir.drive):]
        env["APPDATA"]         = str(appdata_roaming)
        env["LOCALAPPDATA"]    = str(appdata_local)
        env["HOME"]            = str(profile_dir)
        env["XDG_CONFIG_HOME"] = str(appdata_roaming)
        env["XDG_DATA_HOME"]   = str(appdata_local)
        env["PROGRAMDATA"]     = str(programdata_dir)
        env["ALLUSERSPROFILE"] = str(programdata_dir)

        self._active_env = env
        self._active_cwd = str(profile_dir)

        self.cmd_input.setEnabled(True)
        self.run_btn.setEnabled(True)
        self.active_label.setText(f"◉  Active: {profile_name}  →  {profile_dir}")
        self.active_label.setStyleSheet(f"color: {CP_GREEN}; font-size: 8pt;")
        self._log(f"[⚡] Profile '{profile_name}' activated for command runner.")
        self._log(f"     CWD: {profile_dir}")
        self.cmd_input.setFocus()

    # ── Run a command ────────────────────────────────────────────────────

    def _run_command(self):
        if self._cmd_worker and self._cmd_worker.isRunning():
            self._log("[!] A command is already running.")
            return

        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        # Add to history (avoid consecutive duplicates)
        if not self._cmd_history or self._cmd_history[-1] != cmd:
            self._cmd_history.append(cmd)
        self._hist_idx = -1

        self.cmd_input.clear()
        self._log(f"\n> {cmd}")

        self.run_btn.setEnabled(False)
        self.cmd_input.setEnabled(False)

        self._cmd_worker = CommandWorker(cmd, self._active_env, self._active_cwd)
        self._cmd_worker.log.connect(self._log)
        self._cmd_worker.finished.connect(self._on_cmd_finished)
        self._cmd_worker.start()

    def _on_cmd_finished(self, success: bool):
        self.run_btn.setEnabled(True)
        self.cmd_input.setEnabled(True)
        self.cmd_input.setFocus()

    # ── ↑↓ command history in the input field ───────────────────────────

    def eventFilter(self, obj, event):
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        if obj is self.cmd_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Up and self._cmd_history:
                if self._hist_idx == -1:
                    self._hist_idx = len(self._cmd_history) - 1
                elif self._hist_idx > 0:
                    self._hist_idx -= 1
                self.cmd_input.setText(self._cmd_history[self._hist_idx])
                return True
            if key == Qt.Key.Key_Down and self._cmd_history:
                if self._hist_idx == -1 or self._hist_idx >= len(self._cmd_history) - 1:
                    self._hist_idx = -1
                    self.cmd_input.clear()
                else:
                    self._hist_idx += 1
                    self.cmd_input.setText(self._cmd_history[self._hist_idx])
                return True
        return super().eventFilter(obj, event)

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
