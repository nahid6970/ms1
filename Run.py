import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
import pickle

class FileSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Search and Open in VSCode")
        self.root.geometry("600x400")  # Extended window for initial suggestions
        self.root.resizable(False, False)

        # Directories to search
        self.directories = [
            "C:/ms1/",  # Example directory
            "C:/ms2/",  # Example directory
            "C:/ms3/",  # Example directory
        ]

        # Load or initialize file usage counter
        self.usage_data_file = r"C:\Users\nahid\file_usage_data.pkl"
        self.file_usage_counter = self.load_usage_data()

        # Search bar
        self.search_var = tk.StringVar()
        self.search_bar = ttk.Entry(root, textvariable=self.search_var, font=("JetBrainsmono nfp", 12))
        self.search_bar.pack(fill=tk.X, padx=10, pady=10)
        self.search_bar.bind("<KeyRelease>", self.perform_search)
        self.search_bar.bind("<Return>", self.open_selected_file)

        # Automatically focus on the search bar
        self.search_bar.focus_set()

        # Listbox for suggestions (always shown for top suggestions)
        self.suggestions_list = tk.Listbox(
            root,
            font=("JetBrainsMono nfp", 12),
            height=5,
            bg="#282a36",      # Set background color to black
            fg="white",       # Set foreground (text) color to white
            selectbackground="white",  # Set background color for selected item
            selectforeground="blue"   # Set foreground (text) color for selected item

        )
        self.suggestions_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.suggestions_list.bind("<Double-1>", self.open_selected_file)


        # Status label
        self.status_label = ttk.Label(root, text="Most opened files:", font=("JetBrainsMono nfp", 10), anchor="w")
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

        # Show most opened files initially
        self.show_top_files()

    def load_usage_data(self):
        if os.path.exists(self.usage_data_file):
            with open(self.usage_data_file, "rb") as f:
                return pickle.load(f)
        return Counter()

    def save_usage_data(self):
        with open(self.usage_data_file, "wb") as f:
            pickle.dump(self.file_usage_counter, f)

    def show_top_files(self):
        self.suggestions_list.delete(0, tk.END)
        top_files = self.file_usage_counter.most_common(10)

        if top_files:
            for file, _ in top_files:
                self.suggestions_list.insert(tk.END, file)
        else:
            self.suggestions_list.insert(tk.END, "No files opened yet")

    def perform_search(self, event):
        query = self.search_var.get().lower()
        self.suggestions_list.delete(0, tk.END)

        if not query:
            self.status_label.config(text="Most opened files:")
            self.show_top_files()
            return

        results = []
        for directory in self.directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    if query in file.lower():
                        full_path = os.path.join(root, file)
                        results.append(os.path.normpath(full_path))  # Normalize the path

        if results:
            self.status_label.config(text=f"{len(results)} file(s) found")
            for result in results:
                self.suggestions_list.insert(tk.END, result)
        else:
            self.status_label.config(text="No files found")
            self.suggestions_list.insert(tk.END, "No matches found")

    def open_selected_file(self, event):
        try:
            selected = self.suggestions_list.get(self.suggestions_list.curselection())
            # Normalize the selected file path
            selected = os.path.normpath(selected)
            
            # Run the subprocess to open the file in VSCode
            subprocess.run(["code", selected], shell=True, check=True)
            
            # Close the GUI after opening the file
            self.root.quit()  # This will close the Tkinter window
            
            # Update the usage counter and save
            self.file_usage_counter[selected] += 1
            self.save_usage_data()
        except IndexError:
            messagebox.showwarning("No Selection", "Please select a file to open.")
        except Exception as e:
            messagebox.showerror("Error", str(e))



if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(root)
    root.update_idletasks()
    root.configure(bg="#9aa1ff")
    root.attributes('-topmost', True)  # Set always on top
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.mainloop()