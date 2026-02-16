import sys
import psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QPushButton
)
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation, QRect, QEasingCurve
from PyQt6.QtGui import QColor


class ProcessViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.processes = []
        self.is_expanded = False
        self.sort_mode = 0  # 0: Default, 1: CPU, 2: RAM
        self.init_ui()
        self.load_processes()
        # Update processes every 2 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_processes)
        self.timer.start(2000)

    def init_ui(self):
        self.setWindowTitle('Process Viewer')
        # Start with compact size centered on screen
        screen = QApplication.primaryScreen().geometry()
        compact_width = 600
        compact_height = 100  # Increased to accommodate bigger search box
        x = (screen.width() - compact_width) // 2
        y = (screen.height() - compact_height) // 2
        self.setGeometry(x, y, compact_width, compact_height)
        
        # Store expanded dimensions
        self.expanded_width = 1000
        self.expanded_height = 600

        # Main layout
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('Search:'))
        self.search_bar = QLineEdit()
        self.search_bar.setMinimumHeight(40)  # Make search box taller
        self.search_bar.setStyleSheet("font-size: 14px; padding: 5px;")  # Bigger font and padding
        self.search_bar.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_bar)

        # Add toggle button beside kill button
        self.toggle_button = QPushButton("D")
        self.toggle_button.setToolTip("Sort: Default")
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        self.toggle_button.setFixedSize(30, 30)
        self.toggle_button.clicked.connect(self.toggle_sort_mode)
        search_layout.addWidget(self.toggle_button)

        # Add red round button to kill matching processes
        self.kill_button = QPushButton("●")
        self.kill_button.setToolTip("Kill matching processes")
        self.kill_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 16px;
                font-weight: bold;
                width: 30px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
            QPushButton:pressed {
                background-color: crimson;
            }
        """)
        self.kill_button.setFixedSize(30, 30)
        self.kill_button.clicked.connect(self.kill_matching_processes)
        search_layout.addWidget(self.kill_button)

        layout.addLayout(search_layout)

        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(4)
        self.process_table.setHorizontalHeaderLabels(['Name', 'CPU %', 'RAM %', 'Command Path'])
        # Set specific resize modes for columns
        self.process_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Name
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # CPU
        self.process_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # RAM
        self.process_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Command Path
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Hide table initially
        self.process_table.hide()
        layout.addWidget(self.process_table)

        # Focus on search bar by default
        self.search_bar.setFocus()
        
        # Enable keyboard navigation
        self.search_bar.returnPressed.connect(self.on_search_enter)
        self.process_table.keyPressEvent = self.table_key_press_event

        self.setLayout(layout)

    def toggle_sort_mode(self):
        self.sort_mode = (self.sort_mode + 1) % 3
        modes = ["D", "C", "M"]
        tooltips = ["Sort: Default", "Sort: Highest CPU", "Sort: Most RAM"]
        self.toggle_button.setText(modes[self.sort_mode])
        self.toggle_button.setToolTip(tooltips[self.sort_mode])
        self.filter_processes()

    def load_processes(self):
        # Get all processes with their information
        self.processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'cpu_percent', 'memory_percent']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                cpu = proc.info['cpu_percent'] if proc.info['cpu_percent'] is not None else 0.0
                mem = proc.info['memory_percent'] if proc.info['memory_percent'] is not None else 0.0
                
                # Try to get the full command line first, fallback to exe if not available
                if proc.info['cmdline']:
                    # Join the command line arguments into a single string
                    cmdline = ' '.join(proc.info['cmdline'])
                    exe = cmdline if cmdline else (proc.info['exe'] if proc.info['exe'] else 'N/A')
                else:
                    exe = proc.info['exe'] if proc.info['exe'] else 'N/A'
                self.processes.append({
                    'pid': pid,
                    'name': name,
                    'exe': exe,
                    'cpu': cpu,
                    'mem': mem
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have terminated or we don't have access
                pass

        # Always update the table view
        self.filter_processes()

    def on_search_changed(self):
        self.filter_processes()
    
    def expand_window(self):
        if self.is_expanded:
            return
        self.is_expanded = True
        self.process_table.show()
        
        # Get current geometry
        current_geo = self.geometry()
        
        # Calculate new position to keep window centered
        screen = QApplication.primaryScreen().geometry()
        new_x = (screen.width() - self.expanded_width) // 2
        new_y = (screen.height() - self.expanded_height) // 2
        
        # Animate the resize with smooth easing
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)  # Increased duration for smoother animation
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # Smooth deceleration
        self.animation.setStartValue(current_geo)
        self.animation.setEndValue(QRect(new_x, new_y, self.expanded_width, self.expanded_height))
        self.animation.start()
    
    def collapse_window(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        
        # Get current geometry
        current_geo = self.geometry()
        
        # Calculate new position to keep window centered
        screen = QApplication.primaryScreen().geometry()
        compact_width = 600
        compact_height = 100  # Match the increased compact height
        new_x = (screen.width() - compact_width) // 2
        new_y = (screen.height() - compact_height) // 2
        
        # Animate the resize with smooth easing
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)  # Increased duration for smoother animation
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)  # Smooth acceleration and deceleration
        self.animation.setStartValue(current_geo)
        self.animation.setEndValue(QRect(new_x, new_y, compact_width, compact_height))
        self.animation.finished.connect(lambda: self.process_table.hide())
        self.animation.start()

    def filter_processes(self):
        search_text = self.search_bar.text().strip()
        
        # Determine if we should show processes (if searching OR if in a non-default sort mode)
        should_show = bool(search_text) or self.sort_mode != 0
        
        if not should_show:
            if self.is_expanded:
                self.collapse_window()
            self.update_table([])
            return

        if not self.is_expanded:
            self.expand_window()

        # Split search text into multiple words
        search_terms = search_text.lower().split()
        
        # Filter processes based on search terms
        filtered_processes = []
        for proc in self.processes:
            if not search_terms:
                filtered_processes.append(proc)
                continue
                
            name_lower = proc['name'].lower()
            exe_lower = proc['exe'].lower()
            
            all_terms_match = True
            for term in search_terms:
                if term not in name_lower and term not in exe_lower:
                    all_terms_match = False
                    break
            
            if all_terms_match:
                filtered_processes.append(proc)
        
        # Apply sorting
        if self.sort_mode == 1:  # CPU
            filtered_processes.sort(key=lambda x: x['cpu'], reverse=True)
        elif self.sort_mode == 2:  # RAM
            filtered_processes.sort(key=lambda x: x['mem'], reverse=True)
            
        self.update_table(filtered_processes)

    def kill_matching_processes(self):
        # Get the current search text
        search_text = self.search_bar.text().strip()
        if not search_text:
            return  # Don't kill all processes if no search term

        # Split search text into multiple words
        search_terms = search_text.lower().split()
        
        # Find matching processes based on all search terms
        matching_processes = []
        for proc in self.processes:
            # Check if all search terms match either name or exe path
            name_lower = proc['name'].lower()
            exe_lower = proc['exe'].lower()
            
            # Check if all terms match
            all_terms_match = True
            for term in search_terms:
                if term not in name_lower and term not in exe_lower:
                    all_terms_match = False
                    break
            
            if all_terms_match:
                matching_processes.append(proc)

        # Terminate matching processes
        for proc in matching_processes:
            try:
                process = psutil.Process(proc['pid'])
                process.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have already terminated or we don't have permission
                pass

        # Refresh the process list after termination
        self.load_processes()

    def update_table(self, processes):
        # Clear the table
        self.process_table.setRowCount(0)

        # Add processes to the table
        for proc in processes:
            row_position = self.process_table.rowCount()
            self.process_table.insertRow(row_position)

            # Add process name with custom colors
            name_item = QTableWidgetItem(proc['name'])
            name_item.setForeground(QColor('#25251b'))
            name_item.setBackground(QColor('#aaec24'))
            self.process_table.setItem(row_position, 0, name_item)

            # Add CPU %
            cpu_item = QTableWidgetItem(f"{proc['cpu']:.1f}%")
            self.process_table.setItem(row_position, 1, cpu_item)

            # Add RAM %
            mem_item = QTableWidgetItem(f"{proc['mem']:.1f}%")
            self.process_table.setItem(row_position, 2, mem_item)

            # Add command path
            self.process_table.setItem(row_position, 3, QTableWidgetItem(proc['exe']))



    def on_search_enter(self):
        # If there are results, select the first one
        if self.process_table.rowCount() > 0:
            self.process_table.selectRow(0)
            self.process_table.setFocus()

    def table_key_press_event(self, event):
        # Handle key presses in the table
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Get selected row
            selected_row = self.process_table.currentRow()
            if selected_row >= 0 and selected_row < self.process_table.rowCount():
                # Get the process PID from the selected row
                # Note: We don't display PID in the table, so we need to find it
                # This would require storing the mapping between table rows and processes
                pass
        elif event.key() == Qt.Key.Key_Escape:
            # Return focus to search bar
            self.search_bar.setFocus()
        else:
            # Default behavior for other keys
            QTableWidget.keyPressEvent(self.process_table, event)





def main():
    app = QApplication(sys.argv)
    viewer = ProcessViewer()
    viewer.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
