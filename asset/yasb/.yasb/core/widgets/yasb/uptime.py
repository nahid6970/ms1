import psutil
from datetime import datetime, timedelta
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer

class UptimeWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="uptime-widget")

        self._label_content = label
        self._label_alt_content = label_alt

        self._label = QLabel()
        self.widget_layout.addWidget(self._label)

        self._update_label()

        self.callback_right = callbacks["on_right"]

        # Create a QTimer instance for updating the label text
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_label)
        self.timer.start(update_interval)

    def _update_label(self):
        boot_time = psutil.boot_time()
        uptime = datetime.now() - datetime.fromtimestamp(boot_time)
        days, hours, minutes = uptime.days, uptime.seconds // 3600, (uptime.seconds // 60) % 60
        uptime_str = f"{days}d, {hours}h, {minutes}m"
        
        self._label.setText(uptime_str)
