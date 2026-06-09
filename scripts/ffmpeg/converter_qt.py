# -*- coding: utf-8 -*-
import sys
import os
import re
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QComboBox, QProgressBar,
    QGroupBox, QFormLayout, QFileDialog, QListWidget, QListWidgetItem,
    QScrollArea, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

THEME = f"""
QMainWindow {{ background-color: {CP_BG}; }}
QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; background-color: {CP_BG}; }}
QLineEdit, QComboBox {{
    background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
}}
QLineEdit:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{ background-color: {CP_PANEL}; color: {CP_CYAN};
    selection-background-color: {CP_CYAN}; selection-color: #000; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white;
    padding: 6px 14px; font-weight: bold;
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QPushButton:disabled {{ color: #555; border-color: #333; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QProgressBar {{
    background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: #000;
    text-align: center; font-weight: bold;
}}
QProgressBar::chunk {{ background-color: {CP_CYAN}; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: {CP_BG}; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {CP_DIM}; min-height: 20px; border-radius: 4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

ENCODERS = {
    "H.264 AMF (AMD GPU) — Recommended":     ("h264_amf", "aac", "mp4"),
    "H.265 AMF (AMD GPU) — Better quality":  ("hevc_amf", "aac", "mp4"),
    "H.264 CPU (libx264) — Compatible fallback": ("libx264", "aac", "mp4"),
}


# ── Per-file row widget ────────────────────────────────────────────────────────
class FileRow(QWidget):
    remove_clicked = pyqtSignal(object)  # emits self

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setFixedHeight(28)

        row = QHBoxLayout(self)
        row.setContentsMargins(4, 0, 4, 0)
        row.setSpacing(6)

        self.name_lbl = QLabel(os.path.basename(path))
        self.name_lbl.setStyleSheet(f"color: {CP_CYAN}; background: transparent;")

        self.status_lbl = QLabel("")
        self.status_lbl.setFixedWidth(52)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_lbl.setStyleSheet("color: #808080; background: transparent; font-size: 9pt;")

        rm = QPushButton("✕")
        rm.setFixedSize(20, 20)
        rm.setStyleSheet(f"QPushButton {{ background: transparent; border: none; color: {CP_DIM}; font-size: 9pt; }}"
                         f"QPushButton:hover {{ color: {CP_RED}; }}")
        rm.setCursor(Qt.CursorShape.PointingHandCursor)
        rm.clicked.connect(lambda: self.remove_clicked.emit(self))

        row.addWidget(self.name_lbl, stretch=1)
        row.addWidget(self.status_lbl)
        row.addWidget(rm)

    def set_progress(self, pct: int):
        self.status_lbl.setStyleSheet("color: #808080; background: transparent; font-size: 9pt;")
        self.status_lbl.setText(f"{pct}%")

    def set_done(self):
        self.status_lbl.setStyleSheet(f"color: {CP_GREEN}; background: transparent; font-size: 11pt;")
        self.status_lbl.setText("✔")

    def set_failed(self):
        self.status_lbl.setStyleSheet(f"color: {CP_RED}; background: transparent; font-size: 11pt;")
        self.status_lbl.setText("✘")

    def reset(self):
        self.status_lbl.setStyleSheet("color: #808080; background: transparent; font-size: 9pt;")
        self.status_lbl.setText("")


# ── Drop area containing FileRows ──────────────────────────────────────────────
class FilePanel(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setWidgetResizable(True)
        self.setMinimumHeight(130)

        self._container = QWidget()
        self._layout    = QVBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        self._layout.addStretch()
        self.setWidget(self._container)

        self._rows: list[FileRow] = []

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dragMoveEvent(self, e): e.acceptProposedAction()
    def dropEvent(self, e: QDropEvent):
        for url in e.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p): self.add(p)

    def add(self, path):
        if any(r.path == path for r in self._rows): return
        row = FileRow(path)
        row.remove_clicked.connect(self._remove)
        self._layout.insertWidget(self._layout.count() - 1, row)
        self._rows.append(row)

    def _remove(self, row: FileRow):
        self._rows.remove(row)
        self._layout.removeWidget(row)
        row.deleteLater()

    def clear_all(self):
        for r in list(self._rows): self._remove(r)

    def get_paths(self):
        return [r.path for r in self._rows]

    def row_at(self, idx) -> FileRow:
        return self._rows[idx]

    def reset_statuses(self):
        for r in self._rows: r.reset()


# ── Conversion thread ──────────────────────────────────────────────────────────
class ConvertThread(QThread):
    file_progress = pyqtSignal(int, int)   # file_index, 0-100
    file_done     = pyqtSignal(int, bool)  # file_index, success
    total_progress = pyqtSignal(int, int)  # completed, total
    status        = pyqtSignal(str)
    done          = pyqtSignal()

    def __init__(self, files, encoder, crf, audio_codec, ext):
        super().__init__()
        self.files, self.encoder, self.crf = files, encoder, crf
        self.audio_codec, self.ext = audio_codec, ext
        self._cancel = False
        self._proc   = None

    def cancel(self):
        self._cancel = True
        if self._proc: self._proc.terminate()

    def _duration_us(self, path):
        try:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return float(r.stdout.strip()) * 1_000_000
        except Exception:
            return 0

    def run(self):
        total = len(self.files)
        for i, path in enumerate(self.files):
            if self._cancel:
                self.status.emit("⛔ Cancelled.")
                break
            self.status.emit(f"Encoding [{i+1}/{total}]: {os.path.basename(path)}")
            self.file_progress.emit(i, 0)
            dur = self._duration_us(path)

            base, _ = os.path.splitext(path)
            out     = base + "_new." + self.ext
            cmd = ["ffmpeg", "-y", "-progress", "pipe:2", "-nostats", "-i", path]
            if self.encoder in ("h264_amf", "hevc_amf"):
                cmd += ["-c:v", self.encoder, "-quality", "balanced",
                        "-rc", "cqp", "-qp_i", str(self.crf), "-qp_p", str(self.crf)]
            else:
                cmd += ["-c:v", self.encoder, "-crf", str(self.crf), "-preset", "fast"]
            cmd += ["-c:a", self.audio_codec, "-b:a", "128k", out]

            self._proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                          text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            for line in self._proc.stderr:
                if self._cancel: break
                m = re.match(r"out_time_us=(\d+)", line.strip())
                if m and dur > 0:
                    pct = min(int(int(m.group(1)) / dur * 100), 99)
                    self.file_progress.emit(i, pct)
            self._proc.wait()

            ok = self._proc.returncode == 0
            self.file_done.emit(i, ok)
            self.total_progress.emit(i + 1, total)
        self.done.emit()


# ── Main window ────────────────────────────────────────────────────────────────
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ VIDEO CONVERTER — MOBILE COMPATIBLE")
        self.resize(700, 600)
        self.thread = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("⚡ VIDEO CONVERTER")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-size: 14pt; font-weight: bold; background: transparent;")
        root.addWidget(title)

        # Files
        fg = QGroupBox("INPUT FILES  (drag & drop or browse)")
        fl = QVBoxLayout(fg)
        self.file_panel = FilePanel()
        fl.addWidget(self.file_panel)
        btn_row = QHBoxLayout()
        for label, slot in [("＋ ADD FILES", self.add_files),
                             ("✕ REMOVE SELECTED", self._remove_noop),
                             ("⌫ CLEAR ALL", self.file_panel.clear_all)]:
            b = QPushButton(label)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(slot)
            btn_row.addWidget(b)
        fl.addLayout(btn_row)
        root.addWidget(fg)

        # Settings
        sg = QGroupBox("SETTINGS")
        sf = QFormLayout(sg)
        self.encoder_combo = QComboBox()
        for lbl in ENCODERS: self.encoder_combo.addItem(lbl)

        self.crf_input = QLineEdit("22")
        self.crf_input.setMaximumWidth(60)
        crf_note = QLabel("  lower = better quality  |  AMF sweet spot: 18-28")
        crf_note.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt; background: transparent;")
        crf_w = QWidget(); cr = QHBoxLayout(crf_w); cr.setContentsMargins(0,0,0,0)
        cr.addWidget(self.crf_input); cr.addWidget(crf_note); cr.addStretch()

        sf.addRow("Encoder:", self.encoder_combo)
        sf.addRow("Quality (QP/CRF):", crf_w)
        root.addWidget(sg)

        # Total progress
        pg_row = QHBoxLayout()
        pg_lbl = QLabel("TOTAL:")
        pg_lbl.setStyleSheet(f"color: {CP_DIM}; background: transparent;")
        pg_lbl.setFixedWidth(55)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        pg_row.addWidget(pg_lbl)
        pg_row.addWidget(self.progress)
        root.addLayout(pg_row)

        # Status
        self.status_lbl = QLabel("Ready.")
        self.status_lbl.setStyleSheet(f"color: {CP_GREEN}; background: transparent; font-size: 9pt;")
        self.status_lbl.setWordWrap(True)
        root.addWidget(self.status_lbl)

        # Buttons
        action_row = QHBoxLayout()
        self.convert_btn = QPushButton("▶  CONVERT")
        self.convert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.convert_btn.setStyleSheet(
            f"QPushButton {{ background: {CP_GREEN}; color: black; border: none; padding: 8px 20px; font-size: 11pt; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {CP_YELLOW}; }}")
        self.convert_btn.clicked.connect(self.start_convert)

        self.cancel_btn = QPushButton("⛔  CANCEL")
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_convert)

        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))

        action_row.addWidget(self.convert_btn)
        action_row.addWidget(self.cancel_btn)
        action_row.addStretch()
        action_row.addWidget(restart_btn)
        root.addLayout(action_row)

    def _remove_noop(self):
        pass  # FileRow has its own ✕ button; this btn kept for symmetry, could remove

    def add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Videos", "D:\\song",
            "Video Files (*.webm *.mp4 *.mkv *.avi *.mov *.flv *.wmv *.ts)")
        for p in paths: self.file_panel.add(p)

    def start_convert(self):
        files = self.file_panel.get_paths()
        if not files:
            QMessageBox.warning(self, "No files", "Add some video files first."); return

        enc, aud, ext = ENCODERS[self.encoder_combo.currentText()]
        try: crf = int(self.crf_input.text())
        except ValueError: crf = 22

        self.file_panel.reset_statuses()
        self.progress.setMaximum(len(files))
        self.progress.setValue(0)
        self.convert_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

        self.thread = ConvertThread(files, enc, crf, aud, ext)
        self.thread.file_progress.connect(
            lambda idx, pct: self.file_panel.row_at(idx).set_progress(pct))
        self.thread.file_done.connect(
            lambda idx, ok: self.file_panel.row_at(idx).set_done() if ok
                            else self.file_panel.row_at(idx).set_failed())
        self.thread.total_progress.connect(
            lambda cur, _: self.progress.setValue(cur))
        self.thread.status.connect(self.status_lbl.setText)
        self.thread.done.connect(self.on_done)
        self.thread.start()

    def cancel_convert(self):
        if self.thread: self.thread.cancel()

    def on_done(self):
        self.convert_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_lbl.setText("✔ All done!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME)
    w = App()
    w.show()
    sys.exit(app.exec())
