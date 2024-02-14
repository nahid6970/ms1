import tkinter as tk
import pyautogui
from datetime import datetime
import os
import ctypes

def capture_screenshot():
    # Hide the Tkinter window
    root.withdraw()

    
    # Get the current date and time
    now = datetime.now()
    timestamp = now.strftime("%Y_%m_%d_%H_%M_%S")
    
    # Construct the filename
    filename = f"D:\\@gallery\\{timestamp}.png"
    
    # Capture the screenshot without the Tkinter window
    screenshot = pyautogui.screenshot(region=(0, 0, root.winfo_screenwidth(), root.winfo_screenheight()))
    
    # Save the screenshot
    screenshot.save(filename)
    
    # Restore the Tkinter window
    root.deiconify()
    
    # Create buttons for user options
    options_frame = tk.Toplevel(root)
    options_frame.title("Options")
 
    options_frame.title("Screenshot Capture")
    options_frame.geometry("200x50")
    options_frame.attributes('-topmost', True)  # Set always on top


    # Function to handle user choice
    def handle_choice(choice):
        options_frame.destroy()
        if choice == "Paint":
            os.system(f"mspaint {filename}")
        elif choice == "View":
            os.startfile(filename)
        elif choice == "Copy":
            os.system(f"copy {filename} NUL")
        elif choice == "Delete":
            os.remove(filename)


    
    
    # Create buttons for user options
    paint_button = tk.Button(options_frame, text="Paint", command=lambda: handle_choice("Paint"))
    paint_button.pack(side="left", padx=5, pady=5)
    
    view_button = tk.Button(options_frame, text="View", command=lambda: handle_choice("View"))
    view_button.pack(side="left", padx=5, pady=5)
    
    copy_button = tk.Button(options_frame, text="Copy", command=lambda: handle_choice("Copy"))
    copy_button.pack(side="left", padx=5, pady=5)
    
    delete_button = tk.Button(options_frame, bg="red", fg="white", text="Delete", command=lambda: handle_choice("Delete"))
    delete_button.pack(side="left", padx=5, pady=5)

# Calculate the screen width and height
    screen_width = options_frame.winfo_screenwidth()
    screen_height = options_frame.winfo_screenheight()

    # Calculate the x and y coordinates to center the window
    x = (screen_width - 210) // 1  #  higher means left side lower means right side
    y = (screen_height - 240) // 1  #  higher means top side lower means bottom side

    # Set the geometry of the window
    options_frame.geometry(f"200x50+{x}+{y}") #! overall size of the window

# Create the Tkinter window
    
def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)
set_console_title("capture")

root = tk.Tk()
root.title("Screenshot Capture")
root.attributes('-topmost', True)  # Set always on top
root.geometry("150x50")
root.attributes('-topmost', True)  # Set always on top


# Create the button to capture the screenshot
capture_button = tk.Button(root, text="Capture Screenshot", command=capture_screenshot)
capture_button.pack(padx=10, pady=10)

# Calculate the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Calculate the x and y coordinates to center the window
x = (screen_width - 170) // 1  # 400 is the width of your window higher means left side lower means right side
y = (screen_height - 150) // 1  # 700 is the height of your window higher means top side lower means bottom side

# Set the geometry of the window
root.geometry(f"150x50+{x}+{y}") #! overall size of the window

# Run the Tkinter event loop
root.mainloop()