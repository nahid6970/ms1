import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import pickle
import pyperclip  # We will use this library to copy to clipboard

BOOKMARKS_FILE = r"C:\Users\nahid\bookmarks.pkl"

def load_bookmarks():
    if os.path.exists(BOOKMARKS_FILE):
        with open(BOOKMARKS_FILE, "rb") as f:
            return pickle.load(f)
    return []

def save_bookmarks(bookmarks):
    with open(BOOKMARKS_FILE, "wb") as f:
        pickle.dump(bookmarks, f)

# Load bookmarks on startup
bookmarks = load_bookmarks()

def create_custom_border(parent):
    BORDER_FRAME = tk.Frame(parent, bg="#4c44cb", bd=0, highlightthickness=1, highlightbackground="#fb674b")
    BORDER_FRAME.place(relwidth=1, relheight=1)
    return BORDER_FRAME

# Initialize the main window
root = tk.Tk()
root.title("File Search and Open in VSCode")
root.geometry("1000x500")
root.resizable(False, False)
BORDER_FRAME = create_custom_border(root)

# Directories to search
directories = [
    "C:/ms1/",
    "C:/ms2/",
    "C:/ms3/",
    "C:/msBackups/",
]

# Flag to indicate if we are viewing bookmarks
viewing_bookmarks = False
# Global list to store full paths corresponding to listbox items
current_file_paths = []

# A label to display the full path (place it wherever you like)
path_label = ttk.Label(root, text="", font=("JetBrainsMono nfp", 10, "bold"), foreground="#060efe", anchor="w")
path_label.pack(padx=10, pady=5, fill=tk.X)

# Update the path label based on the current selection in the listbox
def update_path_label(event=None):
    selected_indices = suggestions_list.curselection()
    if selected_indices:
        index = selected_indices[0]
        if index < len(current_file_paths):
            full_path = current_file_paths[index]
            path_label.config(text=full_path)

# Perform search and populate the listbox with only filenames (plus a star if bookmarked)
def perform_search(event):
    global viewing_bookmarks, current_file_paths
    if viewing_bookmarks:
        return  # Do nothing if we are viewing bookmarks

    query = search_var.get().lower()
    suggestions_list.delete(0, tk.END)
    current_file_paths = []

    if not query:
        status_label.config(text="Enter search text")
        return

    results = []
    search_terms = query.split()
    for directory in directories:
        for r, _, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(r, file)
                if all(term in full_path.lower() for term in search_terms):
                    results.append(os.path.normpath(full_path))
    if results:
        status_label.config(text=f"{len(results)} file(s) found")
        for full_path in results:
            current_file_paths.append(full_path)
            file_name = os.path.basename(full_path)
            star = " ★" if full_path in bookmarks else ""
            suggestions_list.insert(tk.END, file_name + star)
        suggestions_list.select_set(0)
        suggestions_list.focus_set()
        update_path_label()
    else:
        status_label.config(text="No files found")
        suggestions_list.insert(tk.END, "No matches found")
    search_bar.focus_set()

# Function to display bookmarks (only filename with a star) in the listbox
def show_bookmarks():
    global viewing_bookmarks
    viewing_bookmarks = True  # Ensure it stays in bookmarks mode
    suggestions_list.delete(0, tk.END)
    
    if bookmarks:
        for bm in bookmarks:
            suggestions_list.insert(tk.END, bm)
        suggestions_list.select_set(0)
        suggestions_list.focus_set()
    else:
        suggestions_list.insert(tk.END, "No bookmarks found")

    search_bar.focus_set()

def reset_viewing_bookmarks(event):
    global viewing_bookmarks
    viewing_bookmarks = False

