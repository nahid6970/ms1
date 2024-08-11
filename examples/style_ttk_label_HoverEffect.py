
from tkinter import *
from tkinter.ttk import *

def apply_hover_effect(widget):
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def on_enter(event):
    event.widget.configure(style='Hover.TLabel')

def on_leave(event):
    event.widget.configure(style='Custom.TLabel')

root = Tk()
root.geometry('400x300')

# Create a style object
style = Style()

# Configure a custom style for TLabel
style.configure('Custom.TLabel', 
                font=('Helvetica', 12, 'italic'), 
                background='lightgrey', 
                foreground='darkblue', 
                borderwidth=2, 
                relief='solid',
                padding=(10, 5),
                anchor='center',
                width=30)

# Configure a hover style
style.configure('Hover.TLabel', 
                font=('Helvetica', 12, 'italic'), 
                background='red', 
                foreground='darkblue', 
                borderwidth=2, 
                relief='solid',
                padding=(10, 5),
                anchor='center',
                width=30)

# Create labels using the custom style
lbl1 = Label(root, text='Styled Label 1', style='Custom.TLabel')
lbl1.pack(pady=20)
apply_hover_effect(lbl1)

root.mainloop()






# from tkinter import *
# from tkinter.ttk import *

# def on_enter(event):
#     event.widget.configure(style='Hover.TLabel')

# def on_leave(event):
#     event.widget.configure(style='Custom.TLabel')

# root = Tk()
# root.geometry('400x300')

# # Create a style object
# style = Style()

# # Configure a custom style for TLabel
# style.configure('Custom.TLabel', 
#                 font=('Helvetica', 12, 'italic'), 
#                 background='lightgrey', 
#                 foreground='darkblue', 
#                 borderwidth=2, 
#                 relief='solid',
#                 padding=(10, 5),
#                 anchor='center',
#                 width=30)

# # Configure a hover style
# style.configure('Hover.TLabel', 
#                 font=('Helvetica', 12, 'italic'), 
#                 background='red', 
#                 foreground='darkblue', 
#                 borderwidth=2, 
#                 relief='solid',
#                 padding=(10, 5),
#                 anchor='center',
#                 width=30)
# # Create a label using the custom style
# lbl = Label(root, text='Styled Label', style='Custom.TLabel')
# lbl.pack(pady=20)
# lbl.bind("<Enter>", on_enter)
# lbl.bind("<Leave>", on_leave)

# root.mainloop()


