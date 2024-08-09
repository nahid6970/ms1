import datetime
import subprocess
import sys
import time
import pyautogui
import pygetwindow as gw
import random
import threading
from tkinter import Tk, Button
from ctypes import windll, c_char_p, c_buffer
from struct import calcsize, pack
from PIL import Image
from PIL import Image, ImageDraw
import os
from tkinter import messagebox
import tkinter as tk

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
y = screen_height - 800
# ROOT.geometry(f"35x230+{x}+{y}")
ROOT.geometry(f"+{x}+{y}")

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

# Global variables
error_count = 0  # Initialize the error counter
# stop_thread = False  # Flag to stop the thread
screen_size = (10000, 10000)  # optimistic until we know better

def grab_screen(region=None):
    """Grabs a screenshot that supports multiple monitors."""
    global screen_size
    gdi32 = windll.gdi32
    # Win32 functions
    CreateDC = gdi32.CreateDCA
    CreateCompatibleDC = gdi32.CreateCompatibleDC
    GetDeviceCaps = gdi32.GetDeviceCaps
    CreateCompatibleBitmap = gdi32.CreateCompatibleBitmap
    BitBlt = gdi32.BitBlt
    SelectObject = gdi32.SelectObject
    GetDIBits = gdi32.GetDIBits
    DeleteDC = gdi32.DeleteDC
    DeleteObject = gdi32.DeleteObject
    # Win32 constants
    NULL = 0
    HORZRES = 8
    VERTRES = 10
    SRCCOPY = 13369376
    HGDI_ERROR = 4294967295
    ERROR_INVALID_PARAMETER = 87
    SM_XVIRTUALSCREEN = 76
    SM_YVIRTUALSCREEN = 77
    SM_CXVIRTUALSCREEN = 78
    SM_CYVIRTUALSCREEN = 79

    bitmap = None
    try:
        screen = CreateDC(c_char_p(b'DISPLAY'), NULL, NULL, NULL)
        screen_copy = CreateCompatibleDC(screen)

        if region:
            left, top, width, height = region
        else:
            left = windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
            top = windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
            width = windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            height = windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

        bitmap = CreateCompatibleBitmap(screen, width, height)
        if bitmap == NULL:
            print('grab_screen: Error calling CreateCompatibleBitmap. Returned NULL')
            return

        hobj = SelectObject(screen_copy, bitmap)
        if hobj == NULL or hobj == HGDI_ERROR:
            print(f'grab_screen: Error calling SelectObject. Returned {hobj}.')
            return

        if BitBlt(screen_copy, 0, 0, width, height, screen, left, top, SRCCOPY) == NULL:
            print('grab_screen: Error calling BitBlt. Returned NULL.')
            return

        bitmap_header = pack('LHHHH', calcsize('LHHHH'), width, height, 1, 24)
        bitmap_buffer = c_buffer(bitmap_header)
        bitmap_bits = c_buffer(b' ' * (height * ((width * 3 + 3) & -4)))
        got_bits = GetDIBits(screen_copy, bitmap, 0, height, bitmap_bits, bitmap_buffer, 0)
        if got_bits == NULL or got_bits == ERROR_INVALID_PARAMETER:
            print(f'grab_screen: Error calling GetDIBits. Returned {got_bits}.')
            return

        image = Image.frombuffer('RGB', (width, height), bitmap_bits, 'raw', 'BGR', (width * 3 + 3) & -4, -1)
        if not region:
            screen_size = image.size
        return image
    finally:
        if bitmap is not None:
            if bitmap:
                DeleteObject(bitmap)
            DeleteDC(screen_copy)
            DeleteDC(screen)

# Override pyautogui's screenshot functions with our custom function
pyautogui.screenshot = grab_screen
pyautogui.pyscreeze.screenshot = grab_screen
pyautogui.size = lambda: screen_size

# Rest of the code remains the same


# def find_image(image_path, confidence=0.7):
#     """Find the location of the image on the screen."""
#     global error_count
#     try:
#         location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
#         if location:
#             image_name = os.path.basename(image_path)
#             print(f"Found image: {image_name}")
#             return location
#     except Exception as e:
#         error_count += 1
#         print(f"{error_count} times not found. Error: {e}")
#     return None

