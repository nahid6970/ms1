import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
import subprocess

class TrafficWidget(BaseWidget):
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
        super().__init__(update_interval, class_name="traffic-widget")
        self.interval = update_interval // 1000

        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

        self._upload_label = QLabel()
        self._download_label = QLabel()
        self._notepad_label = QLabel()
        self._chrome_label = QLabel()
        self._vscode_label = QLabel()

        self.widget_layout.addWidget(self._upload_label)
        self.widget_layout.addWidget(self._download_label)
        self.widget_layout.addWidget(self._notepad_label)
        self.widget_layout.addWidget(self._chrome_label)
        self.widget_layout.addWidget(self._vscode_label)

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

        try:
            upload_speed, download_speed = self._get_speed()
        except Exception:
            upload_speed, download_speed = "N/A", "N/A"

        self._upload_label.setText("\udb80\uddda " + upload_speed)
        self._download_label.setText("\udb81\udd52 " + download_speed)

        self._set_label_color(self._upload_label, upload_speed)
        self._set_label_color(self._download_label, download_speed)

        # Set text and colors for additional labels
        self._notepad_label.setText("Notepad")
        self._chrome_label.setText("Chrome")
        self._vscode_label.setText("VSCode")

        self._set_label_color(self._notepad_label, "Notepad")
        self._set_label_color(self._chrome_label, "Chrome")
        self._set_label_color(self._vscode_label, "VSCode")

        # Connect click events to respective functions
        self._download_label.mousePressEvent = self._open_settings
        self._upload_label.mousePressEvent = self._open_task_manager
        self._notepad_label.mousePressEvent = self._open_notepad
        self._chrome_label.mousePressEvent = self._open_chrome
        self._vscode_label.mousePressEvent = self._open_vscode

    def _set_label_color(self, label, content):
        # Define colors and stylesheets based on content
        if content == "Notepad":
            bg_color = "#FF5733"  # Orange
            fg_color = "#000000"  # Black
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px;"
        elif content == "Chrome":
            bg_color = "#4285F4"  # Blue
            fg_color = "#FFFFFF"  # White
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px;"
        elif content == "VSCode":
            bg_color = "#007ACC"  # Dark Blue
            fg_color = "#FFFFFF"  # White
            stylesheet = f"background-color: {bg_color}; color: {fg_color}; border: 1px solid black; border-radius: 5px;"
        else:
            speed_float = float(content.split()[0])
            if speed_float == 0:
                bg_color = "#1d2027"  # Dark Grey
                fg_color = "#FFFFFF"  # White
            elif 0 < speed_float < 0.5:
                bg_color = "#dfffdf"  # Light Green
                fg_color = "#000000"  # Black
            elif 0.5 <= speed_float < 1:
                bg_color = "#67D567"  # Green
                fg_color = "#000000"  # Black
            elif 1 <= speed_float < 5:
                bg_color = "#4b95e9"  # Blue
                fg_color = "#000000"  # Black
            else:
                bg_color = "#ff0000"  # Red
                fg_color = "#000000"  # Black
            stylesheet = f"background-color: {bg_color}; color: {fg_color};"

        label.setStyleSheet(stylesheet)

    def _get_speed(self) -> [str, str]:
        current_io = psutil.net_io_counters()
        download_diff = current_io.bytes_recv - self.bytes_recv
        upload_diff = current_io.bytes_sent - self.bytes_sent

        # Convert bytes to MB
        download_speed = download_diff / (1024 * 1024 * self.interval)
        upload_speed = upload_diff / (1024 * 1024 * self.interval)

        # Format speeds to two decimal places
        download_speed_str = "{:.2f}".format(download_speed)
        upload_speed_str = "{:.2f}".format(upload_speed)

        self.bytes_sent = current_io.bytes_sent
        self.bytes_recv = current_io.bytes_recv

        return download_speed_str, upload_speed_str

    def _open_settings(self, event):
        # Open settings when download label is clicked
        subprocess.Popen(['cmd.exe', '/c', 'start', 'ms-settings:'])

    def _open_task_manager(self, event):
        # Open task manager when upload label is clicked
        subprocess.Popen(['cmd.exe', '/c', 'start', 'taskmgr.exe'])

    def _open_notepad(self, event):
        # Open Notepad when Notepad label is clicked
        subprocess.Popen(['notepad.exe'])

    def _open_chrome(self, event):
        # Open Chrome when Chrome label is clicked
        subprocess.Popen(['cmd.exe', '/c', 'start', 'chrome.exe'])

    def _open_vscode(self, event):
        # Open VSCode when VSCode label is clicked
        subprocess.Popen(['cmd.exe', '/c','code'])

if __name__ == "__main__":
    app = QApplication([])
    widget = TrafficWidget("Download", "Upload", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()
