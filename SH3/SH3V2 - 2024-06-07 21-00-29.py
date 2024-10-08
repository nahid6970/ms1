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

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

# Global variables
error_count = 0  # Initialize the error counter
stop_thread = False  # Flag to stop the thread
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

def find_image(image_path, confidence=0.7):
    """Find the location of the image on the screen."""
    global error_count
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        # location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
        if location:
            return location
    except Exception:
        error_count += 1
        print(f"{error_count} times not found")
    return None

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

# def press_keys_with_delay(window, key1, delay, key2):
#     """Press key1, wait for delay seconds, then press key2."""
#     press_key(window, key1)
#     time.sleep(delay)
#     press_key(window, key2)

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





action1 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight.png"
action2 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight2.png"

ads1 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad1.png"
ads2 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad2.png"
ads3 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad3.png"
ads4 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad4.png"
ads5 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad5.png"
ads6 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad6.png"
ads7 = r"C:\Users\nahid\OneDrive\Desktop\image_9.png"
ads_images = [ads1, ads2, ads3, ads4, ads5, ads6, ads7]

"""
███████  █████  ███    ███ ███████
██      ██   ██ ████  ████ ██
█████   ███████ ██ ████ ██ █████
██      ██   ██ ██  ██  ██ ██
██      ██   ██ ██      ██ ███████
"""

