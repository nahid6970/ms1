import sys, os
# 1. Add the absolute path to the folder containing install_deps.py
UTILITY_PATH = r"C:\@delta\ms1"
if UTILITY_PATH not in sys.path: sys.path.append(UTILITY_PATH)

# 2. Import and run the bootstrap
import install_deps
install_deps.bootstrap(__file__)

import sys
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

try:
    from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    PYCAW = True
except ImportError:
    PYCAW = False

# PALETTE
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

STYLESHEET = f"""
QMainWindow, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QSlider::groove:horizontal {{ height: 3px; background: {CP_DIM}; border-radius: 1px; }}
QSlider::handle:horizontal {{
    background: {CP_CYAN}; width: 12px; height: 12px;
    margin: -5px 0; border-radius: 6px;
}}
QSlider::sub-page:horizontal {{ background: {CP_CYAN}; border-radius: 1px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: {CP_BG}; width: 8px; margin: 0px; }}
QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
"""


def get_sessions():
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
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        # Clickable name label — click to mute/unmute
        self.lbl = QLabel(name[:24])
        self.lbl.setFixedWidth(150)
        self.lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl.mousePressEvent = lambda _: self._toggle_mute()
        self._set_name_color(bool(self.vol.GetMute()))

        # Volume % label
        self.vol_lbl = QLabel("100%")
        self.vol_lbl.setFixedWidth(34)
        self.vol_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.vol_lbl.setStyleSheet(f"color: {CP_TEXT};")

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setFixedWidth(140)
        current = int((self.vol.GetMasterVolume() or 0.0) * 100)
        self.slider.setValue(current)
        self.vol_lbl.setText(f"{current}%")
        self.slider.valueChanged.connect(self._on_volume)

        layout.addWidget(self.lbl)
        layout.addWidget(self.vol_lbl)
        layout.addWidget(self.slider)

    def _set_name_color(self, muted):
        color = CP_RED if muted else CP_CYAN
        self.lbl.setStyleSheet(f"color: {color};")

    def _on_volume(self, val):
        self.vol.SetMasterVolume(val / 100.0, None)
        self.vol_lbl.setText(f"{val}%")

    def _toggle_mute(self):
        self.vol.SetMute(not self.vol.GetMute(), None)
        self._set_name_color(bool(self.vol.GetMute()))

    def refresh(self):
        vol = int((self.vol.GetMasterVolume() or 0.0) * 100)
        if self.slider.value() != vol:
            self.slider.blockSignals(True)
            self.slider.setValue(vol)
            self.slider.blockSignals(False)
            self.vol_lbl.setText(f"{vol}%")
        self._set_name_color(bool(self.vol.GetMute()))



class VolumeMixer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ VOLUME MIXER")
        self.setFixedWidth(420)
        self.setMaximumHeight(800)
        self.setStyleSheet(STYLESHEET)
        self._rows = {}
        self._build_ui()
        self._populate()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        hdr = QHBoxLayout()
        title = QLabel("⚡ VOLUME MIXER")
        title.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CP_YELLOW};")
        hdr.addWidget(title)
        root.addLayout(hdr)

        if not PYCAW:
            from PyQt6.QtWidgets import QLabel as L
            warn = L("⚠  pip install pycaw")
            warn.setStyleSheet(f"color: {CP_RED}; padding: 20px;")
            warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(warn)
            return

        self.grp = QGroupBox("AUDIO SESSIONS")
        self.sessions_layout = QVBoxLayout(self.grp)
        self.sessions_layout.setSpacing(1)
        root.addWidget(self.grp)

    def _populate(self):
        if not PYCAW:
            return
        self._rows.clear()
        while self.sessions_layout.count():
            item = self.sessions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        sessions = get_sessions()
        if not sessions:
            lbl = QLabel("No active audio sessions.")
            lbl.setStyleSheet(f"color: {CP_DIM}; padding: 10px;")
            self.sessions_layout.addWidget(lbl)
            return

        for name, pid, vol in sessions:
            row = SessionRow(name, vol)
            self._rows[f"{name}_{pid}"] = row
            self.sessions_layout.addWidget(row)
        self.sessions_layout.addStretch()
        QTimer.singleShot(0, self.adjustSize)

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
