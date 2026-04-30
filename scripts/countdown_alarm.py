import sys, os, threading, time
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QInputDialog
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

CP_BG = "#050505"; CP_CYAN = "#00F0FF"

class _AlarmSignal(QObject):
    alarm = pyqtSignal()
_alarm_signal = _AlarmSignal()

class CountdownState:
    active = False
    last_type = None
    last_minutes = None
countdown = CountdownState()

def _thread(minutes, ctype, lbl):
    t = minutes * 60
    while t > 0:
        if not countdown.active: lbl.setText("⏱"); return
        lbl.setText(f"⏱ {int(t)//60:02}:{int(t)%60:02}")
        time.sleep(1); t -= 1
    if countdown.active:
        countdown.active = False; lbl.setText("⏱")
        if ctype == 1: _alarm_signal.alarm.emit()
        else: os.system("shutdown /s /f /t 1")

def show_alarm():
    dlg = QDialog()
    dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    dlg.setStyleSheet("background: #1d2027;")
    dlg.resize(600, 300)
    lay = QVBoxLayout(dlg)
    lbl = QLabel("⏰ ALARM! Time's up!")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("color: #ff0000; font-size: 36pt; font-weight: bold;")
    lay.addWidget(lbl)
    _b = [True]
    t = QTimer(dlg)
    def blink():
        lbl.setStyleSheet(f"color: {'#ff0000' if _b[0] else '#00aaff'}; font-size: 36pt; font-weight: bold;")
        _b[0] = not _b[0]
    t.timeout.connect(blink); t.start(500)
    dlg.mousePressEvent = lambda e: dlg.accept()
    s = QApplication.primaryScreen().geometry()
    dlg.move(s.center().x() - 300, s.center().y() - 150)
    dlg.exec()

_alarm_signal.alarm.connect(show_alarm)

class MainDlg(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Countdown")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"background: {CP_BG}; color: white; font-family: Consolas; font-size: 11pt;")
        self.resize(200, 80)
        lay = QVBoxLayout(self)
        self.lbl = QLabel("⏱"); self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet("color: #fc6a35; font-size: 20pt; font-weight: bold;")
        self.lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lbl.mousePressEvent = self._click
        lay.addWidget(self.lbl)
        s = QApplication.primaryScreen().geometry()
        self.move(s.center().x() - 100, s.center().y() - 40)

    def _click(self, e):
        if e.button() == Qt.MouseButton.RightButton:
            self._repeat()
        else:
            self._new()

    def _new(self):
        if countdown.active: countdown.active = False; self.lbl.setText("⏱"); return
        choice, ok = QInputDialog.getInt(self, "Type", "1=Alarm  2=Shutdown", 1, 1, 2)
        if not ok: return
        mins, ok2 = QInputDialog.getDouble(self, "Minutes", "Enter minutes:", 5, 0.1, 9999, 1)
        if not ok2 or mins <= 0: return
        countdown.active = True; countdown.last_type = choice; countdown.last_minutes = mins
        threading.Thread(target=_thread, args=(mins, choice, self.lbl), daemon=True).start()

    def _repeat(self):
        if countdown.last_type is None: return
        if countdown.active: countdown.active = False; self.lbl.setText("⏱"); return
        countdown.active = True
        threading.Thread(target=_thread, args=(countdown.last_minutes, countdown.last_type, self.lbl), daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    w = MainDlg(); w.show()
    sys.exit(app.exec())
