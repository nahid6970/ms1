import time
import os
import datetime
import pyperclip
import threading
from pystray import MenuItem as item, Icon as icon, Menu as menu
from PIL import Image, ImageDraw

# --- Configuration ---
LOG_FILE = r"C:\Users\nahid\ms\db\clipboard\clipboard.txt"
SEPARATOR = "-----x-----"
PAUSE_COLOR = 'red'
RESUME_COLOR = 'green'
# ---------------------

# Make sure directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# --- Global State ---
last_text = ""
paused = False
# --------------------

def log_clipboard(text):
    """Append the copied text with timestamp to the file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    normalized_text = text.replace("\r\n", "\n").rstrip("\n")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}\n{normalized_text}\n{SEPARATOR}\n")

def clipboard_monitoring():
    """The main loop for monitoring clipboard changes."""
    global last_text
    while True:
        if not paused:
            try:
                current_text = pyperclip.paste()
                if current_text and current_text != last_text:
                    last_text = current_text
                    log_clipboard(current_text)
            except Exception:
                # Errors (like clipboard being used by another process) are ignored
                pass
        time.sleep(0.5)

def create_icon_image(state):
    """Creates a simple geometric icon based on the state."""
    width = 64
    height = 64
    # Use RGBA for transparency
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    if state == 'paused':
        # Draw a red "pause" symbol (two vertical bars)
        draw.rectangle([(18, 16), (28, 48)], fill=PAUSE_COLOR)
        draw.rectangle([(36, 16), (46, 48)], fill=PAUSE_COLOR)
    else:  # 'resumed'
        # Draw a green "play" triangle
        draw.polygon([(22, 16), (22, 48), (48, 32)], fill=RESUME_COLOR)

    return image

# --- Tray Menu Actions ---
def quit_app(tray_icon, menu_item):
    """Stops the icon and exits the application."""
    tray_icon.stop()

def toggle_pause(tray_icon, menu_item):
    """Toggles the paused state, updates the icon, and syncs clipboard on resume."""
    global paused, last_text
    paused = not paused

    if not paused:
        try:
            # On resume, get current clipboard content to prevent logging old items
            last_text = pyperclip.paste()
        except Exception:
            pass  # Ignore if clipboard is busy

    # Update the icon to reflect the new state
    update_icon(tray_icon)

def update_icon(tray_icon):
    """Updates the tray icon's image based on the current paused state."""
    if paused:
        tray_icon.icon = create_icon_image('paused')
    else:
        tray_icon.icon = create_icon_image('resumed')

def setup_tray():
    """Sets up and runs the system tray icon."""
    # This generator is called by pystray to build the menu dynamically.
    def menu_generator():
        # By setting default=True, this becomes the action for a single left-click.
        yield item(
            'Pause' if not paused else 'Resume',
            toggle_pause,
            default=True)
        yield item(
            'Quit',
            quit_app)

    # Create the initial icon for the "resumed" state
    initial_icon = create_icon_image('resumed')

    tray_icon = icon(
        'clipboard.py',
        initial_icon,
        "Clipboard Logger",
        menu=menu(menu_generator))

    # Run clipboard monitoring in a background thread
    monitor_thread = threading.Thread(target=clipboard_monitoring, daemon=True)
    monitor_thread.start()

    print("Clipboard logger started. Find it in the system tray.")
    tray_icon.run()

if __name__ == "__main__":
    setup_tray()