from core.widgets.base import BaseWidget
from PyQt6.QtWidgets import QLabel

class TestWidget(BaseWidget):
    def __init__(
        self,
        label: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="test-widget")

        self._label_content = label

        self._label = QLabel()
        self._label.setProperty("class", "label")
        self.widget_layout.addWidget(self._label)

        self.register_callback("update_label", self._update_label)
        self.callback_timer = "update_label"

        self._update_label()

        self.start_timer()

    def _update_label(self):
        self._label.setText(self._label_content)
        self._label.setStyleSheet("background-color: red; color: white")
