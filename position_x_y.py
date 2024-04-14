import tkinter as tk
import pyautogui

def update_position():
    x, y = pyautogui.position()
    position_label.config(text=f"X: {x}, Y: {y}")
    root.after(1000, update_position)  # Schedule the update every 1000 milliseconds (1 second)

# Create the main window
root = tk.Tk()
root.title("Mouse Position Tracker")

# Create a label to display the mouse position
position_label = tk.Label(root, text="")
position_label.pack()

# Start updating the mouse position
update_position()

# Run the Tkinter event loop
root.mainloop()
