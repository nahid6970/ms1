# screen_recorder.py — Cyberpunk Screen Recorder
import sys, os, json, time, threading, subprocess, tempfile
import numpy as np
import mss
import pyaudio
import win32gui, win32con
from dataclasses import dataclass, asdict, field
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QFormLayout, QLineEdit,
    QSpinBox, QCheckBox, QDialog, QTabWidget, QFileDialog, QListWidget,
    QListWidgetItem, QRubberBand, QSizePolicy, QSlider, QMessageBox,
    QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QRect, QSize, QPoint, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QScreen, QPixmap, QIcon

# ── Palette ──────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"
CP_SUBTEXT= "#808080"

THEME = f"""
QMainWindow, QDialog {{
    background-color: {CP_BG};
}}
QWidget {{
    color: {CP_TEXT};
    font-family: 'Consolas';
    font-size: 10pt;
    background-color: {CP_BG};
}}
QTabWidget::pane {{
    border: 1px solid {CP_DIM};
    background: {CP_BG};
}}
QTabBar::tab {{
    background: {CP_PANEL};
    color: {CP_SUBTEXT};
    padding: 6px 14px;
    border: 1px solid {CP_DIM};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    color: {CP_YELLOW};
    border-color: {CP_YELLOW};
    background: {CP_BG};
}}
QLineEdit, QSpinBox, QComboBox, QTextEdit {{
    background-color: {CP_PANEL};
    color: {CP_CYAN};
    border: 1px solid {CP_DIM};
    padding: 4px;
    selection-background-color: {CP_CYAN};
    selection-color: #000;
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border: 1px solid {CP_CYAN};
}}
QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; border: none; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {CP_PANEL};
    color: {CP_CYAN};
    selection-background-color: {CP_CYAN};
    selection-color: #000;
    border: 1px solid {CP_DIM};
}}
QPushButton {{
    background-color: {CP_DIM};
    border: 1px solid {CP_DIM};
    color: white;
    padding: 6px 14px;
    font-weight: bold;
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
    color: {CP_SUBTEXT};
    border-color: {CP_DIM};
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
    padding: 0 5px;
}}
QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {CP_DIM};
    background: {CP_PANEL};
}}
QCheckBox::indicator:checked {{
    background: {CP_YELLOW};
    border-color: {CP_YELLOW};
}}
QListWidget {{
    background: {CP_PANEL};
    color: {CP_TEXT};
    border: 1px solid {CP_DIM};
}}
QListWidget::item:selected {{
    background: {CP_CYAN};
    color: #000;
}}
QScrollBar:vertical {{
    background: {CP_BG}; width: 8px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {CP_CYAN}; min-height: 20px; border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
QStatusBar {{
    background: {CP_PANEL};
    color: {CP_SUBTEXT};
    border-top: 1px solid {CP_DIM};
}}
QSlider::groove:horizontal {{
    height: 4px; background: {CP_DIM}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {CP_CYAN}; width: 12px; height: 12px;
    margin: -4px 0; border-radius: 6px;
}}
QSlider::sub-page:horizontal {{ background: {CP_CYAN}; border-radius: 2px; }}
"""

# ── Settings ──────────────────────────────────────────────────────────────────
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorder_settings.json")

@dataclass
class Settings:
    save_dir: str = os.path.join(os.path.expanduser("~"), "Videos")
    format: str = "mp4"
    fps: int = 30
    resolution: str = "Source"          # "Source" | "1920x1080" | "1280x720" | "854x480"
    video_bitrate: str = "8000k"
    audio_source: str = "None"          # sounddevice device name
    mic_source: str = "None"
    audio_bitrate: str = "192k"
    capture_mode: str = "fullscreen"    # fullscreen | area | window
    show_cursor: bool = True
    highlight_clicks: bool = False
    countdown: int = 3
    hotkey_start: str = "F9"
    hotkey_stop: str = "F10"
    encoder: str = "libx264"            # libx264 | libx265 | h264_nvenc | hevc_nvenc
    crf: int = 23
    preset: str = "fast"
    filename_template: str = "recording_%Y%m%d_%H%M%S"

def load_settings() -> Settings:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            s = Settings()
            for k, v in data.items():
                if hasattr(s, k):
                    setattr(s, k, v)
            return s
        except Exception:
            pass
    return Settings()

