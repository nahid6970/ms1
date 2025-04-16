import pyautogui
import chilimangoes

# Override pyautogui's screenshot with improved multi-monitor support
pyautogui.screenshot = chilimangoes.grab_screen
pyautogui.pyscreeze.screenshot = chilimangoes.grab_screen
pyautogui.size = lambda: chilimangoes.screen_size

import time

# Adjust path to your image
image_path = 'C:\\Users\\nahid\\Desktop\\image_117.png'

# Coordinates of second monitor (you said it's to the right, 1920x1080)
second_monitor_region = (1920, 0, 1920, 1080)

print("Looking for image on second monitor...")

while True:
    location = pyautogui.locateOnScreen(image_path, region=second_monitor_region, confidence=0.8)
    if location:
        print(f"Image found at {location}")
        pyautogui.click(pyautogui.center(location))
        break
    else:
        print("Not found yet...")
    time.sleep(1)
