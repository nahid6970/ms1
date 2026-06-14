import sys
import os
import wave
import threading
import time
import numpy as np
import soundcard as sc
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QComboBox, QGroupBox, QProgressBar,
    QFileDialog, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont

# ── Palette ──────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

SAMPLERATE = 48000
CHANNELS   = 2
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
QComboBox QAbstractItemView {{ background: {CP_PANEL}; color: {CP_CYAN}; selection-background-color: {CP_CYAN}; selection-color: #000; }}
QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
QProgressBar {{
    background: {CP_PANEL}; border: 1px solid {CP_DIM}; height: 6px; text-align: center;
}}
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

# ── Recorder signals ─────────────────────────────────────────────────────────
class RecorderSignals(QObject):
    level_sys = pyqtSignal(float)   # 0.0-1.0
    level_mic = pyqtSignal(float)
    stopped   = pyqtSignal(str)     # output path

# ── Recording worker ──────────────────────────────────────────────────────────
class Recorder:
    def __init__(self, out_path, sys_dev, mic_dev, record_sys, record_mic):
        self.out_path   = out_path
        self.sys_dev    = sys_dev
        self.mic_dev    = mic_dev
        self.record_sys = record_sys
        self.record_mic = record_mic
        self.signals    = RecorderSignals()
        self._stop      = threading.Event()

    def _rms(self, data: np.ndarray) -> float:
        if data.size == 0:
            return 0.0
        val = float(np.sqrt(np.mean(data.astype(np.float32) ** 2))) / 32768.0
        return min(val * 8, 1.0)

    def start(self):
        self._stop.clear()
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self._stop.set()

    def _run(self):
        frames_sys, frames_mic = [], []

        ctx_sys = self.sys_dev.recorder(samplerate=SAMPLERATE, channels=CHANNELS, blocksize=CHUNK) if self.record_sys else None
        ctx_mic = self.mic_dev.recorder(samplerate=SAMPLERATE, channels=CHANNELS, blocksize=CHUNK) if self.record_mic else None

        try:
            with (ctx_sys or _NullContext()) as rec_sys, \
                 (ctx_mic or _NullContext()) as rec_mic:
                while not self._stop.is_set():
                    if self.record_sys:
                        raw = rec_sys.record(numframes=CHUNK)        # float32, [-1,1]
                        pcm = (raw * 32767).astype(np.int16)
                        frames_sys.append(pcm.tobytes())
                        self.signals.level_sys.emit(float(np.sqrt(np.mean(raw ** 2))) * 4)
                    if self.record_mic:
                        raw = rec_mic.record(numframes=CHUNK)
                        pcm = (raw * 32767).astype(np.int16)
                        frames_mic.append(pcm.tobytes())
                        self.signals.level_mic.emit(float(np.sqrt(np.mean(raw ** 2))) * 4)
        except Exception as e:
            self.signals.stopped.emit(f"ERROR: {e}")
            return

        self._save(frames_sys, frames_mic)

    def _save(self, frames_sys, frames_mic):
        # Mix if both recorded, otherwise use whichever has data
        if frames_sys and frames_mic:
            arr_sys = np.frombuffer(b"".join(frames_sys), dtype=np.int16).astype(np.float32)
            arr_mic = np.frombuffer(b"".join(frames_mic), dtype=np.int16).astype(np.float32)
            n = min(len(arr_sys), len(arr_mic))
            mixed = np.clip((arr_sys[:n] + arr_mic[:n]) / 2, -32768, 32767).astype(np.int16)
            final = mixed.tobytes()
        elif frames_sys:
            final = b"".join(frames_sys)
        elif frames_mic:
            final = b"".join(frames_mic)
        else:
            self.signals.stopped.emit("Nothing recorded.")
            return

        with wave.open(self.out_path, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLERATE)
            wf.writeframes(final)

        self.signals.stopped.emit(self.out_path)


class _NullContext:
    """Dummy context manager when a source is disabled."""
    def __enter__(self): return self
    def __exit__(self, *_): pass
    def record(self, numframes=None): return np.zeros((numframes, CHANNELS), dtype=np.float32)


# ── Main Window ───────────────────────────────────────────────────────────────
class AudioRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("◈ AUDIO RECORDER")
        self.setFixedWidth(460)
        self.setStyleSheet(QSS)

        self._recorder: Recorder | None = None
        self._elapsed  = 0
        self._timer    = QTimer(self)
        self._timer.timeout.connect(self._tick)

        # enumerate devices once
        all_devs = sc.all_microphones(include_loopback=True)
        self._loopbacks = [d for d in all_devs if "loopback" in type(d).__name__.lower() or hasattr(d, '_isloopback')]
        self._mics      = [d for d in all_devs if d not in self._loopbacks]

        # fallback: split by name heuristic
        if not self._loopbacks:
            self._loopbacks = [d for d in all_devs if "loopback" in repr(d).lower() or "speaker" in repr(d).lower()]
            self._mics      = [d for d in all_devs if d not in self._loopbacks]

        self._build_ui()

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        # ── Title ──
        title = QLabel("▶  AUDIO  RECORDER")
        title.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {CP_CYAN}; letter-spacing: 3px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # ── System Sound ──
        grp_sys = QGroupBox("SYSTEM SOUND")
        sys_layout = QVBoxLayout(grp_sys)

        row_sys = QHBoxLayout()
        self.chk_sys = QCheckBox("Enable")
        self.chk_sys.setChecked(True)
        self.chk_sys.toggled.connect(lambda v: self.cmb_sys.setEnabled(v))
        row_sys.addWidget(self.chk_sys)

        self.cmb_sys = QComboBox()
        for d in self._loopbacks:
            self.cmb_sys.addItem(repr(d).replace("<Loopback ", "").replace(">", "").strip(), d)
        if not self._loopbacks:
            self.cmb_sys.addItem("No loopback device found")
            self.chk_sys.setChecked(False)
            self.chk_sys.setEnabled(False)
        row_sys.addWidget(self.cmb_sys, 1)
        sys_layout.addLayout(row_sys)

        self.bar_sys = QProgressBar()
        self.bar_sys.setRange(0, 100)
        self.bar_sys.setTextVisible(False)
        self.bar_sys.setFixedHeight(6)
        sys_layout.addWidget(self.bar_sys)
        layout.addWidget(grp_sys)

        # ── Microphone ──
        grp_mic = QGroupBox("MICROPHONE")
        mic_layout = QVBoxLayout(grp_mic)

        row_mic = QHBoxLayout()
        self.chk_mic = QCheckBox("Enable")
        self.chk_mic.setChecked(True)
        self.chk_mic.toggled.connect(lambda v: self.cmb_mic.setEnabled(v))
        row_mic.addWidget(self.chk_mic)

        self.cmb_mic = QComboBox()
        for d in self._mics:
            self.cmb_mic.addItem(repr(d).replace("<Microphone ", "").replace(">", "").strip(), d)
        if not self._mics:
            self.cmb_mic.addItem("No microphone found")
            self.chk_mic.setChecked(False)
            self.chk_mic.setEnabled(False)
        row_mic.addWidget(self.cmb_mic, 1)
        mic_layout.addLayout(row_mic)

        self.bar_mic = QProgressBar()
        self.bar_mic.setRange(0, 100)
        self.bar_mic.setTextVisible(False)
        self.bar_mic.setFixedHeight(6)
        mic_layout.addWidget(self.bar_mic)
        layout.addWidget(grp_mic)

        # ── Output ──
        grp_out = QGroupBox("OUTPUT")
        out_layout = QHBoxLayout(grp_out)
        self.lbl_out = QLabel("(auto-named in same folder)")
        self.lbl_out.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt;")
        self.lbl_out.setWordWrap(True)
        out_layout.addWidget(self.lbl_out, 1)
        btn_browse = QPushButton("BROWSE")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._browse)
        out_layout.addWidget(btn_browse)
        layout.addWidget(grp_out)
        self._out_path: str | None = None

        # ── Timer ──
        self.lbl_time = QLabel("00:00:00")
        self.lbl_time.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self.lbl_time.setStyleSheet(f"color: {CP_YELLOW};")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_time)

        # ── Controls ──
        btn_row = QHBoxLayout()
        self.btn_rec  = QPushButton("⏺  RECORD")
        self.btn_stop = QPushButton("⏹  STOP")
        self.btn_stop.setEnabled(False)
        self.btn_rec.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_rec.setStyleSheet(f"border-color: {CP_GREEN}; color: {CP_GREEN};")
        self.btn_stop.setStyleSheet(f"border-color: {CP_RED}; color: {CP_RED};")
        self.btn_rec.clicked.connect(self._start)
        self.btn_stop.clicked.connect(self._stop)
        btn_row.addWidget(self.btn_rec)
        btn_row.addWidget(self.btn_stop)
        layout.addLayout(btn_row)

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("READY")

    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save recording as", "", "WAV Files (*.wav)")
        if path:
            self._out_path = path
            self.lbl_out.setText(os.path.basename(path))
            self.lbl_out.setStyleSheet(f"color: {CP_CYAN}; font-size: 9pt;")

    def _resolve_out(self) -> str:
        if self._out_path:
            return self._out_path
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), f"recording_{ts}.wav")

    def _start(self):
        rec_sys = self.chk_sys.isChecked() and self.cmb_sys.count() > 0
        rec_mic = self.chk_mic.isChecked() and self.cmb_mic.count() > 0
        if not rec_sys and not rec_mic:
            self.statusBar().showMessage("Enable at least one source!")
            return

        sys_dev = self.cmb_sys.currentData() if rec_sys else None
        mic_dev = self.cmb_mic.currentData() if rec_mic else None

        out = self._resolve_out()
        self._recorder = Recorder(out, sys_dev, mic_dev, rec_sys, rec_mic)
        self._recorder.signals.level_sys.connect(lambda v: self.bar_sys.setValue(int(min(v, 1.0) * 100)))
        self._recorder.signals.level_mic.connect(lambda v: self.bar_mic.setValue(int(min(v, 1.0) * 100)))
        self._recorder.signals.stopped.connect(self._on_stopped)
        self._recorder.start()

        self._elapsed = 0
        self._timer.start(1000)
        self.btn_rec.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.chk_sys.setEnabled(False)
        self.chk_mic.setEnabled(False)
        self.statusBar().showMessage(f"● RECORDING → {os.path.basename(out)}")

    def _stop(self):
        if self._recorder:
            self._recorder.stop()
        self._timer.stop()
        self.btn_stop.setEnabled(False)
        self.statusBar().showMessage("Stopping…")

    def _tick(self):
        self._elapsed += 1
        h, r = divmod(self._elapsed, 3600)
        m, s = divmod(r, 60)
        self.lbl_time.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _on_stopped(self, result: str):
        self.bar_sys.setValue(0)
        self.bar_mic.setValue(0)
        self.btn_rec.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.chk_sys.setEnabled(True)
        self.chk_mic.setEnabled(True)
        self._recorder = None
        if result.startswith("ERROR"):
            self.statusBar().showMessage(result)
        else:
            self.statusBar().showMessage(f"✔ Saved: {result}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AudioRecorder()
    w.show()
    sys.exit(app.exec())
