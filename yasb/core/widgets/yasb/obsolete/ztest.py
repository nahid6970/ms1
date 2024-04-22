from PyQt6.QtWidgets import QLabel
from core.widgets.base import BaseWidget
from pyadl import ADLManager

class GPUUsageWidget(BaseWidget):
    def __init__(
            self,
            label: str,
            label_alt: str,
            update_interval: int,
            callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="gpu-usage-widget")
        self._label_content = label
        self._label_alt_content = label_alt
        self._label = QLabel()
        self._label_alt = QLabel()
        self._label.setProperty("class", "label")
        self._label_alt.setProperty("class", "label alt")
        self.widget_layout.addWidget(self._label)
        self.widget_layout.addWidget(self._label_alt)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)
        self.callback_left = callbacks['on_left']
        self.callback_right = callbacks['on_right']
        self.callback_middle = callbacks['on_middle']
        self.callback_timer = "update_label"

        self._label.show()
        self._label_alt.hide()
        self._show_alt_label = False
        self._update_label()
        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label

        if self._show_alt_label:
            self._label.hide()
            self._label_alt.show()
        else:
            self._label.show()
            self._label_alt.hide()

        self._update_label()

    def _update_label(self):
        active_label = self._label_alt if self._show_alt_label else self._label
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content

        gpu_usage = self._get_gpu_usage()
        label_content = active_label_content.format(gpu_usage=gpu_usage)
        active_label.setText(label_content)

        # Set background color based on GPU usage
        if gpu_usage == "0":
            active_label.setStyleSheet("background-color: #1d2027; color: #00ff21;")
        elif float(gpu_usage) < 25:
            active_label.setStyleSheet("background-color: #1d2027; color: #00ff21;")
        elif 10 <= float(gpu_usage) < 50:
            active_label.setStyleSheet("background-color: #ff9282; color: #000000;")
        elif 50 <= float(gpu_usage) < 80:
            active_label.setStyleSheet("background-color: #ff6b54; color: #000000;")
        else:
            active_label.setStyleSheet("background-color: #ff3010; color: #FFFFFF;")

    def _get_gpu_usage(self):
        try:
            # Get the first GPU device (you can modify this if you have multiple GPUs)
            device = ADLManager.getInstance().getDevices()[0]
            # Get the current GPU usage
            gpu_usage = device.getCurrentUsage()
            return gpu_usage
        except Exception as e:
            print(f"Error retrieving GPU usage: {e}")
            return "N/A"  # Return a default value in case of error
