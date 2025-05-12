import tkinter as tk
from tkinter import ttk
import subprocess

root = tk.Tk()

# Create main frame
main_frame = tk.Frame(root, bg="#1d2027")
main_frame.pack(side="top", anchor="center", pady=(0,0), padx=(0,0))

# Create search button
search_button = tk.Button(main_frame, text="Search", command=lambda: print("Search functionality not yet implemented"))
search_button.grid(row=0, column=0, columnspan=4, pady=(5, 0), padx=(5, 5))

# Create buttons
buttons = [
    ("AlignMultiCoulmnsbySeparator", "\uf037"),
    ("BookmarkLine", "⭐"),
    ("Bookmarklistall", "?⭐"),
    ("BracketsGoTo", "\uebe5")
]

for index, (name, text) in enumerate(buttons):
    row = (index // 4) + 1  # Start from row 1
    col = index % 4
    button = tk.Label(main_frame, bg="#000000", fg="#FFFFFF", height=1, width=20, bd=0, highlightthickness=0, 
                      command=lambda n=name: subprocess.Popen(["powershell", f"python c:/ms1/HotKeys.py {n}"]), text=text)
    button.grid(row=row, column=col, padx=(5, 5), pady=(5, 5))

root.mainloop()
