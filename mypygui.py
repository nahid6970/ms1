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
CP_FONT = "Consolas"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "mypygui_config.json")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config from {CONFIG_FILE}: {e}")
        return {}

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config to {CONFIG_FILE}: {e}")

CONFIG = load_config()

def handle_action(action_cfg):
    if not action_cfg: return
    atype = action_cfg.get("type")
    cmd = action_cfg.get("cmd")
    cwd = action_cfg.get("cwd")
    admin = action_cfg.get("admin", False)
    hide = action_cfg.get("hide", False)
    
    if admin:
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

def open_edit_gui(item_cfg, category, index=None):
    edit_win = tk.Toplevel(ROOT)
    edit_win.title(f"Edit {item_cfg.get('id', 'Item')}")
    edit_win.geometry("700x850")
    edit_win.configure(bg=CP_BG)
    edit_win.attributes("-topmost", True)

    canvas = tk.Canvas(edit_win, bg=CP_BG, highlightthickness=0)
    scrollbar = ttk.Scrollbar(edit_win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=CP_BG)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    fields = ["text", "fg", "bg", "id"]
    entries = {}
    for i, field in enumerate(fields):
        tk.Label(scroll_frame, text=field.upper(), fg=CP_YELLOW, bg=CP_BG, font=(CP_FONT, 10, "bold")).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        ent = tk.Entry(scroll_frame, width=50, bg=CP_PANEL, fg=CP_CYAN, insertbackground=CP_CYAN, font=(CP_FONT, 10), highlightthickness=1, highlightbackground=CP_DIM)
        ent.insert(0, str(item_cfg.get(field, "")))
        ent.grid(row=i, column=1, padx=10, pady=5, sticky="w")
        entries[field] = ent

    click_types = [
        ("Left Click", "Button-1"),
        ("Right Click", "Button-3"),
        ("Ctrl + Left Click", "Control-Button-1"),
        ("Ctrl + Right Click", "Control-Button-3")
    ]
    
    binding_inputs = {}
    current_row = len(fields)

    for label, key in click_types:
        frame = tk.LabelFrame(scroll_frame, text=label, fg=CP_YELLOW, bg=CP_BG, font=(CP_FONT, 11, "bold"), padx=10, pady=10, bd=1, relief="solid")
        frame.grid(row=current_row, column=0, columnspan=2, padx=10, pady=15, sticky="nsew")
        current_row += 1
        
        cfg = item_cfg.get("bindings", {}).get(key, {})
        
        tk.Label(frame, text="Command:", fg=CP_TEXT, bg=CP_BG, font=(CP_FONT, 10)).grid(row=0, column=0, sticky="w")
        cmd_ent = tk.Entry(frame, width=60, bg=CP_PANEL, fg=CP_CYAN, insertbackground=CP_CYAN, font=(CP_FONT, 10), highlightthickness=1, highlightbackground=CP_DIM)
        cmd_ent.insert(0, cfg.get("cmd", cfg.get("func", "")))
        cmd_ent.grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(frame, text="Type:", fg=CP_TEXT, bg=CP_BG, font=(CP_FONT, 10)).grid(row=1, column=0, sticky="w")
        type_var = tk.StringVar(value=cfg.get("type", "subprocess"))
        type_combo = ttk.Combobox(frame, textvariable=type_var, values=["subprocess", "run_command", "python", "function"], state="readonly", width=20)
        type_combo.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        opt_frame = tk.Frame(frame, bg=CP_BG)
        opt_frame.grid(row=2, column=1, sticky="w")
        
        hide_var = tk.BooleanVar(value=cfg.get("hide", False))
        tk.Checkbutton(opt_frame, text="Hide Terminal", variable=hide_var, fg=CP_TEXT, bg=CP_BG, selectcolor=CP_PANEL, activebackground=CP_BG, activeforeground=CP_CYAN, font=(CP_FONT, 10)).pack(side="left")
        
        admin_var = tk.BooleanVar(value=cfg.get("admin", False))
        tk.Checkbutton(opt_frame, text="Run as Admin", variable=admin_var, fg=CP_TEXT, bg=CP_BG, selectcolor=CP_PANEL, activebackground=CP_BG, activeforeground=CP_CYAN, font=(CP_FONT, 10)).pack(side="left", padx=20)
        
        binding_inputs[key] = {
            "cmd": cmd_ent, "type": type_var, "hide": hide_var, "admin": admin_var
        }

    def save():
        for field in fields:
            item_cfg[field] = entries[field].get()
        new_bindings = {}
        for key, inputs in binding_inputs.items():
            cmd = inputs["cmd"].get()
            if not cmd: continue
            b_type = inputs["type"].get()
            new_bindings[key] = {
                "type": b_type, "hide": inputs["hide"].get(), "admin": inputs["admin"].get()
            }
            if b_type == "function": new_bindings[key]["func"] = cmd
            else: new_bindings[key]["cmd"] = cmd
        item_cfg["bindings"] = new_bindings
        config = load_config()
        if category in config:
            if index is not None: config[category][index] = item_cfg
            else: config[category][item_cfg["id"]] = item_cfg
        save_config(config)
        edit_win.destroy()
        if messagebox.askyesno("Restart", "Settings saved. Restart GUI to apply?"): restart()

    def delete():
        if not messagebox.askyesno("Delete", f"Are you sure you want to delete '{item_cfg.get('id', 'this item')}'?"): return
        config = load_config()
        if category in config:
            if isinstance(config[category], list):
                if index is not None and 0 <= index < len(config[category]): config[category].pop(index)
                else:
                    item_id = item_cfg.get("id")
                    config[category] = [item for item in config[category] if item.get("id") != item_id]
            else:
                item_id = item_cfg.get("id")
                if item_id in config[category]: del config[category][item_id]
        save_config(config)
        edit_win.destroy()
        if messagebox.askyesno("Restart", "Item deleted. Restart GUI to apply?"): restart()

    btn_frame = tk.Frame(scroll_frame, bg=CP_BG)
    btn_frame.grid(row=current_row, column=0, columnspan=2, pady=30, sticky="nsew")
    tk.Button(btn_frame, text="SAVE CONFIGURATION", command=save, bg=CP_YELLOW, fg="black", font=(CP_FONT, 12, "bold"), pady=10).pack(side="left", fill="x", expand=True, padx=(0, 5))
    tk.Button(btn_frame, text="DELETE ITEM", command=delete, bg=CP_RED, fg="black", font=(CP_FONT, 12, "bold"), pady=10).pack(side="left", fill="x", expand=True, padx=(5, 0))

