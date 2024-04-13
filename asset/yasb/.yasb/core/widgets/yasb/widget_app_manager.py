import os
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt

class AppWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="app-widget")

        self._label_content = label
        self._label_alt_content = label_alt

        self._label = QLabel()
        self._label.setText("A")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._label.setStyleSheet("background-color: #4b95e9; color: #000000;")
        self.widget_layout.addWidget(self._label)
        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]

        self._label.mousePressEvent = self._on_mouse_press_event

    def _on_mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            os.system("start C:/ms1/mypygui_import/applist.py")
        elif event.button() == Qt.MouseButton.RightButton:
            os.system("start C:/ms1/mypygui_import/app_store.py")
