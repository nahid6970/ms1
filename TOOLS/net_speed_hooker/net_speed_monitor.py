import sys
import os
import psutil
import socket
import threading
import time
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QGroupBox, QFrame, QDialog, QSpinBox, QFormLayout,
                             QScrollArea)
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

# Target settings path
SETTINGS_DIR = r"C:\@delta\output\net_speed_monitor"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    try:
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    except:
        return "0 B"

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if isinstance(other, QTableWidgetItem):
            my_data = self.data(Qt.ItemDataRole.UserRole)
            other_data = other.data(Qt.ItemDataRole.UserRole)
            if my_data is not None and other_data is not None:
                return my_data < other_data
        return super().__lt__(other)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("SYSTEM_EXTENDED_SETTINGS")
        self.resize(400, 500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }}
            QLabel {{ color: {CP_YELLOW}; font-family: 'Consolas'; font-weight: bold; }}
            QSpinBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QScrollArea {{ border: none; background-color: transparent; }}
        """)
        
        main_layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Window Group
        win_group = QGroupBox("WINDOW DIMENSIONS")
        win_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        win_form = QFormLayout()
        self.win_w = QSpinBox()
        self.win_w.setRange(400, 3840)
        self.win_w.setValue(current_settings.get('win_w', 900))
        self.win_h = QSpinBox()
        self.win_h.setRange(300, 2160)
        self.win_h.setValue(current_settings.get('win_h', 700))
        win_form.addRow("WIDTH:", self.win_w)
        win_form.addRow("HEIGHT:", self.win_h)
        win_group.setLayout(win_form)
        layout.addWidget(win_group)
        
        # Table Group
        tbl_group = QGroupBox("TABLE CONFIG")
        tbl_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        tbl_form = QFormLayout()
        self.row_h = QSpinBox()
        self.row_h.setRange(20, 100)
        self.row_h.setValue(current_settings.get('row_height', 40))
        tbl_form.addRow("ROW HEIGHT:", self.row_h)
        tbl_group.setLayout(tbl_form)
        layout.addWidget(tbl_group)
        
        # Columns Group
        col_group = QGroupBox("COLUMN WIDTHS")
        col_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        col_form = QFormLayout()
        self.col_0 = QSpinBox() # ICON
        self.col_0.setRange(30, 200)
        self.col_0.setValue(current_settings.get('col_widths', [50, 200, 150, 150])[0])
        self.col_1 = QSpinBox() # APPLICATION
        self.col_1.setRange(50, 1000)
        self.col_1.setValue(current_settings.get('col_widths', [50, 200, 150, 150])[1])
        self.col_2 = QSpinBox() # SPEED
        self.col_2.setRange(50, 1000)
        self.col_2.setValue(current_settings.get('col_widths', [50, 200, 150, 150])[2])
        self.col_3 = QSpinBox() # TOTAL
        self.col_3.setRange(50, 1000)
        self.col_3.setValue(current_settings.get('col_widths', [50, 200, 150, 150])[3])
        
        col_form.addRow("ICON COL:", self.col_0)
        col_form.addRow("APP NAME COL:", self.col_1)
        col_form.addRow("SPEED COL:", self.col_2)
        col_form.addRow("TOTAL COL:", self.col_3)
        col_group.setLayout(col_form)
        layout.addWidget(col_group)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
        self.save_btn = QPushButton("SAVE & APPLY")
        self.save_btn.clicked.connect(self.accept)
        main_layout.addWidget(self.save_btn)

    def get_settings(self):
        return {
            'win_w': self.win_w.value(),
            'win_h': self.win_h.value(),
            'row_height': self.row_h.value(),
            'col_widths': [self.col_0.value(), self.col_1.value(), self.col_2.value(), self.col_3.value()]
        }

class MonitorStats:
    def __init__(self):
        self.lock = threading.Lock()
        self.proc_data = {}
        self.conn_map = {}
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
        except:
            pass
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
                    'current_bytes': 0
                }
            self.proc_data[pid]['total_bytes'] += size
            self.proc_data[pid]['current_bytes'] += size

    def get_snapshot(self):
        with self.lock:
            snapshot = []
            for pid, data in self.proc_data.items():
                speed = data['current_bytes']
                data['current_bytes'] = 0
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
            if not self.running: return
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
                pid = self.stats.conn_map.get((src_ip, sport)) or self.stats.conn_map.get((dst_ip, dport))
                if pid: self.stats.update_packet(pid, len(packet))

        def refresher():
            while self.running:
                self.stats.refresh_connections()
                time.sleep(2)
        
        threading.Thread(target=refresher, daemon=True).start()
        try:
            sniff(prn=packet_callback, store=0, stop_filter=lambda x: not self.running)
        except:
            pass

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NET-SPEED HOOKER // CYBER_MONITOR")
        
        self.load_settings()
        self.resize(self.win_w, self.win_h)

        self.stats = MonitorStats()
        self.monitor_thread = NetworkThread(self.stats)
        self.monitor_thread.start()

        self.icon_cache = {}
        from PyQt6.QtWidgets import QFileIconProvider
        self.icon_provider = QFileIconProvider()

        self.init_ui()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def load_settings(self):
        # Default values
        self.win_w = 900
        self.win_h = 700
        self.row_height = 40
        self.col_widths = [50, 200, 150, 150]
        self.current_sort_col = 2
        self.current_sort_order = Qt.SortOrder.DescendingOrder

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    self.win_w = s.get('win_w', 900)
                    self.win_h = s.get('win_h', 700)
                    self.row_height = s.get('row_height', 40)
                    self.col_widths = s.get('col_widths', [50, 200, 150, 150])
                    self.current_sort_col = s.get('sort_col', 2)
                    self.current_sort_order = Qt.SortOrder(s.get('sort_order', 1))
            except:
                pass

    def save_settings(self):
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            settings = {
                'win_w': self.width(),
                'win_h': self.height(),
                'row_height': self.row_height,
                'col_widths': [self.table.columnWidth(i) for i in range(4)],
                'sort_col': self.current_sort_col,
                'sort_order': self.current_sort_order.value
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except:
            pass

    def init_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QTableWidget {{
                background-color: {CP_PANEL}; gridline-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: {CP_TEXT};
            }}
            QHeaderView::section {{
                background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 5px; border: 1px solid {CP_BG}; font-weight: bold;
            }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QHBoxLayout()
        title = QLabel("SYSTEM NETWORK TRAFFIC")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 18pt; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        
        self.restart_btn = QPushButton("RESTART")
        self.restart_btn.clicked.connect(self.restart_app)
        header.addWidget(self.restart_btn)
        
        self.settings_btn = QPushButton("SETTINGS")
        self.settings_btn.clicked.connect(self.show_settings)
        header.addWidget(self.settings_btn)
        layout.addLayout(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ICON", "APPLICATION", "SPEED / SEC", "TOTAL USAGE"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Apply Column Widths
        for i, width in enumerate(self.col_widths):
            self.table.setColumnWidth(i, width)
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self.on_sort_changed)
        self.table.horizontalHeader().setSortIndicator(self.current_sort_col, self.current_sort_order)
        layout.addWidget(self.table)
        
        footer = QLabel("STATUS: MONITORING_ACTIVE // PATH: " + SETTINGS_FILE)
        footer.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        layout.addWidget(footer)

    def on_sort_changed(self, index, order):
        self.current_sort_col = index
        self.current_sort_order = order
        self.save_settings()

    def update_stats(self):
        snapshot = self.stats.get_snapshot()
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(snapshot))
        for i, data in enumerate(snapshot):
            self.table.setRowHeight(i, self.row_height)
            
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
            
            name_item = QTableWidgetItem(data['name'])
            name_item.setData(Qt.ItemDataRole.UserRole, data['name'].lower())
            name_item.setForeground(QColor(CP_TEXT))
            self.table.setItem(i, 1, name_item)
            
            speed_str = format_size(data['speed']) + "/s"
            speed_item = NumericTableWidgetItem(speed_str)
            speed_item.setData(Qt.ItemDataRole.UserRole, data['speed'])
            speed_item.setForeground(QColor(CP_RED if data['speed'] > 1024*1024 else (CP_CYAN if data['speed'] > 1024*10 else CP_TEXT)))
            self.table.setItem(i, 2, speed_item)
            
            total_str = format_size(data['total'])
            total_item = NumericTableWidgetItem(total_str)
            total_item.setData(Qt.ItemDataRole.UserRole, data['total'])
            total_item.setForeground(QColor(CP_YELLOW))
            self.table.setItem(i, 3, total_item)
            
        self.table.setSortingEnabled(True)
        self.table.sortByColumn(self.current_sort_col, self.current_sort_order)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.save_settings()

    def restart_app(self):
        self.monitor_thread.running = False
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_settings(self):
        current = {
            'win_w': self.width(),
            'win_h': self.height(),
            'row_height': self.row_height,
            'col_widths': [self.table.columnWidth(i) for i in range(4)]
        }
        dlg = SettingsDialog(self, current)
        if dlg.exec():
            new_s = dlg.get_settings()
            self.row_height = new_s['row_height']
            self.resize(new_s['win_w'], new_s['win_h'])
            for i, width in enumerate(new_s['col_widths']):
                self.table.setColumnWidth(i, width)
            self.save_settings()
            self.update_stats()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
