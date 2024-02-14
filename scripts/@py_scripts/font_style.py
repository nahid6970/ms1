import tkinter as tk
from tkinter import font
import pyperclip

def update_text(event=None):
    text = input_text.get()
    selected_index = font_listbox.curselection()
    if selected_index:  # Check if an item is selected
        font_family = font_listbox.get(selected_index[0])
        # Update the style string based on the selected checkboxes
        style = ""
        if bold_var.get():
            style += "bold "
        if italic_var.get():
            style += "italic "
        if underline_var.get():
            style += "underline "
        if strikethrough_var.get():
            style += "overstrike "
            
        output_text.config(text=text, font=(font_family, 12, style))
    else:
        output_text.config(text="Please select a font family", font=("Arial", 12))

def filter_fonts(*args):
    query = search_var.get().lower()
    font_listbox.delete(0, tk.END)
    for item in font_list:
        if query in item.lower():
            font_listbox.insert(tk.END, item)

# Keyboard arrow key navigation
def on_arrow_key(event):
    if event.keysym == 'Up':
        current_index = font_listbox.curselection()[0]
        if current_index > 0:
            font_listbox.selection_clear(current_index)
            font_listbox.selection_set(current_index - 1)
            font_listbox.see(current_index - 1)
            update_text()
        return "break"  # Prevent default behavior
    elif event.keysym == 'Down':
        current_index = font_listbox.curselection()[0]
        if current_index < font_listbox.size() - 1:
            font_listbox.selection_clear(current_index)
            font_listbox.selection_set(current_index + 1)
            font_listbox.see(current_index + 1)
            update_text()
        return "break"  # Prevent default behavior

def copy_font_family():
    selected_index = font_listbox.curselection()
    if selected_index:  # Check if an item is selected
        font_family = font_listbox.get(selected_index[0])
        pyperclip.copy(font_family)
        print("Font family copied:", font_family)
    else:
        print("No font family selected.")

# Create the Tkinter window
root = tk.Tk()
root.title("Font Preview")

# Create input text box
input_text = tk.Entry(root, width=30)
input_text.pack(pady=10)

# Create font listbox with scrollbar
font_list = sorted(font.families())
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL)
font_listbox = tk.Listbox(root, selectmode=tk.SINGLE, exportselection=False, yscrollcommand=scrollbar.set, width=30)
for item in font_list:
    font_listbox.insert(tk.END, item)
font_listbox.pack(side=tk.LEFT, padx=10)
scrollbar.config(command=font_listbox.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)

# Create search box
search_var = tk.StringVar()
search_var.trace_add('write', filter_fonts)
search_entry = tk.Entry(root, textvariable=search_var, width=30)
search_entry.pack(pady=5)

# Bind the update_text function to the ListboxSelect event
font_listbox.bind("<<ListboxSelect>>", update_text)

# Bind arrow key events to navigate the font listbox
font_listbox.bind("<Up>", on_arrow_key)
font_listbox.bind("<Down>", on_arrow_key)

# Create output text label
output_text = tk.Label(root, text="Please select a font family", font=("Arial", 12), width=30, height=1, relief="flat", highlightthickness=1, highlightbackground="#76acfa", padx=1, pady=0)
output_text.pack(pady=10)

# Create checkboxes for bold and italic styles
bold_var = tk.BooleanVar()
italic_var = tk.BooleanVar()
underline_var = tk.BooleanVar()
strikethrough_var = tk.BooleanVar()

bold_check = tk.Checkbutton(root, text="Bold", variable=bold_var, command=update_text)
italic_check = tk.Checkbutton(root, text="Italic", variable=italic_var, command=update_text)
bold_check.pack(side=tk.RIGHT, padx=5, pady=5)
italic_check.pack(side=tk.RIGHT, padx=5, pady=5)

# Create checkboxes for underline and strikethrough styles
underline_check = tk.Checkbutton(root, text="Underline", variable=underline_var, command=update_text)
strikethrough_check = tk.Checkbutton(root, text="Strikethrough", variable=strikethrough_var, command=update_text)
underline_check.pack(side=tk.RIGHT, padx=5, pady=5)
strikethrough_check.pack(side=tk.RIGHT, padx=5, pady=5)

# Create a "Copy" button
copy_button = tk.Button(root, text="Copy Font Family", command=copy_font_family)
copy_button.pack(pady=5)

# Run the Tkinter event loop
root.mainloop()
