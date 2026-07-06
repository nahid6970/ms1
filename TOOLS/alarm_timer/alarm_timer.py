# alarm_timer.py  –  Multi-column Alarm Countdown Timer
# Cyberpunk theme  |  PyQt6
# ============================================================

import sys
import os
import re
import json
import uuid
import time
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QDialog,
    QFormLayout, QGroupBox, QFrame, QSizePolicy, QInputDialog,
    QMessageBox, QDateTimeEdit, QRadioButton,
    QButtonGroup, QDialogButtonBox, QGridLayout,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime, QByteArray, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QIcon
from PyQt6.QtSvg import QSvgRenderer

# ── SVG icon helper ────────────────────────────────────────

def svg_icon(svg_str: str, size: int = 18) -> QIcon:
    """Render an inline SVG string into a QIcon."""
    ba = QByteArray(svg_str.encode())
    renderer = QSvgRenderer(ba)
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.end()
    return QIcon(pm)

def _svg(path_d: str, color: str, vb: str = "0 0 24 24") -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'
            f'<path fill="{color}" d="{path_d}"/></svg>')

def icon_play(color: str = "#00ff21", size: int = 16) -> QIcon:
    return svg_icon(_svg("M8 5v14l11-7z", color), size)

def icon_pause(color: str = "#ff934b", size: int = 16) -> QIcon:
    return svg_icon(_svg("M6 19h4V5H6v14zm8-14v14h4V5h-4z", color), size)

def icon_reset(color: str = "#E0E0E0", size: int = 16) -> QIcon:
    return svg_icon(_svg(
        "M17.65 6.35A7.958 7.958 0 0 0 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 "
        "7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0 1 12 18c-3.31 "
        "0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z",
        color), size)

def icon_rename(color: str = "#00F0FF", size: int = 16) -> QIcon:
    return svg_icon(_svg(
        "M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 "
        "0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z",
        color), size)

def icon_delete(color: str = "#FF003C", size: int = 16) -> QIcon:
    return svg_icon(_svg(
        "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 "
        "1H5v2h14V4z",
        color), size)

def icon_duplicate(color: str = "#00F0FF", size: int = 16) -> QIcon:
    return svg_icon(_svg(
        "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 "
        "1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z",
        color), size)

# ── Cyberpunk Palette ──────────────────────────────────────
CP_BG      = "#050505"
CP_PANEL   = "#111111"
CP_YELLOW  = "#FCEE0A"
CP_CYAN    = "#00F0FF"
CP_RED     = "#FF003C"
CP_GREEN   = "#00ff21"
CP_ORANGE  = "#ff934b"
CP_DIM     = "#3a3a3a"
CP_TEXT    = "#E0E0E0"
CP_SUBTEXT = "#808080"

# ── Global Stylesheet ──────────────────────────────────────
GLOBAL_QSS = f"""
QMainWindow, QDialog {{
    background-color: {CP_BG};
}}
QWidget {{
    color: {CP_TEXT};
    font-family: 'Consolas';
    font-size: 10pt;
    background-color: transparent;
}}
QLineEdit, QSpinBox, QComboBox, QDateTimeEdit {{
    background-color: {CP_PANEL};
    color: {CP_CYAN};
    border: 1px solid {CP_DIM};
    padding: 4px;
    selection-background-color: {CP_CYAN};
    selection-color: #000000;
}}
QLineEdit:focus, QDateTimeEdit:focus {{
    border: 1px solid {CP_CYAN};
}}
QDateTimeEdit::drop-down {{
    border: none;
    background: {CP_DIM};
    width: 18px;
}}
QCalendarWidget QAbstractItemView {{
    background-color: {CP_PANEL};
    color: {CP_TEXT};
    selection-background-color: {CP_CYAN};
    selection-color: #000;
}}
QCalendarWidget QWidget#qt_calendar_navigationbar {{
    background-color: {CP_BG};
}}
QCalendarWidget QToolButton {{
    color: {CP_YELLOW};
    background-color: {CP_BG};
    font-weight: bold;
}}
QCalendarWidget QSpinBox {{
    color: {CP_CYAN};
    background-color: {CP_PANEL};
}}
QPushButton {{
    background-color: {CP_DIM};
    border: 1px solid {CP_DIM};
    color: white;
    padding: 5px 10px;
    font-weight: bold;
    font-family: 'Consolas';
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
    background-color: #1a1a1a;
    color: #444;
    border: 1px solid #222;
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
QScrollArea {{ background: transparent; border: none; }}
QScrollBar:vertical {{
    background: {CP_BG}; width: 8px; margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: {CP_CYAN}; min-height: 20px; border-radius: 4px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px; background: none;
}}
QScrollBar:horizontal {{
    background: {CP_BG}; height: 8px; margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: {CP_CYAN}; min-width: 20px; border-radius: 4px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px; background: none;
}}
QLabel  {{ background: transparent; }}
QFrame  {{ background: transparent; }}
QRadioButton {{ spacing: 6px; color: {CP_TEXT}; }}
QRadioButton::indicator {{
    width: 12px; height: 12px;
    border: 1px solid {CP_DIM};
    border-radius: 6px;
    background: {CP_PANEL};
}}
QRadioButton::indicator:checked {{
    background: {CP_CYAN}; border-color: {CP_CYAN};
}}
"""

# ── Defaults ───────────────────────────────────────────────
DEFAULT_SETTINGS = {
    "column_width": 280,
    "alarm_sound": "",
    "custom_patterns": [
        {"name": "Standard (HH:mm on dd MMM)", "pattern": "%H:%M on %d %b"},
        {"name": "Compact (HH:mm dd/MM/yy)", "pattern": "%H:%M %d/%m/%y"},
        {"name": "Date only (yyyy-MM-dd)", "pattern": "%Y-%m-%d"}
    ]
}

# ── Helpers ────────────────────────────────────────────────

def parse_time_string(s: str) -> int:
    """Parse 25d35h66m9s / 154h25m20s / 25m / 90s / 30 (bare = minutes).
    Supports d (days), h (hours), m (minutes), s (seconds). Returns seconds or -1."""
    s = s.strip().lower()
    if not s:
        return -1
    try:
        return int(float(s) * 60)
    except ValueError:
        pass
    m = re.fullmatch(
        r'(?:(\d+(?:\.\d+)?)d)?(?:(\d+(?:\.\d+)?)h)?(?:(\d+(?:\.\d+)?)m)?(?:(\d+(?:\.\d+)?)s)?',
        s
    )
    if not m or not any(m.groups()):
        return -1
    total = int(float(m.group(1) or 0) * 86400
                + float(m.group(2) or 0) * 3600
                + float(m.group(3) or 0) * 60
                + float(m.group(4) or 0))
    return total if total > 0 else -1


