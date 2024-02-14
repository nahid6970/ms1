import tkinter as tk

def search_and_display():
    search_term = search_entry.get()
    if search_term:
        try:
            with open("D:\\@git\\ms1\\asset\\keybindings.txt", "r+", encoding="utf-8") as file:
                clear_output()
                lines = file.readlines()
                output_text.delete("1.0", tk.END)  # Clear the existing content
                for line in lines:
                    if search_term.lower() in line.lower():
                        output_text.insert(tk.END, line.strip() + "\n")
        except FileNotFoundError:
            print("File not found")

def clear_output():
    output_text.delete("1.0", tk.END)

def save_changes():
    try:
        with open("D:\\@git\\ms1\\asset\\keybindings.txt", "r+", encoding="utf-8") as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if search_entry.get().lower() in line.lower():
                    file.write(output_text.get("1.0", tk.END).strip() + "\n")
                else:
                    file.write(line)
            file.truncate()
    except FileNotFoundError:
        print("File not found")

# Create the Tkinter window
ROOT = tk.Tk()
ROOT.title("Search and Display")

# Create a search entry
search_entry = tk.Entry(ROOT)
search_entry.pack(pady=5)

# Create a search button
search_button = tk.Button(ROOT, text="Search", command=search_and_display)
search_button.pack(pady=5)

# Create a clear button
clear_button = tk.Button(ROOT, text="Clear Output", command=clear_output)
clear_button.pack(pady=5)

# Create a save button
save_button = tk.Button(ROOT, text="Save Changes", command=save_changes)
save_button.pack(pady=5)

# Create an output text box
output_text = tk.Text(ROOT, height=10, width=100, bg="#FFFFFF", fg="#000000", font=("Hack Nerd Font Mono", 10))
output_text.pack(pady=5)

# Run the Tkinter event loop
ROOT.mainloop()
