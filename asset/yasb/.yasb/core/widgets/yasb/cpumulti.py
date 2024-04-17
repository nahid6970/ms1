import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import subprocess

class MultiCPU_Widget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="multicpu-widget")
        self.interval = update_interval // 1000

        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

        self._cpu_core_bars = []

        self.widget_layout.addWidget(QLabel("\uf4bc"))

        for _ in range(psutil.cpu_count()):
            bar = QLabel()
            bar.setStyleSheet("background-color: #1d2027; border: 1px solid black; border-radius: 3px;")
            self._cpu_core_bars.append(bar)
            self.widget_layout.addWidget(bar)

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
        cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)

        for bar, usage in zip(self._cpu_core_bars, cpu_usage_per_core):
            bar_height = int((usage / 100) * 25)  # Max bar height is 25 pixels
            bar.setStyleSheet(f"background-color: {self._determine_color(usage)}; border: 1px solid black; border-radius: 3px;")
            bar.setFixedHeight(bar_height)

    def _determine_color(self, usage):
        if usage >= 90:
            return "#8B0000"
        elif usage >= 80:
            return "#f12c2f"
        elif usage >= 50:
            return "#ff9282"
        else:
            return "#14bcff"

if __name__ == "__main__":
    app = QApplication([])
    widget = MultiCPU_Widget("CPU Usage", "CPU Usage", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()
