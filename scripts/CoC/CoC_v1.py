import sys
import os
import json

if "python312" not in sys.executable:  # Check if the script is NOT running with Python 3.12
    os.execvp("python312", ["python312"] + sys.argv)  # Restart with python312
# Continue running with Python 3.12
print(f"Running with: {sys.executable}")

from datetime import datetime
from tkinter import Label, Tk, Button, messagebox
from tkinter import ttk
import glob
import pyautogui
import pygetwindow as gw
import subprocess
import threading
import time
import tkinter as tk
import win32gui

ROOT = tk.Tk()
ROOT.title("Utility Buttons")
ROOT.attributes('-topmost', True) 
ROOT.overrideredirect(True)
# ROOT.configure(bg="#282c34")

# def create_custom_border(parent):
#     BORDER_FRAME = tk.Frame(parent, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#6d4dff")
#     BORDER_FRAME.place(relwidth=1, relheight=1)
#     return BORDER_FRAME
# BORDER_FRAME = create_custom_border(ROOT)

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

#* ███████╗██╗███╗   ██╗██████╗     ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
#* ██╔════╝██║████╗  ██║██╔══██╗    ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║
#* █████╗  ██║██╔██╗ ██║██║  ██║    █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║
#* ██╔══╝  ██║██║╚██╗██║██║  ██║    ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║
#* ██║     ██║██║ ╚████║██████╔╝    ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#* ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
# Initialize variables
last_found_time = None
is_searching = False
last_used_time = time.time()  # Tracks when the function was last called
image_found_count = {}  # Dictionary to store cumulative counts of found images
output_file_path = r"C:\Users\nahid\ms\msBackups\sf3_img.txt"  # Path to save found image output

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

def display_image_found_chart():
    """Display a chart of found images and their cumulative counts in aligned columns."""
    column_width = 20  # Set a fixed width for the image name column
    print("\n\033[94m--- Cumulative Image Found Summary ---\033[0m")
    print(f"{'Image Name'.ljust(column_width)} : Count")
    print("-" * (column_width + 10))  # Adjust width for alignment
    for image, count in image_found_count.items():
        print(f"{image.ljust(column_width)} : {count}")
    print("\033[94m-------------------------------------\033[0m\n")

def find_image(image_path, confidence=0.7, region=None):
    """Find the location of the image on the screen within an optional specified region.
    region should be a tuple of (x1, y1, x2, y2). If not provided, the function searches the entire screen.
    """
    global last_found_time, is_searching, last_used_time
    current_time = time.time()
    # Reset timer if the function is not used for 10 seconds
    if current_time - last_used_time > 10:
        last_found_time = None
        is_searching = False
    last_used_time = current_time  # Update the last used time
    # Convert (x1, y1, x2, y2) region format to (x, y, width, height) for pyautogui
    if region:
        x1, y1, x2, y2 = region
        region = (x1, y1, x2 - x1, y2 - y1)
    try:
        # Start counting only when the function is searching for the image
        if not is_searching:
            is_searching = True
            last_found_time = time.time()  # Start the timer when first searching
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True, region=region)
        if location:
            image_name = os.path.basename(image_path)
            # Get current date and time in the desired format
            formatted_time = datetime.now().strftime('%I:%M:%S %p')
            print(f"\033[92m󱑂 {formatted_time} --> Found image: {image_name}\033[0m")
            
            # Update cumulative count of found images
            image_found_count[image_name] = image_found_count.get(image_name, 0) + 1
            
            # Save the output to the file
            with open(output_file_path, 'a') as file:
                file.write(f"{formatted_time} --> Found image: {image_name}\n")
            
            # Reset search and timer upon finding the image
            last_found_time = time.time()
            is_searching = False  # Stop the search
            return location
    except Exception as e:
        image_name = os.path.basename(image_path)  # Get the image name
        # Get current date and time for error messages
        formatted_time = datetime.now().strftime(' %I:%M:%S %p')
        # Calculate time since the last found time (only while searching)
        elapsed_time = time.time() - last_found_time if last_found_time else 0
        print(f"{formatted_time} --> {int(elapsed_time)} seconds since not found ---> {image_name} {e}")
    # Check if 120 seconds have passed since the last found time while searching
    if is_searching and time.time() - last_found_time > 200: # for ads do 120 second
        ntfy_signal_cli()  # Run the script instead of showing a message
        last_found_time = time.time()  # Reset the last found time to avoid repeated executions
    return None


