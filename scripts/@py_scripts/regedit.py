import tkinter as tk
from tkinter import simpledialog
import winreg

def create_registry_entry():
    # Prompt user for key name and value
    key_name = simpledialog.askstring("Input", "Enter the registry key name:")
    key_value = simpledialog.askstring("Input", "Enter the registry key value:")
    
    # Open the registry key and set the value
    path = winreg.HKEY_LOCAL_MACHINE
    RUN = winreg.OpenKeyEx(path, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\")
    new_key = winreg.CreateKey(RUN, "Run")
    winreg.SetValueEx(new_key, key_name, 0, winreg.REG_SZ, key_value)
    
    # Close the registry key
    if new_key:
        winreg.CloseKey(new_key)

# Create the Tkinter window
root = tk.Tk()
root.title("Registry Entry Creator")

# Create the button
create_button = tk.Button(root, text="Create Registry Entry", command=create_registry_entry)
create_button.pack(padx=10, pady=10)

# Run the Tkinter event loop
root.mainloop()
