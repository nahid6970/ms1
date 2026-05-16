import sys
import os
import subprocess
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

class ConvertThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, input_file, output_file, dim, target_kb):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.dim = dim
        self.target_kb = target_kb
    
    def _build_cmd(self, quality, density=None):
        is_pdf = self.input_file.lower().endswith('.pdf')
        if is_pdf:
            return ['magick', '-density', str(density or 150), self.input_file + '[0]',
                    '-resize', self.dim, '-quality', str(quality),
                    '-background', 'white', '-alpha', 'remove', self.output_file]
        return ['magick', self.input_file, '-resize', self.dim, '-quality', str(quality), self.output_file]

    def run(self):
        try:
            is_pdf = self.input_file.lower().endswith('.pdf')
            target_bytes = self.target_kb * 1024
            quality = 95

            # Initial conversion
            result = subprocess.run(self._build_cmd(quality), capture_output=True, text=True)
            if result.returncode != 0:
                err = result.stderr
                if 'ghostscript' in err.lower() or 'gswin' in err.lower():
                    self.error.emit("Ghostscript not found. Install from: https://ghostscript.com/releases/gsdnld.html")
                else:
                    self.error.emit(f"Conversion failed: {err.split('magick:')[-1].strip()[:200]}")
                return

            current_size = os.path.getsize(self.output_file)

            if current_size > target_bytes:
                # Shrink: reduce quality
                while os.path.getsize(self.output_file) > target_bytes and quality > 10:
                    quality -= 5
                    subprocess.run(self._build_cmd(quality), capture_output=True)

            elif current_size < target_bytes and not is_pdf:
                # Inflate: increase quality then pad with a comment chunk
                # First push quality to 100
                subprocess.run(self._build_cmd(100), capture_output=True)
                current_size = os.path.getsize(self.output_file)

                # If still under target, pad the file with a harmless JPEG comment
                if current_size < target_bytes:
                    pad_needed = target_bytes - current_size
                    ext = Path(self.output_file).suffix.lower()
                    if ext in ('.jpg', '.jpeg'):
                        # Append JPEG comment marker (0xFFFE) with padding
                        with open(self.output_file, 'ab') as f:
                            # JPEG comment: FF FE + 2-byte length (length includes the 2 length bytes)
                            chunk_size = min(pad_needed, 65533)  # max JPEG comment payload
                            written = 0
                            while written < pad_needed:
                                payload = min(65533, pad_needed - written)
                                f.write(b'\xff\xfe')
                                f.write((payload + 2).to_bytes(2, 'big'))
                                f.write(b'\x00' * payload)
                                written += payload
                    elif ext == '.png':
                        # Append a PNG tEXt chunk with padding data
                        with open(self.output_file, 'ab') as f:
                            import struct, zlib
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
        self.resize(700, 500)
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
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
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
        
        # Header
        header = QLabel("FILE CONVERTER")
        header.setStyleSheet(f"font-size: 18pt; color: {CP_YELLOW}; font-weight: bold;")
        layout.addWidget(header)
        
        # Input Group
        grp_input = QGroupBox("INPUT FILE")
        form_input = QHBoxLayout()
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Select input file...")
        btn_browse_input = QPushButton("BROWSE")
        btn_browse_input.clicked.connect(self.browse_input)
        btn_browse_input.setCursor(Qt.CursorShape.PointingHandCursor)
        form_input.addWidget(self.input_path)
        form_input.addWidget(btn_browse_input)
        grp_input.setLayout(form_input)
        
        # Output Group
        grp_output = QGroupBox("OUTPUT FILE")
        form_output = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setPlaceholderText("Select output file...")
        btn_browse_output = QPushButton("BROWSE")
        btn_browse_output.clicked.connect(self.browse_output)
        btn_browse_output.setCursor(Qt.CursorShape.PointingHandCursor)
        form_output.addWidget(self.output_path)
        form_output.addWidget(btn_browse_output)
        grp_output.setLayout(form_output)
        
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
        self.max_size.setSuffix(" KB")
        self.max_size.setKeyboardTracking(False)
        
        form_settings.addRow("Width:", self.width_input)
        form_settings.addRow("Height:", self.height_input)
        form_settings.addRow("Target Size:", self.max_size)
        grp_settings.setLayout(form_settings)
        
        # Action Buttons
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
        
        # Status
        self.status = QLineEdit("READY...")
        self.status.setReadOnly(True)
        self.status.setStyleSheet(f"color: {CP_CYAN}; padding: 10px; border: 1px solid {CP_DIM};")
        
        layout.addWidget(grp_input)
        layout.addWidget(grp_output)
        layout.addWidget(grp_settings)
        layout.addLayout(btn_layout)
        layout.addWidget(self.status)
        layout.addStretch()

    def browse_input(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", 
                                              "All Files (*.pdf *.jpg *.jpeg *.png *.bmp *.gif)")
        if file:
            self.input_path.setText(file)
    
    def browse_output(self):
        file, _ = QFileDialog.getSaveFileName(self, "Select Output File", "",
                                              "JPEG (*.jpg);;PNG (*.png);;PDF (*.pdf);;All Files (*.*)")
        if file:
            self.output_path.setText(file)
    
    def convert(self):
        input_file = self.input_path.text()
        output_file = self.output_path.text()
        
        if not input_file or not output_file:
            self.status.setText("ERROR: Select input and output files")
            self.status.setStyleSheet(f"color: {CP_RED}; padding: 10px;")
            return
        
        if not os.path.exists(input_file):
            self.status.setText("ERROR: Input file not found")
            self.status.setStyleSheet(f"color: {CP_RED}; padding: 10px;")
            return
        
        dim = f"{self.width_input.text()}x{self.height_input.text()}"
        max_kb = self.max_size.value()
        
        self.status.setText("CONVERTING...")
        self.status.setStyleSheet(f"color: {CP_YELLOW}; padding: 10px;")
        
        self.thread = ConvertThread(input_file, output_file, dim, max_kb)
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
