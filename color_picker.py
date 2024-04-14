import tkinter as tk
import pyautogui
import pyperclip
import keyboard

def update_color():
    # Get the position of the mouse cursor
    x, y = pyautogui.position()
    
    # Capture the color of the screen at the mouse cursor position
    color = pyautogui.screenshot().getpixel((x, y))
    
    # Convert the RGB color to hexadecimal format
    hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
    
    # Update the color label text and background color
    color_label.config(text=f"Color: {hex_color}", bg=hex_color)
    
    # Schedule the update every 100 milliseconds (0.1 second)
    root.after(100, update_color)

def copy_color():
    # Get the text of the color label
    color_text = color_label.cget("text")
    
    # Extract the color value (hexadecimal)
    hex_color = color_text.split(": ")[1]
    
    # Copy the color value to the clipboard
    pyperclip.copy(hex_color)

# Create the main window
root = tk.Tk()
root.title("Color Picker")

# Create a label to display the color
color_label = tk.Label(root, text="Color: ", font=("Arial", 14), padx=10, pady=5)
color_label.pack()

# Start updating the color
update_color()

# Register a global hotkey (Ctrl+Space) to copy the color
keyboard.add_hotkey("ctrl+space", copy_color)

# Run the Tkinter event loop
root.mainloop()
