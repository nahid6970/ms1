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
output_file_path = r"C:\msBackups\sf3_img.txt"  # Path to save found image output

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


WhatsApp_Entry=r'C:\msBackups\shadowfight3\whatsapp\whatsapp_mobile\Enter_Whatsapp.png'
WhatsApp_Cally=r'C:\msBackups\shadowfight3\whatsapp\whatsapp_mobile\call.png'
WhatsApp_Cancel=r'C:\msBackups\shadowfight3\whatsapp\whatsapp_mobile\cancel.png'
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


Signal_Entry =r"C:\msBackups\shadowfight3\ntfy\Signal\Signal_Enter.png"
Signal_Cally =r"C:\msBackups\shadowfight3\ntfy\Signal\Signal_Call.png"
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
    script_path = r"C:\ms1\SH3\sf3_AHK.py"
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
# hornass =r"C:\msBackups\shadowfight3\testing\horn.png"
hornass =r"C:\msBackups\shadowfight3\testing\guardian_trash.png"

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

# T2REGION_LB = Label(
#     ROOT,
#     text="2Way",
#     bg="#5a9b5a",
#     fg="#ffffff",
#     width=5,
#     height=0,
#     font=("Jetbrainsmono nfp", 12, "bold"),
#     relief="flat",
#     highlightbackground="#ffffff",
#     highlightthickness=1,
# )
# T2REGION_LB.pack(side="left", padx=(1, 1), pady=(1, 1))
# T2REGION_LB.bind("<Button-1>", lambda event: Attack2Way(T2REGION_LB))

#* ███████╗██╗   ██╗███████╗███╗   ██╗████████╗
#* ██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝
#* █████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║
#* ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║
#* ███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║
#* ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝
# File path to save the selected key
EVENT_SAVE_FILE = r"C:\Users\nahid\sf3_event.txt"

# Mapping keys to descriptions
event_key_mapping = {
    "num1": "T1",
    "num2": "T2",
    "num3": "ALT",
    # "num4": "T4",
}

# Generate dropdown values like "F13: KOS"
event_dropdown_values = {f"{key}: {desc}": key for key, desc in event_key_mapping.items()}

def event_save_selected_key(key):
    """Save the selected key to a file."""
    try:
        with open(EVENT_SAVE_FILE, "w") as file:
            file.write(key)
    except Exception as e:
        print(f"Error saving key: {e}")

def event_load_selected_key():
    """Load the last selected key from the file."""
    if os.path.exists(EVENT_SAVE_FILE):
        try:
            with open(EVENT_SAVE_FILE, "r") as file:
                key = file.read().strip()
                if key in event_key_mapping:  # Ensure it's a valid option
                    return key
        except Exception as e:
            print(f"Error loading key: {e}")
    return "num1"

def event_update_dropdown_display(event=None):
    """Update the dropdown display to show only the description."""
    selected_full = key_var_eve.get()  # "F13: KOS"
    selected_key = event_dropdown_values[selected_full]  # Extract "F13"
    key_var_eve.set(event_key_mapping[selected_key])  # Set only "KOS" in dropdown
    event_save_selected_key(selected_key)  # Save selection

