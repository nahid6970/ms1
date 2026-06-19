import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt

BG      = "#FFFFFF"
PANEL   = "#F0F0F0"
BORDER  = "#CCCCCC"
TEXT    = "#111111"
ACCENT  = "#0078D4"
BTN_BG  = "#E0E0E0"

STYLE = f"""
QMainWindow, QWidget {{ background-color: {BG}; color: {TEXT}; font-family: Arial; font-size: 10pt; }}
QGroupBox {{ border: 1px solid {BORDER}; margin-top: 10px; padding-top: 10px; color: {ACCENT}; font-weight: bold; }}
QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
QLineEdit {{ background: {PANEL}; border: 1px solid {BORDER}; padding: 4px; color: {TEXT}; }}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QPushButton {{ background: {BTN_BG}; border: 1px solid {BORDER}; padding: 6px 14px; color: {TEXT}; font-weight: bold; }}
QPushButton:hover {{ background: {ACCENT}; color: white; border-color: {ACCENT}; }}
QLabel#title {{ font-size: 14pt; font-weight: bold; color: {ACCENT}; }}
"""

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note Taker")
        self.resize(400, 300)
        self.setStyleSheet(STYLE)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("NOTE TAKER")
        title.setObjectName("title")
        layout.addWidget(title)

        grp = QGroupBox("NEW NOTE")
        vbox = QVBoxLayout(grp)
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type your note here...")
        self.note_label = QLabel("No notes yet.")
        btn = QPushButton("SAVE NOTE")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._save)
        vbox.addWidget(self.input)
        vbox.addWidget(btn)
        vbox.addWidget(self.note_label)
        layout.addWidget(grp)
        layout.addStretch()

    def _save(self):
        text = self.input.text().strip()
        if text:
            self.note_label.setText(f"Saved: {text}")
            self.input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())
