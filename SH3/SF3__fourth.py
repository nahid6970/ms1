import time
import pyautogui
import pygetwindow as gw
import random
from pynput import keyboard

# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

def find_image(image_path, confidence=0.7):
    """Find the location of the image on the screen."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            return location
    except Exception as e:
        print(f"Error finding image: {e}")
    return None

def focus_window(window_title):
    """Set focus to the window with the given title."""
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        window = windows[0]
        window.activate()
        return window
    return None

def on_press(key):
    """Handle key press event."""
    try:
        if key.char == 'q':
            return False  # Stop listener
    except AttributeError:
        pass
    return True

def main():
    window_title = 'LDPlayer'
    action_image = r"C:\Users\nahid\OneDrive\Desktop\accc.png"
    e_image = r"C:\ms1\SH3\b_tournament.png"
    space_image = r"C:\ms1\SH3\b_space.png"
    continue_image = r"C:\Users\nahid\OneDrive\Desktop\cont.png"
    select_img = r"C:\Users\nahid\OneDrive\Desktop\select.png"
    advertise = r"C:\Users\nahid\OneDrive\Desktop\video_click.png"
    home_img = r"C:\Users\nahid\OneDrive\Desktop\home.png"
    fourth_tiurnament = r"C:\Users\nahid\OneDrive\Desktop\fourth_tiurnament.png"
    advert1 = r"C:\Users\nahid\OneDrive\Desktop\adddddddddddddd.png"
    advert2 = r"C:\Users\nahid\OneDrive\Desktop\advert_6.png"
    advert3 = r"C:\Users\nahid\OneDrive\Desktop\adv_7.png"
    advert8 = r"C:\Users\nahid\OneDrive\Desktop\ad8.png"
    advert9 = r"C:\Users\nahid\OneDrive\Desktop\ad9.png"

    print("Press 'q' to stop the script.")
    
    # Start the keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while True:
            # Focus on the LDPlayer window
            if not focus_window(window_title):
                print(f"Window with title '{window_title}' not found. Retrying...")
                time.sleep(1)
                continue
            
            # Check for each image and perform the corresponding action
            # if find_image(action_image, confidence=0.8):
            #     # Randomly choose whether to hold or press 'k' and 'j'
            #     if random.choice([True, False]):
            #         pyautogui.keyDown('k')
            #         pyautogui.keyDown('j')
            #         time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' and 'j' for a random duration
            #         pyautogui.keyUp('k')
            #         pyautogui.keyUp('j')
            #     else:
            #         pyautogui.press('k')
            #         pyautogui.press('j')
            if find_image(action_image,confidence=0.8):
                # Randomly choose whether to hold or press 'k'
                if random.choice([True, False]):
                    pyautogui.keyDown('k')
                    pyautogui.keyDown('l')
                    time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
                    pyautogui.keyUp('k')
                    pyautogui.keyUp('l')
                else:
                    pyautogui.press('k')
            elif find_image(e_image):
                pyautogui.press('e')
            elif find_image(space_image, confidence=0.8):
                pyautogui.press(' ')
            elif find_image(continue_image, confidence=0.8):
                pyautogui.press('c')
            elif find_image(select_img):
                pyautogui.press('1')
            elif find_image(home_img):
                pyautogui.press('f')
            elif find_image(fourth_tiurnament):
                pyautogui.press('n')
            elif find_image(advertise):
                pyautogui.press('v')
            else:
                # Click on advertisement images
                advert_location = find_image(advert1, confidence=0.8)
                if advert_location:
                    pyautogui.click(advert_location)
                advert_location = find_image(advert2, confidence=0.8)
                if advert_location:
                    pyautogui.click(advert_location)
                advert_location = find_image(advert3, confidence=0.8)
                if advert_location:
                    pyautogui.click(advert_location)
                advert_location = find_image(advert8, confidence=0.8)
                if advert_location:
                    pyautogui.click(advert_location)
                advert_location = find_image(advert9, confidence=0.8)
                if advert_location:
                    pyautogui.click(advert_location)

            time.sleep(0.1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Script stopped by user.")

if __name__ == "__main__":
    main()