# Flag to track if the notification has been sent
notification_sent = False
def ntfy_signal_cli():
    global notification_sent
    try:
        # Only send the command if it hasn't been sent already
        if not notification_sent:
            notification_sent = True
            while True:
                # Get the current date and time in 12-hour format
                current_time = datetime.now().strftime("%I:%M %p, %d-%b-%Y")
                # Properly escape the message for PowerShell
                # command = f'signal-cli -a +8801533876178 send -m \'{current_time}\' +8801779787186'
                command = f'signal-cli --trust-new-identities always -a +8801533876178 send -m \'{current_time}\' +8801779787186'
                # Execute the command
                os.system(f"powershell -Command \"{command}\"")
                print(f"Command executed: {command}")
                time.sleep(30)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        # Reset the flag when the function finishes
        notification_sent = False



Signal_Entry =r"C:\Users\nahid\ms\msBackups\shadowfight3\ntfy\Signal\Signal_Enter.png"
Signal_Cally =r"C:\Users\nahid\ms\msBackups\shadowfight3\ntfy\Signal\Signal_Call.png"
def ntfy_Signal():
    pyautogui.click(x=1778, y=900)
    time.sleep(2)
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while True:  # Loop will continue indefinitely unless interrupted by an external condition
            focus_window(window_title)
            if find_image(Signal_Entry, region=(233,241, 367,387)): press_global_screen_with_delays((294,299,3),(414,270,2))
            if find_image(Signal_Cally, region=(1500,115, 1755,211)): press_global_screen_with_delays((1656,170,2),(1297,588,60))
            # elif find_image(cancel, confidence=0.8): press_keys_with_delays(window, "c", 1)
            time.sleep(0.1)
    except KeyboardInterrupt: print("Script stopped by user.")


# focus_window
def focus_window(window_title):
    """Set focus to the window with the given title."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
        window.activate()
        return window
    return None

# press_key
def press_key(window, key):
    """Send a key press to a specific window."""
    window.activate()
    pyautogui.press(key)

# key_down
def key_down(window, key):
    """Send a key down event to a specific window."""
    window.activate()
    pyautogui.keyDown(key)

# key_up
def key_up(window, key):
    """Send a key up event to a specific window."""
    window.activate()
    pyautogui.keyUp(key)

# click
def click(window, x, y):
    """Send a mouse click to a specific window."""
    window.activate()
    pyautogui.click(x, y)

# press_keys_with_delays
def press_keys_with_delays(window, *args):
    """Press keys with specified delays in between.
    Usage: press_keys_with_delays(window, 'u', 2, 'p', 3, 'z', 2, 'x')
    """
    if len(args) % 2 != 0:
        raise ValueError("Arguments should be in pairs of (key, delay).")
    for i in range(0, len(args), 2):
        key = args[i]
        delay = args[i+1]
        press_key(window, key)
        time.sleep(delay)

def press_keys_with_two_delays(window, *args):
    """Press keys with two specified delays: one before pressing the key and one after pressing it.
    Usage: press_keys_with_two_delays(window, 1, 'u', 2, 1.5, 'p', 3, 2, 'z', 2, 'x')
    """
    if len(args) % 3 != 0:
        raise ValueError("Arguments should be in sets of (before_delay, key, after_delay).")
    for i in range(0, len(args), 3):
        before_delay = args[i]
        key = args[i+1]
        after_delay = args[i+2]
        time.sleep(before_delay)  # Delay before pressing the key
        press_key(window, key)    # Press the key
        time.sleep(after_delay)   # Delay after pressing the key


def get_window_rect(hwnd):
    """Get the window's position and size."""
    rect = win32gui.GetWindowRect(hwnd)
    return rect  # Returns (left, top, right, bottom)
