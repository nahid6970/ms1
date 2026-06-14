import sys
import os
import json
import wave
import warnings
import threading
warnings.filterwarnings("ignore", category=RuntimeWarning)
import numpy as np
import soundcard as sc
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QComboBox, QGroupBox, QProgressBar,
    QFileDialog, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, QByteArray, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

# ── Palette ───────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

SAMPLERATE = 48000
CHUNK      = 1024

QSS = f"""
QMainWindow, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 12px; padding-top: 8px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QComboBox {{
    background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
}}
QComboBox QAbstractItemView {{ background: {CP_PANEL}; color: {CP_CYAN};
    selection-background-color: {CP_CYAN}; selection-color: #000; }}
QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
QProgressBar {{ background: {CP_PANEL}; border: 1px solid {CP_DIM}; text-align: center; }}
QProgressBar::chunk {{ background: {CP_CYAN}; }}
QPushButton {{
    background: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
    padding: 7px 18px; font-weight: bold;
}}
QPushButton:hover {{ background: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background: {CP_YELLOW}; color: #000; }}
QPushButton:disabled {{ color: #555; border-color: #2a2a2a; }}
QStatusBar {{ background: {CP_PANEL}; color: {CP_DIM}; font-size: 9pt; }}
"""

# ── SVG icons ─────────────────────────────────────────────────────────────────
def svg_icon(svg: str, size: int = 18) -> QIcon:
    r = QSvgRenderer(QByteArray(svg.encode()))
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    r.render(p)
    p.end()
    return QIcon(px)

ICON_REC  = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8" fill="#00ff21"/></svg>'
ICON_STOP = '<svg viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" fill="#FF003C"/></svg>'
ICON_DIR  = '<svg viewBox="0 0 24 24"><path d="M2 6a2 2 0 012-2h4l2 2h8a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" fill="#FCEE0A"/></svg>'

# ── Signals ───────────────────────────────────────────────────────────────────
class RecorderSignals(QObject):
    level_sys = pyqtSignal(float)
    level_mic = pyqtSignal(float)
    stopped   = pyqtSignal(str)

# ── Recorder ──────────────────────────────────────────────────────────────────
class Recorder:
    def __init__(self, out_path, sys_dev, mic_dev, record_sys, record_mic):
        self.out_path   = out_path
        self.sys_dev    = sys_dev
        self.mic_dev    = mic_dev
        self.record_sys = record_sys
        self.record_mic = record_mic
        self.signals    = RecorderSignals()
        self._stop      = threading.Event()

    def start(self):
        self._stop.clear()
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._stop.set()

    def _run(self):
        frames_sys, frames_mic = [], []
        sys_ch = self.sys_dev.channels if self.record_sys else 2
        mic_ch = self.mic_dev.channels if self.record_mic else 2

        ctx_sys = self.sys_dev.recorder(samplerate=SAMPLERATE, channels=sys_ch, blocksize=CHUNK) if self.record_sys else None
        ctx_mic = self.mic_dev.recorder(samplerate=SAMPLERATE, channels=mic_ch, blocksize=CHUNK) if self.record_mic else None

        try:
            with (ctx_sys or _Null(sys_ch)) as rs, (ctx_mic or _Null(mic_ch)) as rm:
                while not self._stop.is_set():
                    if self.record_sys:
                        raw = rs.record(numframes=CHUNK)
                        if raw.shape[1] == 1: raw = np.repeat(raw, 2, axis=1)
                        frames_sys.append((raw * 32767).astype(np.int16).tobytes())
                        self.signals.level_sys.emit(min(float(np.sqrt(np.mean(raw**2))) * 4, 1.0))
                    if self.record_mic:
                        raw = rm.record(numframes=CHUNK)
                        if raw.shape[1] == 1: raw = np.repeat(raw, 2, axis=1)
                        frames_mic.append((raw * 32767).astype(np.int16).tobytes())
                        self.signals.level_mic.emit(min(float(np.sqrt(np.mean(raw**2))) * 4, 1.0))
        except Exception as e:
            self.signals.stopped.emit(f"ERROR: {e}"); return

        self._save(frames_sys, frames_mic)

    def _save(self, fs, fm):
        if fs and fm:
            a = np.frombuffer(b"".join(fs), np.int16).astype(np.float32)
            b = np.frombuffer(b"".join(fm), np.int16).astype(np.float32)
            n = min(len(a), len(b))
            final = np.clip((a[:n] + b[:n]) / 2, -32768, 32767).astype(np.int16).tobytes()
        elif fs: final = b"".join(fs)
        elif fm: final = b"".join(fm)
        else: self.signals.stopped.emit("Nothing recorded."); return

        with wave.open(self.out_path, "wb") as wf:
            wf.setnchannels(2); wf.setsampwidth(2)
            wf.setframerate(SAMPLERATE); wf.writeframes(final)
        self.signals.stopped.emit(self.out_path)

