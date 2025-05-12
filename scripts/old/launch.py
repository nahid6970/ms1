import subprocess
import os
from tkinter import Tk, Button, simpledialog, messagebox

def launch_shortcut():
    # Ask for password
    password = simpledialog.askstring("Password", "Enter the password:", show='*')
    
    # Check if the password is correct
    if password == "753951":
        # Path to the shortcut
        shortcut_path = "C:/Riot Games/Riot Client/RiotClientServices.exe"

        # Command to launch the shortcut with required arguments
        command = [shortcut_path, '--launch-product=valorant', '--launch-patchline=live']

        # Set the working directory
        os.chdir("C:/Riot Games/Riot Client")

        # Launch the shortcut using subprocess
        subprocess.Popen(command)
    else:
        messagebox.showerror("Error", "Incorrect password!")

# Create a GUI window
root = Tk()
root.title("Launch Valorant Shortcut")

# Create a button to launch the shortcut
launch_button = Button(root, text="Launch Valorant", command=launch_shortcut)
launch_button.pack()

# Run the GUI application
root.mainloop()
