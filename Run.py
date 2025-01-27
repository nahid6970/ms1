import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import pickle
import pyperclip  # We will use this library to copy to clipboard

# Initialize the main window
root = tk.Tk()
root.title("File Search and Open in VSCode")
root.geometry("1000x500")  # Extended window for initial suggestions
root.resizable(False, False)

# Directories to search
directories = [
    "C:/ms1/",
    "C:/ms2/",
    "C:/ms3/",
    "C:/msBackups/",
]

# Load or initialize file usage counter
def load_usage_data():
    usage_data_file = r"C:\Users\nahid\file_usage_data.pkl"
    if os.path.exists(usage_data_file):
        with open(usage_data_file, "rb") as f:
            return pickle.load(f)
    return Counter()

def save_usage_data():
    with open(r"C:\Users\nahid\file_usage_data.pkl", "wb") as f:
        pickle.dump(file_usage_counter, f)

# Clear usage data
def clear_usage_data():
    file_usage_counter.clear()
    save_usage_data()
    show_top_files()


# Show most opened files
def show_top_files():
    suggestions_list.delete(0, tk.END)
    top_files = file_usage_counter.most_common(10)

    if top_files:
        for file, _ in top_files:
            suggestions_list.insert(tk.END, file)
        suggestions_list.select_set(0)  # Automatically select the first item
        suggestions_list.focus_set()  # Set focus to the Listbox
    else:
        suggestions_list.insert(tk.END, "No files opened yet")
    
    # Refocus on the search bar to allow typing
    search_bar.focus_set()

# Perform search
def perform_search(event):
    query = search_var.get().lower()
    suggestions_list.delete(0, tk.END)

    if not query:
        status_label.config(text="Most opened files:")
        show_top_files()
        return

    results = []
    search_terms = query.split()  # Split the query into separate words

    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                # Check if all search terms are present in the path (directory + filename)
                full_path = os.path.join(root, file)
                if all(term in full_path.lower() for term in search_terms):
                    # Normalize the path to use backslashes and keep original case
                    results.append(os.path.normpath(full_path))
    if results:
        status_label.config(text=f"{len(results)} file(s) found")
        for result in results:
            suggestions_list.insert(tk.END, result)
        suggestions_list.select_set(0)  # Automatically select the first item
        suggestions_list.focus_set()  # Set focus to the Listbox
    else:
        status_label.config(text="No files found")
        suggestions_list.insert(tk.END, "No matches found")
    
    # Refocus on the search bar to allow typing
    search_bar.focus_set()


# Open selected file with the appropriate application
def open_selected_file(event):
    try:
        selected = suggestions_list.get(suggestions_list.curselection())
        selected = os.path.normpath(selected)
        
        # Get the file extension
        file_extension = os.path.splitext(selected)[1].lower()
        
        # Open file with the appropriate application based on extension
        if file_extension == '.xls' or file_extension == '.xlsx':
            # Open Excel file
            subprocess.run(["start", "excel", selected], shell=True, check=True)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Open image file with Photos app (Windows)
            subprocess.run(["start", "mspaint", selected], shell=True, check=True)
        else:
            # Open all other files in VSCode
            subprocess.run(["code", selected], shell=True, check=True)

        # Update file usage counter and save
        root.quit()
        file_usage_counter[selected] += 1
        save_usage_data()

    except IndexError:
        messagebox.showwarning("No Selection", "Please select a file to open.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# Copy selected file path to clipboard
def copy_to_clipboard(event):
    try:
        selected = suggestions_list.get(suggestions_list.curselection())
        pyperclip.copy(selected)  # Copy file path to clipboard
        messagebox.showinfo("Copied", f"File path copied to clipboard:\n{selected}")
    except IndexError:
        messagebox.showwarning("No Selection", "Please select a file to copy.")

# Initialize file usage data
file_usage_counter = load_usage_data()

# Top buttons frame
top_buttons_frame = ttk.Frame(root)
top_buttons_frame.pack(anchor="e" ,padx=10, pady=5)


# Create the Close GUI label
close_label = tk.Label(
    top_buttons_frame, 
    text="\uf2d3",  # FontAwesome or icon text
    font=("JetBrainsMono NF", 16),
    fg="red",
    relief="flat",
)
close_label.pack(side=tk.RIGHT, padx=5)
close_label.bind("<Button-1>", lambda e: root.quit())

# Create the Clear Usage Data label
clear_label = tk.Label(
    top_buttons_frame, 
    text="\udb85\ude35",  # Unicode character
    font=("JetBrainsMono NF", 16),
    fg="red",
    relief="flat",
)
clear_label.pack(side=tk.RIGHT, padx=5)
clear_label.bind("<Button-1>", lambda e: clear_usage_data())


# Create the search bar with tk.Entry instead of ttk.Entry
search_var = tk.StringVar()
search_bar = tk.Entry(root, textvariable=search_var, font=("JetBrainsMono nfp", 12), bg="#c0c8f3", fg="#000000")
search_bar.pack(fill=tk.X, padx=10, pady=10)
search_bar.bind("<KeyRelease>", perform_search)
search_bar.bind("<Return>", open_selected_file)
search_bar.focus_set()


# Suggestions listbox
suggestions_list = tk.Listbox(
    root,
    font=("JetBrainsMono nfp", 12),
    height=5,
    bg="#282a36",
    fg="#FFFFFF",
    selectbackground="#282a36",
    selectforeground="#FFFFFF"
)
suggestions_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
suggestions_list.bind("<Double-1>", open_selected_file)
suggestions_list.bind("<Return>", open_selected_file)

# Status label
status_label = ttk.Label(root, text="Most opened files:", font=("JetBrainsMono nfp", 10), anchor="w")
status_label.pack(fill=tk.X, padx=10, pady=5)

# Show top files initially
show_top_files()

# Configure root window
root.overrideredirect(True)  # Remove default borders
root.update_idletasks()
root.configure(bg="#4c44cb")
root.attributes('-topmost', True)
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Bind Ctrl+C to the copy_to_clipboard function
root.bind('<Control-c>', copy_to_clipboard)

# Main loop
root.mainloop()
