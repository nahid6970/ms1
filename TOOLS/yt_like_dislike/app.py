import sys
import os
import re
import json
import argparse
import requests

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(data: dict):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QProgressBar, QFrame,
    QDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtSvgWidgets import QSvgWidget

# ── PALETTE ──────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

GLOBAL_QSS = f"""
QMainWindow, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
QLineEdit {{
    background-color: {CP_PANEL}; color: {CP_CYAN};
    border: 1px solid {CP_DIM}; padding: 6px;
}}
QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
QPushButton {{
    background-color: {CP_DIM}; border: 1px solid {CP_DIM};
    color: white; padding: 7px 16px; font-weight: bold;
}}
QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
QGroupBox {{
    border: 1px solid {CP_DIM}; margin-top: 12px; padding-top: 12px;
    font-weight: bold; color: {CP_YELLOW};
}}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QProgressBar {{
    background-color: {CP_PANEL}; border: 1px solid {CP_DIM};
    height: 18px; text-align: center; color: {CP_BG};
}}
QProgressBar::chunk {{ background-color: {CP_GREEN}; }}
"""


def extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
        r"^([A-Za-z0-9_-]{11})$",
    ]
    for p in patterns:
        m = re.search(p, url.strip())
        if m:
            return m.group(1)
    return None


def fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


class FetchWorker(QThread):
    done  = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, video_id: str):
        super().__init__()
        self.video_id = video_id

    def run(self):
        try:
            # title via oEmbed
            oe = requests.get(
                f"https://www.youtube.com/oembed?url=https://youtu.be/{self.video_id}&format=json",
                timeout=8
            )
            title = oe.json().get("title", "Unknown") if oe.ok else "Unknown"

            # likes/dislikes via Return YouTube Dislike
            ryd = requests.get(
                f"https://returnyoutubedislikeapi.com/votes?videoId={self.video_id}",
                timeout=8
            )
            if not ryd.ok:
                self.error.emit(f"RYD API error: {ryd.status_code}")
                return
            data = ryd.json()
            self.done.emit({
                "title":    title,
                "likes":    data.get("likes", 0),
                "dislikes": data.get("dislikes", 0),
                "views":    data.get("viewCount", 0),
                "rating":   data.get("rating", 0),
            })
        except Exception as e:
            self.error.emit(str(e))


ICONS = {
    "LIKES":    '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 21h4V9H1v12zm22-11c0-1.1-.9-2-2-2h-6.31l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 1 7.59 7.59C7.22 7.95 7 8.45 7 9v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05c.09-.23.14-.47.14-.73v-2z"/></svg>',
    "DISLIKES": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M15 3H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05c-.09.23-.14.47-.14.73v2c0 1.1.9 2 2 2h6.31l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 23l6.59-6.59c.36-.36.58-.86.58-1.41V5c0-1.1-.9-2-2-2zm4 0v12h4V3h-4z"/></svg>',
    "VIEWS":    '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>',
    "RATING":   '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>',
}


