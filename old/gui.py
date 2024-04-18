import tkinter as tk
from tkinter import ttk
import subprocess

def run_script(script):
    subprocess.Popen(script, shell=True)

def create_category_frame(notebook, category_name, scripts):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=category_name)

    for text, cmd in scripts:
        button = ttk.Button(frame, text=text, command=lambda c=cmd: run_script(c))
        button.pack(pady=5)

def main():
    window = tk.Tk()

    # Set window dimensions (widthxheight)
    window.geometry("400x300")
    window.title("Script Launcher")

    notebook = ttk.Notebook(window)
    notebook.pack(expand=True, fill=tk.BOTH)

    # Add categories and scripts
    categories = [
        ("FFmpeg", [
            ("Go to D:", "cd D:"),
            ("List Files in D:", "dir")
        ]),
        ("rclone", [
            ("Open rclone config", "rclone config"),
            ("List Files in D:", "rclone ls d:"),
            ("List Files in C:", "rclone ls c:")
        ]),
        ("system", [
            ("Temp Cleaner", "rclone config"),

        ])
    ]

    for category_name, scripts in categories:
        create_category_frame(notebook, category_name, scripts)

    window.mainloop()

if __name__ == "__main__":
    main()
