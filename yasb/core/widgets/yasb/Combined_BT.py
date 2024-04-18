import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import subprocess
import os
import time

class HoverLabel(QLabel):
    def __init__(self, initial_color, hover_color, hover_after_color, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet(initial_color)
        self.hover_color = hover_color
        self.hover_after_color = hover_after_color

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.hover_after_color)
        super().leaveEvent(event)

class CombinedWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA
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

        self._Edit_label = HoverLabel(
            initial_color="background-color: #282c34; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;",
            hover_color="background-color: #ff0000; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;",
            hover_after_color="background-color: #00ff00; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"
        )

        self._chrome_label = HoverLabel(
            initial_color="background-color: #000000; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;",
            hover_color="background-color: #0000ff; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;",
            hover_after_color="background-color: #ff0000; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"
        )

        self._reload_label = HoverLabel(
            initial_color="background-color: #000000; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;",
            hover_color="background-color: #0000ff; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;",
            hover_after_color="background-color: #ff0000; color: #FFFFFF; border: 1px solid black; border-radius: 5px; margin: 4px 3px;"
        )

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
        self._chrome_label.setText("\uf005")
        self._reload_label.setText("\uf256")

        self._Edit_label.mousePressEvent = lambda event: self._on_Edit_click(event, self._Edit_label)
        self._chrome_label.mousePressEvent = lambda event: self._on_chrome_click(event, self._chrome_label)
        self._reload_label.mousePressEvent = lambda event: self._reload_yasb(event, self._reload_label)


    def _on_Edit_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'C:\ms1\mypygui_import\edit_files.py'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'code', '-g', 'C:\\ms1\\mypygui_import\\edit_files.py:89'])

    def _on_chrome_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'start', 'taskmgr.exe'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'start', 'taskmgr.exe'])

    def _reload_yasb(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            os.system('cmd /c start taskkill /f /im python.exe')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'start', 'taskmgr.exe'])

if __name__ == "__main__":
    app = QApplication([])
    widget = CombinedWidget("Download", "Upload", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()






