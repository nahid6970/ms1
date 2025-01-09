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
        self.coord_label = None
        self.running = True
        self.show_coordinates = True  # Toggle to show or hide coordinates

        # Hide Python console window
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        # Start the real-time update thread
        self.update_thread = threading.Thread(target=self.update_crosshair)
        self.update_thread.daemon = True
        self.update_thread.start()

        # Set up global hotkeys
        keyboard.add_hotkey("ctrl+c", self.copy_coordinates)
        keyboard.add_hotkey("esc", self.exit_script)
        keyboard.add_hotkey("CAPSLOCK", self.toggle_coordinates)

    def update_crosshair(self):
        """Continuously update the crosshair position and display coordinates."""
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

        self.coord_label = tk.Toplevel()
        self.coord_label.overrideredirect(True)
        self.coord_label.attributes("-topmost", True)
        label = tk.Label(self.coord_label, bg="#9ffb63", fg="black", font=("JetBrainsMono NFP", 12, "bold"))
        label.pack()

        while self.running:
            with mouse.Controller() as m:
                mouse_x, mouse_y = m.position

            # Update vertical line
            self.vertical_line.geometry(f"2x{screen_height}+{mouse_x}+0")

            # Update horizontal line
            self.horizontal_line.geometry(f"{screen_width}x2+0+{mouse_y}")

            if self.show_coordinates:
                # Update coordinate label
                label.config(text=f"X={mouse_x}, Y={mouse_y}")

                # Position label with edge detection
                offset_x = 20
                offset_y = 20

                if mouse_x + offset_x + 100 > screen_width:
                    label_x = mouse_x - offset_x - 135
                else:
                    label_x = mouse_x + offset_x

                if mouse_y + offset_y + 30 > screen_height:
                    label_y = mouse_y - offset_y - 30
                else:
                    label_y = mouse_y + offset_y

                self.coord_label.geometry(f"+{label_x}+{label_y}")
                self.coord_label.deiconify()  # Show the label
            else:
                self.coord_label.withdraw()  # Hide the label

            root.update_idletasks()
            root.update()

        # Clean up when stopped
        self.vertical_line.destroy()
        self.horizontal_line.destroy()
        self.coord_label.destroy()

    def copy_coordinates(self):
        """Copy the current mouse coordinates to the clipboard."""
        with mouse.Controller() as m:
            mouse_x, mouse_y = m.position
        pyperclip.copy(f"X={mouse_x}, Y={mouse_y}")

    def toggle_coordinates(self):
        """Toggle the visibility of the coordinates."""
        self.show_coordinates = not self.show_coordinates

    def exit_script(self):
        """Exit the script and remove the crosshair."""
        self.running = False
        keyboard.remove_all_hotkeys()

if __name__ == "__main__":
    overlay = CrosshairOverlay()
    overlay.update_thread.join()