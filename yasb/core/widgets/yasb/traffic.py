import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel


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

        self.widget_layout.addWidget(self._upload_label)
        self.widget_layout.addWidget(self._download_label)

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

    def _set_label_color(self, label, speed):
        speed_float = float(speed.split()[0])

        if speed_float == 0:
            bg_color = "#1d2027"
            fg_color = "#FFFFFF"
        elif 0 < speed_float < 0.5:
            bg_color = "#A8E4A8"
            fg_color = "#000000"
        elif 0.5 <= speed_float < 1:
            bg_color = "#67D567"
            fg_color = "#000000"
        elif 1 <= speed_float < 5:
            bg_color = "#32AB32"
            fg_color = "#000000"
        else:
            bg_color = "#ff0000"
            fg_color = "#000000"

        label.setStyleSheet(f"background-color: {bg_color}; color: {fg_color};")

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
