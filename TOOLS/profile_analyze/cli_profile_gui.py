import sys
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QPlainTextEdit, QLabel,
    QGroupBox, QFormLayout, QSizePolicy, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QColor, QPalette, QKeyEvent

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
    QSplitter::handle {{
        background-color: {CP_DIM};
        height: 2px;
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
    "none": [],
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
# HELPERS
# ---------------------------------------------------------------------------
def build_profile_env(profile_name: str) -> tuple[dict, str]:
    """Build isolated env vars for the given profile. Returns (env, cwd)."""
    profiles_base_dir = Path.home() / "CLI_Profiles"
    profile_dir       = profiles_base_dir / profile_name
    appdata_roaming   = profile_dir / "AppData" / "Roaming"
    appdata_local     = profile_dir / "AppData" / "Local"
    programdata_dir   = profile_dir / "ProgramData"

    for d in (appdata_roaming, appdata_local, programdata_dir):
        d.mkdir(parents=True, exist_ok=True)

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

    return env, str(profile_dir)


# ---------------------------------------------------------------------------
# WORKER — streams a single command's output
# ---------------------------------------------------------------------------
class CommandWorker(QThread):
    log      = pyqtSignal(str)
    finished = pyqtSignal(int)   # exit code

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
            self.finished.emit(proc.returncode)
        except Exception as e:
            self.log.emit(f"[✗] {e}")
            self.finished.emit(1)


# ---------------------------------------------------------------------------
# WORKER — opens a shell window
# ---------------------------------------------------------------------------
class ShellWorker(QThread):
    log      = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, profile_name: str, shell: str, browser: str):
        super().__init__()
        self.profile_name = profile_name
        self.shell        = shell
        self.browser      = browser

    def run(self):
        try:
            env, cwd = build_profile_env(self.profile_name)

            if self.browser != "none":
                candidates = BROWSER_PATHS.get(self.browser, [])
                exe = next((p for p in candidates if p and p.exists()), None)
                if exe:
                    self.log.emit(f"[+] Opening {self.browser.capitalize()} (your default profile)...")
                    subprocess.Popen(
                        [str(exe)],
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    self.log.emit(f"[!] {self.browser} not found — skipping browser.")

            self.log.emit(f"[+] Shell window: {self.shell}")
            if self.shell == "cmd":
                subprocess.run(["cmd.exe", "/k", f"title Profile: {self.profile_name}"],
                               env=env, cwd=cwd)
            elif self.shell == "powershell":
                subprocess.run(["powershell.exe", "-NoExit", "-Command",
                                f"$Host.UI.RawUI.WindowTitle = 'Profile: {self.profile_name}'"],
                               env=env, cwd=cwd)
            else:
                subprocess.run(["pwsh.exe", "-NoExit", "-Command",
                                f"$Host.UI.RawUI.WindowTitle = 'Profile: {self.profile_name}'"],
                               env=env, cwd=cwd)

            self.log.emit(f"[✓] Shell closed.")
            self.finished.emit(True)
        except FileNotFoundError as e:
            self.log.emit(f"[✗] Shell not found: {e}")
            self.finished.emit(False)
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
        self.setMinimumSize(620, 580)
        self.resize(740, 660)
        self.setStyleSheet(GLOBAL_QSS)

        self._cmd_worker:   CommandWorker | None = None
        self._shell_worker: ShellWorker   | None = None
        self._active_env:   dict | None          = None
        self._active_cwd:   str  | None          = None
        self._active_name:  str                  = ""
        self._history:      list[str]            = []
        self._hist_idx:     int                  = -1

        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(8)

        # Header
        hdr = QLabel("◈  CLI  PROFILE  LAUNCHER  ◈")
        hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hdr.setStyleSheet(f"color:{CP_YELLOW}; font-size:13pt; font-weight:bold; letter-spacing:3px;")
        root.addWidget(hdr)

        div = QLabel("─" * 90)
        div.setAlignment(Qt.AlignmentFlag.AlignCenter)
        div.setStyleSheet(f"color:{CP_DIM}; font-size:7pt;")
        root.addWidget(div)

        # ── Profile config (compact) ─────────────────────────────────────
        cfg_grp = QGroupBox("PROFILE")
        cfg_row = QHBoxLayout()
        cfg_row.setContentsMargins(10, 14, 10, 10)
        cfg_row.setSpacing(10)

        cfg_row.addWidget(self._lbl("NAME:"))
        self.profile_input = QLineEdit()
        self.profile_input.setPlaceholderText("work / personal / client-x")
        self.profile_input.setClearButtonEnabled(True)
        self.profile_input.setMinimumWidth(160)
        cfg_row.addWidget(self.profile_input, stretch=3)

        cfg_row.addWidget(self._lbl("SHELL:"))
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["pwsh", "cmd", "powershell"])
        self.shell_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_row.addWidget(self.shell_combo, stretch=1)

        cfg_row.addWidget(self._lbl("BROWSER:"))
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(["none", "chrome", "helium"])
        self.browser_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        cfg_row.addWidget(self.browser_combo, stretch=1)

        cfg_grp.setLayout(cfg_row)
        root.addWidget(cfg_grp)

        # ── Command runner ───────────────────────────────────────────────
        cmd_grp = QGroupBox("RUN COMMAND")
        cmd_outer = QVBoxLayout()
        cmd_outer.setContentsMargins(10, 14, 10, 10)
        cmd_outer.setSpacing(8)

        # Input row
        cmd_row = QHBoxLayout()
        cmd_row.setSpacing(6)

        self.prompt_label = QLabel("$")
        self.prompt_label.setStyleSheet(f"color:{CP_GREEN}; font-size:13pt; font-weight:bold; background:transparent;")
        cmd_row.addWidget(self.prompt_label)

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("codex  |  gemini  |  aws s3 ls  |  gh auth status  ...")
        self.cmd_input.setMinimumHeight(34)
        self.cmd_input.setStyleSheet(f"""
            QLineEdit {{
                background-color:{CP_PANEL}; color:{CP_GREEN};
                border:1px solid {CP_DIM}; padding:4px 8px; font-size:11pt;
            }}
            QLineEdit:focus {{ border:1px solid {CP_GREEN}; }}
        """)
        self.cmd_input.returnPressed.connect(self._run_command)
        self.cmd_input.installEventFilter(self)
        cmd_row.addWidget(self.cmd_input, stretch=1)

        self.run_btn = QPushButton("▶  RUN")
        self.run_btn.setMinimumHeight(34)
        self.run_btn.setMinimumWidth(90)
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.setStyleSheet(f"""
            QPushButton {{
                background-color:{CP_DIM}; border:1px solid {CP_GREEN};
                color:{CP_GREEN}; font-weight:bold; font-size:11pt;
            }}
            QPushButton:hover {{ border:1px solid {CP_YELLOW}; color:{CP_YELLOW}; }}
            QPushButton:pressed {{ background-color:{CP_GREEN}; color:black; }}
            QPushButton:disabled {{ background-color:#1a1a1a; color:{CP_DIM}; border:1px solid #1e1e1e; }}
        """)
        self.run_btn.clicked.connect(self._run_command)
        cmd_row.addWidget(self.run_btn)

        cmd_outer.addLayout(cmd_row)

        # Status row
        status_row = QHBoxLayout()
        self.active_label = QLabel("◌  No profile active  —  enter name above and click ACTIVATE")
        self.active_label.setStyleSheet(f"color:{CP_DIM}; font-size:8pt;")
        status_row.addWidget(self.active_label, stretch=1)

        self.activate_btn = QPushButton("⚡ ACTIVATE")
        self.activate_btn.setMinimumHeight(28)
        self.activate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.activate_btn.setToolTip("Load profile env vars so RUN uses them (no shell window)")
        self.activate_btn.clicked.connect(self._activate)
        status_row.addWidget(self.activate_btn)

        self.shell_btn = QPushButton("⧉ OPEN SHELL")
        self.shell_btn.setMinimumHeight(28)
        self.shell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.shell_btn.setToolTip("Open an isolated shell window for this profile")
        self.shell_btn.clicked.connect(self._open_shell)
        status_row.addWidget(self.shell_btn)

        cmd_outer.addLayout(status_row)
        cmd_grp.setLayout(cmd_outer)
        root.addWidget(cmd_grp)

        # ── Output log ───────────────────────────────────────────────────
        log_grp = QGroupBox("OUTPUT")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(8, 12, 8, 8)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(240)
        self.log_output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color:{CP_PANEL}; color:{CP_GREEN};
                border:1px solid {CP_DIM}; font-family:'Consolas'; font-size:9pt; padding:6px;
            }}
        """)
        self.log_output.setPlaceholderText("// output appears here...")
        log_layout.addWidget(self.log_output)
        log_grp.setLayout(log_layout)
        root.addWidget(log_grp, stretch=1)

        # ── Bottom bar ────────────────────────────────────────────────────
        bot = QHBoxLayout()
        self.status_label = QLabel("● READY")
        self.status_label.setStyleSheet(f"color:{CP_GREEN}; font-size:8pt;")
        bot.addWidget(self.status_label)
        bot.addStretch()

        clear_btn = QPushButton("⌫ CLEAR")
        clear_btn.setMinimumHeight(26)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.log_output.clear)

        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setMinimumHeight(26)
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))

        bot.addWidget(clear_btn)
        bot.addWidget(restart_btn)
        root.addLayout(bot)

        # Focus
        self.profile_input.setFocus()

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet(f"color:{CP_TEXT}; font-weight:bold; background:transparent;")
        return l

    def _log(self, msg: str):
        self.log_output.appendPlainText(msg)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def _set_status(self, text: str, color: str):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color:{color}; font-size:8pt;")

    def _validate_name(self) -> str | None:
        name = self.profile_input.text().strip()
        if not name:
            self._log("[!] Enter a profile name.")
            return None
        if any(c in name for c in r'\/:*?"<>|'):
            self._log("[!] Profile name has invalid characters.")
            return None
        return name

    # ── Activate ────────────────────────────────────────────────────────────
    def _activate(self):
        name = self._validate_name()
        if not name:
            return
        env, cwd = build_profile_env(name)
        self._active_env  = env
        self._active_cwd  = cwd
        self._active_name = name
        self.active_label.setText(f"◉  {name}  →  {cwd}")
        self.active_label.setStyleSheet(f"color:{CP_GREEN}; font-size:8pt;")
        self._log(f"[⚡] Activated: {name}")
        self._log(f"     Path: {cwd}")
        self.cmd_input.setFocus()

    # ── Open shell window ───────────────────────────────────────────────────
    def _open_shell(self):
        name = self._validate_name()
        if not name:
            return
        if self._shell_worker and self._shell_worker.isRunning():
            self._log("[!] A shell is already open.")
            return
        shell   = self.shell_combo.currentText()
        browser = self.browser_combo.currentText()
        self._log(f"\n[⧉] Opening shell for '{name}'  ({shell})...")
        self._shell_worker = ShellWorker(name, shell, browser)
        self._shell_worker.log.connect(self._log)
        self._shell_worker.finished.connect(lambda ok: self._set_status("● READY", CP_GREEN))
        self._set_status("● SHELL OPEN", CP_YELLOW)
        self._shell_worker.start()

    # ── Run command ─────────────────────────────────────────────────────────
    def _run_command(self):
        if self._cmd_worker and self._cmd_worker.isRunning():
            self._log("[!] Already running a command.")
            return

        # Auto-activate if no profile is loaded yet
        if not self._active_env:
            name = self._validate_name()
            if not name:
                return
            self._activate()

        cmd = self.cmd_input.text().strip()
        if not cmd:
            return

        if not self._history or self._history[-1] != cmd:
            self._history.append(cmd)
        self._hist_idx = -1
        self.cmd_input.clear()

        # Open browser alongside the first command if selected
        browser = self.browser_combo.currentText()
        if browser != "none":
            candidates = BROWSER_PATHS.get(browser, [])
            exe = next((p for p in candidates if p and p.exists()), None)
            if exe:
                self._log(f"[+] Opening {browser.capitalize()}...")
                subprocess.Popen(
                    [str(exe)],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                )
            # Reset browser to none so it only opens once per run
            self.browser_combo.setCurrentText("none")

        self._log(f"\n$ {cmd}")
        self.run_btn.setEnabled(False)
        self._set_status("● RUNNING", CP_YELLOW)

        self._cmd_worker = CommandWorker(cmd, self._active_env, self._active_cwd)
        self._cmd_worker.log.connect(self._log)
        self._cmd_worker.finished.connect(self._on_cmd_done)
        self._cmd_worker.start()

    def _on_cmd_done(self, code: int):
        self.run_btn.setEnabled(True)
        self.cmd_input.setFocus()
        if code == 0:
            self._set_status("● READY", CP_GREEN)
        else:
            self._set_status(f"● EXIT {code}", CP_RED)

    # ── ↑↓ history ──────────────────────────────────────────────────────────
    def eventFilter(self, obj, event):
        if obj is self.cmd_input and event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Up and self._history:
                self._hist_idx = (len(self._history) - 1
                                  if self._hist_idx == -1
                                  else max(0, self._hist_idx - 1))
                self.cmd_input.setText(self._history[self._hist_idx])
                return True
            if key == Qt.Key.Key_Down and self._history:
                if self._hist_idx == -1 or self._hist_idx >= len(self._history) - 1:
                    self._hist_idx = -1
                    self.cmd_input.clear()
                else:
                    self._hist_idx += 1
                    self.cmd_input.setText(self._history[self._hist_idx])
                return True
        return super().eventFilter(obj, event)


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

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
