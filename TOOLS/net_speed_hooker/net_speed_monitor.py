import sys
import os
import psutil
import socket
import threading
import time
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QGroupBox, QFrame)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont
from scapy.all import sniff, IP, TCP, UDP

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

class MonitorStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.proc_data = {} # pid -> {name, total_bytes, current_bytes, last_updated}
        self.conn_map = {} # (ip, port) -> pid
        self.last_conn_refresh = 0

    def refresh_connections(self):
        now = time.time()
        if now - self.last_conn_refresh < 2:
            return
        
        new_map = {}
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and conn.pid:
                    new_map[(conn.laddr.ip, conn.laddr.port)] = conn.pid
        except Exception as e:
            print(f"Error refreshing connections: {e}")
            
        with self.lock:
            self.conn_map = new_map
            self.last_conn_refresh = now

    def update_packet(self, pid, size):
        with self.lock:
            if pid not in self.proc_data:
                try:
                    proc = psutil.Process(pid)
                    name = proc.name()
                    exe = proc.exe()
                except:
                    name = f"PID {pid}"
                    exe = ""
                self.proc_data[pid] = {
                    'name': name,
                    'exe': exe,
                    'total_bytes': 0,
                    'current_bytes': 0,
                    'last_sec_bytes': 0
                }
            
            self.proc_data[pid]['total_bytes'] += size
            self.proc_data[pid]['current_bytes'] += size

    def get_snapshot(self):
        with self.lock:
            snapshot = []
            for pid, data in self.proc_data.items():
                speed = data['current_bytes']
                data['last_sec_bytes'] = speed
                data['current_bytes'] = 0 # reset for next second
                snapshot.append({
                    'pid': pid,
                    'name': data['name'],
                    'exe': data['exe'],
                    'speed': speed,
                    'total': data['total_bytes']
                })
            return snapshot

class NetworkThread(threading.Thread):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats
        self.daemon = True
        self.running = True

    def run(self):
        def packet_callback(packet):
            if not self.running:
                return
            
            if IP in packet:
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                
                sport = None
                dport = None
                if TCP in packet:
                    sport = packet[TCP].sport
                    dport = packet[TCP].dport
                elif UDP in packet:
                    sport = packet[UDP].sport
                    dport = packet[UDP].dport
                
                # Check mapping
                pid = self.stats.conn_map.get((src_ip, sport)) or self.stats.conn_map.get((dst_ip, dport))
                
                if pid:
                    self.stats.update_packet(pid, len(packet))
                else:
                    # Maybe it's a new connection, trigger refresh soon if many misses
                    pass

        # Periodically refresh connections in another small thread or just here
        def refresher():
            while self.running:
                self.stats.refresh_connections()
                time.sleep(2)
        
        refresh_t = threading.Thread(target=refresher, daemon=True)
        refresh_t.start()

        sniff(prn=packet_callback, store=0, stop_filter=lambda x: not self.running)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NET-SPEED HOOKER // CYBER_MONITOR")
        self.resize(900, 700)
        
        self.stats = MonitorStats()
        self.monitor_thread = NetworkThread(self.stats)
        self.monitor_thread.start()

        self.icon_cache = {} # exe_path -> QPixmap
        from PyQt6.QtWidgets import QFileIconProvider
        self.icon_provider = QFileIconProvider()

        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def init_ui(self):
        # Global Theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QTableWidget {{
                background-color: {CP_PANEL};
                gridline-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
            }}
            QHeaderView::section {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                padding: 5px;
                border: 1px solid {CP_BG};
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
                border: 1px solid {CP_YELLOW};
                color: {CP_YELLOW};
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {CP_YELLOW};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("SYSTEM NETWORK TRAFFIC")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.restart_btn = QPushButton("RESTART")
        self.restart_btn.clicked.connect(self.restart_app)
        header_layout.addWidget(self.restart_btn)
        
        self.settings_btn = QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(self.settings_btn)
        
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ICON", "APPLICATION", "SPEED / SEC", "TOTAL USAGE"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        
        layout.addWidget(self.table)
        
        # Footer
        footer = QLabel("STATUS: MONITORING_ACTIVE // ENCRYPTION_NONE")
        footer.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        layout.addWidget(footer)

    def update_stats(self):
        snapshot = self.stats.get_snapshot()
        
        # Sort by speed descending
        snapshot.sort(key=lambda x: x['speed'], reverse=True)
        
        # Filter: only show if they have used internet (glasswire style)
        # or just show everything that has ever been caught.
        
        # Update table
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(snapshot))
        
        for i, data in enumerate(snapshot):
            # Icon
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            exe_path = data['exe']
            if exe_path and os.path.exists(exe_path):
                if exe_path not in self.icon_cache:
                    from PyQt6.QtCore import QFileInfo
                    icon = self.icon_provider.icon(QFileInfo(exe_path))
                    pixmap = icon.pixmap(QSize(24, 24))
                    self.icon_cache[exe_path] = pixmap
                icon_label.setPixmap(self.icon_cache[exe_path])
            self.table.setCellWidget(i, 0, icon_label)
            
            # Name
            name_item = QTableWidgetItem(data['name'])
            name_item.setForeground(QColor(CP_TEXT))
            self.table.setItem(i, 1, name_item)
            
            # Speed
            speed_str = format_size(data['speed']) + "/s"
            speed_item = QTableWidgetItem()
            speed_item.setData(Qt.ItemDataRole.DisplayRole, speed_str)
            # Custom sorting data
            speed_item.setData(Qt.ItemDataRole.UserRole, data['speed'])
            if data['speed'] > 1024 * 1024: # > 1MB/s
                speed_item.setForeground(QColor(CP_RED))
            elif data['speed'] > 1024 * 10: # > 10KB/s
                speed_item.setForeground(QColor(CP_CYAN))
            else:
                speed_item.setForeground(QColor(CP_TEXT))
            self.table.setItem(i, 2, speed_item)
            
            # Total
            total_str = format_size(data['total'])
            total_item = QTableWidgetItem()
            total_item.setData(Qt.ItemDataRole.DisplayRole, total_str)
            total_item.setData(Qt.ItemDataRole.UserRole, data['total'])
            total_item.setForeground(QColor(CP_YELLOW))
            self.table.setItem(i, 3, total_item)
            
        self.table.setSortingEnabled(True)

    def restart_app(self):
        self.monitor_thread.running = False
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_settings(self):
        # Empty settings panel as requested
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "SETTINGS", "Settings panel is currently empty.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
