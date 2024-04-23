from tkinter import *

root = Tk()



def button_click(event):  # Modify the function to accept the event argument
    print("Button clicked!")
    
canvas = Canvas(root, width=100, height=50, bg="lightgray")
text_id = canvas.create_text(50, 25, text="Click Me", angle=90)
canvas.bind("<Button-1>", button_click)

canvas.pack()

root.mainloop()
