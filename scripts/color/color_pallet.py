import tkinter as tk
from tkinter import Scrollbar, Canvas
from random import randint
import pyperclip

def generate_palette_colors():
    """Generates 10 different random color palettes."""
    palettes = []
    for _ in range(10):
        palette = []
        for _ in range(5):
            color = "#{:02x}{:02x}{:02x}".format(randint(0, 255), randint(0, 255), randint(0, 255))
            palette.append(color)
        palettes.append(palette)
    return palettes

def get_text_color(hex_color):
    """Determines black or white text color based on background luminance."""
    hex_color_val = hex_color.lstrip('#')
    r, g, b = int(hex_color_val[0:2], 16), int(hex_color_val[2:4], 16), int(hex_color_val[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#ffffff" if luminance < 0.5 else "#000000"

def copy_to_clipboard(color_value, include_hash=False):
    """
    Copies a color value to the clipboard.
    If include_hash is True, copies with '#'. Otherwise, copies without '#'.
    """
    if include_hash:
        pyperclip.copy(color_value)
        show_copy_feedback(f"Copied with #: {color_value}")
    else:
        pyperclip.copy(color_value[1:]) # Remove '#'
        show_copy_feedback(f"Copied without #: {color_value[1:]}")

def show_copy_feedback(message):
    """Displays temporary feedback when a color is copied."""
    feedback_label.config(text=message, fg="blue")
    root.after(1500, lambda: feedback_label.config(text="", fg="black")) # Clear after 1.5 seconds

def display_palettes():
    """Generates and displays new palettes in the scrollable frame."""
    # Clear existing palette widgets from the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    palettes = generate_palette_colors()
    for i, palette in enumerate(palettes):
        palette_frame = tk.Frame(scrollable_frame, bd=2, relief="flat", padx=10, pady=5)
        palette_frame.grid(row=i, column=0, pady=5, sticky="ew")
        scrollable_frame.grid_columnconfigure(0, weight=1)

        # Color display - directly placed without a header frame
        colors_display_frame = tk.Frame(palette_frame)
        colors_display_frame.pack(fill="x")

        for j, color in enumerate(palette):
            text_color = get_text_color(color)
            color_label = tk.Label(colors_display_frame, text=color, bg=color, font=("jetbrainsmono nfp", 10), padx=8, pady=4, relief="flat", bd=1)
            color_label.config(fg=text_color)
            color_label.pack(side="left", padx=3, expand=True, fill="x")
            
            # Bind left-click to copy without hash
            color_label.bind("<Button-1>", lambda event, c=color: copy_to_clipboard(c, include_hash=False))
            # Bind right-click to copy with hash
            color_label.bind("<Button-3>", lambda event, c=color: copy_to_clipboard(c, include_hash=True))

    # Update scroll region
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# --- Main Window Setup ---
root = tk.Tk()
root.title("Random Color Palettes Generator")
root.geometry("800x600") # Set initial window size

# Main frame for overall layout
main_frame = tk.Frame(root, padx=15, pady=0)
main_frame.pack(fill="both", expand=True)

# Generate button
generate_button = tk.Button(main_frame, text="Generate New Palettes", command=display_palettes,
                            font=("jetbrainsmono nfp", 14, "bold"), bg="#4CAF50", fg="white", activebackground="#45a049", activeforeground="white")
generate_button.pack(pady=0, fill="x")

# Feedback label for copy actions
feedback_label = tk.Label(main_frame, text="", font=("jetbrainsmono nfp", 10, "italic"))
feedback_label.pack(pady=(0, 10))

# Scrollable area for palettes
canvas = Canvas(main_frame, borderwidth=0, background="#f0f0f0")
vertical_scrollbar = Scrollbar(main_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vertical_scrollbar.set)

vertical_scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scrollable_frame = tk.Frame(canvas, background="#f0f0f0")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

# Configure canvas to resize the scrollable frame
scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas.create_window((0, 0), window=scrollable_frame, anchor="nw"), width=e.width))

# Initial display of palettes
display_palettes()

root.mainloop()