def save_settings(s: Settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(asdict(s), f, indent=2)


# ── Area Selector Overlay ─────────────────────────────────────────────────────
class AreaSelector(QWidget):
    """Full-screen transparent overlay; user drags to select a region."""
    area_selected = pyqtSignal(QRect)
    cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self._origin = QPoint()
        self._rect = QRect()
        self._selecting = False

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.cancelled.emit()
            self.close()

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._origin = e.pos()
            self._rect = QRect(self._origin, QSize())
            self._selecting = True

    def mouseMoveEvent(self, e):
        if self._selecting:
            self._rect = QRect(self._origin, e.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._selecting:
            self._selecting = False
            if self._rect.width() > 10 and self._rect.height() > 10:
                self.area_selected.emit(self._rect)
            else:
                self.cancelled.emit()
            self.close()

    def paintEvent(self, e):
        p = QPainter(self)
        # dark overlay
        p.fillRect(self.rect(), QColor(0, 0, 0, 120))
        if not self._rect.isNull():
            # cut out selected area
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            p.fillRect(self._rect, Qt.GlobalColor.transparent)
            p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            # cyan border
            pen = QPen(QColor(CP_CYAN), 2)
            p.setPen(pen)
            p.drawRect(self._rect)
            # size label
            p.setPen(QColor(CP_YELLOW))
            p.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            label = f"{self._rect.width()} × {self._rect.height()}"
            p.drawText(self._rect.bottomRight() + QPoint(6, -4), label)


# ── Window Picker Dialog ──────────────────────────────────────────────────────
class WindowPicker(QDialog):
    window_chosen = pyqtSignal(int)   # emits hwnd

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pick a Window")
        self.resize(480, 360)
        self.setStyleSheet(THEME)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a window to record:"))

        self.list = QListWidget()
        layout.addWidget(self.list)

        btn_row = QHBoxLayout()
        ok = QPushButton("SELECT")
        ok.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel = QPushButton("CANCEL")
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        layout.addLayout(btn_row)

        ok.clicked.connect(self._pick)
        cancel.clicked.connect(self.reject)
        self.list.itemDoubleClicked.connect(lambda _: self._pick())

        self._populate()

    def _populate(self):
        self._windows = []
        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and title.strip():
                    self._windows.append((hwnd, title))
        win32gui.EnumWindows(cb, None)
        for hwnd, title in self._windows:
            self.list.addItem(QListWidgetItem(f"[{hwnd}]  {title}"))

    def _pick(self):
        row = self.list.currentRow()
        if row >= 0:
            hwnd, _ = self._windows[row]
            self.window_chosen.emit(hwnd)
            self.accept()

    @staticmethod
    def get_window_rect(hwnd) -> QRect:
        try:
            rect = win32gui.GetWindowRect(hwnd)
            return QRect(rect[0], rect[1], rect[2]-rect[0], rect[3]-rect[1])
        except Exception:
            return QRect()


# ── Audio helpers ─────────────────────────────────────────────────────────────
def list_audio_devices():
    """Return list of (index, name, is_input) for all pyaudio devices."""
    pa = pyaudio.PyAudio()
    devices = []
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        devices.append((i, info["name"], info["maxInputChannels"] > 0))
    pa.terminate()
    return devices

def get_loopback_devices():
    """Return output devices that support loopback (WASAPI) for desktop audio."""
    import sounddevice as sd
    devs = []
    for d in sd.query_devices():
        if d["max_input_channels"] > 0 and "loopback" in d["name"].lower():
            devs.append(d["name"])
    return devs

def get_input_devices():
    """Return mic/input device names via sounddevice."""
    import sounddevice as sd
    return [d["name"] for d in sd.query_devices() if d["max_input_channels"] > 0]


# ── Recording Thread ──────────────────────────────────────────────────────────
class RecordingThread(QThread):
    status_update = pyqtSignal(str)
    finished_path = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, settings: Settings, capture_rect: QRect):
        super().__init__()
        self.settings = settings
        self.capture_rect = capture_rect   # screen coords
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()            # not paused initially

    def stop(self):
        self._stop_event.set()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def run(self):
        s = self.settings
        r = self.capture_rect

        # ── output path ──
        os.makedirs(s.save_dir, exist_ok=True)
        fname = time.strftime(s.filename_template) + "." + s.format
        out_path = os.path.join(s.save_dir, fname)

        # ── resolve output resolution ──
        if s.resolution == "Source":
            out_w, out_h = r.width(), r.height()
        else:
            out_w, out_h = map(int, s.resolution.split("x"))
        # ffmpeg wants even dimensions
        out_w += out_w % 2
        out_h += out_h % 2

        # ── build ffmpeg command ──
        vf = f"scale={out_w}:{out_h}"
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-pix_fmt", "bgr24",
            "-s", f"{r.width()}x{r.height()}",
            "-r", str(s.fps),
            "-i", "pipe:0",          # video from stdin
        ]

        has_audio = s.audio_source not in ("None", "")
        has_mic   = s.mic_source   not in ("None", "")

        audio_thread = None
        audio_pipe_r = audio_pipe_w = None

        if has_audio or has_mic:
            # create a named pipe / temp file for audio PCM
            audio_pipe_r, audio_pipe_w = os.pipe()
            cmd += [
                "-f", "s16le",
                "-ar", "44100",
                "-ac", "2",
                "-i", f"pipe:{audio_pipe_r}",
            ]

        cmd += [
            "-vf", vf,
            "-vcodec", s.encoder,
            "-b:v", s.video_bitrate,
            "-preset", s.preset,
        ]
        if s.encoder in ("libx264", "libx265"):
            cmd += ["-crf", str(s.crf)]
        if has_audio or has_mic:
            cmd += ["-acodec", "aac", "-b:a", s.audio_bitrate]
        else:
            cmd += ["-an"]
        cmd.append(out_path)

        try:
            extra_fds = {audio_pipe_r: audio_pipe_r} if (has_audio or has_mic) else {}
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=False,
            )
            if has_audio or has_mic:
                os.close(audio_pipe_r)   # child owns read end
                audio_thread = threading.Thread(
                    target=self._audio_worker,
                    args=(audio_pipe_w, s, has_audio, has_mic),
                    daemon=True
                )
                audio_thread.start()

            self._capture_loop(proc, r, s.fps)

            proc.stdin.close()
            proc.wait()

            if audio_pipe_w:
                try: os.close(audio_pipe_w)
                except OSError: pass

            if proc.returncode == 0:
                self.finished_path.emit(out_path)
            else:
                err = proc.stderr.read().decode(errors="replace")[-400:]
                self.error_occurred.emit(f"ffmpeg error:\n{err}")

        except Exception as ex:
            self.error_occurred.emit(str(ex))

    def _capture_loop(self, proc, r: QRect, fps: int):
        interval = 1.0 / fps
        mon = {"top": r.y(), "left": r.x(), "width": r.width(), "height": r.height()}
        with mss.mss() as sct:
            while not self._stop_event.is_set():
                t0 = time.perf_counter()
                self._pause_event.wait()
                if self._stop_event.is_set():
                    break
                frame = np.array(sct.grab(mon))[:, :, :3]  # drop alpha → BGR
                try:
                    proc.stdin.write(frame.tobytes())
                except BrokenPipeError:
                    break
                elapsed = time.perf_counter() - t0
                sleep_t = interval - elapsed
                if sleep_t > 0:
                    time.sleep(sleep_t)
                self.status_update.emit(f"REC  {time.strftime('%H:%M:%S')}")

    def _audio_worker(self, pipe_w, s: Settings, has_audio: bool, has_mic: bool):
        """Capture desktop/mic audio and write raw PCM to pipe_w."""
        CHUNK = 1024
        RATE  = 44100
        CHANS = 2
        pa = pyaudio.PyAudio()

        def find_device(name):
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info["name"] == name and info["maxInputChannels"] > 0:
                    return i
            return None

        streams = []
        if has_audio:
            idx = find_device(s.audio_source)
            if idx is not None:
                try:
                    streams.append(pa.open(format=pyaudio.paInt16, channels=CHANS,
                                           rate=RATE, input=True,
                                           input_device_index=idx, frames_per_buffer=CHUNK))
                except Exception: pass
        if has_mic:
            idx = find_device(s.mic_source)
            if idx is not None:
                try:
                    streams.append(pa.open(format=pyaudio.paInt16, channels=CHANS,
                                           rate=RATE, input=True,
                                           input_device_index=idx, frames_per_buffer=CHUNK))
                except Exception: pass

        try:
            with open(pipe_w, "wb", closefd=True) as pipe:
                while not self._stop_event.is_set():
                    self._pause_event.wait()
                    chunks = []
                    for st in streams:
                        try:
                            chunks.append(np.frombuffer(st.read(CHUNK, exception_on_overflow=False), dtype=np.int16))
                        except Exception:
                            chunks.append(np.zeros(CHUNK * CHANS, dtype=np.int16))
                    if chunks:
                        mixed = np.mean(chunks, axis=0).astype(np.int16) if len(chunks) > 1 else chunks[0]
                        pipe.write(mixed.tobytes())
        except Exception:
            pass
        finally:
            for st in streams:
                try: st.stop_stream(); st.close()
                except Exception: pass
            pa.terminate()


