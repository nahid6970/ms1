import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import subprocess
import os
import time

class CPU_Multi(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    # initialize io counters
    io = psutil.net_io_counters()
    bytes_sent = io.bytes_sent
    bytes_recv = io.bytes_recv
    interval = 1  # second(s)

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="combined-widget")
        self.interval = update_interval // 1000

        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

        self._Edit_label = QLabel()
        self._chrome_label = QLabel()
        self._reload_label = QLabel()

        self.widget_layout.addWidget(self._Edit_label)
        self.widget_layout.addWidget(self._chrome_label)
        self.widget_layout.addWidget(self._reload_label)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label
        self._update_label()

    def _update_label(self):
        # Update the active label at each timer interval
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content

        # Set text and colors for additional labels
        self._Edit_label.setText("\uf044")

        self._set_label_color(self._Edit_label, "Edit")


        self._Edit_label.mousePressEvent = lambda event: self._on_Edit_click(event, self._Edit_label)


    def _set_label_color(self, label, content):
        # Define colors and stylesheets based on content
        if content == "Edit":
            bg_color = "#bcd12f"  # Orange
            fg_color = "#000000"  # Black
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px;"

        label.setStyleSheet(stylesheet)

    def _on_Edit_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'C:\Users\nahid\.yasb\core\widgets\yasb\cpu\cpu_multi_widget.py'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen([])

if __name__ == "__main__":
    app = QApplication([])
    widget = CPU_Multi("Download", "Upload", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()
