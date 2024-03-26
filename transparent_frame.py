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
image_path = "C:/Users/nahid/OneDrive/backup/icon/Dolphin_icon-20x20.png"
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Create a transparent label to overlay the image
transparent_label = Label(win, bg='#ab23ff')
transparent_label.place(relx=0, rely=0, relwidth=1, relheight=1)

# Create a Label with the image
label = Label(transparent_label, image=photo)
label.image = photo  # keep a reference to avoid garbage collection
label.pack(ipadx=50, ipady=50, padx=20)

# Make the label clickable
label.bind("<Button-1>", lambda event: open_directory())

win.mainloop()
