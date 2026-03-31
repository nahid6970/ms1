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
                             QScrollArea, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont
from scapy.all import sniff, IP, TCP, UDP, conf, get_if_list

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"; CP_PANEL = "#111111"; CP_YELLOW = "#FCEE0A"; CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"; CP_GREEN = "#00ff21"; CP_ORANGE = "#ff934b"; CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"; CP_SUBTEXT = "#808080"

SETTINGS_DIR = r"C:\@delta\output\net_speed_monitor"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")

def format_size(size_bytes, unit="MB/s"):
    if size_bytes <= 0: return "0 B"
    val = size_bytes * 8 if "bps" in unit.lower() else size_bytes
    names = ("bps", "Kbps", "Mbps", "Gbps", "Tbps") if "bps" in unit.lower() else ("B", "KB", "MB", "GB", "TB")
    import math
    try:
        i = int(math.floor(math.log(val, 1024))) if val > 0 else 0
        if i >= len(names): i = len(names)-1
        return f"{round(val/math.pow(1024, i), 2)} {names[i]}"
    except: return f"0 {names[0]}"

class TreeItem(QTreeWidgetItem):
    def __lt__(self, other):
        col = self.treeWidget().sortColumn()
        if col in [2, 3]:
            try: return float(self.data(col, Qt.ItemDataRole.UserRole) or 0) < float(other.data(col, Qt.ItemDataRole.UserRole) or 0)
            except: pass
        return super().__lt__(other)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("SYSTEM_EXTENDED_SETTINGS"); self.resize(450, 600)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }} QLabel {{ color: {CP_YELLOW}; font-family: 'Consolas'; font-weight: bold; }} QSpinBox, QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; }} QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold; }} QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }} QScrollArea {{ border: none; background-color: transparent; }}")
        
        l = QVBoxLayout(self); s = QScrollArea(); s.setWidgetResizable(True); c = QWidget(); layout = QVBoxLayout(c)
        
        # Interface Group
        if_group = QGroupBox("NETWORK INTERFACE"); if_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        if_form = QFormLayout(); self.if_combo = QComboBox()
        self.if_list = get_if_list()
        self.if_combo.addItems(self.if_list)
        current_if = current_settings.get('interface', conf.iface)
        if current_if in self.if_list: self.if_combo.setCurrentText(current_if)
        if_form.addRow("ADAPTER:", self.if_combo); if_group.setLayout(if_form); layout.addWidget(if_group)

        # Display Group
        disp_group = QGroupBox("DISPLAY SETTINGS"); disp_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        disp_form = QFormLayout(); self.unit_combo = QComboBox(); self.unit_combo.addItems(["MB/s (Bytes)", "Mbps (Bits)"])
        self.unit_combo.setCurrentIndex(0 if current_settings.get('unit', 'MB/s') == 'MB/s' else 1)
        disp_form.addRow("SPEED UNIT:", self.unit_combo); disp_group.setLayout(disp_form); layout.addWidget(disp_group)

        # Window & Table
        win_group = QGroupBox("WINDOW & TABLE"); win_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        win_form = QFormLayout(); self.win_w = QSpinBox(); self.win_w.setRange(400, 3840); self.win_w.setValue(current_settings.get('win_w', 900))
        self.win_h = QSpinBox(); self.win_h.setRange(300, 2160); self.win_h.setValue(current_settings.get('win_h', 700))
        self.row_h = QSpinBox(); self.row_h.setRange(20, 100); self.row_h.setValue(current_settings.get('row_height', 40))
        win_form.addRow("WIDTH:", self.win_w); win_form.addRow("HEIGHT:", self.win_h); win_form.addRow("ROW HEIGHT:", self.row_h)
        win_group.setLayout(win_form); layout.addWidget(win_group)
        
        # Columns
        col_group = QGroupBox("COLUMN WIDTHS"); col_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        col_form = QFormLayout(); ws = current_settings.get('col_widths', [60, 250, 150, 150])
        self.c0 = QSpinBox(); self.c0.setRange(30, 200); self.c0.setValue(ws[0])
        self.c1 = QSpinBox(); self.c1.setRange(50, 1000); self.c1.setValue(ws[1])
        self.c2 = QSpinBox(); self.c2.setRange(50, 1000); self.c2.setValue(ws[2])
        self.c3 = QSpinBox(); self.c3.setRange(50, 1000); self.c3.setValue(ws[3])
        col_form.addRow("ICON:", self.c0); col_form.addRow("NAME:", self.c1); col_form.addRow("SPEED:", self.c2); col_form.addRow("TOTAL:", self.c3)
        col_group.setLayout(col_form); layout.addWidget(col_group)
        
        s.setWidget(c); l.addWidget(s)
        self.save_btn = QPushButton("SAVE & RESTART MONITOR"); self.save_btn.clicked.connect(self.accept); l.addWidget(self.save_btn)

    def get_settings(self):
        return { 'unit': 'MB/s' if self.unit_combo.currentIndex() == 0 else 'Mbps', 'interface': self.if_combo.currentText(), 'win_w': self.win_w.value(), 'win_h': self.win_h.value(), 'row_height': self.row_h.value(), 'col_widths': [self.c0.value(), self.c1.value(), self.c2.value(), self.c3.value()] }

