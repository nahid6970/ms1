import pyautogui
import tkinter as tk
import win32gui
import time

def get_window_under_mouse():
    """Gets the window handle under the mouse cursor"""
    hwnd = win32gui.WindowFromPoint(pyautogui.position())  # Get window handle at mouse position
    return hwnd

def get_window_rect(hwnd):
    """Get the window's position and size"""
    rect = win32gui.GetWindowRect(hwnd)
    return rect  # Returns (left, top, right, bottom)

def show_mouse_position():
    while True:
        try:
            # Get the window handle under the mouse
            hwnd = get_window_under_mouse()

            # Get the window's position and size
            window_rect = get_window_rect(hwnd)
            window_x, window_y = window_rect[0], window_rect[1]

            # Get the current mouse position
            mouse_x, mouse_y = pyautogui.position()

            # Calculate relative position inside the window
            relative_x = mouse_x - window_x
            relative_y = mouse_y - window_y

            # Update label to show relative coordinates
            label.config(text=f"Mouse in Window: X: {relative_x}, Y: {relative_y}")
        except:
            label.config(text="Error getting window under mouse")

        # Update the Tkinter window and wait for a short time
        root.update()
        time.sleep(0.1)

# Create the tkinter window
root = tk.Tk()
root.title("Mouse Position Tracker")
root.geometry("400x100")

# Create a label to show the mouse coordinates
label = tk.Label(root, text="Hover over a window to see the coordinates", font=("Arial", 12))
label.pack(pady=20)

# Start tracking the mouse position
root.after(100, show_mouse_position)

# Run the tkinter event loop
root.mainloop()