def create_dynamic_button(parent, btn_cfg, category, index=None):
    font = tuple(btn_cfg.get("font", [CP_FONT, 14, "bold"]))
    bg = btn_cfg.get("bg", CP_PANEL)
    fg = btn_cfg.get("fg", CP_TEXT)
    lbl = tk.Label(parent, text=btn_cfg.get("text", ""), bg=bg, fg=fg, font=font, relief="flat", cursor="hand2")
    lbl.pack(side="left", padx=(1, 1))
    bindings = btn_cfg.get("bindings", {})
    for event, action in bindings.items():
        if isinstance(action, str): lbl.bind(f"<{event}>", lambda e, a=action: handle_action({"type": "function", "func": a}))
        else: lbl.bind(f"<{event}>", lambda e, a=action: handle_action(a))
    lbl.bind("<Shift-Button-1>", lambda e: open_edit_gui(btn_cfg, category, index))
    return lbl

def calculate_time_to_appear(start_time):
    print(f"Time taken to appear: {time.time() - start_time:.2f} seconds")

start_time = time.time()

def start_drag(event): drag_data["x"], drag_data["y"] = event.x, event.y
def stop_drag(event): drag_data["x"] = drag_data["y"] = None
def do_drag(event):
    if drag_data["x"] is not None:
        x, y = (event.x - drag_data["x"] + ROOT.winfo_x(), event.y - drag_data["y"] + ROOT.winfo_y())
        ROOT.geometry(f"+{x}+{y}")

def switch_to_frame(frame_to_show, frame_to_hide):
    frame_to_hide.pack_forget()
    frame_to_show.pack()

def set_console_title(title): ctypes.windll.kernel32.SetConsoleTitleW(title)

def run_command(command, admin=False, hide=False, no_exit=True):
    if admin:
        try:
            executable = "pwsh"
            args = f"{'-NoExit ' if no_exit else ''}-Command \"{command}\""
            ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, args, None, 1 if not hide else 0)
        except Exception as e: print(f"Admin run_command failed: {e}")
        return
    if hide: subprocess.Popen(["pwsh", "-Command", command], creationflags=subprocess.CREATE_NO_WINDOW)
    else: subprocess.Popen(f'start pwsh {"-NoExit" if no_exit else ""} -Command "{command}"', shell=True)

def restart(event=None):
    ROOT.destroy()
    os.execv(sys.executable, [sys.executable, os.path.abspath(__file__)] + sys.argv[1:])

def close_window(event=None): ROOT.destroy()

def get_cpu_ram_info(): return psutil.cpu_percent(interval=None), psutil.virtual_memory().percent
def get_gpu_usage():
    try: return ADLManager.getInstance().getDevices()[0].getCurrentUsage()
    except: return 0
