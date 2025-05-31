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
                # Left button pressed - start of drag
                self.start_x = x
                self.start_y = y
                self.is_dragging = True
            else:
                # Left button released - end of drag
                self.end_x = x
                self.end_y = y
                self.is_dragging = False
                # Automatically copy the region when drag ends
                self.copy_coordinates()
                # Reset coordinates after copying to avoid copying the same region repeatedly
                self.start_x = None
                self.start_y = None
                self.end_x = None
                self.end_y = None


    def update_crosshair(self):
        """Continuously update the crosshair position and display coordinates."""
        root = tk.Tk()
        root.withdraw()  # Hide the main tkinter window

        # Screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        self.vertical_line = tk.Toplevel()
        # Initial color is green
        self.vertical_line.configure(bg="green")
        self.vertical_line.overrideredirect(True)
        self.vertical_line.attributes("-topmost", True)

        self.horizontal_line = tk.Toplevel()
        # Initial color is green
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

            # Determine the crosshair color based on dragging state
            if self.is_dragging:
                line_color = "red"
            else:
                line_color = "green"

            # Update vertical line
            self.vertical_line.geometry(f"2x{screen_height}+{mouse_x}+0")
            self.vertical_line.configure(bg=line_color) # Set color dynamically

            # Update horizontal line
            self.horizontal_line.geometry(f"{screen_width}x2+0+{mouse_y}")
            self.horizontal_line.configure(bg=line_color) # Set color dynamically

            if self.show_coordinates:
                # Update coordinate label
                if self.is_dragging and self.start_x is not None:
                    label.config(text=f"Drag: ({self.start_x},{self.start_y}) to ({mouse_x},{mouse_y})")
                elif self.start_x is not None and self.end_x is not None:
                     label.config(text=f"Region: ({self.start_x},{self.start_y}), ({self.end_x},{self.end_y})")
                else:
                    label.config(text=f"X={mouse_x}, Y={mouse_y}")


                # Position label with edge detection
                offset_x = 20
                offset_y = 20

                if mouse_x + offset_x + 135 > screen_width:
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
        """Copy the current mouse coordinates or region to the clipboard."""
        if self.start_x is not None and self.end_x is not None:
            # Sort coordinates to ensure top-left and bottom-right
            x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
            x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)
            pyperclip.copy(f"{x1}, {y1}, {x2}, {y2}")
            print(f"Copied region: {x1}, {y1}, {x2}, {y2}") # For debugging
        else:
            with mouse.Controller() as m:
                mouse_x, mouse_y = m.position
            pyperclip.copy(f"{mouse_x}, {mouse_y}")
            print(f"Copied single point: {mouse_x}, {mouse_y}") # For debugging

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