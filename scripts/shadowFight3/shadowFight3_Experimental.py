# from ctypes import windll, c_char_p, c_buffer
# from PIL import Image
# from PIL import Image, ImageDraw
# from struct import calcsize, pack
# from tkinter import messagebox
# import gc  # Import garbage collector
# import random
from datetime import datetime
from tkinter import Tk, Button, messagebox
import glob
import os
import keyboard
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
y = screen_height - 970
ROOT.geometry(f"+{x}+{y}")

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

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
#                key_down(window, 'F16'); time.sleep(5); key_up(window, 'F16') # THOR
#                key_down(window, 'F17'); time.sleep(5); key_up(window, 'F17')
#                key_down(window, 'F18'); time.sleep(5); key_up(window, 'F18')
#                key_down(window, 'F19'); time.sleep(5); key_up(window, 'F19') # Possessed
                key_down(window, 'F20'); time.sleep(5); key_up(window, 'F20')
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

# Initialize variables
last_found_time = None
is_searching = False
last_used_time = time.time()  # Tracks when the function was last called
image_found_count = {}  # Dictionary to store cumulative counts of found images

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
        WhatsPhotoClick()  # Run the script instead of showing a message
        last_found_time = time.time()  # Reset the last found time to avoid repeated executions
    return None

def WhatsPhotoClick():
    pyautogui.click(x=1778, y=900)
    time.sleep(2)
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while True:  # Loop will continue indefinitely unless interrupted by an external condition
            focus_window(window_title)
            if find_image(profile_pic): press_global_screen_with_delays((294,299,5),(594,908,2))
            if find_image(call_me): press_global_screen_with_delays((238,271,60))
            # elif find_image(cancel, confidence=0.8): press_keys_with_delays(window, "c", 1)

            # [click(window, IMG_CORDINATE.left + IMG_CORDINATE.width // 2, IMG_CORDINATE.top + IMG_CORDINATE.height // 2) or time.sleep(5) 
            # for _ in [1] if (IMG_CORDINATE := find_image(profile_pic, confidence=0.8))]

            # [click(window, IMG_CORDINATE.left + IMG_CORDINATE.width // 2, IMG_CORDINATE.top + IMG_CORDINATE.height // 2) or time.sleep(5) 
            # for _ in [1] if (IMG_CORDINATE := find_image(call_me, confidence=0.8))]

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
            # elif any(find_image(image) for image in continueF): press_keys_with_delays(window, 'c', 2,  "e", 0 )
            elif any(find_image(image, region=contF_Region) for image in continueF): press_keys_with_delays(window, 'c', 2, "e", 0)

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

