import tkinter as tk
from pynput import mouse
import keyboard  # For global hotkeys

class CrosshairOverlay:
    def __init__(self):
        self.vertical_line = None
        self.horizontal_line = None
        self.coord_label = None

        # Set up global hotkeys for refreshing the crosshair and exiting
        keyboard.add_hotkey("ctrl+space", self.refresh_crosshair)
        keyboard.add_hotkey("esc", self.exit_script)

    def refresh_crosshair(self):
        # Remove any existing crosshair and label
        self.remove_crosshair()

        # Get current mouse position
        with mouse.Controller() as m:
            mouse_x, mouse_y = m.position

        # Screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Create vertical line (crosshair)
        self.vertical_line = tk.Toplevel()
        self.vertical_line.geometry(f"2x{screen_height}+{mouse_x}+0")
        self.vertical_line.configure(bg="green")
        self.vertical_line.overrideredirect(True)
        self.vertical_line.attributes("-topmost", True)

        # Create horizontal line (crosshair)
        self.horizontal_line = tk.Toplevel()
        self.horizontal_line.geometry(f"{screen_width}x2+0+{mouse_y}")
        self.horizontal_line.configure(bg="green")
        self.horizontal_line.overrideredirect(True)
        self.horizontal_line.attributes("-topmost", True)

        # Coordinates label with edge detection
        self.coord_label = tk.Toplevel()
        label = tk.Label(self.coord_label, text=f"X={mouse_x}, Y={mouse_y}", bg="yellow", fg="black")
        label.pack()

        # Adjust label position to stay within screen bounds
        offset_x = 20
        offset_y = 20

        # If near the right edge of the screen, adjust position to the left
        if mouse_x + offset_x + 100 > screen_width:
            label_x = mouse_x - offset_x - 100  # Position to the left
        else:
            label_x = mouse_x + offset_x  # Position to the right

        # If near the bottom edge of the screen, adjust position upward
        if mouse_y + offset_y + 30 > screen_height:
            label_y = mouse_y - offset_y - 30  # Position above
        else:
            label_y = mouse_y + offset_y  # Position below

        self.coord_label.geometry(f"+{label_x}+{label_y}")
        self.coord_label.overrideredirect(True)
        self.coord_label.attributes("-topmost", True)

    def remove_crosshair(self):
        # Destroy existing crosshair and label windows if they exist
        if self.vertical_line:
            self.vertical_line.destroy()
            self.vertical_line = None
        if self.horizontal_line:
            self.horizontal_line.destroy()
            self.horizontal_line = None
        if self.coord_label:
            self.coord_label.destroy()
            self.coord_label = None

    def exit_script(self):
        # Remove the hotkeys and exit the script
        keyboard.remove_hotkey("ctrl+space")
        keyboard.remove_hotkey("esc")
        root.quit()  # Close the tkinter event loop

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    overlay = CrosshairOverlay()
    # Run the tkinter event loop for crosshair display
    root.mainloop()