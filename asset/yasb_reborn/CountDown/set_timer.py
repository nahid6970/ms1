import tkinter as tk
from tkinter import messagebox
import re
import time
import json
from datetime import datetime, timedelta
import os

def parse_time_input(time_str):
    """Parse time input like '5h 3m' or '1d 5h 3m' and return total seconds"""
    total_seconds = 0
    
    # Pattern to match time components (number followed by unit)
    pattern = r'(\d+)([a-zA-Z]+)'
    matches = re.findall(pattern, time_str)
    
    for value, unit in matches:
        value = int(value)
        unit = unit.lower()
        
        if unit in ['d', 'day', 'days']:
            total_seconds += value * 86400  # 24 * 60 * 60
        elif unit in ['h', 'hr', 'hour', 'hours']:
            total_seconds += value * 3600   # 60 * 60
        elif unit in ['m', 'min', 'minute', 'minutes']:
            total_seconds += value * 60
        elif unit in ['s', 'sec', 'second', 'seconds']:
            total_seconds += value
    
    return total_seconds

def save_timer(end_time):
    """Save the end time to a file in the user's home directory"""
    try:
        # Get the user's home directory
        home_dir = os.path.expanduser("~")
        timer_dir = os.path.join(home_dir, "script_output")
        
        # Create the directory if it doesn't exist
        os.makedirs(timer_dir, exist_ok=True)
        
        timer_file_path = os.path.join(timer_dir, 'timer_end_time.txt')
        
        with open(timer_file_path, 'w') as f:
            f.write(str(end_time))
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save timer: {str(e)}")
        return False

def set_timer():
    """Main function to set the timer with GUI"""
    # Create main window
    root = tk.Tk()
    root.title("Set Timer")
    root.geometry("350x200")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Create and pack widgets
    label = tk.Label(root, text="Enter time (e.g., 5h 3m or 1d 5h 3m):", font=("Arial", 10))
    label.pack(pady=20)
    
    entry = tk.Entry(root, width=30, font=("Arial", 12))
    entry.pack(pady=10)
    entry.focus()
    
    def on_submit():
        time_input = entry.get().strip()
        if not time_input:
            messagebox.showwarning("Warning", "Please enter a time value.")
            return
            
        try:
            total_seconds = parse_time_input(time_input)
            if total_seconds <= 0:
                messagebox.showwarning("Warning", "Please enter a valid time value.")
                return
                
            # Calculate end time
            end_time = time.time() + total_seconds
            
            # Save to file
            if save_timer(end_time):
                messagebox.showinfo("Success", f"Timer set for {time_input} from now.")
                root.destroy()
            else:
                messagebox.showerror("Error", "Failed to save timer.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Invalid time format: {str(e)}")
    
    # Bind Enter key to submit
    entry.bind('<Return>', lambda event: on_submit())
    
    submit_btn = tk.Button(root, text="Set Timer", command=on_submit, font=("Arial", 12), width=15, height=1)
    submit_btn.pack(pady=20)
    
    # Add example label
    example_label = tk.Label(root, text="Examples: 5h 3m, 1d 5h 3m, 30m, 2h", font=("Arial", 8), fg="gray")
    example_label.pack()
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    set_timer()