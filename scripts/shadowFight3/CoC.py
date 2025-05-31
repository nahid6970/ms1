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


# #* Threads
# fight_thread = None
# fame_light_thread = None
# event_light_thread = None
# raid_light_thread = None
# loss_thread = None

def close_window(event=None):
    # Close the current window
    ROOT.destroy()
    # Start the specified script
    script_path = r"C:\ms1\SH3\sf3_AHK.py"
    subprocess.Popen([sys.executable, script_path])


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


#* Continue Related Images
cont1 =r"C:\msBackups\shadowfight3\continue\cont1.png"
cont3 =r"C:\msBackups\shadowfight3\continue\cont3.png"
cont4 =r"C:\msBackups\shadowfight3\continue\cont4.png"

continueF = [cont1, cont3, cont4]
contF_Region = (1380, 792, 1738, 966)

#* Others
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

# Click_Ads=r"C:\msBackups\shadowfight3\ads\Click_ADS.png"
default_ads=r"C:\msBackups\shadowfight3\event\inside_ads.png"


ROOT.update_idletasks()
width = ROOT.winfo_width()
height = ROOT.winfo_height()

# x = ROOT.winfo_screenwidth() - width
# y = (ROOT.winfo_screenheight() // 2) - (height // 2)

x = (ROOT.winfo_screenwidth() // 2) - (width // 2)
y = 0

ROOT.geometry(f'{width}x{height}+{x}+{y}')
ROOT.mainloop()
