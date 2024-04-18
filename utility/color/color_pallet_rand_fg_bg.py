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

def calculate_text_color(bg_color, fg_color):
    # Calculate the relative luminance of a color
    r_bg, g_bg, b_bg = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
    luminance_bg = (0.299 * r_bg + 0.587 * g_bg + 0.114 * b_bg) / 255

    # Calculate the relative luminance of the foreground color
    r_fg, g_fg, b_fg = tuple(int(fg_color[i:i+2], 16) for i in (1, 3, 5))
    luminance_fg = (0.299 * r_fg + 0.587 * g_fg + 0.114 * b_fg) / 255

    # Adjust the foreground color to ensure sufficient contrast
    if luminance_fg < 0.5:
        fg_color = "#ffffff"  # If foreground color is dark, set it to white
    else:
        fg_color = "#000000"  # If foreground color is light, set it to black

    return fg_color

def display_palettes():
    # Clear any existing labels
    for label in palette_labels:
        label.grid_forget()
    
    # Generate and display new palettes
    palettes = generate_palette()
    for i, palette in enumerate(palettes):
        palette_label = tk.Label(root, text=f"Palette {i+1}:", font=("Arial", 12))
        palette_label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        for j, bg_color in enumerate(palette):
            # Generate a random foreground color
            fg_color = "#{:02x}{:02x}{:02x}".format(randint(0, 255), randint(0, 255), randint(0, 255))
            # Determine text color based on background color
            text_color = calculate_text_color(bg_color, fg_color)
            color_label = tk.Label(root, text=bg_color, bg=bg_color, fg=text_color, font=("Arial", 10), padx=5, pady=2)
            color_label.grid(row=i, column=j+1, padx=5, pady=2)
            color_label.bind("<Button-1>", lambda event, bg=bg_color, fg=fg_color: copy_to_clipboard(bg, fg))
            palette_labels.append(color_label)

def copy_to_clipboard(bg_color, fg_color):
    pyperclip.copy(f"bg={bg_color} fg={fg_color}")

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