def Event_Function():
    """Toggles the functionality for Light Attack 2."""
    state = getattr(Event_Function, "state", {"thread": None, "stop_flag": True})

    if state["thread"] and state["thread"].is_alive():
        # Stop the thread
        state["stop_flag"] = True
        state["thread"].join()
        EVENT_BT.config(text="Event", bg="#ce5129", fg="#000000")
    else:
        # Start the thread
        state["stop_flag"] = False
        
        def search_and_act():
            window = focus_window(window_title)
            if not window:
                print(f"Window '{window_title}' not found.")
                return

            selected_description = key_var_eve.get()
            selected_key = next(k for k, v in event_key_mapping.items() if v == selected_description)
            event_save_selected_key(selected_key)

            # Preload static images
            select_img = r"C:\msBackups\shadowfight3\event\SELECT.png"
            # googleplay_close = r"C:\msBackups\shadowfight3\ads\googleplay_close.png"


            # Preload dynamic folder images
            cont_images = glob.glob(r"C:\msBackups\shadowfight3\cont_dynamic\*.png")
            notify_images = glob.glob(r"C:\msBackups\shadowfight3\notify\*.png")
            ads_images = glob.glob(r"C:\msBackups\shadowfight3\ads\ads_auto_click\*.png")

            # Single-image + action list
            image_action_map = [
                (later, None, lambda: press_global_screen_with_delays((1113, 728, 1))),
                # (googleplay_close, None, lambda: press_global_screen_with_delays((597, 66, 1))),
                # (Open_Chest, None, lambda: press_keys_with_delays(window, 'c', 4, 'c', 3, 'g', 1)),
                (default_ads, (177, 83, 263, 158), lambda: press_global_screen_with_delays((215, 118, 2))),
                (select_img, (1148, 186, 1445, 503), lambda: press_keys_with_delays(window, '1', 1)),
            ]

            try:
                while not Event_Function.state["stop_flag"]:
                    if find_image(Home, confidence=0.8):
                        press_key(window, 'f')
                    elif find_image(Resume, confidence=0.8):
                        press_key(window, 'esc')

                    # elif any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 0) #! quit game creepy party

                    # Handle cont_dynamic folder images
                    for contimg in cont_images:
                        if (location := find_image(contimg, confidence=0.8, region=contF_Region)):
                            press_keys_with_delays(window, 'c', 0)
                            break

                    # Handle notify folder images
                    for Folder_Ntfy in notify_images:
                        if (location := find_image(Folder_Ntfy, confidence=0.8, region=(170, 86, 1749, 970))):
                            ntfy_signal_cli()
                            break

                    # # Handle ads auto-click folder images
                    # for adimg in ads_images:
                    #     if (location := find_image(adimg, confidence=0.8, region=(166, 83, 1758, 978))):
                    #         x, y, w, h = location
                    #         center_x = x + w // 2
                    #         center_y = y + h // 2
                    #         pyautogui.click(center_x, center_y)
                    #         break

                    # General static image-action handling
                    for image_path, region, action in image_action_map:
                        if find_image(image_path, confidence=0.8, region=region):
                            action()
                            break

                    # Special logic for Tournament_step1
                    if find_image(Tournament_step1, confidence=0.8):
                        if selected_key == "num3":
                            press_keys_with_delays(window, "num2", 1, 'c', 1, "m", 1, "num1", 1, "c", 1)
                        else:
                            press_keys_with_delays(window, selected_key, 1, 'c', 1, "y", 1, "c", 1)

                    time.sleep(0.05)

            except KeyboardInterrupt:
                print("Script stopped by user.")

        
        # Create and start the thread
        thread = threading.Thread(target=search_and_act)
        thread.daemon = True
        thread.start()
        # Save the thread in the state dictionary
        state["thread"] = thread
        EVENT_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")
    
    Event_Function.state = state

# Load last saved key
event_last_selected_key = event_load_selected_key()
event_last_selected_value = f"{event_last_selected_key}: {event_key_mapping[event_last_selected_key]}"
# Dropdown variable (stores the displayed value like "KOS")
key_var_eve = tk.StringVar(value=event_key_mapping[event_last_selected_key])

# Configure the Combobox style
style.configure(
    "EVENT.TCombobox",
    padding=5,
    selectbackground="#fa9f49",  # Background when selected (fixed)
    selectforeground="#000000",  # Text color when selected
    # borderwidth=2,
    # relief="solid",
)

# Hover & Selection effects
style.map(
    "EVENT.TCombobox",
    background=[("readonly", "#ff6d6d"), ("active", "#ff2323")],
    fieldbackground=[("readonly", "#fa9f49")],
    foreground=[("readonly", "#000000")], # Text color
)
# event Combobox widget (direct styling without ttk.Style)
event_key_dropdown = ttk.Combobox( ROOT, values=list(event_dropdown_values.keys()), textvariable=key_var_eve, font=("JetBrainsMono NFP", 10, "bold"), width=5, state="readonly", style="EVENT.TCombobox", justify="center")
event_key_dropdown.pack(side="left", padx=5, pady=5, anchor="center")
# Set the default dropdown display to just the description
event_key_dropdown.set(event_key_mapping[event_last_selected_key])
# Update variable when selection changes
event_key_dropdown.bind("<<ComboboxSelected>>", event_update_dropdown_display)

