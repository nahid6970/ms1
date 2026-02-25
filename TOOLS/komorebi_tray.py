import pystray
from PIL import Image, ImageDraw
import subprocess
import threading
import time
import os
import sys

# Name of the komorebi process to check for
PROCESS_NAME = "komorebi.exe"

def is_running():
    """Check if the komorebi process is currently running in the process list."""
    try:
        # Using tasklist to check for the process
        output = subprocess.check_output('tasklist /FI "IMAGENAME eq komorebi.exe"', shell=True).decode()
        return PROCESS_NAME in output
    except Exception:
        return False

def create_running_icon():
    """Square box with green border."""
    width, height = 64, 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Draw green border square
    # [left, top, right, bottom]
    border_width = 6
    dc.rectangle([8, 8, 56, 56], outline='#4CAF50', width=border_width)
    return image

def create_paused_icon():
    """Triangle (play button) with red border."""
    width, height = 64, 64
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Triangle points (pointing right like a play button)
    # Using coordinates that account for border width to avoid clipping
    padding = 10
    points = [
        (padding, padding),             # Top left
        (padding, height - padding),    # Bottom left
        (width - padding, height // 2)  # Middle right (tip)
    ]
    
    # Draw red border triangle
    # We draw it as a polygon. To simulate a 'border only' triangle:
    dc.polygon(points, outline='#F44336', width=6)
    return image

# Pre-generate icons
ICON_ACTIVE = create_running_icon()
ICON_INACTIVE = create_paused_icon()

def toggle_komorebi(icon, item=None):
    """Start or Stop komorebi based on current state."""
    if is_running():
        subprocess.run(["komorebic", "stop"], shell=True)
    else:
        subprocess.run(["komorebic", "start"], shell=True)
    
    # Force an immediate update
    update_state(icon)

def update_state(icon):
    """Updates the tray icon image and tooltip based on process state."""
    running = is_running()
    icon.icon = ICON_ACTIVE if running else ICON_INACTIVE
    state_text = "Running" if running else "Stopped"
    icon.title = f"Komorebi: {state_text}"

def monitor_loop(icon):
    """Background thread to keep the icon in sync with the system state."""
    while icon.visible:
        update_state(icon)
        time.sleep(2) # Poll every 2 seconds

def on_quit(icon, item):
    """Stop the tray application."""
    icon.stop()

def setup(icon):
    icon.visible = True
    # Start the monitoring thread
    thread = threading.Thread(target=monitor_loop, args=(icon,), daemon=True)
    thread.start()

def main():
    # Initial state check for the starting icon
    initial_icon = ICON_ACTIVE if is_running() else ICON_INACTIVE

    # Create the menu
    menu = pystray.Menu(
        pystray.MenuItem("Toggle Start/Stop", toggle_komorebi, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit Tray", on_quit)
    )

    icon = pystray.Icon(
        "komorebi_manager",
        initial_icon,
        title="Komorebi Manager",
        menu=menu
    )

    # Run the icon
    icon.run(setup)

if __name__ == "__main__":
    main()