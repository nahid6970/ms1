import tkinter as tk
import threading
import time
import mss
from PIL import Image, ImageTk, ImageDraw
from screeninfo import get_monitors
import win32api

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

            # Get cursor position
            cursor_x, cursor_y = win32api.GetCursorPos()

            # Check if the cursor is on the secondary monitor
            if bbox[0] <= cursor_x < bbox[0] + bbox[2] and bbox[1] <= cursor_y < bbox[1] + bbox[3]:
                cursor_x -= bbox[0]
                cursor_y -= bbox[1]

                # Draw the cursor on the image
                draw = ImageDraw.Draw(img)
                cursor_size = 10  # Size of the cursor to draw
                cursor_color = (0, 255, 0)  # Red color for visibility
                draw.line((cursor_x, cursor_y - cursor_size, cursor_x, cursor_y + cursor_size), fill=cursor_color, width=5)
                draw.line((cursor_x - cursor_size, cursor_y, cursor_x + cursor_size, cursor_y), fill=cursor_color, width=5)

            # Resize the screenshot to fit the display window
            resized_screenshot = img.resize((int(img.width // 4), int(img.height // 4)))

            # Update the image on the Tkinter label
            img_tk = ImageTk.PhotoImage(resized_screenshot)
            label.config(image=img_tk)
            label.image = img_tk

            # Update the window
            root.update_idletasks()
            root.update()

            # Capture every 100 milliseconds
            time.sleep(0.1)

def close_window():
    root.destroy()

# Create the Tkinter window
root = tk.Tk()
root.title("Secondary Monitor Viewer")

root.overrideredirect(True)
# root.geometry(f"+{75}+{1044}")

# Add bindings to make the window movable
root.bind("<ButtonPress-1>", start_drag)
root.bind("<ButtonRelease-1>", stop_drag)
root.bind("<B1-Motion>", do_drag)

root.attributes('-topmost', True)

# Create a label to display the captured image
label = tk.Label(root)
label.pack()

# Create a close button
close_button = tk.Button(root, text="X", command=close_window)
close_button.config(font=("jetbrainsmono nfp", 8), bg="red", fg="white")
close_button.place(relx=1, x=-2, y=2, anchor="ne")

# Start the screen capture in a separate thread
thread = threading.Thread(target=capture_secondary_monitor)
thread.daemon = True
thread.start()

# Start the Tkinter event loop
root.mainloop()












# import tkinter as tk
# import threading
# import time
# import mss
# from PIL import Image, ImageTk, ImageDraw
# from screeninfo import get_monitors
# import win32api
# import win32gui

# drag_data = {"x": 0, "y": 0}

# def start_drag(event):
#     drag_data["x"] = event.x
#     drag_data["y"] = event.y

# def stop_drag(event):
#     drag_data["x"] = None
#     drag_data["y"] = None

# def do_drag(event):
#     if drag_data["x"] is not None and drag_data["y"] is not None:
#         x, y = (event.x - drag_data["x"] + root.winfo_x(), event.y - drag_data["y"] + root.winfo_y())
#         root.geometry("+%s+%s" % (x, y))

# def get_secondary_monitor_bbox():
#     monitors = get_monitors()
#     primary_monitor = monitors[0]
#     for monitor in monitors:
#         if monitor != primary_monitor:
#             return monitor.x, monitor.y, monitor.width, monitor.height
#     return None

# def capture_secondary_monitor():
#     bbox = get_secondary_monitor_bbox()
#     if not bbox:
#         print("Secondary monitor not found.")
#         return

#     with mss.mss() as sct:
#         monitor = {
#             "top": bbox[1],
#             "left": bbox[0],
#             "width": bbox[2],
#             "height": bbox[3]
#         }

#         while True:
#             start_time = time.time()
#             sct_img = sct.grab(monitor)

#             # Convert the image to PIL format
#             img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)

#             # Get cursor position
#             cursor_x, cursor_y = win32api.GetCursorPos()

#             # Check if the cursor is on the secondary monitor
#             if bbox[0] <= cursor_x < bbox[0] + bbox[2] and bbox[1] <= cursor_y < bbox[1] + bbox[3]:
#                 cursor_x -= bbox[0]
#                 cursor_y -= bbox[1]

#                 # Draw the cursor on the image
#                 draw = ImageDraw.Draw(img)
#                 cursor_size = 10  # Size of the cursor to draw
#                 cursor_color = (0, 255, 0)  # Red color for visibility
#                 draw.line((cursor_x, cursor_y - cursor_size, cursor_x, cursor_y + cursor_size), fill=cursor_color, width=5)
#                 draw.line((cursor_x - cursor_size, cursor_y, cursor_x + cursor_size, cursor_y), fill=cursor_color, width=5)

#             # Resize the screenshot to fit the display window
#             resized_screenshot = img.resize((int(img.width // 3.5), int(img.height // 3.5)))

#             # Update the image on the Tkinter label
#             img_tk = ImageTk.PhotoImage(resized_screenshot)
#             label.config(image=img_tk)
#             label.image = img_tk

#             # Update the window
#             root.update_idletasks()
#             root.update()

#             # Calculate sleep time to achieve a real-time update rate
#             elapsed_time = time.time() - start_time
#             sleep_time = max(0, 0.05 - elapsed_time)  # Adjust 0.05 for desired update rate (in seconds)
#             time.sleep(sleep_time)

# # Create the Tkinter window
# root = tk.Tk()
# root.title("Secondary Monitor Viewer")

# root.overrideredirect(True)
# # root.geometry(f"+{75}+{1044}")

# # Add bindings to make the window movable
# root.bind("<ButtonPress-1>", start_drag)
# root.bind("<ButtonRelease-1>", stop_drag)
# root.bind("<B1-Motion>", do_drag)

# root.attributes('-topmost', True)

# # Create a label to display the captured image
# label = tk.Label(root)
# label.pack()

# # Start the screen capture in a separate thread
# thread = threading.Thread(target=capture_secondary_monitor)
# thread.daemon = True
# thread.start()

# # Start the Tkinter event loop
# root.mainloop()
















# import tkinter as tk
# import threading
# import time
# import mss
# import mss.tools
# from PIL import Image, ImageTk
# from screeninfo import get_monitors

# drag_data = {"x": 0, "y": 0}

# def start_drag(event):
#     drag_data["x"] = event.x
#     drag_data["y"] = event.y

# def stop_drag(event):
#     drag_data["x"] = None
#     drag_data["y"] = None

# def do_drag(event):
#     if drag_data["x"] is not None and drag_data["y"] is not None:
#         x, y = (event.x - drag_data["x"] + root.winfo_x(), event.y - drag_data["y"] + root.winfo_y())
#         root.geometry("+%s+%s" % (x, y))

# def get_secondary_monitor_bbox():
#     monitors = get_monitors()
#     primary_monitor = monitors[0]
#     for monitor in monitors:
#         if monitor != primary_monitor:
#             return monitor.x, monitor.y, monitor.width, monitor.height
#     return None

# def capture_secondary_monitor():
#     bbox = get_secondary_monitor_bbox()
#     if not bbox:
#         print("Secondary monitor not found.")
#         return

#     with mss.mss() as sct:
#         monitor = {
#             "top": bbox[1],
#             "left": bbox[0],
#             "width": bbox[2],
#             "height": bbox[3]
#         }

#         while True:
#             sct_img = sct.grab(monitor)

#             # Convert the image to PIL format
#             img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)

#             # Resize the screenshot to fit the display window
#             resized_screenshot = img.resize((int(img.width // 3.5), int(img.height // 3.5)))

#             # Update the image on the Tkinter label
#             img_tk = ImageTk.PhotoImage(resized_screenshot)
#             label.config(image=img_tk)
#             label.image = img_tk

#             # Update the window
#             root.update_idletasks()
#             root.update()

#             # Capture every 100 milliseconds
#             time.sleep(0.1)

# # Create the Tkinter window
# root = tk.Tk()
# root.title("Secondary Monitor Viewer")
# root.overrideredirect(True)
# # root.geometry(f"+{75}+{1044}")

# # Add bindings to make the window movable
# root.bind("<ButtonPress-1>", start_drag)
# root.bind("<ButtonRelease-1>", stop_drag)
# root.bind("<B1-Motion>", do_drag)

# root.attributes('-topmost', True)


# # Create a label to display the captured image
# label = tk.Label(root)
# label.pack()

# # Start the screen capture in a separate thread
# thread = threading.Thread(target=capture_secondary_monitor)
# thread.daemon = True
# thread.start()

# # Start the Tkinter event loop
# root.mainloop()







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