# Button to start/stop Light Attack 2
EVENT_BT = tk.Button(ROOT, text="Event", bg="#ce5129", fg="#000000", width=5, height=0, command=Event_Function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
EVENT_BT.pack( side="left",padx=(1, 1), pady=(1, 1))

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
                    if find_image(Resume, confidence=0.8): press_key(window, 'r')
                    elif find_image(SPACE, confidence=0.8): press_key(window, ' ')
                    elif find_image(StartFame): press_key(window, 'p')
                    elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
                    elif find_image(e_image, region=e_image_region): press_key(window, 'e')
                    elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
                    # elif any(find_image(image) for image in continueF): press_key(window, 'c')
                    # elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 2,  "e", 0 )
                    elif any(find_image(image, region=contF_Region) for image in continueF): press_keys_with_delays(window, 'c', 2, "e", 0)

                    # elif find_image(r"C:\msBackups\shadowfight3\fame\Lost_2nd_Round.png", confidence=1, region=(1079, 178, 1095, 196)): press_global_screen_with_delays(( 450, 65, 10)) #! not working duel still ranking lost
                    # # elif find_image(r"C:\msBackups\shadowfight3\fame\Lost_2nd_Round.png", confidence=0.8, region=(804, 176, 1101, 199)): press_global_screen_with_delays(( 960, 540, 3)) #! not working duel still ranking lost

                    # elif (find_image(default_ads, confidence=0.8, region=(177, 83, 263, 158)) and 
                    #     find_image(default_sbs, confidence=0.8, region=(177, 83, 500, 500))):
                    #     press_global_screen_with_delays((215, 118, 2))

                   
                   
                    # elif any(find_image(image) for image in notifyF):
                    #     subprocess.run(['python', r'C:\ms1\SH3\whatsapp.py'])
                    #     time.sleep(60)
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

#? ██████╗  █████╗ ██╗██████╗ ███████╗
#? ██╔══██╗██╔══██╗██║██╔══██╗██╔════╝
#? ██████╔╝███████║██║██║  ██║███████╗
#? ██╔══██╗██╔══██║██║██║  ██║╚════██║
#? ██║  ██║██║  ██║██║██████╔╝███████║
#? ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝
#! Raid Raid Raid Raid
stop_thread_raid = True
def raid_items_handler(window):
    try:
        while not stop_thread_raid:
            focus_window(window_title)
            if find_image(Home, confidence=0.8): press_key(window, 'z')
            elif find_image(level3, confidence=0.85): press_keys_with_delays(window, 'n',2, "c",1)
            elif find_image(participate, confidence=0.97): press_key(window, 'c')
            elif find_image(toraid, confidence=0.97): press_key(window, ' ')
            elif find_image(fight, confidence=0.97): press_key(window, 'c')
            elif find_image(claimreward, confidence=0.97): press_key(window, 'c')
            elif any(find_image(image) for image in continueF): press_key(window, 'c')
            time.sleep(0.05)
    except KeyboardInterrupt: print("Script stopped by user.")
def Raid_Light():
    global stop_thread_raid
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    raid_items_thread = threading.Thread(target=raid_items_handler, args=(window,))
    raid_items_thread.daemon = True
    raid_items_thread.start()
    raid_items_thread.join()
def raid_function_light():
    global stop_thread_raid, raid_light_thread, Raid_Light_BT
    if raid_light_thread and raid_light_thread.is_alive():
        stop_thread_raid = True
        raid_light_thread.join()
        Raid_Light_BT.config(text="Raid", bg="#5a9bf7", fg="#000000")
    else:
        stop_thread_raid = False
        raid_light_thread = threading.Thread(target=Raid_Light)
        raid_light_thread.daemon = True
        raid_light_thread.start()
        Raid_Light_BT.config(text="Raid", bg="#1d2027", fg="#fc0000")
Raid_Light_BT = Button(ROOT, text="Raid", bg="#5a9bf7", fg="#000000", width=5, height=0, command=raid_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Raid_Light_BT.pack(side="left",padx=(1, 1), pady=(1, 1))

#* ███████╗███████╗ ██████╗██████╗ ███████╗████████╗    ███████╗██╗ ██████╗ ██╗  ██╗████████╗
#* ██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝    ██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
#* ███████╗█████╗  ██║     ██████╔╝█████╗     ██║       █████╗  ██║██║  ███╗███████║   ██║
#* ╚════██║██╔══╝  ██║     ██╔══██╗██╔══╝     ██║       ██╔══╝  ██║██║   ██║██╔══██║   ██║
#* ███████║███████╗╚██████╗██║  ██║███████╗   ██║       ██║     ██║╚██████╔╝██║  ██║   ██║
#* ╚══════╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝       ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
def SecretFightHandler(button):
    """Toggles the Secret Fight functionality."""
    # Use a dictionary to manage thread state and reference inside the function
    state = getattr(SecretFightHandler, "state", {"thread": None, "stop_flag": True})
    
    if state["thread"] and state["thread"].is_alive():
        # Stop the thread
        state["stop_flag"] = True
        state["thread"].join()
        button.config(text="Secret", bg="#62e7ff", fg="#000000")
    else:
        # Start the thread
        state["stop_flag"] = False

        def SecretFights():
            window = focus_window(window_title)
            if not window:
                print(f"Window '{window_title}' not found.")
                return
            try:
                while not state["stop_flag"]:
                    focus_window(window_title)
                    if any(find_image(image, confidence=actionF[image], region=(214, 914, 375, 1031)) for image in actionF):
                        press_keys_with_delays(window, 'x', 0.5, 'x', 0.5, 'i', 0.5, 'i', 0.5)
                    elif find_image(r"C:\msBackups\shadowfight3\Secret_Fight\Cont.png", confidence=0.8, region=(214, 914, 375, 1031)):
                        press_keys_with_delays(window, 'c', 0.5)
                    elif find_image(r"C:\msBackups\shadowfight3\Secret_Fight\Home.png", confidence=0.8, region=(214, 914, 375, 1031)):
                        press_keys_with_delays(window, 'f', 2, "num2", 1, "c", 0)

                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("Script stopped by user.")

        # Create and start the thread
        thread = threading.Thread(target=SecretFights)
        thread.daemon = True
        thread.start()

        # Save the thread in the state dictionary
        state["thread"] = thread
        button.config(text="Secret", bg="#1d2027", fg="#fc0000")

    # Save state to the function attribute for persistence
    SecretFightHandler.state = state

# Button logic
BT_Secret_Fights = Button( ROOT, text="Secret", bg="#62e7ff", fg="#000000", width=5, height=0, command=lambda: SecretFightHandler(BT_Secret_Fights), font=("Jetbrainsmono nfp", 10, "bold"), relief="flat" )
BT_Secret_Fights.pack(side="left",padx=(1, 1), pady=(1, 1))

#* ██╗      ██████╗ ███████╗███████╗
#* ██║     ██╔═══██╗██╔════╝██╔════╝
#* ██║     ██║   ██║███████╗███████╗
#* ██║     ██║   ██║╚════██║╚════██║
#* ███████╗╚██████╔╝███████║███████║
#* ╚══════╝ ╚═════╝ ╚══════╝╚══════╝
stop_thread_loss = True
def TakeL():
    global stop_thread_loss
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread_loss:
            focus_window(window_title)
            #* if any(find_image(image) for image in actionF):
            if any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 1)
            elif find_image(SPACE, confidence=0.8) : press_key(window, ' ')
            elif find_image(StartFame): press_key(window, 'p')
            elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
            elif find_image(e_image): press_key(window, 'e')
            elif find_image(GoBack, confidence=0.8): press_key(window, 'b')

            elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 2,  "e", 0 )
            time.sleep(0.1)
    except KeyboardInterrupt: print("Script stopped by user.")
