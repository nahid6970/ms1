import tkinter as tk
from PIL import Image, ImageTk, ImageGrab
import threading
import time
from screeninfo import get_monitors

def get_secondary_monitor_bbox():
    monitors = get_monitors()
    primary_monitor = monitors[0]
    for monitor in monitors:
        if monitor != primary_monitor:
            return (monitor.x, monitor.y, monitor.width, monitor.height)
    return None

def capture_secondary_monitor():
    bbox = get_secondary_monitor_bbox()
    if not bbox:
        print("Secondary monitor not found.")
        return

    while True:
        # Capture the entire virtual screen
        virtual_screen = ImageGrab.grab(all_screens=True)

        # Calculate the cropping box
        crop_box = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])

        # Crop the secondary monitor's area
        screenshot = virtual_screen.crop(crop_box)

        # Resize the screenshot to fit the display window
        resized_screenshot = screenshot.resize((int(screenshot.width // 5), int(screenshot.height // 5)))

        # Update the image on the Tkinter label
        img = ImageTk.PhotoImage(resized_screenshot)
        label.config(image=img)
        label.image = img

        # Update the window
        root.update_idletasks()
        root.update()

        # Capture every 100 milliseconds
        time.sleep(0.1)

# Create the Tkinter window
root = tk.Tk()
root.title("Secondary Monitor Viewer")

# Create a label to display the captured image
label = tk.Label(root)
label.pack()

# Start the screen capture in a separate thread
thread = threading.Thread(target=capture_secondary_monitor)
thread.daemon = True
thread.start()

# Start the Tkinter event loop
root.mainloop()
