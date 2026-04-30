# mypygui_qt.py — PyQt6 rewrite of the Windows taskbar status bar

import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from queue import Queue, Empty

import psutil
import win32gui
import win32process

try:
    from pyadl import ADLManager
    _HAS_ADL = True
except Exception:
    _HAS_ADL = False

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QDialog, QLineEdit, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QScrollArea, QMessageBox, QInputDialog,
    QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QPainter, QColor, QPen

# ─── ASCII art ────────────────────────────────────────────────────────────────
print(r"""
$$\   $$\           $$\       $$\       $$\ $$\   $$\  $$$$$$\
$$$\  $$ |          $$ |      \__|      $$ |$$$\  $$ |$$  __$$\
$$$$\ $$ | $$$$$$\  $$$$$$$\  $$\  $$$$$$$ |$$$$\ $$ |$$ /  $$ |
$$ $$\$$ | \____$$\ $$  __$$\ $$ |$$  __$$ |$$ $$\$$ |$$$$$$$$ |
$$ \$$$$ | $$$$$$$ |$$ |  $$ |$$ |$$ /  $$ |$$ \$$$$ |$$  __$$ |
$$ |\$$$ |$$  __$$ |$$ |  $$ |$$ |$$ |  $$ |$$ |\$$$ |$$ |  $$ |
$$ | \$$ |\$$$$$$$ |$$ |  $$ |$$ |\$$$$$$$ |$$ | \$$ |$$ |  $$ |
\__|  \__| \_______|\__|  \__|\__| \_______|\__|  \__|\__|  \__|
""")

start_time = time.time()

# ─── Theme ────────────────────────────────────────────────────────────────────
CP_BG     = "#050505"
CP_PANEL  = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN   = "#00F0FF"
CP_RED    = "#FF003C"
CP_GREEN  = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM    = "#3a3a3a"
CP_TEXT   = "#E0E0E0"

GLOBAL_QSS = f"""
QMainWindow, QWidget {{
    background-color: {CP_BG};
    color: {CP_TEXT};
    font-family: "JetBrainsMono NFP";
    font-size: 10pt;
}}
QPushButton {{
    background-color: {CP_DIM};
    color: {CP_TEXT};
    border: none;
    padding: 2px 6px;
}}
QPushButton:hover {{
    border: 1px solid {CP_YELLOW};
    color: {CP_YELLOW};
}}
QPushButton:pressed {{
    background-color: {CP_YELLOW};
    color: black;
}}
QLabel {{
    background: transparent;
    color: {CP_TEXT};
    margin: 0px;
    padding: 0px;
}}
"""

DIALOG_QSS = f"""
    QDialog, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
    QLineEdit, QComboBox, QSpinBox {{
        background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
    }}
    QLineEdit:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
    QComboBox QAbstractItemView {{ background: {CP_PANEL}; color: {CP_CYAN}; selection-background-color: {CP_CYAN}; selection-color: {CP_BG}; }}
    QPushButton {{
        background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 14px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
    QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
    QPushButton#btn_save {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}
    QPushButton#btn_save:hover {{ background-color: {CP_GREEN}; color: black; }}
    QPushButton#btn_delete {{ border-color: {CP_RED}; color: {CP_RED}; }}
    QPushButton#btn_delete:hover {{ background-color: {CP_RED}; color: white; }}
    QGroupBox {{
        border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 8px; font-weight: bold; color: {CP_YELLOW};
    }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
    QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
    QCheckBox::indicator {{ width: 13px; height: 13px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
    QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
    QScrollArea {{ background: transparent; border: none; }}
    QScrollBar:vertical {{ background: {CP_BG}; width: 8px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 4px; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; background: none; }}
    QLabel#section_label {{ color: {CP_YELLOW}; font-weight: bold; font-size: 9pt; }}
"""

# ─── Config ───────────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mypygui_config.json")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# ─── Helpers ──────────────────────────────────────────────────────────────────
def run_command(command, admin=False, hide=False, no_exit=True):
    if admin:
        try:
            executable = "pwsh"
            args = f"{'-NoExit ' if no_exit else ''}-Command \"{command}\""
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, args, None, 1 if not hide else 0)
        except Exception as e:
            print(f"Admin run_command failed: {e}")
        return
    if hide:
        subprocess.Popen(["pwsh", "-Command", command], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        cmd_list = ["start", "pwsh"]
        if no_exit:
            cmd_list.append("-NoExit")
        cmd_list.extend(["-Command", command])
        subprocess.Popen(" ".join(cmd_list), shell=True)

def handle_action(action_cfg):
    if not action_cfg:
        return
    atype  = action_cfg.get("type")
    cmd    = action_cfg.get("cmd")
    cwd    = action_cfg.get("cwd")
    admin  = action_cfg.get("admin", False)
    hide   = action_cfg.get("hide", False)
    if admin:
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas",
                sys.executable if atype == "python" else "cmd.exe",
                f"/c {cmd}" if atype != "python" else cmd,
                cwd, 0 if hide else 1
            )
        except Exception as e:
            print(f"Admin launch failed: {e}")
        return
    flags = subprocess.CREATE_NO_WINDOW if hide else 0
    if atype == "subprocess":
        subprocess.Popen(cmd, cwd=cwd, shell=True, creationflags=flags)
    elif atype == "run_command":
        run_command(cmd)
    elif atype == "python":
        subprocess.Popen([sys.executable, cmd], cwd=cwd, creationflags=flags)
    elif atype == "function":
        func_name = action_cfg.get("func")
        if func_name == "restart":      _app_restart()
        elif func_name == "close_window": _app_close()
        elif func_name == "force_shutdown": force_shutdown()
        elif func_name == "force_restart":  force_restart()

def _app_close():
    QApplication.instance().quit()

def _app_restart():
    subprocess.Popen([sys.executable] + sys.argv)
    QApplication.instance().quit()

def force_shutdown():
    r = QMessageBox.question(None, "Shutdown", "Are you sure you want to shutdown?")
    if r == QMessageBox.StandardButton.Yes:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])

def force_restart():
    r = QMessageBox.question(None, "Restart", "Are you sure you want to restart?")
    if r == QMessageBox.StandardButton.Yes:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])

def calculate_time_to_appear(t0):
    print(f"Time taken to appear: {time.time() - t0:.2f} seconds")