class _Null:
    def __init__(self, ch=2): self._ch = ch
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def record(self, numframes=None): return np.zeros((numframes, self._ch), np.float32)

# ── Main Window ───────────────────────────────────────────────────────────────
class AudioRecorder(QMainWindow):
    SETTINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("◈ AUDIO RECORDER")
        self.setFixedWidth(520)
        self.setStyleSheet(QSS)

        self._recorder: Recorder | None = None
        self._elapsed = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        all_devs = sc.all_microphones(include_loopback=True)
        self._loopbacks = [d for d in all_devs if "loopback" in repr(d).lower() or "speaker" in repr(d).lower()]
        self._mics      = [d for d in all_devs if d not in self._loopbacks]

        self._cfg = self._load_settings()
        self._build_ui()
        self._apply_settings()

    # ── Settings ──────────────────────────────────────────────────────────────
    def _load_settings(self):
        try:
            with open(self.SETTINGS) as f: return json.load(f)
        except Exception: return {}

    def _save_settings(self):
        try:
            with open(self.SETTINGS, "w") as f:
                json.dump({
                    "sys_enabled": self.chk_sys.isChecked(),
                    "mic_enabled": self.chk_mic.isChecked(),
                    "sys_device":  self.cmb_sys.currentText(),
                    "mic_device":  self.cmb_mic.currentText(),
                    "save_dir":    self._save_dir,
                }, f, indent=2)
        except Exception: pass

    def _apply_settings(self):
        c = self._cfg
        if "save_dir" in c and os.path.isdir(c["save_dir"]):
            self._save_dir = c["save_dir"]
            self.lbl_dir.setText(self._save_dir)
        for key, chk in [("sys_enabled", self.chk_sys), ("mic_enabled", self.chk_mic)]:
            if key in c: chk.setChecked(c[key])
        for key, cmb in [("sys_device", self.cmb_sys), ("mic_device", self.cmb_mic)]:
            if key in c:
                idx = cmb.findText(c[key])
                if idx >= 0: cmb.setCurrentIndex(idx)

    def closeEvent(self, event):
        self._save_settings(); super().closeEvent(event)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QWidget(); self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setSpacing(10); layout.setContentsMargins(14, 14, 14, 14)

        # Title
        title = QLabel("▶  AUDIO  RECORDER")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{CP_CYAN}; letter-spacing:3px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # System sound
        grp_sys = QGroupBox("SYSTEM SOUND")
        sl = QVBoxLayout(grp_sys)
        row = QHBoxLayout()
        self.chk_sys = QCheckBox("Enable")
        self.chk_sys.setChecked(True)
        self.chk_sys.toggled.connect(lambda v: self.cmb_sys.setEnabled(v))
        row.addWidget(self.chk_sys)
        self.cmb_sys = QComboBox()
        for d in self._loopbacks:
            name = d.name
            label = f"{name}  [{d.channels}ch]"
            self.cmb_sys.addItem(label, d)
            self.cmb_sys.setItemData(self.cmb_sys.count()-1, repr(d), Qt.ItemDataRole.ToolTipRole)
        if not self._loopbacks:
            self.cmb_sys.addItem("No loopback device"); self.chk_sys.setChecked(False); self.chk_sys.setEnabled(False)
        row.addWidget(self.cmb_sys, 1); sl.addLayout(row)
        self.bar_sys = QProgressBar(); self.bar_sys.setRange(0,100); self.bar_sys.setTextVisible(False); self.bar_sys.setFixedHeight(6)
        sl.addWidget(self.bar_sys); layout.addWidget(grp_sys)

        # Microphone
        grp_mic = QGroupBox("MICROPHONE")
        ml = QVBoxLayout(grp_mic)
        row2 = QHBoxLayout()
        self.chk_mic = QCheckBox("Enable")
        self.chk_mic.setChecked(True)
        self.chk_mic.toggled.connect(lambda v: self.cmb_mic.setEnabled(v))
        row2.addWidget(self.chk_mic)
        self.cmb_mic = QComboBox()
        for d in self._mics:
            name = d.name
            label = f"{name}  [{d.channels}ch]"
            self.cmb_mic.addItem(label, d)
            self.cmb_mic.setItemData(self.cmb_mic.count()-1, repr(d), Qt.ItemDataRole.ToolTipRole)
            self.cmb_mic.setItemData(self.cmb_mic.count()-1, repr(d), Qt.ItemDataRole.ToolTipRole)
        if not self._mics:
            self.cmb_mic.addItem("No microphone"); self.chk_mic.setChecked(False); self.chk_mic.setEnabled(False)
        row2.addWidget(self.cmb_mic, 1); ml.addLayout(row2)
        self.bar_mic = QProgressBar(); self.bar_mic.setRange(0,100); self.bar_mic.setTextVisible(False); self.bar_mic.setFixedHeight(6)
        ml.addWidget(self.bar_mic); layout.addWidget(grp_mic)

        # Save directory
        grp_out = QGroupBox("SAVE DIRECTORY")
        ol = QHBoxLayout(grp_out)
        self._save_dir = os.path.dirname(os.path.abspath(__file__))
        self.lbl_dir = QLabel(self._save_dir)
        self.lbl_dir.setStyleSheet(f"color:{CP_CYAN}; font-size:9pt;")
        self.lbl_dir.setWordWrap(True)
        ol.addWidget(self.lbl_dir, 1)
        btn_browse = QPushButton()
        btn_browse.setIcon(svg_icon(ICON_DIR, 16))
        btn_browse.setFixedSize(32, 32)
        btn_browse.setToolTip("Browse")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse)
        self._btn_dir = btn_browse
        ol.addWidget(btn_browse)
        layout.addWidget(grp_out)

        # Timer
        self.lbl_time = QLabel("00:00:00")
        self.lbl_time.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        self.lbl_time.setStyleSheet(f"color:{CP_YELLOW};")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_time)

        # Record / Stop
        btn_row = QHBoxLayout()
        self.btn_rec = QPushButton("  RECORD")
        self.btn_rec.setIcon(svg_icon(ICON_REC, 16))
        self.btn_rec.setStyleSheet(f"border-color:{CP_GREEN}; color:{CP_GREEN};")
        self.btn_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rec.clicked.connect(self._start)
        self.btn_stop = QPushButton("  STOP")
        self.btn_stop.setIcon(svg_icon(ICON_STOP, 16))
        self.btn_stop.setStyleSheet(f"border-color:{CP_RED}; color:{CP_RED};")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.clicked.connect(self._stop)
        btn_row.addWidget(self.btn_rec); btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("READY")

    # ── Actions ───────────────────────────────────────────────────────────────
    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select save directory", self._save_dir,
                                              QFileDialog.Option.DontUseNativeDialog)
        if d:
            self._save_dir = d
            self.lbl_dir.setText(d)
            self._save_settings()

    def _resolve_out(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self._save_dir, f"recording_{ts}.wav")

    def _start(self):
        rec_sys = self.chk_sys.isChecked() and self.cmb_sys.count() > 0
        rec_mic = self.chk_mic.isChecked() and self.cmb_mic.count() > 0
        if not rec_sys and not rec_mic:
            self.statusBar().showMessage("Enable at least one source!"); return

        out = self._resolve_out()
        self._recorder = Recorder(out,
            self.cmb_sys.currentData() if rec_sys else None,
            self.cmb_mic.currentData() if rec_mic else None,
            rec_sys, rec_mic)
        self._recorder.signals.level_sys.connect(lambda v: self.bar_sys.setValue(int(v * 100)))
        self._recorder.signals.level_mic.connect(lambda v: self.bar_mic.setValue(int(v * 100)))
        self._recorder.signals.stopped.connect(self._on_stopped)
        self._recorder.start()

        self._elapsed = 0; self._timer.start(1000)
        self.btn_rec.setEnabled(False); self.btn_stop.setEnabled(True)
        self.chk_sys.setEnabled(False); self.chk_mic.setEnabled(False)
        self.statusBar().showMessage(f"● RECORDING → {os.path.basename(out)}")

    def _stop(self):
        if self._recorder: self._recorder.stop()
        self._timer.stop()
        self.btn_stop.setEnabled(False)
        self.statusBar().showMessage("Stopping…")

    def _tick(self):
        self._elapsed += 1
        h, r = divmod(self._elapsed, 3600); m, s = divmod(r, 60)
        self.lbl_time.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _on_stopped(self, result: str):
        self.bar_sys.setValue(0); self.bar_mic.setValue(0)
        self.btn_rec.setEnabled(True); self.btn_stop.setEnabled(False)
        self.chk_sys.setEnabled(True); self.chk_mic.setEnabled(True)
        self._recorder = None
        if result.startswith("ERROR"):
            self.statusBar().showMessage(result)
        else:
            self.statusBar().showMessage(f"✔ Saved: {result}")


if __name__ == "__main__":
    import ctypes
    ctypes.windll.ole32.CoInitializeEx(None, 0x2)
    devnull = open(os.devnull, "w")
    old_fd = os.dup(2); os.dup2(devnull.fileno(), 2)
    app = QApplication(sys.argv)
    os.dup2(old_fd, 2); os.close(old_fd); devnull.close()
    w = AudioRecorder()
    w.show()
    sys.exit(app.exec())
