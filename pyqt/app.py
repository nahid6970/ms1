import sys
import psutil
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QTimer, QTime
import subprocess
import datetime

class CPUMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Info")
        self.setGeometry(0, 0, 1920, 40)
        self.setFixedSize(1920, 40)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool) # Added Qt.Tool flag
        self.setStyleSheet("") # Remove inline style

        # ... (rest of your __init__ method remains the same) ...
        # --- Left Section ---
        self.explorer_button = QPushButton("Explorer")
        self.calculator_button = QPushButton("Calc")  # Shortened text
        self.settings_button = QPushButton("Settings")

        # Set size policy to make buttons take minimum space
        size_policy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        self.explorer_button.setSizePolicy(size_policy)
        self.calculator_button.setSizePolicy(size_policy)
        self.settings_button.setSizePolicy(size_policy)

        self.explorer_button.clicked.connect(self.open_explorer)
        self.calculator_button.clicked.connect(self.open_calculator)
        self.settings_button.clicked.connect(self.open_settings)

        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(5, 0, 5, 0)  # Reduce layout margins
        left_layout.setSpacing(2)  # Reduce spacing between widgets
        left_layout.addWidget(self.explorer_button)
        left_layout.addWidget(self.calculator_button)
        left_layout.addWidget(self.settings_button)

        self.left_widget = QWidget()
        self.left_widget.setLayout(left_layout)
        self.left_widget.setObjectName("leftWidget")

        # --- Center Section ---
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setObjectName("clockLabel")
        self.clock_label.setStyleSheet("font-size: 16px;") # Slightly smaller font
        self.update_clock()

        # --- Right Section ---
        self.cpu_label = QLabel("CPU: 0%")
        self.ram_label = QLabel("RAM: 0%")
        self.cpu_label.setAlignment(Qt.AlignCenter)
        self.ram_label.setAlignment(Qt.AlignCenter)
        self.cpu_label.setObjectName("cpuLabel")
        self.ram_label.setObjectName("ramLabel")
        self.cpu_label.setStyleSheet("font-size: 16px; margin: 0 3px;") # Smaller font and margins
        self.ram_label.setStyleSheet("font-size: 16px; margin: 0 3px;") # Smaller font and margins

        right_layout = QHBoxLayout()
        right_layout.setContentsMargins(5, 0, 5, 0)  # Reduce layout margins
        right_layout.setSpacing(5)  # Reduce spacing
        right_layout.addWidget(self.cpu_label)
        right_layout.addWidget(self.ram_label)

        self.right_widget = QWidget()
        self.right_widget.setLayout(right_layout)
        self.right_widget.setObjectName("rightWidget")

        # --- Main Layout ---
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0) # Reduce main layout margins
        self.main_layout.setSpacing(0) # Reduce main layout spacing
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.clock_label, stretch=1) # Added stretch to clock
        self.main_layout.addWidget(self.right_widget)

        self.setLayout(self.main_layout)

        # --- Timers ---
        self.cpu_ram_timer = QTimer()
        self.cpu_ram_timer.timeout.connect(self.update_cpu_ram_usage)
        self.cpu_ram_timer.start(1000)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(100)

        # --- Apply Stylesheet ---
        self.apply_stylesheet()

    def apply_stylesheet(self):
        try:
            with open("C:\\Users\\nahid\\Desktop\\per\\customize\\style.css", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet file not found: customize/style.css")

    def open_explorer(self):
        subprocess.Popen(['explorer'])

    def open_calculator(self):
        subprocess.Popen(['calc'])

    def open_settings(self):
        subprocess.Popen(['control', 'panel'])

    def update_cpu_ram_usage(self):
        cpu_percent = int(psutil.cpu_percent())  # Converted to integer
        ram_info = psutil.virtual_memory()
        ram_percent = int(ram_info.percent)  # Converted to integer
        self.cpu_label.setText(f"CPU: {cpu_percent}%")
        self.ram_label.setText(f"RAM: {ram_percent}%")

    def update_clock(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M:%S %p")  # Changed to 12-hour format
        self.clock_label.setText(current_time)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    cpu_monitor = CPUMonitor()
    cpu_monitor.show()
    sys.exit(app.exec_())