# press_buttons_with_delays
def press_ldplayer_screen_with_delays(window, *args):
    """Press buttons at specified x, y locations with delays, relative to the window's position.
    Usage: press_buttons_with_delays(window, (100, 200, 2), (150, 250, 3), (300, 400, 2))
    """
    if len(args) == 0:
        raise ValueError("At least one (x, y, delay) tuple is required.")
    # Activate the window
    window.activate()
    # Get the window handle (HWND) using the window title
    hwnd = win32gui.FindWindow(None, window.title)
    if not hwnd:
        raise ValueError("Could not find window with the specified title.")
    # Get the window's position (top-left corner)
    window_rect = get_window_rect(hwnd)
    window_x, window_y = window_rect[0], window_rect[1]
    for i in range(len(args)):
        if len(args[i]) != 3:
            raise ValueError("Each argument should be a tuple (x, y, delay).")
        x, y, delay = args[i]
        # Adjust x, y coordinates to be relative to the window's position
        adjusted_x = window_x + x
        adjusted_y = window_y + y
        # Click at the given coordinates relative to the window
        pyautogui.click(adjusted_x, adjusted_y)
        # Wait for the specified delay before the next action
        time.sleep(delay)

def press_global_screen_with_delays(*args):
    """
    Press buttons at specified x, y locations on the global screen with delays.
    Usage: press_global_screen_with_delays((100, 200, 2), (150, 250, 3), (300, 400, 2))
    """
    if len(args) == 0:
        raise ValueError("At least one (x, y, delay) tuple is required.")
    for i in range(len(args)):
        if len(args[i]) != 3:
            raise ValueError("Each argument should be a tuple (x, y, delay).")
        x, y, delay = args[i]
        # Click at the specified global screen coordinates
        pyautogui.click(x, y)
        # Wait for the specified delay before the next action
        time.sleep(delay)


#* Threads
fight_thread = None
fame_light_thread = None
event_light_thread = None
raid_light_thread = None
loss_thread = None

def close_window(event=None):
    # Close the current window
    ROOT.destroy()
    # Start the specified script
    script_path = r"C:\@delta\ms1\SH3\sf3_AHK.py"
    subprocess.Popen([sys.executable, script_path])




#* ███████╗██╗   ██╗███████╗███╗   ██╗████████╗
#* ██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝
#* █████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║
#* ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║
#* ███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║
#* ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝

import tkinter as tk
from tkinter import ttk
import json
import os
import threading
import time
import subprocess
import sys


EVENT_SAVE_FILE = r"C:\Users\nahid\clash_of_clans.txt"
EVENT_KEYS_FILE = r"C:\Users\nahid\clash_of_clans_keys.json"

# Original event key mapping
event_key_mapping = {
    "num1": "T1",
    "num2": "T2",
    "num3": "ALT",
    # "num4": "T4",
}

# Troop/hero key options
troop_key_mapping = {
    "null": "❌",
    "0": "num0",
    "1": "num1",
    "2": "num2",
    "3": "num3",
    "4": "num4",
    "5": "num5",
    "6": "num6",
    "7": "num7",
    "8": "num8",
    "9": "num9"
}

event_dropdown_values = {f"{key}: {desc}": key for key, desc in event_key_mapping.items()}

# --- Centralized Troop/Hero Definitions ---
# Added 'type' field to categorize for coloring
TROOP_HERO_DEFS = [
    {"label": "Goblin", "var_name": "goblin_key", "default": "0", "type": "troop"},
    {"label": "Valk", "var_name": "valkyrie_key", "default": "1", "type": "troop"},
    {"label": "Jump", "var_name": "jump_spell_key", "default": "5", "type": "spell"},
    {"label": "Rage", "var_name": "rage_spell_key", "default": "4", "type": "spell"},
    {"label": "King", "var_name": "king_key", "default": "6", "type": "hero"},
    {"label": "Queen", "var_name": "queen_key", "default": "7", "type": "hero"},
    {"label": "Warden", "var_name": "warden_key", "default": "3", "type": "hero"},
    {"label": "Minion", "var_name": "MinionPrince_key", "default": "2", "type": "hero"},
]

# Define colors for each type - now includes 'bg' for background
COLOR_MAP = {
    "hero": {"fg": "#FFD700", "bg": "#2F4F4F"},  # Gold text on DarkSlateGray background
    "troop": {"fg": "#8B4513", "bg": "#DDA0DD"}, # SaddleBrown text on Plum background
    "spell": {"fg": "#4169E1", "bg": "#D3D3D3"}, # RoyalBlue text on LightGray background
    "default": {"fg": "#000000", "bg": "#FFFFFF"} # Black text on White background
}

# Dynamically create StringVar instances for troops/heroes
troop_vars = {}
for troop_def in TROOP_HERO_DEFS:
    troop_vars[troop_def["var_name"]] = tk.StringVar(value=troop_def["default"])
    globals()[troop_def["var_name"]] = troop_vars[troop_def["var_name"]]


