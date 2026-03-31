import sys, os, psutil, socket, threading, time, json, sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView,
                             QGroupBox, QDialog, QSpinBox, QFormLayout, QScrollArea, QComboBox, QLineEdit,
                             QCheckBox, QStyledItemDelegate, QColorDialog, QSizePolicy, QFileIconProvider)
from PyQt6.QtCore import Qt, QTimer, QSize, QRectF, QFileInfo
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont, QPainter, QPen
import pydivert

CP_BG="#050505"; CP_PANEL="#111111"; CP_YELLOW="#FCEE0A"; CP_CYAN="#00F0FF"
CP_RED="#FF003C"; CP_GREEN="#00ff21"; CP_ORANGE="#ff934b"; CP_DIM="#3a3a3a"
CP_TEXT="#E0E0E0"; CP_SUBTEXT="#808080"

SETTINGS_DIR = r"C:\@delta\output\net_speed_monitor"
SETTINGS_FILE = os.path.join(SETTINGS_DIR, "settings.json")
DB_FILE = os.path.join(SETTINGS_DIR, "traffic.db")

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
        if col in [2,3,4,5]:
            try: return float(self.data(col, Qt.ItemDataRole.UserRole) or 0) < float(other.data(col, Qt.ItemDataRole.UserRole) or 0)
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
        self.filter_presets = QLineEdit(current_settings.get('filter_presets','0,1024,10240,102400,1048576'))
        self.filter_presets.setPlaceholderText('e.g. 0,1024,10240,102400')
        ff.addRow("PRESETS (B/s):", self.filter_presets); fg.setLayout(ff); layout.addWidget(fg)

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
            'filter_presets': self.filter_presets.text()
        }



