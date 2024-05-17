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
            return True
    except Exception as e:
        print(f"Error finding image: {e}")
    return False

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
    k_image_path = r"C:\Users\nahid\OneDrive\Desktop\k.png"
    e_image_path = r"C:\Users\nahid\OneDrive\Desktop\Screenshot 2024-05-17 224823.png"
    space_image_path = r"C:\Users\nahid\OneDrive\Desktop\space.png"
    continue_image_path = r"C:\Users\nahid\OneDrive\Desktop\continue.png"

    print("Press 'q' to stop the script.")
    
    # Start the keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while True:
            # Focus on the LDPlayer window
            focus_window(window_title)
            if find_image(k_image_path):
                # Randomly choose between clicking or holding down 'k' twice
                if random.choice([True, False]):
                    pyautogui.keyDown('k')
                    time.sleep(random.uniform(0.1, 0.5))  # Hold 'k' for a random duration
                    pyautogui.keyUp('k')
                else:
                    pyautogui.press('k', presses=2, interval=random.uniform(0.1, 0.5))
            if find_image(k_image_path):
                # Randomly choose between clicking or holding down 'j' twice
                if random.choice([True, False]):
                    pyautogui.keyDown('j')
                    time.sleep(random.uniform(0.1, 0.5))  # Hold 'j' for a random duration
                    pyautogui.keyUp('j')
                else:
                    pyautogui.press('j', presses=2, interval=random.uniform(0.1, 0.5))
            elif find_image(e_image_path):
                pyautogui.press('e')
            elif find_image(space_image_path, confidence=0.8):
                pyautogui.press(' ')
            elif find_image(continue_image_path, confidence=0.8):
                pyautogui.press('c')
            time.sleep(0.1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Script stopped by user.")

if __name__ == "__main__":
    main()
