#!/usr/bin/env python3
import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

# SLIGHTER, SIMPLER FLAT DARK THEME
BG_COLOR = "#1e1e1e"
PANEL_COLOR = "#252526"
BORDER_COLOR = "#3c3c3c"
ACCENT_COLOR = "#007acc"
TEXT_COLOR = "#d4d4d4"
TEXT_MUTED = "#858585"
RED_COLOR = "#f44336"

class PortWorker(QThread):
    result_ready = pyqtSignal(list)

    def __init__(self, port_filter=None):
        super().__init__()
        self.port_filter = port_filter

    def run(self):
        pid_map = {}
        # 1. Run tasklist once to fetch all running processes
        try:
            cmd = 'tasklist /FO CSV /NH'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='replace')
            for line in res.stdout.strip().split('\n'):
                if not line.strip():
                    continue
                parts = [p.strip('"') for p in line.split(',')]
                if len(parts) >= 2:
                    name = parts[0]
                    pid = parts[1]
                    pid_map[pid] = name
        except Exception:
            pass

        # 2. Get active listening ports
        try:
            if self.port_filter:
                cmd = f"netstat -ano | findstr :{self.port_filter}"
            else:
                cmd = "netstat -ano | findstr LISTENING"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, errors='replace')
            lines = result.stdout.strip().split('\n') if result.stdout else []
        except Exception:
            lines = []

        # 3. Match netstat info with process names
        results = []
        seen = set()
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 5:
                local_addr = parts[1]
                port = local_addr.split(':')[-1]
                pid = parts[-1]
                
                if self.port_filter and self.port_filter not in port:
                    continue

                if (port, pid) not in seen:
                    seen.add((port, pid))
                    process_name = pid_map.get(pid, "Unknown")
                    results.append((pid, port, process_name, line.strip()))
                    
        self.result_ready.emit(results)


class PortKillerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PORT KILLER")
        self.resize(850, 480)
        self.worker = None
        self.all_ports = []
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {BG_COLOR}; }}
            QWidget {{ color: {TEXT_COLOR}; font-family: 'Segoe UI', 'Consolas', sans-serif; font-size: 10pt; }}
            
            QLineEdit {{
                background-color: {PANEL_COLOR}; color: white; border: 1px solid {BORDER_COLOR}; 
                padding: 5px; border-radius: 3px;
            }}
            QLineEdit:focus {{ border: 1px solid {ACCENT_COLOR}; }}
            
            QPushButton {{
                background-color: {PANEL_COLOR}; border: 1px solid {BORDER_COLOR}; color: {TEXT_COLOR}; 
                padding: 6px 12px; border-radius: 3px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {BORDER_COLOR}; border: 1px solid {ACCENT_COLOR}; color: white;
            }}
            QPushButton:pressed {{
                background-color: {ACCENT_COLOR}; color: white;
            }}
            
            QTableWidget {{
                background-color: {PANEL_COLOR}; color: {TEXT_COLOR}; border: 1px solid {BORDER_COLOR};
                gridline-color: {BORDER_COLOR}; font-size: 9.5pt;
            }}
            QTableWidget::item:selected {{
                background-color: {ACCENT_COLOR}; color: white;
            }}
            QHeaderView::section {{
                background-color: {PANEL_COLOR}; color: white; padding: 5px;
                border: 1px solid {BORDER_COLOR}; font-weight: bold;
            }}
            
            QLabel {{ color: {TEXT_COLOR}; }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title Header
        title = QLabel("PORT KILLER")
        title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {ACCENT_COLOR};")
        layout.addWidget(title)
        
        # Search & controls bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Port filter:"))
        
        self.port_entry = QLineEdit()
        self.port_entry.setPlaceholderText("Filter...")
        self.port_entry.setMaximumWidth(120)
        self.port_entry.textChanged.connect(self.filter_ports)
        search_layout.addWidget(self.port_entry)
        
        btn_search = QPushButton("SEARCH")
        btn_search.clicked.connect(self.filter_ports)
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(btn_search)
        
        btn_list = QPushButton("LIST ALL")
        btn_list.clicked.connect(self.list_all)
        btn_list.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(btn_list)
        
        btn_refresh = QPushButton("REFRESH")
        btn_refresh.clicked.connect(self.refresh)
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(btn_refresh)
        
        btn_restart = QPushButton("RESTART")
        btn_restart.clicked.connect(self.restart_app)
        btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        search_layout.addWidget(btn_restart)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table UI
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "PORT", "PROCESS", "DETAILS"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Action Button
        btn_kill = QPushButton("KILL SELECTED")
        btn_kill.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED_COLOR}; border: 1px solid {RED_COLOR}; color: white;
                padding: 8px; font-weight: bold; font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #d32f2f; border: 1px solid #d32f2f;
            }}
        """)
        btn_kill.clicked.connect(self.kill_selected)
        btn_kill.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn_kill)
        
        # Status Label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt;")
        layout.addWidget(self.status_label)
        
        # Load ports asynchronously
        QTimer.singleShot(50, self.list_all)
    
    def restart_app(self):
        QApplication.quit()
        subprocess.Popen([sys.executable] + sys.argv)
    
    def list_all(self):
        self.status_label.setText("Scanning active connections...")
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
        self.table.setRowCount(0)
        self.worker = PortWorker()
        self.worker.result_ready.connect(self.on_ports_loaded)
        self.worker.start()
        
    def on_ports_loaded(self, ports):
        self.all_ports = ports
        self.display_ports(ports)
        self.status_label.setText(f"Scan complete. Found {len(ports)} ports.")
    
    def display_ports(self, ports):
        self.table.setRowCount(0)
        for pid, port, process, details in ports:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(pid))
            self.table.setItem(row, 1, QTableWidgetItem(port))
            self.table.setItem(row, 2, QTableWidgetItem(process))
            self.table.setItem(row, 3, QTableWidgetItem(details))
    
    def filter_ports(self):
        search_text = self.port_entry.text().strip()
        if not search_text:
            self.display_ports(self.all_ports)
            return
        
        filtered = [p for p in self.all_ports if search_text in p[1]]
        self.display_ports(filtered)
    
    def refresh(self):
        self.port_entry.clear()
        self.list_all()
    
    def kill_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a process to kill")
            return
        
        rows = {item.row() for item in selected}
        
        for row in rows:
            pid = self.table.item(row, 0).text()
            port = self.table.item(row, 1).text()
            
            reply = QMessageBox.question(self, "Confirm", 
                                        f"Kill process {pid} on port {port}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True)
                    QMessageBox.information(self, "Success", f"Process {pid} killed")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to kill process: {e}")
        
        self.refresh()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortKillerApp()
    window.show()
    sys.exit(app.exec())