def get_disk_info(): return psutil.disk_usage('C:').percent, psutil.disk_usage('D:').percent
def get_net_speed():
    net_io = psutil.net_io_counters()
    up = (net_io.bytes_sent - get_net_speed.up_last) / (1024 * 1024)
    down = (net_io.bytes_recv - get_net_speed.down_last) / (1024 * 1024)
    get_net_speed.up_last, get_net_speed.down_last = net_io.bytes_sent, net_io.bytes_recv
    return f"{up:.2f}", f"{down:.2f}"
get_net_speed.up_last = get_net_speed.down_last = 0

def update_info_labels():
    cpu, ram = get_cpu_ram_info()
    gpu = get_gpu_usage()
    dc, dd = get_disk_info()
    up, down = get_net_speed()
    
    LB_CPU.config(text=f'{cpu}%', bg=CP_CYAN if cpu > 80 else CP_PANEL, fg=CP_BG if cpu > 80 else CP_CYAN)
    LB_RAM.config(text=f'{ram}%', bg=CP_ORANGE if ram > 80 else CP_PANEL, fg=CP_BG if ram > 80 else CP_ORANGE)
    LB_GPU.config(text=f'{gpu}%', fg=CP_GREEN)
    LB_DUC.config(text=f'C:{dc}%', bg=CP_RED if dc > 90 else CP_PANEL)
    LB_DUD.config(text=f'D:{dd}%', bg=CP_RED if dd > 90 else CP_PANEL)
    Upload_lb.config(text=f'▲{up}', fg=CP_YELLOW if float(up) > 0.5 else CP_TEXT)
    Download_lb.config(text=f'▼{down}', fg=CP_CYAN if float(down) > 0.5 else CP_TEXT)
    ROOT.after(1000, update_info_labels)

def update_uptime_label():
    uptime = time.time() - psutil.boot_time()
    h, r = divmod(uptime, 3600)
    m, s = divmod(r, 60)
    uptime_label.configure(text=f"\udb81\udf8c {int(h):02}:{int(m):02}:{int(s):02}")
    uptime_label.after(1000, update_uptime_label)

def get_cpu_core_usage(): return psutil.cpu_percent(interval=None, percpu=True)
def update_cpu_core_bars():
    usages = get_cpu_core_usage()
    for i, usage in enumerate(usages):
        core_bar = cpu_core_bars[i]
        core_bar.delete("all")
        h = int((usage / 100) * (25 / 2))
        color = CP_RED if usage > 90 else (CP_ORANGE if usage > 80 else CP_CYAN)
        core_bar.create_rectangle(0, 12.5 - h, 8, 12.5 + h, fill=color)
    ROOT.after(1000, update_cpu_core_bars)

set_console_title("🔥")
ROOT = tk.Tk()
ROOT.configure(bg=CP_BG)
ROOT.overrideredirect(True)
ROOT.option_add("*Font", (CP_FONT, 10))

BORDER_FRAME = tk.Frame(ROOT, bg=CP_PANEL, bd=0, highlightthickness=1, highlightbackground=CP_RED)
BORDER_FRAME.place(relwidth=1, relheight=1)

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg=CP_BG)
MAIN_FRAME.pack(fill="both", expand=True, pady=1)

ROOT1 = tk.Frame(MAIN_FRAME, bg=CP_BG)
ROOT1.pack(side="left", padx=5, anchor="w")

ROOT2 = tk.Frame(MAIN_FRAME, bg=CP_BG)
ROOT2.pack(side="right", padx=5, anchor="e")

uptime_label = CTkLabel(ROOT1, text="", text_color=CP_CYAN, fg_color=CP_BG, font=(CP_FONT, 14, "bold"))
uptime_label.pack(side="left", padx=(0, 5))

for idx, btn in enumerate(CONFIG.get("buttons_left", [])): create_dynamic_button(ROOT1, btn, "buttons_left", idx)

separator = tk.Label(ROOT1, text="[", bg=CP_BG, fg=CP_DIM, font=(CP_FONT, 18, "bold"))
separator.pack(side="left")

queue, status_labels = Queue(), {}
repos = CONFIG.get("git_repos", [])

def check_git_status_thread():
    while True:
        for repo in repos:
            path = repo.get("path")
            if path and os.path.exists(path):
                try:
                    res = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=path)
                    clean = "nothing to commit, working tree clean" in res.stdout
                    queue.put((repo["name"], repo["label"], CP_GREEN if clean else CP_RED))
                except Exception as e:
                    print(f"Git check failed for {path}: {e}")
        time.sleep(5)

