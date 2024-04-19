import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt

class CustomWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="cpu_usage")
        self.interval = update_interval // 1000

        self._cpu_label = QLabel("CPU: -%")
        self.widget_layout.addWidget(self._cpu_label)  # Add CPU label

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
        # CPU usage
        cpu_usage = psutil.cpu_percent()
        self._cpu_label.setText(f"{cpu_usage}%")
        #! self._cpu_label.setText(f"CPU: {cpu_usage}%")
        self._cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._cpu_label.setStyleSheet(self._determine_color(cpu_usage))

    def _determine_color(self, usage):
        if usage == 0:
            return "background-color: #1d2027; color: #00ff21"  # Black background, green text
        elif usage < 25:
            return "background-color: #1d2027; color: #00ff21"  # Black background, green text
        elif 10 <= usage < 50:
            return "background-color: #ff9282; color: #000000"  # Red background, black text
        elif 50 <= usage < 80:
            return "background-color: #ff6b54; color: #000000"  # Orange background, black text
        else:
            return "background-color: #ff3010; color: #FFFFFF"  # Yellow background, white text

if __name__ == "__main__":
    app = QApplication([])
    widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()