# ─── System info ──────────────────────────────────────────────────────────────
def get_cpu_ram_info():
    return psutil.cpu_percent(interval=None), psutil.virtual_memory().percent

def get_gpu_usage():
    if not _HAS_ADL:
        return 0
    try:
        return ADLManager.getInstance().getDevices()[0].getCurrentUsage()
    except Exception:
        return 0

def get_disk_info():
    return psutil.disk_usage('C:').percent, psutil.disk_usage('D:').percent

_net_last = {"sent": 0, "recv": 0}

def get_net_speed():
    io = psutil.net_io_counters()
    up   = (io.bytes_sent - _net_last["sent"]) / (1024 * 1024)
    down = (io.bytes_recv - _net_last["recv"]) / (1024 * 1024)
    _net_last["sent"] = io.bytes_sent
    _net_last["recv"] = io.bytes_recv
    return f"{up:.2f}", f"{down:.2f}"

def get_system_uptime():
    uptime = datetime.now().timestamp() - psutil.boot_time()
    h, rem = divmod(uptime, 3600)
    m, s   = divmod(rem, 60)
    return int(h), int(m), int(s)

def format_uptime():
    h, m, s = get_system_uptime()
    return f"\udb81\udf8c {h:02d}:{m:02d}:{s:02d}"


