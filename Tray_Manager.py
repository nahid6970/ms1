import sys
import os
import json
import subprocess
import threading
import time

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem, Menu

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout,
    QScrollArea, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "tray_settings.json")
UPLOAD_SCRIPT = os.path.join(BASE_DIR, "@Flask", "5002_upload_files", "upload_files.py")

# ── Cyberpunk Palette ────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

GLOBAL_QSS = f"""
QMainWindow, QDialog, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
    background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
}}
QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 0px; padding-top: 4px; font-weight: bold;
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }}
QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}
"""

# ── Settings helpers ─────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "upload_files": {
        "save_folder": os.path.join(os.path.expanduser("~"), "Desktop", "ShareFolder")
    }
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(data: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Process helpers ──────────────────────────────────────────────────────────
def is_process_running(name: str) -> bool:
    try:
        out = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {name}"', shell=True).decode()
        return name.lower() in out.lower()
    except Exception:
        return False

def is_flask_running(port: int = 5002) -> bool:
    try:
        out = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
        return str(port) in out
    except Exception:
        return False

# ── Tray icon drawing ────────────────────────────────────────────────────────
def make_tray_icon() -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dc  = ImageDraw.Draw(img)
    # Green glowing ball
    dc.ellipse([4, 4, 60, 60], fill="#00ff21", outline="#00cc18", width=2)
    dc.ellipse([16, 12, 30, 26], fill="#80ff90")  # highlight
    return img

# ── Qt signal bridge (cross-thread) ─────────────────────────────────────────
class Bridge(QObject):
    show_window = pyqtSignal()

# ── Script card widget ───────────────────────────────────────────────────────
class ScriptCard(QGroupBox):
    """One card per managed script inside the scroll area."""

    def __init__(self, title: str, status_fn, start_fn, stop_fn, settings_widget: QWidget | None = None):
        super().__init__()
        self._title      = title
        self._status_fn  = status_fn
        self._start_fn   = start_fn
        self._stop_fn    = stop_fn

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(8)

        # Header row: big coloured title + icon button
        hdr = QHBoxLayout()
        hdr.setSpacing(10)
        self._lbl = QLabel(title.upper())
        self._lbl.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self._lbl.setStyleSheet("font-size: 16pt; font-weight: bold; font-family: Consolas;")
        hdr.addWidget(self._lbl)

        self._btn = QPushButton()
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.setFixedSize(36, 36)
        self._btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; padding: 0; }"
            "QPushButton:hover { background: #1a1a1a; border-radius: 4px; }"
        )
        self._btn.clicked.connect(self._toggle)
        hdr.addWidget(self._btn)
        hdr.addStretch()
        root.addLayout(hdr)

        # Settings sub-widget (if any)
        if settings_widget:
            root.addWidget(settings_widget)

        self._running = None  # force first paint on refresh()
        self.refresh()

    @staticmethod
    def _make_btn_icon(running: bool):
        from PyQt6.QtGui import QPixmap, QIcon
        from io import BytesIO
        from PyQt6.QtCore import QSize
        size = 28
        img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        dc   = ImageDraw.Draw(img)
        if running:
            # Two vertical bars = stop, red
            dc.rectangle([5, 5, 10, size - 5], fill="#FF003C")
            dc.rectangle([size - 11, 5, size - 6, size - 5], fill="#FF003C")
        else:
            # Triangle = play, green
            dc.polygon([(5, 4), (5, size - 4), (size - 4, size // 2)], fill="#00ff21")
        buf = BytesIO()
        img.save(buf, format="PNG")
        px = QPixmap()
        px.loadFromData(buf.getvalue())
        return QIcon(px)

    def refresh(self):
        from PyQt6.QtCore import QSize
        running = self._status_fn()
        if running == self._running:
            return
        self._running = running
        color = CP_GREEN if running else CP_RED
        self._lbl.setStyleSheet(f"color: {color}; font-size: 16pt; font-weight: bold; font-family: Consolas;")
        self.setStyleSheet(f"QGroupBox {{ border: 1px solid {CP_DIM}; margin-top:0px; padding-top:4px; }}")
        self._btn.setIcon(self._make_btn_icon(running))
        self._btn.setIconSize(QSize(28, 28))
        self._btn.setToolTip("Stop" if running else "Start")

    def _toggle(self):
        if self._running:
            self._stop_fn()
        else:
            self._start_fn()
        time.sleep(0.4)
        self.refresh()

# ── Komorebi settings widget (none needed – just toggle) ─────────────────────
def komorebi_status():  return is_process_running("komorebi.exe")

def komorebi_start():
    subprocess.Popen(["komorebic", "start"], shell=True)

def komorebi_stop():
    subprocess.Popen(["komorebic", "stop"], shell=True)

# ── Upload-files settings widget ─────────────────────────────────────────────
class UploadSettings(QWidget):
    def __init__(self):
        super().__init__()
        self._settings = load_settings()
        form = QFormLayout(self)
        form.setContentsMargins(0, 4, 0, 4)
        form.setSpacing(6)

        row = QHBoxLayout()
        self._path = QLineEdit(self._settings["upload_files"]["save_folder"])
        self._path.setReadOnly(True)
        browse = QPushButton("…")
        browse.setFixedWidth(32)
        browse.setCursor(Qt.CursorShape.PointingHandCursor)
        browse.clicked.connect(self._browse)
        row.addWidget(self._path)
        row.addWidget(browse)

        save_btn = QPushButton("SAVE")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)

        form.addRow(QLabel("Save folder:"), row)
        form.addRow("", save_btn)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select save folder", self._path.text())
        if d:
            self._path.setText(d)

    def _save(self):
        self._settings["upload_files"]["save_folder"] = self._path.text()
        save_settings(self._settings)
        # Patch the running process's SHARE_FOLDER via a sidecar JSON — the
        # upload_files script will pick it up on restart.
        label = QLabel(" ✔ Saved")
        label.setStyleSheet(f"color: {CP_GREEN};")
        self.layout().addRow("", label)
        QTimer.singleShot(2000, label.deleteLater)

_upload_proc: subprocess.Popen | None = None

def upload_status():
    return is_flask_running(5002)

def upload_start():
    global _upload_proc
    if not upload_status():
        _upload_proc = subprocess.Popen(
            [sys.executable, UPLOAD_SCRIPT],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

def upload_stop():
    global _upload_proc
    # Kill by port
    try:
        out = subprocess.check_output("netstat -ano | findstr :5002", shell=True).decode()
        for line in out.splitlines():
            parts = line.split()
            if parts:
                pid = parts[-1]
                subprocess.run(["taskkill", "/PID", pid, "/F"], shell=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass
    if _upload_proc:
        try:
            _upload_proc.terminate()
        except Exception:
            pass
        _upload_proc = None

# ── Main window ──────────────────────────────────────────────────────────────
class TrayManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRAY MANAGER")
        self.resize(520, 480)
        self.setStyleSheet(GLOBAL_QSS)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # Title bar
        title = QLabel("◈  TRAY MANAGER")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CP_CYAN};")
        root.addWidget(title)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        self._cards_layout = QVBoxLayout(inner)
        self._cards_layout.setSpacing(10)
        self._cards_layout.addStretch()
        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        # Bottom bar
        bar = QHBoxLayout()
        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self._restart)
        bar.addStretch()
        bar.addWidget(restart_btn)
        root.addLayout(bar)

        # Build cards
        self._cards: list[ScriptCard] = []
        self._add_card(ScriptCard(
            title="Komorebi",
            status_fn=komorebi_status,
            start_fn=komorebi_start,
            stop_fn=komorebi_stop,
            settings_widget=None
        ))
        self._add_card(ScriptCard(
            title="Upload Files  (Flask :5002)",
            status_fn=upload_status,
            start_fn=upload_start,
            stop_fn=upload_stop,
            settings_widget=UploadSettings()
        ))

        # Refresh timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_all)
        self._timer.start(2000)

    def _add_card(self, card: ScriptCard):
        self._cards.append(card)
        # Insert before the trailing stretch
        self._cards_layout.insertWidget(self._cards_layout.count() - 1, card)

    def _refresh_all(self):
        for card in self._cards:
            card.refresh()

    def closeEvent(self, event):
        # Hide instead of close so the app keeps running
        event.ignore()
        self.hide()

    def _restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

# ── App entry ────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    bridge  = Bridge()
    window  = TrayManagerWindow()

    bridge.show_window.connect(lambda: (window.show(), window.raise_(), window.activateWindow()))

    # ── pystray tray icon ────────────────────────────────────────────────────
    def on_open(icon, item):
        bridge.show_window.emit()

    def on_quit(icon, item):
        icon.stop()
        app.quit()

    tray_icon = pystray.Icon(
        "tray_manager",
        make_tray_icon(),
        title="Tray Manager",
        menu=Menu(
            MenuItem("Open Manager", on_open, default=True),
            Menu.SEPARATOR,
            MenuItem("Exit", on_quit)
        )
    )

    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
