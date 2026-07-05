# alarm_timer.py  –  Multi-column Alarm Countdown Timer
# Cyberpunk theme  |  PyQt6
# ============================================================

import sys
import os
import re
import json
import uuid
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QDialog,
    QFormLayout, QGroupBox, QFrame, QSizePolicy, QInputDialog,
    QMessageBox, QDateTimeEdit, QRadioButton,
    QButtonGroup, QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont

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


def fmt_secs(total: int) -> str:
    total = max(0, total)
    h, rem = divmod(total, 3600)
    m, s   = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


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


# ── Add Timer Dialog ───────────────────────────────────────

class AddTimerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ADD TIMER")
        self.setStyleSheet(GLOBAL_QSS + f"QDialog {{ background: {CP_BG}; }}")
        self.setMinimumWidth(420)
        self.setModal(True)

        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(18, 18, 18, 18)

        # label
        lbl_grp  = QGroupBox("TIMER LABEL")
        lbl_form = QFormLayout(lbl_grp)
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("e.g. Sprint deadline, Study session…")
        lbl_form.addRow("Label:", self.label_edit)

        # mode
        mode_grp = QGroupBox("INPUT MODE")
        mode_h   = QHBoxLayout(mode_grp)
        self.rb_text = QRadioButton("Text  (e.g. 1h30m)")
        self.rb_date = QRadioButton("Pick datetime")
        self.rb_text.setChecked(True)
        bg = QButtonGroup(self)
        bg.addButton(self.rb_text)
        bg.addButton(self.rb_date)
        mode_h.addWidget(self.rb_text)
        mode_h.addWidget(self.rb_date)

        # text panel
        self.text_panel = QWidget()
        tp = QVBoxLayout(self.text_panel)
        tp.setContentsMargins(0, 0, 0, 0)
        hint = QLabel(
            "Formats: <span style='color:#00F0FF'>25d35h66m9s</span> &nbsp;│&nbsp; "
            "<span style='color:#00F0FF'>2h30m20s</span> &nbsp;│&nbsp; "
            "<span style='color:#00F0FF'>45m</span> &nbsp;│&nbsp; "
            "<span style='color:#00F0FF'>90s</span> &nbsp;│&nbsp; "
            "<span style='color:#00F0FF'>1.5h</span> &nbsp;│&nbsp; "
            "<span style='color:#00F0FF'>30</span> (=min)"
        )
        hint.setTextFormat(Qt.TextFormat.RichText)
        hint.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        self.time_edit = QLineEdit()
        self.time_edit.setPlaceholderText("e.g.  25d12h  or  1h30m  or  45m  or  90s")
        self.time_edit.setMinimumHeight(34)
        tp.addWidget(hint)
        tp.addWidget(self.time_edit)

        # date panel
        self.date_panel = QWidget()
        dp = QVBoxLayout(self.date_panel)
        dp.setContentsMargins(0, 0, 0, 0)
        dp.addWidget(QLabel("Select the future date & time when alarm fires:"))
        self.dt_picker = QDateTimeEdit()
        self.dt_picker.setCalendarPopup(True)
        self.dt_picker.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.dt_picker.setDisplayFormat("yyyy-MM-dd  HH:mm:ss")
        self.dt_picker.setMinimumHeight(34)
        dp.addWidget(self.dt_picker)
        self.date_panel.setVisible(False)

        self.err_lbl = QLabel("")
        self.err_lbl.setStyleSheet(f"color: {CP_RED}; font-size: 9pt;")

        btn_row   = QHBoxLayout()
        ok_btn    = QPushButton("✔  ADD TIMER")
        ok_btn.setFixedHeight(36)
        ok_btn.setStyleSheet(
            f"QPushButton {{ background: {CP_GREEN}; color: #000;"
            f" font-weight: bold; border: none; }}"
            f"QPushButton:hover {{ background: #00cc1a; }}"
        )
        cancel_btn = QPushButton("✖  CANCEL")
        cancel_btn.setFixedHeight(36)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)

        lay.addWidget(lbl_grp)
        lay.addWidget(mode_grp)
        lay.addWidget(self.text_panel)
        lay.addWidget(self.date_panel)
        lay.addWidget(self.err_lbl)
        lay.addLayout(btn_row)

        self.rb_text.toggled.connect(self._switch_mode)
        ok_btn.clicked.connect(self._on_ok)
        cancel_btn.clicked.connect(self.reject)
        self._result_seconds = 0
        self._result_label   = ""

    def _switch_mode(self, text_active: bool):
        self.text_panel.setVisible(text_active)
        self.date_panel.setVisible(not text_active)
        self.adjustSize()

    def _on_ok(self):
        label = self.label_edit.text().strip() or "Timer"
        if self.rb_text.isChecked():
            secs = parse_time_string(self.time_edit.text())
            if secs < 0:
                self.err_lbl.setText("⚠  Invalid format. Try: 1h30m, 45m, 90s, 2.5h …")
                return
        else:
            target = self.dt_picker.dateTime().toPyDateTime()
            delta  = (target - datetime.now()).total_seconds()
            if delta <= 0:
                self.err_lbl.setText("⚠  Selected datetime is in the past.")
                return
            secs = int(delta)
        self._result_seconds = secs
        self._result_label   = label
        self.accept()

    @staticmethod
    def get_timer(parent=None):
        dlg = AddTimerDialog(parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg._result_label, dlg._result_seconds
        return None


# ── Settings Dialog ────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙  SETTINGS")
        self.setStyleSheet(GLOBAL_QSS + f"QDialog {{ background: {CP_BG}; }}")
        self.setMinimumWidth(360)
        self.setModal(True)
        self._s = dict(settings)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 18, 18, 18)
        lay.setSpacing(14)

        grp  = QGroupBox("GENERAL")
        form = QFormLayout(grp)

        self.col_w = QLineEdit(str(self._s.get("column_width", 280)))
        self.col_w.setPlaceholderText("280")
        form.addRow("Column width (px):", self.col_w)

        self.snd = QLineEdit(self._s.get("alarm_sound", ""))
        self.snd.setPlaceholderText("optional .wav path")
        form.addRow("Alarm sound:", self.snd)

        lay.addWidget(grp)
        note = QLabel("More settings can be added here.")
        note.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        lay.addWidget(note)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._ok)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _ok(self):
        try:
            self._s["column_width"] = max(180, int(self.col_w.text()))
        except ValueError:
            pass
        self._s["alarm_sound"] = self.snd.text().strip()
        self.accept()

    def get_settings(self) -> dict:
        return self._s



