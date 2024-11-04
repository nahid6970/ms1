# from ctypes import windll, c_char_p, c_buffer
# from PIL import Image
# from PIL import Image, ImageDraw
# from struct import calcsize, pack
# from tkinter import messagebox
# from tkinter import messagebox
# import gc  # Import garbage collector
# import random
from datetime import datetime
from tkinter import Tk, Button, messagebox
import glob
import os
import pyautogui
import pygetwindow as gw
import subprocess
import sys
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
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = screen_width - 60
y = screen_height - 950
ROOT.geometry(f"+{x}+{y}")

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

# Initialize variables
last_found_time = None
is_searching = False
last_used_time = time.time()  # Tracks when the function was last called
image_found_count = {}  # Dictionary to store cumulative counts of found images
chart_last_displayed = time.time()  # Tracks the last time the chart was displayed

def display_image_found_chart():
    """Display a chart of found images and their cumulative counts."""
    print("\n\033[94m--- Cumulative Image Found Summary ---\033[0m")
    for image, count in image_found_count.items():
        print(f"{image}: {count} times")
    print("\033[94m-------------------------------------\033[0m\n")

def find_image(image_path, confidence=0.7, region=None):
    """Find the location of the image on the screen within an optional specified region.
    
    region should be a tuple of (x1, y1, x2, y2). If not provided, the function searches the entire screen.
    """
    global last_found_time, is_searching, last_used_time, chart_last_displayed
    current_time = time.time()
    # Display the chart every 60 seconds without resetting counts
    if current_time - chart_last_displayed >= 60:
        display_image_found_chart()
        chart_last_displayed = current_time  # Update chart display time
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
            formatted_time = datetime.now().strftime('%Y-%m-%d %I-%M-%S %p')
            print(f"\033[92m{formatted_time} --> Found image: {image_name}\033[0m")
            # Update cumulative count of found images
            image_found_count[image_name] = image_found_count.get(image_name, 0) + 1
            # Reset search and timer upon finding the image
            last_found_time = time.time()
            is_searching = False  # Stop the search
            return location
    except Exception as e:
        image_name = os.path.basename(image_path)  # Get the image name
        # Get current date and time for error messages
        formatted_time = datetime.now().strftime('%Y-%m-%d %I-%M-%S %p')
        # Calculate time since the last found time (only while searching)
        elapsed_time = time.time() - last_found_time if last_found_time else 0
        print(f"{formatted_time} --> {int(elapsed_time)} seconds since not found ---> {image_name} {e}")
    # Check if 120 seconds have passed since the last found time while searching
    if is_searching and time.time() - last_found_time > 120:
        run_script()  # Run the script instead of showing a message
        last_found_time = time.time()  # Reset the last found time to avoid repeated executions
    return None

def run_script():
    """Run the whatsapp.py script."""
    try:
        # Replace "python" with the full path to Python if needed
        subprocess.run(["python", r"C:\ms1\scripts\shadowFight3\whatsapp.py"], check=True)
        print("whatsapp.py script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute whatsapp.py: {e}")


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
def press_screen_with_delays(window, *args):
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

"""
███████╗ █████╗ ███╗   ███╗███████╗
██╔════╝██╔══██╗████╗ ████║██╔════╝
█████╗  ███████║██╔████╔██║█████╗
██╔══╝  ██╔══██║██║╚██╔╝██║██╔══╝
██║     ██║  ██║██║ ╚═╝ ██║███████╗
╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
"""
# Fame Fame Fame Fame
stop_thread_fame = True
def fame_items_handler(window):
    try:
        while not stop_thread_fame:
            # Check if we need to pause this handler
            if pause_other_items:
                print("Paused other items handler for 5 seconds.")
                while pause_other_items:
                    time.sleep(0.1)  # Wait until actionF is done
            if find_image(Resume, confidence=0.8): press_key(window, 'r')
            elif find_image(SPACE, confidence=0.8): press_key(window, ' ')
            elif find_image(StartFame): press_key(window, 'p')
            elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
            elif find_image(e_image, region=e_image_region): press_key(window, 'e')
            elif find_image(GoBack, confidence=0.8): press_key(window, 'b')

            # elif any(find_image(image) for image in continueF): press_key(window, 'c')
            elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 2,  "e", 0 )

            # elif any(find_image(image) for image in notifyF):
            #     subprocess.run(['python', r'C:\ms1\SH3\whatsapp.py'])
            #     time.sleep(60)

            time.sleep(2)
    except KeyboardInterrupt: print("Script stopped by user.")
