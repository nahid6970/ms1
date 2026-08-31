from __future__ import annotations

import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import wave
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import mss
import pygetwindow as gw
import soundcard as sc
import sounddevice as sd
from PyQt6.QtCore import QEvent, QPoint, QRect, QSize, Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

try:
    import imageio_ffmpeg
except Exception:  # pragma: no cover - optional dependency resolution
    imageio_ffmpeg = None


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


APP_DIR = Path(__file__).resolve().parent
CONFIG_PATH = APP_DIR / "recorder_settings.json"
DEFAULT_OUTPUT_DIR = APP_DIR / "recordings"
ERROR_LOG_DIR = APP_DIR / "logs"
LAST_ERROR_PATH = ERROR_LOG_DIR / "last_error.txt"


def build_stylesheet() -> str:
    return f"""
    QMainWindow, QDialog {{
        background-color: {CP_BG};
    }}
    QWidget {{
        color: {CP_TEXT};
        font-family: 'Consolas';
        font-size: 10pt;
    }}
    QLabel#subtle {{
        color: {CP_SUBTEXT};
    }}
    QLineEdit, QSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
        background-color: {CP_PANEL};
        color: {CP_CYAN};
        border: 1px solid {CP_DIM};
        padding: 4px;
        selection-background-color: {CP_CYAN};
        selection-color: #000000;
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {CP_CYAN};
    }}
    QSpinBox::up-button, QSpinBox::down-button {{
        width: 0px;
        border: none;
    }}
    QPushButton {{
        background-color: {CP_DIM};
        border: 1px solid {CP_DIM};
        color: white;
        padding: 6px 12px;
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
        background-color: #1d1d1d;
        color: #666666;
        border-color: #1d1d1d;
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
    QCheckBox {{
        spacing: 8px;
        color: {CP_TEXT};
    }}
    QCheckBox::indicator {{
        width: 14px;
        height: 14px;
        border: 1px solid {CP_DIM};
        background: {CP_PANEL};
    }}
    QCheckBox::indicator:checked {{
        background: {CP_YELLOW};
        border-color: {CP_YELLOW};
    }}
    QTabWidget::pane {{
        border: 1px solid {CP_DIM};
        top: -1px;
        background: {CP_BG};
    }}
    QTabBar::tab {{
        background: {CP_PANEL};
        color: {CP_TEXT};
        border: 1px solid {CP_DIM};
        padding: 6px 12px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {CP_DIM};
        color: {CP_YELLOW};
        border-bottom-color: {CP_DIM};
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
    QScrollBar:horizontal {{
        background: {CP_BG};
        height: 10px;
        margin: 0px;
    }}
    QScrollBar::handle:horizontal {{
        background: {CP_CYAN};
        min-width: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px;
        background: none;
    }}
    """


def get_ffmpeg_path() -> Optional[str]:
    if imageio_ffmpeg is not None:
        try:
            path = imageio_ffmpeg.get_ffmpeg_exe()
            if path and os.path.exists(path):
                return path
        except Exception:
            pass
    return shutil.which("ffmpeg")


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return dict(default)
    try:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
    except Exception:
        return dict(default)
    if not isinstance(loaded, dict):
        return dict(default)
    merged = dict(default)
    merged.update(loaded)
    return merged


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write(text)


def append_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def evenize(value: int) -> int:
    value = max(2, int(value))
    return value if value % 2 == 0 else value - 1


def unique_output_path(folder: Path, prefix: str, extension: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{prefix}_{stamp}" if prefix else stamp
    candidate = folder / f"{base}.{extension}"
    index = 1
    while candidate.exists():
        candidate = folder / f"{base}_{index}.{extension}"
        index += 1
    return candidate


def format_exception_report(title: str, message: str) -> str:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{stamp}] {title}\n{message}\n\n"


