import tkinter as tk
from random import randint
import pyperclip

def generate_palette():
    # Generate 10 different random color palettes
    palettes = []
    for _ in range(10):
        palette = []
        for _ in range(5):
            # Generate a random RGB color
            color = "#{:02x}{:02x}{:02x}".format(randint(0, 255), randint(0, 255), randint(0, 255))
            palette.append(color)
        palettes.append(palette)
    return palettes

def display_palettes():
    # Clear any existing labels
    for label in palette_labels:
        label.grid_forget()
    
    # Generate and display new palettes
    palettes = generate_palette()
    for i, palette in enumerate(palettes):
        palette_label = tk.Label(root, text=f"Palette {i+1}:", font=("Arial", 12))
        palette_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        for j, color in enumerate(palette):
            color_label = tk.Label(root, text=color, bg=color, font=("Arial", 10), padx=5, pady=2)
            color_label.grid(row=i, column=j+1, padx=5, pady=2)
            color_label.bind("<Button-1>", lambda event, c=color: copy_to_clipboard(c))
            palette_labels.append(color_label)

def copy_to_clipboard(color):
    pyperclip.copy(color)

# Create the main window
root = tk.Tk()
root.title("Random Color Palettes")

# Create a button to generate and display color palettes
generate_button = tk.Button(root, text="Generate Color Palettes", command=display_palettes)
generate_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

# List to store palette labels
palette_labels = []

# Run the Tkinter event loop
root.mainloop()
