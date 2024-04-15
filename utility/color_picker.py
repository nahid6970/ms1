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
    ROOT.after(100, update_color)

def copy_color():
    # Get the text of the color label
    color_text = color_label.cget("text")
    
    # Extract the color value (hexadecimal)
    hex_color = color_text.split(": ")[1]
    
    # Copy the color value to the clipboard
    pyperclip.copy(hex_color)

# Create the main window
ROOT = tk.Tk()
ROOT.title("Color Picker")



def close_window(event=None):
    ROOT.destroy()
ROOT.attributes('-topmost', True)
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)
screen_width = ROOT.winfo_screenwidth()
screen_height = ROOT.winfo_screenheight()
x = 242
y = 7
ROOT.geometry(f"+{x}+{y}")
ROOT.configure(bg="#282c34")
ROOT.overrideredirect(True)
box1 = tk.Frame(ROOT, bg="#1d2027")
box1.pack(side="right", anchor="center", pady=(0,0),padx=(0,0))

# Create a label to display the color
color_label = tk.Label(ROOT, text="Color: ", font=("JetBrainsMono NF", 10, "bold"))
color_label.pack(side="left")
LB_name = tk.Label(box1, bg="#ff0000", fg="#FFFFFF", font=("JetBrainsMono NF", 10, "bold"), text="X")
LB_name.pack(side="left")
LB_name.bind("<Button-1>", close_window)



# Start updating the color
update_color()

# Register a global hotkey (Ctrl+Space) to copy the color
keyboard.add_hotkey("ctrl+space", copy_color)

# Run the Tkinter event loop
ROOT.mainloop()