class MonitorStats:
    def __init__(self):
        self.lock = threading.Lock(); self.proc_data = {}; self.conn_map = {}; self.last_net_io = psutil.net_io_counters()

    def refresh_connections(self):
        new_map = {}
        try:
            for c in psutil.net_connections(kind='inet'):
                if c.laddr and c.pid: new_map[(c.laddr.ip, c.laddr.port)] = c.pid
        except: pass
        with self.lock: self.conn_map = new_map

    def update_packet(self, pid, size):
        with self.lock:
            if pid not in self.proc_data:
                try: p = psutil.Process(pid); name = p.name(); exe = p.exe()
                except: name = f"PID {pid}"; exe = ""
                self.proc_data[pid] = { 'name': name, 'exe': exe, 'total_bytes': 0, 'current_bytes': 0 }
            self.proc_data[pid]['total_bytes'] += size; self.proc_data[pid]['current_bytes'] += size

    def get_snapshot(self):
        nio = psutil.net_io_counters(); delta = (nio.bytes_sent + nio.bytes_recv) - (self.last_net_io.bytes_sent + self.last_net_io.bytes_recv); self.last_net_io = nio
        with self.lock:
            snap = []; sum_p = 0
            for pid, d in self.proc_data.items():
                s = d['current_bytes']; d['current_bytes'] = 0; sum_p += s
                snap.append({ 'pid': pid, 'name': d['name'], 'exe': d['exe'], 'speed': s, 'total': d['total_bytes'] })
            missed = max(0, delta - sum_p)
            if missed > 1024: snap.append({ 'pid': 0, 'name': '[SYSTEM/OTHER/VPN]', 'exe': '', 'speed': missed, 'total': missed })
            return snap, delta

class NetworkThread(threading.Thread):
    def __init__(self, stats, interface):
        super().__init__(); self.stats = stats; self.interface = interface; self.daemon = True; self.running = True

    def run(self):
        def cb(p):
            if not self.running: return
            if IP in p:
                sz = len(p); ip_p = p[IP]
                sp = p[TCP].sport if TCP in p else (p[UDP].sport if UDP in p else 0)
                dp = p[TCP].dport if TCP in p else (p[UDP].dport if UDP in p else 0)
                pid = self.stats.conn_map.get((ip_p.src, sp)) or self.stats.conn_map.get((ip_p.dst, dp))
                if pid: self.stats.update_packet(pid, sz)
        def rf():
            while self.running: self.stats.refresh_connections(); time.sleep(1)
        threading.Thread(target=rf, daemon=True).start()
        try: sniff(iface=self.interface, filter="ip", prn=cb, store=0, stop_filter=lambda x: not self.running)
        except: pass

