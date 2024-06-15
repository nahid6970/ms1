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
action  = [action1,action2]


Valor2= r"C:\Users\nahid\OneDrive\backup\shadowfight3\valor\image_13.png"
Valor3= r"C:\Users\nahid\OneDrive\backup\shadowfight3\valor\image_14.png"
valor = [Valor2,Valor3]

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
    window_title ='LDPlayer'
    e_image      =r"C:\ms1\SH3\b_tournament.png"
    space_image  =r"C:\ms1\SH3\b_space.png"
    cont1        =r"C:\ms1\SH3\b_continue.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return

    try:
        while not stop_thread:
            focus_window(window_title)
            #if any(find_image(image) for image in action):
            if any(find_image(image) for image in valor):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(e_image):
                press_key(window, 'e')
            elif find_image(space_image, confidence=0.8):
                press_key(window, ' ')
            elif find_image(cont1, confidence=0.8):
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
    Raids          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\Raid_Home.png"
    level3         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\level3.png"
    participate    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\participate.png"
    toraid         =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\to_raid.png"
    fight          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\fightttttt.png"
    claimreward    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\claim.png"
    cont1          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\continue.png"
    cont2          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\raids\continue2.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            #if any(find_image(image) for image in action):
            if any(find_image(image) for image in valor):
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
            elif find_image(cont1, confidence=0.97): press_key(window, 'c')
            elif find_image(cont2, confidence=0.97): press_key(window, 'c')

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
    cont1           =r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\continue.png"
    cont2           =r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\continueeee.png"
    WeekendEvent    =r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\event.png"
    Tournament_step1=r"C:\Users\nahid\OneDrive\backup\shadowfight3\event\Tournament.png"
    Tournament_step2=r"C:\Users\nahid\OneDrive\backup\shadowfight3\WheelofHistory\entertourney2.png"
    Resume          =r"C:\Users\nahid\OneDrive\backup\shadowfight3\resume.png"

    window = focus_window(window_title)
    if not window:
        print(f"Window '{window_title}' not found.")
        return
    try:
        while not stop_thread:
            focus_window(window_title)
            #if any(find_image(image) for image in action):
            if any(find_image(image) for image in valor):
                    key_down(window, 'j')
                    key_down(window, 'l')
                    time.sleep(5)
                    key_up(window, 'l')
                    key_up(window, 'j')

            elif find_image(WeekendEvent, confidence=0.8): press_key(window, 'f')
            elif find_image(cont1, confidence=0.8) or find_image(cont2, confidence=0.8): press_key(window, 'c')
            elif find_image(Tournament_step1,confidence=0.8): press_keys_with_delays(window, 'u', 1, 'c', 1)
            elif find_image(Tournament_step2,confidence=0.8): press_keys_with_delays(window, 'y', 1)
            elif find_image(Resume, confidence=0.8): press_key(window, 'r')

            # for ad_image in ads_images:
            #     ad_location = find_image(ad_image, confidence=0.8)
            #     if ad_location:
            #         click(window, ad_location.left, ad_location.top)

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

"""
 ██████╗ ██████╗ ███╗   ███╗███╗   ███╗███████╗███╗   ██╗████████╗    ██╗     ██╗███╗   ██╗███████╗
██╔════╝██╔═══██╗████╗ ████║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝    ██║     ██║████╗  ██║██╔════╝
██║     ██║   ██║██╔████╔██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║       ██║     ██║██╔██╗ ██║█████╗
██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║       ██║     ██║██║╚██╗██║██╔══╝
╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║       ███████╗██║██║ ╚████║███████╗
 ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝       ╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
"""
script_path = r"C:\ms1\SH3\SH3V2.py"

Event_Action = 286
Event_Valor = 287

Fame_Action = 198
Fame_Valor = 199

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

def write_file(file_path, lines):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def toggle_comment(line_number):
    lines = read_file(script_path)
    line = lines[line_number - 1]
    stripped_line = line.lstrip()
    
    print(f"Toggling comment on line {line_number}: {line.strip()}")
    
    if stripped_line.startswith('#'):
        lines[line_number - 1] = line.replace('#', '', 1)  # Uncomment the line
        is_commented = False
    else:
        indent = len(line) - len(stripped_line)
        lines[line_number - 1] = ' ' * indent + '#' + stripped_line  # Comment the line
        is_commented = True
    
    write_file(script_path, lines)
    
    print(f"Updated line {line_number}: {lines[line_number - 1].strip()}")
    
    return is_commented

