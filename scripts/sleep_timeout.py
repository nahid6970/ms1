import tkinter as tk
import os
import json

# Display and sleep turn-off intervals in seconds
intervals = [60, 300, 900, -1]
settings_file = "timeout_settings.json"
font_name = "JetBrainsMono NFP"

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, "r") as file:
            settings = json.load(file)
            return settings.get("display_index", 0), settings.get("sleep_index", 0)
    return 0, 0

def save_settings(display_index, sleep_index):
    with open(settings_file, "w") as file:
        json.dump({"display_index": display_index, "sleep_index": sleep_index}, file)

def set_display_interval(index):
    interval = intervals[index]
    if interval == -1:
        # Never turn off the display
        os.system("powercfg /change monitor-timeout-ac 0")
        os.system("powercfg /change monitor-timeout-dc 0")
        display_label.config(text="\udb81\udd1f Never")
    else:
        os.system(f"powercfg /change monitor-timeout-ac {interval // 60}")
        os.system(f"powercfg /change monitor-timeout-dc {interval // 60}")
        display_label.config(text=f"\udb81\udd1f {interval // 60} min")

def set_sleep_interval(index):
    interval = intervals[index]
    if interval == -1:
        # Never sleep
        os.system("powercfg /change standby-timeout-ac 0")
        os.system("powercfg /change standby-timeout-dc 0")
        sleep_label.config(text="\udb81\udcb2 Never")
    else:
        os.system(f"powercfg /change standby-timeout-ac {interval // 60}")
        os.system(f"powercfg /change standby-timeout-dc {interval // 60}")
        sleep_label.config(text=f"\udb81\udcb2 {interval // 60} min")

def toggle_display_interval(event=None):
    global display_index
    display_index = (display_index + 1) % len(intervals)
    set_display_interval(display_index)
    save_settings(display_index, sleep_index)

def toggle_sleep_interval(event=None):
    global sleep_index
    sleep_index = (sleep_index + 1) % len(intervals)
    set_sleep_interval(sleep_index)
    save_settings(display_index, sleep_index)

# Load the previous settings
display_index, sleep_index = load_settings()

# Create the main window
root = tk.Tk()
root.title("Timeout Settings")

# Create a label to show the current display timeout state
display_label = tk.Label(root, text="", font=(font_name, 16), cursor="hand2")
display_label.pack(pady=10)
display_label.bind("<Button-1>", toggle_display_interval)

# Create a label to show the current sleep timeout state
sleep_label = tk.Label(root, text="", font=(font_name, 16), cursor="hand2")
sleep_label.pack(pady=10)
sleep_label.bind("<Button-1>", toggle_sleep_interval)

# Set the initial intervals based on saved settings
set_display_interval(display_index)
set_sleep_interval(sleep_index)

# Run the Tkinter event loop
root.mainloop()
