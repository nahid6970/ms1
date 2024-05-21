import tkinter as tk
from tkinter import ttk
import subprocess
import requests
import os
import ctypes

# URL to the executable
url = "https://github.com/oberrich/win11-toggle-rounded-corners/releases/download/v1.2/win11-toggle-rounded-corners.exe"
# Path to the download directory
download_dir = r"C:\Users\nahid\OneDrive\backup"
# Full path to the executable
exe_path = os.path.join(download_dir, "win11-toggle-rounded-corners.exe")

# Function to download the executable
def download_executable():
    response = requests.get(url)
    with open(exe_path, 'wb') as file:
        file.write(response.content)
    print(f"{exe_path} downloaded successfully.")

# Function to run a command as admin
def run_as_admin(command):
    try:
        exe_path = command[0]
        params = ' '.join(command[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe_path, params, None, 1)
    except Exception as e:
        print(f"Error running command as admin: {e}")

# Function to enable rounded corners
def enable_rounded_corners():
    run_as_admin([exe_path, '--enable'])

# Function to disable rounded corners
def disable_rounded_corners():
    run_as_admin([exe_path, '--disable --autostart'])

# Check if the executable is already downloaded, if not download it
if not os.path.exists(exe_path):
    download_executable()

# Create the main window
root = tk.Tk()
root.title("Win11 Toggle Rounded Corners")
root.geometry("300x150")

# Configure dark theme
root.configure(bg='#2e2e2e')
style = ttk.Style()

# Set ttk theme to "clam" which is more easily customizable
style.theme_use('clam')

# Define styles
style.configure('TFrame', background='#2e2e2e')
style.configure('TButton', font=('Arial', 12), background='#3e3e3e', foreground='#ffffff', borderwidth=1)
style.map('TButton', background=[('active', '#575757')])
style.configure('TLabel', font=('Arial', 12), background='#2e2e2e', foreground='#ffffff')

# Create frame
frame = ttk.Frame(root)
frame.pack(expand=True, fill='both')

# Create enable button
enable_button = ttk.Button(frame, text="Enable Rounded Corners", command=enable_rounded_corners)
enable_button.pack(pady=10, padx=20, fill='x')

# Create disable button
disable_button = ttk.Button(frame, text="Disable Rounded Corners", command=disable_rounded_corners)
disable_button.pack(pady=10, padx=20, fill='x')

# Run the Tkinter event loop
root.mainloop()
