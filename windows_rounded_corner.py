import tkinter as tk
import winreg

def toggle_registry_value():
    # Define the registry key path
    key_path = r"Software\Microsoft\Windows\DWM"

    # Open the registry key
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
    except FileNotFoundError:
        # If the key doesn't exist, create it
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)

    # Check the current value
    try:
        current_value, _ = winreg.QueryValueEx(key, "UseWindowFrameStagingBuffer")
    except FileNotFoundError:
        # If the value doesn't exist, set it to 1
        winreg.SetValueEx(key, "UseWindowFrameStagingBuffer", 0, winreg.REG_DWORD, 1)
        label.config(text="Value set to 1")
        return
    except Exception as e:
        label.config(text=f"Error: {e}")
        return

    # Toggle the value between 0 and 1
    new_value = 1 - current_value
    winreg.SetValueEx(key, "UseWindowFrameStagingBuffer", 0, winreg.REG_DWORD, new_value)
    
    if new_value == 0:
        label.config(text="Value set to 0")
    else:
        label.config(text="Value set to 1")

    # Close the registry key
    winreg.CloseKey(key)

# Create the main window
root = tk.Tk()
root.title("Toggle Registry Value")

# Create a button to toggle the registry value
button = tk.Button(root, text="Toggle Value", command=toggle_registry_value)
button.pack(pady=10)

# Create a label to show the current status
label = tk.Label(root, text="")
label.pack()

# Run the Tkinter event loop
root.mainloop()
