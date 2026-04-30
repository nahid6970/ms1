#? https://pypi.org/project/pretty-errors/

from customtkinter import *
from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from queue import Queue
from time import strftime
from tkinter import Label, messagebox
from tkinter import simpledialog
from tkinter import ttk
import ctypes
import filecmp
import importlib
import keyboard
import os
import psutil
import pyautogui
import subprocess
import sys
import threading
import time
import tkinter as tk
import win32gui
import json
import win32process
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QGroupBox, QFormLayout, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

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

CONFIG = load_config()

def handle_action(action_cfg):
    if not action_cfg: return
    atype = action_cfg.get("type")
    cmd = action_cfg.get("cmd")
    cwd = action_cfg.get("cwd")
    admin = action_cfg.get("admin", False)
    hide = action_cfg.get("hide", False)
    
    if admin:
        # Launch as admin using shell execute "runas"
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable if atype=="python" else "cmd.exe", 
                                               f"/c {cmd}" if atype!="python" else cmd, cwd, 1 if not hide else 0)
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
        if func_name == "restart": restart()
        elif func_name == "close_window": close_window()
        elif func_name == "clear_screen": clear_screen()
        elif func_name == "force_shutdown": force_shutdown(None)
        elif func_name == "force_restart": force_restart(None)

def open_edit_gui(item_cfg, category, index=None):
    CP_BG     = "#050505"
    CP_PANEL  = "#111111"
    CP_YELLOW = "#FCEE0A"
    CP_CYAN   = "#00F0FF"
    CP_RED    = "#FF003C"
    CP_GREEN  = "#00ff21"
    CP_DIM    = "#3a3a3a"
    CP_TEXT   = "#E0E0E0"

    QSS = f"""
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

    dlg = QDialog()
    dlg.setWindowTitle(f"Edit — {item_cfg.get('id', 'Item')}")
    dlg.resize(1000, 620)
    dlg.setStyleSheet(QSS)
    dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    root_layout = QVBoxLayout(dlg)
    root_layout.setContentsMargins(10, 10, 10, 10)
    root_layout.setSpacing(8)

    # Title bar
    title = QLabel(f"// EDIT :: {item_cfg.get('id', 'ITEM').upper()}")
    title.setStyleSheet(f"color: {CP_CYAN}; font-size: 13pt; font-weight: bold; padding: 4px 0;")
    root_layout.addWidget(title)

    # Two-panel area
    panels = QHBoxLayout()
    panels.setSpacing(10)
    root_layout.addLayout(panels)

    # ── LEFT PANEL ──────────────────────────────────────────────
    left_scroll = QScrollArea()
    left_scroll.setWidgetResizable(True)
    left_w = QWidget()
    left_layout = QVBoxLayout(left_w)
    left_layout.setSpacing(6)
    left_layout.setContentsMargins(6, 6, 6, 6)
    left_scroll.setWidget(left_w)
    panels.addWidget(left_scroll, 1)

    def section(text):
        lbl = QLabel(text)
        lbl.setObjectName("section_label")
        return lbl

    def field_row(label_text, widget):
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setFixedWidth(90)
        lbl.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt;")
        row.addWidget(lbl)
        row.addWidget(widget)
        return row

    # Appearance group
    grp_appear = QGroupBox("APPEARANCE")
    form_appear = QFormLayout()
    form_appear.setSpacing(6)
    grp_appear.setLayout(form_appear)

    entries = {}
    for field in ["text", "fg", "bg", "id"]:
        ent = QLineEdit(str(item_cfg.get(field, "")))
        form_appear.addRow(field.upper(), ent)
        entries[field] = ent

    left_layout.addWidget(grp_appear)

    # Font group
    grp_font = QGroupBox("FONT")
    form_font = QFormLayout()
    form_font.setSpacing(6)
    grp_font.setLayout(form_font)

    cur_font = item_cfg.get("font", ["JetBrainsMono NFP", 16, "bold"])
    font_families = ["JetBrainsMono NFP", "JetBrainsMono NF", "Jetbrainsmono nfp",
                     "Arial", "Consolas", "Courier New", "Segoe UI", "Tahoma", "Verdana"]
    font_family_cb = QComboBox()
    font_family_cb.addItems(font_families)
    font_family_cb.setCurrentText(cur_font[0] if cur_font else "JetBrainsMono NFP")

    font_size_le = QLineEdit(str(cur_font[1]) if len(cur_font) > 1 else "16")
    font_size_le.setFixedWidth(60)

    font_weight_cb = QComboBox()
    font_weight_cb.addItems(["bold", "normal"])
    font_weight_cb.setCurrentText(cur_font[2] if len(cur_font) > 2 else "bold")

    form_font.addRow("FAMILY", font_family_cb)
    form_font.addRow("SIZE", font_size_le)
    form_font.addRow("WEIGHT", font_weight_cb)
    left_layout.addWidget(grp_font)

    # Padding group
    grp_pad = QGroupBox("PADDING")
    form_pad = QFormLayout()
    form_pad.setSpacing(6)
    grp_pad.setLayout(form_pad)

    padx_left_le  = QLineEdit(str(item_cfg.get("padx_left", 1)))
    padx_right_le = QLineEdit(str(item_cfg.get("padx_right", 1)))
    padx_left_le.setFixedWidth(60)
    padx_right_le.setFixedWidth(60)
    form_pad.addRow("PADX LEFT",  padx_left_le)
    form_pad.addRow("PADX RIGHT", padx_right_le)
    left_layout.addWidget(grp_pad)

    # Placement group
    grp_place = QGroupBox("PLACEMENT")
    form_place = QFormLayout()
    form_place.setSpacing(6)
    grp_place.setLayout(form_place)

    group_cb = QComboBox()
    group_cb.addItems(["buttons_left", "buttons_right"])
    group_cb.setCurrentText(category if category in ["buttons_left", "buttons_right"] else "buttons_left")

    config_now = load_config()
    cur_list = config_now.get(group_cb.currentText(), [])
    max_idx = max(len(cur_list) - 1, 0)
    index_le = QLineEdit(str(index if index is not None else max_idx))
    index_le.setFixedWidth(60)

    def _on_group_changed(text):
        lst = config_now.get(text, [])
        index_le.setText(str(max(len(lst) - 1, 0)))
    group_cb.currentTextChanged.connect(_on_group_changed)

    form_place.addRow("GROUP", group_cb)
    form_place.addRow("INDEX", index_le)
    left_layout.addWidget(grp_place)
    left_layout.addStretch()

    # ── RIGHT PANEL ─────────────────────────────────────────────
    right_scroll = QScrollArea()
    right_scroll.setWidgetResizable(True)
    right_w = QWidget()
    right_layout = QVBoxLayout(right_w)
    right_layout.setSpacing(6)
    right_layout.setContentsMargins(6, 6, 6, 6)
    right_scroll.setWidget(right_w)
    panels.addWidget(right_scroll, 2)

    click_types = [
        ("LEFT CLICK",       "Button-1"),
        ("RIGHT CLICK",      "Button-3"),
        ("CTRL + LEFT",      "Control-Button-1"),
        ("CTRL + RIGHT",     "Control-Button-3"),
    ]
    binding_inputs = {}

    for label_text, bkey in click_types:
        grp = QGroupBox(label_text)
        form = QFormLayout()
        form.setSpacing(4)
        grp.setLayout(form)

        bcfg = item_cfg.get("bindings", {}).get(bkey, {})

        cmd_le = QLineEdit(bcfg.get("cmd", bcfg.get("func", "")))
        type_cb = QComboBox()
        type_cb.addItems(["subprocess", "run_command", "python", "function"])
        type_cb.setCurrentText(bcfg.get("type", "subprocess"))

        hide_chk  = QCheckBox("Hide Terminal")
        hide_chk.setChecked(bcfg.get("hide", False))
        admin_chk = QCheckBox("Run as Admin")
        admin_chk.setChecked(bcfg.get("admin", False))

        chk_row = QWidget()
        chk_layout = QHBoxLayout(chk_row)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        chk_layout.addWidget(hide_chk)
        chk_layout.addWidget(admin_chk)
        chk_layout.addStretch()

        form.addRow("CMD",  cmd_le)
        form.addRow("TYPE", type_cb)
        form.addRow("",     chk_row)

        right_layout.addWidget(grp)
        binding_inputs[bkey] = {"cmd": cmd_le, "type": type_cb, "hide": hide_chk, "admin": admin_chk}

    right_layout.addStretch()

    # ── BOTTOM BUTTONS ───────────────────────────────────────────
    btn_row = QHBoxLayout()
    btn_save   = QPushButton("SAVE")
    btn_delete = QPushButton("DELETE")
    btn_save.setObjectName("btn_save")
    btn_delete.setObjectName("btn_delete")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_row.addWidget(btn_save)
    btn_row.addWidget(btn_delete)
    root_layout.addLayout(btn_row)

    def save():
        for field in ["text", "fg", "bg", "id"]:
            item_cfg[field] = entries[field].text()
        try:
            item_cfg["font"] = [font_family_cb.currentText(), int(font_size_le.text()), font_weight_cb.currentText()]
        except ValueError:
            pass
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

        # Remove from old location first (if editing existing item in a list)
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
        reply = QMessageBox.question(dlg, "Restart", "Settings saved. Restart GUI to apply?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            restart()

    def delete():
        reply = QMessageBox.question(dlg, "Delete", f"Delete '{item_cfg.get('id', 'this item')}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes: return
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
        reply = QMessageBox.question(dlg, "Restart", "Item deleted. Restart GUI to apply?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            restart()

    btn_save.clicked.connect(save)
    btn_delete.clicked.connect(delete)
    dlg.exec()

def create_dynamic_button(parent, btn_cfg, category, index=None):
    widget_type = btn_cfg.get("widget_type", "Label")
    font = tuple(btn_cfg.get("font", ["JetBrainsMono NFP", 16, "bold"]))
    _fg = btn_cfg.get("fg", "") or "white"
    _bg = btn_cfg.get("bg", "") or "#1d2027"
    
    if widget_type == "CTkLabel":
        lbl = CTkLabel(parent, text=btn_cfg.get("text", ""), text_color=_fg, font=font)
    elif widget_type == "CTkButton":
        lbl = CTkButton(parent, text=btn_cfg.get("text", ""), text_color=_fg, fg_color=_bg, font=font, width=0, height=10)
    else:
        lbl = tk.Label(parent, text=btn_cfg.get("text", ""), bg=_bg, fg=_fg, font=font, relief="flat")
    
    px_l = int(btn_cfg.get("padx_left", 1))
    px_r = int(btn_cfg.get("padx_right", 1))
    lbl.pack(side="left", padx=(px_l, px_r))
    
    bindings = btn_cfg.get("bindings", {})
    for event, action in bindings.items():
        # Handle simple string function calls for backward compatibility if any
        if isinstance(action, str):
            lbl.bind(f"<{event}>", lambda e, a=action: handle_action({"type": "function", "func": a}))
        else:
            lbl.bind(f"<{event}>", lambda e, a=action: handle_action(a))
    
    # Shift+Click for editing
    lbl.bind("<Shift-Button-1>", lambda e: open_edit_gui(btn_cfg, category, index))
    return lbl


def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()

# Print ASCII art in the console
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

#! Vaiables to track the position of the mouse when clicking​⁡
drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry("+%s+%s" % (x, y))

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="red")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def run_command(command, admin=False, hide=False, no_exit=True):
    """Run a command (defaulting to PowerShell) with options for admin and visibility."""
    if admin:
        try:
            # Use ShellExecuteW for 'runas' elevation
            # pwsh -NoExit -Command if no_exit is True
            # cmd /c if hide is True
            executable = "pwsh"
            args = f"{'-NoExit ' if no_exit else ''}-Command \"{command}\""
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, args, None, 1 if not hide else 0)
        except Exception as e:
            print(f"Admin run_command failed: {e}")
        return

    # Non-admin run
    if hide:
        subprocess.Popen(["pwsh", "-Command", command], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        # Launching in a new visible window
        cmd_list = ["start", "pwsh"]
        if no_exit:
            cmd_list.append("-NoExit")
        cmd_list.extend(["-Command", command])
        subprocess.Popen(" ".join(cmd_list), shell=True)

class HoverButton(tk.Button):
    def __init__(self, master=None, **kw):
        self.default_color = kw.pop('default_color', "#000000")
        self.hover_color = kw.pop('hover_color', "red")
        self.default_fg = kw.pop('default_fg', "#FFFFFF")
        self.hover_fg = kw.pop('hover_fg', "#000000")
        super().__init__(master, **kw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.configure(bg=self.default_color, fg=self.default_fg)

    def on_enter(self, event):
        self.configure(bg=self.hover_color, fg=self.hover_fg)

    def on_leave(self, event):
        self.configure(bg=self.default_color, fg=self.default_fg)

# wait this time to start the gui
def long_running_function():
    time.sleep(0)
    print("Function completed!")


# Call the long-running function
long_running_function()

set_console_title("🔥")
# Create main window
ROOT = tk.Tk()
import sys as _sys; _qt_app = QApplication.instance() or QApplication(_sys.argv)
ROOT.title("Python GUI")
# ROOT.attributes('-topmost', True)  # Set always on top
# ROOT.geometry("520x800")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)  # Remove default borders


#!############################################################
# def check_window_topmost():
#     if not ROOT.attributes('-topmost'):
#         ROOT.attributes('-topmost', True)
#     ROOT.after(500, check_window_topmost)
# # Call the function to check window topmost status periodically
# check_window_topmost()
#!############################################################


# Create custom border
BORDER_FRAME = create_custom_border(ROOT)

# Add bindings to make the window movable
# ROOT.bind("<ButtonPress-1>", start_drag)
# ROOT.bind("<ButtonRelease-1>", stop_drag)
# ROOT.bind("<B1-Motion>", do_drag)

default_font = ("Jetbrainsmono nfp", 10)
ROOT.option_add("*Font", default_font)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = screen_width//2 - 1920//2
# y = screen_height//2 - 800//2
# y = screen_height-47-40
y = 993
ROOT.geometry(f"1920x39+{x}+{y}") #! overall size of the window


# #! Resize Window
# #* Function to toggle window size
# def toggle_window_size(size):
#     global window_state
#     global x
#     global y
#     if size == 'line':
#         ROOT.geometry('1920x39')
#         x = screen_width // 2 - 1920 // 2
#         y = 993
#         ROOT.configure(bg='red')
#         LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
#         LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
#     elif size == 'max':
#         ROOT.geometry('1920x140')
#         x = screen_width // 2 - 1920 // 2
#         y = 892
#         ROOT.configure(bg='#1d2027')
#         LB_L.config(text='\ueab7', bg="#1d2027", fg="#00FF00", height=1, width=0, font=("JetBrainsMono NF", 16, "bold"))
#         LB_M.config(text='\uea72', bg="#1d2027", fg="#26b2f3", height=1, width=0, font=("JetBrainsMono NF", 18, "bold"))
#     ROOT.focus_force()
#     ROOT.update_idletasks()
#     ROOT.geometry(f'{ROOT.winfo_width()}x{ROOT.winfo_height()}+{x}+{y}')
# def on_windows_x_pressed():
#     global window_size_state
#     if window_size_state == 'line':
#         toggle_window_size('max')
#         window_size_state = 'max'
#     else:
#         toggle_window_size('line')
#         window_size_state = 'line'
# #* Initial window size state
# window_size_state = 'line'
# #* Bind Windows + X to toggle between 'line' and 'max' sizesx
# #! keyboard.add_hotkey('win+x', on_windows_x_pressed)

# x = screen_width//2 - 753//2
# y = 0
# ROOT.geometry(f"+{x}+{y}")

# Create main frame
MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920, height=800)
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1, expand=True)  #! Add some padding at the top

# Adding transparent background property
ROOT.wm_attributes('-transparentcolor', '#000001')





#?  ██████╗  ██████╗  ██████╗ ████████╗    ███████╗██████╗  █████╗ ███╗   ███╗███████╗
#?  ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
#?  ██████╔╝██║   ██║██║   ██║   ██║       █████╗  ██████╔╝███████║██╔████╔██║█████╗
#?  ██╔══██╗██║   ██║██║   ██║   ██║       ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
#?  ██║  ██║╚██████╔╝╚██████╔╝   ██║       ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
#?  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝

def get_active_window_info():
   # Wait for 2 seconds
   time.sleep(2)
   # Get the position of the mouse cursor
   pos = win32gui.GetCursorPos()
   # Get the handle of the window under the cursor
   hwnd = win32gui.WindowFromPoint(pos)
   # Get the active window information
   class_name = win32gui.GetClassName(hwnd)
   window_text = win32gui.GetWindowText(hwnd)
   _, pid = win32process.GetWindowThreadProcessId(hwnd)
   process_name = psutil.Process(pid).name()
   # Print the information with colors and separators
   print(f"\033[91mActive Window Class:\033[0m {class_name}")
   print(f"\033[92mActive Window Process Name:\033[0m {process_name}")
   print(f"\033[94mActive Window Title:\033[0m {window_text}")
   print("...")  # Add dots as a visual separator

#! Close Window
def close_window(event=None):
    ROOT.destroy()

# def close_window(event=None):
#     password = simpledialog.askstring("Password", "Enter the password to close the window:")
#     if password == "":  # Replace "your_password_here" with your actual password
#         ROOT.destroy()
#     else:
#         print("Incorrect password. Window not closed.")

def restart(event=None):
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

#! Pin/Unpin
def check_window_topmost():
    if not ROOT.attributes('-topmost'):
        ROOT.attributes('-topmost', True)
    if checking:  # Only continue checking if the flag is True
        ROOT.after(500, check_window_topmost)

# def toggle_checking():
#     global checking
#     checking = not checking
#     if checking:
#         if ROOT.attributes('-topmost'):  # Only start checking if already topmost
#             check_window_topmost()  # Start checking if toggled on and already topmost
#         Topmost_lb.config(fg="#000000")  # Change text color to green
#         Topmost_lb.config(bg="#FFFFFF")  # Change text color to green
#     else:
#         ROOT.after_cancel(check_window_topmost)  # Cancel the checking if toggled off
#         Topmost_lb.config(fg="#FFFFFF")  # Change text color to white
#         Topmost_lb.config(bg="#000000")  # Change text color to white

checking = False

#! CPU / RAM / DRIVES / NET SPEED
def get_cpu_ram_info():
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage
def get_gpu_usage():
    # Get the first GPU device (you can modify this if you have multiple GPUs)
    device = ADLManager.getInstance().getDevices()[0]
    # Get the current GPU usage
    gpu_usage = device.getCurrentUsage()
    return gpu_usage
def get_disk_info():
    disk_c_usage = psutil.disk_usage('C:').percent
    disk_d_usage = psutil.disk_usage('D:').percent
    return disk_c_usage, disk_d_usage
def get_net_speed():
    net_io = psutil.net_io_counters()
    upload_speed = convert_bytes(net_io.bytes_sent - get_net_speed.upload_speed_last)
    download_speed = convert_bytes(net_io.bytes_recv - get_net_speed.download_speed_last)
    get_net_speed.upload_speed_last = net_io.bytes_sent
    get_net_speed.download_speed_last = net_io.bytes_recv
    return upload_speed, download_speed
def convert_bytes(bytes):
    mb = bytes / (1024 * 1024)
    return f'{mb:.2f}'
def update_info_labels():
    cpu_usage, ram_usage = get_cpu_ram_info()
    gpu_usage = get_gpu_usage()
    disk_c_usage, disk_d_usage = get_disk_info()
    upload_speed, download_speed = get_net_speed()
    LB_CPU['text'] = f'{cpu_usage}%'
    LB_RAM['text'] = f'{ram_usage}%'
    LB_GPU.config(text=f'{gpu_usage}%')
    LB_DUC['text'] = f'\uf0a0 {disk_c_usage}%'
    LB_DUD['text'] = f'\uf0a0 {disk_d_usage}%'
    Upload_lb['text'] = f' ▲ {upload_speed} '
    Download_lb['text'] = f' ▼ {download_speed} '

    # Set background color based on GPU usage
    if gpu_usage == "0":
        LB_GPU.config(bg="#1d2027" , fg="#00ff21")
    elif float(gpu_usage) < 50:
        LB_GPU.config(bg="#1d2027" , fg="#00ff21")
    elif 10 <= float(gpu_usage) < 50:
        LB_GPU.config(bg="#00ff21" , fg="#000000")
    elif 50 <= float(gpu_usage) < 80:
        LB_GPU.config(bg="#00ff21" , fg="#000000")
    else:
        LB_GPU.config(bg="#00ff21" , fg="#FFFFFF")

    # Set background color based on upload speed
    if upload_speed == "0":
        Upload_lb.config(bg='#1d2027', fg="#FFFFFF")
    elif float(upload_speed) < 0.1:  # Less than 100 KB
        Upload_lb.config(bg='#1d2027', fg="#FFFFFF")
    elif 0.1 <= float(upload_speed) < 0.5:  # 100 KB to 499 KB
        Upload_lb.config(bg='#A8E4A8', fg="#000000")
    elif 0.5 <= float(upload_speed) < 1:  # 500 KB to 1 MB
        Upload_lb.config(bg='#67D567', fg='#000000')  # Normal green
    else:
        Upload_lb.config(bg='#32AB32', fg='#000000')  # Dark green
    # Set background color based on download speed
    if download_speed == "0":
        Download_lb.config(bg='#1d2027' , fg="#FFFFFF")
    elif float(download_speed) < 0.1:  # Less than 100 KB
        Download_lb.config(bg='#1d2027', fg="#FFFFFF")
    elif 0.1 <= float(download_speed) < 0.5:  # 100 KB to 499 KB
        Download_lb.config(bg='#A8E4A8', fg="#000000")
    elif 0.5 <= float(download_speed) < 1:  # 500 KB to 1 MB
        Download_lb.config(bg='#67D567', fg='#000000')  # Normal green
    else:
        Download_lb.config(bg='#32AB32', fg='#000000')  # Dark green

    #        # Write speed information to a text file
    # with open("d:\\netspeed_download_upload.log", "a") as logfile:
    #     logfile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Download: {download_speed}, Upload: {upload_speed}\n")

    # Change background and foreground color based on usage thresholds
    LB_RAM.config(bg='#ff934b' if ram_usage > 80 else '#1d2027', fg='#1d2027' if ram_usage > 80 else '#ff934b')
    LB_CPU.config(bg='#14bcff' if cpu_usage > 80 else '#1d2027', fg='#1d2027' if cpu_usage > 80 else '#14bcff')
    LB_DUC.config(bg='#f12c2f' if disk_c_usage > 90 else '#044568', fg='#FFFFFF' if disk_c_usage > 90 else '#fff')
    LB_DUD.config(bg='#f12c2f' if disk_d_usage > 90 else '#044568', fg='#FFFFFF' if disk_d_usage > 90 else '#fff')

    ROOT.after(1000, update_info_labels)
# Initialize static variables for network speed calculation
get_net_speed.upload_speed_last = 0
get_net_speed.download_speed_last = 0


#! Clear Button
def clear_screen():
    try:
        # Clear the screen
        os.system('cls' if os.name == 'nt' else 'clear')
        ascii_art = """
