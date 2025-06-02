import requests
import tkinter as tk
import re

ANDROID_URL = "http://mi9t:5002"
LOW_BATTERY_THRESHOLD = 15
UPDATE_INTERVAL = 60000  # 60 seconds

def fetch_battery_percentage():
    try:
        response = requests.get(ANDROID_URL)
        if response.ok:
            match = re.search(r'(\d+)\s*%', response.text)
            if match:
                return int(match.group(1))
    except Exception as e:
        print(f"Error fetching battery: {e}")
    return None

def update_status():
    percent = fetch_battery_percentage()
    if percent is not None:
        if percent < LOW_BATTERY_THRESHOLD:
            label.config(
                text=f"{percent}% < {LOW_BATTERY_THRESHOLD}%",
                fg="white", bg="red"
            )
        else:
            label.config(
                text=f"{percent}% ≥ {LOW_BATTERY_THRESHOLD}%",
                fg="white", bg="green"
            )
    else:
        label.config(
            text="Error fetching battery",
            fg="white", bg="gray"
        )
    root.after(UPDATE_INTERVAL, update_status)

# Setup Tkinter
root = tk.Tk()
root.title("Android Battery Monitor")


label = tk.Label(root, text="Loading...", font=("Arial", 10), width=10)
label.pack(fill="both", expand=True)

# Start updates
update_status()
root.mainloop()