# ─── Edit GUI dialog ──────────────────────────────────────────────────────────
def open_edit_gui(item_cfg, category, index=None):
    dlg = QDialog(_main_window if "_main_window" in globals() else None)
    dlg.setWindowTitle(f"Edit — {item_cfg.get('id', 'Item')}")
    dlg.resize(1000, 620)
    dlg.setStyleSheet(DIALOG_QSS)
    dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
    screen = QApplication.primaryScreen().geometry()
    dlg.move(screen.center().x() - 500, screen.center().y() - 310)

    root_layout = QVBoxLayout(dlg)
    root_layout.setContentsMargins(10, 10, 10, 10)
    root_layout.setSpacing(8)

    title = QLabel(f"// EDIT :: {item_cfg.get('id', 'ITEM').upper()}")
    title.setStyleSheet(f"color: {CP_CYAN}; font-size: 13pt; font-weight: bold; padding: 4px 0;")
    root_layout.addWidget(title)

    panels = QHBoxLayout()
    panels.setSpacing(10)
    root_layout.addLayout(panels)

    # Left panel
    left_scroll = QScrollArea(); left_scroll.setWidgetResizable(True)
    left_w = QWidget(); left_layout = QVBoxLayout(left_w)
    left_layout.setSpacing(6); left_layout.setContentsMargins(6, 6, 6, 6)
    left_scroll.setWidget(left_w); panels.addWidget(left_scroll, 1)

    grp_appear = QGroupBox("APPEARANCE"); form_appear = QFormLayout(); form_appear.setSpacing(6); grp_appear.setLayout(form_appear)
    entries = {}
    for field in ["text", "fg", "bg", "id"]:
        ent = QLineEdit(str(item_cfg.get(field, ""))); form_appear.addRow(field.upper(), ent); entries[field] = ent
    border_px_le = QLineEdit(str(item_cfg.get("border", 0))); border_px_le.setFixedWidth(50)
    border_color_le = QLineEdit(str(item_cfg.get("border_color", "")))
    form_appear.addRow("BORDER PX", border_px_le)
    form_appear.addRow("BORDER COLOR", border_color_le)
    left_layout.addWidget(grp_appear)

    grp_font = QGroupBox("FONT"); form_font = QFormLayout(); form_font.setSpacing(6); grp_font.setLayout(form_font)
    cur_font = item_cfg.get("font", ["JetBrainsMono NFP", 16, "bold"])
    font_families = ["JetBrainsMono NFP", "JetBrainsMono NF", "Jetbrainsmono nfp", "Arial", "Consolas", "Courier New", "Segoe UI"]
    font_family_cb = QComboBox(); font_family_cb.addItems(font_families)
    font_family_cb.setCurrentText(cur_font[0] if cur_font else "JetBrainsMono NFP")
    font_size_le = QLineEdit(str(cur_font[1]) if len(cur_font) > 1 else "16"); font_size_le.setFixedWidth(60)
    font_weight_cb = QComboBox(); font_weight_cb.addItems(["bold", "normal"])
    font_weight_cb.setCurrentText(cur_font[2] if len(cur_font) > 2 else "bold")
    form_font.addRow("FAMILY", font_family_cb); form_font.addRow("SIZE", font_size_le); form_font.addRow("WEIGHT", font_weight_cb)
    left_layout.addWidget(grp_font)

    grp_pad = QGroupBox("PADDING"); form_pad = QFormLayout(); form_pad.setSpacing(6); grp_pad.setLayout(form_pad)
    padx_left_le  = QLineEdit(str(item_cfg.get("padx_left", 1)));  padx_left_le.setFixedWidth(60)
    padx_right_le = QLineEdit(str(item_cfg.get("padx_right", 1))); padx_right_le.setFixedWidth(60)
    form_pad.addRow("PADX LEFT", padx_left_le); form_pad.addRow("PADX RIGHT", padx_right_le)
    left_layout.addWidget(grp_pad)

    grp_place = QGroupBox("PLACEMENT"); form_place = QFormLayout(); form_place.setSpacing(6); grp_place.setLayout(form_place)
    group_cb = QComboBox(); group_cb.addItems(["buttons_left", "buttons_right"])
    group_cb.setCurrentText(category if category in ["buttons_left", "buttons_right"] else "buttons_left")
    config_now = load_config()
    cur_list = config_now.get(group_cb.currentText(), [])
    index_le = QLineEdit(str(index if index is not None else max(len(cur_list) - 1, 0))); index_le.setFixedWidth(60)
    def _on_group_changed(text):
        lst = config_now.get(text, [])
        index_le.setText(str(max(len(lst) - 1, 0)))
    group_cb.currentTextChanged.connect(_on_group_changed)
    form_place.addRow("GROUP", group_cb); form_place.addRow("INDEX", index_le)
    left_layout.addWidget(grp_place); left_layout.addStretch()

    # Right panel
    right_scroll = QScrollArea(); right_scroll.setWidgetResizable(True)
    right_w = QWidget(); right_layout = QVBoxLayout(right_w)
    right_layout.setSpacing(6); right_layout.setContentsMargins(6, 6, 6, 6)
    right_scroll.setWidget(right_w); panels.addWidget(right_scroll, 2)

    click_types = [("LEFT CLICK", "Button-1"), ("RIGHT CLICK", "Button-3"),
                   ("CTRL + LEFT", "Control-Button-1"), ("CTRL + RIGHT", "Control-Button-3")]
    binding_inputs = {}
    for label_text, bkey in click_types:
        grp = QGroupBox(label_text); form = QFormLayout(); form.setSpacing(4); grp.setLayout(form)
        bcfg = item_cfg.get("bindings", {}).get(bkey, {})
        cmd_le   = QLineEdit(bcfg.get("cmd", bcfg.get("func", "")))
        type_cb  = QComboBox(); type_cb.addItems(["subprocess", "run_command", "python", "function"])
        type_cb.setCurrentText(bcfg.get("type", "subprocess"))
        hide_chk  = QCheckBox("Hide Terminal"); hide_chk.setChecked(bcfg.get("hide", False))
        admin_chk = QCheckBox("Run as Admin");  admin_chk.setChecked(bcfg.get("admin", False))
        chk_row = QWidget(); chk_layout = QHBoxLayout(chk_row); chk_layout.setContentsMargins(0,0,0,0)
        chk_layout.addWidget(hide_chk); chk_layout.addWidget(admin_chk); chk_layout.addStretch()
        form.addRow("CMD", cmd_le); form.addRow("TYPE", type_cb); form.addRow("", chk_row)
        right_layout.addWidget(grp)
        binding_inputs[bkey] = {"cmd": cmd_le, "type": type_cb, "hide": hide_chk, "admin": admin_chk}
    right_layout.addStretch()

    btn_row = QHBoxLayout()
    btn_save   = QPushButton("SAVE");   btn_save.setObjectName("btn_save")
    btn_delete = QPushButton("DELETE"); btn_delete.setObjectName("btn_delete")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_row.addWidget(btn_save); btn_row.addWidget(btn_delete)
    root_layout.addLayout(btn_row)

    def save():
        for field in ["text", "fg", "bg", "id"]:
            item_cfg[field] = entries[field].text()
        try:
            item_cfg["font"] = [font_family_cb.currentText(), int(font_size_le.text()), font_weight_cb.currentText()]
        except ValueError: pass
        try: item_cfg["padx_left"]  = int(padx_left_le.text())
        except ValueError: pass
        try: item_cfg["padx_right"] = int(padx_right_le.text())
        except ValueError: pass
        new_bindings = {}
        for bkey, inputs in binding_inputs.items():
            cmd = inputs["cmd"].text()
            if not cmd: continue
            b_type = inputs["type"].currentText()
            new_bindings[bkey] = {"type": b_type, "hide": inputs["hide"].isChecked(), "admin": inputs["admin"].isChecked()}
            if b_type == "function": new_bindings[bkey]["func"] = cmd
            else:                    new_bindings[bkey]["cmd"]  = cmd
        item_cfg["bindings"] = new_bindings
        new_category = group_cb.currentText()
        try: new_index = int(index_le.text())
        except ValueError: new_index = None
        config = load_config()
        if category != new_category and category in config and isinstance(config[category], list) and index is not None:
            if 0 <= index < len(config[category]):
                config[category].pop(index)
        target = config.get(new_category, [])
        if isinstance(target, list):
            if category == new_category and index is not None and 0 <= index < len(target):
                target.pop(index)
            if new_index is not None and 0 <= new_index <= len(target):
                target.insert(new_index, item_cfg)
            else:
                target.append(item_cfg)
            config[new_category] = target
        else:
            config[new_category][item_cfg["id"]] = item_cfg
        save_config(config)
        dlg.accept()
        r = QMessageBox.question(None, "Restart", "Settings saved. Restart GUI to apply?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            _app_restart()

    def delete():
        r = QMessageBox.question(None, "Delete", f"Delete '{item_cfg.get('id', 'this item')}'?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r != QMessageBox.StandardButton.Yes: return
        config = load_config()
        if category in config:
            if isinstance(config[category], list):
                if index is not None and 0 <= index < len(config[category]):
                    config[category].pop(index)
                else:
                    item_id = item_cfg.get("id")
                    config[category] = [i for i in config[category] if i.get("id") != item_id]
            else:
                item_id = item_cfg.get("id")
                if item_id in config[category]:
                    del config[category][item_id]
        save_config(config)
        dlg.accept()
        r = QMessageBox.question(None, "Restart", "Item deleted. Restart GUI to apply?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r == QMessageBox.StandardButton.Yes:
            _app_restart()

    btn_save.clicked.connect(save)
    btn_delete.clicked.connect(delete)
    dlg.show()


# ─── Rclone settings dialog ───────────────────────────────────────────────────
def open_rclone_settings():
    dlg = QDialog()
    dlg.setWindowTitle("Rclone Settings")
    dlg.resize(380, 200)
    dlg.setStyleSheet(DIALOG_QSS)
    dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    layout = QVBoxLayout(dlg); layout.setContentsMargins(14, 14, 14, 14); layout.setSpacing(10)
    title = QLabel("// RCLONE SETTINGS")
    title.setStyleSheet(f"color: {CP_CYAN}; font-size: 12pt; font-weight: bold;")
    layout.addWidget(title)
    grp = QGroupBox("CHECK BEHAVIOUR"); form = QFormLayout(); form.setSpacing(8); grp.setLayout(form)
    cfg_now = load_config().get("rclone_settings", {"interval_min": 10, "simultaneous": True})
    interval_le = QLineEdit(str(cfg_now.get("interval_min", 10)))
    simul_chk   = QCheckBox("Run simultaneously"); simul_chk.setChecked(bool(cfg_now.get("simultaneous", True)))
    form.addRow("INTERVAL (min)", interval_le); form.addRow("", simul_chk)
    layout.addWidget(grp)
    btn_save = QPushButton("SAVE"); btn_save.setObjectName("btn_save")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor); layout.addWidget(btn_save)
    def save():
        try: mins = int(interval_le.text())
        except ValueError: mins = 10
        config = load_config()
        config["rclone_settings"] = {"interval_min": mins, "simultaneous": simul_chk.isChecked()}
        save_config(config)
        dlg.accept()
    btn_save.clicked.connect(save)
    dlg.show()


# ─── Dynamic button factory ───────────────────────────────────────────────────
def create_dynamic_button(parent_layout, btn_cfg, category, index=None):
    """Creates a QLabel-based button and adds it to parent_layout (QHBoxLayout)."""
    _fg   = btn_cfg.get("fg", "") or "white"
    _bg   = btn_cfg.get("bg", "") or CP_BG
    text  = btn_cfg.get("text", "")
    font_cfg = btn_cfg.get("font", ["JetBrainsMono NFP", 16, "bold"])
    px_l  = int(btn_cfg.get("padx_left", 1))
    px_r  = int(btn_cfg.get("padx_right", 1))

    lbl = QLabel(text)
    lbl.setCursor(Qt.CursorShape.PointingHandCursor)
    font_size   = font_cfg[1] if len(font_cfg) > 1 else 16
    font_weight = font_cfg[2] if len(font_cfg) > 2 else "bold"
    bold = "bold" if font_weight == "bold" else "normal"
    _border_px = int(btn_cfg.get("border", 0))
    _border_col = btn_cfg.get("border_color", "") or _bg
    _border_css = f"border: {_border_px}px solid {_border_col};" if _border_px else "border: none;"
    lbl.setStyleSheet(
        f"color: {_fg}; background: {_bg}; font-family: '{font_cfg[0]}'; "
        f"font-size: {font_size}pt; font-weight: {bold}; "
        f"padding-left: {px_l}px; padding-right: {px_r}px; {_border_css}"
    )

    bindings = btn_cfg.get("bindings", {})

    def _make_handler(action):
        return lambda e: handle_action(action)

    def mousePressEvent(event, _bindings=bindings, _cfg=btn_cfg, _cat=category, _idx=index):
        mods = event.modifiers()
        btn  = event.button()
        if mods & Qt.KeyboardModifier.ShiftModifier:
            open_edit_gui(_cfg, _cat, _idx)
            return
        key = None
        if btn == Qt.MouseButton.LeftButton:
            key = "Control-Button-1" if mods & Qt.KeyboardModifier.ControlModifier else "Button-1"
        elif btn == Qt.MouseButton.RightButton:
            key = "Control-Button-3" if mods & Qt.KeyboardModifier.ControlModifier else "Button-3"
        if key and key in _bindings:
            handle_action(_bindings[key])

    lbl.mousePressEvent = mousePressEvent
    parent_layout.addWidget(lbl)
    return lbl


# ─── Static binding helpers ───────────────────────────────────────────────────
def _open_static_edit(key):
    sb   = load_config().get("static_bindings", {})
    item = {"id": key, "text": key, "fg": "", "bg": "", "bindings": sb.get(key, {})}
    open_edit_gui(item, "static_bindings")

def _bind_static(lbl, key, default_cmd):
    """Attach config-driven click handlers to a QLabel."""
    cfg = load_config().get("static_bindings", {}).get(
        key, {"Button-1": {"type": "subprocess", "cmd": default_cmd}}
    )
    def mousePressEvent(event, _cfg=cfg, _key=key):
        mods = event.modifiers()
        btn  = event.button()
        if mods & Qt.KeyboardModifier.ShiftModifier:
            _open_static_edit(_key)
            return
        bkey = None
        if btn == Qt.MouseButton.LeftButton:
            bkey = "Control-Button-1" if mods & Qt.KeyboardModifier.ControlModifier else "Button-1"
        elif btn == Qt.MouseButton.RightButton:
            bkey = "Control-Button-3" if mods & Qt.KeyboardModifier.ControlModifier else "Button-3"
        if bkey and bkey in _cfg:
            handle_action(_cfg[bkey])
    lbl.mousePressEvent = mousePressEvent
    lbl.setCursor(Qt.CursorShape.PointingHandCursor)


# ─── CPU core bar widget ──────────────────────────────────────────────────────
BAR_WIDTH  = 8
BAR_HEIGHT = 25

def _determine_bar_color(usage):
    if usage >= 90: return QColor("#8B0000")
    if usage >= 80: return QColor("#f12c2f")
    if usage >= 50: return QColor("#ff9282")
    return QColor("#14bcff")

class CpuCoreFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._usages = psutil.cpu_percent(percpu=True)
        n = len(self._usages)
        self.setFixedSize(n * (BAR_WIDTH + 2) + 4, BAR_HEIGHT + 4)

    def update_usages(self, usages):
        self._usages = usages
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#333333"))
        for i, usage in enumerate(self._usages):
            bar_h = int((usage / 100) * (BAR_HEIGHT / 2))
            color = _determine_bar_color(usage)
            painter.fillRect(
                2 + i * (BAR_WIDTH + 2),
                2 + (BAR_HEIGHT // 2) - bar_h,
                BAR_WIDTH,
                bar_h * 2,
                color
            )


# ─── Countdown ────────────────────────────────────────────────────────────────
class CountdownState:
    active       = False
    last_type    = None   # 1=alarm, 2=shutdown
    last_minutes = None
    _time_text   = "\udb86\udee1"  # shared across threads

countdown = CountdownState()

def _countdown_thread(minutes, ctype, label_ref):
    countdown_time = minutes * 60
    while countdown_time > 0:
        if not countdown.active:
            countdown._time_text = "\udb86\udee1"
            return
        m = int(countdown_time) // 60
        s = int(countdown_time) % 60
        countdown._time_text = f"\udb86\udee1:{m:02}:{s:02}"
        time.sleep(1)
        countdown_time -= 1
    if countdown.active:
        countdown.active = False
        countdown._time_text = "\udb86\udee1"
        if ctype == 1:
            _show_alarm_signal.emit()
        else:
            os.system("shutdown /s /f /t 1")

class _AlarmSignalEmitter(QObject):
    alarm = pyqtSignal()
    def emit(self):
        self.alarm.emit()

_show_alarm_signal = _AlarmSignalEmitter()

def show_big_alarm():
    dlg = QDialog()
    dlg.setWindowTitle("ALARM!")
    dlg.resize(600, 300)
    dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    dlg.setStyleSheet(f"background: #1d2027;")
    layout = QVBoxLayout(dlg)
    lbl = QLabel("ALARM! Time's up!")
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet("color: #ff0000; font-size: 36pt; font-weight: bold; font-family: 'JetBrainsMono NFP';")
    layout.addWidget(lbl)
    _blink = [True]
    timer = QTimer(dlg)
    def blink():
        lbl.setStyleSheet(
            f"color: {'#ff0000' if _blink[0] else '#00aaff'}; font-size: 36pt; font-weight: bold; font-family: 'JetBrainsMono NFP';"
        )
        _blink[0] = not _blink[0]
    timer.timeout.connect(blink)
    timer.start(500)
    dlg.mousePressEvent = lambda e: dlg.accept()
    # center
    screen = QApplication.primaryScreen().geometry()
    dlg.move(screen.center() - dlg.rect().center())
    dlg.exec()

_show_alarm_signal.alarm.connect(show_big_alarm)

def start_countdown_option(label_ref):
    choice, ok = QInputDialog.getInt(
        None, "Select Timer Type",
        "Choose an option:\n1 - Countdown Alarm\n2 - Countdown Shutdown",
        1, 1, 2
    )
    if not ok:
        return
    if countdown.active:
        countdown.active = False
        return
    minutes, ok2 = QInputDialog.getDouble(None, "Countdown", "Enter minutes:", 5, 0.1, 9999, 1)
    if not ok2 or minutes <= 0:
        return
    countdown.active       = True
    countdown.last_type    = choice
    countdown.last_minutes = minutes
    t = threading.Thread(target=_countdown_thread, args=(minutes, choice, label_ref), daemon=True)
    t.start()

def run_last_countdown(label_ref):
    if countdown.last_type is None or countdown.last_minutes is None:
        return
    if countdown.active:
        countdown.active = False
        return
    countdown.active = True
    t = threading.Thread(
        target=_countdown_thread,
        args=(countdown.last_minutes, countdown.last_type, label_ref),
        daemon=True
    )
    t.start()


# ─── Git status ───────────────────────────────────────────────────────────────
_git_queue = Queue()

def check_git_status(repo, q):
    git_path = repo["path"]
    if not os.path.exists(git_path):
        q.put((repo["name"], repo["label"], "#000000"))
        return
    result = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=git_path)
    color = "#00ff21" if "nothing to commit, working tree clean" in result.stdout else "#fe1616"
    q.put((repo["name"], repo["label"], color))

def _git_status_loop(repos, q):
    while True:
        for repo in repos:
            check_git_status(repo, q)
        time.sleep(30)

def git_backup(repos):
    commands = " ; ".join([
        f"{r['path']}\\scripts\\Github\\{r['name']}u.ps1" for r in repos
    ])
    subprocess.Popen([
        "Start", "pwsh", "-NoExit", "-Command",
        f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; {commands} ; cd ~}}"
    ], shell=True)