def run_hidden(command: list[str]) -> subprocess.Popen:
    kwargs = {
        "stdin": subprocess.PIPE,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.PIPE,
        "bufsize": 0,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    return subprocess.Popen(command, **kwargs)


def qrect_to_dict(rect: QRect) -> dict:
    return {"left": rect.left(), "top": rect.top(), "width": rect.width(), "height": rect.height()}


def dict_to_qrect(data: dict) -> QRect:
    return QRect(int(data.get("left", 0)), int(data.get("top", 0)), int(data.get("width", 0)), int(data.get("height", 0)))


@dataclass
class AppConfig:
    capture_mode: str = "screen"
    selected_window_title: str = ""
    selected_area: dict = field(default_factory=lambda: {"left": 0, "top": 0, "width": 1280, "height": 720})
    save_folder: str = str(DEFAULT_OUTPUT_DIR)
    filename_prefix: str = "capture"
    fps: int = 60
    video_bitrate_kbps: int = 16000
    use_source_resolution: bool = True
    target_width: int = 1920
    target_height: int = 1080
    container_format: str = "mp4"
    codec_preset: str = "veryfast"
    countdown_seconds: int = 0
    record_system_audio: bool = True
    system_audio_device: str = ""
    system_audio_device_index: int = -1
    record_microphone: bool = True
    microphone_device: str = ""
    microphone_device_index: int = -1
    audio_sample_rate: int = 48000
    audio_track_mode: str = "separate"
    audio_bitrate_kbps: int = 192
    auto_open_folder: bool = True
    keep_temp_files: bool = False

    @classmethod
    def load(cls) -> "AppConfig":
        data = load_json(CONFIG_PATH, asdict(cls()))
        return cls(**data)

    def save(self) -> None:
        save_json(CONFIG_PATH, asdict(self))


def list_visible_windows() -> list[str]:
    titles = []
    for win in gw.getAllWindows():
        try:
            title = (win.title or "").strip()
            if not title:
                continue
            if getattr(win, "isMinimized", False):
                continue
            if win.width <= 0 or win.height <= 0:
                continue
            titles.append(title)
        except Exception:
            continue
    seen = []
    for title in sorted(titles, key=str.lower):
        if title not in seen:
            seen.append(title)
    return seen


def get_window_by_title(title: str):
    matches = gw.getWindowsWithTitle(title)
    for win in matches:
        try:
            if (win.title or "").strip() == title:
                return win
        except Exception:
            continue
    return matches[0] if matches else None


def list_sounddevice_entries() -> tuple[list[dict], list[dict]]:
    devices = sd.query_devices()
    hostapis = sd.query_hostapis()
    inputs = []
    outputs = []
    for index, device in enumerate(devices):
        hostapi_name = hostapis[int(device["hostapi"])]["name"]
        entry = {
            "index": index,
            "name": device["name"],
            "hostapi": hostapi_name,
            "max_input_channels": int(device["max_input_channels"]),
            "max_output_channels": int(device["max_output_channels"]),
            "default_samplerate": int(device["default_samplerate"]),
        }
        if entry["max_input_channels"] > 0:
            inputs.append(entry)
        if entry["max_output_channels"] > 0:
            outputs.append(entry)
    return inputs, outputs


def find_device_index(devices: list[dict], name: str) -> Optional[int]:
    if not name:
        return None
    for entry in devices:
        if entry["name"] == name:
            return entry["index"]
    return None


def find_wasapi_output_devices() -> list[dict]:
    _, outputs = list_sounddevice_entries()
    return [device for device in outputs if device["hostapi"] == "Windows WASAPI"]


def device_label(device: dict) -> str:
    return f'{device["name"]} [{device["hostapi"]}]'


class AreaSelector(QDialog):
    areaSelected = pyqtSignal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._start = QPoint()
        self._end = QPoint()
        self._dragging = False
        geometry = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geometry)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._start = event.position().toPoint()
            self._end = self._start
            self._dragging = True
            self.update()

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._dragging:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._end = event.position().toPoint()
            self._dragging = False
            rect = QRect(self._start, self._end).normalized()
            if rect.width() > 4 and rect.height() > 4:
                self.areaSelected.emit(rect)
            self.accept()

    def keyPressEvent(self, event):  # noqa: N802
        if event.key() == Qt.Key.Key_Escape:
            self.reject()

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 140))
        if self._dragging:
            rect = QRect(self._start, self._end).normalized()
            painter.setPen(QPen(QColor(CP_CYAN), 2, Qt.PenStyle.SolidLine))
            painter.setBrush(QBrush(QColor(0, 240, 255, 45)))
            painter.drawRect(rect)


class ErrorDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(780, 460)
        self._title = title
        self._message = message.strip()

        layout = QVBoxLayout(self)
        heading = QLabel(title)
        heading.setStyleSheet(f"color: {CP_RED}; font-size: 14pt; font-weight: bold;")
        layout.addWidget(heading)

        self.body = QTextEdit()
        self.body.setReadOnly(True)
        self.body.setPlainText(self._message)
        layout.addWidget(self.body, 1)

        buttons = QHBoxLayout()
        self.save_button = QPushButton("Save Error")
        self.save_button.clicked.connect(self.save_error)
        self.open_log_button = QPushButton("Open Log Folder")
        self.open_log_button.clicked.connect(self.open_log_folder)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.save_button)
        buttons.addWidget(self.open_log_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        layout.addLayout(buttons)

    def save_error(self) -> None:
        write_text_file(LAST_ERROR_PATH, f"{self._title}\n\n{self._message}\n")

    def open_log_folder(self) -> None:
        ERROR_LOG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(ERROR_LOG_DIR))  # type: ignore[attr-defined]
        except Exception:
            pass