# ── TimerCard ──────────────────────────────────────────────

class TimerCard(QFrame):
    removed       = pyqtSignal(str)
    state_changed = pyqtSignal()

    STATE_IDLE    = "idle"
    STATE_RUNNING = "running"
    STATE_PAUSED  = "paused"
    STATE_DONE    = "done"

    def __init__(self, card_id: str, label: str, total_seconds: int, parent=None):
        super().__init__(parent)
        self.card_id       = card_id
        self.label         = label
        self.total_seconds = total_seconds
        self.remaining     = total_seconds
        self.state         = self.STATE_IDLE

        self.setFrameShape(QFrame.Shape.Box)
        self.setMinimumWidth(220)
        self._set_border(CP_DIM)
        self._build_ui()

        self._ticker = QTimer(self)
        self._ticker.setInterval(1000)
        self._ticker.timeout.connect(self._tick)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(6)

        # top row: label + delete
        top = QHBoxLayout()
        self._lbl = QLabel(self.label)
        self._lbl.setStyleSheet(
            f"color: {CP_YELLOW}; font-weight: bold; font-size: 10pt;"
        )
        self._lbl.setWordWrap(True)
        del_btn = QPushButton("✖")
        del_btn.setFixedSize(22, 22)
        del_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {CP_DIM}; }}"
            f"QPushButton:hover {{ color: {CP_RED}; }}"
        )
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setToolTip("Delete timer")
        del_btn.clicked.connect(self._on_delete)
        top.addWidget(self._lbl, 1)
        top.addWidget(del_btn, 0)

        # countdown display
        self._display = QLabel(fmt_secs(self.remaining))
        self._display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._display.setToolTip("Click to show/hide controls")
        self._display.setStyleSheet(
            f"color: {CP_CYAN}; font-size: 26pt; font-weight: bold;"
            " font-family: 'Consolas'; letter-spacing: 2px;"
        )

        # thin progress bar
        self._prog_bg = QWidget()
        self._prog_bg.setFixedHeight(4)
        self._prog_bg.setStyleSheet(f"background: {CP_DIM};")
        self._prog_fill = QWidget(self._prog_bg)
        self._prog_fill.setFixedHeight(4)
        self._prog_fill.setStyleSheet(f"background: {CP_CYAN};")

        # status
        self._status = QLabel("READY")
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status.setStyleSheet(
            f"color: {CP_SUBTEXT}; font-size: 8pt; letter-spacing: 1px;"
        )

        # buttons row — hidden until user clicks the card
        self._btn_widget = QWidget()
        btn_row = QHBoxLayout(self._btn_widget)
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(4)
        self._btn_start = self._mkbtn("▶  START",  CP_GREEN,  "#000")
        self._btn_pause = self._mkbtn("⏸  PAUSE",  CP_ORANGE, "#000")
        self._btn_reset = self._mkbtn("↺  RESET",  CP_DIM,    CP_TEXT)
        self._btn_pause.setEnabled(False)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_pause)
        btn_row.addWidget(self._btn_reset)
        self._btn_widget.setVisible(False)   # hidden by default

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {CP_DIM};")

        root.addLayout(top)
        root.addWidget(self._display)
        root.addWidget(self._prog_bg)
        root.addWidget(self._status)
        root.addWidget(sep)
        root.addWidget(self._btn_widget)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_reset.clicked.connect(self._on_reset)

        # click on display or status toggles the button row
        self._display.setCursor(Qt.CursorShape.PointingHandCursor)
        self._display.mousePressEvent = lambda e: self._toggle_controls()
        self._status.setCursor(Qt.CursorShape.PointingHandCursor)
        self._status.mousePressEvent  = lambda e: self._toggle_controls()

    def _toggle_controls(self):
        visible = not self._btn_widget.isVisible()
        self._btn_widget.setVisible(visible)

    def _mkbtn(self, text, bg, fg):
        b = QPushButton(text)
        b.setFixedHeight(28)
        b.setStyleSheet(
            f"QPushButton {{ background: {bg}; color: {fg}; border: none;"
            f" font-size: 8pt; font-weight: bold; font-family: Consolas; }}"
            f"QPushButton:hover {{ border: 1px solid {CP_YELLOW}; }}"
            f"QPushButton:disabled {{ background: #222; color: #444; border: none; }}"
        )
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        return b

    def _set_border(self, color: str):
        self.setStyleSheet(
            f"TimerCard {{ border: 1px solid {color}; background: {CP_PANEL}; }}"
        )

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_bar()

    def _update_bar(self):
        if self.total_seconds <= 0:
            return
        ratio = max(0.0, self.remaining / self.total_seconds)
        w = int(self._prog_bg.width() * ratio)
        self._prog_fill.setFixedWidth(max(0, w))
        color = CP_GREEN if ratio > 0.5 else (CP_ORANGE if ratio > 0.2 else CP_RED)
        self._prog_fill.setStyleSheet(f"background: {color};")

    def _tick(self):
        if self.remaining <= 0:
            self._ticker.stop()
            self._fire_alarm()
            return
        self.remaining -= 1
        self._display.setText(fmt_secs(self.remaining))
        self._update_bar()
        self.state_changed.emit()

    def _fire_alarm(self):
        self.state = self.STATE_DONE
        self._display.setText("00:00")
        self._display.setStyleSheet(
            f"color: {CP_RED}; font-size: 26pt; font-weight: bold;"
            " font-family: 'Consolas'; letter-spacing: 2px;"
        )
        self._status.setText("▐ ALARM!")
        self._status.setStyleSheet(
            f"color: {CP_RED}; font-size: 8pt; font-weight: bold;"
        )
        self._set_border(CP_RED)
        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(False)
        self.state_changed.emit()
        AlarmPopup(self.label, self).exec()

    def _on_start(self):
        if self.state in (self.STATE_IDLE, self.STATE_PAUSED):
            if self.remaining <= 0:
                self.remaining = self.total_seconds
            self.state = self.STATE_RUNNING
            self._ticker.start()
            self._btn_start.setEnabled(False)
            self._btn_pause.setEnabled(True)
            self._status.setText("▶ RUNNING")
            self._status.setStyleSheet(f"color: {CP_GREEN}; font-size: 8pt;")
            self._set_border(CP_GREEN)
            self._display.setStyleSheet(
                f"color: {CP_CYAN}; font-size: 26pt; font-weight: bold;"
                " font-family: 'Consolas'; letter-spacing: 2px;"
            )
            self.state_changed.emit()

    def _on_pause(self):
        if self.state == self.STATE_RUNNING:
            self._ticker.stop()
            self.state = self.STATE_PAUSED
            self._btn_start.setText("▶  RESUME")
            self._btn_start.setEnabled(True)
            self._btn_pause.setEnabled(False)
            self._status.setText("⏸ PAUSED")
            self._status.setStyleSheet(f"color: {CP_ORANGE}; font-size: 8pt;")
            self._set_border(CP_ORANGE)
            self.state_changed.emit()

    def _on_reset(self):
        self._ticker.stop()
        self.remaining = self.total_seconds
        self.state     = self.STATE_IDLE
        self._display.setText(fmt_secs(self.remaining))
        self._display.setStyleSheet(
            f"color: {CP_CYAN}; font-size: 26pt; font-weight: bold;"
            " font-family: 'Consolas'; letter-spacing: 2px;"
        )
        self._btn_start.setText("▶  START")
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._status.setText("READY")
        self._status.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 8pt;")
        self._set_border(CP_DIM)
        self._update_bar()
        self.state_changed.emit()

    def _on_delete(self):
        self._ticker.stop()
        self.removed.emit(self.card_id)

    # serialization
    def to_dict(self) -> dict:
        return {
            "id": self.card_id, "label": self.label,
            "total_seconds": self.total_seconds,
            "remaining": self.remaining, "state": self.state,
        }

    @classmethod
    def from_dict(cls, d: dict, parent=None) -> "TimerCard":
        card = cls(d["id"], d.get("label", "Timer"), d.get("total_seconds", 0), parent)
        card.remaining = d.get("remaining", card.total_seconds)
        card._display.setText(fmt_secs(card.remaining))
        card._update_bar()
        st = d.get("state")
        if st == cls.STATE_RUNNING:
            card.state = cls.STATE_PAUSED
            card._btn_start.setText("▶  RESUME")
            card._status.setText("⏸ PAUSED (was running)")
            card._status.setStyleSheet(f"color: {CP_ORANGE}; font-size: 8pt;")
            card._set_border(CP_ORANGE)
        elif st == cls.STATE_DONE:
            card.state = cls.STATE_DONE
            card._display.setStyleSheet(
                f"color: {CP_RED}; font-size: 26pt; font-weight: bold;"
                " font-family: 'Consolas'; letter-spacing: 2px;"
            )
            card._status.setText("▐ ALARM!")
            card._status.setStyleSheet(
                f"color: {CP_RED}; font-size: 8pt; font-weight: bold;"
            )
            card._set_border(CP_RED)
            card._btn_start.setEnabled(False)
            card._btn_pause.setEnabled(False)
        return card



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

        ren_btn = QPushButton("✏ RENAME")
        ren_btn.setFixedHeight(26)
        ren_btn.setStyleSheet(
            f"QPushButton {{ background: #1e1e1e; border: 1px solid {CP_DIM};"
            f" color: {CP_CYAN}; font-size: 8pt; font-weight: bold;"
            f" padding: 0 6px; }}"
            f"QPushButton:hover {{ border-color: {CP_CYAN}; background: #252525; }}"
            f"QPushButton:pressed {{ background: {CP_CYAN}; color: #000; }}"
        )
        ren_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ren_btn.setToolTip("Rename column")
        ren_btn.clicked.connect(self._on_rename)

        del_btn = QPushButton("✖ DEL")
        del_btn.setFixedHeight(26)
        del_btn.setStyleSheet(
            f"QPushButton {{ background: #1e1e1e; border: 1px solid {CP_DIM};"
            f" color: {CP_RED}; font-size: 8pt; font-weight: bold;"
            f" padding: 0 6px; }}"
            f"QPushButton:hover {{ border-color: {CP_RED}; background: #2a1010; }}"
            f"QPushButton:pressed {{ background: {CP_RED}; color: #fff; }}"
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
        card.state_changed.connect(self.state_changed)

    def remove_card(self, card_id: str):
        card = self._cards.pop(card_id, None)
        if card:
            self._card_layout.removeWidget(card)
            card.deleteLater()

    def _on_add_timer(self):
        result = AddTimerDialog.get_timer(self)
        if result is None:
            return
        label, secs = result
        card = TimerCard(str(uuid.uuid4())[:8], label, secs, self)
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
DEFAULT_SETTINGS = {"column_width": 280, "alarm_sound": ""}


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
        self._btn_save     = self._tbtn("💾  SAVE",     CP_DIM,  CP_TEXT)

        self._btn_add_col.clicked.connect(self._on_add_col)
        self._btn_settings.clicked.connect(self._on_settings)
        self._btn_restart.clicked.connect(self._on_restart)
        self._btn_save.clicked.connect(self._save)

        for b in (self._btn_add_col, self._btn_settings,
                  self._btn_restart, self._btn_save):
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
        if not hasattr(self, "_db") or not self._db.isActive():
            self._db = QTimer(self)
            self._db.setSingleShot(True)
            self._db.timeout.connect(self._save)
        self._db.start(2000)

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
            self._settings.update(data.get("settings", {}))
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
