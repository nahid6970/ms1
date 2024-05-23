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
    action_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\fight.png"
    # action2_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\Sakura_fight.png"
    continue_image = r"C:\Users\nahid\OneDrive\backup\shadowfight3\SanguineForest\cont.png"
    # e_image = r""
    # space_image = r""

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
            
#* Hand
            # if find_image(action_image) or find_image(action2_image):
            if find_image(action_image):
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
            elif find_image(select_from):
                pyautogui.press('1')
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

                positionclick = find_image(advert1, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert2, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert3, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert4, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert5, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert6, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)
                positionclick = find_image(advert7, confidence=0.8)
                if positionclick:
                    pyautogui.click(positionclick)

            time.sleep(0.1)  # Adjust the delay as needed
    except KeyboardInterrupt:
        print("Script stopped by user.")

if __name__ == "__main__":
    main()