def update_git_gui():
    while True:
        try:
            name, label_text, color = queue.get_nowait()
            status_labels[name].config(text=label_text, fg=color)
        except: pass
        time.sleep(0.5)

tk.Label(ROOT1, text="\udb80\udea2", bg=CP_BG, fg=CP_YELLOW, font=(CP_FONT, 18, "bold")).pack(side="left")

for repo in repos:
    lbl = tk.Label(ROOT1, bg=CP_BG, fg=CP_TEXT, font=(CP_FONT, 12, "bold"), text=repo["label"])
    lbl.pack(side="left")
    lbl.bind("<Button-1>", lambda e, p=repo["path"]: run_command(f"cd {p} ; gitter"))
    status_labels[repo["name"]] = lbl

threading.Thread(target=check_git_status_thread, daemon=True).start()
threading.Thread(target=update_git_gui, daemon=True).start()

tk.Label(ROOT1, text="]", bg=CP_BG, fg=CP_DIM, font=(CP_FONT, 18, "bold")).pack(side="left")

for key, cfg in CONFIG.get("rclone_commands", {}).items():
    if "id" not in cfg: cfg["id"] = key
    lbl = tk.Label(ROOT1, bg=CP_BG, fg=CP_CYAN, text=cfg["label"], font=(CP_FONT, 14, "bold"), cursor="hand2")
    lbl.pack(side="left", padx=5)
    lbl.bind("<Shift-Button-1>", lambda e, c=cfg: open_edit_gui(c, "rclone_commands"))

tk.Label(ROOT1, text="\uf415", bg=CP_BG, fg=CP_GREEN, font=(CP_FONT, 18, "bold"), cursor="hand2").pack(side="left", padx=5)

cpu_core_frame = CTkFrame(ROOT2, fg_color=CP_PANEL, border_width=1, border_color=CP_DIM)
cpu_core_frame.pack(side="left", padx=3)
cpu_core_bars = []
for _ in range(psutil.cpu_count()):
    bar = CTkCanvas(cpu_core_frame, bg=CP_DIM, width=8, height=25, highlightthickness=0)
    bar.pack(side="left", padx=1)
    cpu_core_bars.append(bar)

Download_lb = tk.Label(ROOT2, bg=CP_BG, fg=CP_TEXT, font=(CP_FONT, 10, "bold"))
Download_lb.pack(side="left", padx=3)
Upload_lb = tk.Label(ROOT2, bg=CP_BG, fg=CP_TEXT, font=(CP_FONT, 10, "bold"))
Upload_lb.pack(side="left", padx=3)

LB_CPU = tk.Label(ROOT2, bg=CP_PANEL, fg=CP_CYAN, width=5, relief="flat", highlightthickness=1, highlightbackground=CP_DIM, font=(CP_FONT, 10, "bold"))
LB_CPU.pack(side="left", padx=3)
LB_GPU = tk.Label(ROOT2, bg=CP_PANEL, fg=CP_GREEN, width=5, relief="flat", highlightthickness=1, highlightbackground=CP_DIM, font=(CP_FONT, 10, "bold"))
LB_GPU.pack(side="left", padx=3)
LB_RAM = tk.Label(ROOT2, bg=CP_PANEL, fg=CP_ORANGE, width=5, relief="flat", highlightthickness=1, highlightbackground=CP_DIM, font=(CP_FONT, 10, "bold"))
LB_RAM.pack(side="left", padx=3)
LB_DUC = tk.Label(ROOT2, bg=CP_PANEL, fg=CP_TEXT, width=8, relief="flat", highlightthickness=1, highlightbackground=CP_DIM, font=(CP_FONT, 10, "bold"))
LB_DUC.pack(side="left", padx=3)
LB_DUD = tk.Label(ROOT2, bg=CP_PANEL, fg=CP_TEXT, width=8, relief="flat", highlightthickness=1, highlightbackground=CP_DIM, font=(CP_FONT, 10, "bold"))
LB_DUD.pack(side="left", padx=3)

time_left_label = tk.Label(ROOT2, text="\udb86\udee1", font=(CP_FONT, 16, "bold"), fg=CP_YELLOW, bg=CP_BG, cursor="hand2")
time_left_label.pack(side="left", padx=5)

for idx, btn in enumerate(CONFIG.get("buttons_right", [])): create_dynamic_button(ROOT2, btn, "buttons_right", idx)

sw = ROOT.winfo_screenwidth()
ROOT.geometry(f"1920x39+{(sw-1920)//2}+993")
update_info_labels()
update_uptime_label()
update_cpu_core_bars()
ROOT.mainloop()
