import sys
import os
import subprocess
import struct
import zlib
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, QFileDialog, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_GREEN = "#00ff21"
CP_RED = "#FF003C"


def get_image_dimensions(path):
    """Return (width, height) using ImageMagick identify, or None on failure."""
    try:
        r = subprocess.run(['magick', 'identify', '-format', '%wx%h', path],
                           capture_output=True, text=True)
        if r.returncode == 0:
            w, h = r.stdout.strip().split('x')
            return int(w), int(h)
    except Exception:
        pass
    return None


def auto_output_path(input_path):
    p = Path(input_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(p.parent / f"{p.stem}_{ts}{p.suffix}")


class DropLineEdit(QLineEdit):
    """QLineEdit that accepts dropped files."""
    file_dropped = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.setText(path)
            self.file_dropped.emit(path)


class ConvertThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, input_file, output_file, dim, target_kb):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.dim = dim
        self.target_kb = target_kb

    def _build_cmd(self, quality):
        is_pdf = self.input_file.lower().endswith('.pdf')
        if is_pdf:
            return ['magick', '-density', '150', self.input_file + '[0]',
                    '-resize', self.dim, '-quality', str(quality),
                    '-background', 'white', '-alpha', 'remove', self.output_file]
        return ['magick', self.input_file, '-resize', self.dim, '-quality', str(quality), self.output_file]

    def run(self):
        try:
            is_pdf = self.input_file.lower().endswith('.pdf')
            target_bytes = self.target_kb * 1024
            quality = 95

            result = subprocess.run(self._build_cmd(quality), capture_output=True, text=True)
            if result.returncode != 0:
                err = result.stderr
                if 'ghostscript' in err.lower() or 'gswin' in err.lower():
                    self.error.emit("Ghostscript not found. Install from: https://ghostscript.com/releases/gsdnld.html")
                else:
                    self.error.emit(f"Conversion failed: {err.split('magick:')[-1].strip()[:200]}")
                return

            if os.path.getsize(self.output_file) > target_bytes:
                # Phase 1: reduce quality
                while os.path.getsize(self.output_file) > target_bytes and quality > 10:
                    quality -= 5
                    subprocess.run(self._build_cmd(quality), capture_output=True)
                # Phase 2: if still too large, progressively scale down dimensions
                if os.path.getsize(self.output_file) > target_bytes:
                    w, h = (int(x) for x in self.dim.split('x'))
                    scale = 0.9
                    while os.path.getsize(self.output_file) > target_bytes and scale > 0.05:
                        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
                        cmd = self._build_cmd(10)
                        # replace the dim in the command
                        cmd[cmd.index('-resize') + 1] = f"{nw}x{nh}"
                        subprocess.run(cmd, capture_output=True)
                        scale -= 0.1

            elif os.path.getsize(self.output_file) < target_bytes and not is_pdf:
                subprocess.run(self._build_cmd(100), capture_output=True)
                pad_needed = target_bytes - os.path.getsize(self.output_file)
                if pad_needed > 0:
                    ext = Path(self.output_file).suffix.lower()
                    with open(self.output_file, 'ab') as f:
                        if ext in ('.jpg', '.jpeg'):
                            written = 0
                            while written < pad_needed:
                                payload = min(65533, pad_needed - written)
                                f.write(b'\xff\xfe')
                                f.write((payload + 2).to_bytes(2, 'big'))
                                f.write(b'\x00' * payload)
                                written += payload
                        elif ext == '.png':
                            remaining = pad_needed
                            while remaining > 0:
                                payload_size = min(remaining - 12, 65000)
                                if payload_size <= 0:
                                    break
                                data = b'Comment\x00' + b'\x00' * (payload_size - 8)
                                crc = zlib.crc32(b'tEXt' + data) & 0xffffffff
                                f.write(struct.pack('>I', len(data)))
                                f.write(b'tEXt')
                                f.write(data)
                                f.write(struct.pack('>I', crc))
                                remaining -= (len(data) + 12)

            size_kb = os.path.getsize(self.output_file) / 1024
            self.finished.emit(f"Created: {Path(self.output_file).name} ({self.dim}, {size_kb:.1f}KB)")
        except Exception as e:
            self.error.emit(str(e))


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FILE CONVERTER // CYBERPUNK")
        self.resize(700, 460)
        self.script_path = Path(__file__).resolve()

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit, QSpinBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px;
            }}
            QLineEdit:focus, QSpinBox:focus {{ border: 1px solid {CP_CYAN}; }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; border: none; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
                padding: 8px 16px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px;
                font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        header = QLabel("FILE CONVERTER")
        header.setStyleSheet(f"font-size: 18pt; color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(header)

        # Input Group (drag & drop)
        grp_input = QGroupBox("INPUT FILE  [ drag & drop or browse ]")
        form_input = QHBoxLayout()
        self.input_path = DropLineEdit()
        self.input_path.setPlaceholderText("Drag image here or click BROWSE...")
        self.input_path.file_dropped.connect(self.on_file_loaded)
        btn_browse_input = QPushButton("BROWSE")
        btn_browse_input.clicked.connect(self.browse_input)
        btn_browse_input.setCursor(Qt.CursorShape.PointingHandCursor)
        form_input.addWidget(self.input_path)
        form_input.addWidget(btn_browse_input)
        grp_input.setLayout(form_input)

        # Settings Group
        grp_settings = QGroupBox("CONVERSION SETTINGS")
        form_settings = QFormLayout()

        self.width_input = QLineEdit("800")
        self.width_input.setPlaceholderText("e.g. 1920")

        self.height_input = QLineEdit("800")
        self.height_input.setPlaceholderText("e.g. 1080")

        self.max_size = QSpinBox()
        self.max_size.setRange(1, 102400)
        self.max_size.setValue(400)
        self.max_size.setKeyboardTracking(False)

        form_settings.addRow("Width:", self.width_input)
        form_settings.addRow("Height:", self.height_input)
        form_settings.addRow("Target Size (KB):", self.max_size)
        grp_settings.setLayout(form_settings)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_convert = QPushButton("CONVERT")
        btn_convert.clicked.connect(self.convert)
        btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_convert.setStyleSheet(f"""
            QPushButton {{ background-color: {CP_GREEN}; color: black; border: 1px solid {CP_GREEN}; }}
            QPushButton:hover {{ background-color: #00cc1a; }}
        """)
        btn_restart = QPushButton("RESTART")
        btn_restart.clicked.connect(self.restart)
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(btn_convert)
        btn_layout.addWidget(btn_restart)

        self.status = QLineEdit("READY...")
        self.status.setReadOnly(True)
        self.status.setStyleSheet(f"color: {CP_CYAN}; padding: 10px; border: 1px solid {CP_DIM};")

        layout.addWidget(grp_input)
        layout.addWidget(grp_settings)
        layout.addLayout(btn_layout)
        layout.addWidget(self.status)
        layout.addStretch()

    def on_file_loaded(self, path):
        dims = get_image_dimensions(path)
        if dims:
            self.width_input.setText(str(dims[0]))
            self.height_input.setText(str(dims[1]))
            size_kb = os.path.getsize(path) // 1024
            self.max_size.setValue(max(1, size_kb))
            self.status.setText(f"Loaded: {Path(path).name}  ({dims[0]}x{dims[1]}, {size_kb}KB)")
            self.status.setStyleSheet(f"color: {CP_CYAN}; padding: 10px; border: 1px solid {CP_DIM};")

    def browse_input(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Input File", "",
                                              "All Files (*.pdf *.jpg *.jpeg *.png *.bmp *.gif)")
        if file:
            self.input_path.setText(file)
            self.on_file_loaded(file)

    def convert(self):
        input_file = self.input_path.text().strip()
        if not input_file:
            self.status.setText("ERROR: Select an input file")
            self.status.setStyleSheet(f"color: {CP_RED}; padding: 10px;")
            return
        if not os.path.exists(input_file):
            self.status.setText("ERROR: Input file not found")
            self.status.setStyleSheet(f"color: {CP_RED}; padding: 10px;")
            return

        output_file = auto_output_path(input_file)
        dim = f"{self.width_input.text()}x{self.height_input.text()}"

        self.status.setText("CONVERTING...")
        self.status.setStyleSheet(f"color: {CP_YELLOW}; padding: 10px;")

        self.thread = ConvertThread(input_file, output_file, dim, self.max_size.value())
        self.thread.finished.connect(self.on_success)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_success(self, msg):
        self.status.setText(f"SUCCESS: {msg}")
        self.status.setStyleSheet(f"color: {CP_GREEN}; padding: 10px;")

    def on_error(self, msg):
        self.status.setText(f"ERROR: {msg}")
        self.status.setStyleSheet(f"color: {CP_RED}; padding: 10px;")

    def restart(self):
        QApplication.quit()
        subprocess.Popen([sys.executable, str(self.script_path)])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
