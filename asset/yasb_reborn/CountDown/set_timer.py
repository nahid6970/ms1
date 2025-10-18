import customtkinter as ctk
from tkinter import messagebox
import re
import time
import os

# Set the appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
    root = ctk.CTk()
    root.title("Set Timer")
    root.geometry("400x250")
    root.resizable(False, False)
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Configure font
    font_family = "JetBrains Mono"
    
    # Create and pack widgets
    label = ctk.CTkLabel(root, text="Enter time (e.g., 5h 3m or 1d 5h 3m):", 
                        font=(font_family, 14))
    label.pack(pady=(20, 10))
    
    entry = ctk.CTkEntry(root, width=300, height=35, 
                        font=(font_family, 14), 
                        placeholder_text="e.g., 5h 3m or 1d 5h 3m")
    entry.pack(pady=10)
    
    # Ensure focus is set on the entry field
    root.after(100, lambda: entry.focus())
    
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
                # Close window silently on success (no confirmation message)
                root.destroy()
            else:
                messagebox.showerror("Error", "Failed to save timer.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Invalid time format: {str(e)}")
    
    # Bind Enter key to submit
    entry.bind('<Return>', lambda event: on_submit())
    
    submit_btn = ctk.CTkButton(root, text="Set Timer", command=on_submit, 
                              font=(font_family, 14), 
                              width=150, height=35,
                              corner_radius=10)
    submit_btn.pack(pady=20)
    
    # Add example label
    example_label = ctk.CTkLabel(root, text="Examples: 5h 3m, 1d 5h 3m, 30m, 2h", 
                                font=(font_family, 12), 
                                text_color="gray")
    example_label.pack()
    
    # Run the application
    root.mainloop()

if __name__ == "__main__":
    set_timer()