def parse_datetime_string(s: str, now: datetime | None = None) -> datetime | None:
    """Parse pasted date/time strings like '17:42 on 22 Jul' into a future datetime."""
    now = now or datetime.now()
    raw = re.sub(r"\s+", " ", s.strip())
    if not raw:
        return None

    normalized = re.sub(r"\s+on\s+", " ", raw, flags=re.IGNORECASE)
    normalized = normalized.replace(",", "")

    patterns = [
        "%H:%M %d %b %Y",
        "%H:%M %d %B %Y",
        "%d %b %H:%M %Y",
        "%d %B %H:%M %Y",
        "%H:%M %d %b",
        "%H:%M %d %B",
        "%d %b %H:%M",
        "%d %B %H:%M",
    ]

    for fmt in patterns:
        try:
            parsed = datetime.strptime(normalized, fmt)
        except ValueError:
            continue

        if "%Y" not in fmt:
            parsed = parsed.replace(year=now.year)
            if parsed <= now:
                parsed = parsed.replace(year=now.year + 1)
        return parsed

    return None


def parse_custom_pattern(s: str, pattern: str, now: datetime | None = None) -> datetime | None:
    """Parse a date/time string based on a custom strptime pattern."""
    now = now or datetime.now()
    raw = re.sub(r"\s+", " ", s.strip())
    if not raw:
        return None
    try:
        parsed = datetime.strptime(raw, pattern)
        if "%Y" not in pattern and "%y" not in pattern:
            parsed = parsed.replace(year=now.year)
            if parsed <= now:
                parsed = parsed.replace(year=now.year + 1)
        return parsed
    except ValueError:
        return None


def fmt_secs(total: int) -> str:
    total = max(0, total)
    d, rem = divmod(total, 86400)
    h, rem = divmod(rem, 3600)
    m, s   = divmod(rem, 60)
    
    if d > 0:
        return f"{d:02d}:{h:02d}:{m:02d}:{s:02d}"
    elif h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


# ── Alarm Popup ────────────────────────────────────────────

class AlarmPopup(QDialog):
    def __init__(self, label: str = "TIME'S UP!", parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Dialog
        )
        self.setModal(True)
        self.setStyleSheet(f"background-color: {CP_BG};")
        self.resize(520, 260)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(30, 30, 30, 30)
        lay.setSpacing(20)

        icon = QLabel("⏰")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 48pt; background: transparent;")

        self._title = QLabel("ALARM!")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title.setStyleSheet(
            f"font-size: 28pt; font-weight: bold; color: {CP_RED};"
            " font-family: 'Consolas'; background: transparent;"
        )

        sub = QLabel(label)
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(
            f"font-size: 13pt; color: {CP_YELLOW};"
            " font-family: 'Consolas'; background: transparent;"
        )

        dismiss = QPushButton("■  DISMISS")
        dismiss.setFixedHeight(40)
        dismiss.setStyleSheet(
            f"QPushButton {{ background: {CP_RED}; color: white; border: none;"
            f" font-size: 12pt; font-weight: bold; }}"
            f"QPushButton:hover {{ background: #cc0030; }}"
        )
        dismiss.setCursor(Qt.CursorShape.PointingHandCursor)
        dismiss.clicked.connect(self.accept)

        lay.addWidget(icon)
        lay.addWidget(self._title)
        lay.addWidget(sub)
        lay.addWidget(dismiss)

        self._blink = True
        t = QTimer(self)
        t.timeout.connect(self._do_blink)
        t.start(500)
        self._blink_timer = t

        scr = QApplication.primaryScreen().geometry()
        self.move(scr.center().x() - 260, scr.center().y() - 130)

    def _do_blink(self):
        c = CP_RED if self._blink else CP_CYAN
        self._title.setStyleSheet(
            f"font-size: 28pt; font-weight: bold; color: {c};"
            " font-family: 'Consolas'; background: transparent;"
        )
        self._blink = not self._blink

    def closeEvent(self, e):
        self._blink_timer.stop()
        super().closeEvent(e)


# ── Extensible Timer Dialog (Add / Edit) ───────────────────

