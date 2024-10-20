from tkinter import *
from PIL import Image, ImageTk
import os

def open_directory():
    directory = "D:\\"
    os.startfile(directory)

# Create an instance of Tkinter Frame
win = Tk()

# Set the geometry
win.geometry("700x250")

# Adding transparent background property
win.wm_attributes('-transparentcolor', '#ab23ff')

# Load the image
image_path = "C:/Users/nahid/OneDrive/backup/icon/Dolphin_icon-small.png"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Create a transparent label to overlay the image
transparent_label = Label(win, bg='#ab23ff')
transparent_label.place(relx=0, rely=0, relwidth=1, relheight=1)

# Create a Label with the image
label = Label(transparent_label, image=photo, bg='#ab23ff')
label.image = photo  # keep a reference to avoid garbage collection
label.pack(ipadx=1, ipady=1, padx=1)

# Make the label clickable
label.bind("<Button-1>", lambda event: open_directory())

# Create a label for text
text_label = Label(transparent_label, text="D Drive", font=("Helvetica", 12), bg='#ab23ff', fg="#ff0101")
text_label.pack(pady=(0, 10))  # Adjust the padding as needed

win.mainloop()
