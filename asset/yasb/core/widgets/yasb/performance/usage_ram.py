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
        super().__init__(update_interval, class_name="ram_usage")
        self.interval = update_interval // 1000

        self._ram_label = QLabel("RAM: -%")
        self.widget_layout.addWidget(self._ram_label)  # Add RAM label

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
        # RAM usage
        ram_usage = psutil.virtual_memory().percent
        self._ram_label.setText(f"{ram_usage}%")
        self._ram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        #! self._ram_label.setText(f"RAM: {ram_usage}%")
        self._ram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._ram_label.setStyleSheet(self._determine_color(ram_usage))

    def _determine_color(self, usage):
        if usage > 80:
            return "background-color: #f12c2f; color: #FFFFFF"  # Red background, white text
        else:
            return "background-color: #03415f; color: #ff934b"  # Black background, orange text
            # return "background-color: #1d2027; color: #ff934b"  # Black background, orange text

if __name__ == "__main__":
    app = QApplication([])
    widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()
