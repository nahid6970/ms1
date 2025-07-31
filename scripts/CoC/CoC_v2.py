import tkinter as tk
from tkinter import ttk
import json
import os
import threading
import time
import subprocess
import sys

# Assume these are defined elsewhere in your actual code
# For demonstration, I'm providing placeholder definitions
ROOT = tk.Tk()
ROOT.title("CoC Automation")
window_title = "Clash of Clans" # Placeholder
def focus_window(title):
    print(f"Simulating focusing window: {title}")
    return True # Placeholder for actual window focusing
def press_global_screen_with_delays(*args):
    print(f"Simulating global screen press: {args}") # Placeholder
def press_keys_with_delays(window, *args):
    print(f"Simulating key presses for window {window}: {args}") # Placeholder
def find_image(image_path, confidence, region):
    print(f"Simulating image search for {image_path} in region {region}")
    # Simulate finding the attack image to trigger the troop deployment logic
    if "attack.png" in image_path:
        return True
    return False # Placeholder

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
    {"label": "Minion", "var_name": "MinionPrince_key", "default": "2", "type": "troop"},
    {"label": "Rage", "var_name": "rage_spell_key", "default": "4", "type": "spell"},
    {"label": "Jump", "var_name": "jump_spell_key", "default": "5", "type": "spell"},
    {"label": "King", "var_name": "king_key", "default": "6", "type": "hero"},
    {"label": "Queen", "var_name": "queen_key", "default": "7", "type": "hero"},
    {"label": "Warden", "var_name": "warden_key", "default": "3", "type": "hero"},
    {"label": "Archer", "var_name": "archer_key", "default": "8", "type": "troop"},
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

# Modified load_troop_keys to also update the combobox display
def load_troop_keys():
    if os.path.exists(EVENT_KEYS_FILE):
        try:
            with open(EVENT_KEYS_FILE, "r") as f:
                data = json.load(f)
                for troop_def in TROOP_HERO_DEFS:
                    key_name = troop_def["var_name"].replace("_key", "")
                    loaded_key = data.get(key_name, troop_def["default"])
                    troop_vars[troop_def["var_name"]].set(loaded_key)
                    # Update the display string in the Combobox
                    # This relies on the global 'display_vars' dictionary
                    if troop_def["var_name"] in display_vars:
                        display_vars[troop_def["var_name"]].set(f"{troop_def['label']}: {loaded_key}")
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

# --- New: Dictionary to hold the StringVar for the Combobox display text ---
display_vars = {}
for troop_def in TROOP_HERO_DEFS:
    # Initialize with "Label: DefaultKey" format
    display_vars[troop_def["var_name"]] = tk.StringVar(value=f"{troop_def['label']}: {troop_def['default']}")

# Create labeled dropdowns using the centralized TROOP_HERO_DEFS
# Modified create_key_dropdown to use the new display_variable
def create_key_dropdown(label_text, value_variable, display_variable, label_fg_color="black", label_bg_color="white", label_width=6, dropdown_height=10):
    frame = tk.Frame(ROOT)
    frame.pack(side="left", padx=3)
    tk.Label(frame, text=label_text, font=("JetBrainsMono NFP", 8),
             fg=label_fg_color, bg=label_bg_color, width=label_width).pack()

    def on_change(event):
        # Update the hidden value_variable (e.g., goblin_key) with the selected raw key
        selected_display_text = display_variable.get() # Get "Label: Key"
        # Extract the raw key from the display text
        selected_raw_key = selected_display_text.split(": ")[-1]
        value_variable.set(selected_raw_key)

        # Reconstruct the display string to ensure it's always "Label: Key"
        # This handles cases where user might manually type if state wasn't readonly
        display_variable.set(f"{label_text}: {selected_raw_key}")

        save_troop_keys() # Save all keys after a change

    cb = ttk.Combobox(
        frame,
        # Values for the dropdown list will be just the raw keys
        values=list(troop_key_mapping.keys()),
        # The textvariable for the Combobox itself will be the display_variable
        textvariable=display_variable,
        font=("JetBrainsMono NFP", 9),
        width=8, # Increased width to accommodate "Label:Key" format
        state="readonly",
        justify="center",
        style="EVENT.TCombobox",
        height=dropdown_height
    )
    cb.bind("<<ComboboxSelected>>", on_change)
    cb.pack()

# Iterate through TROOP_HERO_DEFS and pass the appropriate colors and width
for troop_def in TROOP_HERO_DEFS:
    colors = COLOR_MAP.get(troop_def.get("type", "default"), COLOR_MAP["default"])
    create_key_dropdown(troop_def["label"],
                        troop_vars[troop_def["var_name"]],    # This holds the actual key (e.g., "6")
                        display_vars[troop_def["var_name"]],  # This holds the display string (e.g., "King: 6")
                        label_fg_color=colors["fg"],
                        label_bg_color=colors["bg"],
                        label_width=6,
                        dropdown_height=min(len(troop_key_mapping), 10))

EVENT_BT = tk.Button(ROOT, text="CoC", bg="#ce5129", fg="#000000", width=5, height=0, command=Event_Function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
EVENT_BT.pack(side="left", padx=(1, 1), pady=(1, 1))

load_troop_keys() # Load keys and update display after all widgets are created

# Restart function that displays the cumulative summary before restarting
def display_image_found_chart():
    print("Displaying image found chart summary...") # Placeholder
def restart():
    display_image_found_chart()  # Show the summary of found images
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

# Button to restart the script
Restart_BT = tk.Button(ROOT, text="RE", bg="#443e3e", fg="#fff", width=5, height=0, command=restart, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Restart_BT.pack( side="left",padx=(1, 1), pady=(1, 1))

ROOT.mainloop()