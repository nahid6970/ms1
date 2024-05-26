import tkinter as tk
import threading
import time
import mss
import mss.tools
from PIL import Image, ImageTk
from screeninfo import get_monitors

drag_data = {"x": 0, "y": 0}

def start_drag(event):
    drag_data["x"] = event.x
    drag_data["y"] = event.y

def stop_drag(event):
    drag_data["x"] = None
    drag_data["y"] = None

def do_drag(event):
    if drag_data["x"] is not None and drag_data["y"] is not None:
        x, y = (event.x - drag_data["x"] + root.winfo_x(), event.y - drag_data["y"] + root.winfo_y())
        root.geometry("+%s+%s" % (x, y))

def get_secondary_monitor_bbox():
    monitors = get_monitors()
    primary_monitor = monitors[0]
    for monitor in monitors:
        if monitor != primary_monitor:
            return monitor.x, monitor.y, monitor.width, monitor.height
    return None

def capture_secondary_monitor():
    bbox = get_secondary_monitor_bbox()
    if not bbox:
        print("Secondary monitor not found.")
        return

    with mss.mss() as sct:
        monitor = {
            "top": bbox[1],
            "left": bbox[0],
            "width": bbox[2],
            "height": bbox[3]
        }

        while True:
            sct_img = sct.grab(monitor)

            # Convert the image to PIL format
            img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)

            # Resize the screenshot to fit the display window
            resized_screenshot = img.resize((int(img.width // 3), int(img.height // 3)))

            # Update the image on the Tkinter label
            img_tk = ImageTk.PhotoImage(resized_screenshot)
            label.config(image=img_tk)
            label.image = img_tk

            # Update the window
            root.update_idletasks()
            root.update()

            # Capture every 100 milliseconds
            time.sleep(0.1)

# Create the Tkinter window
root = tk.Tk()
root.title("Secondary Monitor Viewer")

root.overrideredirect(True)
# root.geometry(f"+{75}+{1044}")

def check_window_topmost():
    if not root.attributes('-topmost'):
        root.attributes('-topmost', True)
    root.after(500, check_window_topmost)
# Call the function to check window topmost status periodically
check_window_topmost()

# Add bindings to make the window movable
root.bind("<ButtonPress-1>", start_drag)
root.bind("<ButtonRelease-1>", stop_drag)
root.bind("<B1-Motion>", do_drag)

# Create a label to display the captured image
label = tk.Label(root)
label.pack()

# Start the screen capture in a separate thread
thread = threading.Thread(target=capture_secondary_monitor)
thread.daemon = True
thread.start()

# Start the Tkinter event loop
root.mainloop()







# import tkinter as tk
# from PIL import Image, ImageTk, ImageGrab
# import threading
# import time
# from screeninfo import get_monitors

# def get_secondary_monitor_bbox():
#     monitors = get_monitors()
#     primary_monitor = monitors[0]
#     for monitor in monitors:
#         if monitor != primary_monitor:
#             return (monitor.x, monitor.y, monitor.width, monitor.height)
#     return None

# def capture_secondary_monitor():
#     bbox = get_secondary_monitor_bbox()
#     if not bbox:
#         print("Secondary monitor not found.")
#         return

#     while True:
#         # Capture the entire virtual screen
#         virtual_screen = ImageGrab.grab(all_screens=True)

#         # Calculate the cropping box
#         crop_box = (bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3])

#         # Crop the secondary monitor's area
#         screenshot = virtual_screen.crop(crop_box)

#         # Resize the screenshot to fit the display window
#         resized_screenshot = screenshot.resize((int(screenshot.width // 5), int(screenshot.height // 5)))

#         # Update the image on the Tkinter label
#         img = ImageTk.PhotoImage(resized_screenshot)
#         label.config(image=img)
#         label.image = img

#         # Update the window
#         root.update_idletasks()
#         root.update()

#         # Capture every 100 milliseconds
#         time.sleep(0.1)

# # Create the Tkinter window
# root = tk.Tk()
# root.title("Secondary Monitor Viewer")

# # Create a label to display the captured image
# label = tk.Label(root)
# label.pack()

# # Start the screen capture in a separate thread
# thread = threading.Thread(target=capture_secondary_monitor)
# thread.daemon = True
# thread.start()

# # Start the Tkinter event loop
# root.mainloop()
