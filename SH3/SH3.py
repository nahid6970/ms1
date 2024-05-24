import time
import pyautogui
import pygetwindow as gw
import random
import threading
from tkinter import Tk, Button


# Disable fail-safe to prevent interruptions
pyautogui.FAILSAFE = False

error_count = 0  # Initialize the error counter
stop_thread = False  # Flag to stop the thread


def find_image(image_path, confidence=0.7):
    """Find the location of the image on the screen."""
    global error_count
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            return location
    except Exception:
        error_count += 1
        print(f"{error_count} times image not found")
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
    button1.pack(pady=10, side="left")

    button2 = Button(root, text="SanguineForest", command=start_function2, bg="#c4f728", fg="#000000")
    button2.pack(pady=10, side="left")

    button3 = Button(root, text="Stop", command=stop_functions, bg="#ff0e0e", fg="#FFFFFF")
    button3.pack(pady=10,side="left")

    root.mainloop()
