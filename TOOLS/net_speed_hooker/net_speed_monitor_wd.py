import sys, os, psutil, socket, threading, time, json, sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView,
                             QGroupBox, QDialog, QSpinBox, QFormLayout, QScrollArea, QComboBox, QLineEdit,
                             QCheckBox, QStyledItemDelegate, QColorDialog, QSizePolicy, QFileIconProvider,
                             QSystemTrayIcon, QMenu, QCalendarWidget)
from PyQt6.QtCore import Qt, QTimer, QSize, QRectF, QFileInfo
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont, QPainter, QPen, QAction
import pydivert

CP_BG="#050505"; CP_PANEL="#111111"; CP_YELLOW="#FCEE0A"; CP_CYAN="#00F0FF"
CP_RED="#FF003C"; CP_GREEN="#00ff21"; CP_ORANGE="#ff934b"; CP_DIM="#3a3a3a"
CP_TEXT="#E0E0E0"; CP_SUBTEXT="#808080"

SETTINGS_DIR = r"C:\@delta\output\net_speed_monitor"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")
DB_FILE = os.path.join(SETTINGS_DIR, "traffic.db")
BLOCKED_FILE = os.path.join(SETTINGS_DIR, "blocked.json")
ICON_FILE = os.path.join(SETTINGS_DIR, "icon.svg")

import ipaddress

# Private/LAN IP ranges (RFC 1918, link-local, CGNAT)
_LAN_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('169.254.0.0/16'),   # link-local
    ipaddress.ip_network('100.64.0.0/10'),    # CGNAT
]

def is_private_ip(ip_str):
    """Return True if the IP is a private/LAN address."""
    try:
        addr = ipaddress.ip_address(ip_str)
        return any(addr in net for net in _LAN_NETWORKS)
    except: return False

def create_default_icon():
    if not os.path.exists(ICON_FILE):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        svg = """<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect width="32" height="32" fill="#050505" rx="4"/>
          <path d="M16 4L6 14h6v14h8V14h6L16 4z" fill="#00F0FF"/>
        </svg>"""
        with open(ICON_FILE, "w") as f: f.write(svg)

def load_blocked_json():
    try:
        if os.path.exists(BLOCKED_FILE):
            with open(BLOCKED_FILE) as f: return json.load(f)  # {name: exe}
    except: pass
    return {}

def save_blocked_json(name_exe_map):
    os.makedirs(SETTINGS_DIR, exist_ok=True)
    with open(BLOCKED_FILE, 'w') as f: json.dump(name_exe_map, f)

def format_size(b, unit="MB/s"):
    if b <= 0: return "0 B"
    import math
    val = b * 8 if "bps" in unit.lower() else b
    names = ("bps","Kbps","Mbps","Gbps") if "bps" in unit.lower() else ("B","KB","MB","GB")
    try:
        i = min(int(math.floor(math.log(val, 1024))), len(names)-1) if val > 0 else 0
        return f"{round(val/math.pow(1024,i),2)} {names[i]}"
    except: return f"0 {names[0]}"


class CustomBorderDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.max_values = {2:0, 3:0, 4:0, 5:0}
        self.settings = {'enabled':True, 'cols':{2:True,3:True,4:True,5:True}, 'color':CP_CYAN, 'thickness':2}

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        col = index.column()
        if not self.settings['enabled'] or not self.settings['cols'].get(col, False): return
        if col in self.max_values:
            val = index.data(Qt.ItemDataRole.UserRole)
            if val and val > 0 and val == self.max_values[col]:
                painter.save()
                pen = QPen(QColor(self.settings['color']), self.settings['thickness'])
                painter.setPen(pen)
                t = self.settings['thickness']; r = option.rect
                painter.drawLine(r.left(), r.bottom() - t//2, r.right(), r.bottom() - t//2)
                painter.restore()


class TreeItem(QTreeWidgetItem):
    def __lt__(self, other):
        col = self.treeWidget().sortColumn()
        v1 = self.data(col, Qt.ItemDataRole.UserRole)
        v2 = other.data(col, Qt.ItemDataRole.UserRole)
        if v1 is not None and v2 is not None:
            try: return float(v1) < float(v2)
            except: pass
        return super().__lt__(other)


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("SETTINGS"); self.resize(500, 700)
        self.setStyleSheet(f"QDialog{{background-color:{CP_BG};border:1px solid {CP_CYAN};}} QLabel{{color:{CP_YELLOW};font-family:'Consolas';font-weight:bold;}} QSpinBox,QComboBox,QLineEdit{{background-color:{CP_PANEL};color:{CP_CYAN};border:1px solid {CP_DIM};padding:4px;}} QPushButton{{background-color:{CP_DIM};border:1px solid {CP_DIM};color:white;padding:10px;font-weight:bold;}} QPushButton:hover{{background-color:#2a2a2a;border:1px solid {CP_YELLOW};color:{CP_YELLOW};}} QScrollArea{{border:none;background-color:transparent;}} QCheckBox{{color:{CP_TEXT};}}")
        l = QVBoxLayout(self); s = QScrollArea(); s.setWidgetResizable(True); c = QWidget(); layout = QVBoxLayout(c)

        gs = f"QGroupBox{{color:{CP_CYAN};border:1px solid {CP_DIM};margin-top:10px;}} QGroupBox::title{{subcontrol-origin:margin;left:10px;}}"

        # Display
        dg = QGroupBox("DISPLAY SETTINGS"); dg.setStyleSheet(gs); df = QFormLayout()
        self.unit_combo = QComboBox(); self.unit_combo.addItems(["MB/s (Bytes)","Mbps (Bits)"])
        self.unit_combo.setCurrentIndex(0 if current_settings.get('unit','MB/s')=='MB/s' else 1)
        df.addRow("SPEED UNIT:", self.unit_combo); dg.setLayout(df); layout.addWidget(dg)

        # Window
        wg = QGroupBox("WINDOW & TABLE"); wg.setStyleSheet(gs); wf = QFormLayout()
        self.win_w = QSpinBox(); self.win_w.setRange(400,3840); self.win_w.setValue(current_settings.get('win_w',1000))
        self.win_h = QSpinBox(); self.win_h.setRange(300,2160); self.win_h.setValue(current_settings.get('win_h',700))
        self.row_h = QSpinBox(); self.row_h.setRange(20,100); self.row_h.setValue(current_settings.get('row_height',40))
        wf.addRow("WIDTH:", self.win_w); wf.addRow("HEIGHT:", self.win_h); wf.addRow("ROW HEIGHT:", self.row_h)
        wg.setLayout(wf); layout.addWidget(wg)

        # Columns
        cg = QGroupBox("COLUMN WIDTHS"); cg.setStyleSheet(gs); cf = QFormLayout()
        ws = current_settings.get('col_weights',[5,25,18,18,17,17])
        while len(ws) < 7: ws.append(13)
        self.spins = []
        for label, w in zip(["ICON","NAME","DL SPEED","UL SPEED","TOTAL DL","TOTAL UL","BLOCK"], ws):
            sb = QSpinBox(); sb.setRange(1,100); sb.setValue(w); self.spins.append(sb)
            cf.addRow(f"{label}:", sb)
        cg.setLayout(cf); layout.addWidget(cg)

        # Highlight
        hg = QGroupBox("PEAK HIGHLIGHT BORDERS"); hg.setStyleSheet(gs.replace(CP_CYAN, CP_YELLOW)); hf = QFormLayout()
        self.hi_global = QCheckBox("Enable All Highlights"); self.hi_global.setChecked(current_settings.get('hi_enabled',True))
        self.hi_dl_s = QCheckBox("DL Speed Peak"); self.hi_dl_s.setChecked(current_settings.get('hi_dl_s',True))
        self.hi_ul_s = QCheckBox("UL Speed Peak"); self.hi_ul_s.setChecked(current_settings.get('hi_ul_s',True))
        self.hi_dl_t = QCheckBox("Total DL Peak"); self.hi_dl_t.setChecked(current_settings.get('hi_dl_t',True))
        self.hi_ul_t = QCheckBox("Total UL Peak"); self.hi_ul_t.setChecked(current_settings.get('hi_ul_t',True))
        hf.addRow(self.hi_global); hf.addRow(self.hi_dl_s); hf.addRow(self.hi_ul_s); hf.addRow(self.hi_dl_t); hf.addRow(self.hi_ul_t)
        self.hi_color = current_settings.get('hi_color', CP_CYAN)
        self.color_btn = QPushButton("PICK BORDER COLOR")
        self.color_btn.setStyleSheet(f"background-color:{self.hi_color};color:black;")
        self.color_btn.clicked.connect(self.pick_color)
        self.hi_thick = QSpinBox(); self.hi_thick.setRange(1,10); self.hi_thick.setValue(current_settings.get('hi_thickness',2))
        hf.addRow("COLOR:", self.color_btn); hf.addRow("THICKNESS:", self.hi_thick)
        hg.setLayout(hf); layout.addWidget(hg)

        fg = QGroupBox("SPEED FILTER PRESETS"); fg.setStyleSheet(gs); ff = QFormLayout()
        self.filter_presets = QLineEdit(current_settings.get('filter_presets','0,0.001,0.01,0.1,1'))
        self.filter_presets.setPlaceholderText('e.g. 0,0.01,0.1,1')
        ff.addRow("PRESETS (MB/s):", self.filter_presets); fg.setLayout(ff); layout.addWidget(fg)

        tg = QGroupBox("SYSTEM TRAY"); tg.setStyleSheet(gs); tf = QVBoxLayout()
        self.tray_toggle = QCheckBox("Minimize to tray on close")
        self.tray_toggle.setChecked(current_settings.get('minimize_to_tray', True))
        tf.addWidget(self.tray_toggle); tg.setLayout(tf); layout.addWidget(tg)

        s.setWidget(c); l.addWidget(s)
        self.save_btn = QPushButton("SAVE & APPLY"); self.save_btn.clicked.connect(self.accept); l.addWidget(self.save_btn)

    def pick_color(self):
        color = QColorDialog.getColor(QColor(self.hi_color), self)
        if color.isValid():
            self.hi_color = color.name()
            self.color_btn.setStyleSheet(f"background-color:{self.hi_color};color:{'white' if color.lightness()<128 else 'black'};")

    def get_settings(self):
        return {
            'unit': 'MB/s' if self.unit_combo.currentIndex()==0 else 'Mbps',
            'win_w': self.win_w.value(), 'win_h': self.win_h.value(), 'row_height': self.row_h.value(),
            'col_weights': [sb.value() for sb in self.spins],
            'hi_enabled': self.hi_global.isChecked(), 'hi_color': self.hi_color, 'hi_thickness': self.hi_thick.value(),
            'hi_dl_s': self.hi_dl_s.isChecked(), 'hi_ul_s': self.hi_ul_s.isChecked(),
            'hi_dl_t': self.hi_dl_t.isChecked(), 'hi_ul_t': self.hi_ul_t.isChecked(),
            'filter_presets': self.filter_presets.text(),
            'minimize_to_tray': self.tray_toggle.isChecked()
        }



class TrafficDB:
    def __init__(self):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS traffic (name TEXT PRIMARY KEY, dl_total INTEGER DEFAULT 0, ul_total INTEGER DEFAULT 0)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS blocked (name TEXT PRIMARY KEY)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS daily_traffic (date TEXT, name TEXT, dl INTEGER DEFAULT 0, ul INTEGER DEFAULT 0, PRIMARY KEY(date, name))")
        self.conn.commit()

    def load(self):
        rows = self.conn.execute("SELECT name, dl_total, ul_total FROM traffic").fetchall()
        return {r[0]: (r[1], r[2]) for r in rows}

    def load_blocked(self):
        return {r[0] for r in self.conn.execute("SELECT name FROM blocked").fetchall()}

    def save_batch(self, data):
        self.conn.executemany("INSERT INTO traffic(name,dl_total,ul_total) VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET dl_total=excluded.dl_total, ul_total=excluded.ul_total", data)
        self.conn.commit()

    def save_daily_batch(self, date, data):
        # data: [(name, dl_inc, ul_inc), ...]
        self.conn.executemany("INSERT INTO daily_traffic(date, name, dl, ul) VALUES(?,?,?,?) ON CONFLICT(date, name) DO UPDATE SET dl=dl+excluded.dl, ul=ul+excluded.ul", 
                             [(date, n, dl, ul) for n, dl, ul in data if dl > 0 or ul > 0])
        self.conn.commit()

    def get_daily_usage(self, date):
        return self.conn.execute("SELECT name, dl, ul FROM daily_traffic WHERE date=?", (date,)).fetchall()

    def get_available_dates(self):
        rows = self.conn.execute("SELECT DISTINCT date FROM daily_traffic").fetchall()
        return [r[0] for r in rows]

    def set_blocked(self, name, blocked):
        if blocked: self.conn.execute("INSERT OR IGNORE INTO blocked(name) VALUES(?)", (name,))
        else: self.conn.execute("DELETE FROM blocked WHERE name=?", (name,))
        self.conn.commit()

    def reset(self):
        self.conn.execute("DELETE FROM traffic")
        self.conn.execute("DELETE FROM blocked")
        self.conn.commit()

class MonitorStats:
    def __init__(self, db):
        self.lock = threading.Lock(); self.db = db
        # pid -> {name, exe,
        #         wan_recv_total, wan_sent_total, wan_recv_curr, wan_sent_curr,
        #         lan_recv_total, lan_sent_total, lan_recv_curr, lan_sent_curr}
        self.proc_data = {}
        self.sys_wan_dl_total = 0; self.sys_wan_ul_total = 0
        self.sys_wan_dl_curr = 0;  self.sys_wan_ul_curr = 0
        self.sys_lan_dl_total = 0; self.sys_lan_ul_total = 0
        self.sys_lan_dl_curr = 0;  self.sys_lan_ul_curr = 0
        self.db_totals = {}
        for name, (dl, ul) in db.load().items():
            if name == '[SYSTEM/OTHER/VPN]': self.sys_wan_dl_total = dl; self.sys_wan_ul_total = ul
            else: self.db_totals[name] = (dl, ul)

    def update_packet(self, pid, size, direction, is_lan):
        with self.lock:
            if pid is None:
                if is_lan:
                    if direction == 'recv': self.sys_lan_dl_curr += size; self.sys_lan_dl_total += size
                    else:                   self.sys_lan_ul_curr += size; self.sys_lan_ul_total += size
                else:
                    if direction == 'recv': self.sys_wan_dl_curr += size; self.sys_wan_dl_total += size
                    else:                   self.sys_wan_ul_curr += size; self.sys_wan_ul_total += size
                return
            if pid not in self.proc_data:
                try: p = psutil.Process(pid); name = p.name(); exe = p.exe()
                except: name = f"PID {pid}"; exe = ""
                dl0, ul0 = self.db_totals.pop(name, (0, 0))
                self.proc_data[pid] = {
                    'name': name, 'exe': exe,
                    'wan_recv_total': dl0, 'wan_sent_total': ul0,
                    'wan_recv_curr': 0,    'wan_sent_curr': 0,
                    'lan_recv_total': 0,   'lan_sent_total': 0,
                    'lan_recv_curr': 0,    'lan_sent_curr': 0,
                }
            d = self.proc_data[pid]
            if is_lan:
                if direction == 'sent': d['lan_sent_total'] += size; d['lan_sent_curr'] += size
                else:                   d['lan_recv_total'] += size; d['lan_recv_curr'] += size
            else:
                if direction == 'sent': d['wan_sent_total'] += size; d['wan_sent_curr'] += size
                else:                   d['wan_recv_total'] += size; d['wan_recv_curr'] += size

    def get_snapshot(self, scope='WAN & LAN'):
        """
        scope: 'WAN' | 'LAN' | 'WAN & LAN'
        Returns (snap_list, dl_speed_total, ul_speed_total)
        Each snap entry has: pid, name, exe, dl_speed, ul_speed, dl_total, ul_total
        """
        with self.lock:
            snap = []
            for pid, d in self.proc_data.items():
                if scope == 'WAN':
                    dl_s = d['wan_recv_curr']; ul_s = d['wan_sent_curr']
                    dl_t = d['wan_recv_total']; ul_t = d['wan_sent_total']
                    d['wan_recv_curr'] = 0; d['wan_sent_curr'] = 0
                elif scope == 'LAN':
                    dl_s = d['lan_recv_curr']; ul_s = d['lan_sent_curr']
                    dl_t = d['lan_recv_total']; ul_t = d['lan_sent_total']
                    d['lan_recv_curr'] = 0; d['lan_sent_curr'] = 0
                else:  # WAN & LAN
                    dl_s = d['wan_recv_curr'] + d['lan_recv_curr']
                    ul_s = d['wan_sent_curr'] + d['lan_sent_curr']
                    dl_t = d['wan_recv_total'] + d['lan_recv_total']
                    ul_t = d['wan_sent_total'] + d['lan_sent_total']
                    d['wan_recv_curr'] = 0; d['wan_sent_curr'] = 0
                    d['lan_recv_curr'] = 0; d['lan_sent_curr'] = 0
                snap.append({'pid': pid, 'name': d['name'], 'exe': d['exe'],
                             'dl_speed': dl_s, 'ul_speed': ul_s,
                             'dl_total': dl_t, 'ul_total': ul_t})
            # DB-only entries (loaded from disk, not yet seen this session)
            for name, (dl, ul) in self.db_totals.items():
                snap.append({'pid': -1, 'name': name, 'exe': '',
                             'dl_speed': 0, 'ul_speed': 0,
                             'dl_total': dl if scope != 'LAN' else 0,
                             'ul_total': ul if scope != 'LAN' else 0})
            # SYSTEM/OTHER/VPN row
            if scope == 'WAN':
                sys_dl_s = self.sys_wan_dl_curr; sys_ul_s = self.sys_wan_ul_curr
                sys_dl_t = self.sys_wan_dl_total; sys_ul_t = self.sys_wan_ul_total
                self.sys_wan_dl_curr = 0; self.sys_wan_ul_curr = 0
            elif scope == 'LAN':
                sys_dl_s = self.sys_lan_dl_curr; sys_ul_s = self.sys_lan_ul_curr
                sys_dl_t = self.sys_lan_dl_total; sys_ul_t = self.sys_lan_ul_total
                self.sys_lan_dl_curr = 0; self.sys_lan_ul_curr = 0
            else:
                sys_dl_s = self.sys_wan_dl_curr + self.sys_lan_dl_curr
                sys_ul_s = self.sys_wan_ul_curr + self.sys_lan_ul_curr
                sys_dl_t = self.sys_wan_dl_total + self.sys_lan_dl_total
                sys_ul_t = self.sys_wan_ul_total + self.sys_lan_ul_total
                self.sys_wan_dl_curr = 0; self.sys_wan_ul_curr = 0
                self.sys_lan_dl_curr = 0; self.sys_lan_ul_curr = 0
            snap.append({'pid': 0, 'name': '[SYSTEM/OTHER/VPN]', 'exe': '',
                         'dl_speed': sys_dl_s, 'ul_speed': sys_ul_s,
                         'dl_total': sys_dl_t, 'ul_total': sys_ul_t})
            dl_t_total = sum(e['dl_speed'] for e in snap)
            ul_t_total = sum(e['ul_speed'] for e in snap)
            return snap, dl_t_total, ul_t_total


class NetworkThread(threading.Thread):
    """Capture thread using pydivert — gets PID directly from WinDivert/WFP."""
    def __init__(self, stats):
        super().__init__(); self.stats = stats; self.daemon = True; self.running = True
        self._local_ips = self._get_local_ips()
        self._loopback_prefixes = ('127.', '::1')
        # (src_ip, src_port, dst_ip, dst_port) -> pid  — flow cache for inbound PID resolution
        self._flow_map = {}; self._flow_lock = threading.Lock()
        # port -> pid connection table, refreshed every 200ms
        self._conn_map = {}; self._conn_lock = threading.Lock()
        threading.Thread(target=self._refresh_conns, daemon=True).start()
        threading.Thread(target=self._expire_flows, daemon=True).start()

    def _get_local_ips(self):
        ips = set()
        for _, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET: ips.add(a.address)
        return ips

    def _refresh_conns(self):
        """Refresh local port->pid map every 200 ms."""
        while self.running:
            m = {}
            try:
                for c in psutil.net_connections(kind='inet'):
                    if c.laddr and c.pid:
                        m[(c.laddr.ip, c.laddr.port)] = c.pid
                        if c.laddr.ip in ('0.0.0.0', '::'):
                            m[('*', c.laddr.port)] = c.pid
            except: pass
            with self._conn_lock: self._conn_map = m
            time.sleep(0.2)

    def _expire_flows(self):
        """Evict flow-cache entries older than 60 s to prevent unbounded growth."""
        while self.running:
            time.sleep(30)
            cutoff = time.monotonic() - 60
            with self._flow_lock:
                stale = [k for k, (pid, ts) in self._flow_map.items() if ts < cutoff]
                for k in stale: del self._flow_map[k]

    def _is_loopback(self, ip):
        if not ip: return False
        return ip.startswith(self._loopback_prefixes)

    def _get_pid(self, packet):
        """
        Resolve PID using three methods:
        1. WinDivert process_id (outbound only, most reliable).
           Also stores the outbound flow so the matching inbound reply
           can be attributed to the same process without a port-table hit.
        2. Flow cache  — inbound reply matched to its outbound request.
        3. Connection table lookup by local port (last resort).
        """
        src_ip = packet.ipv4.src_addr if packet.ipv4 else None
        dst_ip = packet.ipv4.dst_addr if packet.ipv4 else None
        sport = dport = 0
        if packet.tcp:   sport = packet.tcp.src_port;  dport = packet.tcp.dst_port
        elif packet.udp: sport = packet.udp.src_port;  dport = packet.udp.dst_port

        # 1. WinDivert direct PID (outbound only)
        pid = getattr(packet, 'process_id', None) or None
        if pid and packet.is_outbound:
            flow_key = (dst_ip, dport, src_ip, sport)   # reversed = what the reply looks like
            with self._flow_lock:
                self._flow_map[flow_key] = (pid, time.monotonic())
            return pid
        if pid:
            return pid

        # 2. Flow cache for inbound reply packets
        if not packet.is_outbound:
            flow_key = (src_ip, sport, dst_ip, dport)
            with self._flow_lock:
                entry = self._flow_map.get(flow_key)
                if entry:
                    self._flow_map[flow_key] = (entry[0], time.monotonic())
                    return entry[0]

        # 3. Connection table by local port
        with self._conn_lock:
            if packet.is_outbound:
                pid = self._conn_map.get((src_ip, sport)) or self._conn_map.get(('*', sport))
            else:
                pid = self._conn_map.get((dst_ip, dport)) or self._conn_map.get(('*', dport))
        return pid

    def run(self):
        try:
            flt = ("ip and "
                   "ip.SrcAddr != 127.0.0.1 and ip.DstAddr != 127.0.0.1 and "
                   "ip.SrcAddr != 0.0.0.0 and ip.DstAddr != 0.0.0.0")
            with pydivert.WinDivert(flt, layer=pydivert.Layer.NETWORK, flags=pydivert.Flag.SNIFF) as w:
                for packet in w:
                    if not self.running: break
                    src_ip = packet.ipv4.src_addr if packet.ipv4 else None
                    dst_ip = packet.ipv4.dst_addr if packet.ipv4 else None
                    if self._is_loopback(src_ip) or self._is_loopback(dst_ip):
                        continue
                    size = len(packet.raw)
                    if size > 65535: continue
                    pid = self._get_pid(packet)
                    direction = 'sent' if packet.is_outbound else 'recv'
                    # Classify WAN vs LAN: the remote end determines scope
                    remote_ip = dst_ip if packet.is_outbound else src_ip
                    is_lan = is_private_ip(remote_ip) if remote_ip else False
                    self.stats.update_packet(pid, size, direction, is_lan)
        except Exception as e:
            print(f"[pydivert error] {e}")


class DailyUsageDialog(QDialog):
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("DAILY TRAFFIC HISTORY"); self.resize(600, 500)
        self.setStyleSheet(f"QDialog{{background-color:{CP_BG};border:1px solid {CP_CYAN};}} QLabel{{color:{CP_YELLOW};font-family:'Consolas';font-weight:bold;}} QTreeWidget{{background-color:{CP_PANEL};border:1px solid {CP_DIM};color:{CP_TEXT};outline:none;}} QHeaderView::section{{background-color:{CP_DIM};color:{CP_YELLOW};padding:5px;border:1px solid {CP_BG};font-weight:bold;}}")
        l = QVBoxLayout(self)
        self.cal = QCalendarWidget()
        self.cal.setStyleSheet(f"QCalendarWidget QWidget{{ background-color: {CP_PANEL}; color: {CP_TEXT}; }} QCalendarWidget QAbstractItemView:enabled{{ background-color: {CP_PANEL}; color: {CP_TEXT}; selection-background-color: {CP_CYAN}; selection-color: black; }} QCalendarWidget QToolButton{{ color: {CP_YELLOW}; }}")
        self.cal.selectionChanged.connect(self.update_list)
        l.addWidget(self.cal)
        
        self.tree = QTreeWidget(); self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["APPLICATION", "TOTAL DL", "TOTAL UL"])
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tree.setSortingEnabled(True)
        self.current_sort_col = 1; self.current_sort_order = Qt.SortOrder.DescendingOrder
        self.tree.header().sortIndicatorChanged.connect(self.on_sort_changed)
        l.addWidget(self.tree)
        
        # Structured Footer for Dialog
        self.footer_widget = QWidget()
        self.footer_widget.setStyleSheet(f"background-color:{CP_PANEL}; border-top:1px solid {CP_DIM};")
        self.footer_layout = QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(0,0,0,0); self.footer_layout.setSpacing(0)
        self.footer_labels = []
        for i in range(3):
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if i >= 1 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lbl.setStyleSheet(f"padding: 5px; font-weight: bold; border-right: 1px solid {CP_DIM}; color: {CP_YELLOW};")
            if i == 0: lbl.setText(" TOTAL FOR DAY:")
            self.footer_layout.addWidget(lbl)
            self.footer_labels.append(lbl)
        l.addWidget(self.footer_widget)
        
        self.highlight_dates()
        self.update_list()

    def highlight_dates(self):
        from PyQt6.QtGui import QTextCharFormat
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(CP_YELLOW))
        fmt.setBackground(QColor("#1a3a3a"))
        fmt.setFontWeight(QFont.Weight.Bold)
        for d_str in self.db.get_available_dates():
            try:
                d = datetime.strptime(d_str, "%Y-%m-%d")
                from PyQt6.QtCore import QDate
                self.cal.setDateTextFormat(QDate(d.year, d.month, d.day), fmt)
            except: pass

    def on_sort_changed(self, i, o):
        if i != self.current_sort_col and o == Qt.SortOrder.AscendingOrder:
            self.tree.header().blockSignals(True)
            self.tree.header().setSortIndicator(i, Qt.SortOrder.DescendingOrder)
            self.tree.header().blockSignals(False)
            self.current_sort_col = i; self.current_sort_order = Qt.SortOrder.DescendingOrder
            self.tree.sortByColumn(i, Qt.SortOrder.DescendingOrder)
            return
        self.current_sort_col = i; self.current_sort_order = o

    def update_list(self):
        date_str = self.cal.selectedDate().toString("yyyy-MM-dd")
        rows = self.db.get_daily_usage(date_str)
        self.tree.setSortingEnabled(False)
        self.tree.clear()
        t_dl = 0; t_ul = 0
        for name, dl, ul in rows:
            t_dl += dl; t_ul += ul
            item = TreeItem(self.tree)
            item.setText(0, name)
            item.setText(1, format_size(dl, "MB/s")); item.setData(1, Qt.ItemDataRole.UserRole, dl)
            item.setText(2, format_size(ul, "MB/s")); item.setData(2, Qt.ItemDataRole.UserRole, ul)
        
        if hasattr(self, 'footer_labels'):
            self.footer_labels[1].setText(format_size(t_dl, "MB/s"))
            self.footer_labels[1].setStyleSheet(f"padding:5px; font-weight:bold; color:{CP_YELLOW}; border-right:1px solid {CP_DIM};")
            self.footer_labels[2].setText(format_size(t_ul, "MB/s"))
            self.footer_labels[2].setStyleSheet(f"padding:5px; font-weight:bold; color:{CP_GREEN}; border-right:1px solid {CP_DIM};")
            QTimer.singleShot(10, self._sync_footer)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(1, Qt.SortOrder.DescendingOrder)

    def _sync_footer(self):
        for i in range(min(3, len(self.footer_labels))):
            self.footer_labels[i].setFixedWidth(self.tree.columnWidth(i))