# ── Settings Dialog ───────────────────────────────────────────────────────────
class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙  SETTINGS")
        self.resize(520, 480)
        self.setStyleSheet(THEME)
        self.s = settings

        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        layout.addWidget(tabs)

        tabs.addTab(self._tab_output(),  "OUTPUT")
        tabs.addTab(self._tab_video(),   "VIDEO")
        tabs.addTab(self._tab_audio(),   "AUDIO")
        tabs.addTab(self._tab_capture(), "CAPTURE")
        tabs.addTab(self._tab_hotkeys(), "HOTKEYS")

        btn_row = QHBoxLayout()
        save_btn = QPushButton("SAVE")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    # ── Output tab ──
    def _tab_output(self):
        w = QWidget(); f = QFormLayout(w)

        self.e_dir = QLineEdit(self.s.save_dir)
        browse = QPushButton("…")
        browse.setFixedWidth(32)
        browse.setCursor(Qt.CursorShape.PointingHandCursor)
        browse.clicked.connect(self._browse_dir)
        row = QHBoxLayout()
        row.addWidget(self.e_dir); row.addWidget(browse)
        row_w = QWidget(); row_w.setLayout(row)
        f.addRow("Save folder:", row_w)

        self.c_format = QComboBox()
        self.c_format.addItems(["mp4", "mkv", "avi", "mov"])
        self.c_format.setCurrentText(self.s.format)
        f.addRow("Container:", self.c_format)

        self.e_template = QLineEdit(self.s.filename_template)
        f.addRow("Filename template:", self.e_template)
        f.addRow("", QLabel("  strftime codes: %Y %m %d %H %M %S"))

        return w

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Select save folder", self.e_dir.text())
        if d: self.e_dir.setText(d)

    # ── Video tab ──
    def _tab_video(self):
        w = QWidget(); f = QFormLayout(w)

        self.c_res = QComboBox()
        self.c_res.addItems(["Source", "1920x1080", "1280x720", "854x480", "640x360"])
        self.c_res.setCurrentText(self.s.resolution)
        f.addRow("Resolution:", self.c_res)

        self.sp_fps = QSpinBox()
        self.sp_fps.setRange(1, 120); self.sp_fps.setValue(self.s.fps)
        f.addRow("FPS:", self.sp_fps)

        self.c_encoder = QComboBox()
        self.c_encoder.addItems(["libx264", "libx265", "h264_nvenc", "hevc_nvenc"])
        self.c_encoder.setCurrentText(self.s.encoder)
        f.addRow("Encoder:", self.c_encoder)

        self.c_preset = QComboBox()
        self.c_preset.addItems(["ultrafast","superfast","veryfast","faster","fast","medium","slow"])
        self.c_preset.setCurrentText(self.s.preset)
        f.addRow("Preset:", self.c_preset)

        self.c_vbitrate = QComboBox()
        self.c_vbitrate.setEditable(True)
        self.c_vbitrate.addItems(["2000k","4000k","6000k","8000k","12000k","20000k","40000k"])
        self.c_vbitrate.setCurrentText(self.s.video_bitrate)
        f.addRow("Video bitrate:", self.c_vbitrate)

        self.sp_crf = QSpinBox()
        self.sp_crf.setRange(0, 51); self.sp_crf.setValue(self.s.crf)
        f.addRow("CRF (0=best):", self.sp_crf)

        return w

    # ── Audio tab ──
    def _tab_audio(self):
        w = QWidget(); f = QFormLayout(w)

        devices = ["None"] + get_input_devices()

        self.c_audio = QComboBox()
        self.c_audio.addItems(devices)
        if self.s.audio_source in devices:
            self.c_audio.setCurrentText(self.s.audio_source)
        f.addRow("Desktop audio:", self.c_audio)

        self.c_mic = QComboBox()
        self.c_mic.addItems(devices)
        if self.s.mic_source in devices:
            self.c_mic.setCurrentText(self.s.mic_source)
        f.addRow("Microphone:", self.c_mic)

        self.c_abitrate = QComboBox()
        self.c_abitrate.addItems(["96k","128k","192k","256k","320k"])
        self.c_abitrate.setCurrentText(self.s.audio_bitrate)
        f.addRow("Audio bitrate:", self.c_abitrate)

        refresh = QPushButton("↺  Refresh devices")
        refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh.clicked.connect(lambda: self._refresh_audio(devices))
        f.addRow("", refresh)

        return w

    def _refresh_audio(self, _):
        devices = ["None"] + get_input_devices()
        for cb in (self.c_audio, self.c_mic):
            cur = cb.currentText()
            cb.clear(); cb.addItems(devices)
            if cur in devices: cb.setCurrentText(cur)

    # ── Capture tab ──
    def _tab_capture(self):
        w = QWidget(); f = QFormLayout(w)

        self.chk_cursor = QCheckBox("Show cursor")
        self.chk_cursor.setChecked(self.s.show_cursor)
        f.addRow(self.chk_cursor)

        self.chk_clicks = QCheckBox("Highlight mouse clicks")
        self.chk_clicks.setChecked(self.s.highlight_clicks)
        f.addRow(self.chk_clicks)

        self.sp_countdown = QSpinBox()
        self.sp_countdown.setRange(0, 10); self.sp_countdown.setValue(self.s.countdown)
        f.addRow("Countdown (sec):", self.sp_countdown)

        return w

    # ── Hotkeys tab ──
    def _tab_hotkeys(self):
        w = QWidget(); f = QFormLayout(w)
        self.e_hk_start = QLineEdit(self.s.hotkey_start)
        self.e_hk_stop  = QLineEdit(self.s.hotkey_stop)
        f.addRow("Start recording:", self.e_hk_start)
        f.addRow("Stop recording:",  self.e_hk_stop)
        f.addRow("", QLabel("  (display only — use buttons or these keys)"))
        return w

    # ── Save ──
    def _save(self):
        s = self.s
        s.save_dir        = self.e_dir.text()
        s.format          = self.c_format.currentText()
        s.filename_template = self.e_template.text()
        s.resolution      = self.c_res.currentText()
        s.fps             = self.sp_fps.value()
        s.encoder         = self.c_encoder.currentText()
        s.preset          = self.c_preset.currentText()
        s.video_bitrate   = self.c_vbitrate.currentText()
        s.crf             = self.sp_crf.value()
        s.audio_source    = self.c_audio.currentText()
        s.mic_source      = self.c_mic.currentText()
        s.audio_bitrate   = self.c_abitrate.currentText()
        s.show_cursor     = self.chk_cursor.isChecked()
        s.highlight_clicks= self.chk_clicks.isChecked()
        s.countdown       = self.sp_countdown.value()
        s.hotkey_start    = self.e_hk_start.text()
        s.hotkey_stop     = self.e_hk_stop.text()
        save_settings(s)
        self.accept()