class TimerDialog(QDialog):
    def __init__(self, title: str, ok_text: str, label_val: str = "", fires_at_val: float | None = None, settings: dict | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet(GLOBAL_QSS + f"QDialog {{ background: {CP_BG}; }}")
        self.setMinimumWidth(500)
        self.setModal(True)
        
        self._settings = settings or DEFAULT_SETTINGS
        self._custom_patterns = self._settings.get("custom_patterns", [])
        
        self._result_label = label_val
        self._result_fires_at = fires_at_val
        self.custom_edits = {}
        
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 18, 18, 18)
        
        # 1. Label Section
        lbl_grp = QGroupBox("TIMER LABEL")
        lbl_form = QFormLayout(lbl_grp)
        self.label_edit = QLineEdit(label_val)
        self.label_edit.setPlaceholderText("e.g. Sprint deadline, Study session…")
        lbl_form.addRow("Label:", self.label_edit)
        lay.addWidget(lbl_grp)
        
        # 2. Input Mode Selection
        mode_grp = QGroupBox("INPUT MODE")
        mode_layout = QVBoxLayout(mode_grp)
        
        # Header row with help button
        hdr_row = QHBoxLayout()
        hdr_row.addWidget(QLabel("Select an input mode:"))
        hdr_row.addStretch(1)
        
        self.help_btn = QPushButton("ⓘ")
        self.help_btn.setFixedSize(24, 24)
        self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_btn.setToolTip("Click for format guide")
        self.help_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {CP_CYAN}; "
            f"color: {CP_CYAN}; border-radius: 12px; font-weight: bold; font-size: 10pt; }}"
            f"QPushButton:hover {{ background: {CP_CYAN}; color: black; }}"
        )
        self.help_btn.clicked.connect(self._show_help)
        hdr_row.addWidget(self.help_btn)
        mode_layout.addLayout(hdr_row)
        
        # Grid layout for radio buttons to support dynamic list elegantly
        radio_grid = QGridLayout()
        self.bg = QButtonGroup(self)
        
        self.modes_config = [
            ("text", "Relative text", self._create_text_panel),
            ("picker", "Pick datetime", self._create_picker_panel)
        ]
        
        for idx, pat in enumerate(self._custom_patterns):
            mode_id = f"custom_{idx}"
            self.modes_config.append((
                mode_id,
                pat["name"],
                lambda idx=idx, pat=pat: self._create_custom_panel(idx, pat)
            ))
            
        self.radio_buttons = {}
        cols = 2
        for i, (mode_id, mode_label, _) in enumerate(self.modes_config):
            rb = QRadioButton(mode_label)
            self.bg.addButton(rb)
            self.radio_buttons[mode_id] = rb
            
            row_idx = i // cols
            col_idx = i % cols
            radio_grid.addWidget(rb, row_idx, col_idx)
            
        mode_layout.addLayout(radio_grid)
        lay.addWidget(mode_grp)
        
        # Panels container
        self.panels = {}
        for mode_id, _, builder_func in self.modes_config:
            panel = builder_func()
            lay.addWidget(panel)
            self.panels[mode_id] = panel
            panel.setVisible(False)
            
        # Select default mode based on fires_at_val
        if fires_at_val is not None:
            self.radio_buttons["picker"].setChecked(True)
            self._switch_mode("picker")
        else:
            self.radio_buttons["text"].setChecked(True)
            self._switch_mode("text")
            
        # Connect toggles
        for mode_id, rb in self.radio_buttons.items():
            rb.toggled.connect(self._make_toggle_callback(mode_id))
            
        # Error Label
        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {CP_RED}; font-size: 9pt;")
        lay.addWidget(self.err_lbl)
        
        # Bottom Buttons
        btn_row = QHBoxLayout()
        ok_btn = QPushButton(ok_text)
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet(
            f"QPushButton {{ background: {CP_GREEN}; color: #000;"
            f" font-weight: bold; border: none; }}"
            f"QPushButton:hover {{ background: #00cc1a; }}"
        )
        cancel_btn = QPushButton("✖ CANCEL")
        cancel_btn.setFixedHeight(36)
        
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        lay.addLayout(btn_row)
        
        ok_btn.clicked.connect(self._on_ok)
        cancel_btn.clicked.connect(self.reject)

    def _make_toggle_callback(self, mode_id):
        return lambda checked: self._switch_mode(mode_id) if checked else None

    def _switch_mode(self, active_mode_id):
        for mode_id, panel in self.panels.items():
            panel.setVisible(mode_id == active_mode_id)
        self.adjustSize()

    def _create_text_panel(self) -> QWidget:
        widget = QWidget()
        tp = QVBoxLayout(widget)
        tp.setContentsMargins(0, 0, 0, 0)
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("e.g. 25d12h or 1h30m or 45m or 90s")
        self.time_edit.setMinimumHeight(34)
        tp.addWidget(self.time_edit)
        return widget

    def _create_paste_panel(self) -> QWidget:
        # Backward compatibility / fallback
        widget = QWidget()
        pp = QVBoxLayout(widget)
        pp.setContentsMargins(0, 0, 0, 0)
        pp.addWidget(QLabel("Paste standard date/time like: <span style='color:#00F0FF'>17:42 on 22 Jul</span>"))
        self.paste_edit = QLineEdit()
        self.paste_edit.setPlaceholderText("e.g. 17:42 on 22 Jul")
        self.paste_edit.setMinimumHeight(34)
        pp.addWidget(self.paste_edit)
        return widget

    def _create_picker_panel(self) -> QWidget:
        widget = QWidget()
        dp = QVBoxLayout(widget)
        dp.setContentsMargins(0, 0, 0, 0)
        dp.addWidget(QLabel("Select the future date & time when alarm fires:"))
        self.dt_picker = QDateTimeEdit()
        self.dt_picker.setCalendarPopup(True)
        
        if self._result_fires_at is not None:
            self.dt_picker.setDateTime(QDateTime.fromSecsSinceEpoch(int(self._result_fires_at)))
        else:
            self.dt_picker.setDateTime(QDateTime.currentDateTime().addSecs(3600))
            
        self.dt_picker.setDisplayFormat("yyyy-MM-dd  HH:mm:ss")
        self.dt_picker.setMinimumHeight(34)
        dp.addWidget(self.dt_picker)
        return widget

    def _create_custom_panel(self, idx: int, pat: dict) -> QWidget:
        widget = QWidget()
        lp = QVBoxLayout(widget)
        lp.setContentsMargins(0, 0, 0, 0)
        
        desc = QLabel(f"Input date/time matching pattern: <span style='color:{CP_CYAN}'><b>{pat['pattern']}</b></span>")
        desc.setTextFormat(Qt.TextFormat.RichText)
        
        edit = QLineEdit()
        edit.setMinimumHeight(34)
        try:
            sample = datetime.now().strftime(pat["pattern"])
        except Exception:
            sample = "matching format"
        edit.setPlaceholderText(f"e.g., {sample}")
        
        lp.addWidget(desc)
        lp.addWidget(edit)
        
        self.custom_edits[f"custom_{idx}"] = edit
        return widget

    def _show_help(self):
        help_text = (
            "<h3>⏰ FORMAT CODE REFERENCE GUIDE</h3>"
            "<p>When creating or editing custom patterns in Settings, use these standard <b>%</b> codes:</p>"
            "<ul>"
            "<li><b>%H</b> : 24-hour hour with leading zero (00-23)</li>"
            "<li><b>%I</b> : 12-hour hour with leading zero (01-12)</li>"
            "<li><b>%M</b> : Minute with leading zero (00-59)  <i>(Note: Capital M!)</i></li>"
            "<li><b>%d</b> : Day of month with leading zero (01-31)</li>"
            "<li><b>%b</b> : Short month name (e.g., Jan, Feb, Jul)</li>"
            "<li><b>%B</b> : Full month name (e.g., January, July)</li>"
            "<li><b>%m</b> : Month number with leading zero (01-12)</li>"
            "<li><b>%y</b> : Two-digit year (e.g., 26)</li>"
            "<li><b>%Y</b> : Four-digit year (e.g., 2026)</li>"
            "<li><b>%p</b> : AM/PM indicator (e.g., AM, PM)</li>"
            "</ul>"
            "<p><b>Relative Input Examples:</b><br>"
            "• <code>1h30m</code> (1 hour, 30 minutes)<br>"
            "• <code>45m</code> (45 minutes)<br>"
            "• <code>30</code> (default is minutes)</p>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("FORMAT REFERENCE")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStyleSheet(GLOBAL_QSS + f"QMessageBox {{ background: {CP_BG}; }}")
        msg.exec()

    def _on_ok(self):
        label = self.label_edit.text().strip() or "Timer"
        active_mode = None
        for mode_id, rb in self.radio_buttons.items():
            if rb.isChecked():
                active_mode = mode_id
                break
                
        if active_mode == "text":
            raw = self.time_edit.text().strip()
            if not raw and self._result_fires_at is not None:
                fires_at = self._result_fires_at
            else:
                secs = parse_time_string(raw)
                if secs < 0:
                    self.err_lbl.setText("⚠  Invalid format. Try: 1h30m, 45m, 90s, 2.5h …")
                    return
                fires_at = time.time() + secs
        elif active_mode == "picker":
            target = self.dt_picker.dateTime().toPyDateTime()
            delta = (target - datetime.now()).total_seconds()
            if delta <= 0:
                self.err_lbl.setText("⚠  Selected datetime is in the past.")
                return
            fires_at = target.timestamp()
        elif active_mode.startswith("custom_"):
            edit = self.custom_edits.get(active_mode)
            raw_input = edit.text().strip() if edit else ""
            if not raw_input and self._result_fires_at is not None:
                fires_at = self._result_fires_at
            else:
                idx = int(active_mode.split("_")[1])
                pat = self._custom_patterns[idx]
                target = parse_custom_pattern(raw_input, pat["pattern"])
                if target is None:
                    self.err_lbl.setText(f"⚠  Input does not match pattern: {pat['pattern']}")
                    return
                delta = (target - datetime.now()).total_seconds()
                if delta <= 0:
                    self.err_lbl.setText("⚠  Parsed datetime is in the past.")
                    return
                fires_at = target.timestamp()
        else:
            self.err_lbl.setText("⚠  Please select an input mode.")
            return
            
        self._result_fires_at = fires_at
        self._result_label = label
        self.accept()

    @staticmethod
    def get_timer(title: str, ok_text: str, label_val: str = "", fires_at_val: float | None = None, settings: dict | None = None, parent=None):
        dlg = TimerDialog(title, ok_text, label_val, fires_at_val, settings, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg._result_label, dlg._result_fires_at
        return None


# ── Settings Dialog ────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙  SETTINGS")
        self.setStyleSheet(GLOBAL_QSS + f"QDialog {{ background: {CP_BG}; }}")
        self.setMinimumWidth(480)
        self.setModal(True)
        self._s = dict(settings)
        self._custom_pats = [dict(p) for p in self._s.get("custom_patterns", [])]

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(14)

        # General Group
        grp  = QGroupBox("GENERAL")
        form = QFormLayout(grp)

        self.col_w = QLineEdit(str(self._s.get("column_width", 280)))
        self.col_w.setPlaceholderText("280")
        form.addRow("Column width (px):", self.col_w)

        self.snd = QLineEdit(self._s.get("alarm_sound", ""))
        self.snd.setPlaceholderText("optional .wav path")
        form.addRow("Alarm sound:", self.snd)
        lay.addWidget(grp)

        # Custom Patterns Group
        pat_grp = QGroupBox("CUSTOM DATE/TIME PATTERNS")
        pat_v = QVBoxLayout(pat_grp)
        
        self.pat_scroll = QScrollArea()
        self.pat_scroll.setWidgetResizable(True)
        self.pat_scroll.setFixedHeight(160)
        
        self.pat_container = QWidget()
        self.pat_list_lay = QVBoxLayout(self.pat_container)
        self.pat_list_lay.setContentsMargins(4, 4, 4, 4)
        self.pat_list_lay.setSpacing(6)
        self.pat_list_lay.addStretch(1)
        self.pat_scroll.setWidget(self.pat_container)
        pat_v.addWidget(self.pat_scroll)
        
        # Form to add a new pattern
        add_form = QHBoxLayout()
        self.new_name = QLineEdit()
        self.new_name.setPlaceholderText("Name (e.g., Short Date)")
        self.new_pat = QLineEdit()
        self.new_pat.setPlaceholderText("Pattern (e.g., %d %b)")
        
        # Help Button next to pattern field
        self.help_btn = QPushButton("ⓘ")
        self.help_btn.setFixedSize(24, 24)
        self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_btn.setToolTip("Click for format guide")
        self.help_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: 1px solid {CP_CYAN}; "
            f"color: {CP_CYAN}; border-radius: 12px; font-weight: bold; font-size: 10pt; }}"
            f"QPushButton:hover {{ background: {CP_CYAN}; color: black; }}"
        )
        self.help_btn.clicked.connect(self._show_help)

        add_btn = QPushButton("＋ ADD")
        add_btn.setFixedSize(60, 28)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(
            f"QPushButton {{ background: {CP_CYAN}; color: black; border: none; font-weight: bold; }}"
            f"QPushButton:hover {{ background: #00ccff; }}"
        )
        add_btn.clicked.connect(self._add_pattern)
        
        add_form.addWidget(self.new_name, 2)
        add_form.addWidget(self.new_pat, 3)
        add_form.addWidget(self.help_btn, 0)
        add_form.addWidget(add_btn, 1)
        pat_v.addLayout(add_form)
        
        self.pat_err_lbl = QLabel("")
        self.pat_err_lbl.setStyleSheet(f"color: {CP_RED}; font-size: 8pt;")
        pat_v.addWidget(self.pat_err_lbl)
        
        lay.addWidget(pat_grp)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._ok)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        self._refresh_patterns()

    def _show_help(self):
        help_text = (
            "<h3>⏰ FORMAT CODE REFERENCE GUIDE</h3>"
            "<p>When creating or editing custom patterns in Settings, use these standard <b>%</b> codes:</p>"
            "<ul>"
            "<li><b>%H</b> : 24-hour hour with leading zero (00-23)</li>"
            "<li><b>%I</b> : 12-hour hour with leading zero (01-12)</li>"
            "<li><b>%M</b> : Minute with leading zero (00-59)  <i>(Note: Capital M!)</i></li>"
            "<li><b>%d</b> : Day of month with leading zero (01-31)</li>"
            "<li><b>%b</b> : Short month name (e.g., Jan, Feb, Jul)</li>"
            "<li><b>%B</b> : Full month name (e.g., January, July)</li>"
            "<li><b>%m</b> : Month number with leading zero (01-12)</li>"
            "<li><b>%y</b> : Two-digit year (e.g., 26)</li>"
            "<li><b>%Y</b> : Four-digit year (e.g., 2026)</li>"
            "<li><b>%p</b> : AM/PM indicator (e.g., AM, PM)</li>"
            "</ul>"
            "<p><b>Relative Input Examples:</b><br>"
            "• <code>1h30m</code> (1 hour, 30 minutes)<br>"
            "• <code>45m</code> (45 minutes)<br>"
            "• <code>30</code> (default is minutes)</p>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("FORMAT REFERENCE")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStyleSheet(GLOBAL_QSS + f"QMessageBox {{ background: {CP_BG}; }}")
        msg.exec()

    def _refresh_patterns(self):
        while self.pat_list_lay.count() > 1:
            item = self.pat_list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for idx, pat in enumerate(self._custom_pats):
            row = QWidget()
            row_h = QHBoxLayout(row)
            row_h.setContentsMargins(4, 4, 4, 4)
            row_h.setSpacing(8)
            
            lbl = QLabel(f"<b>{pat['name']}</b> &nbsp;│&nbsp; <span style='color:{CP_CYAN}'>{pat['pattern']}</span>")
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setStyleSheet(f"color: {CP_TEXT}; font-size: 9.5pt;")
            
            ren_b = QPushButton("✏")
            ren_b.setFixedSize(22, 22)
            ren_b.setCursor(Qt.CursorShape.PointingHandCursor)
            ren_b.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {CP_CYAN}; border: 1px solid {CP_CYAN}; font-weight: bold; }}"
                f"QPushButton:hover {{ background: {CP_CYAN}; color: black; }}"
            )
            ren_b.clicked.connect(lambda checked, i=idx: self._edit_pattern(i))
            
            del_b = QPushButton("✖")
            del_b.setFixedSize(22, 22)
            del_b.setCursor(Qt.CursorShape.PointingHandCursor)
            del_b.setStyleSheet(
                f"QPushButton {{ background: transparent; color: {CP_RED}; border: 1px solid {CP_RED}; font-weight: bold; }}"
                f"QPushButton:hover {{ background: {CP_RED}; color: black; }}"
            )
            del_b.clicked.connect(lambda checked, i=idx: self._delete_pattern(i))
            
            row_h.addWidget(lbl, 1)
            row_h.addWidget(ren_b, 0)
            row_h.addWidget(del_b, 0)
            
            self.pat_list_lay.insertWidget(self.pat_list_lay.count() - 1, row)

    def _edit_pattern(self, idx: int):
        if 0 <= idx < len(self._custom_pats):
            pat = self._custom_pats[idx]
            dlg = EditPatternDialog(pat["name"], pat["pattern"], self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                self._custom_pats[idx]["name"] = dlg.result_name
                self._custom_pats[idx]["pattern"] = dlg.result_pattern
                self._refresh_patterns()

    def _add_pattern(self):
        name = self.new_name.text().strip()
        pattern = self.new_pat.text().strip()
        self.pat_err_lbl.setText("")
        
        if not name or not pattern:
            self.pat_err_lbl.setText("⚠ Name and pattern cannot be empty.")
            return
            
        try:
            datetime.now().strftime(pattern)
        except Exception as exc:
            self.pat_err_lbl.setText(f"⚠ Invalid pattern format: {exc}")
            return
            
        self._custom_pats.append({"name": name, "pattern": pattern})
        self.new_name.clear()
        self.new_pat.clear()
        self._refresh_patterns()

    def _delete_pattern(self, idx: int):
        if 0 <= idx < len(self._custom_pats):
            self._custom_pats.pop(idx)
            self._refresh_patterns()

    def _ok(self):
        try:
            self._s["column_width"] = max(180, int(self.col_w.text()))
        except ValueError:
            pass
        self._s["alarm_sound"] = self.snd.text().strip()
        self._s["custom_patterns"] = self._custom_pats
        self.accept()

    def get_settings(self) -> dict:
        return self._s


# ── Edit Pattern Dialog ────────────────────────────────────

class EditPatternDialog(QDialog):
    def __init__(self, name: str, pattern: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EDIT PATTERN MODE")
        self.setStyleSheet(GLOBAL_QSS + f"QDialog {{ background: {CP_BG}; }}")
        self.setMinimumWidth(380)
        self.setModal(True)
        
        self.result_name = name
        self.result_pattern = pattern
        
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 18, 18, 18)
        
        grp = QGroupBox("PATTERN DETAILS")
        form = QFormLayout(grp)
        
        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("e.g. Compact Date")
        self.name_edit.setMinimumHeight(30)
        
        self.pat_edit = QLineEdit(pattern)
        self.pat_edit.setPlaceholderText("e.g. %H:%M %d/%m/%y")
        self.pat_edit.setMinimumHeight(30)
        
        form.addRow("Mode Name:", self.name_edit)
        form.addRow("Format Pattern:", self.pat_edit)
        lay.addWidget(grp)
        
        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {CP_RED}; font-size: 8pt;")
        lay.addWidget(self.err_lbl)
        
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._validate_and_accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)
        
    def _validate_and_accept(self):
        name = self.name_edit.text().strip()
        pattern = self.pat_edit.text().strip()
        
        if not name or not pattern:
            self.err_lbl.setText("⚠ Fields cannot be empty.")
            return
        
        try:
            datetime.now().strftime(pattern)
        except Exception as exc:
            self.err_lbl.setText(f"⚠ Invalid pattern format: {exc}")
            return
        
        self.result_name = name
        self.result_pattern = pattern
        self.accept()