def loss_function():
    global stop_thread_loss, loss_thread, Loss_BT
    if loss_thread and loss_thread.is_alive():
        stop_thread_loss = True
        loss_thread.join()
        Loss_BT.config(text="Loss", bg="#443e3e", fg="#fff")
    else:
        stop_thread_loss = False
        loss_thread = threading.Thread(target=TakeL)
        loss_thread.daemon = True
        loss_thread.start()
        Loss_BT.config(text="Loss", bg="#1d2027", fg="#fc0000")
Loss_BT = Button(ROOT, text="Loss", bg="#443e3e", fg="#fff", width=5, height=0, command=loss_function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Loss_BT.pack(side="left",padx=(1, 1), pady=(1, 1))

# ███████╗███████╗██╗  ██╗
# ██╔════╝██╔════╝██║  ██║
# ███████╗█████╗  ███████║
# ╚════██║██╔══╝  ╚════██║
# ███████║██║          ██║
# ╚══════╝╚═╝          ╚═╝
# sf4_FIGHT = r"C:\msBackups\shadowfight3\sf4\Fight.png"
# sf4_CLOSE = r"C:\msBackups\shadowfight3\sf4\Close.png"
# sf4_Claim_Middle = r"C:\msBackups\shadowfight3\sf4\Claim_Middle.png"
# sf4_Claim_Right = r"C:\msBackups\shadowfight3\sf4\Claim_Right.png"
# sf4_Select_Hero = r"C:\msBackups\shadowfight3\sf4\Select_Hero.png"
# sf4_Continue = r"C:\msBackups\shadowfight3\sf4\Continue.png"
# sf4_Skip = r"C:\msBackups\shadowfight3\sf4\SKIP.png"
# sf4_ART_of_Servitude = r"C:\msBackups\shadowfight3\sf4\ART_of_Servitude.png"
# sf4_Register = r"C:\msBackups\shadowfight3\sf4\Register.png"
# sf4_My_Hero = r"C:\msBackups\shadowfight3\sf4\Choose_Hero.png"

# stop_thread_loss = True
# def SF4_event():
#     global stop_thread_loss
#     window = focus_window(window_title)
#     if not window:
#         print(f"Window '{window_title}' not found.")
#         return
#     try:
#         while not stop_thread_loss:
#             focus_window(window_title)
#             #* if any(find_image(image) for image in actionF):
#             # if any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 1)
#             # elif find_image(Resume, confidence=0.8): press_key(window, 'r')
#             if find_image(sf4_ART_of_Servitude, confidence=0.8, region=(1006, 227, 1535, 738)) : press_global_screen_with_delays((1261, 884, 2))
#             if find_image(sf4_Register, confidence=0.8, region=(1422, 828, 1749, 936)) : press_global_screen_with_delays((1588, 887, 2), (1185, 697,0))
#             if find_image(sf4_My_Hero, confidence=0.8, region=(831, 438, 1072, 501)) : press_global_screen_with_delays((1068, 653, 2), (957, 884, 1))
#             if find_image(sf4_FIGHT, confidence=0.8, region=(1421,827, 1749,939)) : press_global_screen_with_delays((1587, 886, 2))
#             if find_image(sf4_CLOSE, confidence=0.8, region=(713,825, 1205,954)) : press_global_screen_with_delays((957, 884, 2))
#             if find_image(sf4_Claim_Middle, confidence=0.8, region=(713,825, 1205,954)) : press_global_screen_with_delays((957, 884, 2))
#             if find_image(sf4_Claim_Right, confidence=0.8, region=(1417,830, 1757,947)) : press_global_screen_with_delays((1585,886, 2))
#             if find_image(sf4_Continue, confidence=0.8, region=(713,825, 1205,954)) : press_global_screen_with_delays((957, 884, 2))
#             if find_image(sf4_Skip, confidence=0.8, region=(187,835, 374,941)) : press_global_screen_with_delays((242, 884, 2))
#             if find_image(sf4_Select_Hero, confidence=0.8, region=(702,124, 1194,229)) : press_global_screen_with_delays((336,553,1),(336,553,1), (520, 563,1),(520, 563,1), (704,593,8),(704,593,5),
#                                                                                                                          (957,581,2),(957,581,2),(957,581,2),(957,581,2),(957,581,2),(957,581,2),(957,581,2),(957,581,2),(957,581,2),(957,581,2))
#             elif find_image(StartFame): press_key(window, 'p')
#             elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
#             elif find_image(e_image): press_key(window, 'e')
#             elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
#             # elif any(find_image(image) for image in continueF): press_key(window, 'c')
#             elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 2,  "e", 0 )
#             time.sleep(0.1)
#     except KeyboardInterrupt: print("Script stopped by user.")
# def start_sf4():
#     global stop_thread_loss, loss_thread, SF4_BT
#     if loss_thread and loss_thread.is_alive():
#         stop_thread_loss = True
#         loss_thread.join()
#         SF4_BT.config(text="SF4", bg="#8e9636", fg="#000000")
#     else:
#         stop_thread_loss = False
#         loss_thread = threading.Thread(target=SF4_event)
#         loss_thread.daemon = True
#         loss_thread.start()
#         SF4_BT.config(text="SF4", bg="#1d2027", fg="#fc0000")
# SF4_BT = Button(ROOT, text="SF4", bg="#8e9636", fg="#000000", width=5, height=0, command=start_sf4, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
# SF4_BT.pack( side="left", padx=(1, 1), pady=(1, 1))



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
# mhome = r"C:\msBackups\shadowfight3"
# Home = rf"{mhome}\Home.png"

# Home Page of the SH3
Home=r"C:\msBackups\shadowfight3\Home.png"

# # Action Related Images
void_compass=r"C:\msBackups\shadowfight3\action\void_compass.png"
eruption=r"C:\msBackups\shadowfight3\action\eruption.png"
thud=r"C:\msBackups\shadowfight3\action\thud.png"
collector=r"C:\msBackups\shadowfight3\action\collector.png"
bolt=r"C:\msBackups\shadowfight3\action\bolt.png"
uppercut=r"C:\msBackups\shadowfight3\action\uppercut.png"
Peg_Top=r"C:\msBackups\shadowfight3\action\peg_top.png"
KOS_Cloud=r"C:\msBackups\shadowfight3\action\Kos_Cloud.png"
Temporary_Kibo=r"C:\msBackups\shadowfight3\action\temporary_kibo.png"
Temporary_Serge=r"C:\msBackups\shadowfight3\action\temporary_serge.png"
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

# # temp_ac=r"C:\msBackups\shadowfight3\action\temporary_action.png"
# health_bar=r"C:\msBackups\shadowfight3\action\bar_health.png"
# shadow_bar=r"C:\msBackups\shadowfight3\action\bar_shadow.png"
# actionF = {
#     health_bar: 0.98,
#     shadow_bar: 0.85,
# }
# Action_region = (835, 125, 910, 180)

#* Continue Related Images
cont1 =r"C:\msBackups\shadowfight3\continue\cont1.png"
# cont2 =r"C:\msBackups\shadowfight3\continue\cont2.png"
cont3 =r"C:\msBackups\shadowfight3\continue\cont3.png"
cont4 =r"C:\msBackups\shadowfight3\continue\cont4.png"
# cont5 =r"C:\msBackups\shadowfight3\continue\cont5.png"
continueF = [cont1, cont3, cont4]
contF_Region = (1380, 792, 1738, 966)

#* notifyF Related Images
# currencyERR =r"C:\msBackups\shadowfight3\notify\no_currency.png"
# connectionERR =r"C:\msBackups\shadowfight3\notify\no_server1.png"
# connectionERR2 =r"C:\msBackups\shadowfight3\notify\image_65.png"
# doesnt_exist =r"C:\msBackups\shadowfight3\notify\not_exist.png"
# no_activity =r"C:\msBackups\shadowfight3\notify\no_activity.png"
# no_voidenergy =r"C:\msBackups\shadowfight3\notify\no_voidEnergy.png"
# home_screen =r"C:\msBackups\shadowfight3\notify\home_screen.png"
# notifyF = [currencyERR, connectionERR,connectionERR2,doesnt_exist,no_activity,no_voidenergy,home_screen]

#* Others
# space_image  =r"C:\msBackups\shadowfight3\fame\b_space.png"
# space_image  =r"C:\msBackups\shadowfight3\fame\b_space.png"
SPACE =r"C:\msBackups\shadowfight3\fame\b_space2.png"
Resume =r"C:\msBackups\shadowfight3\resume.png"
later =r"C:\msBackups\shadowfight3\later.png"

# Fame Related Images
e_image      =r"C:\msBackups\shadowfight3\fame\b_tournament.png"
e_image_region = (196, 656, 384, 845)  # Example coordinates and dimensions


StartFame    =r"C:\msBackups\shadowfight3\fame\image_19.png"
WorldIcon    =r"C:\msBackups\shadowfight3\fame\image_20.png"
GoBack       =r"C:\msBackups\shadowfight3\fame\image_21.png"

# Raids Related Images
level3         =r"C:\msBackups\shadowfight3\raids\level3.png"
participate    =r"C:\msBackups\shadowfight3\raids\participate.png"
toraid         =r"C:\msBackups\shadowfight3\raids\to_raid.png"
fight          =r"C:\msBackups\shadowfight3\raids\fightttttt.png"
claimreward    =r"C:\msBackups\shadowfight3\raids\claim.png"

# DailyMission=r"C:\msBackups\shadowfight3\DailyMission.png"

# Event Related
Tournament_step1=r"C:\msBackups\shadowfight3\event\Tournament.png"
back_battlepass=r'C:\msBackups\shadowfight3\back_battlepass.png'

Select_CreepyParty=r"C:\msBackups\shadowfight3\event\Select\CreepyParty.png"
Select_SelectOption=r"C:\msBackups\shadowfight3\event\Select\Select.png"

Open_Chest=r"C:\msBackups\shadowfight3\chest.png"

# continue for ads
passed_50sv=r"C:\msBackups\shadowfight3\continue\cont_ads\50sv.png"
failed_50sv=r"C:\msBackups\shadowfight3\continue\cont_ads\50sv_failed.png"
continueADS = [passed_50sv, failed_50sv]

ads_folder = r"C:\msBackups\shadowfight3\ads\ads_auto_click"
ads_images = glob.glob(os.path.join(ads_folder, "*.png"))

cont_folder = r"C:\msBackups\shadowfight3\cont_dynamic"
cont_dynamic = glob.glob(os.path.join(cont_folder, "*.png"))

back_GPlay=r"C:\msBackups\shadowfight3\ads\Back_GooglePlay.png"
Error_Processing_Video=r"C:\msBackups\shadowfight3\ads\error_Video.png"

skip=r'C:\msBackups\shadowfight3\skip.png'
# Advertisement
# ads1 = r"C:\msBackups\shadowfight3\ads\ad1.png"
# ads2 = r"C:\msBackups\shadowfight3\ads\ad2.png"
# ads3 = r"C:\msBackups\shadowfight3\ads\ad3.png"
# ads4 = r"C:\msBackups\shadowfight3\ads\ad4.png"
# ads5 = r"C:\msBackups\shadowfight3\ads\ad5.png"
# ads6 = r"C:\msBackups\shadowfight3\ads\ad6.png"
# ads7 = r"C:\msBackups\shadowfight3\ads\ad7.png"
# ads8 = r"C:\msBackups\shadowfight3\ads\ad8.png"
# ads9 = r"C:\msBackups\shadowfight3\ads\ad9.png"
# ads10 = r"C:\msBackups\shadowfight3\ads\ad10.png"
# ads11 = r"C:\msBackups\shadowfight3\ads\ad11.png"
# ads12 = r"C:\msBackups\shadowfight3\ads\ad12.png"
# sf_ads1=r"C:\msBackups\shadowfight3\ads\sf_ads1.png"
# ads_images = [ads1, ads2, ads3, ads4, ads5, ads6, ads7, ads8, ads9, ads10, ads11, ads12, sf_ads1]

# Click_Ads=r"C:\msBackups\shadowfight3\ads\Click_ADS.png"
default_ads=r"C:\msBackups\shadowfight3\event\inside_ads.png"




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


# from ctypes import windll, c_char_p, c_buffer
# from PIL import Image
# from PIL import Image, ImageDraw
# from struct import calcsize, pack
# from tkinter import messagebox
# import gc  # Import garbage collector
# import keyboard
# import random