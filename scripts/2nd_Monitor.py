import tkinter as tk
import threading
import time
import mss
from PIL import Image, ImageTk, ImageDraw, ImageFont
from screeninfo import get_monitors
import win32api
import keyboard

try:
    font = ImageFont.truetype("C:/Windows/Fonts/JetBrainsMonoNerdFont-Regular.ttf", 40) # Adjust path and size as needed
except IOError:
    font = ImageFont.load_default()
    print("JetBrainsMono NFP font not found, using default font.")

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
        root.geometry(f"+{x}+{y}")

def get_primary_monitor_bbox():
    monitors = get_monitors()
    primary_monitor = monitors[0]
    return primary_monitor.x, primary_monitor.y, primary_monitor.width, primary_monitor.height

def get_secondary_monitor_bbox():
    monitors = get_monitors()
    primary_monitor = monitors[0]
    for monitor in monitors:
        if monitor != primary_monitor:
            return monitor.x, monitor.y, monitor.width, monitor.height
    return None

def capture_loop(stop_event):
    with mss.mss() as sct:
        while not stop_event.is_set():
            bbox = get_secondary_monitor_bbox()
            if bbox:
                monitor = {
                    "top": bbox[1],
                    "left": bbox[0],
                    "width": bbox[2],
                    "height": bbox[3]
                }
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
                    cursor_color = (0, 255, 0)  # Green color for visibility
                    draw.line((cursor_x, cursor_y - cursor_size, cursor_x, cursor_y + cursor_size), fill=cursor_color, width=5)
                    draw.line((cursor_x - cursor_size, cursor_y, cursor_x + cursor_size, cursor_y), fill=cursor_color, width=5)

                # Resize the screenshot to fit the display window
                resized_screenshot = img.resize((int(img.width // 10), int(img.height // 10)))

                # Update the image on the Tkinter label
                img_tk = ImageTk.PhotoImage(resized_screenshot)
                label.config(image=img_tk, text="")
                label.image = img_tk

                # Update the window
                root.update_idletasks()
                root.update()

                # Capture every 100 milliseconds
                time.sleep(0.1)
            else:
                # No secondary monitor found, display a message
                img = Image.new('RGB', (192, 108), (0, 0, 0))
                draw = ImageDraw.Draw(img)
                draw.text((80, 30), "󰶐", font=font, fill=(255, 255, 255))
                
                img_tk = ImageTk.PhotoImage(img)
                label.config(image=img_tk, text="")
                label.image = img_tk
                
                root.update_idletasks()
                root.update()
                time.sleep(1)

def close_window():
    stop_event.set()  # Stop all threads before closing the window
    root.destroy()

# Create the Tkinter window
root = tk.Tk()
root.title("Secondary Monitor Viewer")

root.overrideredirect(True)

# Get primary monitor dimensions and set the position to bottom-left
primary_x, primary_y, primary_width, primary_height = get_primary_monitor_bbox()

# Calculate the bottom-left corner position
window_x = primary_x
window_y = primary_y + primary_height - 200  # Adjust the height based on window size

root.geometry(f"+{window_x}+{window_y}")

# Add bindings to make the window movable
root.bind("<ButtonPress-1>", start_drag)
root.bind("<ButtonRelease-1>", stop_drag)
root.bind("<B1-Motion>", do_drag)

root.attributes('-topmost', True)

# Create a label to display the captured image
label = tk.Label(root)
label.pack()

# Create an event to stop the threads when needed
stop_event = threading.Event()

# Start monitoring for the secondary monitor in a separate thread
capture_thread = threading.Thread(target=capture_loop, args=(stop_event,))
capture_thread.daemon = True
capture_thread.start()

root.mainloop()
