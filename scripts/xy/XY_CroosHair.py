import tkinter as tk
from pynput import mouse

class CrosshairGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crosshair GUI")
        self.root.geometry("300x100")
        self.root.resizable(False, False)
        
        # Initialize crosshair lines and label
        self.vertical_line = None
        self.horizontal_line = None
        self.coord_label = None
        self.crosshair_visible = False

        # Toggle Button
        self.toggle_button = tk.Button(self.root, text="Toggle Crosshair", command=self.toggle_crosshair)
        self.toggle_button.pack(pady=20)

        # Bind the Space key to toggle crosshair
        self.root.bind("<space>", lambda event: self.toggle_crosshair())

    def toggle_crosshair(self):
        if self.crosshair_visible:
            # Hide crosshair
            self.remove_crosshair()
        else:
            # Show crosshair
            self.show_crosshair()
        self.crosshair_visible = not self.crosshair_visible

    def show_crosshair(self):
        # Capture mouse position
        with mouse.Controller() as m:
            mouse_pos = m.position
        
        # Coordinates label
        self.coord_label = tk.Label(self.root, text=f"Mouse Position: X={mouse_pos[0]} Y={mouse_pos[1]}")
        self.coord_label.pack()

        # Create vertical and horizontal crosshair lines
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Vertical line
        self.vertical_line = tk.Toplevel(self.root)
        self.vertical_line.geometry(f"2x{screen_height}+{mouse_pos[0]}+0")
        self.vertical_line.configure(bg="green")
        self.vertical_line.overrideredirect(True)
        self.vertical_line.attributes("-topmost", True)

        # Horizontal line
        self.horizontal_line = tk.Toplevel(self.root)
        self.horizontal_line.geometry(f"{screen_width}x2+0+{mouse_pos[1]}")
        self.horizontal_line.configure(bg="green")
        self.horizontal_line.overrideredirect(True)
        self.horizontal_line.attributes("-topmost", True)

    def remove_crosshair(self):
        # Destroy the crosshair lines and coordinate label if they exist
        if self.vertical_line:
            self.vertical_line.destroy()
            self.vertical_line = None
        if self.horizontal_line:
            self.horizontal_line.destroy()
            self.horizontal_line = None
        if self.coord_label:
            self.coord_label.destroy()
            self.coord_label = None

if __name__ == "__main__":
    root = tk.Tk()
    app = CrosshairGUI(root)
    root.mainloop()
