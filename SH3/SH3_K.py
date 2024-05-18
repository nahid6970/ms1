import time
import pyautogui
import pygetwindow as gw
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
    action_image = r"C:\ms1\SH3\b_action.png"
    e_image = r"C:\ms1\SH3\b_tournament.png"
    space_image = r"C:\ms1\SH3\b_space.png"
    continue_image = r"C:\ms1\SH3\b_continue.png"

    print("Press 'q' to stop the script.")
    
    # Start the keyboard listener in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while True:
            # Focus on the LDPlayer window
            focus_window(window_title)
            if find_image(action_image):
                pyautogui.press('k')
            elif find_image(e_image):
                pyautogui.press('e')
            elif find_image(space_image, confidence=0.8):
                pyautogui.press(' ')
            elif find_image(continue_image, confidence=0.8):
                pyautogui.press('c')
            time.sleep(0.1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Script stopped by user.")

if __name__ == "__main__":
    main()