def event_function_Main():
    global stop_thread_event, event_light_thread, Event_Light_BT

    def event_items_handler(window):
        try:
            # Define the folder where the images are stored
            Jewel_of_Folder = r'C:\msBackups\shadowfight3\priority_images\Jewel_of_Trash'

            # Get a list of all image files in the folder, sorted by their numeric filename
            image_files = [f for f in os.listdir(Jewel_of_Folder) if f.endswith('.png')]
            image_files.sort(key=lambda x: int(x.split('.')[0]))  # Sort by numeric part of filename
            
            # Create prioritized_images list by assigning priority based on filename order
            prioritized_images = [(os.path.join(Jewel_of_Folder, img), int(img.split('.')[0])) for img in image_files]


            while not stop_thread_event:
                focus_window(window_title)

                if find_image(Home, confidence=0.8): 
                    press_key(window, 'f')

                elif find_image(Resume, confidence=0.8): 
                    press_key(window, 'r')

                elif find_image(Tournament_step1, confidence=0.8): 
                    press_keys_with_delays(window, 'u', 1, 'c', 1)

                elif find_image(later, confidence=0.8): 
                    press_global_screen_with_delays((1113, 728, 1)) #! need fixing
                
                elif find_image(Open_Chest, confidence=0.8): 
                    press_keys_with_delays(window, 'c', 4, 'c', 3, 'g', 1)

                elif find_image(skip, confidence=0.8): 
                    press_keys_with_delays(window, ' ', 1) #! optional

                # Handle dynamic content
                [press_keys_with_delays(window, 'c', 1) 
                 for contimg in cont_dynamic if (location := find_image(contimg, confidence=0.8, region=contF_Region))]

                # Check prioritized images
                for img_path, _ in prioritized_images:
                    location = find_image(img_path, confidence=0.8)
                    if location:
                        # Extract the coordinates of the found image
                        x, y = location[0], location[1]
                        # Add the offset to the image location (10, 5)
                        click_x = x + 187
                        click_y = y + 550
                        # Simulate a click at the adjusted coordinates
                        pyautogui.click(click_x, click_y)
                        break  # Click only the first detected image with the highest priority

                # # Test First
                # for img_path, _ in prioritized_images:
                #     location = find_image(img_path, confidence=0.8)
                #     if location:
                #         # Extract the coordinates of the found image
                #         x, y = location[0], location[1]
                #         # Add the offset to the image location (187, 575)
                #         move_x = x + 187
                #         move_y = y + 550
                #         # Move the mouse to the adjusted coordinates (no click)
                #         pyautogui.moveTo(move_x, move_y, duration=1)  # The duration can be adjusted
                #         # Optionally, print out the coordinates for debugging
                #         print(f"Mouse moved to: {move_x}, {move_y}")
                #         break


                time.sleep(0.05)
        except KeyboardInterrupt:
            print("Other items thread stopped by user.")


    if event_light_thread and event_light_thread.is_alive():
        stop_thread_event = True
        event_light_thread.join()
        Event_Light_BT.config(text="Event", bg="#ce5129", fg="#000000")
    else:
        stop_thread_event = False
        window = focus_window(window_title)
        if not window:
            print(f"Window '{window_title}' not found.")
            return
        event_light_thread = threading.Thread(target=event_items_handler, args=(window,))
        event_light_thread.daemon = True
        event_light_thread.start()
        Event_Light_BT.config(text="Event", bg="#1d2027", fg="#fc0000")

