import sys
import os
import psutil
import socket
import threading
import time
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, 
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
    if size_bytes == 0: return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    try:
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
    except: return "0 B"

class TreeItem(QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        # Custom numeric sorting for columns 2 and 3 (Speed and Total)
        if column in [2, 3]:
            try:
                val_self = float(self.data(column, Qt.ItemDataRole.UserRole) or 0)
                val_other = float(other.data(column, Qt.ItemDataRole.UserRole) or 0)
                return val_self < val_other
            except: pass
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
        self.win_w = QSpinBox(); self.win_w.setRange(400, 3840); self.win_w.setValue(current_settings.get('win_w', 900))
        self.win_h = QSpinBox(); self.win_h.setRange(300, 2160); self.win_h.setValue(current_settings.get('win_h', 700))
        win_form.addRow("WIDTH:", self.win_w)
        win_form.addRow("HEIGHT:", self.win_h)
        win_group.setLayout(win_form)
        layout.addWidget(win_group)
        
        # Table Group
        tbl_group = QGroupBox("TABLE CONFIG")
        tbl_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        tbl_form = QFormLayout()
        self.row_h = QSpinBox(); self.row_h.setRange(20, 100); self.row_h.setValue(current_settings.get('row_height', 40))
        tbl_form.addRow("ROW HEIGHT:", self.row_h)
        tbl_group.setLayout(tbl_form)
        layout.addWidget(tbl_group)
        
        # Columns Group
        col_group = QGroupBox("COLUMN WIDTHS")
        col_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        col_form = QFormLayout()
        widths = current_settings.get('col_widths', [60, 250, 150, 150])
        self.col_0 = QSpinBox(); self.col_0.setRange(30, 200); self.col_0.setValue(widths[0])
        self.col_1 = QSpinBox(); self.col_1.setRange(50, 1000); self.col_1.setValue(widths[1])
        self.col_2 = QSpinBox(); self.col_2.setRange(50, 1000); self.col_2.setValue(widths[2])
        self.col_3 = QSpinBox(); self.col_3.setRange(50, 1000); self.col_3.setValue(widths[3])
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
        if now - self.last_conn_refresh < 2: return
        new_map = {}
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and conn.pid:
                    new_map[(conn.laddr.ip, conn.laddr.port)] = conn.pid
        except: pass
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
                sport = None; dport = None
                if TCP in packet:
                    sport = packet[TCP].sport; dport = packet[TCP].dport
                elif UDP in packet:
                    sport = packet[UDP].sport; dport = packet[UDP].dport
                pid = self.stats.conn_map.get((src_ip, sport)) or self.stats.conn_map.get((dst_ip, dport))
                if pid: self.stats.update_packet(pid, len(packet))

        def refresher():
            while self.running:
                self.stats.refresh_connections()
                time.sleep(2)
        
        threading.Thread(target=refresher, daemon=True).start()
        try:
            sniff(prn=packet_callback, store=0, stop_filter=lambda x: not self.running)
        except: pass

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
        self.win_w = 900; self.win_h = 700; self.row_height = 40
        self.col_widths = [60, 250, 150, 150]
        self.current_sort_col = 2
        self.current_sort_order = Qt.SortOrder.DescendingOrder

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    self.win_w = s.get('win_w', 900)
                    self.win_h = s.get('win_h', 700)
                    self.row_height = s.get('row_height', 40)
                    self.col_widths = s.get('col_widths', [60, 250, 150, 150])
                    self.current_sort_col = s.get('sort_col', 2)
                    self.current_sort_order = Qt.SortOrder(s.get('sort_order', 1))
            except: pass

    def save_settings(self):
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            settings = {
                'win_w': self.width(),
                'win_h': self.height(),
                'row_height': self.row_height,
                'col_widths': [self.tree.columnWidth(i) for i in range(4)],
                'sort_col': self.current_sort_col,
                'sort_order': self.current_sort_order.value
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=4)
        except: pass

    def init_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QTreeWidget {{
                background-color: {CP_PANEL}; 
                border: 1px solid {CP_DIM}; 
                color: {CP_TEXT};
                outline: none;
                show-decoration-selected: 1;
            }}
            QTreeWidget::item {{ 
                border-bottom: 1px solid {CP_DIM}; 
                border-left: none;
                border-right: none;
                padding: 4px;
            }}
            QTreeWidget::item:selected {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                outline: none;
                border: none;
            }}
            QTreeWidget::item:focus {{
                outline: none;
                border: none;
            }}
            QHeaderView::section {{
                background-color: {CP_DIM}; 
                color: {CP_YELLOW}; 
                padding: 5px; 
                border: 1px solid {CP_BG}; 
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

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

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["ICON", "APPLICATION", "SPEED / SEC", "TOTAL USAGE"])
        self.tree.setIndentation(20)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.tree.setAllColumnsShowFocus(True)
        
        for i, width in enumerate(self.col_widths):
            self.tree.setColumnWidth(i, width)
        
        self.tree.setSortingEnabled(True)
        self.tree.header().sortIndicatorChanged.connect(self.on_sort_changed)
        self.tree.header().setSortIndicator(self.current_sort_col, self.current_sort_order)
        layout.addWidget(self.tree)
        
        footer = QLabel("STATUS: MONITORING_ACTIVE // PATH: " + SETTINGS_FILE)
        footer.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;")
        layout.addWidget(footer)

    def on_sort_changed(self, index, order):
        self.current_sort_col = index
        self.current_sort_order = order
        self.save_settings()

    def update_stats(self):
        snapshot = self.stats.get_snapshot()
        
        # Group by Application Name
        groups = {}
        for data in snapshot:
            name = data['name']
            if name not in groups:
                groups[name] = {'speed': 0, 'total': 0, 'exe': data['exe'], 'items': []}
            groups[name]['speed'] += data['speed']
            groups[name]['total'] += data['total']
            groups[name]['items'].append(data)

        self.tree.setSortingEnabled(False)
        
        # Keep track of existing groups to update instead of clearing
        existing_groups = {}
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            existing_groups[item.text(1)] = item
            
        # Update or Create Groups
        for name, gdata in groups.items():
            if name in existing_groups:
                root = existing_groups[name]
            else:
                root = TreeItem(self.tree)
                root.setText(1, name)
                # Load Icon
                exe_path = gdata['exe']
                if exe_path and os.path.exists(exe_path):
                    if exe_path not in self.icon_cache:
                        from PyQt6.QtCore import QFileInfo
                        icon = self.icon_provider.icon(QFileInfo(exe_path))
                        self.icon_cache[exe_path] = icon.pixmap(QSize(24, 24))
                    root.setIcon(0, QIcon(self.icon_cache[exe_path]))
            
            # Update Root Stats
            root.setText(2, format_size(gdata['speed']) + "/s")
            root.setData(2, Qt.ItemDataRole.UserRole, gdata['speed'])
            root.setText(3, format_size(gdata['total']))
            root.setData(3, Qt.ItemDataRole.UserRole, gdata['total'])
            
            # Apply Row Height
            root.setSizeHint(0, QSize(0, self.row_height))
            
            # Root Colors
            root.setForeground(2, QColor(CP_RED if gdata['speed'] > 1024*1024 else (CP_CYAN if gdata['speed'] > 1024*10 else CP_TEXT)))
            root.setForeground(3, QColor(CP_YELLOW))
            
            # Update Children (Individual Processes)
            if len(gdata['items']) > 1:
                # Sync children to avoid flickering
                existing_pids = {root.child(j).text(1): root.child(j) for j in range(root.childCount())}
                new_pids = set()
                
                for item_data in gdata['items']:
                    pid_text = f"PID: {item_data['pid']}"
                    new_pids.add(pid_text)
                    if pid_text in existing_pids:
                        child = existing_pids[pid_text]
                    else:
                        child = TreeItem(root)
                        child.setText(1, pid_text)
                    
                    child.setText(2, format_size(item_data['speed']) + "/s")
                    child.setData(2, Qt.ItemDataRole.UserRole, item_data['speed'])
                    child.setText(3, format_size(item_data['total']))
                    child.setData(3, Qt.ItemDataRole.UserRole, item_data['total'])
                    
                    child.setSizeHint(0, QSize(0, self.row_height))
                    child.setForeground(1, QColor(CP_SUBTEXT))
                    child.setForeground(2, QColor(CP_SUBTEXT))
                    child.setForeground(3, QColor(CP_SUBTEXT))
                
                # Remove children no longer present
                for pid_text, child in existing_pids.items():
                    if pid_text not in new_pids:
                        root.removeChild(child)
            else:
                # Clear children if only 1 process
                for j in reversed(range(root.childCount())):
                    root.removeChild(root.child(j))

        # Remove groups that no longer exist
        for i in reversed(range(self.tree.topLevelItemCount())):
            item = self.tree.topLevelItem(i)
            if item.text(1) not in groups:
                self.tree.takeTopLevelItem(i)

        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(self.current_sort_col, self.current_sort_order)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.save_settings()

    def restart_app(self):
        self.monitor_thread.running = False
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_settings(self):
        current = {
            'win_w': self.width(), 'win_h': self.height(),
            'row_height': self.row_height,
            'col_widths': [self.tree.columnWidth(i) for i in range(4)]
        }
        dlg = SettingsDialog(self, current)
        if dlg.exec():
            new_s = dlg.get_settings()
            self.row_height = new_s['row_height']
            self.resize(new_s['win_w'], new_s['win_h'])
            for i, width in enumerate(new_s['col_widths']):
                self.tree.setColumnWidth(i, width)
            self.save_settings()
            self.update_stats()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