# ── TimerCard ──────────────────────────────────────────────

class TimerCard(QFrame):
    removed       = pyqtSignal(str)
    duplicated    = pyqtSignal(str)   # emits card_id — parent handles the clone
    state_changed = pyqtSignal()

    def __init__(self, card_id: str, label: str, fires_at: float, created_at: float = 0.0, parent=None):
        super().__init__(parent)
        self.card_id  = card_id
        self.label    = label
        self.fires_at = fires_at
        
        now = time.time()
        if created_at <= 0.0 or created_at >= fires_at:
            self.created_at = now
        else:
            self.created_at = created_at
            
        self.fired    = False

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumWidth(220)
        self._set_border(CP_DIM)
        self._build_ui()

        self._ticker = QTimer(self)
        self._ticker.setInterval(1000)
        self._ticker.timeout.connect(self._tick)
        self._ticker.start()

        QTimer.singleShot(100, self._tick)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # top row: label + edit + duplicate + delete
        top = QHBoxLayout()
        self._lbl = QLabel(self.label)
        self._lbl.setStyleSheet(
            f"color: {CP_YELLOW}; font-weight: bold; font-size: 10pt; background: transparent; border: none;"
        )
        self._lbl.setWordWrap(True)

        edit_btn = QPushButton()
        edit_btn.setFixedSize(22, 22)
        edit_btn.setIcon(icon_rename(color=CP_CYAN, size=13))
        edit_btn.setIconSize(QSize(13, 13))
        edit_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; }}"
            f"QPushButton:hover {{ background: #1e1e1e; border: 1px solid {CP_CYAN}; }}"
        )
        edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_btn.setToolTip("Edit label & time")
        edit_btn.clicked.connect(self._on_edit)

        dup_btn = QPushButton()
        dup_btn.setFixedSize(22, 22)
        dup_btn.setIcon(icon_duplicate(color=CP_CYAN, size=13))
        dup_btn.setIconSize(QSize(13, 13))
        dup_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; }}"
            f"QPushButton:hover {{ background: #1e1e1e; border: 1px solid {CP_CYAN}; }}"
        )
        dup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dup_btn.setToolTip("Duplicate timer")
        dup_btn.clicked.connect(self._on_duplicate)

        del_btn = QPushButton()
        del_btn.setFixedSize(22, 22)
        del_btn.setIcon(icon_delete(color=CP_RED, size=13))
        del_btn.setIconSize(QSize(13, 13))
        del_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; }}"
            f"QPushButton:hover {{ background: #2a1010; border: 1px solid {CP_RED}; }}"
        )
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setToolTip("Delete timer")
        del_btn.clicked.connect(self._on_delete)
        
        top.addWidget(self._lbl, 1)
        top.addWidget(edit_btn, 0)
        top.addWidget(dup_btn, 0)
        top.addWidget(del_btn, 0)

        # countdown display
        self._display = QLabel("00:00")
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setStyleSheet(
            f"color: {CP_DIM}; font-size: 26pt; font-weight: bold;"
            " font-family: 'Consolas'; letter-spacing: 2px; background: transparent; border: none;"
        )

        # thin progress bar
        self._prog_bg = QWidget()
        self._prog_bg.setFixedHeight(4)
        self._prog_bg.setStyleSheet(f"background: {CP_DIM};")
        self._prog_fill = QWidget(self._prog_bg)
        self._prog_fill.setFixedHeight(4)
        self._prog_fill.setStyleSheet(f"background: {CP_CYAN};")

        root.addLayout(top)
        root.addWidget(self._display)
        root.addWidget(self._prog_bg)

    def _set_border(self, color: str):
        self.setStyleSheet(
            f"TimerCard {{ border: 1px solid {color}; background: {CP_PANEL}; }}"
        )

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_bar()

    def _update_bar(self):
        now = time.time()
        if self.fires_at <= now:
            self._prog_fill.setFixedWidth(0)
            self._prog_bg.setVisible(False)
            return
        
        self._prog_bg.setVisible(True)
        duration = self.fires_at - self.created_at
        if duration <= 0:
            duration = 1.0
        
        ratio = max(0.0, min(1.0, (self.fires_at - now) / duration))
        w = int(self._prog_bg.width() * ratio)
        self._prog_fill.setFixedWidth(max(0, w))
        
        color = CP_GREEN if ratio > 0.5 else (CP_ORANGE if ratio > 0.2 else CP_RED)
        self._prog_fill.setStyleSheet(f"background: {color};")

    def _tick(self):
        now = time.time()
        if now >= self.fires_at:
            self._display.setText("00:00")
            self._display.setStyleSheet(
                f"color: {CP_RED}; font-size: 26pt; font-weight: bold;"
                " font-family: 'Consolas'; letter-spacing: 2px; background: transparent; border: none;"
            )
            self._set_border(CP_RED)
            self._prog_fill.setFixedWidth(0)
            self._prog_bg.setVisible(False)
            
            if not self.fired:
                self.fired = True
                p = self.parent()
                if p and hasattr(p, "sort_cards"):
                    p.sort_cards()
        else:
            self.fired = False
            rem = int(self.fires_at - now)
            self._display.setText(fmt_secs(rem))
            self._display.setStyleSheet(
                f"color: {CP_CYAN}; font-size: 26pt; font-weight: bold;"
                " font-family: 'Consolas'; letter-spacing: 2px; background: transparent; border: none;"
            )
            self._set_border(CP_GREEN)
            self._update_bar()

    def _on_delete(self):
        self._ticker.stop()
        self.removed.emit(self.card_id)

    def _on_duplicate(self):
        self.duplicated.emit(self.card_id)

    def _on_edit(self):
        """Edit this timer's label and/or time."""
        settings = None
        p = self.parent()
        while p:
            if hasattr(p, "_settings"):
                settings = p._settings
                break
            p = p.parent()
            
        result = TimerDialog.get_timer(
            "EDIT TIMER",
            "✔  APPLY",
            self.label,
            self.fires_at,
            settings=settings,
            parent=self
        )
        if result is None:
            return
        new_label, new_fires_at = result
        self.label = new_label
        self._lbl.setText(self.label)
        
        if abs(new_fires_at - self.fires_at) > 0.01:
            self.created_at = time.time()
            
        self.fires_at = new_fires_at
        self.fired = False
        self._tick()
        self.state_changed.emit()

    # serialization
    def to_dict(self) -> dict:
        return {
            "id": self.card_id,
            "label": self.label,
            "fires_at": self.fires_at,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict, parent=None) -> "TimerCard":
        card_id = d["id"]
        label = d.get("label", "Timer")
        fires_at = d.get("fires_at", 0.0)
        created_at = d.get("created_at", 0.0)
        return cls(card_id, label, fires_at, created_at, parent)