class TrafficDB:
    def __init__(self):
        os.makedirs(SETTINGS_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS traffic (name TEXT PRIMARY KEY, dl_total INTEGER DEFAULT 0, ul_total INTEGER DEFAULT 0)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS blocked (name TEXT PRIMARY KEY)")
        self.conn.commit()

    def load(self):
        rows = self.conn.execute("SELECT name, dl_total, ul_total FROM traffic").fetchall()
        return {r[0]: (r[1], r[2]) for r in rows}

    def load_blocked(self):
        return {r[0] for r in self.conn.execute("SELECT name FROM blocked").fetchall()}

    def save_batch(self, data):
        self.conn.executemany("INSERT INTO traffic(name,dl_total,ul_total) VALUES(?,?,?) ON CONFLICT(name) DO UPDATE SET dl_total=excluded.dl_total, ul_total=excluded.ul_total", data)
        self.conn.commit()

    def set_blocked(self, name, blocked):
        if blocked: self.conn.execute("INSERT OR IGNORE INTO blocked(name) VALUES(?)", (name,))
        else: self.conn.execute("DELETE FROM blocked WHERE name=?", (name,))
        self.conn.commit()

    def reset(self):
        self.conn.execute("DELETE FROM traffic"); self.conn.execute("DELETE FROM blocked"); self.conn.commit()

class MonitorStats:
    def __init__(self, db):
        self.lock = threading.Lock(); self.db = db
        self.proc_data = {}  # pid -> {name, exe, sent_total, recv_total, sent_curr, recv_curr}
        self.sys_dl_total = 0; self.sys_ul_total = 0
        self.sys_dl_curr = 0; self.sys_ul_curr = 0
        # pre-load totals from DB (keyed by name, merged into proc_data when PID seen)
        self.db_totals = {}
        for name, (dl, ul) in db.load().items():
            if name == '[SYSTEM/OTHER/VPN]': self.sys_dl_total = dl; self.sys_ul_total = ul
            else: self.db_totals[name] = (dl, ul)

    def update_packet(self, pid, size, direction):
        with self.lock:
            if pid is None:
                if direction == 'recv': self.sys_dl_curr += size; self.sys_dl_total += size
                else: self.sys_ul_curr += size; self.sys_ul_total += size
                return
            if pid not in self.proc_data:
                try: p = psutil.Process(pid); name = p.name(); exe = p.exe()
                except: name = f"PID {pid}"; exe = ""
                dl0, ul0 = self.db_totals.pop(name, (0, 0))
                self.proc_data[pid] = {'name': name, 'exe': exe, 'sent_total':ul0, 'recv_total':dl0, 'sent_curr':0, 'recv_curr':0}
            d = self.proc_data[pid]
            if direction == 'sent': d['sent_total'] += size; d['sent_curr'] += size
            else: d['recv_total'] += size; d['recv_curr'] += size

    def get_snapshot(self):
        with self.lock:
            snap = []
            for pid, d in self.proc_data.items():
                dl = d['recv_curr']; ul = d['sent_curr']; d['recv_curr'] = 0; d['sent_curr'] = 0
                snap.append({'pid': pid, 'name': d['name'], 'exe': d['exe'],
                             'dl_speed': dl, 'ul_speed': ul, 'dl_total': d['recv_total'], 'ul_total': d['sent_total']})
            # include DB-only entries (not yet active this session)
            for name, (dl, ul) in self.db_totals.items():
                snap.append({'pid': -1, 'name': name, 'exe': '', 'dl_speed': 0, 'ul_speed': 0, 'dl_total': dl, 'ul_total': ul})
            snap.append({'pid': 0, 'name': '[SYSTEM/OTHER/VPN]', 'exe': '',
                         'dl_speed': self.sys_dl_curr, 'ul_speed': self.sys_ul_curr,
                         'dl_total': self.sys_dl_total, 'ul_total': self.sys_ul_total})
            self.sys_dl_curr = 0; self.sys_ul_curr = 0
            dl_t = sum(e['dl_speed'] for e in snap); ul_t = sum(e['ul_speed'] for e in snap)
            return snap, dl_t, ul_t


class NetworkThread(threading.Thread):
    """Capture thread using pydivert — gets PID directly from WinDivert/WFP."""
    def __init__(self, stats):
        super().__init__(); self.stats = stats; self.daemon = True; self.running = True
        self._local_ips = self._get_local_ips()
        # port -> pid cache, refreshed every 500ms
        self._conn_map = {}; self._conn_lock = threading.Lock()
        threading.Thread(target=self._refresh_conns, daemon=True).start()

    def _get_local_ips(self):
        ips = set()
        for _, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET: ips.add(a.address)
        return ips

    def _refresh_conns(self):
        while self.running:
            m = {}
            try:
                for c in psutil.net_connections(kind='inet'):
                    if c.laddr and c.pid: m[(c.laddr.ip, c.laddr.port)] = c.pid
            except: pass
            with self._conn_lock: self._conn_map = m
            time.sleep(0.2)  # 200ms — tighter than scapy version

    def _get_pid(self, packet):
        # pydivert provides process_id directly on Windows for outbound packets
        if hasattr(packet, 'process_id') and packet.process_id:
            return packet.process_id
        # fallback: port lookup
        with self._conn_lock:
            src_ip = packet.ipv4.src_addr if packet.ipv4 else None
            dst_ip = packet.ipv4.dst_addr if packet.ipv4 else None
            sport = dport = 0
            if packet.tcp: sport = packet.tcp.src_port; dport = packet.tcp.dst_port
            elif packet.udp: sport = packet.udp.src_port; dport = packet.udp.dst_port
            return self._conn_map.get((src_ip, sport)) or self._conn_map.get((dst_ip, dport))

    def run(self):
        # NETWORK layer, outbound+inbound, no loopback — read-only (no re-inject needed for monitoring)
        self.blocked_pids = set()
        try:
            with pydivert.WinDivert("ip", layer=pydivert.Layer.NETWORK) as w:
                for packet in w:
                    if not self.running: break
                    pid = self._get_pid(packet)
                    if pid is None and not packet.is_outbound:
                        with self._conn_lock:
                            dport = packet.tcp.dst_port if packet.tcp else (packet.udp.dst_port if packet.udp else 0)
                            dst_ip = packet.ipv4.dst_addr if packet.ipv4 else None
                            pid = self._conn_map.get((dst_ip, dport))
                    if pid in self.blocked_pids: continue  # drop — don't re-inject
                    w.send(packet)  # re-inject allowed packets
                    size = len(packet.raw)
                    direction = 'sent' if packet.is_outbound else 'recv'
                    self.stats.update_packet(pid, size, direction)
        except Exception as e:
            print(f"[pydivert error] {e}")


class App(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("NET-SPEED HOOKER // WinDivert")
        self.load_settings(); self.resize(self.win_w, self.win_h)
        self.db = TrafficDB(); self.blocked_names = self.db.load_blocked()
        self.stats = MonitorStats(self.db); self.monitor = NetworkThread(self.stats); self.monitor.start()
        self.icon_cache = {}; self.icon_provider = QFileIconProvider()
        self.init_ui(); self.timer = QTimer(); self.timer.timeout.connect(self.update_stats); self.timer.start(1000)

    def load_settings(self):
        self.win_w=1000; self.win_h=700; self.row_height=40; self.col_weights=[5,22,16,16,14,14,13]
        self.current_sort_col=2; self.current_sort_order=Qt.SortOrder.DescendingOrder
        self.unit="MB/s"; self.show_dl=True; self.show_ul=True
        self.hi_enabled=True; self.hi_color=CP_CYAN; self.hi_thickness=2
        self.hi_dl_s=True; self.hi_ul_s=True; self.hi_dl_t=True; self.hi_ul_t=True
        self.min_speed=0; self.filter_presets='0,1024,10240,102400,1048576'
        try:
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE) as f: s = json.load(f)
                self.win_w=s.get('win_w',1000); self.win_h=s.get('win_h',700); self.row_height=s.get('row_height',40)
                self.col_weights=s.get('col_weights',[5,25,18,18,17,17])
                self.current_sort_col=s.get('sort_col',2); self.current_sort_order=Qt.SortOrder(s.get('sort_order',1))
                self.unit=s.get('unit','MB/s'); self.show_dl=s.get('show_dl',True); self.show_ul=s.get('show_ul',True)
                self.hi_enabled=s.get('hi_enabled',True); self.hi_color=s.get('hi_color',CP_CYAN)
                self.hi_thickness=s.get('hi_thickness',2)
                self.hi_dl_s=s.get('hi_dl_s',True); self.hi_ul_s=s.get('hi_ul_s',True)
                self.hi_dl_t=s.get('hi_dl_t',True); self.hi_ul_t=s.get('hi_ul_t',True)
                self.min_speed=s.get('min_speed',0); self.filter_presets=s.get('filter_presets','0,1024,10240,102400,1048576')
        except: pass

    def save_settings(self):
        try:
            os.makedirs(SETTINGS_DIR, exist_ok=True)
            s = {'unit':self.unit,'win_w':self.width(),'win_h':self.height(),'row_height':self.row_height,
                 'col_weights':self.col_weights,'sort_col':self.current_sort_col,'sort_order':self.current_sort_order.value,
                 'show_dl':self.show_dl,'show_ul':self.show_ul,'hi_enabled':self.hi_enabled,'hi_color':self.hi_color,
                 'hi_thickness':self.hi_thickness,'hi_dl_s':self.hi_dl_s,'hi_ul_s':self.hi_ul_s,
                 'hi_dl_t':self.hi_dl_t,'hi_ul_t':self.hi_ul_t,'min_speed':int(self.filter_combo.currentText()) if hasattr(self,'filter_combo') and self.filter_combo.currentText().isdigit() else self.min_speed,'filter_presets':self.filter_presets}
            with open(SETTINGS_FILE,'w') as f: json.dump(s, f, indent=4)
        except: pass

    def init_ui(self):
        self.setStyleSheet(f"QMainWindow{{background-color:{CP_BG};}} QWidget{{color:{CP_TEXT};font-family:'Consolas';font-size:10pt;}} QTreeWidget{{background-color:{CP_PANEL};border:1px solid {CP_DIM};color:{CP_TEXT};outline:none;show-decoration-selected:0;}} QTreeWidget::item{{border-bottom:1px solid {CP_DIM};padding:4px;}} QTreeWidget::item:hover{{background-color:#1a1a1a;}} QTreeWidget::item:selected{{background-color:{CP_DIM};color:{CP_YELLOW};outline:none;}} QHeaderView::section{{background-color:{CP_DIM};color:{CP_YELLOW};padding:5px;border:1px solid {CP_BG};font-weight:bold;}} QPushButton{{background-color:{CP_DIM};border:1px solid {CP_DIM};color:white;padding:6px 12px;font-weight:bold;}} QPushButton:hover{{background-color:#2a2a2a;border:1px solid {CP_YELLOW};color:{CP_YELLOW};}} QCheckBox{{color:{CP_CYAN};font-weight:bold;}}")
        c = QWidget(); self.setCentralWidget(c); l = QVBoxLayout(c); ht = QHBoxLayout()
        t = QLabel("NET-SPEED HOOKER // WinDivert"); t.setStyleSheet(f"color:{CP_CYAN};font-size:16pt;font-weight:bold;"); ht.addWidget(t)
        self.cb_dl = QCheckBox("DOWNLOAD"); self.cb_dl.setChecked(self.show_dl); self.cb_dl.stateChanged.connect(self.toggle_cols)
        self.cb_ul = QCheckBox("UPLOAD"); self.cb_ul.setChecked(self.show_ul); self.cb_ul.stateChanged.connect(self.toggle_cols)
        ht.addStretch()
        fl = QLabel("MIN SPEED:"); fl.setStyleSheet(f"color:{CP_DIM};font-size:9pt;"); ht.addWidget(fl)
        self.filter_combo = QComboBox(); self.filter_combo.setFixedWidth(110)
        self.filter_combo.setStyleSheet(f'QComboBox{{background-color:{CP_PANEL};color:{CP_CYAN};border:1px solid {CP_DIM};padding:2px;}}')
        self._rebuild_filter_combo()
        ht.addWidget(self.filter_combo)
        ht.addWidget(self.cb_dl); ht.addWidget(self.cb_ul)
        self.tl = QLabel("DL: 0.00 | UL: 0.00"); self.tl.setStyleSheet(f"color:{CP_YELLOW};font-weight:bold;font-size:10pt;border:1px solid {CP_DIM};padding:5px;"); ht.addWidget(self.tl); l.addLayout(ht)
        hb = QHBoxLayout(); hb.addStretch()
        dbb = QPushButton("RESET DB"); dbb.clicked.connect(self.reset_db); hb.addWidget(dbb)
        rb = QPushButton("RESTART"); rb.clicked.connect(self.restart_app); hb.addWidget(rb)
        sb = QPushButton("SETTINGS"); sb.clicked.connect(self.show_settings); hb.addWidget(sb); l.addLayout(hb)
        self.tree = QTreeWidget(); self.tree.setColumnCount(7)
        self.tree.setHeaderLabels(["ICON","APPLICATION","DL SPEED","UL SPEED","TOTAL DL","TOTAL UL","BLOCK"])
        self.tree.setIndentation(20); self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.delegate = CustomBorderDelegate(self.tree); self.apply_delegate_settings(); self.tree.setItemDelegate(self.delegate)
        self.tree.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        QTimer.singleShot(0, self._apply_col_widths)
        self.tree.setSortingEnabled(True)
        self.tree.header().sortIndicatorChanged.connect(self.on_sort_changed)
        self.tree.header().setSortIndicator(self.current_sort_col, self.current_sort_order); l.addWidget(self.tree)
        self.fl = QLabel(f"STATUS: MONITORING_ACTIVE // ENGINE: WinDivert // UNIT: {self.unit}")
        self.fl.setStyleSheet(f"color:{CP_DIM};font-size:8pt;"); l.addWidget(self.fl); self.toggle_cols()


    def _rebuild_filter_combo(self):
        cur = self.filter_combo.currentText() if hasattr(self,'filter_combo') else str(self.min_speed)
        self.filter_combo.blockSignals(True); self.filter_combo.clear()
        for v in self.filter_presets.split(','):
            v=v.strip()
            if v.isdigit(): self.filter_combo.addItem(v)
        idx = self.filter_combo.findText(cur)
        self.filter_combo.setCurrentIndex(idx if idx>=0 else 0)
        self.filter_combo.blockSignals(False)

    def _apply_col_widths(self):
        self.tree.header().setStretchLastSection(False)
        total = self.tree.viewport().width() or self.win_w
        s = sum(self.col_weights) or 1
        for i, w in enumerate(self.col_weights): self.tree.setColumnWidth(i, int(total * w / s))
        self.tree.header().setStretchLastSection(False)
    def apply_delegate_settings(self):
        self.delegate.settings = {'enabled':self.hi_enabled,'color':self.hi_color,'thickness':self.hi_thickness,
                                  'cols':{2:self.hi_dl_s,3:self.hi_ul_s,4:self.hi_dl_t,5:self.hi_ul_t}}

    def toggle_cols(self):
        self.show_dl = self.cb_dl.isChecked(); self.show_ul = self.cb_ul.isChecked()
        self.tree.setColumnHidden(2, not self.show_dl); self.tree.setColumnHidden(4, not self.show_dl)
        self.tree.setColumnHidden(3, not self.show_ul); self.tree.setColumnHidden(5, not self.show_ul)
        self.save_settings()

    def on_sort_changed(self, i, o): self.current_sort_col = i; self.current_sort_order = o; self.save_settings()

    def update_stats(self):
        snap, dl_t, ul_t = self.stats.get_snapshot()
        self.tl.setText(f"DL: {format_size(dl_t, self.unit)} | UL: {format_size(ul_t, self.unit)}")
        groups = {}; max_v = {2:0, 3:0, 4:0, 5:0}
        for d in snap:
            n = d['name']
            if n not in groups: groups[n] = {'dl_s':0,'ul_s':0,'dl_t':0,'ul_t':0,'exe':d['exe'],'items':[]}
            groups[n]['dl_s'] += d['dl_speed']; groups[n]['ul_s'] += d['ul_speed']
            groups[n]['dl_t'] += d['dl_total']; groups[n]['ul_t'] += d['ul_total']
            groups[n]['items'].append(d)
            max_v[2]=max(max_v[2],groups[n]['dl_s']); max_v[3]=max(max_v[3],groups[n]['ul_s'])
            max_v[4]=max(max_v[4],groups[n]['dl_t']); max_v[5]=max(max_v[5],groups[n]['ul_t'])
        self.delegate.max_values = max_v
        self.tree.setSortingEnabled(False)
        exs = {self.tree.topLevelItem(i).text(1): self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())}
        for n, gd in groups.items():
            r = exs[n] if n in exs else TreeItem(self.tree); r.setText(1, n)
            r.setFlags(r.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            r.setCheckState(6, Qt.CheckState.Checked if n in self.blocked_names else Qt.CheckState.Unchecked)
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
            try: _f=int(self.filter_combo.currentText())
            except: _f=0
            r.setHidden(gd['dl_s'] < _f and gd['ul_s'] < _f)
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
        self._save_db(snap)
        self._sync_blocked()

    def _save_db(self, snap):
        groups = {}
        for d in snap:
            n = d['name']
            if n not in groups: groups[n] = [0, 0]
            groups[n][0] += d['dl_total']; groups[n][1] += d['ul_total']
        self.db.save_batch([(n, dl, ul) for n, (dl, ul) in groups.items()])

    def _sync_blocked(self):
        # read checkboxes -> update blocked_names and monitor.blocked_pids
        new_blocked = set()
        for i in range(self.tree.topLevelItemCount()):
            r = self.tree.topLevelItem(i)
            if r.checkState(6) == Qt.CheckState.Checked: new_blocked.add(r.text(1))
        # persist changes
        for n in new_blocked - self.blocked_names: self.db.set_blocked(n, True)
        for n in self.blocked_names - new_blocked: self.db.set_blocked(n, False)
        self.blocked_names = new_blocked
        # update monitor blocked pids
        blocked_pids = set()
        with self.stats.lock:
            for pid, d in self.stats.proc_data.items():
                if d['name'] in self.blocked_names: blocked_pids.add(pid)
        self.monitor.blocked_pids = blocked_pids

    def reset_db(self):
        self.db.reset(); self.blocked_names = set(); self.monitor.blocked_pids = set()
        with self.stats.lock:
            self.stats.proc_data.clear(); self.stats.sys_dl_total = 0; self.stats.sys_ul_total = 0
        self.tree.clear()

    def show_settings(self):
        curr = {'unit':self.unit,'win_w':self.width(),'win_h':self.height(),'row_height':self.row_height,
                'col_weights':self.col_weights,'hi_enabled':self.hi_enabled,'hi_color':self.hi_color,
                'hi_thickness':self.hi_thickness,'hi_dl_s':self.hi_dl_s,'hi_ul_s':self.hi_ul_s,
                'hi_dl_t':self.hi_dl_t,'hi_ul_t':self.hi_ul_t,'filter_presets':self.filter_presets}
        dlg = SettingsDialog(self, curr)
        if dlg.exec():
            ns = dlg.get_settings()
            self.unit=ns['unit']; self.row_height=ns['row_height']; self.resize(ns['win_w'],ns['win_h'])
            self.hi_enabled=ns['hi_enabled']; self.hi_color=ns['hi_color']; self.hi_thickness=ns['hi_thickness']
            self.hi_dl_s=ns['hi_dl_s']; self.hi_ul_s=ns['hi_ul_s']; self.hi_dl_t=ns['hi_dl_t']; self.hi_ul_t=ns['hi_ul_t']
            self.col_weights=ns['col_weights']; self.filter_presets=ns['filter_presets']
            self._rebuild_filter_combo()
            self.apply_delegate_settings()
            self._apply_col_widths()
            self.save_settings(); self.restart_app()

    def restart_app(self):
        self.monitor.running = False; os.execl(sys.executable, sys.executable, *sys.argv)

    def closeEvent(self, e):
        self.monitor.running = False; self.save_settings(); super().closeEvent(e)


if __name__ == "__main__":
    app = QApplication(sys.argv); window = App(); window.show(); sys.exit(app.exec())
