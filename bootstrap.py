import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Scrollbar
from ttkbootstrap.constants import *

root = tk.Tk()
root.title("Scrollbar Example")

# Create a frame to contain the buttons
frame = ttk.Frame(root)
frame.pack(fill="both", expand=True)

# Create a canvas inside the frame
canvas = tk.Canvas(frame)
canvas.pack(side="left", fill="both", expand=True)

# Add a default round scrollbar to the frame
scrollbar = Scrollbar(frame, bootstyle="round", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.config(yscrollcommand=scrollbar.set)

# Create another frame inside the canvas to hold the buttons
button_frame = ttk.Frame(canvas)
canvas.create_window((0,0), window=button_frame, anchor="nw")

# Function to resize the canvas scroll region
def resize(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Bind the resize function to canvas resize
canvas.bind("<Configure>", resize)

# Create buttons inside the button frame
buttons = []
for i in range(20):
    button = ttk.Button(button_frame, text=f"Button {i+1}", bootstyle=PRIMARY)
    button.pack(fill="x", padx=5, pady=5)
    buttons.append(button)

root.mainloop()
