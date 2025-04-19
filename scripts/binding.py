import keyboard
import os
import subprocess
import ctypes

# Define the key bindings first
bindings = {
    ('alt', 'x'): 'start cmd',            # Open terminal (cmd)
    ('alt', 'q'): 'kill_active_window',   # Kill the active window
    ('ctrl', 'm'): 'exit_script',         # Exit the script
    ('ctrl', 'e'): 'some_command',        # Execute some command
    ('ctrl', 'v'): 'toggle_floating',     # Toggle floating window (placeholder)
    ('ctrl', 'r'): 'some_command',        # Execute some command
    ('ctrl', 'p'): 'code',                # Open VS Code
    ('ctrl', 'j'): 'toggle_split',        # Toggle split window (placeholder)
    ('ctrl', 'z', 'x'): 'start notepad' # Open Notepad with three-button shortcut
}

# Define the functions to handle the actions
user32 = ctypes.windll.user32

def kill_active_window():
    hwnd = user32.GetForegroundWindow()
    user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE

def exec_command(command):
    subprocess.Popen(command, shell=True)

def toggle_floating():
    print("Toggle floating is not directly supported on Windows.")
    # Implement the logic if you are using a tiling window manager on Windows

def toggle_split():
    print("Toggle split is not directly supported on Windows.")
    # Implement the logic if you are using a tiling window manager on Windows

def exit_script():
    os._exit(0)

# Mapping string actions to functions
action_mapping = {
    'kill_active_window': kill_active_window,
    'exit_script': exit_script,
    'toggle_floating': toggle_floating,
    'toggle_split': toggle_split,
}

# Register the key bindings
for keys, action in bindings.items():
    if action in action_mapping:
        keyboard.add_hotkey('+'.join(keys), action_mapping[action])
    else:
        keyboard.add_hotkey('+'.join(keys), lambda a=action: exec_command(a))

# Block forever, waiting for events.
keyboard.wait()
