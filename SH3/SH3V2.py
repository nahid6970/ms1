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
        #* location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        location = pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True)
        if location:
            image_name = os.path.basename(image_path)
            print(f"Found image: {image_name}")
            return location
    except Exception as e:
        error_count += 1
        print(f"{error_count} times not found. Error: {e}")
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


void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"
#* actionF = [void_compass, eruption, thud, collector]
actionF = {
    void_compass: 0.7,
    eruption: 0.85,
    thud: 0.7,
    collector: 0.7
}


cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"
continueF = [cont1, cont2, cont3, cont4, cont5]

"""
███████╗██╗ ██████╗ ██╗  ██╗████████╗
██╔════╝██║██╔════╝ ██║  ██║╚══██╔══╝
█████╗  ██║██║  ███╗███████║   ██║
██╔══╝  ██║██║   ██║██╔══██║   ██║
██║     ██║╚██████╔╝██║  ██║   ██║
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝
"""

def Fight():
    window_title ='LDPlayer'
    space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"

    void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
    eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
    thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
    collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"

    cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
    cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
    cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
    cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
    cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return

    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(void_compass) or find_image(eruption) or find_image(thud) or find_image(collector): 
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')
            elif find_image(space_image, confidence=0.8): press_key(window, ' ')
            elif find_image(cont1) or find_image(cont2) or find_image(cont3) or find_image(cont4) or find_image(cont5): press_key(window, 'c')
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")
"""
███████  █████  ███    ███ ███████
██      ██   ██ ████  ████ ██
█████   ███████ ██ ████ ██ █████
██      ██   ██ ██  ██  ██ ██
██      ██   ██ ██      ██ ███████
"""
def TournamentFame():
    window_title ='LDPlayer'

    e_image      =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_tournament.png"
    space_image  =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space.png"
    space_image2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\b_space2.png"

    StartFame    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_19.png"
    WorldIcon    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_20.png"
    GoBack       =r"C:\Users\nahid\OneDrive\backup\shadowfight3\fame\image_21.png"
    Resume =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return

    try:
        while not stop_thread:
            focus_window(window_title)
            #* if any(find_image(image) for image in actionF):
            if any(find_image(image, confidence=actionF[image]) for image in actionF):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(Resume, confidence=0.8): press_key(window, 'r')
            elif find_image(space_image, confidence=0.8) or find_image(space_image2, confidence=0.8): press_key(window, ' ')
            elif find_image(StartFame): press_key(window, 'p')
            elif find_image(WorldIcon, confidence=0.8): press_key(window, 'o')
            elif find_image(e_image): press_key(window, 'e')
            elif find_image(GoBack, confidence=0.8): press_key(window, 'b')
            elif any(find_image(image) for image in continueF): press_key(window, 'c')

            time.sleep(0.1)
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

    void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
    eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
    thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
    collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"

    Raids          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\Raid_Home.png"
    level3         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\level3.png"
    participate    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\participate.png"
    toraid         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\to_raid.png"
    fight          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\fightttttt.png"
    claimreward    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\claim.png"

    cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
    cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
    cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
    cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
    cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"

    Resume =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(void_compass) or find_image(eruption) or find_image(thud) or find_image(collector): 
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(Raids, confidence=0.8): press_key(window, 'z')
            elif find_image(level3, confidence=0.85): press_key(window, '3')
            elif find_image(participate, confidence=0.97): press_key(window, 'c')
            elif find_image(toraid, confidence=0.97): press_key(window, ' ')
            elif find_image(fight, confidence=0.97): press_key(window, 'c')
            elif find_image(claimreward, confidence=0.97): press_key(window, 'c')
            elif find_image(cont1) or find_image(cont2) or find_image(cont3) or find_image(cont4) or find_image(cont5): press_key(window, 'c')

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
    window_title    ='LDPlayer'

    void_compass=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\void_compass.png"
    eruption=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\eruption.png"
    thud=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\thud.png"
    collector=r"C:\Users\nahid\OneDrive\backup\shadowfight3\action\collector.png"

    WeekendEvent    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\event.png"
    Tournament_step1=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\Tournament.png"
    # Tournament_step2=r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\entertourney2.png"

    cont1 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont1.png"
    cont2 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont2.png"
    cont3 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont3.png"
    cont4 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont4.png"
    cont5 =r"C:\Users\nahid\OneDrive\backup\shadowfight3\continue\cont5.png"

    Resume =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            if find_image(void_compass) or find_image(eruption) or find_image(thud) or find_image(collector): 
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(WeekendEvent, confidence=0.8): press_key(window, 'f')
            # elif find_image(cont1, confidence=0.8) or find_image(cont2, confidence=0.8): press_key(window, 'c')
            elif find_image(cont1) or find_image(cont2) or find_image(cont3) or find_image(cont4) or find_image(cont5): press_key(window, 'c')
            elif find_image(Tournament_step1,confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
            #! elif find_image(Tournament_step2,confidence=0.8): press_keys_with_delays(window, 'y', 1)
            elif find_image(Resume, confidence=0.8): press_key(window, 'r')

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Script stopped by user.")

def Fight_Function():
    global stop_thread
    stop_thread = False
    t = threading.Thread(target=Fight)
    t.daemon = True
    t.start()

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


x = screen_width - 40
y = screen_height//2 - 190//2
ROOT.geometry(f"35x190+{x}+{y}")

button_frame = tk.Frame(ROOT, bg="#1d2027", width=1, height=0)
button_frame.pack(side="top", padx=1, pady=1, fill="both")

F_bt    =Button(ROOT,text="\udb82\udf65",bg="#1d2027",fg="#9dff00",width=0,height=0,command=Fight_Function,font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
Fame_bt =Button(ROOT,text="F"           ,bg="#1d2027",fg="#ffffff",width=0,height=0,command=Fame_Function ,font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
Event_bt=Button(ROOT,text="E"           ,bg="#1d2027",fg="#ffffff",width=0,height=0,command=event_function,font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
Raids_bt=Button(ROOT,text="R"           ,bg="#1d2027",fg="#52a3ff",width=0,height=0,command=Raids_Function,font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
Stop_bt =Button(ROOT,text="\uf04d"      ,bg="#1d2027",fg="#fc0000",width=0,height=0,command=stop_functions,font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")

F_bt.pack      (side="top")
Fame_bt.pack   (side="top")
Event_bt.pack  (side="top")
Raids_bt.pack  (side="top")
Stop_bt.pack   (side="top")

ROOT.mainloop()










# Restart_bt=Button(ROOT,text="Restart",command=restart       , width=15,height=4,bg="#1d2027",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
# Exit_bt   =Button(ROOT,text="Exit"   ,command=close_window  , width=15,height=4,bg="#1d2027",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
