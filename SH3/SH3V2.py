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
        if location:
            return location
    except Exception:
        error_count += 1
        print(f"Error finding image occurred {error_count} times")
    return None

def focus_window(window_title):
    """Set focus to the window with the given title."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
        window.activate()
        return window
    return None
action_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight.png"
action2_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight2.png"

"""
████████  ██████  ██    ██ ██████  ███    ██  █████  ███    ███ ███████ ███    ██ ████████
   ██    ██    ██ ██    ██ ██   ██ ████   ██ ██   ██ ████  ████ ██      ████   ██    ██
   ██    ██    ██ ██    ██ ██████  ██ ██  ██ ███████ ██ ████ ██ █████   ██ ██  ██    ██
   ██    ██    ██ ██    ██ ██   ██ ██  ██ ██ ██   ██ ██  ██  ██ ██      ██  ██ ██    ██
   ██     ██████   ██████  ██   ██ ██   ████ ██   ██ ██      ██ ███████ ██   ████    ██
"""
def TournamentFame():
    window_title = 'LDPlayer'
    # action_image = r"C:\ms1\SH3\b_action.png"
    e_image = r"C:\ms1\SH3\b_tournament.png"
    space_image = r"C:\ms1\SH3\b_space.png"
    continue_image = r"C:\ms1\SH3\b_continue.png"
    ability_image = r"C:\Users\nahid\OneDrive\Desktop\b_ability.png"

    try:
        # while True:
        while not stop_thread:
            # Focus on the LDPlayer window
            focus_window(window_title)

#* Hand
            if find_image(action_image) or find_image(action2_image):
                # Randomly choose whether to hold or press 'k'
                if random.choice([True, False]):
                    pyautogui.keyDown('j')
                    pyautogui.keyDown('l')
                    time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
                    pyautogui.keyUp('j')
                    pyautogui.keyUp('l')
                else:
                    pyautogui.press('j')
#* Kick
            # if find_image(action_image):
            #     # Randomly choose whether to hold or press 'k'
            #     if random.choice([True, False]):
            #         pyautogui.keyDown('k')
            #         pyautogui.keyDown('l')
            #         time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
            #         pyautogui.keyUp('k')
            #         pyautogui.keyUp('l')
            #     else:
            #         pyautogui.press('k')
#* Hand and Kick Combo
            # if find_image(action_image):
            #     # Randomly choose between different combos
            #     combo_choice = random.choice(['hand', 'kick', 'hand_kick'])

            #     if combo_choice == 'hand':
            #         if random.choice([True, False]):
            #             pyautogui.keyDown('j')
            #             pyautogui.keyDown('l')
            #             time.sleep(random.uniform(0.1, 0.5))  # Hold 'j' and 'l' for a random duration
            #             pyautogui.keyUp('j')
            #             pyautogui.keyUp('l')
            #         else:
            #             pyautogui.press('j')

            #     elif combo_choice == 'kick':
            #         if random.choice([True, False]):
            #             pyautogui.keyDown('k')
            #             pyautogui.keyDown('l')
            #             time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' and 'l' for a random duration
            #             pyautogui.keyUp('k')
            #             pyautogui.keyUp('l')
            #         else:
            #             pyautogui.press('k')

            #     elif combo_choice == 'hand_kick':
            #         if random.choice([True, False]):
            #             pyautogui.keyDown('j')
            #             pyautogui.keyDown('k')
            #             time.sleep(random.uniform(0.1, 0.5))  # Hold 'j' and 'k' for a random duration
            #             pyautogui.keyUp('j')
            #             pyautogui.keyUp('k')
            #         else:
            #             pyautogui.press('j')
            #             pyautogui.press('k')

            elif find_image(e_image):
                pyautogui.press('e')
            elif find_image(space_image, confidence=0.8):
                pyautogui.press(' ')
            elif find_image(continue_image, confidence=0.8):
                pyautogui.press('c')
            time.sleep(0.1)  # Adjust the delay as needed
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
    # action_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight.png"
    # action2_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight2.png"
    continue_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\cont.png"

    Four_paths = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\EnterSanguineForest.png"
    fourth_tournament = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\EnterTournament.png"
    select_from = r"C:\Users\nahid\OneDrive\backup\shadowfight3\Four_Paths\select.png"

    advertise = r"C:\Users\nahid\OneDrive\backup\shadowfight3\video_click.png"
    advert1 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad1.png"
    advert2 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad2.png"
    advert3 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad3.png"
    advert4 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad4.png"
    advert5 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad5.png"
    advert6 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad6.png"
    advert7 = r"C:\Users\nahid\OneDrive\backup\shadowfight3\ads\ad7.png"

    try:
        # while True:
        while not stop_thread:
            # Focus on the LDPlayer window
            # if not focus_window(window_title):
            focus_window(window_title)
                # print(f"Window with title '{window_title}' not found. Retrying...")
                # time.sleep(1)
                # continue

#* Hand
            # if find_image(action_image):
            if find_image(action_image) or find_image(action2_image):
                # Randomly choose whether to hold or press 'k'
                if random.choice([True, False]):
                    pyautogui.keyDown('j')
                    pyautogui.keyDown('l')
                    time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
                    pyautogui.keyUp('j')
                    pyautogui.keyUp('l')
                else:
                    pyautogui.press('j')

#* Kick
            # if find_image(action_image):
            #     # Randomly choose whether to hold or press 'k'
            #     if random.choice([True, False]):
            #         pyautogui.keyDown('k')
            #         pyautogui.keyDown('l')
            #         time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
            #         pyautogui.keyUp('k')
            #         pyautogui.keyUp('l')
            #     else:
            #         pyautogui.press('k')

#* Hand and Kick Combo
            # if find_image(action_image):
            #     # Randomly choose between different combos
            #     combo_choice = random.choice(['hand', 'kick', 'hand_kick'])

            #     if combo_choice == 'hand':
            #         if random.choice([True, False]):
            #             pyautogui.keyDown('j')
            #             pyautogui.keyDown('l')
            #             time.sleep(random.uniform(0.1, 0.5))  # Hold 'j' and 'l' for a random duration
            #             pyautogui.keyUp('j')
            #             pyautogui.keyUp('l')
            #         else:
            #             pyautogui.press('j')

            #     elif combo_choice == 'kick':
            #         if random.choice([True, False]):
            #             pyautogui.keyDown('k')
            #             pyautogui.keyDown('l')
            #             time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' and 'l' for a random duration
            #             pyautogui.keyUp('k')
            #             pyautogui.keyUp('l')
            #         else:
            #             pyautogui.press('k')

            #     elif combo_choice == 'hand_kick':
            #         if random.choice([True, False]):
            #             pyautogui.keyDown('j')
            #             pyautogui.keyDown('k')
            #             time.sleep(random.uniform(0.1, 0.5))  # Hold 'j' and 'k' for a random duration
            #             pyautogui.keyUp('j')
            #             pyautogui.keyUp('k')
            #         else:
            #             pyautogui.press('j')
            #             pyautogui.press('k')



            elif find_image(continue_image, confidence=0.8):
                pyautogui.press('c')
            # elif find_image(select_from):
            #     pyautogui.press('1')
            elif find_image(Four_paths, confidence=0.8):
                pyautogui.press('f')
            elif find_image(fourth_tournament):
                pyautogui.press('n')
            else:
                # Click on position images
                positionclick = find_image(Four_paths, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)

                positionclick = find_image(advertise)
                if positionclick:
                    pyautogui.click(positionclick)

                positionclick = find_image(advert1, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert2, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert3, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert4, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert5, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert6, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert7, confidence=0.9)
                if positionclick:
                    pyautogui.click(positionclick)

            time.sleep(0.1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Script stopped by user.")


def start_function1():
    global stop_thread
    stop_thread = False
    threading.Thread(target=TournamentFame).start()

def start_function2():
    global stop_thread
    stop_thread = False
    threading.Thread(target=SanguineForest).start()

def stop_functions():
    global stop_thread
    stop_thread = True




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


if __name__ == "__main__":
    root = Tk()
    root.title("Function Selector")

    button1 = Button(root, text="TournamentFame", command=start_function1, bg="#01c1fc", fg="#000000")
    button2 = Button(root, text="SanguineForest", command=start_function2, bg="#c4f728", fg="#000000")
    button3 = Button(root, text="Stop", command=stop_functions, bg="#ff0e0e", fg="#FFFFFF")

    button1.grid(row=1, column=1, columnspan=1)
    button2.grid(row=1, column=2, columnspan=1)
    button3.grid(row=2, column=1, columnspan=2, sticky="ew")

    root.mainloop()
