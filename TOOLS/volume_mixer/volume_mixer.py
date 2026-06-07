import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QScrollArea, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    from comtypes import CLSCTX_ALL
    PYCAW = True
except ImportError:
    PYCAW = False

# PALETTE
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

STYLESHEET = f"""
QMainWindow, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
    padding: 4px 10px; font-weight: bold; font-family: 'Consolas';
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QPushButton[muted="true"] {{ background-color: {CP_RED}; border: 1px solid {CP_RED}; color: white; }}
QPushButton[muted="true"]:hover {{ border: 1px solid #ff6680; color: #ff6680; }}
QSlider::groove:horizontal {{
    height: 4px; background: {CP_DIM}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {CP_CYAN}; width: 14px; height: 14px;
    margin: -5px 0; border-radius: 7px;
}}
QSlider::sub-page:horizontal {{ background: {CP_CYAN}; border-radius: 2px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
"""


def get_sessions():
    """Return list of (name, pid, volume_interface) tuples."""
    if not PYCAW:
        return []
    sessions = []
    for s in AudioUtilities.GetAllSessions():
        vol = s._ctl.QueryInterface(ISimpleAudioVolume)
        name = s.Process.name() if s.Process else "System Sounds"
        sessions.append((name, s.Process.pid if s.Process else 0, vol))
    return sessions


class SessionRow(QWidget):
    def __init__(self, name, vol_iface, parent=None):
        super().__init__(parent)
        self.vol = vol_iface
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        # App name
        lbl = QLabel(name[:28])
        lbl.setMinimumWidth(180)
        lbl.setStyleSheet(f"color: {CP_CYAN};")

        # Volume label
        self.vol_lbl = QLabel("100%")
        self.vol_lbl.setMinimumWidth(38)
        self.vol_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.vol_lbl.setStyleSheet(f"color: {CP_TEXT};")

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        current = int((self.vol.GetMasterVolume() or 0.0) * 100)
        self.slider.setValue(current)
        self.vol_lbl.setText(f"{current}%")
        self.slider.setMinimumWidth(200)
        self.slider.valueChanged.connect(self._on_volume)

        # Mute button
        self.mute_btn = QPushButton("MUTE")
        self.mute_btn.setFixedWidth(56)
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._sync_mute_btn()
        self.mute_btn.clicked.connect(self._toggle_mute)

        layout.addWidget(lbl)
        layout.addWidget(self.vol_lbl)
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.mute_btn)

    def _on_volume(self, val):
        self.vol.SetMasterVolume(val / 100.0, None)
        self.vol_lbl.setText(f"{val}%")

    def _toggle_mute(self):
        self.vol.SetMute(not self.vol.GetMute(), None)
        self._sync_mute_btn()

    def _sync_mute_btn(self):
        muted = bool(self.vol.GetMute())
        self.mute_btn.setProperty("muted", str(muted).lower())
        self.mute_btn.setText("MUTED" if muted else "MUTE")
        self.mute_btn.style().unpolish(self.mute_btn)
        self.mute_btn.style().polish(self.mute_btn)

    def refresh(self):
        """Pull current state from the audio session."""
        vol = int((self.vol.GetMasterVolume() or 0.0) * 100)
        if self.slider.value() != vol:
            self.slider.blockSignals(True)
            self.slider.setValue(vol)
            self.slider.blockSignals(False)
            self.vol_lbl.setText(f"{vol}%")
        self._sync_mute_btn()


class VolumeMixer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ VOLUME MIXER")
        self.resize(620, 400)
        self.setStyleSheet(STYLESHEET)
        self._rows = {}
        self._build_ui()
        self._populate()
        # Auto-refresh every 2s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("⚡ VOLUME MIXER")
        title.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CP_YELLOW};")
        hdr.addWidget(title)
        hdr.addStretch()

        refresh_btn = QPushButton("↻ REFRESH")
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.clicked.connect(self._populate)
        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))
        hdr.addWidget(refresh_btn)
        hdr.addWidget(restart_btn)
        root.addLayout(hdr)

        if not PYCAW:
            warn = QLabel("⚠  pycaw not installed — run:  pip install pycaw")
            warn.setStyleSheet(f"color: {CP_RED}; padding: 20px;")
            warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(warn)
            return

        # Scroll area for sessions
        self.grp = QGroupBox("AUDIO SESSIONS")
        self.sessions_layout = QVBoxLayout(self.grp)
        self.sessions_layout.setSpacing(2)

        scroll = QScrollArea()
        scroll.setWidget(self.grp)
        scroll.setWidgetResizable(True)
        root.addWidget(scroll)

    def _populate(self):
        if not PYCAW:
            return
        # Clear existing
        self._rows.clear()
        while self.sessions_layout.count():
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sessions = get_sessions()
        if not sessions:
            lbl = QLabel("No active audio sessions found.")
            lbl.setStyleSheet(f"color: {CP_DIM}; padding: 10px;")
            self.sessions_layout.addWidget(lbl)
            return

        for name, pid, vol in sessions:
            key = f"{name}_{pid}"
            row = SessionRow(name, vol)
            self._rows[key] = row
            self.sessions_layout.addWidget(row)
        self.sessions_layout.addStretch()

    def _refresh(self):
        for row in self._rows.values():
            try:
                row.refresh()
            except Exception:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = VolumeMixer()
    win.show()
    sys.exit(app.exec())