class StatBox(QFrame):
    """A labeled value box."""
    def __init__(self, label: str, color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"QFrame {{ border: 1px solid {color}; padding: 8px; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 8, 12, 8)

        self.val_lbl = QLabel("—")
        self.val_lbl.setStyleSheet(f"color: {color}; font-size: 20pt; font-weight: bold; border: none;")
        self.val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        svg = ICONS[label].replace('currentColor', color)
        self._icon = QSvgWidget()
        self._icon.setFixedSize(20, 20)
        self._icon.load(bytearray(f'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" {svg[4:]}'.encode()))
        self._icon.setStyleSheet("background: transparent; border: none;")

        icon_wrap = QWidget()
        icon_wrap.setStyleSheet("background: transparent; border: none;")
        iw_lay = QHBoxLayout(icon_wrap)
        iw_lay.setContentsMargins(0, 0, 0, 0)
        iw_lay.addStretch()
        iw_lay.addWidget(self._icon)
        iw_lay.addStretch()

        lay.addWidget(self.val_lbl)
        lay.addWidget(icon_wrap)

    def set_value(self, v: str):
        self.val_lbl.setText(v)


class SettingsDialog(QDialog):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedWidth(280)
        self.setStyleSheet(GLOBAL_QSS)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)

        title = QLabel("⚙ SETTINGS")
        title.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 11pt;")
        lay.addWidget(title)

        self.aot_cb = QCheckBox("Always on Top")
        self.aot_cb.setChecked(bool(parent.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        self.aot_cb.toggled.connect(self._toggle_aot)
        lay.addWidget(self.aot_cb)

    def _toggle_aot(self, checked: bool):
        win = self.parent()
        flags = win.windowFlags()
        if checked:
            win.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
        else:
            win.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
        win._settings['always_on_top'] = checked
        save_settings(win._settings)
        win.show()


class RatioBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(18)
        self._pct = 0  # like percentage 0-100

    def set_pct(self, pct: int):
        self._pct = pct
        self.update()

    def paintEvent(self, _):
        from PyQt6.QtGui import QPainter, QColor
        p = QPainter(self)
        w, h = self.width(), self.height()
        split = int(w * self._pct / 100)
        if split > 0:
            p.fillRect(0, 0, split, h, QColor(CP_GREEN))
        if split < w:
            p.fillRect(split, 0, w - split, h, QColor(CP_RED))


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Like/Dislike Analyzer")
        self.resize(560, 420)
        self.setStyleSheet(GLOBAL_QSS)
        self._worker = None
        self._settings = load_settings()
        if self._settings.get('always_on_top'):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # ── input ──
        grp_in = QGroupBox("VIDEO URL")
        in_lay = QHBoxLayout(grp_in)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self.url_input.returnPressed.connect(self._fetch)
        self.fetch_btn = QPushButton("ANALYZE")
        self.fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fetch_btn.clicked.connect(self._fetch)
        in_lay.addWidget(self.url_input)
        in_lay.addWidget(self.fetch_btn)
        root.addWidget(grp_in)

        # ── video title ──
        self.title_lbl = QLabel("")
        self.title_lbl.setStyleSheet(f"color: {CP_YELLOW}; font-size: 10pt;")
        self.title_lbl.setWordWrap(True)
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.title_lbl)

        # ── stat boxes ──
        grp_stats = QGroupBox("RESULTS")
        stats_lay = QHBoxLayout(grp_stats)
        self.box_likes    = StatBox("LIKES",    CP_GREEN)
        self.box_dislikes = StatBox("DISLIKES", CP_RED)
        self.box_views    = StatBox("VIEWS",    CP_CYAN)
        self.box_rating   = StatBox("RATING",   CP_YELLOW)
        for b in (self.box_likes, self.box_dislikes, self.box_views, self.box_rating):
            stats_lay.addWidget(b)
        root.addWidget(grp_stats)

        # ── ratio bar ──
        grp_ratio = QGroupBox("LIKE RATIO")
        ratio_lay = QVBoxLayout(grp_ratio)
        self.ratio_bar = RatioBar()
        self.ratio_lbl = QLabel("")
        self.ratio_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ratio_lbl.setStyleSheet(f"color: {CP_TEXT}; font-size: 9pt;")
        ratio_lay.addWidget(self.ratio_bar)
        ratio_lay.addWidget(self.ratio_lbl)
        root.addWidget(grp_ratio)

        # ── status + restart ──
        bot = QHBoxLayout()
        self.status_lbl = QLabel("Ready.")
        self.status_lbl.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt;")

        settings_btn = QPushButton("⚙ SETTINGS")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self._open_settings)

        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self._restart)
        bot.addWidget(self.status_lbl)
        bot.addStretch()
        bot.addWidget(settings_btn)
        bot.addWidget(restart_btn)
        root.addLayout(bot)

    def _set_status(self, msg: str, color: str = CP_DIM):
        self.status_lbl.setText(msg)
        self.status_lbl.setStyleSheet(f"color: {color}; font-size: 9pt;")

    def _fetch(self):
        url = self.url_input.text().strip()
        vid = extract_video_id(url)
        if not vid:
            self._set_status("⚠ Invalid YouTube URL", CP_RED)
            return

        self.fetch_btn.setEnabled(False)
        self._set_status("Fetching...", CP_CYAN)
        self.title_lbl.setText("")

        self._worker = FetchWorker(vid)
        self._worker.done.connect(self._on_done)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_done(self, d: dict):
        likes    = d["likes"]
        dislikes = d["dislikes"]
        total    = likes + dislikes

        self.title_lbl.setText(f'"{d["title"]}"')
        self.box_likes.set_value(fmt(likes))
        self.box_dislikes.set_value(fmt(dislikes))
        self.box_views.set_value(fmt(d["views"]))
        self.box_rating.set_value(f'{d["rating"]:.2f}')

        if total > 0:
            pct = int(likes / total * 100)
            self.ratio_bar.set_pct(pct)
            self.ratio_lbl.setText(
                f"{fmt(likes)} likes  vs  {fmt(dislikes)} dislikes  ({pct}% positive)"
            )
        else:
            self.ratio_bar.set_pct(0)
            self.ratio_lbl.setText("No data")

        self._set_status("✔ Done", CP_GREEN)
        self.fetch_btn.setEnabled(True)

    def _on_error(self, msg: str):
        self._set_status(f"✘ {msg}", CP_RED)
        self.fetch_btn.setEnabled(True)

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def _restart(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="", help="YouTube URL to pre-fill")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    win = App()
    if args.url:
        win.url_input.setText(args.url)
        win._fetch()
    win.show()
    sys.exit(app.exec())