def fame_Light():
    global stop_thread_fame
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    fame_items_thread = threading.Thread(target=fame_items_handler, args=(window,))
    fame_items_thread.daemon = True
    fame_items_thread.start()
    fame_items_thread.join()
def fame_function_light():
    global stop_thread_fame, fame_light_thread, Fame_Light_BT
    if fame_light_thread and fame_light_thread.is_alive():
        stop_thread_fame = True
        fame_light_thread.join()
        Fame_Light_BT.config(text="Fame", bg="#bda24a", fg="#000000")
    else:
        stop_thread_fame = False
        fame_light_thread = threading.Thread(target=fame_Light)
        fame_light_thread.daemon = True
        fame_light_thread.start()
        Fame_Light_BT.config(text="Fame", bg="#1d2027", fg="#fc0000")
Fame_Light_BT = Button(ROOT, text="Fame", bg="#bda24a", fg="#000000", width=5, height=2, command=fame_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Fame_Light_BT.pack(padx=(1, 1), pady=(1, 1))

#! ███████╗██╗   ██╗███████╗███╗   ██╗████████╗
#! ██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝
#! █████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║
#! ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║
#! ███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║
#! ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝
stop_thread_event = True
def event_items_handler(window):
    try:
        while not stop_thread_event:
            focus_window(window_title)
            #* Handle the other image searches and actions
            if find_image(Home, confidence=0.8): press_key(window, 'f')
            # if find_image(Home, confidence=0.8): press_screen_with_delays(window, (1265, 351, 2))
            elif find_image(Resume, confidence=0.8): press_key(window, 'r')

            # elif any(find_image(image) for image in continueF): press_key(window, 'c')
            # elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 2)
            
            # elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 1)
            elif find_image(Error_Processing_Video, confidence=0.8): press_key(window, 'esc') #! optional
            elif find_image(Click_Ads, confidence=0.95): press_keys_with_delays(window, '3', 1) #! optional
            elif any(find_image(image, confidence=0.95) for image in continueF): press_keys_with_delays(window, 'c', 1)

            elif find_image(Tournament_step1, confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)

            elif find_image(Select_CreepyParty, confidence=0.8): press_keys_with_delays(window, 'y', 1) #! optional
            elif find_image(Select_SelectOption, confidence=0.8): press_keys_with_delays(window, '2', 1) #! optional

            # elif find_image(back_battlepass, confidence=0.8): press_keys_with_delays(window, 'b', 1)
            elif find_image(back_GPlay, confidence=0.8): press_screen_with_delays(window, (1628, 815, 2)) #! optional

            # elif any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 0) #! optional

            # for ad_image in ads_images: #! optional
            #     ad_location = find_image(ad_image, confidence=0.8)
            #     if ad_location:
            #         click(window, ad_location.left, ad_location.top) 

            # [click(window, ad_location.left, ad_location.top) for ad_image in ads_images if (ad_location := find_image(ad_image, confidence=0.8))]

            # click the middle part of the ads
            # [click(window, ad_location.left + ad_location.width // 2, ad_location.top + ad_location.height // 2) #! optional
            # for ad_image in ads_images if (ad_location := find_image(ad_image, confidence=0.8))]

            [click(window, ad_location.left + ad_location.width // 2, ad_location.top + ad_location.height // 2)
            for ad_image in ads_images if (ad_location := find_image(ad_image, confidence=0.8))]

            # # Check if the no_currency image is found
            # elif any(find_image(image) for image in notifyF):
            #     subprocess.run(['python', r'C:\ms1\SH3\whatsapp.py'])
            #     time.sleep(60)

            # # Check if the no_currency image is found
            # elif find_image(r'C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_currency.png', confidence=0.8):
            #     # Run the whatsapp.py script
            #     subprocess.run(['python', r'C:\ms1\SH3\whatsapp.py'])
            #     # Wait for 1 minute
            #     time.sleep(60)

            time.sleep(0.05)
    except KeyboardInterrupt: print("Other items thread stopped by user.")
def Start_Event_Light():
    global stop_thread_event
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    other_items_thread = threading.Thread(target=event_items_handler, args=(window,))
    other_items_thread.daemon = True
    other_items_thread.start()
    other_items_thread.join()

def event_function_light():
    global stop_thread_event, event_light_thread, Event_Light_BT
    if event_light_thread and event_light_thread.is_alive():
        stop_thread_event = True
        event_light_thread.join()
        Event_Light_BT.config(text="Event", bg="#ce5129", fg="#000000")
    else:
        stop_thread_event = False
        event_light_thread = threading.Thread(target=Start_Event_Light)
        event_light_thread.daemon = True
        event_light_thread.start()
        Event_Light_BT.config(text="Event", bg="#1d2027", fg="#fc0000")
Event_Light_BT = Button(ROOT, text="Event", bg="#ce5129", fg="#000000", width=5, height=2, command=event_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Event_Light_BT.pack(padx=(1, 1), pady=(1, 1))

"""
██████╗  █████╗ ██╗██████╗ ███████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔════╝
██████╔╝███████║██║██║  ██║███████╗
██╔══██╗██╔══██║██║██║  ██║╚════██║
██║  ██║██║  ██║██║██████╔╝███████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝
"""
# Raid Raid Raid Raid
stop_thread_raid = True
def raid_items_handler(window):
    try:
        while not stop_thread_raid:
            focus_window(window_title)
            if find_image(Home, confidence=0.8): press_key(window, 'z')
            elif find_image(level3, confidence=0.85): press_key(window, '3')
            elif find_image(participate, confidence=0.97): press_key(window, 'c')
            elif find_image(toraid, confidence=0.97): press_key(window, ' ')
            elif find_image(fight, confidence=0.97): press_key(window, 'c')
            elif find_image(claimreward, confidence=0.97): press_key(window, 'c')
            elif any(find_image(image) for image in continueF): press_key(window, 'c')

            # elif any(find_image(image) for image in notifyF):
            #     subprocess.run(['python', r'C:\ms1\SH3\whatsapp.py'])
            #     time.sleep(60)

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
Raid_Light_BT = Button(ROOT, text="Raid", bg="#5a9bf7", fg="#000000", width=5, height=2, command=raid_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Raid_Light_BT.pack(padx=(1, 1), pady=(1, 1))

"""
██╗      ██████╗ ███████╗███████╗
██║     ██╔═══██╗██╔════╝██╔════╝
██║     ██║   ██║███████╗███████╗
██║     ██║   ██║╚════██║╚════██║
███████╗╚██████╔╝███████║███████║
╚══════╝ ╚═════╝ ╚══════╝╚══════╝
"""
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
            if any(find_image(image, confidence=actionF[image]) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 1)
            # elif find_image(Resume, confidence=0.8): press_key(window, 'r')
            elif find_image(SPACE, confidence=0.8) : press_key(window, ' ')
            elif find_image(StartFame): press_key(window, 'p')
            elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
            elif find_image(e_image): press_key(window, 'e')
            elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
            # elif any(find_image(image) for image in continueF): press_key(window, 'c')
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
Loss_BT = Button(ROOT, text="Loss", bg="#443e3e", fg="#fff", width=5, height=2, command=loss_function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Loss_BT.pack(padx=(1, 1), pady=(1, 1))

#!  █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗    ███████╗████████╗██╗   ██╗██╗     ███████╗
#! ██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝    ██╔════╝╚══██╔══╝╚██╗ ██╔╝██║     ██╔════╝
#! ███████║   ██║      ██║   ███████║██║     █████╔╝     ███████╗   ██║    ╚████╔╝ ██║     █████╗
#! ██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗     ╚════██║   ██║     ╚██╔╝  ██║     ██╔══╝
#! ██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗    ███████║   ██║      ██║   ███████╗███████╗
#! ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝
# light attack1
# Global flag for stopping the threads
pause_other_items = False
Action_Light_Thread = None
stop_thread_action1 = False
image_found = False
action_timer = None

#? ██████╗      ██╗
#? ██╔══██╗     ██║
#? ██║  ██║     ██║
#? ██║  ██║██   ██║
#? ██████╔╝╚█████╔╝
#? ╚═════╝  ╚════╝
# Unified function to handle both image searching and performing actions
def action_main_handler_1():
    global stop_thread_action1, image_found, pause_other_items, action_timer, Action_Light_Thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    def search_and_act():
        holding_keys = False
        while not stop_thread_action1:
            # Image searching logic
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                image_found = True
                print("Image found, resetting action timer.")
                action_timer = time.time()  # Reset the 5-second timer when image is found
            else:
                image_found = False
                print("Image not found.")
            time.sleep(0.05)  # Check image every 0.05 seconds
            # Action performing logic
            if image_found:
                pause_other_items = True
                holding_keys = True
                while holding_keys and not stop_thread_action1:
                    # Continuously press keys for 5 seconds
                    if time.time() - action_timer >= 5:
                        print("5 seconds of action completed. Stopping.")
                        holding_keys = False
                        break
                    # Key press logic
                    key_down(window, 'd')
                    press_key(window, 'j')
                    press_key(window, 'j')
                    key_up(window, 'd')
                    time.sleep(0.1)
                # Release the keys after action is completed
                key_up(window, 'd')
                pause_other_items = False
            else:
                time.sleep(0.05)  # Prevent CPU usage when idle
    # Start or stop the action handler
    if Action_Light_Thread and Action_Light_Thread.is_alive():
        stop_thread_action1 = True
        Action_Light_Thread.join()  # Wait for thread to stop
        ACTION_1_PY.config(text="dj", bg="#607af0", fg="#222222")  # Update button
    else:
        stop_thread_action1 = False
        Action_Light_Thread = threading.Thread(target=search_and_act)
        Action_Light_Thread.daemon = True
        Action_Light_Thread.start()
        ACTION_1_PY.config(text="Stop", bg="#1d2027", fg="#fc0000")  # Update button
# Button definition to start/stop the action
ACTION_1_PY = Button(ROOT, text="dj", bg="#607af0", fg="#222222", width=5, height=2,
                  command=action_main_handler_1, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_1_PY.pack(padx=(1, 1), pady=(1, 1))

#? ██╗  ██╗███████╗ █████╗ ██╗   ██╗██╗   ██╗
#? ██║  ██║██╔════╝██╔══██╗██║   ██║╚██╗ ██╔╝
#? ███████║█████╗  ███████║██║   ██║ ╚████╔╝
#? ██╔══██║██╔══╝  ██╔══██║╚██╗ ██╔╝  ╚██╔╝
#? ██║  ██║███████╗██║  ██║ ╚████╔╝    ██║
#? ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═══╝     ╚═╝
stop_thread_action3 = True
fight_thread = None
pause_other_items = False
def fight_heavy_handler(window):
    global pause_other_items
    holding_keys = False
    fight_duration = 5  # Initial duration for holding the keys (in seconds)
    try:
        while not stop_thread_action3:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                # Pause the other items handler
                pause_other_items = True
                start_time = time.time()
                while time.time() - start_time < fight_duration:
                    if not holding_keys:
                        key_down(window, 'j')
                        key_down(window, 'l')
                        holding_keys = True
                    # Check at the 3-second mark if the actionF image is still present
                    if time.time() - start_time >= 3:
                        if any(find_image(image, confidence=actionF[image]) for image in actionF):
                            print("Fight image found again. Extending time.")
                            # Extend the duration by resetting start_time and adding 5 more seconds
                            start_time = time.time()
                            fight_duration = 5
                # Release keys if holding
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'j')
                    holding_keys = False
                # Unpause the other items handler after fight is done
                pause_other_items = False
            time.sleep(0.05)
    except KeyboardInterrupt: 
        print("Fight thread stopped by user.")
    finally:
        key_up(window, 'l')
        key_up(window, 'j')
        pause_other_items = False
def fight_Heavy():
    global stop_thread_action3
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    fight_thread = threading.Thread(target=fight_heavy_handler, args=(window,))
    fight_thread.daemon = True
    fight_thread.start()
    fight_thread.join()
def fight_function():
    global stop_thread_action3, fight_thread, ACTION_3
    if fight_thread and fight_thread.is_alive():
        stop_thread_action3 = True
        fight_thread.join()
        ACTION_3.config(text="Heavy", bg="#607af0", fg="#222222")
    else:
        stop_thread_action3 = False
        fight_thread = threading.Thread(target=fight_Heavy)
        fight_thread.daemon = True
        fight_thread.start()
        ACTION_3.config(text="Stop", bg="#1d2027", fg="#fc0000")
ACTION_3 = Button(ROOT, text="Heavy", bg="#607af0", fg="#222222", width=5, height=2, command=fight_function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_3.pack(padx=(1,1), pady=(1,1))

"""
 █████╗ ██╗  ██╗██╗  ██╗     █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗
██╔══██╗██║  ██║██║ ██╔╝    ██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝
███████║███████║█████╔╝     ███████║   ██║      ██║   ███████║██║     █████╔╝
██╔══██║██╔══██║██╔═██╗     ██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗
██║  ██║██║  ██║██║  ██╗    ██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
"""
# Possessed
def action_main_handler_5():
    global stop_thread_action1, image_found, pause_other_items2, action_timer, Action_Light_Thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    def search_and_act():
        while not stop_thread_action1:
            # Image searching logic
            if any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF):
                image_found = True
                print("Image found in Light Attack 2, resetting action timer.")
                action_timer = time.time()  # Reset the 5-second timer when image is found
            else:
                image_found = False
                print("Image not found in Light Attack 2.")
            time.sleep(0.05)
            # Action performing logic
            if image_found:
                pause_other_items2 = True
                print("Triggering AHK...")
#                key_down(window, 'F13'); time.sleep(5); key_up(window, 'F13') # dj
#                key_down(window, 'F14'); time.sleep(5); key_up(window, 'F14')
#                key_down(window, 'F15'); time.sleep(5); key_up(window, 'F15')
#                key_down(window, 'F16'); time.sleep(5); key_up(window, 'F16')
#                key_down(window, 'F17'); time.sleep(5); key_up(window, 'F17')
#                key_down(window, 'F18'); time.sleep(5); key_up(window, 'F18')
                key_down(window, 'F19'); time.sleep(5); key_up(window, 'F19') # Possessed
#                key_down(window, 'F20'); time.sleep(5); key_up(window, 'F20')
#                key_down(window, 'F21'); time.sleep(5); key_up(window, 'F21')
#                key_down(window, 'F22'); time.sleep(5); key_up(window, 'F22')
#                key_down(window, 'F23'); time.sleep(5); key_up(window, 'F23')
#                key_down(window, 'F24'); time.sleep(5); key_up(window, 'F24')
                print("AHK action completed.")
                pause_other_items2 = False
            else:
                time.sleep(0.05)  # Prevent CPU usage when idle
    # Start or stop the action handler
    if Action_Light_Thread and Action_Light_Thread.is_alive():
        stop_thread_action1 = True
        Action_Light_Thread.join()  # Wait for thread to stop
        ACTION_5_AHK.config(text="AHK", bg="#5a9b5a", fg="#222222")  # Update button
    else:
        stop_thread_action1 = False
        Action_Light_Thread = threading.Thread(target=search_and_act)
        Action_Light_Thread.daemon = True
        Action_Light_Thread.start()
        ACTION_5_AHK.config(text="Stop", bg="#1d2027", fg="#fc0000")  # Update button

# Button definition to start/stop Light Attack 2
ACTION_5_AHK = Button(ROOT, text="AHK", bg="#5a9b5a", fg="#222222", width=5, height=2, command=action_main_handler_5, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_5_AHK.pack(padx=(1, 1), pady=(1, 1))

"""
 ██████╗ ██████╗ ███╗   ███╗███╗   ███╗███████╗███╗   ██╗████████╗     ██████╗ ██╗   ██╗████████╗
██╔════╝██╔═══██╗████╗ ████║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝    ██╔═══██╗██║   ██║╚══██╔══╝
██║     ██║   ██║██╔████╔██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║       ██║   ██║██║   ██║   ██║
██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║       ██║   ██║██║   ██║   ██║
╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║       ╚██████╔╝╚██████╔╝   ██║
 ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝        ╚═════╝  ╚═════╝    ╚═╝
"""
file_path = r"C:\ms1\scripts\shadowFight3\shadowFight3.py"  # Path to your script file
# Generalized function to toggle comments on specified line number
def toggle_comment(line_number, button):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # Check if line is commented
    if lines[line_number - 1].strip().startswith("#"):
        # Uncomment line by removing the #
        lines[line_number - 1] = lines[line_number - 1][1:]  # Remove the first character (the #)
        button.config(bg="#1e883e")  # Change color to #ffffff for uncommented
    else:
        # Comment line by adding a #
        lines[line_number - 1] = "#" + lines[line_number - 1]
        button.config(bg="#6b6a6a")  # Change color to red for commented
    # Write back the modified lines
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def initialize_button(line_number, button_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create a button and determine its initial state
    button = tk.Button(
        ROOT, 
        text=button_name,  # Set the custom button name
        bg="#6b6a6a",  # Default background color when first loaded
        fg="#ffffff",  # Text color
        width=0,  # Width adjusted for longer names
        height=0,
        font=("Jetbrains Mono", 10, "bold"),  # Font style
        relief="flat"  # Relief style
    )
    # Check if the line is commented to set the initial state
    if lines[line_number - 1].strip().startswith("#"):
        button.config(bg="#6b6a6a")  # Line is commented
    else:
        button.config(bg="#1e883e")  # Line is uncommented
    # Set the command for the button
    button.config(command=lambda: toggle_comment(line_number, button))
    button.pack(fill='x', padx=(1, 1), pady=(1, 1))  # Fill the horizontal space

# Initialize buttons for specified lines with custom names
initialize_button(648, "F13\ndj")
initialize_button(649, "F14")
initialize_button(650, "F15")
initialize_button(651, "F16")
initialize_button(652, "F17")
initialize_button(653, "F18")
initialize_button(654, "F19\nPOSS")
initialize_button(655, "F20")
initialize_button(656, "F21")
initialize_button(657, "F22")
initialize_button(658, "F23")
initialize_button(659, "F24")

def restart(event=None):
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)
Destroy_BT = Button(ROOT, text="RE", bg="#443e3e", fg="#fff", width=5, height=2, command=restart, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Destroy_BT.pack(padx=(1, 1), pady=(1, 1))


"""
███████╗███╗   ██╗██████╗ ██╗███╗   ██╗ ██████╗
██╔════╝████╗  ██║██╔══██╗██║████╗  ██║██╔════╝
█████╗  ██╔██╗ ██║██║  ██║██║██╔██╗ ██║██║  ███╗
██╔══╝  ██║╚██╗██║██║  ██║██║██║╚██╗██║██║   ██║
███████╗██║ ╚████║██████╔╝██║██║ ╚████║╚██████╔╝
╚══════╝╚═╝  ╚═══╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝
"""
# window title
window_title='LDPlayer'

# mhome = r"C:\Users\nahid\OneDrive\backup\shadowfight3"
# Home = rf"{mhome}\Home.png"

# Home Page of the SH3
Home=r"C:\Users\nahid\OneDrive\backup\shadowfight3\Home.png"

# Action Related Images
# void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
# eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
# thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
# collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"
# bolt=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\bolt.png"
# uppercut=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\uppercut.png"
# Peg_Top=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\peg_top.png"
# #! actionF = [void_compass, eruption, thud, collector]
# actionF = {
#     void_compass: 0.7,
#     eruption: 0.85,
#     thud: 0.7,
#     collector: 0.7,
#     uppercut: 0.7,
#     Peg_Top: 0.85,
#     # bolt: 1,
# }
# Action_region = (198, 84, 359, 241)  # Replace with your actual coordinates

temp_ac=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\temporary_action.png"
health_bar=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\bar_health.png"
shadow_bar=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\bar_shadow.png"
actionF = {
    health_bar: 0.98,
    shadow_bar: 0.85,
}
# Action_region = (352, 187, 887, 273)
Action_region = (815, 110, 892, 168)


#* Continue Related Images
# cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
# cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
# cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
# cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
# cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"
# # continueF = [cont1, cont2, cont3, cont4, cont5]
# continueF = [cont4]
ads_with_token_cont=r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\ads_cont.png"
ads_with_token_cont2=r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\ads_cont_notshown.png"
continueF = [ads_with_token_cont,ads_with_token_cont2]

#* notifyF Related Images
# currencyERR =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_currency.png"
# connectionERR =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_server1.png"
# connectionERR2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\image_65.png"
# doesnt_exist =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\not_exist.png"
# no_activity =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_activity.png"
# no_voidenergy =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_voidEnergy.png"
# home_screen =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\home_screen.png"
# notifyF = [currencyERR, connectionERR,connectionERR2,doesnt_exist,no_activity,no_voidenergy,home_screen]

#* Others
# space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
# space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
SPACE =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space2.png"
Resume =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

# Fame Related Images
e_image      =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_tournament.png"
e_image_region = (196, 656, 384, 845)  # Example coordinates and dimensions


StartFame    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_19.png"
WorldIcon    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_20.png"
GoBack       =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_21.png"

# Raids Related Images
level3         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\level3.png"
participate    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\participate.png"
toraid         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\to_raid.png"
fight          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\fightttttt.png"
claimreward    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\claim.png"

# DailyMission=r"C:\Users\nahid\OneDrive\backup\shadowfight3\DailyMission.png"

# Event Related
Tournament_step1=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\Tournament.png"
back_battlepass=r'C:\Users\nahid\OneDrive\backup\shadowfight3\back_battlepass.png'

Select_CreepyParty=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\Select\CreepyParty.png"
Select_SelectOption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\Select\Select.png"

# Advertisement
# ads1 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad1.png"
# ads2 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad2.png"
# ads3 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad3.png"
# ads4 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad4.png"
# ads5 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad5.png"
# ads6 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad6.png"
# ads7 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad7.png"
# ads8 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad8.png"
# ads9 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad9.png"
# ads10 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad10.png"
# ads11 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad11.png"
# ads12 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad12.png"
sf_ads1=r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\sf_ads1.png"
# ads_images = [ads1, ads2, ads3, ads4, ads5, ads6, ads7, ads8, ads9, ads10, ads11, ads12, sf_ads1]

ads_folder = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ads_auto_click"
ads_images = glob.glob(os.path.join(ads_folder, "*.png"))

Click_Ads=r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\Click_ADS.png"

back_GPlay=r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\Back_GooglePlay.png"
Error_Processing_Video=r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\error_Video.png"

ROOT.mainloop()