def save_troop_keys():
    data = {troop_def["var_name"].replace("_key", ""): troop_vars[troop_def["var_name"]].get()
            for troop_def in TROOP_HERO_DEFS}
    try:
        with open(EVENT_KEYS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Failed to save troop keys: {e}")

def load_troop_keys():
    if os.path.exists(EVENT_KEYS_FILE):
        try:
            with open(EVENT_KEYS_FILE, "r") as f:
                data = json.load(f)
                for troop_def in TROOP_HERO_DEFS:
                    key_name = troop_def["var_name"].replace("_key", "")
                    troop_vars[troop_def["var_name"]].set(data.get(key_name, troop_def["default"]))
        except Exception as e:
            print(f"Failed to load troop keys: {e}")

def event_save_selected_key(key):
    try:
        with open(EVENT_SAVE_FILE, "w") as file:
            file.write(key)
    except Exception as e:
        print(f"Error saving key: {e}")

def event_load_selected_key():
    if os.path.exists(EVENT_SAVE_FILE):
        try:
            with open(EVENT_SAVE_FILE, "r") as file:
                key = file.read().strip()
                if key in event_key_mapping:
                    return key
        except Exception as e:
            print(f"Error loading key: {e}")
    return "num1"

def event_update_dropdown_display(event=None):
    selected_full = key_var_eve.get()
    selected_key = event_dropdown_values[selected_full]
    key_var_eve.set(event_key_mapping[selected_key])
    event_save_selected_key(selected_key)

def Event_Function():
    state = getattr(Event_Function, "state", {"thread": None, "stop_flag": True})

    if state["thread"] and state["thread"].is_alive():
        state["stop_flag"] = True
        state["thread"].join()
        EVENT_BT.config(text="CoC", bg="#ce5129", fg="#000000")
    else:
        state["stop_flag"] = False

        def search_and_act():
            window = focus_window(window_title)
            if not window:
                print(f"Window '{window_title}' not found.")
                return

            selected_description = key_var_eve.get()
            selected_key = next(k for k, v in event_key_mapping.items() if v == selected_description)
            event_save_selected_key(selected_key)

            image_action_map = [
                (r"C:\Users\nahid\ms\msBackups\CoC\MainBase\Train.png", (179, 690, 269, 781), lambda: press_global_screen_with_delays((265,878,1),(1313,591,1))),
                (r"C:\Users\nahid\ms\msBackups\CoC\MainBase\return.png", (819, 786, 1087, 920), lambda: press_global_screen_with_delays((961, 855,1))),
                (r"C:\Users\nahid\ms\msBackups\CoC\MainBase\okay.png", (757, 758, 1158, 951), lambda: press_global_screen_with_delays((961, 855,1))),
            ]

            try:
                while not Event_Function.state["stop_flag"]:
                    if find_image(r"C:\Users\nahid\ms\msBackups\CoC\MainBase\attack.png", confidence=0.8, region=(1452, 639, 1759, 804)):
                        # Access troop keys dynamically
                        press_keys_with_delays(window, troop_vars["jump_spell_key"].get(), 1)
                        press_global_screen_with_delays((1230,426,1), (1227,626,1))

                        press_keys_with_delays(window,
                                               troop_vars["warden_key"].get(), 1, 'p', 0,
                                               troop_vars["MinionPrince_key"].get(), 1, 'p', 0,
                                               troop_vars["queen_key"].get(), 1, 'p', 0,
                                               troop_vars["king_key"].get(), 1, 'p', 0)

                        press_keys_with_delays(window, troop_vars["valkyrie_key"].get(), 0, 'f12', 3)

                        press_keys_with_delays(window, troop_vars["rage_spell_key"].get(), 1)
                        press_global_screen_with_delays((1230,426,0), (1227,626,3), (1086,508,0))

                        press_keys_with_delays(window, troop_vars["goblin_key"].get(), 1, 'f12', 1)

                        if "archer_key" in troop_vars:
                            press_keys_with_delays(window, troop_vars["archer_key"].get(), 1)


                    for image_path, region, action in image_action_map:
                        if find_image(image_path, confidence=0.8, region=region):
                            action()
                            break

                    time.sleep(0.05)

            except KeyboardInterrupt:
                print("Script stopped by user.")

        thread = threading.Thread(target=search_and_act)
        thread.daemon = True
        thread.start()
        state["thread"] = thread
        EVENT_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

    Event_Function.state = state

# --- GUI SETUP ---
style = ttk.Style()

# Last selected event key
event_last_selected_key = event_load_selected_key()
key_var_eve = tk.StringVar(value=event_key_mapping[event_last_selected_key])

style.configure("EVENT.TCombobox", padding=5, selectbackground="#fa9f49", selectforeground="#000000")
style.map("EVENT.TCombobox", background=[("readonly", "#ff6d6d"), ("active", "#ff2323")], fieldbackground=[("readonly", "#fa9f49")], foreground=[("readonly", "#000000")])

event_key_dropdown = ttk.Combobox(ROOT, values=list(event_dropdown_values.keys()), textvariable=key_var_eve, font=("JetBrainsMono NFP", 10, "bold"), width=5, state="readonly", style="EVENT.TCombobox", justify="center")
event_key_dropdown.pack(side="left", padx=5, pady=5, anchor="center")
event_key_dropdown.set(event_key_mapping[event_last_selected_key])
event_key_dropdown.bind("<<ComboboxSelected>>", event_update_dropdown_display)

# Create labeled dropdowns using the centralized TROOP_HERO_DEFS
# Modified create_key_dropdown to accept 'label_fg_color' and 'label_bg_color' arguments
def create_key_dropdown(label_text, variable, label_fg_color="black", label_bg_color="white", label_width=6, dropdown_height=11): # New parameter
    frame = tk.Frame(ROOT)
    frame.pack(side="left", padx=3)
    # Use the fg (foreground) and bg (background) options to set label colors
    tk.Label(frame, text=label_text, width=8, font=("JetBrainsMono NFP", 10), fg=label_fg_color, bg=label_bg_color).pack()

    def on_change(event):
        save_troop_keys()

    cb = ttk.Combobox(
        frame,
        values=list(troop_key_mapping.keys()),
        textvariable=variable,
        font=("JetBrainsMono NFP", 9),
        width=3,
        height=dropdown_height,
        state="readonly",
        justify="center",
        style="EVENT.TCombobox"
    )
    cb.bind("<<ComboboxSelected>>", on_change)
    cb.pack()

# Iterate through TROOP_HERO_DEFS and pass the appropriate colors
for troop_def in TROOP_HERO_DEFS:
    colors = COLOR_MAP.get(troop_def.get("type", "default"), COLOR_MAP["default"])
    create_key_dropdown(troop_def["label"], troop_vars[troop_def["var_name"]],
                        label_fg_color=colors["fg"], label_bg_color=colors["bg"])

EVENT_BT = tk.Button(ROOT, text="CoC", bg="#ce5129", fg="#000000", width=5, height=0, command=Event_Function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
EVENT_BT.pack(side="left", padx=(1, 1), pady=(1, 1))

load_troop_keys()


# Restart function that displays the cumulative summary before restarting
def restart():
    display_image_found_chart()  # Show the summary of found images
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

# Button to restart the script
Restart_BT = Button(ROOT, text="RE", bg="#443e3e", fg="#fff", width=5, height=0, command=restart, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Restart_BT.pack( side="left",padx=(1, 1), pady=(1, 1))
# keyboard.add_hotkey("esc", restart)

#* ███████╗███╗   ██╗██████╗ ██╗███╗   ██╗ ██████╗
#* ██╔════╝████╗  ██║██╔══██╗██║████╗  ██║██╔════╝
#* █████╗  ██╔██╗ ██║██║  ██║██║██╔██╗ ██║██║  ███╗
#* ██╔══╝  ██║╚██╗██║██║  ██║██║██║╚██╗██║██║   ██║
#* ███████╗██║ ╚████║██████╔╝██║██║ ╚████║╚██████╔╝
#* ╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝

window_title='LDPlayer'

# ending

ROOT.update_idletasks()
width = ROOT.winfo_width()
height = ROOT.winfo_height()

# x = ROOT.winfo_screenwidth() - width
# y = (ROOT.winfo_screenheight() // 2) - (height // 2)

x = (ROOT.winfo_screenwidth() // 2) - (width // 2)
y = 0

ROOT.geometry(f'{width}x{height}+{x}+{y}')
ROOT.mainloop()