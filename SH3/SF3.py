# from ctypes import windll, c_char_p, c_buffer
# from PIL import Image
# from PIL import Image, ImageDraw
# from struct import calcsize, pack
# from tkinter import messagebox
# from tkinter import messagebox
from tkinter import Tk, Button, messagebox
import datetime
import os
import pyautogui
import pygetwindow as gw
import random
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
y = screen_height - 800
ROOT.geometry(f"+{x}+{y}")

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

error_count = 0
last_found_time = time.time()
def find_image(image_path, confidence=0.7):
    """Find the location of the image on the screen."""
    global error_count, last_found_time
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
        if location:
            image_name = os.path.basename(image_path)
            print(f"Found image: {image_name}")
            last_found_time = time.time()  # Update the last found time
            return location
    except Exception as e:
        error_count += 1
        print(f"{error_count} times not found. Error: {e}")
    # Check if 5 seconds have passed since the last found time
    if time.time() - last_found_time > 120:
        run_script()  # Run the script instead of showing a message
        last_found_time = time.time()  # Reset the last found time to avoid repeated executions
    return None
def run_script():
    """Run the whatsapp.py script."""
    try:
        # Replace "python" with the full path to Python if needed
        subprocess.run(["python", r"C:\ms1\SH3\whatsapp.py"], check=True)
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



# window title
window_title='LDPlayer'

# Home Page of the SH3
Home=r"C:\Users\nahid\OneDrive\backup\shadowfight3\Home.png"

# Action Related Images
void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"
bolt=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\bolt.png"
uppercut=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\uppercut.png"
Peg_Top=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\peg_top.png"
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

# Continue Related Images
cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"
continueF = [cont1, cont2, cont3, cont4, cont5]

# # notifyF Related Images
# currencyERR =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_currency.png"
# connectionERR =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_server1.png"
# connectionERR2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\image_65.png"
# doesnt_exist =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\not_exist.png"
# no_activity =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_activity.png"
# no_voidenergy =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\no_voidEnergy.png"
# home_screen =r"C:\Users\nahid\OneDrive\backup\shadowfight3\notify\home_screen.png"
# notifyF = [currencyERR, connectionERR,connectionERR2,doesnt_exist,no_activity,no_voidenergy,home_screen]

# Others
#* space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
#* space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
SPACE =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space2.png"
Resume =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

# Fame Related Images
e_image      =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_tournament.png"
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
Tournament_step2=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\SELECT.png"
back_battlepass=r'C:\Users\nahid\OneDrive\backup\shadowfight3\back_battlepass.png'

#* Threads
fight_thread = None
fightLight_thread = None

fame_heavy_thread = None
fame_light_thread = None

event_light_thread = None
event_heavy_thread = None

raid_heavy_thread = None
raid_light_thread = None

loss_thread = None

def close_window(event=None):
    # Close the current window
    ROOT.destroy()
    # Start the specified script
    script_path = r"C:\ms1\SH3\sf3_AHK.py"
    subprocess.Popen([sys.executable, script_path])

#!  █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗    ███████╗████████╗██╗   ██╗██╗     ███████╗
#! ██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝    ██╔════╝╚══██╔══╝╚██╗ ██╔╝██║     ██╔════╝
#! ███████║   ██║      ██║   ███████║██║     █████╔╝     ███████╗   ██║    ╚████╔╝ ██║     █████╗
#! ██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗     ╚════██║   ██║     ╚██╔╝  ██║     ██╔══╝
#! ██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗    ███████║   ██║      ██║   ███████╗███████╗
#! ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝
# light attack1
# Global flag for stopping the threads
pause_other_items = False

Action_Light_Thread1 = None
stop_thread_action1 = False
image_found1 = False
action_timer1 = None

Action_Light_Thread2 = None
stop_thread_action2 = False
image_found2 = False
action_timer2 = None

def search_image_1():
    global image_found1
    while not stop_thread_action1:
        if any(find_image(image, confidence=actionF[image]) for image in actionF):
            image_found1 = True
            print("Image found in Light Attack 1, resetting action timer.")
        else:
            image_found1 = False
            print("Image not found in Light Attack 1.")
        time.sleep(0.05)  # Adjust as necessary

def perform_action_1(window):
    global pause_other_items1, action_timer1
    holding_keys = False
    while not stop_thread_action1:
        if image_found1:
            pause_other_items1 = True
            holding_keys = True
            action_timer1 = time.time()  # Reset 5-second timer
            while holding_keys and not stop_thread_action1:
                if time.time() - action_timer1 >= 5:
                    print("5 seconds of Light Attack 1 action completed.")
                    holding_keys = False
                    break
                # Perform the key presses
                key_down(window, 'd')
                press_key(window, 'j')
                press_key(window, 'j')
                key_up(window, 'd')
                time.sleep(0.1)
            key_up(window, 'd')
            pause_other_items1 = False
        else:
            time.sleep(0.05)

def actionF_L1(window):
    try:
        image_search_thread = threading.Thread(target=search_image_1)
        image_search_thread.start()
        action_thread = threading.Thread(target=perform_action_1, args=(window,))
        action_thread.start()
        image_search_thread.join()
        action_thread.join()
    except KeyboardInterrupt:
        print("ActionF_L1 thread stopped by user.")