# Open selected file with the appropriate application
def open_selected_file(event):
    try:
        selected_index = suggestions_list.curselection()[0]
        if selected_index < len(current_file_paths):
            selected = current_file_paths[selected_index]
        else:
            return
        selected = os.path.normpath(selected)
        file_extension = os.path.splitext(selected)[1].lower()

        if file_extension in ['.xls', '.xlsx']:
            subprocess.run(["start", "excel", selected], shell=True, check=True)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            subprocess.run(["start", "mspaint", selected], shell=True, check=True)
        elif file_extension == '.exe':
            subprocess.Popen([selected], shell=True)
        else:
            subprocess.run(["code", selected], shell=True, check=True)

        root.quit()
    except IndexError:
        messagebox.showwarning("No Selection", "Please select a file to open.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Copy selected file path to clipboard
def copy_to_clipboard(event):
    try:
        selected_index = suggestions_list.curselection()[0]
        if selected_index < len(current_file_paths):
            selected = current_file_paths[selected_index]
            pyperclip.copy(selected)
            messagebox.showinfo("Copied", f"File path copied to clipboard:\n{selected}")
    except IndexError:
        messagebox.showwarning("No Selection", "Please select a file to copy.")

# Bookmark the selected file
def bookmark_file(event):
    try:
        selected_index = suggestions_list.curselection()[0]
        if selected_index < len(current_file_paths):
            selected = current_file_paths[selected_index]
            selected = os.path.normpath(selected)
            if selected not in bookmarks:
                bookmarks.append(selected)
                save_bookmarks(bookmarks)
                messagebox.showinfo("Bookmarked", f"Bookmarked:\n{selected}")
                # Update the display in the listbox if needed
                update_display_for_index(selected_index)
            else:
                messagebox.showinfo("Already Bookmarked", "This file is already bookmarked.")
    except IndexError:
        messagebox.showwarning("No Selection", "Please select a file to bookmark.")

def update_display_for_index(index):
    """Refresh the listbox display for one item if it has been bookmarked."""
    if index < len(current_file_paths):
        full_path = current_file_paths[index]
        file_name = os.path.basename(full_path)
        star = " ★" if full_path in bookmarks else ""
        suggestions_list.delete(index)
        suggestions_list.insert(index, file_name + star)
        suggestions_list.select_set(index)

# Top buttons frame
top_buttons_frame = tk.Frame(root, bg="#4c44cb")
top_buttons_frame.pack(anchor="e", padx=10, pady=5)

close_label = tk.Label(top_buttons_frame, text="\uf2d3", font=("JetBrainsMono NFP", 16), fg="#ffffff", bg="#4c44cb", relief="flat")
close_label.pack(side=tk.RIGHT, padx=5)
close_label.bind("<Button-1>", lambda e: root.quit())

def clear_bookmarks():
    global bookmarks
    if messagebox.askyesno("Clear Bookmarks", "Are you sure you want to clear all bookmarks?"):
        bookmarks = []
        save_bookmarks(bookmarks)
        if viewing_bookmarks:
            suggestions_list.delete(0, tk.END)
            suggestions_list.insert(tk.END, "No bookmarks found")

clear_bm_label = tk.Label(top_buttons_frame, text="\u232b", font=("JetBrainsMono NFP", 16), fg="#ffffff", bg="#4c44cb", relief="flat")
clear_bm_label.pack(side=tk.RIGHT, padx=5)
clear_bm_label.bind("<Button-1>", lambda e: clear_bookmarks())

# Navigation functions
def focus_suggestions(event):
    if suggestions_list.size() > 0:
        suggestions_list.focus_set()
        suggestions_list.select_set(0)

def navigate_up(event):
    selected_index = suggestions_list.curselection()
    if selected_index:
        current_index = selected_index[0]
        if current_index == 0:  # If already at the first item
            search_bar.focus_set()  # Move focus to the search bar
            search_bar.icursor(tk.END)  # Place the cursor at the end of the text
        else:
            suggestions_list.select_clear(current_index)
            suggestions_list.select_set(current_index - 0)  # Move selection up
            suggestions_list.activate(current_index - 0)  # Highlight the new selection
    else:
        # If no selection, just select the last item
        suggestions_list.select_set(suggestions_list.size() - 1)

# Navigate through the list with Down Arrow
def navigate_down(event):
    selected_index = suggestions_list.curselection()
    if selected_index:
        current_index = selected_index[0]
        if current_index < suggestions_list.size() - 1:  # If not the last item
            suggestions_list.select_clear(current_index)
            suggestions_list.select_set(current_index + 0)  # Move selection down
            suggestions_list.activate(current_index + 0)  # Highlight the new selection

# Create search bar
search_var = tk.StringVar()
search_bar = tk.Entry(root, textvariable=search_var, font=("JetBrainsMono nfp", 12), bg="#c0c8f3", fg="#000000")
search_bar.pack(fill=tk.X, padx=10, pady=10)
search_bar.bind("<KeyRelease>", perform_search)
search_bar.bind("<Return>", open_selected_file)
search_bar.bind("<Down>", focus_suggestions)
search_bar.bind("<Key>", reset_viewing_bookmarks)
search_bar.focus_set()

# Suggestions listbox (shows only filenames)
suggestions_list = tk.Listbox(root, font=("JetBrainsMono nfp", 12), height=10, bg="#282a36", fg="#93eea2",
                             selectbackground="#282a36", selectforeground="#FFFFFF")
suggestions_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
suggestions_list.bind("<Double-1>", open_selected_file)
suggestions_list.bind("<Return>", open_selected_file)
suggestions_list.bind("<<ListboxSelect>>", update_path_label)
suggestions_list.bind("<Up>", navigate_up)
suggestions_list.bind("<Down>", navigate_down)

# Status label
status_label = ttk.Label(root, text="", width=50, font=("JetBrainsMono nfp", 10, "bold"), foreground="#060efe", anchor="n")
status_label.pack(padx=10, pady=5)

# Configure root window
root.overrideredirect(True)
root.update_idletasks()
root.attributes('-topmost', True)
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Key Bindings
root.bind('<Control-c>', copy_to_clipboard)
root.bind("<Escape>", lambda e: root.destroy())

# Binding for bookmarking:
# Press 'F2' to bookmark the currently selected file
root.bind("<F1>", bookmark_file)
# Press 'F1' to show all bookmarks
root.bind("<F2>", lambda e: show_bookmarks())

# Bind keys from 'a' to 'z' (lowercase and uppercase) and Backspace to focus on the search bar
for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
    root.bind(f"<Key-{char}>", lambda e: search_bar.focus_set())

root.bind("<BackSpace>", lambda e: search_bar.focus_set())

root.mainloop()