Event_Light_BT = Button( ROOT, text="Event", bg="#ce5129", fg="#000000", width=5, height=2, command=event_function_Main, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat" )
Event_Light_BT.pack(padx=(1, 1), pady=(1, 1))

#!  ███████╗██╗   ██╗███████╗███╗   ██╗████████╗    ██╗    ██╗     █████╗ ██████╗ ███████╗
#!  ██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝    ██║    ██║    ██╔══██╗██╔══██╗██╔════╝
#!  █████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║       ██║ █╗ ██║    ███████║██║  ██║███████╗
#!  ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║       ██║███╗██║    ██╔══██║██║  ██║╚════██║
#!  ███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║       ╚███╔███╔╝    ██║  ██║██████╔╝███████║
#!  ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝        ╚══╝╚══╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝
def event_function_Ads():
    global stop_thread_event, event_light_thread, Event_Light_BT
    def event_items_handler(window):
        try:
            while not stop_thread_event:
                focus_window(window_title)
                # Handle the other image searches and actions
                if find_image(Home, confidence=0.8): press_key(window, 'f')
                elif find_image(Resume, confidence=0.8): press_key(window, 'r')

                elif find_image(Error_Processing_Video, confidence=0.8): press_key(window, 'esc') #! optional
                elif any(find_image(image, confidence=0.95) for image in continueADS): press_keys_with_delays(window, 'c', 1)

                elif find_image(Tournament_step1, confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)

                elif find_image(later, confidence=0.8): press_global_screen_with_delays(( 1113, 728, 1)) #! need fixing

                # elif find_image(Select_CreepyParty, confidence=0.8): press_keys_with_delays(window, 'y', 1) #! optional
                elif find_image(Select_SelectOption, confidence=0.8): press_keys_with_delays(window, '2', 1) #! optional

                # elif find_image(back_battlepass, confidence=0.8): press_keys_with_delays(window, 'b', 1)
                elif find_image(back_GPlay, confidence=0.8): press_ldplayer_screen_with_delays(window, (1628, 815, 2)) #! optional

                # elif any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 0) #! optional

                [click(window, ad_location.left + ad_location.width // 2, ad_location.top + ad_location.height // 2)
                for ad_image in ads_images if (ad_location := find_image(ad_image, confidence=0.8))]

                # for ad_image in ads_images: #! optional
                #     ad_location = find_image(ad_image, confidence=0.8)
                #     if ad_location:
                #         click(window, ad_location.left, ad_location.top) 

                # [click(window, ad_location.left, ad_location.top) for ad_image in ads_images if (ad_location := find_image(ad_image, confidence=0.8))]

                # click the middle part of the ads
                # [click(window, ad_location.left + ad_location.width // 2, ad_location.top + ad_location.height // 2) #! optional
                # for ad_image in ads_images if (ad_location := find_image(ad_image, confidence=0.8))]

                time.sleep(0.05)
        except KeyboardInterrupt: print("Other items thread stopped by user.")

    if event_light_thread and event_light_thread.is_alive():
        stop_thread_event = True
        event_light_thread.join()
        Event_w_Ads_BT.config(text="Event\nAds", bg="#ce5129", fg="#000000")
    else:
        stop_thread_event = False
        window = focus_window(window_title)
        if not window:
            print(f"Window '{window_title}' not found.")
            return
        event_light_thread = threading.Thread(target=event_items_handler, args=(window,))
        event_light_thread.daemon = True
        event_light_thread.start()
        Event_w_Ads_BT.config(text="Event\nAds", bg="#1d2027", fg="#fc0000")

Event_w_Ads_BT = Button( ROOT, text="Event\nAds", bg="#ce5129", fg="#000000", width=5, height=2, command=event_function_Ads, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat" )
Event_w_Ads_BT.pack(padx=(1, 1), pady=(1, 1))
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
            elif find_image(level3, confidence=0.85): press_keys_with_delays(window, '3',2, "c",1)
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
            if any(find_image(image, confidence=actionF[image], region=Action_region) for image in actionF): press_keys_with_delays(window, 'q', 1, '0', 1, "m", 1)
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
initialize_button(73, "F13\ndj")
initialize_button(74, "F14")
initialize_button(75, "F15")
initialize_button(76, "F16\nTHOR")
initialize_button(77, "F17")
initialize_button(78, "F18")
initialize_button(79, "F19\nPOSS")
initialize_button(80, "F20\nHound")
initialize_button(81, "F21\nLaggy")
initialize_button(82, "F22")
initialize_button(83, "F23")
initialize_button(84, "F24")

# Restart function that displays the cumulative summary before restarting
def restart():
    display_image_found_chart()  # Show the summary of found images
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

# Button to restart the script
Restart_BT = Button(ROOT, text="RE", bg="#443e3e", fg="#fff", width=5, height=2, command=restart, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Restart_BT.pack(padx=(1, 1), pady=(1, 1))
# keyboard.add_hotkey("esc", restart)

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
#! actionF = [void_compass, eruption, thud, collector]
actionF = {
    void_compass: 0.7,
    eruption: 0.85,
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




"""
██╗    ██╗██╗  ██╗ █████╗ ████████╗███████╗ █████╗ ██████╗ ██████╗
██║    ██║██║  ██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗
██║ █╗ ██║███████║███████║   ██║   ███████╗███████║██████╔╝██████╔╝
██║███╗██║██╔══██║██╔══██║   ██║   ╚════██║██╔══██║██╔═══╝ ██╔═══╝
╚███╔███╔╝██║  ██║██║  ██║   ██║   ███████║██║  ██║██║     ██║
 ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
"""
profile_pic=r'C:\msBackups\shadowfight3\whatsapp\whatsapp_mobile\Enter_Whatsapp.png'
call_me=r'C:\msBackups\shadowfight3\whatsapp\whatsapp_mobile\call.png'
cancel=r'C:\msBackups\shadowfight3\whatsapp\whatsapp_mobile\cancel.png'
ROOT.mainloop()