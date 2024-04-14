import ctypes
import psutil
import tkinter as tk

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

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="#013f5e")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

set_console_title("🔥")
ROOT = tk.Tk()
ROOT.title("Python GUI")
ROOT.attributes('-topmost', True)  # Set always on top
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)


#!############################################################
# def check_window_topmost():
#     if not ROOT.attributes('-topmost'):
#         ROOT.attributes('-topmost', True)
#     ROOT.after(500, check_window_topmost)
# # Call the function to check window topmost status periodically
# check_window_topmost()
#!############################################################


BORDER_FRAME = create_custom_border(ROOT)

ROOT.bind("<ButtonPress-1>", start_drag)
ROOT.bind("<ButtonRelease-1>", stop_drag)
ROOT.bind("<B1-Motion>", do_drag)

screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()

x = 177
y = 0

ROOT.geometry(f"80x36+{x}+{y}") #! overall size of the window

MAIN_FRAME = tk.Frame(BORDER_FRAME, bg="#1D2027", width=800, height=800)
MAIN_FRAME.pack_propagate(False)
MAIN_FRAME.pack(pady=1, expand=True)

BOX_ROW2_ROOT = tk.Frame(ROOT, bg="#013f5e")
BOX_ROW2_ROOT.pack(side="top", anchor="center", pady=(3,2),padx=(0,0))

def get_cpu_core_usage():
    cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
    return cpu_usage_per_core
def update_cpu_core_bars():
    cpu_core_usage = get_cpu_core_usage()
    for i, usage in enumerate(cpu_core_usage):
        core_bar = cpu_core_bars[i]
        core_bar.delete("all")
        bar_height = int((usage / 100) * BAR_HEIGHT)
        bar_color = determine_color(usage)
        core_bar.create_rectangle(0, BAR_HEIGHT - bar_height, BAR_WIDTH, BAR_HEIGHT, fill=bar_color)
    ROOT.after(1000, update_cpu_core_bars)
def determine_color(usage):
    if usage >= 90:
        return "#8B0000"
    elif usage >= 80:
        return "#f12c2f"
    elif usage >= 50:
        return "#ff9282"
    else:
        return "#14bcff"
BAR_WIDTH = 8
BAR_HEIGHT = 25
cpu_core_frame = tk.Frame(BOX_ROW2_ROOT, bg="#013f5e", highlightthickness=1, highlightbackground="#717d99", relief="solid")
cpu_core_frame.pack(side="right", anchor="nw", padx=0, pady=1)
cpu_core_bars = []
for i in range(psutil.cpu_count()):
    frame = tk.Frame(cpu_core_frame, bg="#013f5e")
    frame.pack(side="left", padx=(0, 0), pady=0)
    core_bar = tk.Canvas(frame, bg="#1d2027", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="top")
    cpu_core_bars.append(core_bar)
update_cpu_core_bars()

ROOT.mainloop()