# ── ColumnWidget ───────────────────────────────────────────

class ColumnWidget(QFrame):
    removed       = pyqtSignal(str)
    state_changed = pyqtSignal()

    def __init__(self, col_id: str, name: str, col_width: int = 280, parent=None):
        super().__init__(parent)
        self.col_id    = col_id
        self.name      = name
        self.col_width = col_width
        self._cards: dict[str, TimerCard] = {}

        self.setFixedWidth(col_width)
        self.setFrameShape(QFrame.Shape.Box)
        self.setStyleSheet(
            f"ColumnWidget {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}"
        )
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # header
        hdr = QWidget()
        hdr.setFixedHeight(44)
        hdr.setStyleSheet(
            f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};"
        )
        h = QHBoxLayout(hdr)
        h.setContentsMargins(10, 0, 6, 0)
        h.setSpacing(4)

        self._name_lbl = QLabel(self.name.upper())
        self._name_lbl.setStyleSheet(
            f"color: {CP_YELLOW}; font-weight: bold; font-size: 11pt;"
            " letter-spacing: 1px; background: transparent;"
        )
        self._name_lbl.setToolTip("Click ✏ to rename")

        ren_btn = QPushButton()
        ren_btn.setFixedSize(28, 28)
        ren_btn.setIcon(icon_rename(color=CP_CYAN, size=16))
        ren_btn.setIconSize(QSize(16, 16))
        ren_btn.setStyleSheet(
            f"QPushButton {{ background: #1e1e1e; border: 1px solid {CP_DIM}; }}"
            f"QPushButton:hover {{ border-color: {CP_CYAN}; background: #252525; }}"
            f"QPushButton:pressed {{ background: {CP_CYAN}; }}"
        )
        ren_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ren_btn.setToolTip("Rename column")
        ren_btn.clicked.connect(self._on_rename)

        del_btn = QPushButton()
        del_btn.setFixedSize(28, 28)
        del_btn.setIcon(icon_delete(color=CP_RED, size=16))
        del_btn.setIconSize(QSize(16, 16))
        del_btn.setStyleSheet(
            f"QPushButton {{ background: #1e1e1e; border: 1px solid {CP_DIM}; }}"
            f"QPushButton:hover {{ border-color: {CP_RED}; background: #2a1010; }}"
            f"QPushButton:pressed {{ background: {CP_RED}; }}"
        )
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setToolTip("Delete column")
        del_btn.clicked.connect(self._on_del_col)

        h.addWidget(self._name_lbl, 1)
        h.addWidget(ren_btn, 0)
        h.addWidget(del_btn, 0)

        # scroll area for cards
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._card_container = QWidget()
        self._card_container.setStyleSheet(f"background: {CP_BG};")
        self._card_layout = QVBoxLayout(self._card_container)
        self._card_layout.setContentsMargins(8, 8, 8, 8)
        self._card_layout.setSpacing(8)
        self._card_layout.addStretch(1)
        self._scroll.setWidget(self._card_container)

        # add-timer button
        self._add_btn = QPushButton("＋  ADD TIMER")
        self._add_btn.setFixedHeight(34)
        self._add_btn.setStyleSheet(
            f"QPushButton {{ background: {CP_DIM};"
            f" border: 1px dashed {CP_CYAN};"
            f" color: {CP_CYAN}; font-weight: bold; margin: 6px; }}"
            f"QPushButton:hover {{ background: #1a1a1a;"
            f" border-color: {CP_YELLOW}; color: {CP_YELLOW}; }}"
        )
        self._add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._add_btn.clicked.connect(self._on_add_timer)

        root.addWidget(hdr)
        root.addWidget(self._scroll, 1)
        root.addWidget(self._add_btn)

    def add_card(self, card: TimerCard):
        idx = self._card_layout.count() - 1   # before stretch
        self._card_layout.insertWidget(idx, card)
        self._cards[card.card_id] = card
        card.removed.connect(self._on_card_removed)
        card.duplicated.connect(self._on_card_duplicated)
        card.state_changed.connect(self.state_changed)
        card.state_changed.connect(self.sort_cards)
        self.sort_cards()

    def sort_cards(self):
        cards = list(self._cards.values())
        now = time.time()
        cards.sort(key=lambda c: (0 if c.fires_at <= now else 1, c.fires_at))
        for i, card in enumerate(cards):
            self._card_layout.removeWidget(card)
            self._card_layout.insertWidget(i, card)

    def remove_card(self, card_id: str):
        card = self._cards.pop(card_id, None)
        if card:
            self._card_layout.removeWidget(card)
            card.deleteLater()

    def _on_card_duplicated(self, cid: str):
        src = self._cards.get(cid)
        if src is None:
            return
        new_card = TimerCard(
            str(uuid.uuid4())[:8],
            src.label + " (copy)",
            src.fires_at,
            time.time(),
            self,
        )
        self.add_card(new_card)
        QTimer.singleShot(50, lambda:
            self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()
            )
        )
        self.state_changed.emit()

    def _on_add_timer(self):
        settings = None
        p = self.parent()
        while p:
            if hasattr(p, "_settings"):
                settings = p._settings
                break
            p = p.parent()
            
        result = TimerDialog.get_timer("ADD TIMER", "✔  ADD TIMER", settings=settings, parent=self)
        if result is None:
            return
        label, fires_at = result
        card = TimerCard(str(uuid.uuid4())[:8], label, fires_at, time.time(), self)
        self.add_card(card)
        QTimer.singleShot(50, lambda:
            self._scroll.verticalScrollBar().setValue(
                self._scroll.verticalScrollBar().maximum()
            )
        )
        self.state_changed.emit()

    def _on_card_removed(self, cid: str):
        self.remove_card(cid)
        self.state_changed.emit()

    def _on_rename(self):
        name, ok = QInputDialog.getText(
            self, "Rename Column", "Column name:", text=self.name
        )
        if ok and name.strip():
            self.name = name.strip()
            self._name_lbl.setText(self.name.upper())
            self.state_changed.emit()

    def _on_del_col(self):
        n   = len(self._cards)
        msg = f"Delete column '{self.name}'"
        if n:
            msg += f" and its {n} timer(s)"
        msg += "?"
        if QMessageBox.question(
            self, "Confirm", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.removed.emit(self.col_id)

    # serialization
    def to_dict(self) -> dict:
        return {
            "id": self.col_id, "name": self.name,
            "cards": [c.to_dict() for c in self._cards.values()],
        }

    @classmethod
    def from_dict(cls, d: dict, col_width: int = 280, parent=None) -> "ColumnWidget":
        col = cls(d["id"], d.get("name", "Column"), col_width, parent)
        for cd in d.get("cards", []):
            col.add_card(TimerCard.from_dict(cd, col))
        return col


# ── MainWindow ─────────────────────────────────────────────

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alarm_state.json")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⏰  ALARM TIMER  //  CYBERPUNK")
        self.setMinimumSize(700, 520)
        self.resize(1100, 660)
        self.setStyleSheet(GLOBAL_QSS)

        self._settings: dict = dict(DEFAULT_SETTINGS)
        self._columns: dict[str, ColumnWidget] = {}

        self._build_ui()
        self._load_state()

        self._autosave = QTimer(self)
        self._autosave.setInterval(30_000)
        self._autosave.timeout.connect(self._save)
        self._autosave.start()

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet(f"background: {CP_BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # toolbar
        tb = QWidget()
        tb.setFixedHeight(50)
        tb.setStyleSheet(
            f"background: {CP_PANEL}; border-bottom: 1px solid {CP_DIM};"
        )
        tbl = QHBoxLayout(tb)
        tbl.setContentsMargins(14, 0, 14, 0)
        tbl.setSpacing(8)

        title = QLabel("⏰  ALARM TIMER")
        title.setStyleSheet(
            f"color: {CP_YELLOW}; font-size: 14pt; font-weight: bold;"
            " letter-spacing: 2px; background: transparent;"
        )
        tbl.addWidget(title)
        tbl.addStretch(1)

        self._btn_add_col  = self._tbtn("＋  COLUMN",  CP_CYAN, "#000")
        self._btn_settings = self._tbtn("⚙  SETTINGS", CP_DIM,  CP_TEXT)
        self._btn_restart  = self._tbtn("↺  RESTART",  CP_DIM,  CP_TEXT)

        self._btn_add_col.clicked.connect(self._on_add_col)
        self._btn_settings.clicked.connect(self._on_settings)
        self._btn_restart.clicked.connect(self._on_restart)

        for b in (self._btn_add_col, self._btn_settings, self._btn_restart):
            tbl.addWidget(b)

        # horizontal scroll for columns
        self._hscroll = QScrollArea()
        self._hscroll.setWidgetResizable(True)
        self._hscroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._hscroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._hscroll.setStyleSheet(
            f"QScrollArea {{ background: {CP_BG}; border: none; }}"
        )

        self._col_container = QWidget()
        self._col_container.setStyleSheet(f"background: {CP_BG};")
        self._col_layout = QHBoxLayout(self._col_container)
        self._col_layout.setContentsMargins(10, 10, 10, 10)
        self._col_layout.setSpacing(10)
        self._col_layout.addStretch(1)
        self._hscroll.setWidget(self._col_container)

        # status bar
        self._sbar = QLabel("  Ready")
        self._sbar.setFixedHeight(24)
        self._sbar.setStyleSheet(
            f"background: {CP_PANEL}; color: {CP_SUBTEXT}; font-size: 8pt;"
            f" border-top: 1px solid {CP_DIM}; padding-left: 8px;"
        )

        root.addWidget(tb)
        root.addWidget(self._hscroll, 1)
        root.addWidget(self._sbar)

    def _tbtn(self, text, bg, fg):
        b = QPushButton(text)
        b.setFixedHeight(32)
        b.setMinimumWidth(90)
        b.setStyleSheet(
            f"QPushButton {{ background: {bg}; color: {fg}; border: none;"
            f" font-size: 9pt; font-weight: bold; padding: 0 10px; }}"
            f"QPushButton:hover {{ border: 1px solid {CP_YELLOW};"
            f" color: {CP_YELLOW}; }}"
            f"QPushButton:pressed {{ background: {CP_YELLOW}; color: #000; }}"
        )
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    def _add_col_widget(self, col: ColumnWidget):
        idx = self._col_layout.count() - 1
        self._col_layout.insertWidget(idx, col)
        self._columns[col.col_id] = col
        col.removed.connect(self._on_col_removed)
        col.state_changed.connect(self._on_changed)

    def _on_add_col(self):
        name, ok = QInputDialog.getText(
            self, "New Column", "Project / column name:"
        )
        if not ok or not name.strip():
            return
        cw  = self._settings.get("column_width", 280)
        col = ColumnWidget(str(uuid.uuid4())[:8], name.strip(), cw, self)
        self._add_col_widget(col)
        QTimer.singleShot(60, lambda:
            self._hscroll.horizontalScrollBar().setValue(
                self._hscroll.horizontalScrollBar().maximum()
            )
        )
        self._st("Column added: " + name.strip())
        self._save()

    def _on_col_removed(self, cid: str):
        col = self._columns.pop(cid, None)
        if col:
            self._col_layout.removeWidget(col)
            col.deleteLater()
        self._save()
        self._st("Column removed.")

    def _on_settings(self):
        dlg = SettingsDialog(self._settings, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._settings = dlg.get_settings()
            self._save()
            self._st("Settings saved.")

    def _on_restart(self):
        self._save()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def _on_changed(self):
        self._save()

    def _save(self):
        data = {
            "settings": self._settings,
            "columns":  [c.to_dict() for c in self._columns.values()],
        }
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self._st("Saved  ·  " + datetime.now().strftime("%H:%M:%S"))
        except Exception as exc:
            self._st(f"Save error: {exc}")

    def _load_state(self):
        if not os.path.exists(STATE_FILE):
            col = ColumnWidget(
                str(uuid.uuid4())[:8], "My Project", 280, self
            )
            self._add_col_widget(col)
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            loaded_settings = data.get("settings", {})
            for k, v in DEFAULT_SETTINGS.items():
                if k not in loaded_settings:
                    loaded_settings[k] = v
                    
            self._settings.update(loaded_settings)
            cw = self._settings.get("column_width", 280)
            for cd in data.get("columns", []):
                self._add_col_widget(
                    ColumnWidget.from_dict(cd, cw, self)
                )
            self._st("State loaded.")
        except Exception as exc:
            self._st(f"Load error: {exc}")

    def _st(self, msg: str):
        self._sbar.setText("  " + msg)

    def closeEvent(self, e):
        self._save()
        super().closeEvent(e)


# ── Entry point ────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
