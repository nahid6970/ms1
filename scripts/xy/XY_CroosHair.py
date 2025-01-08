import tkinter as tk
from pynput import mouse
import keyboard  # For global hotkeys
import pyperclip  # For clipboard functionality
import threading
import ctypes

class CrosshairOverlay:
    def __init__(self):
        self.vertical_line = None
        self.horizontal_line = None
        self.running = True

        # Hide Python console window
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # Start the real-time update thread
        self.update_thread = threading.Thread(target=self.update_crosshair)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Set up global hotkeys
        keyboard.add_hotkey("ctrl+c", self.copy_coordinates)
        keyboard.add_hotkey("esc", self.exit_script)

    def update_crosshair(self):
        """Continuously update the crosshair position based on the mouse location."""
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window

        # Screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        self.vertical_line = tk.Toplevel()
        self.vertical_line.configure(bg="green")
        self.vertical_line.overrideredirect(True)
        self.vertical_line.attributes("-topmost", True)

        self.horizontal_line = tk.Toplevel()
        self.horizontal_line.configure(bg="green")
        self.horizontal_line.overrideredirect(True)
        self.horizontal_line.attributes("-topmost", True)

        while self.running:
            with mouse.Controller() as m:
                mouse_x, mouse_y = m.position

            # Update vertical line
            self.vertical_line.geometry(f"2x{screen_height}+{mouse_x}+0")

            # Update horizontal line
            self.horizontal_line.geometry(f"{screen_width}x2+0+{mouse_y}")

            root.update_idletasks()
            root.update()

        # Clean up when stopped
        self.vertical_line.destroy()
        self.horizontal_line.destroy()

    def copy_coordinates(self):
        """Copy the current mouse coordinates to the clipboard."""
        with mouse.Controller() as m:
            mouse_x, mouse_y = m.position
        pyperclip.copy(f"X={mouse_x}, Y={mouse_y}")

    def exit_script(self):
        """Exit the script and remove the crosshair."""
        self.running = False
        keyboard.remove_all_hotkeys()

if __name__ == "__main__":
    overlay = CrosshairOverlay()
    overlay.update_thread.join()