def update_button_color(button, is_commented):
    button.config(bg="gray" if is_commented else "yellow")

def toggle_event_action():
    is_commented = toggle_comment(Event_Action)
    update_button_color(Event_action_bt, is_commented)

def toggle_event_valor():
    is_commented = toggle_comment(Event_Valor)
    update_button_color(Event_valor_bt, is_commented)

def toggle_fame_action():
    is_commented = toggle_comment(Fame_Action)
    update_button_color(Fame_action_bt, is_commented)

def toggle_fame_valor():
    is_commented = toggle_comment(Fame_Valor)
    update_button_color(Fame_valor_bt, is_commented)



# def restart(event=None):
#     root.destroy()
#     subprocess.Popen([sys.executable] + sys.argv)

# def close_window(event=None):
#     root.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title("Function Selector")
    # root.overrideredirect(True)
    default_font = ("Jetbrainsmono nfp", 10)
    root.option_add("*Font", default_font)
    root.geometry("+715+400")

    # def check_window_topmost():
    #     if not root.attributes('-topmost'):
    #         root.attributes('-topmost', True)
    #     root.after(500, check_window_topmost)
    # check_window_topmost()

    Fame_bt   =Button(root,text="Fame"   ,command=Fame_Function , width=15,height=4,bg="#bda24a",fg="#000000", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
    Event_bt  =Button(root,text="Event"  ,command=event_function, width=15,height=4,bg="#5a0000",fg="#ffffff", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
    Raids_bt  =Button(root,text="Raids"  ,command=Raids_Function, width=15,height=4,bg="#006173",fg="#ffffff", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
    Stop_bt   =Button(root,text="Stop"   ,command=stop_functions, width=15,height=4,bg="#ff0e0e",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
    # Restart_bt=Button(root,text="Restart",command=restart       , width=15,height=4,bg="#0e93ff",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")
    # Exit_bt   =Button(root,text="Exit"   ,command=close_window  , width=15,height=4,bg="#080808",fg="#FFFFFF", font=("Jetbrainsmono nfp",12,"bold") ,relief="flat")

    Fame_bt.grid   (row=1,column=1, sticky="ew")
    Event_bt.grid  (row=1,column=2, sticky="ew")
    Raids_bt.grid  (row=1,column=3, sticky="ew")
    Stop_bt.grid   (row=2,column=1, sticky="ew", columnspan=3)
    # Restart_bt.grid(row=2,column=2, sticky="ew")
    # Exit_bt.grid   (row=2,column=3, sticky="ew")

    #? Event
    Event_Heading_bt = Button(root,text="Event"                 ,command=None)
    Event_action_bt = Button(root ,text=f"Action {Event_Action}",command=toggle_event_action)
    Event_valor_bt = Button(root  ,text=f"Valor {Event_Valor}"  ,command=toggle_event_valor)
    update_button_color(Event_action_bt, read_file(script_path)[Event_Action - 1].strip().startswith('#'))
    update_button_color(Event_valor_bt, read_file(script_path)[Event_Valor - 1].strip().startswith('#'))
    Event_Heading_bt.grid(row=3,column=1,sticky="ew")
    Event_action_bt.grid( row=3,column=2,sticky="ew")
    Event_valor_bt.grid(  row=3,column=3,sticky="ew")

    #? Fame
    Fame_Heading_bt = Button(root,text="Fame"                 ,command=None)
    Fame_action_bt = Button(root ,text=f"Action {Fame_Action}",command=toggle_fame_action)
    Fame_valor_bt = Button(root  ,text=f"Valor {Fame_Valor}"  ,command=toggle_fame_valor)
    update_button_color(Fame_action_bt, read_file(script_path)[Fame_Action - 1].strip().startswith('#'))
    update_button_color(Fame_valor_bt, read_file(script_path)[Fame_Valor - 1].strip().startswith('#'))
    Fame_Heading_bt.grid(row=4,column=1,sticky="ew")
    Fame_action_bt.grid( row=4,column=2,sticky="ew")
    Fame_valor_bt.grid(  row=4,column=3,sticky="ew")









    root.mainloop()