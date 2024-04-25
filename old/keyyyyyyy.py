import argparse
import keyboard
import os

def execute_shortcut(shortcut_actions):
    for shortcut, action in shortcut_actions.items():
        keyboard.add_hotkey(shortcut, action)

def main():
    # Define shortcuts and their actions
    shortcut_actions = {
        "win+alt+1": lambda: os.system("code"),
        "ctrl+alt+s": lambda: print("Hello, World!")
        # Add more shortcuts and actions as needed
    }

    # Execute the shortcuts and their respective actions
    execute_shortcut(shortcut_actions)

    # Keep the script running
    keyboard.wait('esc')

if __name__ == "__main__":
    main()