##################################################
************* Everything is clean ****************
##################################################
        """
        print(ascii_art)
    except Exception as e:
        print(f"Error clearing screen: {e}")


def get_system_uptime():
    uptime_seconds = psutil.boot_time()
    current_time = datetime.now().timestamp()
    uptime = current_time - uptime_seconds
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return int(hours), int(minutes), int(seconds)
def format_uptime():
    hours, minutes, seconds = get_system_uptime()
    return f"\udb81\udf8c {hours:02d}:{minutes:02d}:{seconds:02d}"
def update_uptime_label():
    uptime_str = format_uptime()
    uptime_label.configure(text=f"{uptime_str}")
    uptime_label.after(1000, update_uptime_label)



def Lockbox_update_label(LockBox_lb):
    path = "d:/tt/"
    if os.path.exists(path):
        status = "\uf13e"
        color = "#f44336"
    else:
        status = "\uf023"
        color = "#4CAF50"
    LockBox_lb.config(text=status, fg=color, font=("JetBrainsMono NFP", 16, "bold"))
    LockBox_lb.after(1000, lambda: Lockbox_update_label(LockBox_lb))


# def compare_path_file():
#     source_dest_pairs = {
# "komorebi"       :(komorebi_src    ,komorebi_dst    ),
# # "glaze-wm"       :(glazewm_src     ,glazewm_dst     ),
# # "Nilesoft"       :(Nilesoft_src    ,Nilesoft_dst    ),
# # "whkd"           :(whkd_src        ,whkd_dst        ),
# "pwshH"          :(pwshH_src       ,pwshH_dst       ),
# "terminal"       :(terminal_src    ,terminal_dst    ),
# "rclone_config"  :(rclone_src      ,rclone_dst      ),
# "pwsh_profile"   :(pwsh_profile_src,pwsh_profile_dst),
# "ProwlarrDB"        :(ProwlarrDB_src     ,ProwlarrDB_dst     ),
# "RadarrDB"          :(RadarrDB_src       ,RadarrDB_dst       ),
# "SonarrDB"          :(SonarrDB_src       ,SonarrDB_dst       ),
# # "br_cf"          :(br_cf_src       ,br_cf_dst       ),
# # "br_db"          :(br_db_src       ,br_db_dst       ),
# # "Pr_cf"          :(Pr_cf_src       ,Pr_cf_dst       ),
# # "Rr_cf"          :(Rr_cf_src       ,Rr_cf_dst       ),
# # "Sr_cf"          :(Sr_cf_src       ,Sr_cf_dst       ),
# "RssDB"         :(Rss_db_src      ,Rss_db_dst      ),
# "RssCF"         :(Rss_cf_src      ,Rss_cf_dst      ),
#     }
#     is_all_same = True
#     names = []
#     for name, (source, dest) in source_dest_pairs.items():
#         if os.path.isdir(source) and os.path.isdir(dest):
#             dcmp = filecmp.dircmp(source, dest)
#             if dcmp.diff_files or dcmp.left_only or dcmp.right_only:
#                 is_all_same = False
#                 names.append(name)
#         elif os.path.isfile(source) and os.path.isfile(dest):
#             if not filecmp.cmp(source, dest):
#                 is_all_same = False
#                 names.append(name)
#         else:
#             is_all_same = False
#             names.append(name)
#     if is_all_same:
#         emoji = "✅"
#         name = "✅"
#     else:
#         emoji = "❌"
#         names_per_row = 4
#         formatted_names = [", ".join(names[i:i + names_per_row]) for i in range(0, len(names), names_per_row)]
#         name = "\n".join(formatted_names)
#     Changes_Monitor_lb.config(text=f"{name}")
#     Changes_Monitor_lb.after(1000, compare_path_file)


def get_cpu_core_usage():
    # Get CPU usage for each core
    cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
    return cpu_usage_per_core
def update_cpu_core_bars():
    # Get CPU usage for each core
    cpu_core_usage = get_cpu_core_usage()
    # Update the bars for each CPU core
    for i, usage in enumerate(cpu_core_usage):
        core_bar = cpu_core_bars[i]
        # Clear the previous bar
        core_bar.delete("all")
        # Calculate the half height of the bar based on usage percentage
        bar_height = int((usage / 100) * (BAR_HEIGHT / 2))
        # Determine the color based on usage percentage
        bar_color = determine_color(usage)
        # Draw the bar with the determined color from the center vertically
        core_bar.create_rectangle(0, (BAR_HEIGHT / 2) - bar_height, BAR_WIDTH, (BAR_HEIGHT / 2) + bar_height, fill=bar_color)
    # Schedule the next update
    ROOT.after(1000, update_cpu_core_bars)
def determine_color(usage):
    if usage >= 90:
        return "#8B0000"  # Dark red for usage >= 90%
    elif usage >= 80:
        return "#f12c2f"  # Red for usage >= 80%
    elif usage >= 50:
        return "#ff9282"  # Light red for usage >= 50%
    else:
        return "#14bcff"  # Default color
BAR_WIDTH = 8
BAR_HEIGHT = 25





#! ALL Boxes
ROOT1 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT1.pack(side="left", pady=(2,2),padx=(5,1),  anchor="w", fill="x")

ROOT2 = tk.Frame(MAIN_FRAME, bg="#1d2027")
ROOT2.pack(side="right", pady=(2,2),padx=(5,1), anchor="e", fill="x")

#! ██╗     ███████╗███████╗████████╗
#! ██║     ██╔════╝██╔════╝╚══██╔══╝
#! ██║     █████╗  █████╗     ██║
#! ██║     ██╔══╝  ██╔══╝     ██║
#! ███████╗███████╗██║        ██║
#! ╚══════╝╚══════╝╚═╝        ╚═╝

uptime_label=CTkLabel(ROOT1, text="", corner_radius=3, width=100,height=20,  text_color="#6bc0f8",fg_color="#1d2027", font=("JetBrainsMono NFP" ,16,"bold"))
uptime_label.pack(side="left",padx=(0,5),pady=(1,0))
uptime_label.bind("<Button-1>", lambda e: subprocess.Popen("timedate.cpl", shell=True))

# Load dynamic buttons for ROOT1
for idx, btn_cfg in enumerate(CONFIG.get("buttons_left", [])):
    create_dynamic_button(ROOT1, btn_cfg, "buttons_left", idx)



#! FFMPEG
# FFMPEG_bt = CTkButton(ROOT1, text="\uf07cffmpeg",width=0, command=lambda:switch_to_frame(FR_FFmpeg , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# FFMPEG_bt.pack(side="left")
# FR_FFmpeg = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FR_FFmpeg.pack_propagate(True)
# BoxForFFmpeg = tk.Frame(FR_FFmpeg, bg="#1d2027")
# BoxForFFmpeg.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
# back_ffmpeg=tk.Button(BoxForFFmpeg,text="\ueb6f",width=0,bg="#1D2027",fg="#FFFFFF",command=lambda:switch_to_frame (MAIN_FRAME,FR_FFmpeg))
# back_ffmpeg.pack(side="left" )
# def ffmpeg(FR_FFmpeg):
#     Trim_bt          =tk.Button(BoxForFFmpeg,text="Trim"          ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_trim        ); Trim_bt.pack          (side="left",padx=(0,0))
#     Convert_bt       =tk.Button(BoxForFFmpeg,text="Convert"       ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_convert     ); Convert_bt.pack       (side="left",padx=(0,0))
#     Dimension_bt     =tk.Button(BoxForFFmpeg,text="Dimension"     ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_dimension   ); Dimension_bt.pack     (side="left",padx=(0,0))
#     Imagedimension_bt=tk.Button(BoxForFFmpeg,text="Imagedimension",width=0,fg="#FFFFFF",bg="#1D2027", command=lambda: subprocess.Popen(["cmd /c start C:\\@delta\\ms1\\scripts\\ffmpeg\\imgdim.ps1"], shell=True)) ; Imagedimension_bt.pack(side="left",padx=(0,0))
#     Merge_bt         =tk.Button(BoxForFFmpeg,text="Merge"         ,width=0,fg="#FFFFFF",bg="#1D2027",command=start_merge       ); Merge_bt.pack         (side="left",padx=(0,0))
# ffmpeg(FR_FFmpeg)

#! Find
# Find_bt = CTkButton(ROOT1, text="\uf07cfind",width=0, command=lambda:switch_to_frame(FR_Find , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# Find_bt.pack(side="left")
# FR_Find = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FR_Find.pack_propagate(True)
# BoxForFind = tk.Frame(FR_Find, bg="#1d2027")
# BoxForFind.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
# back_find=tk.Button(BoxForFind,text="\ueb6f",width=0 ,bg="#1D2027", fg="#FFFFFF", command=lambda:switch_to_frame(MAIN_FRAME,FR_Find))
# back_find.pack(side="left" ,padx=(0,0))
# def find(FR_Find):
#     Search_bt=tk.Label(BoxForFind, text="\uf422",bg="#1d2027",fg="#95c64d",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",16,"bold"))
#     Search_bt.pack(side="left",padx=(3,0),pady=(0,0))
#     Search_bt.bind("<Button-1>",fzf_search)
#     Search_bt.bind("<Control-Button-1>",edit_fzfSearch)

#     File_bt    =tk.Button(BoxForFind,text="File"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_file   ); File_bt.pack   (side="left" ,padx=(0,0))
#     Pattern_bt =tk.Button(BoxForFind,text="Pattern"    ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_pattern); Pattern_bt.pack(side="left" ,padx=(0,0))
#     Size_bt    =tk.Button(BoxForFind,text="Size"       ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_find_size   ); Size_bt.pack   (side="left" ,padx=(0,0))
#     FZFC_bt    =tk.Button(BoxForFind,text="FZF-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_c       ); FZFC_bt.pack   (side="left" ,padx=(0,0))
#     FZFD_bt    =tk.Button(BoxForFind,text="FZF-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_fzf_d       ); FZFD_bt.pack   (side="left" ,padx=(0,0))
#     # ackc_bt    =tk.Button(BoxForFind,text="ACK-C"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_c       ); ackc_bt.pack   (side="left" ,padx=(0,0)) #! removed from reference
#     # ackd_bt    =tk.Button(BoxForFind,text="ACK-D"      ,width=0 ,fg="#FFFFFF", bg="#1D2027", command=start_ack_d       ); ackd_bt.pack   (side="left" ,padx=(0,0)) #! removed from reference
# find(FR_Find)

# #! Desktop
# Desktop_bt = CTkButton(ROOT1, text="\uf07cDesktop",width=0, command=lambda:switch_to_frame(FR_Desktop , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0,hover_color="#1dd463", border_width=1, border_color="#FFFFFF", fg_color="#0099ff", text_color="#000000")
# Desktop_bt.pack(side="left")
# FR_Desktop = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FR_Desktop.pack_propagate(True)
# BoxForDesktop = tk.Frame(FR_Desktop, bg="#1d2027")
# BoxForDesktop.pack(side="left", pady=(4,2),padx=(5,1),  anchor="w", fill="x")
# BACK=tk.Button(BoxForDesktop,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,FR_Desktop))
# BACK.pack(side="left" ,padx=(0,0))

# sonarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\sonarr-20x20.png"))
# radarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\radarr-20x20.png"))
# def Folder(FR_Desktop):
#     Sonarr_bt=tk.Label(BoxForDesktop, image=sonarr_img, compound=tk.TOP, text="", height=30, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
#     # Sonarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Sonarr"],shell=True)))
#     Sonarr_bt.pack(pady=(0,2), side="left", anchor="w", padx=(0,0))
#     Radarr_bt=tk.Label(BoxForDesktop, image=radarr_img, compound=tk.TOP, text="", height=50, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
#     # Radarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Radarr"],shell=True)))
#     Radarr_bt.pack(pady=(0,2), side="left", anchor="w", padx=(0,0))
# Folder(FR_Desktop)

# #! Worspace_1
# WorkSpace_1 = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# WorkSpace_1.pack_propagate(True)
# Enter_WS1 = CTkButton(ROOT1, text="\uf07cP", width=0, hover_color="#1dd463", command=lambda:switch_to_frame(WorkSpace_1 , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, border_color="#000000", fg_color="#bff130", text_color="#000")
# Enter_WS1.pack(side="left", padx=(1,1))
# BOX = tk.Frame(WorkSpace_1, bg="#1D2027")
# BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
# BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,WorkSpace_1))
# BACK.pack(side="left" ,padx=(0,0))

# #! EDIT SPACE
# EDIT_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# EDIT_FRAME.pack_propagate(True)
# ENTER_FRAME = CTkButton(ROOT1, text="\uf07cedit", width=0, command=lambda:switch_to_frame(EDIT_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# ENTER_FRAME.pack(side="left", padx=(1,1))
# BOX = tk.Frame(EDIT_FRAME, bg="#1D2027")
# BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
# BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,EDIT_FRAME))
# BACK.pack(side="left" ,padx=(0,0))
# def Folder(EDIT_FRAME):
#     MYPYGUI=tk.Button(BOX,text="MYPYGUI",width=0 ,fg="#ffffff", bg="#204892", command=lambda:(subprocess.Popen(["cmd /c Code C:\\@delta\\ms1\\mypygui.py"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     MYPYGUI.pack(side="left" ,padx=(0,0))
#     AHKEDIT=tk.Button(BOX,text="AHKSCRIPT",width=0 ,fg="#020202", bg="#5f925f", command=lambda:(subprocess.Popen(["cmd /c Code C:\\@delta\\ms1\\ahk_v2.ahk"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     AHKEDIT.pack(side="left" ,padx=(0,0))
#     KOMOREBIC=tk.Button(BOX,text="Komoreb",width=0 ,fg="#080808", bg="#7fc8f3", command=lambda:(subprocess.Popen(["cmd /c Code C:\\Users\\nahid\\komorebi.json"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     KOMOREBIC.pack(side="left" ,padx=(0,0))
#     MYHOMEHTML=tk.Button(BOX,text="myhome.html",width=0 ,fg="#080808", bg="#c7d449", command=lambda:(subprocess.Popen(["cmd /c Code C:\\ms2\\myhome.html"],shell=True), switch_to_frame(MAIN_FRAME,EDIT_FRAME)))
#     MYHOMEHTML.pack(side="left" ,padx=(0,0))
# Folder(EDIT_FRAME)

#! Function SPACE
# FUNCTION_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=1920)
# FUNCTION_FRAME.pack_propagate(True)
# ENTER_FRAME = CTkButton(ROOT1, text="\uf07cF", width=0, command=lambda:switch_to_frame(FUNCTION_FRAME , MAIN_FRAME), font=("JetBrainsMono NFP",14,"bold"), corner_radius=0, border_width=1, hover_color="#6824b6", border_color="#000000", fg_color="#1d2027", text_color="#ffdb75")
# ENTER_FRAME.pack(side="left", padx=(1,1))
# BOX = tk.Frame(FUNCTION_FRAME, bg="#1D2027")
# BOX.pack(side="top", pady=(4,2),padx=(5,1), anchor="center", fill="x")
# BACK=tk.Button(BOX,text="\ueb6f",width=0 ,bg="#1d2027", fg="#ffffff", command=lambda:switch_to_frame(MAIN_FRAME,FUNCTION_FRAME))
# BACK.pack(side="left" ,padx=(0,0))
# def Folder(FUNCTION_FRAME):
#         # Function to simulate key press
#         # def send_f13():
#         #     keyboard.send('f13')
#         # F13=tk.Button(BOX,text="F13",width=0 ,fg="#ffffff", bg="#204892", command=send_f13)
#         # F13.pack(side="left" ,padx=(0,0))

#         # def send_f15():
#         #     keyboard.send('f15')
#         # F15=tk.Button(BOX,text="F15",width=0 ,fg="#ffffff", bg="#204892", command=send_f15)
#         # F15.pack(side="left" ,padx=(0,0))

#         def powertoys_ruler():
#             keyboard.press_and_release('win+shift+m')
#         TOY_RULER=tk.Button(BOX,text="\uee11",width=0 ,fg="#ffffff", bg="#204892", command=powertoys_ruler)
#         TOY_RULER.pack(side="left" ,padx=(0,0))

#         def powertoys_mousecrosshair():
#             keyboard.press_and_release('win+alt+p')
#         TOY_MCROSSHAIR=tk.Button(BOX,text="\uf245",width=0 ,fg="#ffffff", bg="#204892", command=powertoys_mousecrosshair)
#         TOY_MCROSSHAIR.pack(side="left" ,padx=(0,0))

#         def powertoys_TextExtract():
#             keyboard.press_and_release('win+shift+f')
#         TOY_TEXTEXTRACT=tk.Button(BOX,text="\ueb69",width=0 ,fg="#ffffff", bg="#204892", command=powertoys_TextExtract)
#         TOY_TEXTEXTRACT.pack(side="left" ,padx=(0,0))

#         def capture2text():
#             is_running = any(proc.name() == "Capture2Text.exe" for proc in psutil.process_iter())
#             if not is_running:
#                 subprocess.Popen(r"C:\Users\nahid\scoop\apps\Capture2Text\current\Capture2Text.exe")
#                 time.sleep(2)  # Wait 2 seconds if the app had to be started
#             else:
#                 time.sleep(1)  # Wait 1 second if the app is already running
#             keyboard.press_and_release('win+ctrl+alt+shift+q')
#         CAPTURE2_TEXTEXTRACT=tk.Button(BOX,text="\ueb69",width=0 ,fg="#db1725", bg="#204892", command=capture2text)
#         CAPTURE2_TEXTEXTRACT.pack(side="left" ,padx=(0,0))

# Folder(FUNCTION_FRAME)

#! Worspace_3
SEPARATOR=tk.Label(ROOT1,text="[",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",font=("JetBrainsMono NFP",18,"bold"))
SEPARATOR.pack(side="left",padx=(3,0),pady=(0,0))

CONFIG = load_config()

#! Github status
# Define your repositories here
queue = Queue()
repos = CONFIG.get("git_repos", [])

status_labels = {}

def check_git_status(git_path, queue):
    if not os.path.exists(git_path):
        queue.put((git_path, "Invalid", "#000000"))
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    
    label_text = next((r["label"] for r in repos if r["path"] == git_path), "?")
    
    if "nothing to commit, working tree clean" in git_status.stdout:
        queue.put((git_path, label_text, "#00ff21"))  # Green
    else:
        queue.put((git_path, label_text, "#fe1616"))  # Red


def show_git_changes(git_path):
    if not os.path.exists(git_path):
        print("Invalid path")
        return
    os.chdir(git_path)
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "git status && git diff --stat"])

def git_backup(event):
    commands = " ; ".join([f"{r['path']}\\scripts\\Github\\{r['name']}u.ps1" for r in repos])
    subprocess.Popen([
        "Start", "pwsh", "-NoExit", "-Command",
        f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; {commands} ; cd ~}}"
    ], shell=True)

def delete_git_lock_files(event=None):
    for repo in repos:
        lock_file = os.path.join(repo["path"], ".git", "index.lock")
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"Deleted: {lock_file}")
            else:
                print(f"File not found: {lock_file}")
        except Exception as e:
            print(f"Error deleting {lock_file}: {e}")

def update_status():
    while True:
        for repo in repos:
            check_git_status(repo["path"], queue)
        time.sleep(1)

def update_gui():
    while True:
        try:
            git_path, text, color = queue.get_nowait()
            for repo in repos:
                if git_path == repo["path"]:
                    status_labels[repo["name"]].config(text=text, fg=color)
        except:
            pass
        time.sleep(0.1)

# Git Backup All Icon
bkup = tk.Label(ROOT1, text="\udb80\udea2", bg="#1d2027", fg="#009fff", font=("JetBrainsMono NFP", 18, "bold"))
bkup.pack(side="left")
bkup.bind("<Button-1>", git_backup)

# Add repo-specific labels and bindings dynamically
for repo in repos:
    label = tk.Label(
        ROOT1, bg="#1d2027", fg="#FFFFFF",
        font=("JetBrainsMono NFP", 12, "bold"), text=repo["label"]
    )
    label.pack(side="left")
    label.bind("<Button-1>", lambda e, p=repo["path"]: subprocess.Popen(
        ["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd {p.replace(os.sep, '/')} ; gitter}}"], shell=True
    ))
    # Ctrl + Left click → open repo folder in Explorer
    label.bind("<Control-Button-1>", lambda e, p=repo["path"]: subprocess.Popen(
        f'explorer "{p}"', shell=True
    ))
    label.bind("<Button-3>", lambda e, p=repo["path"]: subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=p, shell=True))
    label.bind("<Control-Button-3>", lambda e, p=repo["path"]: subprocess.Popen(
        ["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd {p.replace(os.sep, '/')} ; git restore . }}"], shell=True
    ))
    status_labels[repo["name"]] = label

# Git Lock File Cleaner Icon
DelGitIgnore = tk.Label(ROOT1, text="\udb82\udde7", bg="#1d2027", fg="#ffffff", font=("JetBrainsMono NFP", 18, "bold"))
DelGitIgnore.pack(side="left")
DelGitIgnore.bind("<Button-1>", delete_git_lock_files)

#! For Github Status
status_thread = threading.Thread(target=update_status, daemon=True)
gui_thread = threading.Thread(target=update_gui, daemon=True)
status_thread.start()
gui_thread.start()

SEPARATOR=tk.Label(ROOT1,text="]",bg="#1d2027",fg="#009fff",height=0,width=0,relief="flat",font=("JetBrainsMono NFP",18,"bold"))
SEPARATOR.pack(side="left",padx=(0,0),pady=(0,0))

# sonarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\sonarr-20x20.png"))
# Sonarr_bt=tk.Label(ROOT1, image=sonarr_img, compound=tk.TOP, text="", height=30, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
# Sonarr_bt=tk.Label(ROOT1, text="\udb81\udff4", height=0, width=0, bg="#000000", fg="#ffdb75", bd=0, highlightthickness=0, anchor="center", font=("Jetbrainsmono nfp", 20, "bold"))
# Sonarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Sonarr"],shell=True)))
# Sonarr_bt.pack(pady=(2,2), side="left", anchor="w", padx=(1,1))

# radarr_img = ImageTk.PhotoImage(Image.open("C:\\Users\\nahid\\OneDrive\\backup\\icon\\radarr-20x20.png"))
# Radarr_bt=tk.Label(ROOT1, image=radarr_img, compound=tk.TOP, text="", height=50, width=30, bg="#ffffff", fg="#ffffff", bd=0, highlightthickness=0, anchor="center", font=("calibri", 14, "bold"))
# Radarr_bt=tk.Label(ROOT1, text="\udb83\udfce", height=0, width=0, bg="#000000", fg="#ffdb75", bd=0, highlightthickness=0, anchor="center", font=("Jetbrainsmono nfp", 20, "bold"))
# Radarr_bt.bind("<Button-1>",lambda event:(subprocess.Popen(["explorer","D:\\Downloads\\@Radarr"],shell=True)))
# Radarr_bt.pack(pady=(2,2), side="left", anchor="w", padx=(1,10))

# Changes_Monitor_lb = tk.Label(ROOT1, text="", bg="#1d2027", fg="#68fc2d")
# Changes_Monitor_lb.pack(side="left",padx=(0,0),pady=(0,0))
# compare_path_file()
 



# Command config
# Ensure log folder exists
LOG_DIR = r"C:\Users\nahid\script_output\rclone"
os.makedirs(LOG_DIR, exist_ok=True)

commands = CONFIG.get("rclone_commands", {})

# Show log output in Microsoft Edit in a new PowerShell terminal
def on_label_click(event, cfg):
    try:
        subprocess.Popen([
            "powershell", "-NoExit", "-Command", f'edit "{cfg["log"]}"'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print(f"Error opening log file for {cfg['label']}: {e}")

def ctrl_left_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        # Use handle_action for consistency
        action = cfg.get("bindings", {}).get("Control-Button-1", {
            "type": "run_command",
            "cmd": cfg.get("left_click_cmd", "rclone sync src dst -P --fast-list --log-level INFO").replace("src", cfg["src"]).replace("dst", cfg["dst"])
        })
        handle_action(action)

def ctrl_right_click(event, cfg):
    if event.state & 0x0004:  # Ctrl key mask
        action = cfg.get("bindings", {}).get("Control-Button-3", {
            "type": "run_command",
            "cmd": cfg.get("right_click_cmd", "rclone sync dst src -P --fast-list").replace("src", cfg["src"]).replace("dst", cfg["dst"])
        })
        handle_action(action)

# Periodically check using rclone
rclone_status = {}  # key -> color
_rclone_cfg = load_config().get("rclone_settings", {"interval_min": 10, "simultaneous": True})
RCLONE_INTERVAL_MS = int(_rclone_cfg.get("interval_min", 10)) * 60000
RCLONE_SIMULTANEOUS = bool(_rclone_cfg.get("simultaneous", True))

def update_toggle_bt_color():
    if not rclone_status: return
    agg = "#06de22" if all(c == "#06de22" for c in rclone_status.values()) else "red"
    try: ROOT.after(0, lambda c=agg: rclone_toggle_bt.config(fg=c))
    except Exception: pass

def check_and_update(label, cfg):
    def run_check():
        actual_cmd = cfg["cmd"].replace("src", cfg["src"]).replace("dst", cfg["dst"])
        with open(cfg["log"], "w") as f:
            subprocess.run(actual_cmd, shell=True, stdout=f, stderr=f)
        with open(cfg["log"], "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        color = "#06de22" if "ERROR" not in content else "red"
        rclone_status[cfg["id"]] = color
        update_toggle_bt_color()
        try:
            ROOT.after(0, lambda c=color: label.config(text=cfg["label"], fg=c))
            ROOT.after(RCLONE_INTERVAL_MS, lambda: threading.Thread(target=run_check, daemon=True).start())
        except Exception:
            pass
    threading.Thread(target=run_check, daemon=True).start()

# Rclone popup panel
rclone_popup = None

def toggle_rclone_popup(event=None):
    global rclone_popup
    if rclone_popup and tk.Toplevel.winfo_exists(rclone_popup):
        rclone_popup.destroy()
        rclone_popup = None
        return

    rclone_popup = tk.Toplevel(ROOT)
    rclone_popup.overrideredirect(True)
    rclone_popup.configure(bg="#1d2027")
    rclone_popup.attributes("-topmost", True)

    frame = tk.Frame(rclone_popup, bg="#1d2027", highlightthickness=1, highlightbackground="red")
    frame.pack(fill="both", expand=True)

    for key, cfg in commands.items():
        if "id" not in cfg: cfg["id"] = key
        lbl = tk.Label(frame, width=0, bg="#1d2027", text=cfg["label"],
                       font=("JetBrainsMono NFP", 16, "bold"), cursor="hand2")
        lbl.pack(side="left", padx=(5, 5), pady=(2, 2))
        lbl.bind("<Button-1>", lambda e, c=cfg: on_label_click(e, c))
        lbl.bind("<Control-Button-1>", lambda e, c=cfg: ctrl_left_click(e, c))
        lbl.bind("<Control-Button-3>", lambda e, c=cfg: ctrl_right_click(e, c))
        lbl.bind("<Shift-Button-1>", lambda e, c=cfg: open_edit_gui(c, "rclone_commands"))
        # show cached status color if available
        cached = rclone_status.get(cfg.get("id", key))
        if cached: lbl.config(fg=cached)

    rclone_popup.update_idletasks()
    pw = rclone_popup.winfo_reqwidth()
    ph = rclone_popup.winfo_reqheight()
    bx = rclone_toggle_bt.winfo_rootx() + rclone_toggle_bt.winfo_width() // 2 - pw // 2
    by = ROOT.winfo_rooty()
    rclone_popup.geometry(f"{pw}x{ph}+{bx}+{by - ph - 1}")

    rclone_popup.bind("<FocusOut>", lambda e: rclone_popup.destroy() if rclone_popup else None)

rclone_toggle_bt = tk.Label(ROOT1, text="\uef2c", bg="#1d2027", fg="#fcfcfc",
                             font=("JetBrainsMono NFP", 20, "bold"), cursor="hand2")
rclone_toggle_bt.pack(side="left", padx=(5, 5))
rclone_toggle_bt.bind("<Button-1>", toggle_rclone_popup)

# Start background rclone status checks
def _start_rclone_checks():
    _items = list(commands.items())
    def _run_sequential(items):
        if not items: return
        _key, _cfg = items[0]
        if "id" not in _cfg: _cfg["id"] = _key
        _lbl = tk.Label(ROOT, text="")
        check_and_update(_lbl, _cfg)
        ROOT.after(100, lambda: _run_sequential(items[1:]))
    if RCLONE_SIMULTANEOUS:
        for _key, _cfg in _items:
            if "id" not in _cfg: _cfg["id"] = _key
            _lbl = tk.Label(ROOT, text="")
            check_and_update(_lbl, _cfg)
    else:
        _run_sequential(_items)
_start_rclone_checks()

def open_rclone_settings():
    CP_BG="#050505"; CP_PANEL="#111111"; CP_YELLOW="#FCEE0A"; CP_CYAN="#00F0FF"
    CP_RED="#FF003C"; CP_GREEN="#00ff21"; CP_DIM="#3a3a3a"; CP_TEXT="#E0E0E0"

    QSS = f"""
        QDialog, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
        }}
        QLineEdit:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}
        QPushButton {{
            background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 14px; font-weight: bold;
        }}
        QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
        QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
        QPushButton#btn_save {{ border-color: {CP_GREEN}; color: {CP_GREEN}; }}
        QPushButton#btn_save:hover {{ background-color: {CP_GREEN}; color: black; }}
        QGroupBox {{
            border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 8px; font-weight: bold; color: {CP_YELLOW};
        }}
        QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
        QCheckBox::indicator {{ width: 13px; height: 13px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
        QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
    """

    dlg = QDialog()
    dlg.setWindowTitle("Rclone Settings")
    dlg.resize(380, 200)
    dlg.setStyleSheet(QSS)
    dlg.setWindowFlags(dlg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(14, 14, 14, 14)
    layout.setSpacing(10)

    title = QLabel("// RCLONE SETTINGS")
    title.setStyleSheet(f"color: {CP_CYAN}; font-size: 12pt; font-weight: bold;")
    layout.addWidget(title)

    grp = QGroupBox("CHECK BEHAVIOUR")
    form = QFormLayout()
    form.setSpacing(8)
    grp.setLayout(form)

    cfg_now = load_config().get("rclone_settings", {"interval_min": 10, "simultaneous": True})

    interval_le = QLineEdit(str(cfg_now.get("interval_min", 10)))
    simul_chk   = QCheckBox("Run simultaneously")
    simul_chk.setChecked(bool(cfg_now.get("simultaneous", True)))

    form.addRow("INTERVAL (min)", interval_le)
    form.addRow("", simul_chk)
    layout.addWidget(grp)

    btn_save = QPushButton("SAVE")
    btn_save.setObjectName("btn_save")
    btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
    layout.addWidget(btn_save)

    def save():
        global RCLONE_INTERVAL_MS, RCLONE_SIMULTANEOUS
        try: mins = int(interval_le.text())
        except ValueError: mins = 10
        simul = simul_chk.isChecked()
        config = load_config()
        config["rclone_settings"] = {"interval_min": mins, "simultaneous": simul}
        save_config(config)
        RCLONE_INTERVAL_MS = mins * 60000
        RCLONE_SIMULTANEOUS = simul
        dlg.accept()

    btn_save.clicked.connect(save)
    dlg.exec()

rclone_settings_bt = tk.Label(ROOT1, text="", bg="#1d2027", fg="#808080",
                               font=("JetBrainsMono NFP", 14, "bold"), cursor="hand2")
rclone_settings_bt.pack(side="left", padx=(0, 5))
rclone_settings_bt.bind("<Button-1>", lambda e: open_rclone_settings())

# Add a permanent "ADD NEW" button to ROOT1
add_new_bt = tk.Label(ROOT1, text="+", bg="#1d2027", fg="#98c379", font=("JetBrainsMono NFP", 18, "bold"), cursor="hand2")
add_new_bt.pack(side="left", padx=(10, 5))
add_new_bt.bind("<Button-1>", lambda e: open_edit_gui({"text": "NEW", "fg": "#ffffff", "bg": "#1d2027", "id": f"btn_{int(time.time())}", "bindings": {}}, "buttons_left"))


# ms1_rclone_o0 = tk.Label(ROOT1,text="ms1", bg="#1d2027", fg="#cc5907", height=0, width=0, relief="flat", highlightthickness=0, highlightbackground="#ffffff", anchor="w", font=("JetBrainsMono NFP", 16, "bold"))
# ms1_rclone_o0.pack(side="left", padx=(0, 0), pady=(0, 0))
# ms1_rclone_o0.bind( "<Button-1>", lambda event=None: run_command( r'rclone sync C:/@delta/ms1/ o0:/ms1/ --exclude ".git/**" --exclude "__pycache__/**" -P --fast-list' ))


#! ██████╗ ██╗ ██████╗ ██╗  ██╗████████╗
#! ██╔══██╗██║██╔════╝ ██║  ██║╚══██╔══╝
#! ██████╔╝██║██║  ███╗███████║   ██║
#! ██╔══██╗██║██║   ██║██╔══██║   ██║
#! ██║  ██║██║╚██████╔╝██║  ██║   ██║
#! ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝


# import requests
# import tkinter as tk
# import re

# ANDROID_URL = "http://mi9t:5002"
# LOW_BATTERY_THRESHOLD = 15
# UPDATE_INTERVAL = 60000  # 60 seconds
# def fetch_battery_percentage():
#     try:
#         response = requests.get(ANDROID_URL)
#         if response.ok:
#             match = re.search(r'(\d+)\s*%', response.text)
#             if match:
#                 return int(match.group(1))
#     except Exception as e:
#         print(f"Error fetching battery: {e}")
#     return None

# def update_status_battery_mi9t():
#     percent = fetch_battery_percentage()
#     if percent is not None:
#         Android_mi9t_battery.config(text=f"mi9t {percent}%")
#         if percent == 100:
#             Android_mi9t_battery.config(fg="black", bg="#58a6ff")
#         elif percent < LOW_BATTERY_THRESHOLD:
#             Android_mi9t_battery.config(fg="white", bg="red")
#         else:
#             Android_mi9t_battery.config(fg="black", bg="#abec72")
#     else:
#         Android_mi9t_battery.config(
#             text="Error fetching battery",
#             fg="white",
#             bg="gray"
#         )
#     ROOT2.after(UPDATE_INTERVAL, update_status_battery_mi9t)

# Android_mi9t_battery = tk.Label(ROOT2, text="Loading...", font=("Jetbrainsmono nfp", 10, "bold"), width=10)
# Android_mi9t_battery.pack(side="left", padx=(3,10), pady=(0,0))
# # Start updates
# update_status_battery_mi9t()




# UPDATE_INTERVAL_SEC = 60  # 600 seconds = 10 minutes
# PING_COMMAND = ["ping", "-n", "1", "-w", "1000", "192.168.0.103"]  # -n 1 = once, -w 1000 = 1s timeout

# def ping_mi9t():
#     def run_ping():
#         try:
#             result = subprocess.run(PING_COMMAND, capture_output=True, text=True, timeout=5)
#             output = result.stdout + result.stderr

#             if "Reply from" in output:
#                 update_ui("mi9t ✓", "black", "#abec72")  # green
#             elif "Request timed out" in output or "Destination host unreachable" in output:
#                 update_ui("mi9t ✗", "white", "red")  # red
#             else:
#                 update_ui("mi9t ?", "white", "gray")  # unknown
#         except Exception as e:
#             update_ui("Error", "white", "gray")
#             print(f"Ping error: {e}")
#         finally:
#             ROOT2.after(UPDATE_INTERVAL_SEC * 1000, ping_mi9t)

#     threading.Thread(target=run_ping, daemon=True).start()

# def update_ui(text, fg, bg):
#     Android_mi9t_status.config(text=text, fg=fg, bg=bg)


# Android_mi9t_status = tk.Label(ROOT2, text="Loading...", font=("Jetbrainsmono NFP", 10, "bold"), width=10)
# Android_mi9t_status.pack(side="left", padx=(3,10), pady=(0,0))

# ping_mi9t()







Download_lb=tk.Label(ROOT2,bg="#000000",fg="#080505",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Download_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Download_lb.bind("<Button-1>", lambda event: subprocess.Popen(["sniffnet"], shell=True))

Upload_lb=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =0,relief="flat",highlightthickness=0,highlightbackground="#ffffff",anchor ="w",font=("JetBrainsMono NFP",10,"bold"),text="")
Upload_lb.pack(side="left",padx=(3,0 ),pady=(0,0))
Upload_lb.bind("<Button-1>", lambda event: subprocess.Popen(["sniffnet"], shell=True))

LB_CPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_CPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_CPU.bind( "<Button-1>", lambda event=None: subprocess.Popen([sys.executable, r'C:\@delta\ms1\scripts\process\process_viewer.py']))
LB_CPU.bind("<Control-Button-1>",lambda event=None: subprocess.Popen(['code', r'C:\@delta\ms1\scripts\process\process_viewer.py']))
cpu_core_frame =CTkFrame(ROOT2,corner_radius=5,bg_color="#1d2027",border_width=1,border_color="#000000", fg_color="#fff")
cpu_core_frame.pack(side="left",padx=(3,0),pady=(0,0))
# LB_CPU.bind("<Button-1>", lambda event: subprocess.Popen( [r"C:\WINDOWS\SYSTEM32\cmd.exe", "/c", "start" ,"powershell", "-ExecutionPolicy", "Bypass", "-File", r"C:\@delta\ms1\scripts\pk.ps1"], shell=True))
# LB_CPU.bind("<Button-3>", lambda event: subprocess.Popen( [r"C:\WINDOWS\SYSTEM32\cmd.exe", "/c", "start" ,"powershell", "-ExecutionPolicy", "Bypass", "-File", r"C:\@delta\ms1\scripts\pk2.ps1"], shell=True))
# LB_CPU.bind("<Control-Button-1>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\pk.ps1"], shell=True))
# LB_CPU.bind("<Control-Button-3>",lambda event:subprocess.Popen(["cmd /c code C:\\@delta\\ms1\\scripts\\pk2.ps1"], shell=True))

LB_GPU=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#00ff21",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_GPU.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_GPU.bind("<Button-1>", lambda e: subprocess.Popen("start ms-settings:display", shell=True))

LB_RAM=tk.Label(ROOT2,bg="#000000",fg="#FFFFFF",height=0,width =5,relief="flat",highlightthickness=1,highlightbackground="#f08d0c",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_RAM.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_RAM.bind("<Button-1>", lambda e: subprocess.Popen("taskmgr", shell=True))

LB_DUC=tk.Label(ROOT2,height=0,width =8,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DUC.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DUC.bind("<Button-1>", lambda e: subprocess.Popen("explorer C:\\", shell=True))

LB_DUD=tk.Label(ROOT2,height=0,width =8,relief="flat",highlightthickness=1,highlightbackground="#1b8af1",anchor ="center",font=("JetBrainsMono NFP",10,"bold"),text="")
LB_DUD.pack(side="left",padx=(3,0 ),pady=(0,0))
LB_DUD.bind("<Button-1>", lambda e: subprocess.Popen("explorer D:\\", shell=True))

# Topmost_lb=tk.Label(ROOT2,text="\udb81\udc03",bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
# Topmost_lb.pack(side="left",padx=(3,0),pady=(0,0))
# Topmost_lb.bind  ("<Button-1>",lambda event:toggle_checking())

# CLEAR=tk.Label(ROOT2, text="\ueabf",bg="#1d2027",fg="#FFFFFF",height=0,width=0,relief="flat",anchor="w",font=("JetBrainsMono NFP",12,"bold"))
# CLEAR.pack(side="left",padx=(3,0),pady=(0,0))
# CLEAR.bind("<Button-1>",lambda event:clear_screen())











countdown_active = False
shutdown_thread = None
alarm_window = None
blinking = False
last_countdown_type = None  # To store the last chosen type (1 for alarm, 2 for shutdown)
last_countdown_minutes = None  # To store the last entered minutes

def shutdown_timer(minutes):
    global countdown_active
    countdown_time = minutes * 60
    while countdown_time > 0:
        if not countdown_active:
            time_left_label.config(text="Timer")
            return
        minutes_left = int(countdown_time) // 60
        seconds_left = int(countdown_time) % 60
        time_left_label.config(text=f"\udb86\udee1:{minutes_left:02}:{seconds_left:02}")
        time_left_label.update()
        time.sleep(1)
        countdown_time -= 1
    if countdown_active:
        os.system("shutdown /s /f /t 1")
        countdown_active = False
        time_left_label.config(text="Timer")

def alarm_timer(minutes):
    global countdown_active
    countdown_time = minutes * 60
    while countdown_time > 0:
        if not countdown_active:
            time_left_label.config(text="Timer")
            return
        minutes_left = int(countdown_time) // 60
        seconds_left = int(countdown_time) % 60
        time_left_label.config(text=f"\udb86\udee1:{minutes_left:02}:{seconds_left:02}")
        time_left_label.update()
        time.sleep(1)
        countdown_time -= 1
    if countdown_active:
        show_big_alarm()
        countdown_active = False
        time_left_label.config(text="Timer")

# Show blinking alarm in a new window
def show_big_alarm():
    global alarm_window, blinking

    alarm_window = tk.Toplevel(ROOT)
    alarm_window.title("ALARM!")
    alarm_window.geometry("600x300")
    alarm_window.configure(bg="#1d2027")
    alarm_window.attributes("-topmost", True)
    alarm_window.overrideredirect(True)
    alarm_window.resizable(False, False)
    width = alarm_window.winfo_width()
    height = alarm_window.winfo_height()
    x = (alarm_window.winfo_screenwidth() // 2) - (width // 2)
    y = (alarm_window.winfo_screenheight() // 2) - (height // 2)
    alarm_window.geometry(f'{width}x{height}+{x}+{y}')

    label = tk.Label(
        alarm_window,
        text="ALARM! Time's up!",
        font=("JetBrainsMono NFP", 36, "bold"),
        fg="#ff0000",
        bg="#1d2027"
    )
    label.pack(expand=True)

    blinking = True
    blink_state = True

    def blink():
        nonlocal blink_state
        if blinking:
            label.config(fg="#ff0000" if blink_state else "#00aaff")
            blink_state = not blink_state
            alarm_window.after(500, blink)

    def stop_alarm(event=None):
        global blinking
        blinking = False
        alarm_window.destroy()

    alarm_window.bind("<Button-1>", stop_alarm)
    blink()

# Custom input for countdown minutes
def get_countdown_input():
    input_window = tk.Toplevel(ROOT)
    input_window.title("Enter Countdown Minutes")
    input_window.geometry("300x100")
    input_window.grab_set()

    # Center the window on the screen
    input_window.update_idletasks()
    w = 300
    h = 100
    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()
    x = (screen_width // 2) - (w // 2)
    y = (screen_height // 2) - (h // 2)
    input_window.geometry(f"{w}x{h}+{x}+{y}")

    label = tk.Label(input_window, text="Enter minutes for the countdown:")
    label.pack(pady=5)

    minutes_entry = tk.Entry(input_window, font=("JetBrainsMono NFP", 14))
    minutes_entry.pack(pady=5)
    minutes_entry.focus()

    result = {"minutes": None}

    def on_submit(event=None):  # Accept optional event for key binding
        try:
            val = float(minutes_entry.get())
            if val > 0:
                result["minutes"] = val
                input_window.destroy()
        except ValueError:
            error_label.config(text="Enter a valid number > 0")

    submit_btn = tk.Button(input_window, text="Start", command=on_submit)
    submit_btn.pack(pady=5)

    error_label = tk.Label(input_window, text="", fg="red")
    error_label.pack()

    # Bind Enter key to submit
    minutes_entry.bind("<Return>", on_submit)

    input_window.wait_window()
    return result["minutes"]


# Main click handler
def start_countdown_option(event=None):
    global countdown_active, shutdown_thread, last_countdown_type, last_countdown_minutes
    choice = simpledialog.askinteger("Select Timer Type", "Choose an option:\n1 - Countdown Alarm\n2 - Countdown Shutdown")
    if choice == 1:
        if countdown_active:
            countdown_active = False
            time_left_label.config(text="Timer")
            return
        minutes = get_countdown_input()
        if minutes:
            countdown_active = True
            last_countdown_type = 1
            last_countdown_minutes = minutes
            shutdown_thread = threading.Thread(target=alarm_timer, args=(minutes,))
            shutdown_thread.start()
            time_left_label.config(text=f"\udb86\udee1:{minutes:02}:00")
    elif choice == 2:
        if countdown_active:
            countdown_active = False
            time_left_label.config(text="Timer")
            return
        minutes = get_countdown_input()
        if minutes:
            countdown_active = True
            last_countdown_type = 2
            last_countdown_minutes = minutes
            shutdown_thread = threading.Thread(target=shutdown_timer, args=(minutes,))
            shutdown_thread.start()
            time_left_label.config(text=f"\udb86\udee1:{minutes:02}:00")

# Function to run the last used countdown
def run_last_countdown():
    global countdown_active, shutdown_thread, last_countdown_type, last_countdown_minutes
    if last_countdown_type is None or last_countdown_minutes is None:
        # Optionally, inform the user that no previous countdown exists
        print("No previous countdown to run.") # Or show a message box
        return

    if countdown_active:
        countdown_active = False
        time_left_label.config(text="Timer")
        # Give a moment for the current thread to stop if it's running
        if shutdown_thread and shutdown_thread.is_alive():
            shutdown_thread.join(timeout=1) # Wait briefly for the thread to terminate
        time.sleep(0.1) # Small delay to ensure state update

    countdown_active = True
    if last_countdown_type == 1:
        shutdown_thread = threading.Thread(target=alarm_timer, args=(last_countdown_minutes,))
        shutdown_thread.start()
        time_left_label.config(text=f"Time left: {int(last_countdown_minutes):02}:00 (Last Alarm)")
    elif last_countdown_type == 2:
        shutdown_thread = threading.Thread(target=shutdown_timer, args=(last_countdown_minutes,))
        shutdown_thread.start()
        time_left_label.config(text=f"Time left: {int(last_countdown_minutes):02}:00 (Last Shutdown)")


# Add this to your layout wherever your buttons/widgets go
time_left_label = tk.Label(
    ROOT2,
    text="\udb86\udee1",
    font=("JetBrainsMono NFP", 16, "bold"),
    fg="#fc6a35",
    bg="#1d2027",
    cursor="hand2",
    relief="flat"
)
time_left_label.pack(side="left", padx=(10, 0), pady=(0, 0))
time_left_label.bind("<Button-1>", start_countdown_option)

# New "Run Last" button
run_last_button = tk.Button(
    ROOT2,
    text="\udb86\udee5",
    font=("JetBrainsMono NFP", 16),
    command=run_last_countdown,
    fg="#50fa7b",
    bg="#1d2027",
    activeforeground="#ffffff",
    activebackground="#2e7d32",
    relief="flat"
)
run_last_button.pack(side="left", padx=(0, 0), pady=(0, 0))









def force_shutdown(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
    if confirmed:
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"])
        # subprocess.run(["shutdown", "/s", "/t", "0"])
def force_restart(event):
    confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
    if confirmed:
        subprocess.run(["shutdown", "/r", "/f", "/t", "0"])
        # subprocess.run(["shutdown", "/r", "/t", "0"])

# Load dynamic buttons for ROOT2
for idx, btn_cfg in enumerate(CONFIG.get("buttons_right", [])):
    create_dynamic_button(ROOT2, btn_cfg, "buttons_right", idx)

LB_R=None # Dummy to avoid errors if referenced elsewhere
LB_XXX=None # Dummy to avoid errors if referenced elsewhere

#! Slider Left
#! Slider Right


cpu_core_bars = []
for i in range(psutil.cpu_count()):
    frame = CTkFrame(cpu_core_frame, bg_color="#1d2027")
    frame.pack(side="left", padx=(0, 0), pady=0)
    core_bar = CTkCanvas(frame, bg="#333333", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="top")
    cpu_core_bars.append(core_bar)
update_cpu_core_bars()



update_uptime_label()
update_info_labels()
# check_window_topmost()
# Lockbox_update_label(LockBox_lb)
calculate_time_to_appear(start_time)

ROOT.mainloop()
