import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, QObject, QRunnable, QThreadPool, pyqtSignal
import time

class WorkerSignals(QObject):
    result = pyqtSignal(list)

class ProcessWorker(QRunnable):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals

    def run(self):
        while True:
            processes_mapping = {
                #   "Notepad.exe":  {"abbreviation": "&nbsp;N  ","bg_color": "#add8e6","fg_color": "#000080","width": 30},
                  "python.exe":   {"abbreviation": "&nbsp;P  ","bg_color": "#3772a4","fg_color": "#000000","width": 20},
                  "Code.exe":     {"abbreviation": "&nbsp;C  ","bg_color": "#23a9f2","fg_color": "#000000","width": 25},
                  "whkd.exe":     {"abbreviation": "&nbsp;W  ","bg_color": "#FFFFFF","fg_color": "#000000","width": 25},
                  "komorebi.exe": {"abbreviation": "&nbsp;K  ","bg_color": "#9068b0","fg_color": "#000000","width": 25},
                  "glazewm.exe":  {"abbreviation": "&nbsp;GW ","bg_color": "#41bdf8","fg_color": "#000000","width": 25}
            }
            active_processes = [processes_mapping[p] for p in processes_mapping if self._is_process_running(p)]
            self.signals.result.emit(active_processes)
            time.sleep(1)  # Adjust the update interval as needed

    def _is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

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

        self.callback_right = callbacks["on_right"]

        # Create a thread pool and signals for communication
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()

        # Create and start the worker
        self.worker = ProcessWorker(self.signals)
        self.signals.result.connect(self.update_label)
        self.threadpool.start(self.worker)

    def update_label(self, active_processes):
        if active_processes:
            labels = []
            for process in active_processes:
                label_text = process["abbreviation"]
                bg_color = process["bg_color"]
                fg_color = process["fg_color"]
                width = process["width"]
                label_style = f"background-color: {bg_color}; color: {fg_color}; width: {width}px; padding: 2px 5px; border-radius: 3px;"
                label_html = f"<span style='{label_style}'>{label_text}</span>"
                labels.append(label_html)
            self._label.setText("Active: " + " ".join(labels))
        else:
            self._label.setText("No active processes")
