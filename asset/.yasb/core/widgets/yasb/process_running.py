import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QHBoxLayout
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
                "whkd.exe":     {"abbreviation": "W","bg_color": "#FFFFFF","fg_color": "#000000"},
                "komorebi.exe": {"abbreviation": "K","bg_color": "#9068b0","fg_color": "#000000"},
                "glazewm.exe":  {"abbreviation": "GW","bg_color": "#41bdf8","fg_color": "#000000"},
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
        super().__init__(update_interval, class_name="process-widget")

        self._label_content = label
        self._label_alt_content = label_alt

        self.labels_layout = QHBoxLayout()
        self.widget_layout.addLayout(self.labels_layout)

        self.callback_right = callbacks["on_right"]

        # Create a thread pool and signals for communication
        self.threadpool = QThreadPool()
        self.signals = WorkerSignals()

        # Create and start the worker
        self.worker = ProcessWorker(self.signals)
        self.signals.result.connect(self.update_label)
        self.threadpool.start(self.worker)

    def update_label(self, active_processes):
        # Clear existing labels
        for i in reversed(range(self.labels_layout.count())):
            widgetToRemove = self.labels_layout.itemAt(i).widget()
            if widgetToRemove is not None:
                widgetToRemove.setParent(None)

        if active_processes:
            symbol_label = QLabel("\udb81\udc6e")
            symbol_label.setStyleSheet("color: white; font-size: 20px;")
            self.labels_layout.addWidget(symbol_label)


            for process in active_processes:
                label_text = process["abbreviation"]
                bg_color = process["bg_color"]
                fg_color = process["fg_color"]

                label = QLabel(label_text)
                label.setStyleSheet(f"background-color: {bg_color}; color: {fg_color}; padding: 2 5; margin: 2 2 2 2; border-radius: 3px;")
                self.labels_layout.addWidget(label)
        else:
            self._label = QLabel()
            self._label.setText("<font color='#efff28'>\uebde</font>")
            self.labels_layout.addWidget(self._label)
