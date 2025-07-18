# sf3_gui.py
import json, os, time, threading, sys, subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pyautogui, pygetwindow as gw
from datetime import datetime

pyautogui.FAILSAFE = False
CONFIG_FILE = "sf3_automation_config.json"
WINDOW_TITLE = "LDPlayer"

# ---------------------------------------------------------
# Helper functions reused from your old script
# ---------------------------------------------------------
def focus_window(title):
    wins = gw.getWindowsWithTitle(title)
    return wins[0] if wins else None

def press_key(window, key):
    window.activate()
    pyautogui.press(key)

def press_keys_with_delays(window, *pairs):
    # pairs = key1, delay1, key2, delay2, ...
    for i in range(0, len(pairs), 2):
        press_key(window, pairs[i])
        time.sleep(pairs[i+1])

def press_global(x, y, delay):
    pyautogui.click(x, y)
    time.sleep(delay)

# ---------------------------------------------------------
# Main GUI
# ---------------------------------------------------------
class SF3Tool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SF3 Event Builder")
        self.geometry("1100x700")
        self.configure(bg="#2e2e2e")
        self.events = {}
        self.threads = {}
        self.stop_flags = {}

        # load last session
        self.load_config()
        self.build_ui()
        self.refresh_event_buttons()

    # ---------- ui ----------
    def build_ui(self):
        # left panel
        left = ttk.LabelFrame(self, text="Events", padding=8)
        left.pack(side="left", fill="y", padx=5, pady=5)
        ttk.Button(left, text="Add Event", command=self.add_event).pack(fill="x", pady=2)
        ttk.Button(left, text="Rename", command=self.rename_event).pack(fill="x", pady=2)
        ttk.Button(left, text="Delete", command=self.delete_event).pack(fill="x", pady=2)

        self.ev_list = tk.Listbox(left, width=20, height=25, exportselection=False)
        self.ev_list.pack(fill="both", expand=True)
        self.ev_list.bind("<<ListboxSelect>>", self.on_event_select)

        # right panel
        right = ttk.LabelFrame(self, text="Images for selected event", padding=8)
        right.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # image list
        self.img_list = tk.Listbox(right, height=10, exportselection=False)
        self.img_list.pack(fill="x")
        self.img_list.bind("<<ListboxSelect>>", self.on_image_select)

        btn_bar = ttk.Frame(right)
        btn_bar.pack(fill="x", pady=4)
        ttk.Button(btn_bar, text="Add Image", command=self.add_image).pack(side="left")
        ttk.Button(btn_bar, text="Delete Image", command=self.delete_image).pack(side="left")
        ttk.Button(btn_bar, text="Save Image", command=self.save_image).pack(side="left")

        # config area
        cfg = ttk.LabelFrame(right, text="Image config")
        cfg.pack(fill="both", expand=True, pady=5)

        ttk.Label(cfg, text="Path:").grid(row=0, column=0, sticky="w")
        self.path_var = tk.StringVar()
        ttk.Entry(cfg, textvariable=self.path_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(cfg, text="Browse", command=self.browse_path).grid(row=0, column=2)

        ttk.Label(cfg, text="Confidence:").grid(row=1, column=0, sticky="w")
        self.conf_var = tk.DoubleVar(value=0.8)
        ttk.Scale(cfg, variable=self.conf_var, from_=0.1, to=1, orient="horizontal").grid(
            row=1, column=1, sticky="ew")
        ttk.Label(cfg, textvariable=self.conf_var).grid(row=1, column=2)

        ttk.Label(cfg, text="Region x1,y1,x2,y2:").grid(row=2, column=0, sticky="w")
        reg_frm = ttk.Frame(cfg)
        reg_frm.grid(row=2, column=1, columnspan=2, sticky="w")
        self.reg_vars = [tk.IntVar() for _ in range(4)]
        for i, v in enumerate(self.reg_vars):
            ttk.Entry(reg_frm, textvariable=v, width=7).pack(side="left")

        ttk.Label(cfg, text="Action:").grid(row=3, column=0, sticky="nw")
        self.act_frm = ttk.Frame(cfg)
        self.act_frm.grid(row=3, column=1, columnspan=2, sticky="nsew")
        cfg.columnconfigure(1, weight=1)

        # bottom row with Start / Stop buttons
        self.btn_container = ttk.Frame(self)
        self.btn_container.pack(fill="x", padx=5, pady=5)
        ttk.Button(self.btn_container, text="Save Config", command=self.save_config).pack(side="right")
        ttk.Button(self.btn_container, text="Load Config", command=self.load_config).pack(side="right")

    def refresh_event_buttons(self):
        for w in self.btn_container.winfo_children():
            if getattr(w, "_is_event_btn", False):
                w.destroy()

        for ev in self.events:
            btn = ttk.Button(
                self.btn_container, text=f"Start {ev}",
                command=lambda e=ev: self.toggle_event(e))
            btn.pack(side="left", padx=2)
            btn._is_event_btn = True

    # ---------- event handling ----------
    def add_event(self):
        name = simpledialog.askstring("New Event", "Name:")
        if name and name not in self.events:
            self.events[name] = {"images": []}
            self.populate_events()
            self.save_config()
            self.refresh_event_buttons()

    def rename_event(self):
        sel = self.ev_list.curselection()
        if not sel:
            return
        old = self.ev_list.get(sel[0])
        new = simpledialog.askstring("Rename", "New name:", initialvalue=old)
        if new and new != old and new not in self.events:
            self.events[new] = self.events.pop(old)
            self.populate_events()
            self.save_config()
            self.refresh_event_buttons()

    def delete_event(self):
        sel = self.ev_list.curselection()
        if not sel:
            return
        name = self.ev_list.get(sel[0])
        if messagebox.askyesno("Delete", f"Delete '{name}' ?"):
            self.stop_event(name)
            self.events.pop(name, None)
            self.populate_events()
            self.save_config()
            self.refresh_event_buttons()

    def populate_events(self):
        self.ev_list.delete(0, "end")
        for ev in self.events:
            self.ev_list.insert("end", ev)

    def on_event_select(self, *_):
        sel = self.ev_list.curselection()
        if not sel:
            return
        ev = self.ev_list.get(sel[0])
        self.populate_images(ev)

    def populate_images(self, ev):
        self.img_list.delete(0, "end")
        for img in self.events[ev]["images"]:
            self.img_list.insert("end", img.get("name", "unnamed"))

    # ---------- image handling ----------
    def add_image(self):
        sel = self.ev_list.curselection()
        if not sel:
            return
        ev = self.ev_list.get(sel[0])
        name = simpledialog.askstring("Image Name", "Name:")
        if not name:
            return
        img = {
            "name": name,
            "path": "",
            "confidence": 0.8,
            "region": None,
            "action": {"type": "key_press", "key": "space", "delay": 0.1}
        }
        self.events[ev]["images"].append(img)
        self.populate_images(ev)
        self.save_config()

    def delete_image(self):
        ev_sel = self.ev_list.curselection()
        img_sel = self.img_list.curselection()
        if not (ev_sel and img_sel):
            return
        ev = self.ev_list.get(ev_sel[0])
        idx = img_sel[0]
        del self.events[ev]["images"][idx]
        self.populate_images(ev)
        self.save_config()

    def on_image_select(self, *_):
        ev_sel = self.ev_list.curselection()
        img_sel = self.img_list.curselection()
        if not (ev_sel and img_sel):
            return
        ev = self.ev_list.get(ev_sel[0])
        idx = img_sel[0]
        img = self.events[ev]["images"][idx]
        self.load_image_form(img)

    def load_image_form(self, img):
        self.path_var.set(img.get("path", ""))
        self.conf_var.set(img.get("confidence", 0.8))
        reg = img.get("region")
        for i, v in enumerate(self.reg_vars):
            v.set(reg[i] if reg else 0)
        self.build_action_form(img["action"])

    def build_action_form(self, act):
        for w in self.act_frm.winfo_children():
            w.destroy()
        self.action_data = act
        t = act["type"]
        ttk.Label(self.act_frm, text=t).pack()
        if t == "key_press":
            self.key_var = tk.StringVar(value=act.get("key", ""))
            self.dly_var = tk.DoubleVar(value=act.get("delay", 0.1))
            ttk.Entry(self.act_frm, textvariable=self.key_var).pack()
            ttk.Entry(self.act_frm, textvariable=self.dly_var).pack()
        elif t == "key_sequence":
            self.seq_var = tk.StringVar(value=act.get("sequence", ""))
            ttk.Entry(self.act_frm, textvariable=self.seq_var).pack()
        elif t == "mouse_click":
            self.x_var = tk.IntVar(value=act.get("x", 0))
            self.y_var = tk.IntVar(value=act.get("y", 0))
            self.dly_var = tk.DoubleVar(value=act.get("delay", 0.1))
            ttk.Entry(self.act_frm, textvariable=self.x_var).pack()
            ttk.Entry(self.act_frm, textvariable=self.y_var).pack()
            ttk.Entry(self.act_frm, textvariable=self.dly_var).pack()
        elif t == "mouse_sequence":
            self.mouse_seq_var = tk.StringVar(value=act.get("sequence", ""))
            ttk.Entry(self.act_frm, textvariable=self.mouse_seq_var).pack()

    def save_image(self):
        ev_sel = self.ev_list.curselection()
        img_sel = self.img_list.curselection()
        if not (ev_sel and img_sel):
            return
        ev = self.ev_list.get(ev_sel[0])
        idx = img_sel[0]
        img = self.events[ev]["images"][idx]

        img["path"] = self.path_var.get()
        img["confidence"] = self.conf_var.get()
        r = [v.get() for v in self.reg_vars]
        img["region"] = r if any(r) else None

        act = img["action"]
        t = act["type"]
        if t == "key_press":
            act["key"] = self.key_var.get()
            act["delay"] = self.dly_var.get()
        elif t == "key_sequence":
            act["sequence"] = self.seq_var.get()
        elif t == "mouse_click":
            act["x"] = self.x_var.get()
            act["y"] = self.y_var.get()
            act["delay"] = self.dly_var.get()
        elif t == "mouse_sequence":
            act["sequence"] = self.mouse_seq_var.get()

        self.save_config()

    def browse_path(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.bmp")])
        if f:
            self.path_var.set(f)

    # ---------- run ----------
    def toggle_event(self, ev):
        if ev in self.threads and self.threads[ev].is_alive():
            self.stop_event(ev)
        else:
            self.start_event(ev)

    def start_event(self, ev):
        self.stop_flags[ev] = False
        t = threading.Thread(target=self.loop_event, args=(ev,), daemon=True)
        t.start()
        self.threads[ev] = t

    def stop_event(self, ev):
        self.stop_flags[ev] = True
        if ev in self.threads:
            self.threads[ev].join(timeout=1)

    def loop_event(self, ev):
        win = focus_window(WINDOW_TITLE)
        if not win:
            print("LDPlayer not found")
            return
        imgs = self.events[ev]["images"]
        while not self.stop_flags.get(ev, True):
            for img in imgs:
                if self.stop_flags.get(ev, True):
                    break
                if self.find_and_do(img, win):
                    break
            time.sleep(0.1)

    def find_and_do(self, img, win):
        if not os.path.exists(img["path"]):
            return False
        reg = img.get("region")
        if reg:
            x1, y1, x2, y2 = reg
            reg = (x1, y1, x2 - x1, y2 - y1)
        loc = pyautogui.locateOnScreen(
            img["path"],
            confidence=img.get("confidence", 0.8),
            grayscale=True,
            region=reg
        )
        if loc:
            self.execute(img["action"], win)
            return True
        return False

    def execute(self, act, win):
        t = act["type"]
        if t == "key_press":
            press_key(win, act["key"])
            time.sleep(act["delay"])
        elif t == "key_sequence":
            parts = act["sequence"].split(",")
            for i in range(0, len(parts), 2):
                press_key(win, parts[i])
                time.sleep(float(parts[i + 1]))
        elif t == "mouse_click":
            press_global(act["x"], act["y"], act["delay"])
        elif t == "mouse_sequence":
            parts = act["sequence"].split(",")
            for i in range(0, len(parts), 3):
                press_global(int(parts[i]), int(parts[i + 1]), float(parts[i + 2]))

    # ---------- config ----------
    def save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.events, f, indent=2)

    def load_config(self):
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                self.events = json.load(f)
        else:
            self.events = {}

if __name__ == "__main__":
    SF3Tool().mainloop()