def delete_git_lock_files(repos):
    for repo in repos:
        lock_file = os.path.join(repo["path"], ".git", "index.lock")
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"Deleted: {lock_file}")
        except Exception as e:
            print(f"Error deleting {lock_file}: {e}")


# ─── Rclone ───────────────────────────────────────────────────────────────────
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

rclone_status = {}  # id -> color

def _update_toggle_color_cb(toggle_lbl):
    if not rclone_status:
        return
    agg = CP_GREEN if all(c == CP_GREEN for c in rclone_status.values()) else CP_RED
    toggle_lbl.setStyleSheet(
        f"color: {agg}; font-family: 'JetBrainsMono NFP'; font-size: 20pt; font-weight: bold;"
    )

def check_and_update_rclone(cfg, toggle_lbl):
    def run():
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        with open(cfg["log"], "w") as f:
            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
        with open(cfg["log"], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        color = CP_GREEN if "ERROR" not in content else CP_RED
        rclone_status[cfg.get("id", cfg["label"])] = color
        # schedule UI update on main thread via QTimer.singleShot
        QTimer.singleShot(0, lambda: _update_toggle_color_cb(toggle_lbl))
        interval_ms = int(load_config().get("rclone_settings", {}).get("interval_min", 10)) * 60000
        QTimer.singleShot(interval_ms, lambda: check_and_update_rclone(cfg, toggle_lbl))
    threading.Thread(target=run, daemon=True).start()


# ─── Main window ──────────────────────────────────────────────────────────────
class StatusBar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedSize(1920, 39)
        screen_w = QApplication.primaryScreen().geometry().width()
        self.move(screen_w // 2 - 960, 993)
        self.setStyleSheet(GLOBAL_QSS + f"QMainWindow {{ border: 1px solid {CP_RED}; }}")

        self._config = load_config()

        border_frame = QFrame()
        border_frame.setStyleSheet(f"QFrame {{ background: {CP_BG}; border: 1px solid {CP_RED}; }}")
        self.setCentralWidget(border_frame)
        inner = QWidget(border_frame)
        inner.setStyleSheet(f"background: {CP_BG}; border: none;")
        border_layout = QVBoxLayout(border_frame)
        border_layout.setContentsMargins(1, 1, 1, 1)
        border_layout.addWidget(inner)
        central = inner
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(2, 1, 2, 1)
        main_layout.setSpacing(0)

        # Left widget (stretches)
        self._left_widget = QWidget()
        self._left_widget.setStyleSheet(f"background: {CP_BG};")
        self._left_layout = QHBoxLayout(self._left_widget)
        self._left_layout.setContentsMargins(0, 0, 0, 0)
        self._left_layout.setSpacing(0)
        self._left_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self._left_widget, 1)

        # Right widget (fixed right)
        self._right_widget = QWidget()
        self._right_widget.setStyleSheet(f"background: {CP_BG};")
        self._right_layout = QHBoxLayout(self._right_widget)
        self._right_layout.setContentsMargins(0, 0, 0, 0)
        self._right_layout.setSpacing(0)
        self._right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        main_layout.addWidget(self._right_widget)

        self._build_left()
        self._build_right()
        self._start_timers()

    # ── Left panel ────────────────────────────────────────────────────────────
    def _build_left(self):
        ll = self._left_layout

        # 1. Uptime label
        self.uptime_label = QLabel(format_uptime())
        self.uptime_label.setStyleSheet(
            f"color: #6bc0f8; font-family: 'JetBrainsMono NFP'; font-size: 16pt; font-weight: bold;"
        )
        self.uptime_label.setCursor(Qt.CursorShape.PointingHandCursor)
        def _uptime_click(event):
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                _open_static_edit("uptime")
            else:
                subprocess.Popen("timedate.cpl", shell=True)
        self.uptime_label.mousePressEvent = _uptime_click
        ll.addWidget(self.uptime_label)

        # 2. Paginated buttons_left
        self._bl_page_size = self._config.get("buttons_left_page_size", 10)
        self._bl_offset    = 0
        self._bl_widgets   = []

        prev_bt = QPushButton("«")
        prev_bt.setStyleSheet(
            "background: white; color: black; font-weight: bold; border-radius: 4px; padding: 1px 4px;"
        )
        prev_bt.setFixedSize(22, 20)
        prev_bt.clicked.connect(self._bl_prev)
        ll.addWidget(prev_bt)
        self._bl_prev_bt = prev_bt

        self._bl_container = QWidget()
        self._bl_container.setStyleSheet(f"background: {CP_BG};")
        self._bl_container_layout = QHBoxLayout(self._bl_container)
        self._bl_container_layout.setContentsMargins(0, 0, 0, 0)
        self._bl_container_layout.setSpacing(0)
        ll.addWidget(self._bl_container)

        next_bt = QPushButton("»")
        next_bt.setStyleSheet(
            "background: white; color: black; font-weight: bold; border-radius: 4px; padding: 1px 4px;"
        )
        next_bt.setFixedSize(22, 20)
        next_bt.clicked.connect(self._bl_next)
        ll.addWidget(next_bt)
        self._bl_next_bt = next_bt

        gear_bt = QPushButton("⚙")
        gear_bt.setStyleSheet(
            "background: white; color: black; font-family: 'JetBrainsMono NFP'; border-radius: 4px; padding: 1px 4px;"
        )
        gear_bt.setFixedSize(22, 20)
        gear_bt.clicked.connect(self._bl_settings)
        ll.addWidget(gear_bt)

        self._bl_render()

        # 3. Git section
        self._build_git(ll)

        # 4. Rclone toggle
        self._rclone_popup = None
        self._rclone_toggle = QLabel("\uef2c")
        self._rclone_toggle.setStyleSheet(
            f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 20pt; font-weight: bold;"
        )
        self._rclone_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._rclone_toggle.mousePressEvent = lambda e: self._toggle_rclone_popup()
        ll.addWidget(self._rclone_toggle)

        # 5. Rclone settings gear
        rclone_gear = QLabel("⚙")
        rclone_gear.setStyleSheet(
            f"color: #808080; font-family: 'JetBrainsMono NFP'; font-size: 14pt;"
        )
        rclone_gear.setCursor(Qt.CursorShape.PointingHandCursor)
        rclone_gear.mousePressEvent = lambda e: open_rclone_settings()
        ll.addWidget(rclone_gear)

        # 6. Add new button
        add_bt = QLabel("+")
        add_bt.setStyleSheet(
            f"color: {CP_GREEN}; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;"
        )
        add_bt.setCursor(Qt.CursorShape.PointingHandCursor)
        add_bt.mousePressEvent = lambda e: open_edit_gui(
            {"text": "NEW", "fg": "#ffffff", "bg": CP_BG, "id": f"btn_{int(time.time())}", "bindings": {}},
            "buttons_left"
        )
        ll.addWidget(add_bt)

    def _bl_render(self):
        # Clear old widgets
        for w in self._bl_widgets:
            w.setParent(None)
        self._bl_widgets.clear()
        items = load_config().get("buttons_left", [])
        start = self._bl_offset
        end   = min(start + self._bl_page_size, len(items))
        for idx in range(start, end):
            w = create_dynamic_button(self._bl_container_layout, items[idx], "buttons_left", idx)
            self._bl_widgets.append(w)
        # Update arrow colors
        dim = f"background: #555555; color: black; font-weight: bold; border-radius: 4px; padding: 1px 4px;"
        act = f"background: white;   color: black; font-weight: bold; border-radius: 4px; padding: 1px 4px;"
        self._bl_prev_bt.setStyleSheet(act if self._bl_offset > 0 else dim)
        self._bl_next_bt.setStyleSheet(act if end < len(items) else dim)

    def _bl_prev(self):
        if self._bl_offset > 0:
            self._bl_offset = max(0, self._bl_offset - self._bl_page_size)
            self._bl_render()

    def _bl_next(self):
        items = load_config().get("buttons_left", [])
        if self._bl_offset + self._bl_page_size < len(items):
            self._bl_offset += self._bl_page_size
            self._bl_render()

    def _bl_settings(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Button Bar Settings")
        dlg.resize(320, 160)
        dlg.setStyleSheet(DIALOG_QSS)
        dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        lay = QVBoxLayout(dlg); lay.setContentsMargins(12, 12, 12, 12)
        title = QLabel("// BUTTON BAR")
        title.setStyleSheet(f"color: {CP_CYAN}; font-size: 12pt; font-weight: bold;")
        lay.addWidget(title)
        grp = QGroupBox("PAGE SIZE"); form = QFormLayout(); grp.setLayout(form)
        size_le = QLineEdit(str(self._bl_page_size)); size_le.setFixedWidth(60)
        form.addRow("VISIBLE BUTTONS", size_le); lay.addWidget(grp)
        btn = QPushButton("SAVE"); btn.setObjectName("btn_save")
        btn.setCursor(Qt.CursorShape.PointingHandCursor); lay.addWidget(btn)
        def _save():
            try: self._bl_page_size = int(size_le.text())
            except ValueError: pass
            cfg = load_config(); cfg["buttons_left_page_size"] = self._bl_page_size; save_config(cfg)
            dlg.accept(); self._bl_render()
        btn.clicked.connect(_save); dlg.show()

    # ── Git section ───────────────────────────────────────────────────────────
    def _build_git(self, ll):
        self._config = load_config()
        repos = self._config.get("git_repos", [])
        self._git_labels = {}

        sep_l = QLabel("[")
        sep_l.setStyleSheet(f"color: {CP_CYAN}; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;")
        ll.addWidget(sep_l)

        bkup = QLabel("\udb80\udea2")
        bkup.setStyleSheet(f"color: {CP_CYAN}; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;")
        bkup.setCursor(Qt.CursorShape.PointingHandCursor)
        bkup.mousePressEvent = lambda e: git_backup(repos)
        ll.addWidget(bkup)

        for repo in repos:
            lbl = QLabel(repo["label"])
            lbl.setStyleSheet(f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 12pt; font-weight: bold;")
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            p = repo["path"]
            def _make_click(path):
                def click(event):
                    mods = event.modifiers()
                    btn  = event.button()
                    if btn == Qt.MouseButton.LeftButton:
                        if mods & Qt.KeyboardModifier.ControlModifier:
                            subprocess.Popen(f'explorer "{path}"', shell=True)
                        else:
                            subprocess.Popen(
                                ["Start", "pwsh", "-NoExit", "-Command",
                                 f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd '{path}' ; gitter}}"],
                                shell=True
                            )
                    elif btn == Qt.MouseButton.RightButton:
                        if mods & Qt.KeyboardModifier.ControlModifier:
                            subprocess.Popen(
                                ["Start", "pwsh", "-NoExit", "-Command",
                                 f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd '{path}' ; git restore . }}"],
                                shell=True
                            )
                        else:
                            subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=path, shell=True)
                return click
            lbl.mousePressEvent = _make_click(p)
            ll.addWidget(lbl)
            self._git_labels[repo["name"]] = lbl

        del_lbl = QLabel("\udb82\udde7")
        del_lbl.setStyleSheet(f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;")
        del_lbl.setCursor(Qt.CursorShape.PointingHandCursor)
        del_lbl.mousePressEvent = lambda e: delete_git_lock_files(repos)
        ll.addWidget(del_lbl)

        sep_r = QLabel("]")
        sep_r.setStyleSheet(f"color: {CP_CYAN}; font-family: 'JetBrainsMono NFP'; font-size: 18pt; font-weight: bold;")
        ll.addWidget(sep_r)

        # Start git status thread
        if repos:
            t = threading.Thread(target=_git_status_loop, args=(repos, _git_queue), daemon=True)
            t.start()

    # ── Rclone popup ──────────────────────────────────────────────────────────
    def _toggle_rclone_popup(self):
        if self._rclone_popup and self._rclone_popup.isVisible():
            self._rclone_popup.hide()
            self._rclone_popup = None
            return

        commands = load_config().get("rclone_commands", {})
        popup = QFrame(self, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        popup.setStyleSheet(f"background: #1d2027; border: 1px solid {CP_RED};")
        row = QHBoxLayout(popup)
        row.setContentsMargins(4, 2, 4, 2)
        row.setSpacing(4)

        for key, cfg in commands.items():
            if "id" not in cfg:
                cfg["id"] = key
            lbl = QLabel(cfg["label"])
            cached = rclone_status.get(cfg.get("id", key))
            color  = cached if cached else "white"
            lbl.setStyleSheet(
                f"color: {color}; font-family: 'JetBrainsMono NFP'; font-size: 16pt; font-weight: bold;"
            )
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            def _make_rclone_click(c):
                def click(event):
                    mods = event.modifiers()
                    if mods & Qt.KeyboardModifier.ShiftModifier:
                        open_edit_gui(c, "rclone_commands")
                    elif mods & Qt.KeyboardModifier.ControlModifier:
                        if event.button() == Qt.MouseButton.LeftButton:
                            action = c.get("bindings", {}).get("Control-Button-1", {
                                "type": "run_command", "cmd": c.get("left_click_cmd", "")
                            })
                            handle_action(action)
                        elif event.button() == Qt.MouseButton.RightButton:
                            action = c.get("bindings", {}).get("Control-Button-3", {
                                "type": "run_command", "cmd": c.get("right_click_cmd", "")
                            })
                            handle_action(action)
                    else:
                        try:
                            subprocess.Popen(
                                ["powershell", "-NoExit", "-Command", f'edit "{c["log"]}"'],
                                creationflags=subprocess.CREATE_NEW_CONSOLE
                            )
                        except Exception as ex:
                            print(f"Error opening log: {ex}")
                return click
            lbl.mousePressEvent = _make_rclone_click(cfg)
            row.addWidget(lbl)

        popup.adjustSize()
        gpos = self._rclone_toggle.mapToGlobal(self._rclone_toggle.rect().topLeft())
        popup.move(gpos.x(), gpos.y() - popup.height() - 2)
        popup.show()
        self._rclone_popup = popup


    # ── Right panel ───────────────────────────────────────────────────────────
    def _build_right(self):
        rl = self._right_layout

        # Download / Upload
        self.download_lb = QLabel("")
        self.download_lb.setStyleSheet(
            f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
        )
        _bind_static(self.download_lb, "download", "sniffnet")
        rl.addWidget(self.download_lb)

        self.upload_lb = QLabel("")
        self.upload_lb.setStyleSheet(
            f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
        )
        _bind_static(self.upload_lb, "upload", "sniffnet")
        rl.addWidget(self.upload_lb)

        # CPU label
        self.lb_cpu = QLabel("")
        self.lb_cpu.setFixedWidth(55)
        self.lb_cpu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_cpu.setStyleSheet(
            f"color: #1b8af1; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
            f"border: 1px solid #1b8af1;"
        )
        _bind_static(self.lb_cpu, "cpu", r"C:\@delta\ms1\scripts\process\process_viewer.py")
        rl.addWidget(self.lb_cpu)

        # CPU core bars
        self.cpu_core_frame = CpuCoreFrame()
        rl.addWidget(self.cpu_core_frame)

        # GPU label
        self.lb_gpu = QLabel("")
        self.lb_gpu.setFixedWidth(55)
        self.lb_gpu.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_gpu.setStyleSheet(
            f"color: {CP_GREEN}; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
            f"border: 1px solid {CP_GREEN};"
        )
        _bind_static(self.lb_gpu, "gpu", "start ms-settings:display")
        rl.addWidget(self.lb_gpu)

        # RAM label
        self.lb_ram = QLabel("")
        self.lb_ram.setFixedWidth(55)
        self.lb_ram.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_ram.setStyleSheet(
            f"color: #f08d0c; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
            f"border: 1px solid #f08d0c;"
        )
        _bind_static(self.lb_ram, "ram", "taskmgr")
        rl.addWidget(self.lb_ram)

        # Drive C
        self.lb_duc = QLabel("")
        self.lb_duc.setFixedWidth(80)
        self.lb_duc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_duc.setStyleSheet(
            f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
            f"border: 1px solid #1b8af1;"
        )
        _bind_static(self.lb_duc, "drive_c", "explorer C:\\")
        rl.addWidget(self.lb_duc)

        # Drive D
        self.lb_dud = QLabel("")
        self.lb_dud.setFixedWidth(80)
        self.lb_dud.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lb_dud.setStyleSheet(
            f"color: white; font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
            f"border: 1px solid #1b8af1;"
        )
        _bind_static(self.lb_dud, "drive_d", "explorer D:\\")
        rl.addWidget(self.lb_dud)

        # Countdown timer label
        self.time_left_label = QLabel("\udb86\udee1")
        self.time_left_label.setStyleSheet(
            f"color: {CP_ORANGE}; font-family: 'JetBrainsMono NFP'; font-size: 16pt; font-weight: bold;"
        )
        self.time_left_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.time_left_label.mousePressEvent = lambda e: start_countdown_option(self.time_left_label)
        rl.addWidget(self.time_left_label)

        # Run last countdown button
        run_last_bt = QPushButton("\udb86\udee5")
        run_last_bt.setStyleSheet(
            f"color: {CP_GREEN}; background: {CP_BG}; font-family: 'JetBrainsMono NFP'; "
            f"font-size: 16pt; border: none; padding: 0px;"
        )
        run_last_bt.setCursor(Qt.CursorShape.PointingHandCursor)
        run_last_bt.clicked.connect(lambda: run_last_countdown(self.time_left_label))
        rl.addWidget(run_last_bt)

        # Dynamic buttons_right
        for idx, btn_cfg in enumerate(self._config.get("buttons_right", [])):
            create_dynamic_button(rl, btn_cfg, "buttons_right", idx)

    # ── Timers ────────────────────────────────────────────────────────────────
    def _start_timers(self):
        # Uptime
        self._uptime_timer = QTimer(self)
        self._uptime_timer.timeout.connect(self._update_uptime)
        self._uptime_timer.start(1000)

        # System info (cpu/gpu/ram/disk/net)
        self._info_timer = QTimer(self)
        self._info_timer.timeout.connect(self._update_info)
        self._info_timer.start(1000)

        # CPU core bars
        self._core_timer = QTimer(self)
        self._core_timer.timeout.connect(self._update_cores)
        self._core_timer.start(1000)

        # Git queue drain
        self._git_timer = QTimer(self)
        self._git_timer.timeout.connect(self._drain_git_queue)
        self._git_timer.start(200)

        # Countdown label poll
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._update_countdown_label)
        self._countdown_timer.start(500)

        # Start rclone checks
        commands = self._config.get("rclone_commands", {})
        rclone_cfg = self._config.get("rclone_settings", {"simultaneous": True})
        items = list(commands.items())
        if rclone_cfg.get("simultaneous", True):
            for key, cfg in items:
                if "id" not in cfg: cfg["id"] = key
                check_and_update_rclone(cfg, self._rclone_toggle)
        else:
            def _seq(remaining):
                if not remaining: return
                key, cfg = remaining[0]
                if "id" not in cfg: cfg["id"] = key
                check_and_update_rclone(cfg, self._rclone_toggle)
                QTimer.singleShot(100, lambda: _seq(remaining[1:]))
            _seq(items)

    def _update_uptime(self):
        self.uptime_label.setText(format_uptime())

    def _update_info(self):
        cpu, ram = get_cpu_ram_info()
        gpu       = get_gpu_usage()
        dc, dd    = get_disk_info()
        up, down  = get_net_speed()

        self.lb_cpu.setText(f"{cpu}%")
        self.lb_ram.setText(f"{ram}%")
        self.lb_gpu.setText(f"{gpu}%")
        self.lb_duc.setText(f"\uf0a0 {dc}%")
        self.lb_dud.setText(f"\uf0a0 {dd}%")
        self.upload_lb.setText(f" ▲ {up} ")
        self.download_lb.setText(f" ▼ {down} ")

        # Dynamic colors
        cpu_f = float(cpu)
        ram_f = float(ram)
        dc_f  = float(dc)
        dd_f  = float(dd)
        up_f  = float(up)
        dn_f  = float(down)

        self.lb_cpu.setStyleSheet(
            f"color: {'black' if cpu_f > 80 else '#1b8af1'}; "
            f"background: {'#14bcff' if cpu_f > 80 else CP_BG}; "
            f"font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #1b8af1;"
        )
        self.lb_ram.setStyleSheet(
            f"color: {'black' if ram_f > 80 else '#f08d0c'}; "
            f"background: {'#ff934b' if ram_f > 80 else CP_BG}; "
            f"font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #f08d0c;"
        )
        self.lb_duc.setStyleSheet(
            f"color: white; background: {'#f12c2f' if dc_f > 90 else '#044568'}; "
            f"font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #1b8af1;"
        )
        self.lb_dud.setStyleSheet(
            f"color: white; background: {'#f12c2f' if dd_f > 90 else '#044568'}; "
            f"font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold; border: 1px solid #1b8af1;"
        )

        def _net_style(val):
            if val < 0.1:   return f"color: white; background: black;"
            if val < 0.5:   return f"color: black; background: #A8E4A8;"
            if val < 1.0:   return f"color: black; background: #67D567;"
            return              f"color: black; background: #32AB32;"
        base = "font-family: 'JetBrainsMono NFP'; font-size: 10pt; font-weight: bold;"
        self.upload_lb.setStyleSheet(_net_style(up_f) + base)
        self.download_lb.setStyleSheet(_net_style(dn_f) + base)

    def _update_cores(self):
        usages = psutil.cpu_percent(percpu=True)
        self.cpu_core_frame.update_usages(usages)

    def _drain_git_queue(self):
        try:
            while True:
                name, text, color = _git_queue.get_nowait()
                if name in self._git_labels:
                    self._git_labels[name].setText(text)
                    self._git_labels[name].setStyleSheet(
                        f"color: {color}; font-family: 'JetBrainsMono NFP'; font-size: 12pt; font-weight: bold;"
                    )
        except Empty:
            pass

    def _update_countdown_label(self):
        self.time_left_label.setText(countdown._time_text)


# ─── Entry point ──────────────────────────────────────────────────────────────
_main_window = None
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(GLOBAL_QSS)
    window = StatusBar()
    _main_window = window
    window.show()
    calculate_time_to_appear(start_time)
    sys.exit(app.exec())