class App(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NET-SPEED HOOKER // CYBER_MONITOR")
        self.load_settings(); self.resize(self.win_w, self.win_h)
        self.stats = MonitorStats(); self.monitor = NetworkThread(self.stats, self.interface); self.monitor.start()
        self.icon_cache = {}; from PyQt6.QtWidgets import QFileIconProvider; self.icon_provider = QFileIconProvider()
        self.init_ui(); self.timer = QTimer(); self.timer.timeout.connect(self.update_stats); self.timer.start(1000)

    def load_settings(self):
        self.win_w = 900; self.win_h = 700; self.row_height = 40; self.col_widths = [60, 250, 150, 150]; self.current_sort_col = 2; self.current_sort_order = Qt.SortOrder.DescendingOrder; self.unit = "MB/s"; self.interface = conf.iface
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f); self.win_w = s.get('win_w', 900); self.win_h = s.get('win_h', 700); self.row_height = s.get('row_height', 40); self.col_widths = s.get('col_widths', [60, 250, 150, 150]); self.current_sort_col = s.get('sort_col', 2); self.current_sort_order = Qt.SortOrder(s.get('sort_order', 1)); self.unit = s.get('unit', 'MB/s'); self.interface = s.get('interface', conf.iface)
            except: pass

    def save_settings(self):
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            settings = { 'unit': self.unit, 'interface': self.interface, 'win_w': self.width(), 'win_h': self.height(), 'row_height': self.row_height, 'col_widths': [self.tree.columnWidth(i) for i in range(4)], 'sort_col': self.current_sort_col, 'sort_order': self.current_sort_order.value }
            with open(SETTINGS_FILE, 'w') as f: json.dump(settings, f, indent=4)
        except: pass

    def init_ui(self):
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }} QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }} QTreeWidget {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; outline: none; show-decoration-selected: 1; }} QTreeWidget::item {{ border-bottom: 1px solid {CP_DIM}; padding: 4px; }} QTreeWidget::item:selected {{ background-color: {CP_DIM}; color: {CP_YELLOW}; outline: none; }} QHeaderView::section {{ background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 5px; border: 1px solid {CP_BG}; font-weight: bold; }} QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }} QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}")
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c); ht = QHBoxLayout()
        t = QLabel("SYSTEM NETWORK TRAFFIC"); t.setStyleSheet(f"color: {CP_CYAN}; font-size: 18pt; font-weight: bold;"); ht.addWidget(t); ht.addStretch()
        self.tl = QLabel("TOTAL: 0.00 MB/s"); self.tl.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 12pt; border: 1px solid {CP_DIM}; padding: 5px;"); ht.addWidget(self.tl); l.addLayout(ht)
        hb = QHBoxLayout(); hb.addStretch(); rb = QPushButton("RESTART"); rb.clicked.connect(self.restart_app); hb.addWidget(rb); sb = QPushButton("SETTINGS"); sb.clicked.connect(self.show_settings); hb.addWidget(sb); l.addLayout(hb)
        self.tree = QTreeWidget(); self.tree.setColumnCount(4); self.tree.setHeaderLabels(["ICON", "APPLICATION", f"SPEED ({self.unit})", "TOTAL USAGE"]); self.tree.setIndentation(20); self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus); self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows); self.tree.setAllColumnsShowFocus(True)
        for i, w in enumerate(self.col_widths): self.tree.setColumnWidth(i, w)
        self.tree.setSortingEnabled(True); self.tree.header().sortIndicatorChanged.connect(self.on_sort_changed); self.tree.header().setSortIndicator(self.current_sort_col, self.current_sort_order); l.addWidget(self.tree)
        self.fl = QLabel(f"STATUS: MONITORING_ACTIVE // ADAPTER: {self.interface} // UNIT: {self.unit}"); self.fl.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;"); l.addWidget(self.fl)

    def on_sort_changed(self, i, o): self.current_sort_col = i; self.current_sort_order = o; self.save_settings()

    def update_stats(self):
        snap, total = self.stats.get_snapshot(); self.tl.setText(f"TOTAL: {format_size(total, self.unit)}")
        groups = {}
        for d in snap:
            n = d['name']
            if n not in groups: groups[n] = {'speed': 0, 'total': 0, 'exe': d['exe'], 'items': []}
            groups[n]['speed'] += d['speed']; groups[n]['total'] += d['total']; groups[n]['items'].append(d)
        self.tree.setSortingEnabled(False); exs = {self.tree.topLevelItem(i).text(1): self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())}
        for n, gd in groups.items():
            r = exs[n] if n in exs else TreeItem(self.tree); r.setText(1, n)
            if gd['exe'] and os.path.exists(gd['exe']) and gd['exe'] not in self.icon_cache:
                from PyQt6.QtCore import QFileInfo; icon = self.icon_provider.icon(QFileInfo(gd['exe'])); self.icon_cache[gd['exe']] = icon.pixmap(QSize(24, 24))
            if gd['exe'] in self.icon_cache: r.setIcon(0, QIcon(self.icon_cache[gd['exe']]))
            r.setText(2, format_size(gd['speed'], self.unit)); r.setData(2, Qt.ItemDataRole.UserRole, gd['speed'])
            r.setText(3, format_size(gd['total'], "MB/s")); r.setData(3, Qt.ItemDataRole.UserRole, gd['total']); r.setSizeHint(0, QSize(0, self.row_height))
            r.setForeground(2, QColor(CP_RED if gd['speed'] > 1024*1024 else (CP_CYAN if gd['speed'] > 1024*10 else CP_TEXT))); r.setForeground(3, QColor(CP_YELLOW))
            if len(gd['items']) > 1:
                eps = {r.child(j).text(1): r.child(j) for j in range(r.childCount())}; nps = set()
                for id in gd['items']:
                    pt = f"PID: {id['pid']}"; nps.add(pt); c = eps[pt] if pt in eps else TreeItem(r); c.setText(1, pt); c.setText(2, format_size(id['speed'], self.unit)); c.setData(2, Qt.ItemDataRole.UserRole, id['speed']); c.setText(3, format_size(id['total'], "MB/s")); c.setData(3, Qt.ItemDataRole.UserRole, id['total']); c.setSizeHint(0, QSize(0, self.row_height))
                    for col in range(1, 4): c.setForeground(col, QColor(CP_SUBTEXT))
                for pt, c in eps.items():
                    if pt not in nps: r.removeChild(c)
            else:
                for j in reversed(range(r.childCount())): r.removeChild(r.child(j))
        for i in reversed(range(self.tree.topLevelItemCount())):
            if self.tree.topLevelItem(i).text(1) not in groups: self.tree.takeTopLevelItem(i)
        self.tree.setSortingEnabled(True); self.tree.sortByColumn(self.current_sort_col, self.current_sort_order)

    def restart_app(self): self.monitor.running = False; os.execl(sys.executable, sys.executable, *sys.argv)

    def show_settings(self):
        curr = { 'unit': self.unit, 'interface': self.interface, 'win_w': self.width(), 'win_h': self.height(), 'row_height': self.row_height, 'col_widths': [self.tree.columnWidth(i) for i in range(4)] }
        dlg = SettingsDialog(self, curr)
        if dlg.exec():
            ns = dlg.get_settings(); self.unit = ns['unit']; self.interface = ns['interface']; self.row_height = ns['row_height']; self.resize(ns['win_w'], ns['win_h'])
            for i, w in enumerate(ns['col_widths']): self.tree.setColumnWidth(i, w)
            self.tree.setHeaderLabel(2, f"SPEED ({self.unit})"); self.save_settings(); self.restart_app()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = App(); window.show(); sys.exit(app.exec())
