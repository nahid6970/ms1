import tkinter as tk
from PyDictionary import PyDictionary

def get_meaning():
    word = word_entry.get()
    dictionary = PyDictionary()

    meaning = dictionary.meaning(word)
    if meaning:
        simplified_meaning = '\n'.join([f"{part}: {', '.join(definitions)}" for part, definitions in meaning.items()])
        meaning_text.delete(1.0, tk.END)
        meaning_text.insert(tk.END, simplified_meaning)
    else:
        meaning_text.delete(1.0, tk.END)
        meaning_text.insert(tk.END, "Word not found in the dictionary.")

# Create tkinter window
root = tk.Tk()
root.title("Dictionary")

# Create frames
top_frame = tk.Frame(root)
top_frame.pack()

bottom_frame = tk.Frame(root)
bottom_frame.pack()

# Create labels
word_label = tk.Label(top_frame, text="Word:")
word_label.grid(row=0, column=0)

meaning_label = tk.Label(top_frame, text="Meaning:")
meaning_label.grid(row=1, column=0)

# Create entry boxes
word_entry = tk.Entry(top_frame, width=30)
word_entry.grid(row=0, column=1)

meaning_text = tk.Text(bottom_frame, height=10, width=40)
meaning_text.grid(row=0, column=1)

# Create button
search_button = tk.Button(top_frame, text="Search", command=get_meaning)
search_button.grid(row=0, column=2)

# Run the tkinter event loop
root.mainloop()
