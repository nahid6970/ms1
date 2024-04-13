import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer

class ProcessWidget(BaseWidget):
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

        self._label = QLabel()
        self.widget_layout.addWidget(self._label)

        self._update_label()

        self.callback_right = callbacks["on_right"]

        # Create a QTimer instance for updating the label text
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_label)
        self.timer.start(update_interval)

    def _update_label(self):
        processes_mapping = {
            "Notepad.exe": {"abbreviation": "&nbsp;N ", "bg_color": "#add8e6", "fg_color": "#000080", "width": 30},
            "whkd.exe": {"abbreviation": "&nbsp;W ", "bg_color": "#ffffff", "fg_color": "#000080", "width": 30},
            "python.exe": {"abbreviation": "&nbsp;P ", "bg_color": "#0000FF", "fg_color": "#FFFFFF", "width": 20},
            "Code.exe": {"abbreviation": "&nbsp;C ", "bg_color": "#FF0000", "fg_color": "#008000", "width": 25}
        }
        active_processes = [processes_mapping[p] for p in processes_mapping if self._is_process_running(p)]

        if active_processes:
            labels = []
            for process in active_processes:
                label_text = process["abbreviation"]
                bg_color = process["bg_color"]
                fg_color = process["fg_color"]
                width = process["width"]
                label_style = f"background-color: {bg_color}; color: {fg_color}; padding: 10px 10px; border-radius: 3px; width: {width}px;"
                label_html = f"<span style='{label_style}'>{label_text}</span>"
                labels.append(label_html)
            self._label.setText("Active: " + " ".join(labels))
        else:
            self._label.setText("No active processes")

    def _is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False
