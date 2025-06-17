import tkinter as tk
from tkinter import font, colorchooser, messagebox
import pyperclip

class FontPreviewer:
    def __init__(self, master):
        self.master = master
        master.title("Font Previewer")
        master.geometry("600x700") # Set a default window size

        self.create_widgets()
        self.populate_font_list()
        self.bind_events()

    def create_widgets(self):
        # --- Input and Output Sections ---
        input_frame = tk.Frame(self.master, padx=10, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Enter Text:").pack(side=tk.LEFT)
        self.input_text = tk.Entry(input_frame, width=40)
        self.input_text.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.input_text.insert(0, "The quick brown fox jumps over the lazy dog.")
        self.input_text.bind("<KeyRelease>", self.update_text)

        self.output_text = tk.Label(self.master, text="Select a font to preview",
                                    font=("Arial", 12), width=50, height=2,
                                    relief="groove", highlightthickness=1,
                                    highlightbackground="#76acfa", padx=5, pady=5)
        self.output_text.pack(pady=10, fill=tk.X, padx=10)

        # --- Font Selection Section ---
        font_selection_frame = tk.Frame(self.master, padx=10, pady=5)
        font_selection_frame.pack(fill=tk.BOTH, expand=True)

        # Search box
        search_frame = tk.Frame(font_selection_frame)
        search_frame.pack(fill=tk.X, pady=5)
        tk.Label(search_frame, text="Search Font:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_fonts)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Font listbox with scrollbar
        listbox_frame = tk.Frame(font_selection_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.font_listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE,
                                       exportselection=False, yscrollcommand=scrollbar.set,
                                       width=40, height=15)
        self.font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.font_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Style Options Section ---
        style_frame = tk.LabelFrame(self.master, text="Text Styles", padx=10, pady=10)
        style_frame.pack(fill=tk.X, padx=10, pady=5)

        self.bold_var = tk.BooleanVar()
        self.italic_var = tk.BooleanVar()
        self.underline_var = tk.BooleanVar()
        self.strikethrough_var = tk.BooleanVar()

        tk.Checkbutton(style_frame, text="Bold", variable=self.bold_var, command=self.update_text).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        tk.Checkbutton(style_frame, text="Italic", variable=self.italic_var, command=self.update_text).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        tk.Checkbutton(style_frame, text="Underline", variable=self.underline_var, command=self.update_text).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        tk.Checkbutton(style_frame, text="Strikethrough", variable=self.strikethrough_var, command=self.update_text).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        # --- Color Options Section ---
        color_frame = tk.LabelFrame(self.master, text="Colors", padx=10, pady=10)
        color_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(color_frame, text="Background Color:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.bg_entry = tk.Entry(color_frame, width=10)
        self.bg_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        self.bg_entry.insert(tk.END, "#FFFFFF")
        tk.Button(color_frame, text="Choose", command=self.choose_bg_color).grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        self.bg_entry.bind("<KeyRelease>", self.update_text)


        tk.Label(color_frame, text="Foreground Color:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.fg_entry = tk.Entry(color_frame, width=10)
        self.fg_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        self.fg_entry.insert(tk.END, "#000000")
        tk.Button(color_frame, text="Choose", command=self.choose_fg_color).grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        self.fg_entry.bind("<KeyRelease>", self.update_text)

        # --- Action Buttons ---
        button_frame = tk.Frame(self.master, padx=10, pady=10)
        button_frame.pack(fill=tk.X)

        tk.Button(button_frame, text="Copy Font Family", command=self.copy_font_family).pack(side=tk.LEFT, expand=True)

    def populate_font_list(self):
        self.font_list = sorted(font.families())
        for item in self.font_list:
            self.font_listbox.insert(tk.END, item)
        if self.font_list:
            self.font_listbox.selection_set(0) # Select the first font by default
            self.update_text()

    def bind_events(self):
        self.font_listbox.bind("<<ListboxSelect>>", self.update_text)
        self.font_listbox.bind("<Up>", self.on_arrow_key)
        self.font_listbox.bind("<Down>", self.on_arrow_key)

    def update_text(self, event=None):
        text = self.input_text.get()
        if not text:
            text = " " # Ensure there's always some text to display for styling

        selected_index = self.font_listbox.curselection()
        if not selected_index:
            self.output_text.config(text="Please select a font family", font=("Arial", 12))
            return

        font_family = self.font_listbox.get(selected_index[0])
        style = ""
        if self.bold_var.get():
            style += "bold "
        if self.italic_var.get():
            style += "italic "
        if self.underline_var.get():
            style += "underline "
        if self.strikethrough_var.get():
            style += "overstrike "

        bg_color = self.bg_entry.get()
        fg_color = self.fg_entry.get()

        try:
            self.output_text.config(text=text, font=(font_family, 12, style), bg=bg_color, fg=fg_color)
        except tk.TclError as e:
            # Catch errors related to invalid color codes
            messagebox.showerror("Color Error", f"Invalid color code: {e}")
            # Reset colors to default or previous valid state if an error occurs
            self.bg_entry.delete(0, tk.END)
            self.bg_entry.insert(tk.END, "#FFFFFF")
            self.fg_entry.delete(0, tk.END)
            self.fg_entry.insert(tk.END, "#000000")
            self.output_text.config(bg="#FFFFFF", fg="#000000")
            self.update_text() # Re-apply valid settings


    def filter_fonts(self, *args):
        query = self.search_var.get().lower()
        self.font_listbox.delete(0, tk.END)
        for item in self.font_list:
            if query in item.lower():
                self.font_listbox.insert(tk.END, item)
        if self.font_listbox.size() > 0:
            self.font_listbox.selection_set(0) # Select the first item in the filtered list
            self.font_listbox.see(0) # Scroll to the top

    def on_arrow_key(self, event):
        current_index_tuple = self.font_listbox.curselection()
        if not current_index_tuple:
            return "break" # No selection, do nothing

        current_index = current_index_tuple[0]

        if event.keysym == 'Up':
            if current_index > 0:
                self.font_listbox.selection_clear(current_index)
                self.font_listbox.selection_set(current_index - 1)
                self.font_listbox.see(current_index - 1)
                self.update_text()
            return "break"
        elif event.keysym == 'Down':
            if current_index < self.font_listbox.size() - 1:
                self.font_listbox.selection_clear(current_index)
                self.font_listbox.selection_set(current_index + 1)
                self.font_listbox.see(current_index + 1)
                self.update_text()
            return "break"

    def copy_font_family(self):
        selected_index = self.font_listbox.curselection()
        if selected_index:
            font_family = self.font_listbox.get(selected_index[0])
            pyperclip.copy(font_family)
            messagebox.showinfo("Copied!", f"'{font_family}' copied to clipboard.")
        else:
            messagebox.showwarning("No Selection", "No font family selected to copy.")

    def choose_bg_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.bg_entry.delete(0, tk.END)
            self.bg_entry.insert(tk.END, color)
            self.update_text()

    def choose_fg_color(self):
        color = colorchooser.askcolor(title="Choose Foreground Color")[1]
        if color:
            self.fg_entry.delete(0, tk.END)
            self.fg_entry.insert(tk.END, color)
            self.update_text()

if __name__ == "__main__":
    root = tk.Tk()
    app = FontPreviewer(root)
    root.mainloop()