def TournamentFame():
    window_title = 'LDPlayer'
    e_image = r"C:\ms1\SH3\b_tournament.png"
    space_image = r"C:\ms1\SH3\b_space.png"
    continue_image = r"C:\ms1\SH3\b_continue.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return

    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(action1) or find_image(action2):
                if random.choice([True, False]):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(random.uniform(0.1, 0.5))
                    key_up(window, 'j')
                    key_up(window, 'l')
                else:
                    press_key(window, 'j')

            elif find_image(e_image):
                press_key(window, 'e')
            elif find_image(space_image, confidence=0.8):
                press_key(window, ' ')
            elif find_image(continue_image, confidence=0.8):
                press_key(window, 'c')
            time.sleep(0.1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Script stopped by user.")

"""
██████   █████  ██ ██████  ███████
██   ██ ██   ██ ██ ██   ██ ██
██████  ███████ ██ ██   ██ ███████
██   ██ ██   ██ ██ ██   ██      ██
██   ██ ██   ██ ██ ██████  ███████
"""
def Raids():
    window_title   ='LDPlayer'
    continue_image =r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\cont.png"
    Raids          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\Raid_Home.png"
    level3         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\level3.png"
    participate    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\participate.png"
    toraid         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\to_raid.png"
    fight          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\fightttttt.png"
    claimreward    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\claim.png"
    continuee      =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\continue.png"
    continuee2     =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\continue2.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            # if find_image(action1) or find_image(action2):
            #     if random.choice([True, False]):
            #         key_down(window, 'j')
            #         key_down(window, 'l')
            #         time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
            #         key_up(window, 'j')
            #         key_up(window, 'l')
            #     else:
            #         press_key(window, 'j')
            if find_image(action1) or find_image(action2):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            # elif find_image(continue_image, confidence=0.8):
            #     press_key(window, 'c')

            elif find_image(continue_image, confidence=0.8): press_key(window, 'c')

            # else:
            #     positionclick = find_image(Raids, confidence=0.8)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)

            elif find_image(Raids, confidence=0.8): press_key(window, 'z')

            #     positionclick = find_image(level3, confidence=0.85)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)

            elif find_image(level3, confidence=0.85): press_key(window, '3')

            #     positionclick = find_image(participate, confidence=.97)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)
            elif find_image(participate, confidence=0.97): press_key(window, 'c')

            #     positionclick = find_image(toraid, confidence=.97)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)
            elif find_image(toraid, confidence=0.97): press_key(window, ' ')

            #     positionclick = find_image(fight, confidence=.97)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)
            elif find_image(fight, confidence=0.97): press_key(window, 'c')

            #     positionclick = find_image(claimreward, confidence=.97)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)
            elif find_image(claimreward, confidence=0.97): press_key(window, 'c')

            #     positionclick = find_image(continuee, confidence=.97)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)
            elif find_image(continuee, confidence=0.97): press_key(window, 'c')

            #     positionclick = find_image(continuee2, confidence=.97)
            #     if positionclick:
            #         click(window, positionclick.left, positionclick.top)
            elif find_image(continuee2, confidence=0.97): press_key(window, 'c')

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")

"""
███████  █████  ███    ██  ██████  ██    ██ ██ ███    ██ ███████ ███████  ██████  ██████  ███████ ███████ ████████
██      ██   ██ ████   ██ ██       ██    ██ ██ ████   ██ ██      ██      ██    ██ ██   ██ ██      ██         ██
███████ ███████ ██ ██  ██ ██   ███ ██    ██ ██ ██ ██  ██ █████   █████   ██    ██ ██████  █████   ███████    ██
     ██ ██   ██ ██  ██ ██ ██    ██ ██    ██ ██ ██  ██ ██ ██      ██      ██    ██ ██   ██ ██           ██    ██
███████ ██   ██ ██   ████  ██████   ██████  ██ ██   ████ ███████ ██       ██████  ██   ██ ███████ ███████    ██
"""
def SanguineForest():
    window_title = 'LDPlayer'
    continue_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\continue.png"
    EnterSanguineForest = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\EnterSanguineForest.png"
    EnterTournament = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\EnterTournament.png"
    fight = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\fight.png"
    # advertise = r"C:\Users\nahid\OneDrive\backup\shadowfight3\video_click.png"




    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return

    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(action1) or find_image(action2):
                if random.choice([True, False]):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
                    key_up(window, 'j')
                    key_up(window, 'l')
                else:
                    press_key(window, 'j')

            elif find_image(EnterSanguineForest, confidence=0.8): press_key(window, 'f')
            elif find_image(EnterTournament): press_key(window, 'g')
            elif find_image(fight, confidence=0.8): press_key(window, 'c')
            elif find_image(continue_image, confidence=0.8): press_key(window, 'p')

            # else:
                # if find_image(EnterSanguineForest, confidence=0.8): click(window, find_image(EnterSanguineForest, confidence=0.8).left, find_image(EnterSanguineForest, confidence=0.8).top)
                # if find_image(fight, confidence=0.8): click(window, find_image(fight, confidence=0.8).left, find_image(fight, confidence=0.8).top)
            if find_image(ads1, confidence=0.8): click(window, find_image(ads1, confidence=0.8).left, find_image(ads1, confidence=0.8).top)
            if find_image(ads2, confidence=0.8): click(window, find_image(ads2, confidence=0.8).left, find_image(ads2, confidence=0.8).top)
            if find_image(ads3, confidence=0.8): click(window, find_image(ads3, confidence=0.8).left, find_image(ads3, confidence=0.8).top)
            if find_image(ads4, confidence=0.8): click(window, find_image(ads4, confidence=0.8).left, find_image(ads4, confidence=0.8).top)
            if find_image(ads5, confidence=0.8): click(window, find_image(ads5, confidence=0.8).left, find_image(ads5, confidence=0.8).top)
            if find_image(ads6, confidence=0.8): click(window, find_image(ads6, confidence=0.8).left, find_image(ads6, confidence=0.8).top)
            if find_image(ads7, confidence=0.8): click(window, find_image(ads7, confidence=0.8).left, find_image(ads7, confidence=0.8).top)


                # if positionclick := find_image(EnterSanguineForest, confidence=0.8):
                #     click(window, positionclick.left, positionclick.top)

                # if positionclick := find_image(fight, confidence=0.8):
                #     click(window, positionclick.left, positionclick.top)

                # positionclick = find_image(advertise)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)

                # positionclick = find_image(advert1, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
                # positionclick = find_image(advert2, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
                # positionclick = find_image(advert3, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
                # positionclick = find_image(advert4, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
                # positionclick = find_image(advert5, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
                # positionclick = find_image(advert6, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
                # positionclick = find_image(advert7, confidence=0.9)
                # if positionclick:
                #     click(window, positionclick.left, positionclick.top)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")

"""
██████   █████  ███    ██  ██████  ███████ ██████   ██████  ██    ██ ███████ ███████ ██   ██  ██████  ██     ██
██   ██ ██   ██ ████   ██ ██       ██      ██   ██ ██    ██ ██    ██ ██      ██      ██   ██ ██    ██ ██     ██
██   ██ ███████ ██ ██  ██ ██   ███ █████   ██████  ██    ██ ██    ██ ███████ ███████ ███████ ██    ██ ██  █  ██
██   ██ ██   ██ ██  ██ ██ ██    ██ ██      ██   ██ ██    ██ ██    ██      ██      ██ ██   ██ ██    ██ ██ ███ ██
██████  ██   ██ ██   ████  ██████  ███████ ██   ██  ██████   ██████  ███████ ███████ ██   ██  ██████   ███ ███
"""
def DangerousShow():
    window_title   ='LDPlayer'
    continue_image =r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\continue.png"
    DangerousShow  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\DangerousShow\DangerousShow.png"
    Tournament     =r"C:\Users\nahid\OneDrive\backup\shadowfight3\DangerousShow\Tournament.png"
    Resume         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"


    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return

    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(action1) or find_image(action2):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(DangerousShow, confidence=0.8): press_key(window, 'f')
            elif find_image(Tournament,confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
            elif find_image(continue_image, confidence=0.8): press_key(window, 'c')
            elif find_image(Resume, confidence=0.8): press_key(window, 'r')

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")

"""
███████╗██╗   ██╗███████╗███╗   ██╗████████╗
██╔════╝██║   ██║██╔════╝████╗  ██║╚══██╔══╝
█████╗  ██║   ██║█████╗  ██╔██╗ ██║   ██║
██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║
███████╗ ╚████╔╝ ███████╗██║ ╚████║   ██║
╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝
"""

def Start_Event():
    window_title         ='LDPlayer'
    continue_image       =r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\continue.png"
    continue_image2      =r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\continueeee.png"
    WeekendEvent         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\WheelofHistory.png"
    Tournament_step1     =r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\entertourney.png"
    Tournament_step2     =r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\entertourney2.png"
    Resume               =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(action1) or find_image(action2):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(WeekendEvent, confidence=0.8): press_key(window, 'f')
            elif find_image(continue_image, confidence=0.8) or find_image(continue_image2, confidence=0.8): press_key(window, 'c')
            elif find_image(Tournament_step1,confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
            elif find_image(Tournament_step2,confidence=0.8): press_keys_with_delays(window, 'y', 1)
            elif find_image(Resume, confidence=0.8): press_key(window, 'r')
            
            for ad_image in ads_images:
                ad_location = find_image(ad_image, confidence=0.8)
                if ad_location:
                    click(window, ad_location.left, ad_location.top)

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")


def Fame_Function():
    global stop_thread
    stop_thread = False
    t = threading.Thread(target=TournamentFame)
    t.daemon = True
    t.start()

def Raids_Function():
    global stop_thread
    stop_thread = False
    t = threading.Thread(target=Raids)
    t.daemon = True
    t.start()

def event_function():
    global stop_thread
    stop_thread = False
    t = threading.Thread(target=Start_Event)
    t.daemon = True
    t.start()

def stop_functions():
    global stop_thread
    stop_thread = True

def restart(event=None):
    root.destroy()
    subprocess.Popen([sys.executable] + sys.argv)

def close_window(event=None):
    root.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title("Function Selector")
    root.overrideredirect(True)
    default_font = ("Jetbrainsmono nfp", 10)
    root.option_add("*Font", default_font)
    root.geometry(f"+{75}+{1044}")

    def check_window_topmost():
        if not root.attributes('-topmost'):
            root.attributes('-topmost', True)
        root.after(500, check_window_topmost)
    check_window_topmost()

    Fame_bt = Button(root, text="Fame", command=Fame_Function, bg="#bda24a", fg="#000000")
    Fame_bt.pack(side="left")
    Event_bt = Button(root, text="Event", command=event_function, bg="#5a0000", fg="#ffffff")
    Event_bt.pack(side="left")
    Raids_bt = Button(root, text="Raids", command=Raids_Function, bg="#006173", fg="#ffffff")
    Raids_bt.pack(side="left")
    Stop_bt = Button(root, text="Stop", command=stop_functions, bg="#ff0e0e", fg="#FFFFFF")
    Stop_bt.pack(side="left")
    Restart_bt = Button(root, text="Restart", command=restart, bg="#0e93ff", fg="#FFFFFF")
    Restart_bt.pack(side="left")
    Exit_bt = Button(root, text="Exit", command=close_window, bg="#080808", fg="#FFFFFF")
    Exit_bt.pack(side="left")

    root.mainloop()


# if __name__ == "__main__":
#     print("Press '1' for TournamentFame")
#     print("Press '2' for SanguineForest")

#     choice = input().strip()

#     if choice == '1':
#         TournamentFame()
#     elif choice == '2':
#         SanguineForest()
#     else:
#         print("Invalid choice. Exiting.")
