import sys
import os

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
from pathlib import Path
from functools import partial
from PIL import ImageGrab
from chilimangoes import grab_screen

# This will make ImageGrab.grab capture all monitors, not just the primary
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

ROOT = tk.Tk()
ROOT.title("Utility Buttons")
ROOT.attributes('-topmost', True) 
ROOT.overrideredirect(True)
ROOT.configure(bg="#282c34")

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#1d2027", bd=0, highlightthickness=1, highlightbackground="#66fd1f")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME
BORDER_FRAME = create_custom_border(ROOT)

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

#* ███████╗██╗███╗   ██╗██████╗     ███████╗██╗   ██╗███╗   ██╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
#* ██╔════╝██║████╗  ██║██╔══██╗    ██╔════╝██║   ██║████╗  ██║██╔════╝╚══██╔══╝██║██╔═██╗████╗  ██║
#* █████╗  ██║██╔██╗ ██║██║  ██║    █████╗  ██║   ██║██╔██╗ ██║██║        ██║   ██║██║   ██║██╔██╗ ██║
#* ██╔══╝  ██║██║╚██╗██║██║  ██║    ██╔══╝  ██║   ██║██║╚██╗██║██║        ██║   ██║██║   ██║██║╚██╗██║
#* ██║     ██║██║ ╚████║██████╔╝    ██║     ╚██████╔╝██║ ╚████║╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#* ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝     ╚═╝      ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
# Initialize variables
last_found_time = None
is_searching = False
last_used_time = time.time()  # Tracks when the function was last called
image_found_count = {}  # Dictionary to store cumulative counts of found images

# --- Display Selection Logic ---
display_offsets = {"M-1": (0, 0), "M-2": (1920, 0)}
display_cycle = ["M-1", "M-2"]
current_display_index = 0

def toggle_display():
    global current_display_index
    current_display_index = (current_display_index + 1) % len(display_cycle)
    display_name = display_cycle[current_display_index]
    display_button.config(text=display_name)

output_file_path = Path.home() / "script_output" / "sf3_img.txt"
output_file_path.parent.mkdir(exist_ok=True)  # Create script_output if missing

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
    """Find the location of the image on the screen within an optional specified region."""
    global last_found_time, is_searching, last_used_time, current_display_index, display_cycle, display_offsets
    current_time = time.time()
    # Reset timer if the function is not used for 10 seconds
    if current_time - last_used_time > 10:
        last_found_time = None
        is_searching = False
    last_used_time = current_time  # Update the last used time

    display_name = display_cycle[current_display_index]
    offset_x, offset_y = display_offsets[display_name]

    search_region_pyautogui = None
    if region:
        x1, y1, x2, y2 = region
        search_region_pyautogui = (x1 + offset_x, y1 + offset_y, x2 - x1, y2 - y1)
    else:
        # No region, search entire selected monitor
        search_region_pyautogui = (offset_x, offset_y, 1920, 1080)

    try:
        # Start counting only when the function is searching for the image
        if not is_searching:
            is_searching = True
            last_found_time = time.time()  # Start the timer when first searching
        
        screenshot = grab_screen()
        if screenshot is None:
            return None
        location = pyautogui.locate(image_path, screenshot, confidence=confidence, grayscale=True, region=search_region_pyautogui)

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
            
            # Adjust the found location to be relative to the selected monitor
            relative_location = (
                location.left - offset_x,
                location.top - offset_y,
                location.width,
                location.height
            )
            return relative_location
    except Exception as e:
        image_name = os.path.basename(image_path)  # Get the image name
        # Get current date and time for error messages
        formatted_time = datetime.now().strftime(' %I:%M:%S %p')
        # Calculate time since the last found time (only while searching)
        elapsed_time = time.time() - last_found_time if last_found_time else 0
        print(f"{formatted_time} --> {int(elapsed_time)} seconds since not found ---> {image_name} {e}")
    # Check if 120 seconds have passed since the last found time while searching
    if is_searching and time.time() - last_found_time > 120: # for ads do 120 second
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

def ntfy_termux_rclone_touch():
    command = "rclone touch g00:ntfy"
    try:
        while True:
            os.system(f"powershell -Command \"{command}\"")
            print("Command executed: rclone touch g00:ntfy")
            time.sleep(30)
    except KeyboardInterrupt:
        print("Script stopped by user.")


