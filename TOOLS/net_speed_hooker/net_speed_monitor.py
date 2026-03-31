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
                             QScrollArea, QComboBox, QCheckBox)
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
        if col in [2, 3, 4, 5]:
            try: return float(self.data(col, Qt.ItemDataRole.UserRole) or 0) < float(other.data(col, Qt.ItemDataRole.UserRole) or 0)
            except: pass
        return super().__lt__(other)

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("SYSTEM_EXTENDED_SETTINGS"); self.resize(450, 650)
        self.setStyleSheet(f"QDialog {{ background-color: {CP_BG}; border: 1px solid {CP_CYAN}; }} QLabel {{ color: {CP_YELLOW}; font-family: 'Consolas'; font-weight: bold; }} QSpinBox, QComboBox {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; }} QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 10px; font-weight: bold; }} QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }} QScrollArea {{ border: none; background-color: transparent; }}")
        
        l = QVBoxLayout(self); s = QScrollArea(); s.setWidgetResizable(True); c = QWidget(); layout = QVBoxLayout(c)
        
        # Interface Group
        if_group = QGroupBox("NETWORK INTERFACE"); if_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        if_form = QFormLayout(); self.if_combo = QComboBox()
        self.if_list = [str(iface) for iface in get_if_list()]
        self.if_combo.addItems(self.if_list)
        current_if = str(current_settings.get('interface', conf.iface))
        if current_if in self.if_list: self.if_combo.setCurrentText(current_if)
        if_form.addRow("ADAPTER:", self.if_combo); if_group.setLayout(if_form); layout.addWidget(if_group)

        # Display Group
        disp_group = QGroupBox("DISPLAY SETTINGS"); disp_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        disp_form = QFormLayout(); self.unit_combo = QComboBox(); self.unit_combo.addItems(["MB/s (Bytes)", "Mbps (Bits)"])
        self.unit_combo.setCurrentIndex(0 if current_settings.get('unit', 'MB/s') == 'MB/s' else 1)
        disp_form.addRow("SPEED UNIT:", self.unit_combo); disp_group.setLayout(disp_form); layout.addWidget(disp_group)

        # Window & Table
        win_group = QGroupBox("WINDOW & TABLE"); win_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        win_form = QFormLayout(); self.win_w = QSpinBox(); self.win_w.setRange(400, 3840); self.win_w.setValue(current_settings.get('win_w', 1000))
        self.win_h = QSpinBox(); self.win_h.setRange(300, 2160); self.win_h.setValue(current_settings.get('win_h', 700))
        self.row_h = QSpinBox(); self.row_h.setRange(20, 100); self.row_h.setValue(current_settings.get('row_height', 40))
        win_form.addRow("WIDTH:", self.win_w); win_form.addRow("HEIGHT:", self.win_h); win_form.addRow("ROW HEIGHT:", self.row_h)
        win_group.setLayout(win_form); layout.addWidget(win_group)
        
        # Columns
        col_group = QGroupBox("COLUMN WIDTHS"); col_group.setStyleSheet(f"QGroupBox {{ color: {CP_CYAN}; border: 1px solid {CP_DIM}; margin-top: 10px; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; }}")
        col_form = QFormLayout(); ws = current_settings.get('col_widths', [60, 200, 120, 120, 120, 120])
        # Ensure ws has 6 elements
        while len(ws) < 6: ws.append(120)
        self.spins = []
        labels = ["ICON", "NAME", "DL SPEED", "UL SPEED", "TOTAL DL", "TOTAL UL"]
        for i in range(6):
            sb = QSpinBox(); sb.setRange(30, 1000); sb.setValue(ws[i])
            col_form.addRow(f"{labels[i]}:", sb); self.spins.append(sb)
        col_group.setLayout(col_form); layout.addWidget(col_group)
        
        s.setWidget(c); l.addWidget(s)
        self.save_btn = QPushButton("SAVE & RESTART MONITOR"); self.save_btn.clicked.connect(self.accept); l.addWidget(self.save_btn)

    def get_settings(self):
        return { 
            'unit': 'MB/s' if self.unit_combo.currentIndex() == 0 else 'Mbps', 
            'interface': self.if_combo.currentText(), 
            'win_w': self.win_w.value(), 'win_h': self.win_h.value(), 'row_height': self.row_h.value(), 
            'col_widths': [sb.value() for sb in self.spins] 
        }