def Action_Light_1():
    global stop_thread_action1
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    actionF_thread = threading.Thread(target=actionF_L1, args=(window,))
    actionF_thread.daemon = True
    actionF_thread.start()
    actionF_thread.join()

def action_adjust_1():
    global stop_thread_action1, Action_Light_Thread1, ACTION_1_PY
    if Action_Light_Thread1 and Action_Light_Thread1.is_alive():
        stop_thread_action1 = True
        Action_Light_Thread1.join()
        ACTION_1_PY.config(text="AL", bg="#607af0", fg="#9dff00")
    else:
        stop_thread_action1 = False
        Action_Light_Thread1 = threading.Thread(target=Action_Light_1)
        Action_Light_Thread1.daemon = True
        Action_Light_Thread1.start()
        ACTION_1_PY.config(text="Stop", bg="#1d2027", fg="#fc0000")

ACTION_1_PY = Button(ROOT, text="AL", bg="#607af0", fg="#9dff00", width=5, height=2, command=action_adjust_1, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_1_PY.pack(padx=(1, 1), pady=(1, 1))


# Light Attack 2 Functions (actionF_L2)

def search_image_2():
    global image_found2
    while not stop_thread_action2:
        if any(find_image(image, confidence=actionF[image]) for image in actionF):
            image_found2 = True
            print("Image found in Light Attack 2, resetting action timer.")
        else:
            image_found2 = False
            print("Image not found in Light Attack 2.")
        time.sleep(0.05)

def perform_action_2(window):
    global pause_other_items2, action_timer2
    while not stop_thread_action2:
        if image_found2:
            pause_other_items2 = True
            action_timer2 = time.time()
            print("Triggering F13 in AHK...")
            key_down(window, 'F13')
            time.sleep(5)  # Simulate the wait for 5 seconds
            key_up(window, 'F13')
            print("F13 action completed.")
            pause_other_items2 = False
        else:
            time.sleep(0.05)

def actionF_L2(window):
    try:
        image_search_thread = threading.Thread(target=search_image_2)
        image_search_thread.start()
        action_thread = threading.Thread(target=perform_action_2, args=(window,))
        action_thread.start()
        image_search_thread.join()
        action_thread.join()
    except KeyboardInterrupt:
        print("ActionF_L2 thread stopped by user.")

def Action_Light_2():
    global stop_thread_action2
    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    actionF_thread = threading.Thread(target=actionF_L2, args=(window,))
    actionF_thread.daemon = True
    actionF_thread.start()
    actionF_thread.join()

def action_adjust_2():
    global stop_thread_action2, Action_Light_Thread2, ACTION_2_AHK
    if Action_Light_Thread2 and Action_Light_Thread2.is_alive():
        stop_thread_action2 = True
        Action_Light_Thread2.join()
        ACTION_2_AHK.config(text="AL", bg="#5a9b5a", fg="#9dff00")
    else:
        stop_thread_action2 = False
        Action_Light_Thread2 = threading.Thread(target=Action_Light_2)
        Action_Light_Thread2.daemon = True
        Action_Light_Thread2.start()
        ACTION_2_AHK.config(text="Stop", bg="#1d2027", fg="#fc0000")

ACTION_2_AHK = Button(ROOT, text="AL", bg="#5a9b5a", fg="#9dff00", width=5, height=2, command=action_adjust_2, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_2_AHK.pack(padx=(1, 1), pady=(1, 1))



# heavy attack for fight
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
        ACTION_3.config(text="AH", bg="#6a6a64", fg="#9dff00")
    else:
        stop_thread_action3 = False
        fight_thread = threading.Thread(target=fight_Heavy)
        fight_thread.daemon = True
        fight_thread.start()
        ACTION_3.config(text="Stop", bg="#1d2027", fg="#fc0000")
ACTION_3 = Button(ROOT, text="AH", bg="#6a6a64", fg="#9dff00", width=5, height=2, command=fight_function, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
ACTION_3.pack(padx=(1,1), pady=(1,1))

# ███╗   ███╗ ██████╗ ██████╗ ███████╗
# ████╗ ████║██╔═══██╗██╔══██╗██╔════╝
# ██╔████╔██║██║   ██║██║  ██║█████╗
# ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝
# ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
# ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
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
            elif find_image(e_image): press_key(window, 'e')
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










# Event
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
            elif any(find_image(image) for image in continueF): press_keys_with_two_delays(window, 2, 'c', 2)

            elif find_image(Tournament_step1, confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
            elif find_image(Tournament_step2, confidence=0.8): press_keys_with_delays(window, '2', 1)

            elif find_image(back_battlepass, confidence=0.8): press_keys_with_delays(window, 'b', 1)

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


def restart(event=None):
    ROOT.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

Destroy_BT = Button(ROOT, text="RE", bg="#443e3e", fg="#fff", width=5, height=2, command=restart, font=("Jetbrainsmono nfp", 10, "bold"), relief="flat")
Destroy_BT.pack(padx=(1, 1), pady=(1, 1))

ROOT.mainloop()
