# XY_App_CrossHair.py
# This script creates a crosshair overlay that is constrained to the currently focused application window.
# It displays coordinates relative to the active window and allows copying them.
#
# Dependencies:
# - pynput: for mouse control and listening
# - keyboard: for global hotkeys
# - pyperclip: for clipboard functionality
# - pywin32: for interacting with the Windows API to get window information
#   (install with: pip install pywin32)

import tkinter as tk
from pynput import mouse
import keyboard
import pyperclip
import threading
import ctypes
import win32gui
import time

class AppCrosshairOverlay:
    def __init__(self):
        self.vertical_line = None
        self.horizontal_line = None
        self.coord_label = None
        self.running = True
        self.show_coordinates = True

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.is_dragging = False

        # Hide Python console window
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # Start the real-time update thread
        self.update_thread = threading.Thread(target=self.update_crosshair)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Start the mouse listener thread
        self.mouse_listener_thread = threading.Thread(target=self.start_mouse_listener)
        self.mouse_listener_thread.daemon = True
        self.mouse_listener_thread.start()

        # Set up global hotkeys
        keyboard.add_hotkey("ctrl+c", self.copy_coordinates)
        keyboard.add_hotkey("esc", self.exit_script)
        keyboard.add_hotkey("CAPSLOCK", self.toggle_coordinates)

    def start_mouse_listener(self):
        """Starts the pynput mouse listener."""
        with mouse.Listener(on_click=self.on_click) as listener:
            listener.join()

    def on_click(self, x, y, button, pressed):
        """Callback for mouse click events."""
        if button == mouse.Button.left:
            if pressed:
                self.start_x, self.start_y = x, y
                self.is_dragging = True
            else:
                self.end_x, self.end_y = x, y
                self.is_dragging = False
                self.copy_coordinates()
                self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None

    def update_crosshair(self):
        """Continuously update the crosshair position within the focused window."""
        root = tk.Tk()
        root.withdraw()

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        self.vertical_line = tk.Toplevel()
        self.vertical_line.configure(bg="green")
        self.vertical_line.overrideredirect(True)
        self.vertical_line.attributes("-topmost", True)
        self.vertical_line.withdraw() # Initially hidden

        self.horizontal_line = tk.Toplevel()
        self.horizontal_line.configure(bg="green")
        self.horizontal_line.overrideredirect(True)
        self.horizontal_line.attributes("-topmost", True)
        self.horizontal_line.withdraw() # Initially hidden

        self.coord_label = tk.Toplevel()
        self.coord_label.overrideredirect(True)
        self.coord_label.attributes("-topmost", True)
        label = tk.Label(self.coord_label, bg="#9ffb63", fg="black", font=("JetBrainsMono NFP", 12, "bold"))
        label.pack()
        self.coord_label.withdraw() # Initially hidden

        while self.running:
            time.sleep(0.01) # Small delay to reduce CPU usage
            try:
                hwnd = win32gui.GetForegroundWindow()
                win_rect = win32gui.GetWindowRect(hwnd)
                win_left, win_top, win_right, win_bottom = win_rect
                win_width = win_right - win_left
                win_height = win_bottom - win_top
            except Exception:
                # If we can't get a window, hide everything
                self.vertical_line.withdraw()
                self.horizontal_line.withdraw()
                self.coord_label.withdraw()
                root.update()
                continue

            with mouse.Controller() as m:
                mouse_x, mouse_y = m.position

            # Check if mouse is inside the focused window
            if win_left <= mouse_x < win_right and win_top <= mouse_y < win_bottom:
                self.vertical_line.deiconify()
                self.horizontal_line.deiconify()

                line_color = "red" if self.is_dragging else "green"
                self.vertical_line.configure(bg=line_color)
                self.horizontal_line.configure(bg=line_color)

                self.vertical_line.geometry(f"2x{win_height}+{mouse_x}+{win_top}")
                self.horizontal_line.geometry(f"{win_width}x2+{win_left}+{mouse_y}")

                if self.show_coordinates:
                    self.coord_label.deiconify()
                    relative_x = mouse_x - win_left
                    relative_y = mouse_y - win_top

                    if self.is_dragging and self.start_x is not None:
                        start_rel_x = self.start_x - win_left
                        start_rel_y = self.start_y - win_top
                        label.config(text=f"Drag: ({start_rel_x},{start_rel_y}) to ({relative_x},{relative_y})")
                    elif self.start_x is not None and self.end_x is not None:
                        start_rel_x = self.start_x - win_left
                        start_rel_y = self.start_y - win_top
                        end_rel_x = self.end_x - win_left
                        end_rel_y = self.end_y - win_top
                        label.config(text=f"Region: ({min(start_rel_x, end_rel_x)},{min(start_rel_y, end_rel_y)}), ({max(start_rel_x, end_rel_x)},{max(start_rel_y, end_rel_y)})")
                    else:
                        label.config(text=f"X={relative_x}, Y={relative_y}")

                    offset_x, offset_y = 20, 20
                    label_x = mouse_x + offset_x
                    label_y = mouse_y + offset_y
                    # A bit of a guess for label width/height
                    if label_x + 150 > screen_width: label_x = mouse_x - offset_x - 150
                    if label_y + 30 > screen_height: label_y = mouse_y - offset_y - 30
                    self.coord_label.geometry(f"+{label_x}+{label_y}")
                else:
                    self.coord_label.withdraw()
            else:
                self.vertical_line.withdraw()
                self.horizontal_line.withdraw()
                self.coord_label.withdraw()

            root.update_idletasks()
            root.update()

        self.vertical_line.destroy()
        self.horizontal_line.destroy()
        self.coord_label.destroy()

    def copy_coordinates(self):
        """Copy coordinates relative to the active window to the clipboard."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            win_rect = win32gui.GetWindowRect(hwnd)
            win_left, win_top, _, _ = win_rect
        except Exception:
            print("Error: Could not get active window to calculate relative coordinates.")
            return

        if self.start_x is not None and self.end_x is not None:
            rel_start_x = self.start_x - win_left
            rel_start_y = self.start_y - win_top
            rel_end_x = self.end_x - win_left
            rel_end_y = self.end_y - win_top
            x1, y1 = min(rel_start_x, rel_end_x), min(rel_start_y, rel_end_y)
            x2, y2 = max(rel_start_x, rel_end_x), max(rel_start_y, rel_end_y)
            pyperclip.copy(f"{x1}, {y1}, {x2}, {y2}")
            print(f"Copied relative region: {x1}, {y1}, {x2}, {y2}")
        else:
            with mouse.Controller() as m:
                mouse_x, mouse_y = m.position
            rel_x = mouse_x - win_left
            rel_y = mouse_y - win_top
            pyperclip.copy(f"{rel_x}, {rel_y}")
            print(f"Copied relative point: {rel_x}, {rel_y}")

    def toggle_coordinates(self):
        """Toggle the visibility of the coordinates."""
        self.show_coordinates = not self.show_coordinates

    def exit_script(self):
        """Exit the script and remove the crosshair."""
        self.running = False
        keyboard.remove_all_hotkeys()

if __name__ == "__main__":
    overlay = AppCrosshairOverlay()
    # The main thread will exit when the daemon threads are the only ones left.
    # We need to keep it alive to listen for keyboard hotkeys.
    # A simple way is to join one of the threads.
    overlay.update_thread.join()