class MonitorStats:
    def __init__(self):
        self.lock = threading.Lock(); self.proc_data = {}; self.conn_map = {}
        self.last_net_io = psutil.net_io_counters()
        self.local_ips = self.get_local_ips()

    def get_local_ips(self):
        ips = set()
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET: ips.add(addr.address)
        return ips

    def refresh_connections(self):
        new_map = {}
        try:
            for c in psutil.net_connections(kind='inet'):
                if c.laddr and c.pid: new_map[(c.laddr.ip, c.laddr.port)] = c.pid
        except: pass
        with self.lock: self.conn_map = new_map

    def update_packet(self, pid, size, direction):
        # direction: 'sent' or 'recv'
        with self.lock:
            if pid not in self.proc_data:
                try: p = psutil.Process(pid); name = p.name(); exe = p.exe()
                except: name = f"PID {pid}"; exe = ""
                self.proc_data[pid] = { 
                    'name': name, 'exe': exe, 
                    'sent_total': 0, 'recv_total': 0, 
                    'sent_curr': 0, 'recv_curr': 0 
                }
            if direction == 'sent':
                self.proc_data[pid]['sent_total'] += size
                self.proc_data[pid]['sent_curr'] += size
            else:
                self.proc_data[pid]['recv_total'] += size
                self.proc_data[pid]['recv_curr'] += size

    def get_snapshot(self):
        nio = psutil.net_io_counters()
        dl_delta = nio.bytes_recv - self.last_net_io.bytes_recv
        ul_delta = nio.bytes_sent - self.last_net_io.bytes_sent
        self.last_net_io = nio
        
        with self.lock:
            snap = []; sum_dl = 0; sum_ul = 0
            for pid, d in self.proc_data.items():
                dl = d['recv_curr']; ul = d['sent_curr']
                d['recv_curr'] = 0; d['sent_curr'] = 0
                sum_dl += dl; sum_ul += ul
                snap.append({ 
                    'pid': pid, 'name': d['name'], 'exe': d['exe'], 
                    'dl_speed': dl, 'ul_speed': ul, 
                    'dl_total': d['recv_total'], 'ul_total': d['sent_total'] 
                })
            
            missed_dl = max(0, dl_delta - sum_dl)
            missed_ul = max(0, ul_delta - sum_ul)
            if missed_dl > 1024 or missed_ul > 1024:
                snap.append({ 
                    'pid': 0, 'name': '[SYSTEM/OTHER/VPN]', 'exe': '', 
                    'dl_speed': missed_dl, 'ul_speed': missed_ul, 
                    'dl_total': missed_dl, 'ul_total': missed_ul 
                })
            return snap, dl_delta, ul_delta

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
                
                # Determine direction
                direction = 'recv' # default
                if ip_p.src in self.stats.local_ips:
                    direction = 'sent'
                
                pid = self.stats.conn_map.get((ip_p.src, sp)) or self.stats.conn_map.get((ip_p.dst, dp))
                if pid: self.stats.update_packet(pid, sz, direction)
        
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
        self.win_w = 1000; self.win_h = 700; self.row_height = 40
        self.col_widths = [60, 200, 120, 120, 120, 120]
        self.current_sort_col = 2; self.current_sort_order = Qt.SortOrder.DescendingOrder
        self.unit = "MB/s"; self.interface = conf.iface
        self.show_dl = True; self.show_ul = True

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    s = json.load(f)
                    self.win_w = s.get('win_w', 1000); self.win_h = s.get('win_h', 700)
                    self.row_height = s.get('row_height', 40)
                    self.col_widths = s.get('col_widths', [60, 200, 120, 120, 120, 120])
                    self.current_sort_col = s.get('sort_col', 2)
                    self.current_sort_order = Qt.SortOrder(s.get('sort_order', 1))
                    self.unit = s.get('unit', 'MB/s'); self.interface = s.get('interface', conf.iface)
                    self.show_dl = s.get('show_dl', True); self.show_ul = s.get('show_ul', True)
            except: pass

    def save_settings(self):
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            settings = { 
                'unit': self.unit, 'interface': self.interface, 
                'win_w': self.width(), 'win_h': self.height(), 'row_height': self.row_height, 
                'col_widths': [self.tree.columnWidth(i) for i in range(6)], 
                'sort_col': self.current_sort_col, 'sort_order': self.current_sort_order.value,
                'show_dl': self.show_dl, 'show_ul': self.show_ul
            }
            with open(SETTINGS_FILE, 'w') as f: json.dump(settings, f, indent=4)
        except: pass

    def init_ui(self):
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }} QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }} QTreeWidget {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_TEXT}; outline: none; show-decoration-selected: 1; }} QTreeWidget::item {{ border-bottom: 1px solid {CP_DIM}; padding: 4px; }} QTreeWidget::item:selected {{ background-color: {CP_DIM}; color: {CP_YELLOW}; outline: none; }} QHeaderView::section {{ background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 5px; border: 1px solid {CP_BG}; font-weight: bold; }} QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }} QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }} QCheckBox {{ color: {CP_CYAN}; font-weight: bold; }}")
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c); ht = QHBoxLayout()
        t = QLabel("SYSTEM NETWORK TRAFFIC"); t.setStyleSheet(f"color: {CP_CYAN}; font-size: 18pt; font-weight: bold;"); ht.addWidget(t)
        
        # Checkboxes
        self.cb_dl = QCheckBox("DOWNLOAD"); self.cb_dl.setChecked(self.show_dl); self.cb_dl.stateChanged.connect(self.toggle_cols)
        self.cb_ul = QCheckBox("UPLOAD"); self.cb_ul.setChecked(self.show_ul); self.cb_ul.stateChanged.connect(self.toggle_cols)
        ht.addStretch(); ht.addWidget(self.cb_dl); ht.addWidget(self.cb_ul)
        
        self.tl = QLabel("DL: 0.00 | UL: 0.00"); self.tl.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 10pt; border: 1px solid {CP_DIM}; padding: 5px;"); ht.addWidget(self.tl); l.addLayout(ht)
        
        hb = QHBoxLayout(); hb.addStretch(); rb = QPushButton("RESTART"); rb.clicked.connect(self.restart_app); hb.addWidget(rb); sb = QPushButton("SETTINGS"); sb.clicked.connect(self.show_settings); hb.addWidget(sb); l.addLayout(hb)
        
        self.tree = QTreeWidget(); self.tree.setColumnCount(6)
        self.tree.setHeaderLabels(["ICON", "APPLICATION", "DL SPEED", "UL SPEED", "TOTAL DL", "TOTAL UL"])
        self.tree.setIndentation(20); self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus); self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows); self.tree.setAllColumnsShowFocus(True)
        for i, w in enumerate(self.col_widths): self.tree.setColumnWidth(i, w)
        self.tree.setSortingEnabled(True); self.tree.header().sortIndicatorChanged.connect(self.on_sort_changed); self.tree.header().setSortIndicator(self.current_sort_col, self.current_sort_order); l.addWidget(self.tree)
        
        self.fl = QLabel(f"STATUS: MONITORING_ACTIVE // ADAPTER: {self.interface} // UNIT: {self.unit}"); self.fl.setStyleSheet(f"color: {CP_DIM}; font-size: 8pt;"); l.addWidget(self.fl)
        self.toggle_cols()

    def toggle_cols(self):
        self.show_dl = self.cb_dl.isChecked()
        self.show_ul = self.cb_ul.isChecked()
        self.tree.setColumnHidden(2, not self.show_dl)
        self.tree.setColumnHidden(4, not self.show_dl)
        self.tree.setColumnHidden(3, not self.show_ul)
        self.tree.setColumnHidden(5, not self.show_ul)
        self.save_settings()

    def on_sort_changed(self, i, o): self.current_sort_col = i; self.current_sort_order = o; self.save_settings()

    def update_stats(self):
        snap, dl_t, ul_t = self.stats.get_snapshot()
        self.tl.setText(f"DL: {format_size(dl_t, self.unit)} | UL: {format_size(ul_t, self.unit)}")
        
        groups = {}
        for d in snap:
            n = d['name']
            if n not in groups: groups[n] = {'dl_s': 0, 'ul_s': 0, 'dl_t': 0, 'ul_t': 0, 'exe': d['exe'], 'items': []}
            groups[n]['dl_s'] += d['dl_speed']; groups[n]['ul_s'] += d['ul_speed']
            groups[n]['dl_t'] += d['dl_total']; groups[n]['ul_t'] += d['ul_total']
            groups[n]['items'].append(d)
            
        self.tree.setSortingEnabled(False); exs = {self.tree.topLevelItem(i).text(1): self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())}
        for n, gd in groups.items():
            r = exs[n] if n in exs else TreeItem(self.tree); r.setText(1, n)
            if gd['exe'] and os.path.exists(gd['exe']) and gd['exe'] not in self.icon_cache:
                from PyQt6.QtCore import QFileInfo; icon = self.icon_provider.icon(QFileInfo(gd['exe'])); self.icon_cache[gd['exe']] = icon.pixmap(QSize(24, 24))
            if gd['exe'] in self.icon_cache: r.setIcon(0, QIcon(self.icon_cache[gd['exe']]))
            
            # DL/UL Speed
            r.setText(2, format_size(gd['dl_s'], self.unit)); r.setData(2, Qt.ItemDataRole.UserRole, gd['dl_s'])
            r.setText(3, format_size(gd['ul_s'], self.unit)); r.setData(3, Qt.ItemDataRole.UserRole, gd['ul_s'])
            # Totals
            r.setText(4, format_size(gd['dl_t'], "MB/s")); r.setData(4, Qt.ItemDataRole.UserRole, gd['dl_t'])
            r.setText(5, format_size(gd['ul_t'], "MB/s")); r.setData(5, Qt.ItemDataRole.UserRole, gd['ul_t'])
            
            r.setSizeHint(0, QSize(0, self.row_height))
            # Colors
            r.setForeground(2, QColor(CP_CYAN if gd['dl_s'] > 0 else CP_TEXT))
            r.setForeground(3, QColor(CP_ORANGE if gd['ul_s'] > 0 else CP_TEXT))
            r.setForeground(4, QColor(CP_YELLOW)); r.setForeground(5, QColor(CP_GREEN))
            
            if len(gd['items']) > 1:
                eps = {r.child(j).text(1): r.child(j) for j in range(r.childCount())}; nps = set()
                for id in gd['items']:
                    pt = f"PID: {id['pid']}"; nps.add(pt); c = eps[pt] if pt in eps else TreeItem(r); c.setText(1, pt)
                    c.setText(2, format_size(id['dl_speed'], self.unit)); c.setData(2, Qt.ItemDataRole.UserRole, id['dl_speed'])
                    c.setText(3, format_size(id['ul_speed'], self.unit)); c.setData(3, Qt.ItemDataRole.UserRole, id['ul_speed'])
                    c.setText(4, format_size(id['dl_total'], "MB/s")); c.setData(4, Qt.ItemDataRole.UserRole, id['dl_total'])
                    c.setText(5, format_size(id['ul_total'], "MB/s")); c.setData(5, Qt.ItemDataRole.UserRole, id['ul_total'])
                    c.setSizeHint(0, QSize(0, self.row_height))
                    for col in range(1, 6): c.setForeground(col, QColor(CP_SUBTEXT))
                for pt, c in eps.items():
                    if pt not in nps: r.removeChild(c)
            else:
                for j in reversed(range(r.childCount())): r.removeChild(r.child(j))
                
        for i in reversed(range(self.tree.topLevelItemCount())):
            if self.tree.topLevelItem(i).text(1) not in groups: self.tree.takeTopLevelItem(i)
        self.tree.setSortingEnabled(True); self.tree.sortByColumn(self.current_sort_col, self.current_sort_order)

    def restart_app(self): self.monitor.running = False; os.execl(sys.executable, sys.executable, *sys.argv)

    def show_settings(self):
        curr = { 'unit': self.unit, 'interface': self.interface, 'win_w': self.width(), 'win_h': self.height(), 'row_height': self.row_height, 'col_widths': [self.tree.columnWidth(i) for i in range(6)] }
        dlg = SettingsDialog(self, curr)
        if dlg.exec():
            ns = dlg.get_settings(); self.unit = ns['unit']; self.interface = ns['interface']; self.row_height = ns['row_height']; self.resize(ns['win_w'], ns['win_h'])
            self.col_widths = ns['col_widths']
            for i, w in enumerate(self.col_widths): self.tree.setColumnWidth(i, w)
            self.tree.setHeaderLabel(2, f"DL SPEED"); self.tree.setHeaderLabel(3, f"UL SPEED")
            self.save_settings(); self.restart_app()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = App(); window.show(); sys.exit(app.exec())
