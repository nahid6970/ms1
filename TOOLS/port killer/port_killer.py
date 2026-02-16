#!/usr/bin/env python3
import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QLabel,
                             QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt

# CYBERPUNK PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

class PortKillerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PORT KILLER")
        self.resize(900, 500)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; 
                padding: 6px; font-size: 11pt;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; 
                padding: 8px 16px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            
            QTableWidget {{
                background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM};
                gridline-color: {CP_DIM}; font-size: 10pt;
            }}
            QTableWidget::item:selected {{
                background-color: {CP_CYAN}; color: {CP_BG};
            }}
            QHeaderView::section {{
                background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 6px;
                border: 1px solid {CP_DIM}; font-weight: bold;
            }}
            
            QLabel {{ color: {CP_TEXT}; font-size: 10pt; }}
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("PORT KILLER")
        title.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {CP_YELLOW};")
        layout.addWidget(title)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Port:"))
        self.port_entry = QLineEdit()
        self.port_entry.setPlaceholderText("Enter port number...")
        self.port_entry.setMaximumWidth(150)
        self.port_entry.textChanged.connect(self.filter_ports)
        search_layout.addWidget(self.port_entry)
        
        self.all_ports = []
        
        btn_search = QPushButton("SEARCH")
        btn_search.clicked.connect(self.refresh)
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
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["PID", "PORT", "PROCESS", "DETAILS"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        # Kill button
        btn_kill = QPushButton("KILL SELECTED")
        btn_kill.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_RED}; border: 1px solid {CP_RED}; color: white;
                padding: 10px; font-weight: bold; font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #cc0030; border: 1px solid {CP_YELLOW};
            }}
        """)
        btn_kill.clicked.connect(self.kill_selected)
        btn_kill.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(btn_kill)
        
        # Load ports after GUI is shown
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self.list_all)
    
    def restart_app(self):
        QApplication.quit()
        subprocess.Popen([sys.executable] + sys.argv)
    
    
    def get_listening_ports(self, port=None):
        try:
            if port:
                cmd = f"netstat -ano | findstr :{port}"
            else:
                cmd = "netstat -ano | findstr LISTENING"
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip().split('\n') if result.stdout else []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to get ports: {e}")
            return []
    
    def parse_netstat_line(self, line):
        parts = line.split()
        if len(parts) >= 5:
            local_addr = parts[1]
            port = local_addr.split(':')[-1]
            pid = parts[-1]
            return port, pid
        return None, None
    
    def get_process_info(self, pid):
        try:
            cmd = f'tasklist /FI "PID eq {pid}" /FO CSV /NH'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout:
                parts = result.stdout.strip().split(',')
                if len(parts) >= 1:
                    return parts[0].strip('"')
        except:
            pass
        return "Unknown"
    
    def list_all(self):
        self.table.setRowCount(0)
        lines = self.get_listening_ports()
        
        self.all_ports = []
        seen = set()
        for line in lines:
            if not line.strip():
                continue
            port, pid = self.parse_netstat_line(line)
            if port and pid and (port, pid) not in seen:
                seen.add((port, pid))
                process = self.get_process_info(pid)
                self.all_ports.append((pid, port, process, line.strip()))
        
        self.display_ports(self.all_ports)
    
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
    
    def search_port(self):
        self.refresh()
    
    def refresh(self):
        self.port_entry.clear()
        self.list_all()
    
    def kill_selected(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a process to kill")
            return
        
        rows = set()
        for item in selected:
            rows.add(item.row())
        
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
