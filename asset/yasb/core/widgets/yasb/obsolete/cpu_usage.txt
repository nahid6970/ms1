import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

class CPU_MULTI_Widget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="traffic-widget")

        self._label_content = label
        self._label_alt_content = label_alt

        self._cpu_usage_label = QLabel()
        self.widget_layout.addWidget(self._cpu_usage_label)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self.start_timer()

    def _toggle_label(self):
        pass

    def _update_label(self):
        cpu_usage = self._get_cpu_usage()
        self._cpu_usage_label.setText("CPU Usage: " + cpu_usage)

    def _get_cpu_usage(self) -> str:
        cpu_percent = psutil.cpu_percent()
        return f"{cpu_percent:.2f}%"

class CPUWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.cpu_core_bars = []
        for i in range(psutil.cpu_count()):
            core_bar = QLabel()
            self.cpu_core_bars.append(core_bar)
            self.layout.addWidget(core_bar)

        self.update_cpu_core_bars()

    def update_cpu_core_bars(self):
        cpu_core_usage = self.get_cpu_core_usage()
        for i, usage in enumerate(cpu_core_usage):
            core_bar = self.cpu_core_bars[i]
            core_bar.setText(f"Core {i+1}: {usage}%")

        QTimer.singleShot(1000, self.update_cpu_core_bars)

    def get_cpu_core_usage(self):
        cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
        return cpu_usage_per_core

if __name__ == "__main__":
    app = QApplication([])

    # Create the main widget
    main_widget = CPU_MULTI_Widget("CPU Usage", "CPU Usage", 1000, {"on_left": "", "on_right": "", "on_middle": ""})

    # Create the CPU usage bars widget
    cpu_widget = CPUWidget()
    cpu_widget.show()

    # Start the application event loop
    app.exec()
