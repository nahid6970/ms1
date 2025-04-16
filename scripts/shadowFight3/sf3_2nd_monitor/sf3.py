# main.py

import pyautogui
import time
import chilimangoes  # Import chilimangoes module to override screenshot method
from PIL import Image

# Override pyautogui's screenshot method with the custom multi-monitor version
pyautogui.screenshot = chilimangoes.grab_screen
pyautogui.pyscreeze.screenshot = chilimangoes.grab_screen
pyautogui.size = lambda: chilimangoes.screen_size

# Image path to look for
image_path = 'C:\\Users\\nahid\\Desktop\\image_117.png'

# Region of the second monitor (1920x1080 resolution)
primary_monitor_region = (0, 0, 1920, 1080)  # Primary monitor region
second_monitor_region = (1920, 0, 1920, 1080)

print("Looking for image on second monitor...")

while True:
    # Locate image on second monitor
    location = pyautogui.locateOnScreen(image_path, region=second_monitor_region, confidence=0.8)
    if location:
        print(f"Image found at {location}")
        pyautogui.click(pyautogui.center(location))  # Click on the found image
        break
    else:
        print("Not found yet...")
    time.sleep(1)  # Wait 1 second before retrying