def find_image(image_path, confidence=0.7):
    """Find the location of the image on the screen and show time in 12-hour format."""
    global error_count
    
    def get_current_time():
        """Return the current time in 12-hour format."""
        return datetime.datetime.now().strftime("%I:%M:%S %p")

    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
        if location:
            image_name = os.path.basename(image_path)
            print(f"{get_current_time()} - Found image: {image_name}")
            return location
    except Exception as e:
        error_count += 1
        print(f"{get_current_time()} - {error_count} times not found. Error: {e}")
    return None

# # error_count = 0  # Make sure to initialize this variable
# # stop_thread = False  # Initialize stop_thread
# def find_image(image_path, confidence=0.7, timeout=60):
#     """Find the location of the image on the screen."""
#     global error_count, stop_thread
#     start_time = time.time()
#     while True:
#         # Check if stop_thread is set to True
#         if stop_thread:
#             print("Stopping the function due to stop_thread being set to True.")
#             return None
#         try:
#             location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
#             if location:
#                 image_name = os.path.basename(image_path)
#                 print(f"Found image: {image_name}")
#                 return location
#         except Exception as e:
#             error_count += 1
#             print(f"{error_count} times not found. Error: {e}")
#         # Check if timeout has been reached
#         elapsed_time = time.time() - start_time
#         if elapsed_time >= timeout:
#             print("Timeout reached. Clicking shortcut Ctrl+Shift+M.")
#             pyautogui.hotkey('ctrl', 'shift', 'm')
#             return None
#         # Sleep for a short while to avoid excessive CPU usage
#         time.sleep(0.5)


# last_found_time = time.time()
# def find_image(image_path, confidence=0.7):
#     """Find the location of the image on the screen."""
#     global error_count, last_found_time
#     try:
#         location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
#         if location:
#             image_name = os.path.basename(image_path)
#             print(f"Found image: {image_name}")
#             last_found_time = time.time()  # Update the last found time
#             return location
#     except Exception as e:
#         error_count += 1
#         print(f"{error_count} times not found. Error: {e}")
#     # Check if one minute has passed since the last found time
#     if time.time() - last_found_time > 60:
#         show_message("Error Finding Critical Sys File For 1 Minute")
#         last_found_time = time.time()  # Reset the last found time to avoid repeated messages
#     return None

# def show_message(message):
#     messagebox.showinfo("Information", message, parent=ROOT)


