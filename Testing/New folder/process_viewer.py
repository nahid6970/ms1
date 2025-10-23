import sys
import psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTableWidget, QTableWidgetItem, QLabel, QHeaderView, QPushButton
)
from PyQt6.QtCore import QTimer, Qt


class ProcessViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.processes = []
        self.load_processes()
        # Update processes every 2 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_processes)
        self.timer.start(2000)

    def init_ui(self):
        self.setWindowTitle('Process Viewer')
        self.setGeometry(100, 100, 1000, 600)

        # Main layout
        layout = QVBoxLayout()

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('Search:'))
        self.search_bar = QLineEdit()
        self.search_bar.textChanged.connect(self.filter_processes)
        search_layout.addWidget(self.search_bar)

        # Add red round button to kill matching processes
        self.kill_button = QPushButton("●")
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
        self.process_table.setColumnCount(2)
        self.process_table.setHorizontalHeaderLabels(['Name', 'Command Path'])
        # Set specific resize modes for columns
        self.process_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Name column
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Command Path column
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.process_table)

        # Focus on search bar by default
        self.search_bar.setFocus()
        
        # Enable keyboard navigation
        self.search_bar.returnPressed.connect(self.on_search_enter)
        self.process_table.keyPressEvent = self.table_key_press_event

        self.setLayout(layout)

    def load_processes(self):
        # Store the current search text
        search_text = self.search_bar.text().lower()

        # Get all processes with their information
        self.processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
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
                    'exe': exe
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have terminated or we don't have access
                pass

        # Update the table with filtered processes if there's a search term,
        # otherwise show all processes
        if search_text:
            self.update_table_with_filter(search_text)
        else:
            self.update_table(self.processes)

    def filter_processes(self):
        search_text = self.search_bar.text().strip()
        if not search_text:
            # If search bar is empty, show all processes
            self.update_table(self.processes)
            return

        # Split search text into multiple words
        search_terms = search_text.lower().split()
        
        # Filter processes based on all search terms
        filtered_processes = []
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
                filtered_processes.append(proc)
        
        self.update_table(filtered_processes)

    def update_table_with_filter(self, search_text):
        search_text = search_text.strip()
        if not search_text:
            # If search bar is empty, show all processes
            self.update_table(self.processes)
            return
            
        # Split search text into multiple words
        search_terms = search_text.lower().split()
        
        # Filter processes based on all search terms
        filtered_processes = []
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
                filtered_processes.append(proc)
        
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

        # Get search terms for highlighting
        search_text = self.search_bar.text().strip()
        search_terms = search_text.lower().split() if search_text else []

        # Add processes to the table
        for proc in processes:
            row_position = self.process_table.rowCount()
            self.process_table.insertRow(row_position)

            # Add process name with highlighting
            name_item = QTableWidgetItem(proc['name'])
            if search_terms:
                # Simple highlighting by making the item bold if it matches
                name_lower = proc['name'].lower()
                for term in search_terms:
                    if term in name_lower:
                        font = name_item.font()
                        font.setBold(True)
                        name_item.setFont(font)
                        break
            self.process_table.setItem(row_position, 0, name_item)

            # Add command path with highlighting
            exe_item = QTableWidgetItem(proc['exe'])
            if search_terms:
                # Simple highlighting by making the item bold if it matches
                exe_lower = proc['exe'].lower()
                for term in search_terms:
                    if term in exe_lower:
                        font = exe_item.font()
                        font.setBold(True)
                        exe_item.setFont(font)
                        break
            self.process_table.setItem(row_position, 1, exe_item)

    def update_table(self, processes):
        # Clear the table
        self.process_table.setRowCount(0)

        # Add processes to the table
        for proc in processes:
            row_position = self.process_table.rowCount()
            self.process_table.insertRow(row_position)

            # Add process name
            self.process_table.setItem(row_position, 0, QTableWidgetItem(proc['name']))

            # Add command path
            self.process_table.setItem(row_position, 1, QTableWidgetItem(proc['exe']))

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
