from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import os

class CustomWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="manual_css")
        self.interval = update_interval // 1000

        self._path_label = QLabel("")
        self.widget_layout.addWidget(self._path_label)  # Add path label

        self.callbacks = callbacks  # Store callbacks

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self.register_callback("update_label", self._update_label)  # Register update_label callback

        self.start_timer()

    def _update_label(self):
        # Check if the path exists
        path = "d:/test/"
        if os.path.exists(path):
            status = "\uf023"
            color = "#4CAF50"  # Green color for accessible path
        else:
            status = "\uf13e"
            color = "#f44336"  # Red color for inaccessible path

        self._path_label.setText(f"{status}")
        #! self._path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._path_label.setStyleSheet(f"color: {color}; font-size: 16px;")

if __name__ == "__main__":
    app = QApplication([])
    widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": "", "update_label": ""})
    widget.show()
    app.exec()