WhatsApp_Entry=r'C:\Users\nahid\ms\msBackups\shadowfight3\whatsapp\whatsapp_mobile\Enter_Whatsapp.png'
WhatsApp_Cally=r'C:\Users\nahid\ms\msBackups\shadowfight3\whatsapp\whatsapp_mobile\call.png'
WhatsApp_Cancel=r'C:\Users\nahid\ms\msBackups\shadowfight3\whatsapp\whatsapp_mobile\cancel.png'
def ntfy_WhatsApp():
    pyautogui.click(x=1778, y=900)
    time.sleep(2)
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while True:  # Loop will continue indefinitely unless interrupted by an external condition
            focus_window(window_title)
            if find_image(WhatsApp_Entry): press_global_screen_with_delays((294,299,5),(594,908,2))
            if find_image(WhatsApp_Cally): press_global_screen_with_delays((238,271,60))
            # elif find_image(WhatsApp_Cancel, confidence=0.8): press_keys_with_delays(window, "c", 1)
            time.sleep(0.1)
    except KeyboardInterrupt: print("Script stopped by user.")


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
    Press buttons at specified x, y locations on the selected display with delays.
    Usage: press_global_screen_with_delays((100, 200, 2), (150, 250, 3), (300, 400, 2))
    """
    global current_display_index, display_cycle, display_offsets
    if len(args) == 0:
        raise ValueError("At least one (x, y, delay) tuple is required.")

    display_name = display_cycle[current_display_index]
    offset_x, offset_y = display_offsets[display_name]

    for i in range(len(args)):
        if len(args[i]) != 3:
            raise ValueError("Each argument should be a tuple (x, y, delay).")
        x, y, delay = args[i]
        # Click at the specified coordinates on the selected display
        pyautogui.click(x + offset_x, y + offset_y)
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

#!  █████╗ ██╗  ██╗██╗  ██╗     █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗
#! ██╔══██╗██║  ██║██║ ██╔╝    ██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝
#! ███████║███████║█████╔╝     ███████║   ██║      ██║   ███████║██║     █████╔╝
#! ██╔══██║██╔══██║██╔═██╗     ██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗
#! ██║  ██║██║  ██║██║  ██╗    ██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗
#! ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
# Global flag for stopping the threads
image_found = False
action_timer = None

# File path to save the selected key
SAVE_FILE = r"C:\Users\nahid\sf3_attack.txt"

# Mapping keys to descriptions
key_mapping = {
    "F13": "KOS 2 Tap",
    "F14": "KOS Fame",
    "F15": "Hound",
    "F21": "Butcher",
    "F16": "Hound vortex",
    "F17": "Laggy",
    "F18": "Stranger",
    "F19": "Possessed",
    "F20": "Event"
}

# Generate dropdown values like "F13: KOS"
dropdown_values = {f"{key}: {desc}": key for key, desc in key_mapping.items()}

def save_selected_key(key):
    """Save the selected key to a file."""
    try:
        with open(SAVE_FILE, "w") as file:
            file.write(key)
    except Exception as e:
        print(f"Error saving key: {e}")

def load_selected_key():
    """Load the last selected key from the file."""
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as file:
                key = file.read().strip()
                if key in key_mapping:  # Ensure it's a valid option
                    return key
        except Exception as e:
            print(f"Error loading key: {e}")
    return "F13"  # Default to F13 if no file found

def update_dropdown_display(event=None):
    """Update the dropdown display to show only the description."""
    selected_full = key_var.get()  # "F13: KOS"
    selected_key = dropdown_values[selected_full]  # Extract "F13"
    key_var.set(key_mapping[selected_key])  # Set only "KOS" in dropdown
    save_selected_key(selected_key)  # Save selection

def action_main_handler_5():
    """Toggles the functionality for Light Attack 2."""
    state = getattr(action_main_handler_5, "state", {"thread": None, "stop_flag": True})

    if state["thread"] and state["thread"].is_alive():
        # Stop the thread
        state["stop_flag"] = True
        state["thread"].join()
        ACTION_5_AHK.config(text="AHK", bg="#5a9b5a", fg="#222222")
    else:
        # Start the thread
        state["stop_flag"] = False
        
        def search_and_act():
            window = focus_window(window_title)
            if not window:
                print(f"Window '{window_title}' not found.")
                return
            
            selected_description = key_var.get()
            selected_key = next(k for k, v in key_mapping.items() if v == selected_description)
            save_selected_key(selected_key)
            
            try:
                while not state["stop_flag"]:
                    if any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF):
                        print("Image found in Light Attack 2, resetting action timer.")
                        action_timer = time.time()
                        print(f"Triggering AHK with {selected_key} ({selected_description})...")
                        key_down(window, selected_key); time.sleep(5); key_up(window, selected_key)
                        print("AHK action completed.")
                    else:
                        time.sleep(0.05)
            except KeyboardInterrupt:
                print("Script stopped by user.")
        
        # Create and start the thread
        thread = threading.Thread(target=search_and_act)
        thread.daemon = True
        thread.start()
        # Save the thread in the state dictionary
        state["thread"] = thread
        ACTION_5_AHK.config(text="Stop", bg="#1d2027", fg="#fc0000")
    
    action_main_handler_5.state = state

# Load last saved key
last_selected_key = load_selected_key()
last_selected_value = f"{last_selected_key}: {key_mapping[last_selected_key]}"
# Dropdown variable (stores the displayed value like "KOS")
key_var = tk.StringVar(value=key_mapping[last_selected_key])

# Create a style object
style = ttk.Style()
style.theme_use("alt")
# themelist = clam, alt, default, classic, vista, xpnative, winnative

# Configure the Combobox style
style.configure(
    "Custom.TCombobox",
    padding=5,
    selectbackground="#49ff43",  # Background when selected (fixed)
    selectforeground="#000000",  # Text color when selected
    # borderwidth=2,
    # relief="solid",
)

# Hover & Selection effects
style.map(
    "Custom.TCombobox",
    background=[("readonly", "#ff6d6d"), ("active", "#ff2323")],
    fieldbackground=[("readonly", "#49ff43")],
    foreground=[("readonly", "#000000")], # Text color
)
# Custom Combobox widget (direct styling without ttk.Style)
key_dropdown = ttk.Combobox( ROOT, values=list(dropdown_values.keys()), textvariable=key_var, font=("JetBrainsMono NFP", 10, "bold"), width=14, state="readonly", style="Custom.TCombobox", justify="center")
key_dropdown.pack(side="left", padx=5, pady=5, anchor="center")
# Set the default dropdown display to just the description
key_dropdown.set(key_mapping[last_selected_key])
# Update variable when selection changes
key_dropdown.bind("<<ComboboxSelected>>", update_dropdown_display)

# Button to start/stop Light Attack 2
ACTION_5_AHK = tk.Button(ROOT, text="AHK", bg="#5a9b5a", fg="#222222", width=5, height=0, command=action_main_handler_5, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_5_AHK.pack( side="left",padx=(1, 1), pady=(1, 1))

#! ██████╗ ██╗    ██╗ █████╗ ██╗   ██╗     █████╗ ██╗  ██╗██╗  ██╗
#! ╚════██╗██║    ██║██╔══██╗╚██╗ ██╔╝    ██╔══██╗██║  ██║██║ ██╔╝
#!  █████╔╝██║ █╗ ██║███████║ ╚████╔╝     ███████║███████║█████╔╝
#! ██╔═══╝ ██║███╗██║██╔══██║  ╚██╔╝      ██╔══██║██╔══██║██╔═██╗
#! ███████╗╚███╔███╔╝██║  ██║   ██║       ██║  ██║██║  ██║██║  ██╗
#! ╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
# hornass =r"C:\Users\nahid\ms\msBackups\shadowfight3\testing\horn.png"
hornass =r"C:\Users\nahid\ms\msBackups\shadowfight3\testing\guardian_trash.png"

def Attack2Way(button):
    """Toggles the two-region attack functionality."""
    # Use a dictionary to manage thread state and reference inside the function
    state = getattr(Attack2Way, "state", {"thread": None, "stop_flag": True})
    
    if state["thread"] and state["thread"].is_alive():
        # Stop the thread
        state["stop_flag"] = True
        state["thread"].join()
        button.config(text="2Way", bg="#5a9b5a", fg="#fff")
    else:
        # Start the thread
        state["stop_flag"] = False

        def AdditionalFunction():
            window = focus_window(window_title)
            if not window:
                print(f"Window '{window_title}' not found.")
                return
            try:
                while not state["stop_flag"]:
                    focus_window(window_title)
                    # Example logic
                    if find_image(hornass, confidence=0.7, region=(219, 140, 291, 210)):
                        press_key(window, 'F23')
                    elif find_image(hornass, confidence=0.7, region=(302, 144, 370, 209)):
                        press_key(window, 'F24')
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Script stopped by user.")

        # Create and start the thread
        thread = threading.Thread(target=AdditionalFunction)
        thread.daemon = True
        thread.start()

        # Save the thread in the state dictionary
        state["thread"] = thread
        button.config(text="Stop", bg="#1d2027", fg="#fc0000")
    # Save state to the function attribute for persistence
    Attack2Way.state = state
# Button logic
T2REGION_BT = Button( ROOT, text="2Way", bg="#5a9b5a", fg="#fff", width=5, height=0, command=lambda: Attack2Way(T2REGION_BT), font=("Jetbrainsmono nfp", 10, "bold"), relief="flat" )
T2REGION_BT.pack( side="left",padx=(1, 1), pady=(1, 1))


#* ███████╗ █████╗ ███╗   ███╗███████╗
#* ██╔════╝██╔══██╗████╗ ████║██╔════╝
#* █████╗  ███████║██╔████╔██║█████╗
#* ██╔══╝  ██╔══██║██║╚██╔╝██║██╔══╝
#* ██║     ██║  ██║██║ ╚═╝ ██║███████╗
#* ╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
# #* Fame Fame Fame Fame
def FameFunction(button):
    """Toggles the two-region attack functionality."""
    # Use a dictionary to manage thread state and reference inside the function
    state = getattr(FameFunction, "state", {"thread": None, "stop_flag": True})

    if state["thread"] and state["thread"].is_alive():
        # Stop the thread
        state["stop_flag"] = True
        state["thread"].join()
        button.config(text="Fame", bg="#bda24a", fg="#000000")
    else:
        # Start the thread
        state["stop_flag"] = False

        def AdditionalFunction():
            window = focus_window(window_title)
            if not window:
                print(f"Window '{window_title}' not found.")
                return
            try:
                while not state["stop_flag"]:
                    focus_window(window_title)
                    # Example logic
                    if find_image(r"C:\Users\nahid\ms\msBackups\CoC\builder\Chat.png", confidence=0.8, region=(173, 420, 279, 547)): 
                        press_global_screen_with_delays((1276, 200,1))
                        press_global_screen_with_delays((1339, 846,1))
                        press_global_screen_with_delays((268, 875,1),(268, 875,1))
                        press_global_screen_with_delays((1355, 671,1))

                    if find_image(r"C:\Users\nahid\ms\msBackups\CoC\builder\return.png", confidence=0.8, region=(797, 772, 1115, 920)): 
                        press_global_screen_with_delays((960, 840,1))

                    #! 1st troops
                    if find_image(r"C:\Users\nahid\ms\msBackups\CoC\builder\phase1.png", confidence=0.8, region=(359, 657, 652, 761)): 
                        # press_keys_with_delays(window, 'x',1, 'y',1, 'z',1)
                        press_keys_with_delays(window, 't',4)
                        press_keys_with_delays(window, '0',1, 'x',0, 'y',0, 'z',0)
                        press_keys_with_delays(window, '3',1, 'y',1, '3',1)
                        press_keys_with_delays(window, '4',1, 'x',0, 'z',0)
                    #! 2nd troops
                    if find_image(r"C:\Users\nahid\ms\msBackups\CoC\builder\phase2.png", confidence=0.8, region=(1151, 816, 1273, 978)): 
                        press_keys_with_delays(window, 'f',4)
                        press_keys_with_delays(window, '6',0, 'x',0, '7',0, 'z',0)
                        press_keys_with_delays(window, '0',0, 'x',0, '1',0, 'y',0, '2',0, 'z',0)
                        press_keys_with_delays(window, '3',1, 'y',1, '3',1)
                        press_keys_with_delays(window, '4',0, 'x',0, '5',0, 'z',0)
                    time.sleep(2)
            except KeyboardInterrupt: print("Script stopped by user.")
        # Create and start the thread
        thread = threading.Thread(target=AdditionalFunction)
        thread.daemon = True
        thread.start()
        # Save the thread in the state dictionary
        state["thread"] = thread
        button.config(text="Stop", bg="#1d2027", fg="#fc0000")
    # Save state to the function attribute for persistence
    FameFunction.state = state
# Button logic
Fame_BT = Button( ROOT, text="Fame", bg="#bda24a", fg="#000000", width=5, height=0, command=lambda: FameFunction(Fame_BT), font=("Jetbrainsmono nfp", 10, "bold"), relief="flat" )
Fame_BT.pack( side="left",padx=(1, 1), pady=(1, 1))


# Restart function that displays the cumulative summary before restarting
def restart():
    display_image_found_chart()  # Show the summary of found images
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

# Button to toggle display
display_button = Button(ROOT, text="M-1", bg="#0078D7", fg="#fff", width=8, height=0, command=toggle_display, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
display_button.pack(side="left", padx=(1, 1), pady=(1, 1))

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
# mhome = r"C:\Users\nahid\ms\msBackups\shadowfight3"
# Home = rf"{mhome}\Home.png"

# Home Page of the SH3
Home=r"C:\Users\nahid\ms\msBackups\shadowfight3\Home.png"

# # Action Related Images
void_compass=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\void_compass.png"
eruption=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\eruption.png"
thud=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\thud.png"
collector=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\collector.png"
bolt=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\bolt.png"
uppercut=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\uppercut.png"
Peg_Top=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\peg_top.png"
KOS_Cloud=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\Kos_Cloud.png"
Temporary_Kibo=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\temporary_kibo.png"
Temporary_Serge=r"C:\Users\nahid\ms\msBackups\shadowfight3\action\temporary_serge.png"
#! actionF = [void_compass, eruption, thud, collector]
actionF = {
    void_compass: 0.7,
    eruption: 0.85,
    KOS_Cloud: 0.85,
    Temporary_Kibo: 0.85,
    Temporary_Serge: 0.85,
    thud: 0.7,
    collector: 0.7,
    uppercut: 0.7,
    Peg_Top: 0.85,
    # bolt: 1,
}
Action_region = (216, 99, 374, 253)  # Replace with your actual coordinates


#* Continue Related Images
cont1 =r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont1.png"
# cont2 =r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont2.png"
cont3 =r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont3.png"
cont4 =r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont4.png"
# cont5 =r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont5.png"
continueF = [cont1, cont3, cont4]
contF_Region = (1380, 792, 1738, 966)

SPACE =r"C:\Users\nahid\ms\msBackups\shadowfight3\fame\b_space2.png"
Resume =r"C:\Users\nahid\ms\msBackups\shadowfight3\resume.png"
later =r"C:\Users\nahid\ms\msBackups\shadowfight3\later.png"

# Fame Related Images
e_image      =r"C:\Users\nahid\ms\msBackups\shadowfight3\fame\b_tournament.png"
e_image_region = (196, 656, 384, 845)  # Example coordinates and dimensions


StartFame    =r"C:\Users\nahid\ms\msBackups\shadowfight3\fame\image_19.png"
WorldIcon    =r"C:\Users\nahid\ms\msBackups\shadowfight3\fame\image_20.png"
GoBack       =r"C:\Users\nahid\ms\msBackups\shadowfight3\fame\image_21.png"

# Raids Related Images
level3         =r"C:\Users\nahid\ms\msBackups\shadowfight3\raids\level3.png"
participate    =r"C:\Users\nahid\ms\msBackups\shadowfight3\raids\participate.png"
toraid         =r"C:\Users\nahid\ms\msBackups\shadowfight3\raids\to_raid.png"
fight          =r"C:\Users\nahid\ms\msBackups\shadowfight3\raids\fightttttt.png"
claimreward    =r"C:\Users\nahid\ms\msBackups\shadowfight3\raids\claim.png"

# DailyMission=r"C:\Users\nahid\ms\msBackups\shadowfight3\DailyMission.png"

# Event Related
Tournament_step1=r"C:\Users\nahid\ms\msBackups\shadowfight3\event\Tournament.png"
back_battlepass=r'C:\Users\nahid\ms\msBackups\shadowfight3\back_battlepass.png'

Select_CreepyParty=r"C:\Users\nahid\ms\msBackups\shadowfight3\event\Select\CreepyParty.png"
Select_SelectOption=r"C:\Users\nahid\ms\msBackups\shadowfight3\event\Select\Select.png"

Open_Chest=r"C:\Users\nahid\ms\msBackups\shadowfight3\chest.png"

# continue for ads
passed_50sv=r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont_ads\50sv.png"
failed_50sv=r"C:\Users\nahid\ms\msBackups\shadowfight3\continue\cont_ads\50sv_failed.png"
continueADS = [passed_50sv, failed_50sv]

ads_folder = r"C:\Users\nahid\ms\msBackups\shadowfight3\ads\ads_auto_click"
ads_images = glob.glob(os.path.join(ads_folder, "*.png"))

cont_folder = r"C:\Users\nahid\ms\msBackups\shadowfight3\cont_dynamic"
cont_dynamic = glob.glob(os.path.join(cont_folder, "*.png"))

back_GPlay=r"C:\Users\nahid\ms\msBackups\shadowfight3\ads\Back_GooglePlay.png"
Error_Processing_Video=r"C:\Users\nahid\ms\msBackups\shadowfight3\ads\error_Video.png"

skip=r'C:\Users\nahid\ms\msBackups\shadowfight3\skip.png'
default_ads=r"C:\Users\nahid\ms\msBackups\shadowfight3\event\inside_ads.png"




# ending

ROOT.update_idletasks()
width = ROOT.winfo_width()
height = ROOT.winfo_height()


x = (ROOT.winfo_screenwidth() // 2) - (width // 2)
y = 0

ROOT.geometry(f'{width}x{height}+{x}+{y}')
ROOT.mainloop()
