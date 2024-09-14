import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt

#! Step 1
def get_disk_info():
    disk_c_usage = psutil.disk_usage('C:').percent
    disk_d_usage = psutil.disk_usage('D:').percent
    return disk_c_usage, disk_d_usage

class CustomWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="disk_usage")
        self.interval = update_interval // 1000

#! Step 2
        self._disk_c_label = QLabel("C: -%")
        self._disk_d_label = QLabel("D: -%")

#! Step 3
        self.widget_layout.addWidget(self._disk_c_label)  # Add C drive label
        self.widget_layout.addWidget(self._disk_d_label)  # Add D drive label

        self.callbacks = callbacks  # Store callbacks

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self.register_callback("update_label", self._update_label)  # Register update_label callback

        self.start_timer()

#! Step 4
    def _update_label(self):
        disk_c_usage, disk_d_usage= get_disk_info()
#! Step 5
        self._disk_c_label.setText(f"\uf0a0 \udb82\udff2 {disk_c_usage:.2f}%")
        self._disk_d_label.setText(f" \uf0a0 \udb82\udff5 {disk_d_usage:.2f}%")
#! Step 6
        self._disk_c_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._disk_d_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
#! Step 6
        self._disk_c_label.setStyleSheet(self._determine_color(disk_c_usage, 'C:'))
        self._disk_d_label.setStyleSheet(self._determine_color(disk_d_usage, 'D:'))

#! Step 7
    def _determine_color(self, usage, label):
        if label == 'C:' and usage > 90:
            return "background-color: #f12c2f; color: #FFFFFF"
        elif label == 'D:' and usage > 90:
            return "background-color: #f12c2f; color: #FFFFFF"
        else:
            return "background-color: #044568; color: #ffffff"

if __name__ == "__main__":
    app = QApplication([])
    widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": "", "update_label": ""})
    widget.show()
    app.exec()