# ── Main Window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self._rec_thread: RecordingThread | None = None
        self._capture_rect: QRect | None = None
        self._elapsed = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self.setWindowTitle("◉ SCREEN RECORDER")
        self.setMinimumWidth(480)
        self.setStyleSheet(THEME)

        self._build_ui()
        self._update_mode_label()

    # ── UI construction ──
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(14, 14, 14, 14)

        # title bar row
        title_row = QHBoxLayout()
        title = QLabel("◉  SCREEN RECORDER")
        title.setStyleSheet(f"color:{CP_CYAN}; font-size:14pt; font-weight:bold;")
        title_row.addWidget(title)
        title_row.addStretch()
        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))
        title_row.addWidget(restart_btn)
        root.addLayout(title_row)

        # ── Capture mode group ──
        mode_grp = QGroupBox("CAPTURE MODE")
        mode_layout = QHBoxLayout(mode_grp)

        self.btn_fullscreen = QPushButton("⬛  FULLSCREEN")
        self.btn_area       = QPushButton("⬚  SELECT AREA")
        self.btn_window     = QPushButton("🗗  PICK WINDOW")
        for b in (self.btn_fullscreen, self.btn_area, self.btn_window):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            mode_layout.addWidget(b)

        self.btn_fullscreen.clicked.connect(lambda: self._set_mode("fullscreen"))
        self.btn_area.clicked.connect(self._select_area)
        self.btn_window.clicked.connect(self._pick_window)
        root.addWidget(mode_grp)

        # mode info label
        self.lbl_mode = QLabel()
        self.lbl_mode.setStyleSheet(f"color:{CP_SUBTEXT}; font-size:9pt;")
        root.addWidget(self.lbl_mode)

        # ── Quick settings row ──
        quick_grp = QGroupBox("QUICK SETTINGS")
        qf = QFormLayout(quick_grp)

        self.c_res_quick = QComboBox()
        self.c_res_quick.addItems(["Source","1920x1080","1280x720","854x480","640x360"])
        self.c_res_quick.setCurrentText(self.settings.resolution)
        self.c_res_quick.currentTextChanged.connect(lambda v: setattr(self.settings, "resolution", v))
        qf.addRow("Resolution:", self.c_res_quick)

        self.c_fps_quick = QComboBox()
        self.c_fps_quick.addItems(["15","24","30","60","120"])
        self.c_fps_quick.setCurrentText(str(self.settings.fps))
        self.c_fps_quick.currentTextChanged.connect(lambda v: setattr(self.settings, "fps", int(v)))
        qf.addRow("FPS:", self.c_fps_quick)

        self.c_vbr_quick = QComboBox()
        self.c_vbr_quick.setEditable(True)
        self.c_vbr_quick.addItems(["2000k","4000k","6000k","8000k","12000k","20000k"])
        self.c_vbr_quick.setCurrentText(self.settings.video_bitrate)
        self.c_vbr_quick.currentTextChanged.connect(lambda v: setattr(self.settings, "video_bitrate", v))
        qf.addRow("Bitrate:", self.c_vbr_quick)

        root.addWidget(quick_grp)

        # ── Record controls ──
        ctrl_grp = QGroupBox("CONTROLS")
        ctrl_layout = QHBoxLayout(ctrl_grp)

        self.btn_record = QPushButton("⏺  RECORD")
        self.btn_record.setStyleSheet(
            f"QPushButton{{background:{CP_DIM};border:1px solid {CP_DIM};color:white;padding:8px 20px;font-weight:bold;font-size:11pt;}}"
            f"QPushButton:hover{{border:1px solid {CP_GREEN};color:{CP_GREEN};}}"
        )
        self.btn_pause  = QPushButton("⏸  PAUSE")
        self.btn_stop   = QPushButton("⏹  STOP")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

        for b in (self.btn_record, self.btn_pause, self.btn_stop):
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            ctrl_layout.addWidget(b)

        self.btn_record.clicked.connect(self._start_recording)
        self.btn_pause.clicked.connect(self._toggle_pause)
        self.btn_stop.clicked.connect(self._stop_recording)
        root.addWidget(ctrl_grp)

        # ── Timer + status ──
        info_row = QHBoxLayout()
        self.lbl_timer = QLabel("00:00:00")
        self.lbl_timer.setStyleSheet(f"color:{CP_RED}; font-size:18pt; font-weight:bold; font-family:Consolas;")
        self.lbl_rec_dot = QLabel("●")
        self.lbl_rec_dot.setStyleSheet(f"color:{CP_DIM}; font-size:18pt;")
        info_row.addWidget(self.lbl_rec_dot)
        info_row.addWidget(self.lbl_timer)
        info_row.addStretch()

        settings_btn = QPushButton("⚙  SETTINGS")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self._open_settings)
        open_folder_btn = QPushButton("📁  OPEN FOLDER")
        open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_folder_btn.clicked.connect(self._open_save_folder)
        info_row.addWidget(settings_btn)
        info_row.addWidget(open_folder_btn)
        root.addLayout(info_row)

        # status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Ready")

    # ── Mode helpers ──
    def _set_mode(self, mode: str, rect: QRect = None, label: str = ""):
        self.settings.capture_mode = mode
        if rect:
            self._capture_rect = rect
        elif mode == "fullscreen":
            screen = QApplication.primaryScreen().geometry()
            self._capture_rect = screen
        self._update_mode_label(label)

    def _update_mode_label(self, extra=""):
        mode = self.settings.capture_mode
        icons = {"fullscreen": "⬛", "area": "⬚", "window": "🗗"}
        icon = icons.get(mode, "")
        r = self._capture_rect
        region = f"  {r.width()}×{r.height()} @ ({r.x()},{r.y()})" if r else ""
        self.lbl_mode.setText(f"{icon}  {mode.upper()}{region}  {extra}")

    def _select_area(self):
        self.hide()
        QTimer.singleShot(200, self._launch_area_selector)

    def _launch_area_selector(self):
        self._selector = AreaSelector()
        self._selector.area_selected.connect(self._on_area_selected)
        self._selector.cancelled.connect(self.show)
        self._selector.show()

    def _on_area_selected(self, rect: QRect):
        self.show()
        self._set_mode("area", rect)

    def _pick_window(self):
        dlg = WindowPicker(self)
        dlg.window_chosen.connect(self._on_window_chosen)
        dlg.exec()

    def _on_window_chosen(self, hwnd: int):
        rect = WindowPicker.get_window_rect(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if rect.isValid():
            self._set_mode("window", rect, f"— {title[:40]}")
        else:
            self.status.showMessage("Could not get window rect.")

    # ── Recording controls ──
    def _start_recording(self):
        if self._capture_rect is None:
            screen = QApplication.primaryScreen().geometry()
            self._capture_rect = screen
            self.settings.capture_mode = "fullscreen"

        countdown = self.settings.countdown
        if countdown > 0:
            self._countdown(countdown, self._do_start)
        else:
            self._do_start()

    def _countdown(self, n, callback):
        if n == 0:
            callback(); return
        self.status.showMessage(f"Starting in {n}…")
        QTimer.singleShot(1000, lambda: self._countdown(n - 1, callback))

    def _do_start(self):
        self._elapsed = 0
        self._rec_thread = RecordingThread(self.settings, self._capture_rect)
        self._rec_thread.status_update.connect(self.status.showMessage)
        self._rec_thread.finished_path.connect(self._on_finished)
        self._rec_thread.error_occurred.connect(self._on_error)
        self._rec_thread.start()

        self._timer.start(1000)
        self.btn_record.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.lbl_rec_dot.setStyleSheet(f"color:{CP_RED}; font-size:18pt;")
        self.status.showMessage("Recording…")

    def _toggle_pause(self):
        if not self._rec_thread: return
        if self._rec_thread._pause_event.is_set():
            self._rec_thread.pause()
            self.btn_pause.setText("▶  RESUME")
            self._timer.stop()
            self.lbl_rec_dot.setStyleSheet(f"color:{CP_YELLOW}; font-size:18pt;")
        else:
            self._rec_thread.resume()
            self.btn_pause.setText("⏸  PAUSE")
            self._timer.start(1000)
            self.lbl_rec_dot.setStyleSheet(f"color:{CP_RED}; font-size:18pt;")

    def _stop_recording(self):
        if self._rec_thread:
            self._rec_thread.stop()
        self._timer.stop()
        self.btn_record.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_pause.setText("⏸  PAUSE")
        self.lbl_rec_dot.setStyleSheet(f"color:{CP_DIM}; font-size:18pt;")
        self.status.showMessage("Stopping — encoding…")

    def _tick(self):
        self._elapsed += 1
        h, rem = divmod(self._elapsed, 3600)
        m, s = divmod(rem, 60)
        self.lbl_timer.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _on_finished(self, path: str):
        self.status.showMessage(f"Saved → {path}")
        QMessageBox.information(self, "Recording saved", f"File saved to:\n{path}")

    def _on_error(self, msg: str):
        self.status.showMessage("Error!")
        QMessageBox.critical(self, "Recording error", msg)

    # ── Settings / folder ──
    def _open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # sync quick-setting combos
            self.c_res_quick.setCurrentText(self.settings.resolution)
            self.c_fps_quick.setCurrentText(str(self.settings.fps))
            self.c_vbr_quick.setCurrentText(self.settings.video_bitrate)
            self.status.showMessage("Settings saved.")

    def _open_save_folder(self):
        import subprocess as sp
        sp.Popen(["explorer", os.path.normpath(self.settings.save_dir)])

    def closeEvent(self, e):
        if self._rec_thread and self._rec_thread.isRunning():
            self._stop_recording()
            self._rec_thread.wait(3000)
        save_settings(self.settings)
        e.accept()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
