import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import subprocess
import os
import time

class PowerToysWidget(BaseWidget):
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
        super().__init__(update_interval, class_name="powertoys_combined-widget")
        self.interval = update_interval // 1000

        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

        self.PowerToys_Mouse_Pointer = QLabel()
        self.PowerToys_Text_Extract = QLabel()
        self.PowerToys_Screen_Ruler = QLabel()
        self.PowerToys_Screen_Color = QLabel()

        self.widget_layout.addWidget(self.PowerToys_Mouse_Pointer)
        self.widget_layout.addWidget(self.PowerToys_Text_Extract)
        self.widget_layout.addWidget(self.PowerToys_Screen_Ruler)
        self.widget_layout.addWidget(self.PowerToys_Screen_Color)

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
        self.PowerToys_Mouse_Pointer.setText("\uf245")
        self.PowerToys_Text_Extract.setText("\udb80\ude84")
        self.PowerToys_Screen_Ruler.setText("\udb84\udf53")
        self.PowerToys_Screen_Color.setText("\ue275")

        self._set_label_color(self.PowerToys_Mouse_Pointer, "button_1")
        self._set_label_color(self.PowerToys_Text_Extract, "button_2")
        self._set_label_color(self.PowerToys_Screen_Ruler, "button_3")
        self._set_label_color(self.PowerToys_Screen_Color, "button_4")

        self.PowerToys_Mouse_Pointer.mousePressEvent = lambda event: self._on_button_1_click(event, self.PowerToys_Mouse_Pointer)
        self.PowerToys_Text_Extract.mousePressEvent = lambda event: self._on_button_2_click(event, self.PowerToys_Text_Extract)
        self.PowerToys_Screen_Ruler.mousePressEvent = lambda event: self._on_button_3_click(event, self.PowerToys_Screen_Ruler)
        self.PowerToys_Screen_Color.mousePressEvent = lambda event: self._on_button_4_click(event, self.PowerToys_Screen_Color)

    def _set_label_color(self, label, content):
        if content == "button_1":
            bg_color = "#e75c1c"
            fg_color = "#000000" 
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"
        elif content == "button_2":
            bg_color = "#e75c1c"
            fg_color = "#000000"
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"
        elif content == "button_3":
            bg_color = "#e75c1c"
            fg_color = "#000000"
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"
        elif content == "button_4":
            bg_color = "#e75c1c"
            fg_color = "#000000"
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"

        label.setStyleSheet(stylesheet)

    def _on_button_1_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'python C:\\ms1\\HotKeys.py powertoys_mouse_crosshair'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c',''])

    def _on_button_2_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'python C:\\ms1\\HotKeys.py powertoys_TextExtract'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c',''])

    def _on_button_3_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'python C:\\ms1\\HotKeys.py powertoys_ruler'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c',''])

    def _on_button_4_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'python C:\\ms1\\HotKeys.py winnnnnnnnnn'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c',''])



if __name__ == "__main__":
    app = QApplication([])
    widget = PowerToysWidget("", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()