def focus_window(window_title):
    """Set focus to the window with the given title."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
        window.activate()
        return window
    return None

def press_key(window, key):
    """Send a key press to a specific window."""
    window.activate()
    pyautogui.press(key)

def key_down(window, key):
    """Send a key down event to a specific window."""
    window.activate()
    pyautogui.keyDown(key)

def key_up(window, key):
    """Send a key up event to a specific window."""
    window.activate()
    pyautogui.keyUp(key)

def click(window, x, y):
    """Send a mouse click to a specific window."""
    window.activate()
    pyautogui.click(x, y)

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


window_title='LDPlayer'

#* Home Page of the SH3
Home=r"C:\Users\nahid\OneDrive\backup\shadowfight3\Home.png"

#* Action Related Images
void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"
bolt=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\bolt.png"
uppercut=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\uppercut.png"
#! actionF = [void_compass, eruption, thud, collector]
actionF = {
    void_compass: 0.7,
    eruption: 0.85,
    thud: 0.7,
    collector: 0.7,
    uppercut: 0.7,
    # bolt: 1,
}

#* Continue Related Images
cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"
continueF = [cont1, cont2, cont3, cont4, cont5]

#* Others
# space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
# space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
SPACE =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space2.png"
Resume =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

#* Fame Related Images
e_image      =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_tournament.png"
StartFame    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_19.png"
WorldIcon    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_20.png"
GoBack       =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_21.png"

#* Raids Related Images
level3         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\level3.png"
participate    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\participate.png"
toraid         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\to_raid.png"
fight          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\fightttttt.png"
claimreward    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\claim.png"


#* Event Related
Tournament_step1=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\Tournament.png"
Tournament_step2=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\SELECT.png"

#* Threads
stop_thread = True
fight_thread = None

fame_heavy_thread = None
fame_light_thread = None

event_light_thread = None
event_heavy_thread = None

raid_heavy_thread = None
raid_light_thread = None

loss_thread = None
"""
███████╗██╗ ██████╗ ██╗  ██╗████████╗
██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
█████╗  ██║██║  ███╗███████║   ██║
██╔══╝  ██║██║   ██║██╔══██║   ██║
██║     ██║╚██████╔╝██║  ██║   ██║
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
"""

def fight_Heavy():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    
    holding_keys = False
    try:
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                if not holding_keys:
                    key_down(window, 'j')
                    key_down(window, 'l')
                    holding_keys = True
            else:
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'j')
                    holding_keys = False
            if find_image(SPACE, confidence=0.8):
                press_key(window, ' ')
            elif any(find_image(image) for image in continueF):
                press_key(window, 'c')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        key_up(window, 'l')
        key_up(window, 'j')
def fight_function():
    global stop_thread, fight_thread, Fight_BT
    if fight_thread and fight_thread.is_alive():
        stop_thread = True
        fight_thread.join()
        Fight_BT.config(text="\ueefd", bg="#6a6a64", fg="#9dff00")
    else:
        stop_thread = False
        fight_thread = threading.Thread(target=fight_Heavy)
        fight_thread.daemon = True
        fight_thread.start()
        Fight_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Fight_BT = Button(ROOT, text="\ueefd", bg="#6a6a64", fg="#9dff00", width=5, height=2, command=fight_function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Fight_BT.pack(padx=(2, 2), pady=(3, 0))

"""
███████╗ █████╗ ███╗   ███╗███████╗
██╔════╝██╔══██╗████╗ ████║██╔════╝
█████╗  ███████║██╔████╔██║█████╗
██╔══╝  ██╔══██║██║╚██╔╝██║██╔══╝
██║     ██║  ██║██║ ╚═╝ ██║███████╗
╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
"""
def fame_heavy():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    
    holding_keys = False
    try:
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                if not holding_keys:
                    key_down(window, 'j')
                    key_down(window, 'l')
                    holding_keys = True
                time.sleep(1)
            else:
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'j')
                    holding_keys = False
                if find_image(Resume, confidence=0.8): press_key(window, 'r')
                elif find_image(SPACE, confidence=0.8): press_key(window, ' ')
                elif find_image(StartFame): press_key(window, 'p')
                elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
                elif find_image(e_image): press_key(window, 'e')
                elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
                elif any(find_image(image) for image in continueF): press_key(window, 'c')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        key_up(window, 'l')
        key_up(window, 'j')
def fame_function_heavy():
    global stop_thread, fame_heavy_thread, Fame_Heavy_BT
    if fame_heavy_thread and fame_heavy_thread.is_alive():
        stop_thread = True
        fame_heavy_thread.join()
        Fame_Heavy_BT.config(text="FH", bg="#bda24a", fg="#000000")
    else:
        stop_thread = False
        fame_heavy_thread = threading.Thread(target=fame_heavy)
        fame_heavy_thread.daemon = True
        fame_heavy_thread.start()
        Fame_Heavy_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Fame_Heavy_BT = Button(ROOT, text="FH", bg="#bda24a", fg="#000000", width=5, height=2, command=fame_function_heavy, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Fame_Heavy_BT.pack(padx=(1, 1), pady=(1, 1))

def fame_light():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    
    holding_keys = False
    try:
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                start_time = time.time()
                while time.time() - start_time < 10:  # Loop for 10 seconds
                    if not holding_keys:
                        key_down(window, 'd')
                        key_down(window, 'l')
                        holding_keys = True
                    # Press 'j' rapidly
                    press_key(window, 'j')
                    time.sleep(0.001)  # Reduce sleep time for rapid pressing
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'd')
                    holding_keys = False
            else:
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'd')
                    holding_keys = False
                if find_image(Resume, confidence=0.8): press_key(window, 'r')
                elif find_image(SPACE, confidence=0.8): press_key(window, ' ')
                elif find_image(StartFame): press_key(window, 'p')
                elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
                elif find_image(e_image): press_key(window, 'e')
                elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
                elif any(find_image(image) for image in continueF): press_key(window, 'c')
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        key_up(window, 'l')
        key_up(window, 'j')
def fame_function_light():
    global stop_thread, fame_light_thread, Fame_Light_BT
    if fame_light_thread and fame_light_thread.is_alive():
        stop_thread = True
        fame_light_thread.join()
        Fame_Light_BT.config(text="FL", bg="#bda24a", fg="#000000")
    else:
        stop_thread = False
        fame_light_thread = threading.Thread(target=fame_light)
        fame_light_thread.daemon = True
        fame_light_thread.start()
        Fame_Light_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Fame_Light_BT = Button(ROOT, text="FL", bg="#bda24a", fg="#000000", width=5, height=3, command=fame_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Fame_Light_BT.pack(padx=(1, 1), pady=(1, 1))

"""
███████╗██╗   ██╗███████╗███╗   ██╗████████╗
██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝
█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║
██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║
███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║
╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝
"""


# def start_event_heavy():
#     global stop_thread
#     window = focus_window(window_title)
#     if not window:
#         print(f"Window '{window_title}' not found.")
#         return
#     try:
#         while not stop_thread:
#             focus_window(window_title)
#             if any(find_image(image) for image in actionF):
#                 key_down(window, 'j')
#                 key_down(window, 'l')
#                 time.sleep(5)
#                 key_up(window, 'l')
#                 key_up(window, 'j')
#             elif find_image(Home, confidence=0.8): press_key(window, 'f')
#             elif find_image(Resume, confidence=0.8): press_key(window, 'r')
#             elif any(find_image(image) for image in continueF): press_key(window, 'c')
#             elif find_image(Tournament_step1, confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
#             elif find_image(Tournament_step2, confidence=0.8): press_keys_with_delays(window, '1', 1)
#             time.sleep(0.1)
#     except KeyboardInterrupt: print("Script stopped by user.")
# def event_function_heavy():
#     global stop_thread, event_heavy_thread, Event_Heavy_BT
#     if event_heavy_thread and event_heavy_thread.is_alive():
#         stop_thread = True
#         event_heavy_thread.join()
#         Event_Heavy_BT.config(text="EH", bg="#ce5129", fg="#000000")
#     else:
#         stop_thread = False
#         event_heavy_thread = threading.Thread(target=start_event_heavy)
#         event_heavy_thread.daemon = True
#         event_heavy_thread.start()
#         Event_Heavy_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

# Event_Heavy_BT = Button(ROOT, text="EH", bg="#ce5129", fg="#000000", width=5, height=3, command=event_function_heavy, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
# Event_Heavy_BT.pack(padx=(1, 1), pady=(1, 1))

# def start_event_heavy():
#     global stop_thread
#     window = focus_window(window_title)
#     if not window:
#         print(f"Window '{window_title}' not found.")
#         return
#     try:
#         last_found_time = time.time()  # Initialize the timer
#         while not stop_thread:
#             focus_window(window_title)
#             if any(find_image(image) for image in actionF):
#                 key_down(window, 'j')
#                 key_down(window, 'l')
#                 time.sleep(5)
#                 key_up(window, 'l')
#                 key_up(window, 'j')
#                 last_found_time = time.time()  # Reset the timer
#             elif find_image(Home, confidence=0.8):
#                 press_key(window, 'f')
#                 last_found_time = time.time()  # Reset the timer
#             elif find_image(Resume, confidence=0.8):
#                 press_key(window, 'r')
#                 last_found_time = time.time()  # Reset the timer
#             elif any(find_image(image) for image in continueF):
#                 press_key(window, 'c')
#                 last_found_time = time.time()  # Reset the timer
#             elif find_image(Tournament_step1, confidence=0.8):
#                 press_keys_with_delays(window, 'u', 1, 'c', 1)
#                 last_found_time = time.time()  # Reset the timer
#             elif find_image(Tournament_step2, confidence=0.8):
#                 press_keys_with_delays(window, '1', 1)
#                 last_found_time = time.time()  # Reset the timer
            
#             # Check if 10 seconds have passed since the last image was found
#             if time.time() - last_found_time > 60:
#                 print("No image found for 10 seconds, stopping function.")
#                 pyautogui.hotkey('ctrl', 'shift', 'm')  # Trigger the shortcut
#                 break

#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         print("Script stopped by user.")

# def event_function_heavy():
#     global stop_thread, event_heavy_thread, Event_Heavy_BT
#     if event_heavy_thread and event_heavy_thread.is_alive():
#         stop_thread = True
#         event_heavy_thread.join()
#         Event_Heavy_BT.config(text="EH", bg="#ce5129", fg="#000000")
#     else:
#         stop_thread = False
#         event_heavy_thread = threading.Thread(target=start_event_heavy)
#         event_heavy_thread.daemon = True
#         event_heavy_thread.start()
#         Event_Heavy_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

# Event_Heavy_BT = Button(ROOT, text="EH", bg="#ce5129", fg="#000000", width=5, height=3, command=event_function_heavy, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
# Event_Heavy_BT.pack(padx=(1, 1), pady=(1, 1))

def start_event_heavy():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        last_found_time = time.time()  # Initialize the timer
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image) for image in actionF): key_down(window, 'j'); key_down(window, 'l'); time.sleep(5); key_up(window, 'l'); key_up(window, 'j'); last_found_time = time.time()
            elif find_image(Home, confidence=0.8): press_key(window, 'f'); last_found_time = time.time()
            elif find_image(Resume, confidence=0.8): press_key(window, 'r'); last_found_time = time.time()
            elif any(find_image(image) for image in continueF): press_key(window, 'c'); last_found_time = time.time()
            elif find_image(Tournament_step1, confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1); last_found_time = time.time()
            elif find_image(Tournament_step2, confidence=0.8): press_keys_with_delays(window, '1', 1); last_found_time = time.time()
            
            if time.time() - last_found_time > 60: print("No image found for 60 seconds, stopping function."); pyautogui.hotkey('ctrl', 'shift', 'm'); break
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")

def event_function_heavy():
    global stop_thread, event_heavy_thread, Event_Heavy_BT
    if event_heavy_thread and event_heavy_thread.is_alive():
        stop_thread = True
        event_heavy_thread.join()
        Event_Heavy_BT.config(text="EH", bg="#ce5129", fg="#000000")
    else:
        stop_thread = False
        event_heavy_thread = threading.Thread(target=start_event_heavy)
        event_heavy_thread.daemon = True
        event_heavy_thread.start()
        Event_Heavy_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Event_Heavy_BT = Button(ROOT, text="EH", bg="#ce5129", fg="#000000", width=5, height=3, command=event_function_heavy, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Event_Heavy_BT.pack(padx=(1, 1), pady=(1, 1))



def Start_Event_Light():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    holding_keys = False
    try:
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                start_time = time.time()
                while time.time() - start_time < 5:
                    if not holding_keys:
                        key_down(window, 'd')
                        key_down(window, 'l')
                        holding_keys = True
                    # Press 'j' rapidly
                    press_key(window, 'j')
                    time.sleep(0.001)  # Reduce sleep time for rapid pressing
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'd')
                    holding_keys = False
            else:
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'd')
                    holding_keys = False
                elif find_image(Home, confidence=0.8): press_key(window, 'f')
                elif find_image(Resume, confidence=0.8): press_key(window, 'r')
                # elif find_image(cont1, confidence=0.8) or find_image(cont2, confidence=0.8): press_key(window, 'c')
                elif any(find_image(image) for image in continueF): press_key(window, 'c')
                elif find_image(Tournament_step1, confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
                elif find_image(Tournament_step2, confidence=0.8): press_keys_with_delays(window, '1', 1)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        key_up(window, 'l')
        key_up(window, 'j')
def event_function_light():
    global stop_thread, event_light_thread, Event_Light_BT
    if event_light_thread and event_light_thread.is_alive():
        stop_thread = True
        event_light_thread.join()
        Event_Light_BT.config(text="EL", bg="#ce5129", fg="#000000")
    else:
        stop_thread = False
        event_light_thread = threading.Thread(target=Start_Event_Light)
        event_light_thread.daemon = True
        event_light_thread.start()
        Event_Light_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Event_Light_BT = Button(ROOT, text="EL", bg="#ce5129", fg="#000000", width=5, height=3, command=event_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Event_Light_BT.pack(padx=(1, 1), pady=(1, 1))

"""
██████╗  █████╗ ██╗██████╗ ███████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔════╝
██████╔╝███████║██║██║  ██║███████╗
██╔══██╗██╔══██║██║██║  ██║╚════██║
██║  ██║██║  ██║██║██████╔╝███████║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝
"""
def Raids():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    holding_keys = False  # To track if 'j' and 'l' are being held down
    try:
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                if not holding_keys:
                    key_down(window, 'j')
                    key_down(window, 'l')
                    holding_keys = True
                time.sleep(1)
            else:
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'j')
                    holding_keys = False
                if find_image(Home, confidence=0.8): press_key(window, 'z')
                elif find_image(level3, confidence=0.85): press_key(window, '3')
                elif find_image(participate, confidence=0.97): press_key(window, 'c')
                elif find_image(toraid, confidence=0.97): press_key(window, ' ')
                elif find_image(fight, confidence=0.97): press_key(window, 'c')
                elif find_image(claimreward, confidence=0.97): press_key(window, 'c')
                elif any(find_image(image) for image in continueF): press_key(window, 'c')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        # Ensure keys are released if the loop exits
        key_up(window, 'l')
        key_up(window, 'j')
def raid_function_heavy():
    global stop_thread, raid_heavy_thread, Raid_Heavy_BT
    if raid_heavy_thread and raid_heavy_thread.is_alive():
        stop_thread = True
        raid_heavy_thread.join()
        Raid_Heavy_BT.config(text="RH", bg="#5a9bf7", fg="#000000")
    else:
        stop_thread = False
        raid_heavy_thread = threading.Thread(target=Raids)
        raid_heavy_thread.daemon = True
        raid_heavy_thread.start()
        Raid_Heavy_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Raid_Heavy_BT = Button(ROOT, text="RH", bg="#5a9bf7", fg="#000000", width=5, height=3, command=raid_function_heavy, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Raid_Heavy_BT.pack(padx=(1, 1), pady=(1, 1))



def Raid_Light():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    holding_keys = False
    try:
        while not stop_thread:
            focus_window(window_title)
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                start_time = time.time()
                while time.time() - start_time < 5:
                    if not holding_keys:
                        key_down(window, 'd')
                        key_down(window, 'l')
                        holding_keys = True
                    # Press 'j' rapidly
                    press_key(window, 'j')
                    time.sleep(0.001)  # Reduce sleep time for rapid pressing
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'd')
                    holding_keys = False
            else:
                if holding_keys:
                    key_up(window, 'l')
                    key_up(window, 'd')
                    holding_keys = False
                elif find_image(Home, confidence=0.8): press_key(window, 'z')
                elif find_image(level3, confidence=0.85): press_key(window, '3')
                elif find_image(participate, confidence=0.97): press_key(window, 'c')
                elif find_image(toraid, confidence=0.97): press_key(window, ' ')
                elif find_image(fight, confidence=0.97): press_key(window, 'c')
                elif find_image(claimreward, confidence=0.97): press_key(window, 'c')
                elif any(find_image(image) for image in continueF): press_key(window, 'c')
            time.sleep(1)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Script stopped by user.")
    finally:
        key_up(window, 'l')
        key_up(window, 'j')
def raid_function_light():
    global stop_thread, raid_light_thread, Raid_Light_BT
    if raid_light_thread and raid_light_thread.is_alive():
        stop_thread = True
        raid_light_thread.join()
        Raid_Light_BT.config(text="RL", bg="#5a9bf7", fg="#000000")
    else:
        stop_thread = False
        raid_light_thread = threading.Thread(target=Raid_Light)
        raid_light_thread.daemon = True
        raid_light_thread.start()
        Raid_Light_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Raid_Light_BT = Button(ROOT, text="RL", bg="#5a9bf7", fg="#000000", width=5, height=3, command=raid_function_light, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Raid_Light_BT.pack(padx=(1, 1), pady=(1, 1))

"""
██╗      ██████╗ ███████╗███████╗
██║     ██╔═══██╗██╔════╝██╔════╝
██║     ██║   ██║███████╗███████╗
██║     ██║   ██║╚════██║╚════██║
███████╗╚██████╔╝███████║███████║
╚══════╝ ╚═════╝ ╚══════╝╚══════╝
"""
def TakeL():
    global stop_thread
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            #* if any(find_image(image) for image in actionF):
            if any(find_image(image, confidence=actionF[image]) for image in actionF): press_keys_with_delays(window, 'q', 1, 'b', 1, "m", 1)

            # elif find_image(Resume, confidence=0.8): press_key(window, 'r')
            elif find_image(SPACE, confidence=0.8) : press_key(window, ' ')
            elif find_image(StartFame): press_key(window, 'p')
            elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
            elif find_image(e_image): press_key(window, 'e')
            elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
            elif any(find_image(image) for image in continueF): press_key(window, 'c')

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")

def loss_function():
    global stop_thread, loss_thread, Loss_BT
    if loss_thread and loss_thread.is_alive():
        stop_thread = True
        loss_thread.join()
        Loss_BT.config(text="L", bg="#0c0c0c", fg="#fc0000")
    else:
        stop_thread = False
        loss_thread = threading.Thread(target=TakeL)
        loss_thread.daemon = True
        loss_thread.start()
        Loss_BT.config(text="Stop", bg="#1d2027", fg="#fc0000")

Loss_BT = Button(ROOT, text="L", bg="#0c0c0c", fg="#fc0000", width=5, height=3, command=loss_function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Loss_BT.pack(padx=(1, 1), pady=(1, 1))










ROOT.mainloop()










# Restart_bt=Button(ROOT,text="Restart",command=restart       , width=15,height=4,bg="#1d2027",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
# Exit_bt   =Button(ROOT,text="Exit"   ,command=close_window  , width=15,height=4,bg="#1d2027",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
