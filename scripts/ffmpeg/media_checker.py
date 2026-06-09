# -*- coding: utf-8 -*-
import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog, QTreeWidget,
    QTreeWidgetItem, QGroupBox, QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QDragEnterEvent, QDropEvent

CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"
CP_ORANGE = "#ff934b"

THEME = f"""
QMainWindow {{ background-color: {CP_BG}; }}
QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; background-color: {CP_BG}; }}
QLineEdit {{
    background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
}}
QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 14px; font-weight: bold;
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QPushButton:disabled {{ color: #555; border-color: #333; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QProgressBar {{
    background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: #000; text-align: center; font-weight: bold;
}}
QProgressBar::chunk {{ background-color: {CP_CYAN}; }}
QTreeWidget {{
    background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM};
    alternate-background-color: #161616;
}}
QTreeWidget::item:selected {{ background-color: #1a1a2e; color: {CP_CYAN}; }}
QHeaderView::section {{
    background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 4px; border: none; font-weight: bold;
}}
QScrollBar:vertical {{ background: {CP_BG}; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {CP_DIM}; min-height: 20px; border-radius: 4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

# Android-supported codecs/containers
# Video: H.264, H.265, VP8, VP9, AV1 (Android 10+), MPEG-4
# Audio: AAC, MP3, FLAC, OGG/Vorbis, WAV, OPUS, MIDI, WMA (limited)
# Containers: MP4, MKV (Android 4+), WebM, 3GP, OGG, MP3, FLAC, WAV

ANDROID_VIDEO_CODECS = {"h264", "hevc", "vp8", "vp9", "av1", "mpeg4"}
ANDROID_AUDIO_CODECS = {"aac", "mp3", "flac", "vorbis", "opus", "pcm_s16le", "pcm_s24le",
                        "pcm_u8", "pcm_f32le", "wmav2", "wmav1", "alac", "midi"}
ANDROID_CONTAINERS   = {"mp4", "mov,mp4,m4a,3gp,3g2,mj2", "matroska,webm", "mp3",
                         "flac", "ogg", "wav", "3gp", "aac", "m4a"}

MEDIA_EXTS = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv", ".wmv", ".ts", ".m4v",
              ".mp3", ".aac", ".flac", ".ogg", ".wav", ".m4a", ".opus", ".wma", ".3gp"}


def probe_file(path):
    """Returns dict with codec info or None on error."""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-print_format", "json",
             "-show_streams", "-show_format", path],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW, timeout=15
        )
        return json.loads(r.stdout)
    except Exception:
        return None


def check_android(info):
    """
    Returns (status, reason)
    status: 'ok' | 'warn' | 'fail'
    """
    if not info:
        return "fail", "Could not read file"

    fmt  = info.get("format", {}).get("format_name", "")
    streams = info.get("streams", [])

    issues = []
    has_video = any(s["codec_type"] == "video" for s in streams)

    for s in streams:
        ctype = s.get("codec_type")
        codec = s.get("codec_name", "").lower()

        if ctype == "video":
            if codec not in ANDROID_VIDEO_CODECS:
                issues.append(f"Video codec '{codec}' not supported")
            # Check for AV1 warning (needs Android 10+)
            elif codec == "av1":
                issues.append("AV1 requires Android 10+")

        elif ctype == "audio":
            if codec not in ANDROID_AUDIO_CODECS:
                issues.append(f"Audio codec '{codec}' not supported")

    # Container check
    fmt_ok = any(c in fmt for c in ["mp4", "matroska", "webm", "mp3", "flac",
                                     "ogg", "wav", "3gp", "aac", "m4a"])
    if not fmt_ok:
        issues.append(f"Container '{fmt}' may not be supported")

    if not issues:
        return "ok", "✔ Compatible"

    # Separate hard fails from warnings
    hard = [i for i in issues if "requires" not in i and "may not" not in i]
    if hard:
        return "fail", " | ".join(issues)
    return "warn", " | ".join(issues)


class ScanThread(QThread):
    result   = pyqtSignal(str, str, str, str)  # path, rel_path, status, reason
    progress = pyqtSignal(int, int)
    done     = pyqtSignal(int, int, int)        # ok, warn, fail

    def __init__(self, folder):
        super().__init__()
        self.folder = folder

    def run(self):
        files = []
        for root, _, fnames in os.walk(self.folder):
            for f in fnames:
                if os.path.splitext(f)[1].lower() in MEDIA_EXTS:
                    files.append(os.path.join(root, f))

        total = len(files)
        counts = {"ok": 0, "warn": 0, "fail": 0}
        for i, path in enumerate(files):
            info   = probe_file(path)
            status, reason = check_android(info)
            rel    = os.path.relpath(path, self.folder)
            self.result.emit(path, rel, status, reason)
            counts[status] += 1
            self.progress.emit(i + 1, total)

        self.done.emit(counts["ok"], counts["warn"], counts["fail"])


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📱 ANDROID MEDIA CHECKER")
        self.resize(900, 640)
        self.setAcceptDrops(True)
        self.thread = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("📱 ANDROID MEDIA CHECKER")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-size: 14pt; font-weight: bold; background: transparent;")
        root.addWidget(title)

        # Folder input
        fg = QGroupBox("SCAN FOLDER  (drag & drop folder here)")
        fl = QHBoxLayout(fg)
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Drop a folder or click Browse…")
        browse_btn = QPushButton("📁 BROWSE")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self.browse)
        fl.addWidget(self.folder_input)
        fl.addWidget(browse_btn)
        root.addWidget(fg)

        # Progress
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFormat("Idle")
        root.addWidget(self.progress)

        # Summary
        self.summary_lbl = QLabel("")
        self.summary_lbl.setStyleSheet(f"color: {CP_DIM}; background: transparent; font-size: 9pt;")
        root.addWidget(self.summary_lbl)

        # Results tree
        self.tree = QTreeWidget()
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["FILE", "STATUS", "DETAILS"])
        self.tree.setColumnWidth(0, 380)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 380)
        root.addWidget(self.tree)

        # Buttons
        btn_row = QHBoxLayout()
        self.scan_btn = QPushButton("🔍  SCAN")
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.setStyleSheet(
            f"QPushButton {{ background: {CP_GREEN}; color: black; border: none; padding: 8px 20px; font-size: 11pt; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {CP_YELLOW}; }}")
        self.scan_btn.clicked.connect(self.start_scan)

        filter_row = QHBoxLayout()
        for label, color, attr in [("ALL", CP_TEXT, "_btn_all"),
                                    ("✔ OK", CP_GREEN, "_btn_ok"),
                                    ("⚠ WARN", CP_ORANGE, "_btn_warn"),
                                    ("✘ FAIL", CP_RED, "_btn_fail")]:
            b = QPushButton(label)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"QPushButton {{ color: {color}; }}")
            b.clicked.connect(lambda _, lbl=label: self.filter(lbl))
            setattr(self, attr, b)
            filter_row.addWidget(b)

        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(lambda: os.execv(sys.executable, [sys.executable] + sys.argv))

        btn_row.addWidget(self.scan_btn)
        btn_row.addLayout(filter_row)
        btn_row.addStretch()
        btn_row.addWidget(restart_btn)
        root.addLayout(btn_row)

        self._all_results = []  # list of (rel_path, status, reason)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls(): e.acceptProposedAction()
    def dragMoveEvent(self, e): e.acceptProposedAction()
    def dropEvent(self, e: QDropEvent):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.folder_input.setText(path)
                break

    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder")
        if d: self.folder_input.setText(d)

    def start_scan(self):
        folder = self.folder_input.text().strip()
        if not folder or not os.path.isdir(folder):
            self.summary_lbl.setText("⚠ Please select a valid folder."); return

        self.tree.clear()
        self._all_results.clear()
        self.scan_btn.setEnabled(False)
        self.progress.setFormat("Scanning…")

        self.thread = ScanThread(folder)
        self.thread.result.connect(self.add_result)
        self.thread.progress.connect(self.on_progress)
        self.thread.done.connect(self.on_done)
        self.thread.start()

    def on_progress(self, cur, total):
        self.progress.setMaximum(total)
        self.progress.setValue(cur)
        self.progress.setFormat(f"{cur} / {total}")

    def add_result(self, path, rel_path, status, reason):
        self._all_results.append((rel_path, status, reason))
        if status != "ok":
            self._add_tree_row(rel_path, status, reason)

    def _add_tree_row(self, rel_path, status, reason):
        if status == "ok":
            icon, color = "✔", CP_GREEN
        elif status == "warn":
            icon, color = "⚠", CP_ORANGE
        else:
            icon, color = "✘", CP_RED

        item = QTreeWidgetItem([rel_path, icon, reason])
        item.setForeground(1, QColor(color))
        item.setForeground(0, QColor(CP_TEXT))
        item.setForeground(2, QColor(CP_DIM if status == "ok" else color))
        item.setData(0, Qt.ItemDataRole.UserRole, status)
        self.tree.addTopLevelItem(item)

    def on_done(self, ok, warn, fail):
        self.scan_btn.setEnabled(True)
        self.progress.setFormat("Done")
        self.summary_lbl.setText(
            f"✔ Compatible: {ok}   ⚠ Warning: {warn}   ✘ Incompatible: {fail}   "
            f"(Total: {ok+warn+fail})")
        self.summary_lbl.setStyleSheet(f"color: {CP_TEXT}; background: transparent; font-size: 9pt;")

    def filter(self, label):
        self.tree.clear()
        for rel_path, status, reason in self._all_results:
            if label == "ALL":
                self._add_tree_row(rel_path, status, reason)
            elif label == "✔ OK"   and status == "ok":   self._add_tree_row(rel_path, status, reason)
            elif label == "⚠ WARN" and status == "warn": self._add_tree_row(rel_path, status, reason)
            elif label == "✘ FAIL" and status == "fail": self._add_tree_row(rel_path, status, reason)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(THEME)
    w = App()
    w.show()
    sys.exit(app.exec())