class App(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NET-SPEED HOOKER // WinDivert")
        create_default_icon()
        self.load_settings(); self.resize(self.win_w, self.win_h)
        self.setWindowIcon(QIcon(ICON_FILE))
        self.db = TrafficDB()
        _bj = load_blocked_json()  # {name: exe}
        self.blocked_names = set(_bj.keys())
        self.blocked_exe = dict(_bj)
        self.stats = MonitorStats(self.db); self.monitor = NetworkThread(self.stats); self.monitor.start()
        self.icon_cache = {}; self.icon_provider = QFileIconProvider()
        self.init_ui(); self.init_tray()
        self.timer = QTimer(); self.timer.timeout.connect(self.update_stats); self.timer.start(1000)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(ICON_FILE))
        self.tray_icon.setToolTip("NET-SPEED HOOKER")
        
        menu = QMenu()
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.show_normal)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.full_exit)
        
        menu.addAction(restore_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_normal()

    def show_normal(self):
        self.show()
        self.activateWindow()

    def full_exit(self):
        self.monitor.running = False
        self.save_settings()
        QApplication.quit()

    def load_settings(self):
        self.win_w=1000; self.win_h=700; self.row_height=40; self.col_weights=[5,22,16,16,14,14,13]
        self.current_sort_col=2; self.current_sort_order=Qt.SortOrder.DescendingOrder
        self.unit="MB/s"; self.show_dl=True; self.show_ul=True
        self.hi_enabled=True; self.hi_color=CP_CYAN; self.hi_thickness=2
        self.hi_dl_s=True; self.hi_ul_s=True; self.hi_dl_t=True; self.hi_ul_t=True
        self.min_speed=0; self.min_total=0; self.filter_presets='0,0.001,0.01,0.1,1'
        self.minimize_to_tray=True; self.net_scope='WAN & LAN'
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE) as f: s = json.load(f)
                self.win_w=s.get('win_w',1000); self.win_h=s.get('win_h',700); self.row_height=s.get('row_height',40)
                self.col_weights=s.get('col_weights',[5,22,16,16,14,14,13])
                while len(self.col_weights) < 7: self.col_weights.append(13)
                self.current_sort_col=s.get('sort_col',2); self.current_sort_order=Qt.SortOrder(s.get('sort_order',1))
                self.unit=s.get('unit','MB/s'); self.show_dl=s.get('show_dl',True); self.show_ul=s.get('show_ul',True)
                self.hi_enabled=s.get('hi_enabled',True); self.hi_color=s.get('hi_color',CP_CYAN)
                self.hi_thickness=s.get('hi_thickness',2)
                self.hi_dl_s=s.get('hi_dl_s',True); self.hi_ul_s=s.get('hi_ul_s',True)
                self.hi_dl_t=s.get('hi_dl_t',True); self.hi_ul_t=s.get('hi_ul_t',True)
                self.min_speed=s.get('min_speed',0); self.min_total=s.get('min_total',0)
                self.filter_presets=s.get('filter_presets','0,0.001,0.01,0.1,1')
                self.minimize_to_tray=s.get('minimize_to_tray',True)
                self.net_scope=s.get('net_scope','WAN & LAN')
        except: pass

    def save_settings(self):
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            try: 
                v = self.filter_combo.currentData() if hasattr(self,'filter_combo') else self.min_speed
                _ms = float(v) if v is not None else self.min_speed
            except: _ms = self.min_speed
            try: 
                v = self.filter_total_combo.currentData() if hasattr(self,'filter_total_combo') else self.min_total
                _mt = float(v) if v is not None else self.min_total
            except: _mt = self.min_total
            s = {'unit':self.unit,'win_w':self.width(),'win_h':self.height(),'row_height':self.row_height,
                 'col_weights':self.col_weights,'sort_col':self.current_sort_col,'sort_order':self.current_sort_order.value,
                 'show_dl':self.show_dl,'show_ul':self.show_ul,'hi_enabled':self.hi_enabled,'hi_color':self.hi_color,
                 'hi_thickness':self.hi_thickness,'hi_dl_s':self.hi_dl_s,'hi_ul_s':self.hi_ul_s,
                 'hi_dl_t':self.hi_dl_t,'hi_ul_t':self.hi_ul_t,'min_speed':_ms,'min_total':_mt,
                 'filter_presets':self.filter_presets,'minimize_to_tray':self.minimize_to_tray,
                 'net_scope': self.net_scope}
            with open(SETTINGS_FILE,'w') as f: json.dump(s, f, indent=4)
        except: pass

    def init_ui(self):
        self.setStyleSheet(f"QMainWindow{{background-color:{CP_BG};}} QWidget{{color:{CP_TEXT};font-family:'Consolas';font-size:10pt;}} QTreeWidget{{background-color:{CP_PANEL};border:1px solid {CP_DIM};color:{CP_TEXT};outline:none;show-decoration-selected:0;}} QTreeWidget::item{{border-bottom:1px solid {CP_DIM};padding:4px;}} QTreeWidget::item:hover{{background-color:#1a1a1a;}} QTreeWidget::item:selected{{background-color:{CP_DIM};color:{CP_YELLOW};outline:none;}} QHeaderView::section{{background-color:{CP_DIM};color:{CP_YELLOW};padding:5px;border:1px solid {CP_BG};font-weight:bold;}} QPushButton{{background-color:{CP_DIM};border:1px solid {CP_DIM};color:white;padding:6px 12px;font-weight:bold;}} QPushButton:hover{{background-color:#2a2a2a;border:1px solid {CP_YELLOW};color:{CP_YELLOW};}} QCheckBox{{color:{CP_CYAN};font-weight:bold;}} QTreeWidget::indicator{{width:13px;height:13px;border:1px solid {CP_DIM};background:{CP_PANEL};}}QTreeWidget::indicator:checked{{background:{CP_CYAN};border:1px solid {CP_CYAN};}}QCheckBox::indicator{{width:13px;height:13px;border:1px solid {CP_DIM};background:{CP_PANEL};}}QCheckBox::indicator:checked{{background:{CP_CYAN};border:1px solid {CP_CYAN};}}")
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c); ht = QHBoxLayout()
        self.cb_dl = QCheckBox("DOWNLOAD"); self.cb_dl.setChecked(self.show_dl); self.cb_dl.stateChanged.connect(self.toggle_cols)
        self.cb_ul = QCheckBox("UPLOAD"); self.cb_ul.setChecked(self.show_ul); self.cb_ul.stateChanged.connect(self.toggle_cols)
        ht.addStretch()
        fl = QLabel("MIN SPD:"); fl.setStyleSheet(f"color:{CP_DIM};font-size:9pt;"); ht.addWidget(fl)
        self.filter_combo = QComboBox(); self.filter_combo.setFixedWidth(80)
        self.filter_combo.setStyleSheet(f'QComboBox{{background-color:{CP_PANEL};color:{CP_CYAN};border:1px solid {CP_DIM};padding:2px;}}')
        ht.addWidget(self.filter_combo)
        ftl = QLabel("MIN TOT:"); ftl.setStyleSheet(f"color:{CP_DIM};font-size:9pt;"); ht.addWidget(ftl)
        self.filter_total_combo = QComboBox(); self.filter_total_combo.setFixedWidth(80)
        self.filter_total_combo.setStyleSheet(f'QComboBox{{background-color:{CP_PANEL};color:{CP_CYAN};border:1px solid {CP_DIM};padding:2px;}}')
        ht.addWidget(self.filter_total_combo)
        # WAN / LAN scope selector
        scl = QLabel("SCOPE:"); scl.setStyleSheet(f"color:{CP_DIM};font-size:9pt;"); ht.addWidget(scl)
        self.scope_combo = QComboBox(); self.scope_combo.setFixedWidth(100)
        self.scope_combo.setStyleSheet(f'QComboBox{{background-color:{CP_PANEL};color:{CP_YELLOW};border:1px solid {CP_DIM};padding:2px;font-weight:bold;}}')
        self.scope_combo.addItems(['WAN & LAN', 'WAN', 'LAN'])
        self.scope_combo.setCurrentText(self.net_scope)
        self.scope_combo.currentTextChanged.connect(self._on_scope_changed)
        ht.addWidget(self.scope_combo)
        self._rebuild_filter_combo()
        self.filter_combo.currentIndexChanged.connect(self.save_settings)
        self.filter_total_combo.currentIndexChanged.connect(self.save_settings)
        ht.addWidget(self.cb_dl); ht.addWidget(self.cb_ul)
        l.addLayout(ht)
        hb = QHBoxLayout(); hb.addStretch()
        cb = QPushButton("CALENDAR"); cb.clicked.connect(self.show_calendar); hb.addWidget(cb)
        dbb = QPushButton("RESET DB"); dbb.clicked.connect(self.reset_db); hb.addWidget(dbb)
        rb = QPushButton("RESTART"); rb.clicked.connect(self.restart_app); hb.addWidget(rb)
        sb = QPushButton("SETTINGS"); sb.clicked.connect(self.show_settings); hb.addWidget(sb); l.addLayout(hb)
        self.tree = QTreeWidget(); self.tree.setColumnCount(7)
        self.tree.setHeaderLabels(["ICON","APP","SPD IN","SPD OUT","TOT IN","TOT OUT","⛔"])
        self.tree.setIndentation(20); self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.tree.setAutoScroll(False)
        self.delegate = CustomBorderDelegate(self.tree); self.apply_delegate_settings(); self.tree.setItemDelegate(self.delegate)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        QTimer.singleShot(0, self._apply_col_widths)
        self.tree.setSortingEnabled(True)
        self.tree.header().sortIndicatorChanged.connect(self.on_sort_changed)
        self.tree.header().setSortIndicator(self.current_sort_col, self.current_sort_order); l.addWidget(self.tree)
        
        # Structured Footer
        self.footer_widget = QWidget()
        self.footer_widget.setStyleSheet(f"background-color:{CP_PANEL}; border-top:1px solid {CP_DIM};")
        self.footer_layout = QHBoxLayout(self.footer_widget)
        self.footer_layout.setContentsMargins(0,0,0,0); self.footer_layout.setSpacing(0)
        self.footer_labels = []
        for i in range(7):
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if i >= 2 else Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lbl.setStyleSheet(f"padding: 5px; font-weight: bold; border-right: 1px solid {CP_DIM};")
            if i == 1: lbl.setText(" TOTALS:")
            self.footer_layout.addWidget(lbl)
            self.footer_labels.append(lbl)
        l.addWidget(self.footer_widget)
        
        self.toggle_cols()


    def _rebuild_filter_combo(self):
        curs = self.filter_combo.currentData() if hasattr(self,'filter_combo') and self.filter_combo.currentData() is not None else self.min_speed
        curt = self.filter_total_combo.currentData() if hasattr(self,'filter_total_combo') and self.filter_total_combo.currentData() is not None else self.min_total
        for cb, cur in [(self.filter_combo, curs), (self.filter_total_combo, curt)]:
            cb.blockSignals(True); cb.clear()
            for v in self.filter_presets.split(','):
                v=v.strip()
                try: 
                    num = float(v)
                    # Convert MB (from presets) to Bytes for format_size, but show units
                    # Presets are in MB, so num * 1024 * 1024
                    display_text = format_size(num * 1048576, "MB/s") if num > 0 else "0 B"
                    cb.addItem(display_text, num)
                except ValueError: pass
            try:
                if cur is None: fval = 0.0
                elif isinstance(cur, (float, int)): fval = float(cur)
                else: fval = float(cur) if str(cur).strip() else 0.0
                idx = cb.findData(fval)
            except ValueError:
                idx = 0
            cb.setCurrentIndex(idx if idx>=0 else 0)
            cb.blockSignals(False)

    def _apply_col_widths(self):
        header = self.tree.header()
        header.setStretchLastSection(False)
        total = self.tree.viewport().width() or self.win_w
        s = sum(self.col_weights) or 1
        for i in range(min(len(self.col_weights), 7)):
            w = int(total * self.col_weights[i] / s)
            self.tree.setColumnWidth(i, w)
            if i < len(self.footer_labels):
                self.footer_labels[i].setFixedWidth(w)
        header.setStretchLastSection(True)

    def apply_delegate_settings(self):
        self.delegate.settings = {'enabled':self.hi_enabled,'color':self.hi_color,'thickness':self.hi_thickness,
                                  'cols':{2:self.hi_dl_s,3:self.hi_ul_s,4:self.hi_dl_t,5:self.hi_ul_t}}

    def toggle_cols(self):
        self.show_dl = self.cb_dl.isChecked(); self.show_ul = self.cb_ul.isChecked()
        self.tree.setColumnHidden(2, not self.show_dl); self.tree.setColumnHidden(4, not self.show_dl)
        self.tree.setColumnHidden(3, not self.show_ul); self.tree.setColumnHidden(5, not self.show_ul)
        if hasattr(self, 'footer_labels'):
            self.footer_labels[2].setHidden(not self.show_dl); self.footer_labels[4].setHidden(not self.show_dl)
            self.footer_labels[3].setHidden(not self.show_ul); self.footer_labels[5].setHidden(not self.show_ul)
        self.save_settings()

    def on_sort_changed(self, i, o):
        if i != self.current_sort_col and o == Qt.SortOrder.AscendingOrder:
            self.tree.header().blockSignals(True)
            self.tree.header().setSortIndicator(i, Qt.SortOrder.DescendingOrder)
            self.tree.header().blockSignals(False)
            self.current_sort_col = i; self.current_sort_order = Qt.SortOrder.DescendingOrder
            self.tree.sortByColumn(i, Qt.SortOrder.DescendingOrder)
            self.save_settings()
            return
        self.current_sort_col = i; self.current_sort_order = o; self.save_settings()

    def _on_scope_changed(self, text):
        self.net_scope = text
        self.save_settings()

    def update_stats(self):
        snap, dl_t, ul_t = self.stats.get_snapshot(self.net_scope)
        total_dl_acc = sum(e['dl_total'] for e in snap)
        total_ul_acc = sum(e['ul_total'] for e in snap)
        
        if hasattr(self, 'footer_labels'):
            self.footer_labels[2].setText(format_size(dl_t, self.unit)); self.footer_labels[2].setStyleSheet(f"padding:5px; font-weight:bold; color:{CP_CYAN if dl_t>0 else CP_TEXT}; border-right:1px solid {CP_DIM};")
            self.footer_labels[3].setText(format_size(ul_t, self.unit)); self.footer_labels[3].setStyleSheet(f"padding:5px; font-weight:bold; color:{CP_ORANGE if ul_t>0 else CP_TEXT}; border-right:1px solid {CP_DIM};")
            self.footer_labels[4].setText(format_size(total_dl_acc, "MB/s")); self.footer_labels[4].setStyleSheet(f"padding:5px; font-weight:bold; color:{CP_YELLOW}; border-right:1px solid {CP_DIM};")
            self.footer_labels[5].setText(format_size(total_ul_acc, "MB/s")); self.footer_labels[5].setStyleSheet(f"padding:5px; font-weight:bold; color:{CP_GREEN}; border-right:1px solid {CP_DIM};")
        
        groups = {}; max_v = {2:0, 3:0, 4:0, 5:0}
        for d in snap:
            n = d['name']
            if n not in groups: groups[n] = {'dl_s':0,'ul_s':0,'dl_t':0,'ul_t':0,'exe':d['exe'],'items':[], 'dl_inc': 0, 'ul_inc': 0}
            groups[n]['dl_inc'] += d['dl_speed']
            groups[n]['ul_inc'] += d['ul_speed']
            groups[n]['dl_s'] += d['dl_speed']; groups[n]['ul_s'] += d['ul_speed']
            groups[n]['dl_t'] += d['dl_total']; groups[n]['ul_t'] += d['ul_total']
            groups[n]['items'].append(d)
            max_v[2]=max(max_v[2],groups[n]['dl_s']); max_v[3]=max(max_v[3],groups[n]['ul_s'])
            max_v[4]=max(max_v[4],groups[n]['dl_t']); max_v[5]=max(max_v[5],groups[n]['ul_t'])
        self.delegate.max_values = max_v
        self.tree.setSortingEnabled(False)
        exs = {self.tree.topLevelItem(i).text(1): self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())}
        for n, gd in groups.items():
            is_new = n not in exs
            r = exs[n] if not is_new else TreeItem(self.tree); r.setText(1, n)
            r.setFlags(r.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            if is_new: r.setCheckState(6, Qt.CheckState.Checked if n in self.blocked_names else Qt.CheckState.Unchecked)
            # resolve exe from running processes if missing
            if not gd['exe']:
                for pid, d in list(self.stats.proc_data.items()):
                    if d['name'] == n and d['exe']: gd['exe'] = d['exe']; break
            if gd['exe'] and os.path.exists(gd['exe']) and gd['exe'] not in self.icon_cache:
                self.icon_cache[gd['exe']] = self.icon_provider.icon(QFileInfo(gd['exe'])).pixmap(QSize(24,24))
            if gd['exe'] in self.icon_cache: r.setIcon(0, QIcon(self.icon_cache[gd['exe']]))
            r.setText(2, format_size(gd['dl_s'],self.unit)); r.setData(2, Qt.ItemDataRole.UserRole, gd['dl_s'])
            r.setText(3, format_size(gd['ul_s'],self.unit)); r.setData(3, Qt.ItemDataRole.UserRole, gd['ul_s'])
            r.setText(4, format_size(gd['dl_t'],"MB/s")); r.setData(4, Qt.ItemDataRole.UserRole, gd['dl_t'])
            r.setText(5, format_size(gd['ul_t'],"MB/s")); r.setData(5, Qt.ItemDataRole.UserRole, gd['ul_t'])
            r.setSizeHint(0, QSize(0, self.row_height))
            r.setForeground(2, QColor(CP_CYAN if gd['dl_s']>0 else CP_TEXT))
            r.setForeground(3, QColor(CP_ORANGE if gd['ul_s']>0 else CP_TEXT))
            r.setForeground(4, QColor(CP_YELLOW)); r.setForeground(5, QColor(CP_GREEN))
            
            try: 
                # Use currentData() to get the raw float value (MB) stored in the combo
                _fs_mb = self.filter_combo.currentData()
                if _fs_mb is None: _fs_mb = float(self.filter_combo.currentText()) # fallback
                _fs = _fs_mb * 1048576.0
            except: _fs=0
            try: 
                _ft_mb = self.filter_total_combo.currentData()
                if _ft_mb is None: _ft_mb = float(self.filter_total_combo.currentText()) # fallback
                _ft = _ft_mb * 1048576.0
            except: _ft=0
            
            hide_spd = (gd['dl_s'] < _fs and gd['ul_s'] < _fs) if _fs > 0 else False
            hide_tot = (gd['dl_t'] < _ft and gd['ul_t'] < _ft) if _ft > 0 else False
            
            if _fs > 0 and _ft > 0:
                r.setHidden(hide_spd and hide_tot)
            else:
                r.setHidden(hide_spd or hide_tot)
            if len(gd['items']) > 1:
                eps = {r.child(j).text(1): r.child(j) for j in range(r.childCount())}; nps = set()
                for id in gd['items']:
                    pt = f"PID: {id['pid']}"; nps.add(pt)
                    c = eps[pt] if pt in eps else TreeItem(r)
                    c.setText(1, pt); c.setText(2, format_size(id['dl_speed'],self.unit)); c.setData(2, Qt.ItemDataRole.UserRole, id['dl_speed'])
                    c.setText(3, format_size(id['ul_speed'],self.unit)); c.setData(3, Qt.ItemDataRole.UserRole, id['ul_speed'])
                    c.setText(4, format_size(id['dl_total'],"MB/s")); c.setData(4, Qt.ItemDataRole.UserRole, id['dl_total'])
                    c.setText(5, format_size(id['ul_total'],"MB/s")); c.setData(5, Qt.ItemDataRole.UserRole, id['ul_total'])
                    c.setSizeHint(0, QSize(0, self.row_height))
                    for col in range(1, 6): c.setForeground(col, QColor(CP_SUBTEXT))
                for pt, child in eps.items():
                    if pt not in nps: r.removeChild(child)
            else:
                for j in reversed(range(r.childCount())): r.removeChild(r.child(j))
        for i in reversed(range(self.tree.topLevelItemCount())):
            if self.tree.topLevelItem(i).text(1) not in groups: self.tree.takeTopLevelItem(i)
        self.tree.setSortingEnabled(True); self.tree.sortByColumn(self.current_sort_col, self.current_sort_order)
        self.tree.viewport().update()
        self._save_db(groups)
        self._sync_blocked()

    def _save_db(self, groups):
        # groups is per-name aggregation from update_stats
        data = [(n, gd['dl_t'], gd['ul_t']) for n, gd in groups.items()]
        self.db.save_batch(data)
        
        daily_data = [(n, gd['dl_inc'], gd['ul_inc']) for n, gd in groups.items() if gd['dl_inc'] > 0 or gd['ul_inc'] > 0]
        if daily_data:
            self.db.save_daily_batch(datetime.now().strftime("%Y-%m-%d"), daily_data)

    def show_calendar(self):
        dlg = DailyUsageDialog(self, self.db)
        dlg.exec()

    def _fw_block(self, exe, block):
        import subprocess
        rule = f'NSH_BLOCK_{os.path.basename(exe)}'
        if block:
            cmds = [
                f'netsh advfirewall firewall add rule name="{rule}" dir=out action=block program="{exe}" enable=yes',
                f'netsh advfirewall firewall add rule name="{rule}_in" dir=in action=block program="{exe}" enable=yes',
            ]
        else:
            cmds = [
                f'netsh advfirewall firewall delete rule name="{rule}"',
                f'netsh advfirewall firewall delete rule name="{rule}_in"',
            ]
        for cmd in cmds:
            r = subprocess.run(['powershell','-NoProfile','-Command', cmd], capture_output=True, text=True, creationflags=0x08000000)
            print(f'[fw] {cmd}: {r.stdout.strip() or r.stderr.strip()}')

    def _fw_unblock_by_name(self, proc_name):
        import subprocess
        rule = f'NSH_BLOCK_{proc_name}'
        for r_name in [rule, f'{rule}_in']:
            cmd = f'netsh advfirewall firewall delete rule name="{r_name}"'
            r = subprocess.run(['powershell','-NoProfile','-Command', cmd], capture_output=True, text=True, creationflags=0x08000000)
            print(f'[fw] {cmd}: {r.stdout.strip() or r.stderr.strip()}')

    def _sync_blocked(self):
        new_blocked = set()
        exe_map = {}
        with self.stats.lock:
            for d in self.stats.proc_data.values():
                if d['exe']: exe_map[d['name']] = d['exe']
        for i in range(self.tree.topLevelItemCount()):
            r = self.tree.topLevelItem(i)
            if r.checkState(6) == Qt.CheckState.Checked: new_blocked.add(r.text(1))
        if new_blocked == self.blocked_names: return
        for n in new_blocked - self.blocked_names:
            if n in exe_map: self.blocked_exe[n] = exe_map[n]; threading.Thread(target=self._fw_block, args=(exe_map[n], True), daemon=True).start()
        for n in self.blocked_names - new_blocked:
            self.blocked_exe.pop(n, None)
            threading.Thread(target=self._fw_unblock_by_name, args=(n,), daemon=True).start()
        self.blocked_names = new_blocked
        save_blocked_json(self.blocked_exe)

    def reset_db(self):
        self.db.reset()
        with self.stats.lock:
            self.stats.proc_data.clear()
            self.stats.db_totals.clear()
            self.stats.sys_dl_total = 0; self.stats.sys_ul_total = 0
        # unblock all and clear json
        for n in list(self.blocked_names):
            threading.Thread(target=self._fw_unblock_by_name, args=(n,), daemon=True).start()
        self.blocked_names.clear(); self.blocked_exe.clear()
        save_blocked_json({})
        self.tree.clear()

    def show_settings(self):
        curr = {'unit':self.unit,'win_w':self.width(),'win_h':self.height(),'row_height':self.row_height,
                'col_weights':self.col_weights,'hi_enabled':self.hi_enabled,'hi_color':self.hi_color,
                'hi_thickness':self.hi_thickness,'hi_dl_s':self.hi_dl_s,'hi_ul_s':self.hi_ul_s,
                'hi_dl_t':self.hi_dl_t,'hi_ul_t':self.hi_ul_t,'filter_presets':self.filter_presets,
                'minimize_to_tray':self.minimize_to_tray}
        dlg = SettingsDialog(self, curr)
        if dlg.exec():
            ns = dlg.get_settings()
            self.unit=ns['unit']; self.row_height=ns['row_height']; self.resize(ns['win_w'],ns['win_h'])
            self.hi_enabled=ns['hi_enabled']; self.hi_color=ns['hi_color']; self.hi_thickness=ns['hi_thickness']
            self.hi_dl_s=ns['hi_dl_s']; self.hi_ul_s=ns['hi_ul_s']; self.hi_dl_t=ns['hi_dl_t']; self.hi_ul_t=ns['hi_ul_t']
            self.col_weights=ns['col_weights']; self.filter_presets=ns['filter_presets']
            self.minimize_to_tray=ns['minimize_to_tray']
            self._rebuild_filter_combo()
            self.apply_delegate_settings()
            self._apply_col_widths()
            self.save_settings(); self.restart_app()

    def restart_app(self):
        self.monitor.running = False; os.execl(sys.executable, sys.executable, *sys.argv)

    def closeEvent(self, e):
        if self.minimize_to_tray:
            e.ignore()
            self.hide()
        else:
            self.full_exit()


if __name__ == "__main__":
    app = QApplication(sys.argv); window = App(); window.show(); sys.exit(app.exec())