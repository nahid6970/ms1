import threading
import tkinter as tk
from tkinter import ttk
import subprocess
import pyautogui

def center_and_press_alt_2(window):
    def center_window():
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def press_alt_2():
        pyautogui.hotkey('alt', '2')
    center_window()
    window.after(25, press_alt_2)

# Create the main window
root = tk.Tk()
root.title("Rclone + winfsp")
root.configure(bg="#282c34")

# Variables
command_var = tk.StringVar(value="")
Other_var = tk.StringVar(value="")
grep_var = tk.StringVar(value="")
line_count_var = tk.BooleanVar(value=False)
transfer_var = tk.StringVar(value="4")
include_var = tk.StringVar(value="*.jpg")
exclude_var = tk.StringVar(value="*.jpg")

# Style Configuration
style = ttk.Style()
style.configure("Custom.TRadiobutton", font=("JetBrainsmono nfp", 12, "bold"), foreground="#e6f752", background="#282c34")
style.configure("Black.TFrame", background="#282c34")

# Manage additional items (first 5 items)
additional_options = [
    ("2>&1 redirects stderr", "2>&1", False),
    ("Readable", "--human-readable", False),
    ("Acknowledge Abuse", "--drive-acknowledge-abuse", False),
    ("Web Gui **Rcd", "--rc-web-gui", False),
    ("Log Level", "--log-level ERROR", False),
]

# Create the arguments frame
arguments_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
arguments_frame.grid(row=2, column=0, sticky=tk.W)

# Create labels for additional options
def initialize_labels():
    for idx, (display_text, _, is_selected) in enumerate(additional_options):
        column = idx // 5
        row = idx % 5
        label = tk.Label(arguments_frame, text=display_text, font=("Jetbrainsmono nfp",10,"bold"), bg="#b6fba0" if is_selected else "#fa8a93", width=25, anchor="center")
        label.grid(row=row, column=column, sticky=tk.W, padx=5, pady=5)
        label.bind("<Button-1>", lambda e, l=label, i=idx: toggle_option(l, i))

def toggle_option(label, idx):
    additional_options[idx] = (additional_options[idx][0], additional_options[idx][1], not additional_options[idx][2])
    update_label_color(label, additional_options[idx][2])

def update_label_color(label, is_selected):
    label.config(bg="#b6fba0" if is_selected else "#fa8a93")

initialize_labels()

# Create the command input frame
command_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
command_frame.grid(row=0, column=0, sticky=tk.W)

ttk.Label(command_frame, text="Command:", background="#f15812", font=("Jetbrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)

# Create the command input text box
command_entry = ttk.Entry(command_frame, textvariable=command_var, width=50)
command_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Create Other frame
Other_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
Other_frame.grid(row=1, column=0, sticky=tk.W)

ttk.Label(Other_frame, text="Other:", background="#f15812", font=("JetBrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
Other_radios = [
    {"text": "N/A", "value": "", "row": 0, "column": 1},
    {"text": "C:/", "value": "C:/", "row": 0, "column": 2},
    {"text": "D:/", "value": "D:/", "row": 0, "column": 3},
    {"text": "cgu:/", "value": "cgu:/", "row": 1, "column": 1},
    {"text": "gu:/", "value": "gu:/", "row": 1, "column": 2},
    {"text": "g00:/", "value": "g00:/", "row": 1, "column": 3},
]

for item in Other_radios:
    radio = ttk.Radiobutton(Other_frame, text=item["text"], variable=Other_var, value=item["value"], style="Custom.TRadiobutton")
    radio.grid(row=item["row"], column=item["column"], sticky=tk.W)

# Create a frame for grep filter
grep_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
grep_frame.grid(row=4, column=0, sticky=tk.W)

ttk.Label(grep_frame, text="Grep Text:", background="#f15812", font=("Jetbrainsmono nfp", 12, "bold")).grid(row=0, column=0, sticky=tk.W)
grep_entry = ttk.Entry(grep_frame, textvariable=grep_var, width=30)
grep_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

# Create a frame for line count option
line_count_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
line_count_frame.grid(row=5, column=0, sticky=tk.W)

line_count_checkbox = ttk.Checkbutton(
    line_count_frame,
    text="Include Line Count",
    variable=line_count_var,
    style="Custom.TRadiobutton"
)
line_count_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

# Create a frame for extra items
options_frame = ttk.Frame(root, padding="10", style="Black.TFrame")
options_frame.grid(row=3, column=0, sticky=tk.W)

# Execute Command Function
def execute_command():
    # Construct the command
    command = [command_var.get(), Other_var.get()]

    # Include the first 5 additional options
    for display_text, actual_text, is_selected in additional_options[:5]:  # Only first 5 options
        if is_selected:
            command.append(actual_text)

    # Append grep filter if text is provided
    grep_text = grep_var.get().strip()
    if grep_text:
        command.append(f"| grep {grep_text}")

    # Append line count if option is enabled
    if line_count_var.get():
        command.append("| Measure-Object -Line")  # PowerShell equivalent of `wc -l`

    final_command = " ".join(command)
    print("Executing:", final_command)

    def run_command():
        try:
            # Run the PowerShell command and capture the output
            process = subprocess.Popen(
                ["powershell", "-Command", final_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            # If line count option is enabled, count lines
            if line_count_var.get():
                lines = stdout.splitlines()
                line_count = len(lines) if lines else 0
                print(f"\033[92mLine Count: {line_count}\033[0m")
            else:
                print(stdout)

            if stderr:
                print(f"\033[91mError: {stderr}\033[0m")
        except Exception as e:
            print(f"\033[91mError: {e}\033[0m")

    thread = threading.Thread(target=run_command)
    thread.start()

def clear_terminal():
    subprocess.run("cls", shell=True)

# Bottom frame for execute and clear buttons
BottomFrame = ttk.Frame(root, padding="10", style="Black.TFrame")
BottomFrame.grid(row=6, column=0, sticky=tk.E)

execute_button = tk.Button(BottomFrame, text="Execute", font=("Jetbrainsmono nfp", 12, "bold"), bg="#4da9ff", fg="#000000", command=execute_command)
execute_button.grid(row=4, column=0, pady=10, padx=10, sticky=tk.W)

clear_button = tk.Button(BottomFrame, text="Clear", font=("Jetbrainsmono nfp", 12, "bold"), bg="#282c34", fg="#ffffff", command=clear_terminal)
clear_button.grid(row=4, column=1, pady=10, sticky=tk.W)

center_and_press_alt_2(root)
# Run the main event loop
root.mainloop()
