import os
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt

class Browser(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="browser-widget")

        self._label_content = label
        self._label_alt_content = label_alt

        self._label = QLabel()
        self._label.setText("\udb80\udeaf")
        self._label.setStyleSheet(" font-family: 'JETBRAINSMONO NF'; font-size: 16px; background-color: #282c34; color: #FFFFFF; margin: 4px 3px; padding: 2px 6px;")
        self.widget_layout.addWidget(self._label)
        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]

        self._label.mousePressEvent = self._on_mouse_press_event

        # Connect hover events
        self._label.enterEvent = self._on_mouse_enter_event
        self._label.leaveEvent = self._on_mouse_leave_event

        # Flag to track hover state
        self._is_hovered = False

    def _on_mouse_press_event(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            os.system("start C:/ms1/mypygui_import/applist.py")
        elif event.button() == Qt.MouseButton.RightButton:
            os.system("cmd /c python C:\\ms1\\HotKeys.py powertoys_mouse_crosshair")

    def _on_mouse_enter_event(self, event):
        # Change style or perform actions when mouse enters the widget
        self._is_hovered = True
        # Example: Change background color
        self._label.setStyleSheet("font-family: 'JETBRAINSMONO NF'; font-size: 16px; background-color: #b2b2b2; color: #000000; margin: 4px 3px; padding: 2px 6px;")

    def _on_mouse_leave_event(self, event):
        # Revert style or perform actions when mouse leaves the widget
        self._is_hovered = False
        # Example: Revert background color
        self._label.setStyleSheet(" font-family: 'JETBRAINSMONO NF'; font-size: 16px; background-color: #282c34; color: #FFFFFF; margin: 4px 3px; padding: 2px 6px;")

# Example usage
if __name__ == "__main__":
    app = QApplication([])
    widget = Browser(label="Label", label_alt="Alt Label", update_interval=1000, callbacks={"on_left": "left_action", "on_right": "right_action"})
    widget.show()
    app.exec()