class AudioCaptureJob:
    def __init__(
        self,
        *,
        device_name: str,
        device_index: int,
        device_kind: str,
        sample_rate: int,
        output_path: Path,
    ):
        self.device_name = device_name
        self.device_index = device_index
        self.device_kind = device_kind
        self.sample_rate = sample_rate
        self.output_path = output_path
        self.stop_event = threading.Event()
        self.queue: queue.Queue[Optional[bytes]] = queue.Queue(maxsize=256)
        self.writer_thread: Optional[threading.Thread] = None
        self.stream = None
        self.wave_file = None
        self.error: Optional[str] = None

    def start(self) -> None:
        if self.device_kind == "system":
            self._start_loopback_capture()
            return
        self._start_microphone_capture()

    def _start_microphone_capture(self) -> None:
        device_info = sd.query_devices(self.device_index)
        if device_info["max_input_channels"] <= 0:
            raise RuntimeError(f'Selected microphone device is not an input device: {device_info["name"]}')
        channels = max(1, min(2, int(device_info["max_input_channels"])))
        sample_rate = self.sample_rate or int(device_info["default_samplerate"]) or 48000

        self.wave_file = wave.open(str(self.output_path), "wb")
        self.wave_file.setnchannels(channels)
        self.wave_file.setsampwidth(2)
        self.wave_file.setframerate(sample_rate)

        self.stream = sd.InputStream(
            device=self.device_index,
            samplerate=sample_rate,
            channels=channels,
            dtype="int16",
            callback=self._callback,
        )
        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer_thread.start()
        try:
            self.stream.start()
        except Exception:
            self._cleanup_stream_error()
            raise

    def _start_loopback_capture(self) -> None:
        loopback_mic = None
        if self.device_name:
            try:
                loopback_mic = sc.get_microphone(self.device_name, include_loopback=True)
            except Exception:
                loopback_mic = None
        if loopback_mic is None:
            try:
                loopback_mic = sc.get_microphone(sc.default_speaker().name, include_loopback=True)
            except Exception:
                loopback_mic = None
        if loopback_mic is None:
            raise RuntimeError(f"Loopback speaker not found: {self.device_name or 'default speaker'}")
        channels = max(1, min(2, int(getattr(loopback_mic, "channels", 2) or 2)))
        sample_rate = self.sample_rate or 48000

        self.wave_file = wave.open(str(self.output_path), "wb")
        self.wave_file.setnchannels(channels)
        self.wave_file.setsampwidth(2)
        self.wave_file.setframerate(sample_rate)
        self.writer_thread = threading.Thread(
            target=self._loopback_capture_loop,
            args=(loopback_mic, sample_rate, channels),
            daemon=True,
        )
        self.writer_thread.start()

    def _loopback_capture_loop(self, loopback_mic, sample_rate: int, channels: int) -> None:  # noqa: ANN001
        blocksize = max(1024, sample_rate // 20)
        try:
            with loopback_mic.recorder(samplerate=sample_rate, channels=channels) as recorder:
                while not self.stop_event.is_set():
                    data = recorder.record(blocksize)
                    if data is None:
                        continue
                    self.wave_file.writeframes(data.astype("int16", copy=False).tobytes())
        except Exception as exc:
            self.error = str(exc)
        finally:
            self.stop_event.set()

    def _cleanup_stream_error(self) -> None:
        self.stop_event.set()
        try:
            if self.stream:
                self.stream.close()
        except Exception:
            pass
        try:
            if self.wave_file:
                self.wave_file.close()
        except Exception:
            pass
        try:
            self.queue.put_nowait(None)
        except Exception:
            pass
        if self.writer_thread:
            self.writer_thread.join(timeout=1.0)

    def _callback(self, indata, frames, time_info, status):  # noqa: ANN001
        if status:
            self.error = str(status)
        try:
            self.queue.put_nowait(indata.tobytes())
        except queue.Full:
            self.error = self.error or "Audio buffer overflow"

    def _writer_loop(self) -> None:
        while not (self.stop_event.is_set() and self.queue.empty()):
            try:
                chunk = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if chunk is None:
                break
            if self.wave_file:
                self.wave_file.writeframes(chunk)

    def stop(self) -> None:
        self.stop_event.set()
        if self.stream:
            try:
                self.stream.stop()
            except Exception:
                pass
            try:
                self.stream.close()
            except Exception:
                pass
        try:
            self.queue.put_nowait(None)
        except Exception:
            pass
        if self.writer_thread:
            self.writer_thread.join(timeout=2.0)
        if self.wave_file:
            try:
                self.wave_file.close()
            except Exception:
                pass


class RecorderThread(QThread):
    status = pyqtSignal(str)
    finishedRecording = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, config: AppConfig, capture_rect: QRect, window_title: str, parent=None):
        super().__init__(parent)
        self.config = config
        self.capture_rect = capture_rect
        self.window_title = window_title
        self._stop_requested = threading.Event()
        self._temp_dir = Path(tempfile.mkdtemp(prefix="screen_recorder_"))
        self.output_path: Optional[Path] = None

    def stop(self) -> None:
        self._stop_requested.set()

    def _build_capture_rect(self) -> QRect:
        if self.config.capture_mode == "area":
            rect = self.capture_rect
        elif self.config.capture_mode == "window":
            win = get_window_by_title(self.window_title)
            if win is None:
                raise RuntimeError(f"Window not found: {self.window_title}")
            rect = QRect(int(win.left), int(win.top), int(win.width), int(win.height))
        else:
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                rect = QRect(int(monitor["left"]), int(monitor["top"]), int(monitor["width"]), int(monitor["height"]))
        if rect.width() <= 0 or rect.height() <= 0:
            raise RuntimeError("Invalid capture region")
        return rect

    def _ffmpeg_path(self) -> str:
        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            raise RuntimeError(
                "ffmpeg was not found. Install ffmpeg or keep imageio-ffmpeg available in the Python environment."
            )
        return ffmpeg_path

    def _capture_dimensions(self, rect: QRect) -> tuple[int, int]:
        if self.config.use_source_resolution:
            return rect.width(), rect.height()
        return evenize(self.config.target_width), evenize(self.config.target_height)

    def _build_video_command(self, source_w: int, source_h: int, output_path: Path) -> list[str]:
        output_w = evenize(source_w if self.config.use_source_resolution else self.config.target_width)
        output_h = evenize(source_h if self.config.use_source_resolution else self.config.target_height)
        command = [
            self._ffmpeg_path(),
            "-y",
            "-loglevel",
            "error",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "bgra",
            "-s",
            f"{source_w}x{source_h}",
            "-r",
            str(self.config.fps),
            "-i",
            "pipe:0",
        ]
        command.extend(
            [
                "-vf",
                f"scale={output_w}:{output_h}:flags=lanczos",
            ]
        )
        command.extend(
            [
                "-c:v",
                "libx264",
                "-preset",
                self.config.codec_preset,
                "-pix_fmt",
                "yuv420p",
                "-b:v",
                f"{self.config.video_bitrate_kbps}k",
                "-an",
                str(output_path),
            ]
        )
        return command

    def _mux_command(self, video_path: Path, audio_paths: list[Path], output_path: Path) -> list[str]:
        command = [self._ffmpeg_path(), "-y", "-loglevel", "error", "-i", str(video_path)]
        for audio_path in audio_paths:
            command.extend(["-i", str(audio_path)])
        command.extend(["-map", "0:v:0"])
        for index in range(len(audio_paths)):
            command.extend(["-map", f"{index + 1}:a:0"])

        command.extend(["-c:v", "copy"])
        if audio_paths:
            if self.config.audio_track_mode == "mix" and len(audio_paths) >= 2:
                command = [self._ffmpeg_path(), "-y", "-loglevel", "error", "-i", str(video_path)]
                for audio_path in audio_paths:
                    command.extend(["-i", str(audio_path)])
                command.extend(
                    [
                        "-filter_complex",
                        f"[1:a]aformat=channel_layouts=stereo,aresample={self.config.audio_sample_rate}[a1];"
                        f"[2:a]aformat=channel_layouts=stereo,aresample={self.config.audio_sample_rate}[a2];"
                        f"[a1][a2]amix=inputs=2:duration=longest:dropout_transition=2[mixed]",
                        "-map",
                        "0:v:0",
                        "-map",
                        "[mixed]",
                        "-c:v",
                        "copy",
                        "-c:a",
                        "aac",
                        "-b:a",
                        f"{self.config.audio_bitrate_kbps}k",
                        str(output_path),
                    ]
                )
                if output_path.suffix.lower() == ".mp4":
                    command.insert(-1, "-movflags")
                    command.insert(-1, "+faststart")
                return command

            command.extend(["-c:a", "aac", "-b:a", f"{self.config.audio_bitrate_kbps}k"])
            if output_path.suffix.lower() == ".mp4":
                command.extend(["-movflags", "+faststart"])
            command.append(str(output_path))
        else:
            if output_path.suffix.lower() == ".mp4":
                command.extend(["-movflags", "+faststart"])
            command.extend(["-an", str(output_path)])
        return command

    def _run_mux(self, video_path: Path, audio_paths: list[Path]) -> Path:
        final_ext = self.config.container_format.lower().strip(".")
        output_path = unique_output_path(Path(self.config.save_folder), self.config.filename_prefix, final_ext)
        command = self._mux_command(video_path, audio_paths, output_path)
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "Muxing failed")
        return output_path

    def run(self) -> None:  # noqa: C901
        audio_jobs: list[AudioCaptureJob] = []
        audio_paths: list[Path] = []
        video_temp = self._temp_dir / "video_temp.mkv"
        video_proc: Optional[subprocess.Popen] = None
        try:
            rect = self._build_capture_rect()
            if self.config.countdown_seconds > 0:
                self.status.emit(f"Starting in {self.config.countdown_seconds} seconds...")
                for remaining in range(self.config.countdown_seconds, 0, -1):
                    if self._stop_requested.is_set():
                        raise RuntimeError("Recording cancelled before start")
                    self.status.emit(f"Starting in {remaining} seconds...")
                    time.sleep(1)

            input_devices, output_devices = list_sounddevice_entries()
            if self.config.record_system_audio and self.config.system_audio_device_index >= 0:
                system_path = self._temp_dir / "system_audio.wav"
                job = AudioCaptureJob(
                    device_name=self.config.system_audio_device,
                    device_index=self.config.system_audio_device_index,
                    device_kind="system",
                    sample_rate=self.config.audio_sample_rate,
                    output_path=system_path,
                )
                job.start()
                audio_jobs.append(job)
                audio_paths.append(system_path)

            if self.config.record_microphone and self.config.microphone_device_index >= 0:
                mic_path = self._temp_dir / "microphone.wav"
                job = AudioCaptureJob(
                    device_name=self.config.microphone_device,
                    device_index=self.config.microphone_device_index,
                    device_kind="microphone",
                    sample_rate=self.config.audio_sample_rate,
                    output_path=mic_path,
                )
                job.start()
                audio_jobs.append(job)
                audio_paths.append(mic_path)

            bbox = {
                "left": rect.left(),
                "top": rect.top(),
                "width": rect.width(),
                "height": rect.height(),
            }
            with mss.mss() as sct:
                first_shot = sct.grab(bbox)
                source_w, source_h = int(first_shot.width), int(first_shot.height)
                video_proc = run_hidden(self._build_video_command(source_w, source_h, video_temp))
                if video_proc.stdin is None:
                    raise RuntimeError("Unable to open ffmpeg video input pipe")
                self.status.emit("Recording...")
                video_proc.stdin.write(first_shot.bgra)
                frame_interval = 1.0 / max(1, self.config.fps)
                next_tick = time.perf_counter() + frame_interval
                frames = 1
                while not self._stop_requested.is_set():
                    shot = sct.grab(bbox)
                    try:
                        video_proc.stdin.write(shot.bgra)
                    except BrokenPipeError:
                        stderr = b""
                        try:
                            if video_proc.stderr is not None:
                                stderr = video_proc.stderr.read() or b""
                        except Exception:
                            pass
                        raise RuntimeError(
                            "ffmpeg closed the video pipe while recording window capture.\n"
                            + (stderr.decode("utf-8", errors="ignore").strip() or "No ffmpeg stderr available.")
                        )
                    frames += 1
                    next_tick += frame_interval
                    sleep_for = next_tick - time.perf_counter()
                    if sleep_for > 0:
                        time.sleep(sleep_for)
                    else:
                        next_tick = time.perf_counter()

            if video_proc is not None and video_proc.stdin is not None:
                try:
                    video_proc.stdin.close()
                except Exception:
                    pass
                stderr = video_proc.communicate()[1]
                if video_proc.returncode not in (0, None):
                    err_text = (stderr or b"").decode("utf-8", errors="ignore").strip()
                    raise RuntimeError(err_text or "Video encoder failed")

            for job in audio_jobs:
                job.stop()
                if job.error:
                    self.status.emit(f"Audio warning: {job.error}")

            final_output = self._run_mux(video_temp, audio_paths)
            self.output_path = final_output
            if not self.config.keep_temp_files:
                try:
                    shutil.rmtree(self._temp_dir, ignore_errors=True)
                except Exception:
                    pass
            self.status.emit(f"Saved {final_output}")
            self.finishedRecording.emit(str(final_output))
        except Exception as exc:
            if video_proc is not None:
                try:
                    if video_proc.stdin:
                        video_proc.stdin.close()
                except Exception:
                    pass
                try:
                    video_proc.terminate()
                except Exception:
                    pass
                try:
                    video_proc.wait(timeout=2.0)
                except Exception:
                    try:
                        video_proc.kill()
                    except Exception:
                        pass
                try:
                    if video_proc.stderr is not None:
                        err_text = video_proc.stderr.read().decode("utf-8", errors="ignore").strip()
                        if err_text:
                            exc = RuntimeError(f"{exc}\n{err_text}")
                except Exception:
                    pass
            for job in audio_jobs:
                try:
                    job.stop()
                except Exception:
                    pass
            self.error.emit(str(exc))
            if self.config.keep_temp_files:
                self.status.emit(f"Failed, temp files kept in {self._temp_dir}")
            else:
                shutil.rmtree(self._temp_dir, ignore_errors=True)


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, input_devices: list[dict], output_devices: list[dict], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(760, 560)
        self.config = AppConfig(**asdict(config))
        self.input_devices = input_devices
        self.output_devices = output_devices
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.general_tab = QWidget()
        self.video_tab = QWidget()
        self.audio_tab = QWidget()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.video_tab, "Video")
        self.tabs.addTab(self.audio_tab, "Audio")

        self._build_general_tab()
        self._build_video_tab()
        self._build_audio_tab()

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _build_general_tab(self) -> None:
        layout = QVBoxLayout(self.general_tab)
        group = QGroupBox("OUTPUT & BEHAVIOR")
        form = QFormLayout(group)

        self.save_folder_edit = QLineEdit()
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse_save_folder)
        row = QHBoxLayout()
        row.addWidget(self.save_folder_edit, 1)
        row.addWidget(browse)
        row_widget = QWidget()
        row_widget.setLayout(row)
        form.addRow("Save folder", row_widget)

        self.prefix_edit = QLineEdit()
        form.addRow("File prefix", self.prefix_edit)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv"])
        form.addRow("Container", self.format_combo)

        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(0, 10)
        form.addRow("Countdown (sec)", self.countdown_spin)

        self.auto_open_checkbox = QCheckBox("Open folder after recording")
        self.keep_temp_checkbox = QCheckBox("Keep temp files on disk")
        form.addRow("", self.auto_open_checkbox)
        form.addRow("", self.keep_temp_checkbox)

        layout.addWidget(group)
        layout.addStretch()

    def _build_video_tab(self) -> None:
        layout = QVBoxLayout(self.video_tab)
        group = QGroupBox("VIDEO")
        form = QFormLayout(group)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 240)
        form.addRow("FPS", self.fps_spin)

        self.video_bitrate_spin = QSpinBox()
        self.video_bitrate_spin.setRange(250, 200000)
        self.video_bitrate_spin.setSuffix(" kbps")
        form.addRow("Video bitrate", self.video_bitrate_spin)

        self.use_source_resolution_checkbox = QCheckBox("Use source resolution")
        form.addRow("", self.use_source_resolution_checkbox)

        self.target_width_spin = QSpinBox()
        self.target_width_spin.setRange(16, 7680)
        form.addRow("Target width", self.target_width_spin)

        self.target_height_spin = QSpinBox()
        self.target_height_spin.setRange(16, 4320)
        form.addRow("Target height", self.target_height_spin)

        self.codec_preset_combo = QComboBox()
        self.codec_preset_combo.addItems(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium"])
        form.addRow("Encoder preset", self.codec_preset_combo)

        layout.addWidget(group)
        layout.addStretch()

    def _build_audio_tab(self) -> None:
        layout = QVBoxLayout(self.audio_tab)
        group = QGroupBox("AUDIO")
        form = QFormLayout(group)

        self.record_system_checkbox = QCheckBox("Record system audio")
        form.addRow("", self.record_system_checkbox)

        self.system_device_combo = QComboBox()
        self._fill_audio_combo(self.system_device_combo, self.output_devices)
        form.addRow("System device", self.system_device_combo)

        self.record_microphone_checkbox = QCheckBox("Record microphone")
        form.addRow("", self.record_microphone_checkbox)

        self.microphone_combo = QComboBox()
        self._fill_audio_combo(self.microphone_combo, self.input_devices)
        form.addRow("Microphone", self.microphone_combo)

        self.audio_mode_combo = QComboBox()
        self.audio_mode_combo.addItems(["separate", "mix"])
        form.addRow("Track mode", self.audio_mode_combo)

        self.audio_sample_rate_spin = QSpinBox()
        self.audio_sample_rate_spin.setRange(8000, 192000)
        self.audio_sample_rate_spin.setSingleStep(1000)
        form.addRow("Sample rate", self.audio_sample_rate_spin)

        self.audio_bitrate_spin = QSpinBox()
        self.audio_bitrate_spin.setRange(64, 512)
        self.audio_bitrate_spin.setSuffix(" kbps")
        form.addRow("Audio bitrate", self.audio_bitrate_spin)

        layout.addWidget(group)
        layout.addStretch()

    def _fill_audio_combo(self, combo: QComboBox, entries: list[dict]) -> None:
        combo.clear()
        for device in entries:
            combo.addItem(device_label(device), device["index"])

    def _browse_save_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose save folder", self.save_folder_edit.text() or str(DEFAULT_OUTPUT_DIR))
        if folder:
            self.save_folder_edit.setText(folder)

    def _load_values(self) -> None:
        self.save_folder_edit.setText(self.config.save_folder)
        self.prefix_edit.setText(self.config.filename_prefix)
        self.format_combo.setCurrentText(self.config.container_format)
        self.countdown_spin.setValue(self.config.countdown_seconds)
        self.auto_open_checkbox.setChecked(self.config.auto_open_folder)
        self.keep_temp_checkbox.setChecked(self.config.keep_temp_files)

        self.fps_spin.setValue(self.config.fps)
        self.video_bitrate_spin.setValue(self.config.video_bitrate_kbps)
        self.use_source_resolution_checkbox.setChecked(self.config.use_source_resolution)
        self.target_width_spin.setValue(self.config.target_width)
        self.target_height_spin.setValue(self.config.target_height)
        self.codec_preset_combo.setCurrentText(self.config.codec_preset)

        self.record_system_checkbox.setChecked(self.config.record_system_audio)
        self.record_microphone_checkbox.setChecked(self.config.record_microphone)
        self._set_combo_value(self.system_device_combo, self.config.system_audio_device_index, self.config.system_audio_device, self.output_devices)
        self._set_combo_value(self.microphone_combo, self.config.microphone_device_index, self.config.microphone_device, self.input_devices)
        self.audio_mode_combo.setCurrentText(self.config.audio_track_mode)
        self.audio_sample_rate_spin.setValue(self.config.audio_sample_rate)
        self.audio_bitrate_spin.setValue(self.config.audio_bitrate_kbps)

    def _set_combo_value(self, combo: QComboBox, index_value: int, legacy_name: str, source_devices: list[dict]) -> None:
        index = combo.findData(index_value)
        if index >= 0:
            combo.setCurrentIndex(index)
            return
        if legacy_name:
            for device in source_devices:
                if device["name"] == legacy_name:
                    combo_index = combo.findData(device["index"])
                    if combo_index >= 0:
                        combo.setCurrentIndex(combo_index)
                        return

    def accept(self) -> None:
        self.config.save_folder = self.save_folder_edit.text().strip() or str(DEFAULT_OUTPUT_DIR)
        self.config.filename_prefix = self.prefix_edit.text().strip() or "capture"
        self.config.container_format = self.format_combo.currentText()
        self.config.countdown_seconds = self.countdown_spin.value()
        self.config.auto_open_folder = self.auto_open_checkbox.isChecked()
        self.config.keep_temp_files = self.keep_temp_checkbox.isChecked()
        self.config.fps = self.fps_spin.value()
        self.config.video_bitrate_kbps = self.video_bitrate_spin.value()
        self.config.use_source_resolution = self.use_source_resolution_checkbox.isChecked()
        self.config.target_width = self.target_width_spin.value()
        self.config.target_height = self.target_height_spin.value()
        self.config.codec_preset = self.codec_preset_combo.currentText()
        self.config.record_system_audio = self.record_system_checkbox.isChecked()
        self.config.record_microphone = self.record_microphone_checkbox.isChecked()
        self.config.system_audio_device_index = int(self.system_device_combo.currentData() or -1)
        self.config.microphone_device_index = int(self.microphone_combo.currentData() or -1)
        self.config.system_audio_device = self._device_name_by_index(self.output_devices, self.config.system_audio_device_index)
        self.config.microphone_device = self._device_name_by_index(self.input_devices, self.config.microphone_device_index)
        self.config.audio_track_mode = self.audio_mode_combo.currentText()
        self.config.audio_sample_rate = self.audio_sample_rate_spin.value()
        self.config.audio_bitrate_kbps = self.audio_bitrate_spin.value()
        super().accept()

    def _device_name_by_index(self, devices: list[dict], index_value: int) -> str:
        for device in devices:
            if device["index"] == index_value:
                return device["name"]
        return ""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = AppConfig.load()
        self.input_devices: list[dict] = []
        self.output_devices: list[dict] = []
        self.window_titles: list[str] = []
        self.capture_rect = dict_to_qrect(self.config.selected_area)
        self.recorder: Optional[RecorderThread] = None
        self.recording_started_at: Optional[float] = None
        self._build_ui()
        self.refresh_devices()
        self.refresh_windows()
        self._sync_ui_from_config()
        self._apply_theme()
        self._update_status("Ready")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick_duration)
        self.timer.start(1000)
        self.last_error_message: str = ""

    def _apply_theme(self) -> None:
        self.setStyleSheet(build_stylesheet())
        font = QFont("Consolas")
        QApplication.instance().setFont(font)

    def _build_ui(self) -> None:
        self.setWindowTitle("Screen Recorder")
        self.resize(1100, 760)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        header = QLabel("SCREEN RECORDER CONTROL")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-size: 16pt; font-weight: bold;")
        root.addWidget(header)

        summary = QLabel(
            "Capture area/window with adjustable resolution, bitrate, and audio sources. Settings are saved locally."
        )
        summary.setObjectName("subtle")
        root.addWidget(summary)

        top_grid = QGridLayout()
        root.addLayout(top_grid)

        capture_group = QGroupBox("CAPTURE")
        capture_layout = QFormLayout(capture_group)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["screen", "area", "window"])
        self.mode_combo.currentTextChanged.connect(self._mode_changed)
        capture_layout.addRow("Mode", self.mode_combo)

        self.window_combo = QComboBox()
        capture_layout.addRow("Window", self.window_combo)

        self.select_area_button = QPushButton("Select Area")
        self.select_area_button.clicked.connect(self.select_area)
        self.refresh_windows_button = QPushButton("Refresh Windows")
        self.refresh_windows_button.clicked.connect(self.refresh_windows)

        area_buttons = QHBoxLayout()
        area_buttons.addWidget(self.select_area_button)
        area_buttons.addWidget(self.refresh_windows_button)
        area_buttons_widget = QWidget()
        area_buttons_widget.setLayout(area_buttons)
        capture_layout.addRow("Area tools", area_buttons_widget)

        self.area_label = QLabel("Area: none selected")
        capture_layout.addRow("Area summary", self.area_label)

        self.output_folder_edit = QLineEdit()
        self.output_folder_browse = QPushButton("Browse")
        self.output_folder_browse.clicked.connect(self.browse_output_folder)
        output_row = QHBoxLayout()
        output_row.addWidget(self.output_folder_edit, 1)
        output_row.addWidget(self.output_folder_browse)
        output_row_widget = QWidget()
        output_row_widget.setLayout(output_row)
        capture_layout.addRow("Save folder", output_row_widget)

        self.prefix_edit = QLineEdit()
        capture_layout.addRow("Prefix", self.prefix_edit)

        top_grid.addWidget(capture_group, 0, 0)

        actions_group = QGroupBox("ACTIONS")
        actions_layout = QVBoxLayout(actions_group)

        self.start_button = QPushButton("START RECORDING")
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button = QPushButton("STOP RECORDING")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.settings_button = QPushButton("SETTINGS")
        self.settings_button.clicked.connect(self.open_settings)
        self.restart_button = QPushButton("RESTART")
        self.restart_button.clicked.connect(self.restart_app)
        self.open_folder_button = QPushButton("OPEN FOLDER")
        self.open_folder_button.clicked.connect(self.open_output_folder)

        actions_layout.addWidget(self.start_button)
        actions_layout.addWidget(self.stop_button)
        actions_layout.addWidget(self.settings_button)
        actions_layout.addWidget(self.open_folder_button)
        actions_layout.addWidget(self.restart_button)
        actions_layout.addStretch()

        top_grid.addWidget(actions_group, 0, 1)

        status_group = QGroupBox("STATUS")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel("Ready")
        self.duration_label = QLabel("Duration: 00:00:00")
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMinimumHeight(220)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.duration_label)
        status_layout.addWidget(self.details_text, 1)
        top_grid.addWidget(status_group, 1, 0, 1, 2)

        hint = QLabel(
            "Tip: use Settings for bitrate, resolution, audio devices, and container format. Area selection works like a snipping overlay."
        )
        hint.setObjectName("subtle")
        root.addWidget(hint)

    def _sync_ui_from_config(self) -> None:
        self.mode_combo.setCurrentText(self.config.capture_mode)
        self.output_folder_edit.setText(self.config.save_folder)
        self.prefix_edit.setText(self.config.filename_prefix)
        self._set_window_combo(self.config.selected_window_title)
        self.area_label.setText(self._area_summary())
        self._mode_changed(self.mode_combo.currentText())
        self._refresh_details()

    def _refresh_details(self) -> None:
        system_label = self._lookup_audio_label(
            self.config.system_audio_device_index,
            self.output_devices,
            self.config.system_audio_device,
        )
        mic_label = self._lookup_audio_label(
            self.config.microphone_device_index,
            self.input_devices,
            self.config.microphone_device,
        )
        lines = [
            f"Mode: {self.config.capture_mode}",
            f"Target: {self.config.selected_window_title or ('Area' if self.config.capture_mode == 'area' else 'Screen')}",
            f"Output: {self.config.save_folder}",
            f"Prefix: {self.config.filename_prefix}",
            f"Video: {self.config.fps} fps, {self.config.video_bitrate_kbps} kbps, {self.config.container_format}, preset={self.config.codec_preset}",
            f"Resolution: {'source' if self.config.use_source_resolution else f'{self.config.target_width}x{self.config.target_height}'}",
            f"System audio: {'on' if self.config.record_system_audio else 'off'} ({system_label})",
            f"Microphone: {'on' if self.config.record_microphone else 'off'} ({mic_label})",
            f"Audio mode: {self.config.audio_track_mode}, {self.config.audio_sample_rate} Hz, {self.config.audio_bitrate_kbps} kbps",
        ]
        self.details_text.setPlainText("\n".join(lines))

    def _lookup_audio_label(self, device_index: int, devices: list[dict], legacy_name: str) -> str:
        for device in devices:
            if device["index"] == device_index:
                return device_label(device)
        return legacy_name or "default"

    def _lookup_device_name(self, device_index: int, devices: list[dict], legacy_name: str) -> str:
        for device in devices:
            if device["index"] == device_index:
                return device["name"]
        return legacy_name or ""

    def _update_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _tick_duration(self) -> None:
        if self.recording_started_at is None:
            self.duration_label.setText("Duration: 00:00:00")
            return
        elapsed = int(time.time() - self.recording_started_at)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self.duration_label.setText(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def _area_summary(self) -> str:
        rect = self.capture_rect
        if rect.width() <= 0 or rect.height() <= 0:
            return "Area: none selected"
        return f"Area: {rect.left()}, {rect.top()}  {rect.width()}x{rect.height()}"

    def _mode_changed(self, mode: str) -> None:
        self.config.capture_mode = mode
        self.window_combo.setEnabled(mode == "window")
        self.select_area_button.setEnabled(mode == "area")
        self.area_label.setEnabled(mode == "area")
        if mode == "window" and self.window_combo.count() == 0:
            self.refresh_windows()
        self._refresh_details()

    def _set_window_combo(self, title: str) -> None:
        index = self.window_combo.findText(title)
        if index >= 0:
            self.window_combo.setCurrentIndex(index)
        elif title:
            self.window_combo.addItem(title)
            self.window_combo.setCurrentText(title)

    def browse_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Choose output folder", self.output_folder_edit.text() or str(DEFAULT_OUTPUT_DIR))
        if folder:
            self.output_folder_edit.setText(folder)
            self.config.save_folder = folder
            self.config.save()
            self._refresh_details()

    def open_output_folder(self) -> None:
        folder = Path(self.output_folder_edit.text().strip() or self.config.save_folder)
        folder.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(folder))  # type: ignore[attr-defined]
        except Exception as exc:
            QMessageBox.warning(self, "Open Folder Failed", str(exc))

    def refresh_devices(self) -> None:
        try:
            self.input_devices, self.output_devices = list_sounddevice_entries()
            self.output_devices = [device for device in self.output_devices if device["hostapi"] == "Windows WASAPI"] or self.output_devices

            if self.config.system_audio_device_index < 0 and self.output_devices:
                for device in self.output_devices:
                    if device["name"] == self.config.system_audio_device:
                        self.config.system_audio_device_index = device["index"]
                        break
                if self.config.system_audio_device_index < 0:
                    self.config.system_audio_device_index = self.output_devices[0]["index"]

            if self.config.microphone_device_index < 0 and self.input_devices:
                for device in self.input_devices:
                    if device["name"] == self.config.microphone_device:
                        self.config.microphone_device_index = device["index"]
                        break
                if self.config.microphone_device_index < 0:
                    self.config.microphone_device_index = self.input_devices[0]["index"]

            if self.config.system_audio_device_index >= 0:
                for device in self.output_devices:
                    if device["index"] == self.config.system_audio_device_index:
                        self.config.system_audio_device = device["name"]
                        break
            if self.config.microphone_device_index >= 0:
                for device in self.input_devices:
                    if device["index"] == self.config.microphone_device_index:
                        self.config.microphone_device = device["name"]
                        break
            self.config.save()
        except Exception as exc:
            QMessageBox.warning(self, "Audio Devices", f"Could not list audio devices:\n{exc}")

    def refresh_windows(self) -> None:
        self.window_titles = list_visible_windows()
        current = self.window_combo.currentText()
        self.window_combo.blockSignals(True)
        self.window_combo.clear()
        self.window_combo.addItems(self.window_titles)
        self.window_combo.blockSignals(False)
        if current:
            self._set_window_combo(current)
        if self.window_combo.count() and not self.window_combo.currentText():
            self.window_combo.setCurrentIndex(0)
        self.config.selected_window_title = self.window_combo.currentText()
        self.config.save()
        self._refresh_details()

    def select_area(self) -> None:
        overlay = AreaSelector(self)

        def on_selected(rect: QRect) -> None:
            self.capture_rect = rect
            self.config.selected_area = qrect_to_dict(rect)
            self.config.save()
            self.area_label.setText(self._area_summary())
            self._refresh_details()

        overlay.areaSelected.connect(on_selected)
        overlay.exec()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.config, self.input_devices, self.output_devices, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.config = dialog.config
            self.config.selected_area = qrect_to_dict(self.capture_rect)
            self.config.selected_window_title = self.window_combo.currentText()
            self.config.save()
            self.output_folder_edit.setText(self.config.save_folder)
            self.prefix_edit.setText(self.config.filename_prefix)
            self.mode_combo.setCurrentText(self.config.capture_mode)
            self.area_label.setText(self._area_summary())
            self._refresh_details()

    def restart_app(self) -> None:
        if self.recorder is not None:
            QMessageBox.warning(self, "Restart", "Stop recording before restarting.")
            return
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _resolve_capture_rect(self) -> QRect:
        mode = self.mode_combo.currentText()
        self.config.capture_mode = mode
        if mode == "area":
            rect = self.capture_rect
            if rect.width() <= 0 or rect.height() <= 0:
                raise RuntimeError("Choose an area first.")
            return rect
        if mode == "window":
            title = self.window_combo.currentText().strip()
            if not title:
                raise RuntimeError("Choose a window first.")
            win = get_window_by_title(title)
            if win is None:
                raise RuntimeError(f"Window not found: {title}")
            return QRect(int(win.left), int(win.top), int(win.width), int(win.height))
        with mss.mss() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            return QRect(int(monitor["left"]), int(monitor["top"]), int(monitor["width"]), int(monitor["height"]))

    def start_recording(self) -> None:
        if self.recorder is not None:
            return
        try:
            self.config.save_folder = self.output_folder_edit.text().strip() or self.config.save_folder
            self.config.filename_prefix = self.prefix_edit.text().strip() or "capture"
            self.config.selected_window_title = self.window_combo.currentText()
            self.config.capture_mode = self.mode_combo.currentText()
            self.config.selected_area = qrect_to_dict(self.capture_rect)
            self.config.system_audio_device = self._lookup_device_name(
                self.config.system_audio_device_index,
                self.output_devices,
                self.config.system_audio_device,
            )
            self.config.microphone_device = self._lookup_device_name(
                self.config.microphone_device_index,
                self.input_devices,
                self.config.microphone_device,
            )
            self.config.save()
            capture_rect = self._resolve_capture_rect()
        except Exception as exc:
            QMessageBox.warning(self, "Cannot Start", str(exc))
            return

        ffmpeg_path = get_ffmpeg_path()
        if not ffmpeg_path:
            QMessageBox.warning(
                self,
                "ffmpeg Missing",
                "ffmpeg is not available. Install ffmpeg or keep imageio-ffmpeg in the Python environment.",
            )
            return

        Path(self.config.save_folder).mkdir(parents=True, exist_ok=True)
        self.recorder = RecorderThread(self.config, capture_rect, self.window_combo.currentText(), self)
        self.recorder.status.connect(self._update_status)
        self.recorder.error.connect(self._recording_failed)
        self.recorder.finishedRecording.connect(self._recording_finished)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.recording_started_at = time.time()
        self._update_status("Preparing recording...")
        self.recorder.start()

    def stop_recording(self) -> None:
        if self.recorder is None:
            return
        self._update_status("Stopping...")
        self.recorder.stop()

    def _recording_failed(self, message: str) -> None:
        self.recording_started_at = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.recorder = None
        self.last_error_message = message
        self._update_status(f"Error: {message}")
        report = format_exception_report("Recording Failed", message)
        write_text_file(LAST_ERROR_PATH, report)
        append_text_file(ERROR_LOG_DIR / "history.log", report)
        dialog = ErrorDialog("Recording Failed", message, self)
        dialog.save_error()
        dialog.exec()

    def _recording_finished(self, output_path: str) -> None:
        self.recording_started_at = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.recorder = None
        self._update_status(f"Saved: {output_path}")
        if self.config.auto_open_folder:
            try:
                os.startfile(str(Path(output_path).parent))  # type: ignore[attr-defined]
            except Exception:
                pass

    def closeEvent(self, event):  # noqa: N802
        if self.recorder is not None:
            reply = QMessageBox.question(
                self,
                "Exit",
                "Recording is in progress. Stop and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            self.recorder.stop()
            self.recorder.wait(5000)
        self.config.save()
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
