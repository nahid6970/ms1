import sys
import os
import re
import argparse
import requests
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

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
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
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

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt; border: none;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(self.val_lbl)
        lay.addWidget(lbl)

    def set_value(self, v: str):
        self.val_lbl.setText(v)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT Like/Dislike Analyzer")
        self.resize(560, 420)
        self.setStyleSheet(GLOBAL_QSS)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # ── title bar ──
        title = QLabel("◈ YT LIKE / DISLIKE ANALYZER ◈")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 13pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

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
        self.ratio_bar = QProgressBar()
        self.ratio_bar.setRange(0, 100)
        self.ratio_bar.setValue(0)
        self.ratio_bar.setFormat("—")
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
        restart_btn = QPushButton("↺ RESTART")
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self._restart)
        bot.addWidget(self.status_lbl)
        bot.addStretch()
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
            self.ratio_bar.setValue(pct)
            self.ratio_bar.setFormat(f"{pct}%")
            # color bar red if mostly disliked
            bar_color = CP_GREEN if pct >= 50 else CP_RED
            self.ratio_bar.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {bar_color}; }}"
            )
            self.ratio_lbl.setText(
                f"{fmt(likes)} likes  vs  {fmt(dislikes)} dislikes  ({pct}% positive)"
            )
        else:
            self.ratio_bar.setValue(0)
            self.ratio_bar.setFormat("No data")
            self.ratio_lbl.setText("")

        self._set_status("✔ Done", CP_GREEN)
        self.fetch_btn.setEnabled(True)

    def _on_error(self, msg: str):
        self._set_status(f"✘ {msg}", CP_RED)
        self.fetch_btn.setEnabled(True)

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
