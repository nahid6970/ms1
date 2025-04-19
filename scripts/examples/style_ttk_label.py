from tkinter import *
from tkinter.ttk import *

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

# Map different states to styles
style.map('Custom.TLabel', 
          background=[('active', 'lightblue'), ('disabled', 'lightgrey')],
          foreground=[('active', 'black'), ('disabled', 'grey')],
          relief=[('active', 'raised'), ('disabled', 'sunken')],
          font=[('disabled', ('Helvetica', 10, 'italic'))])

# Create a label using the custom style
lbl = Label(root, text='Styled Label', style='Custom.TLabel')
lbl.pack(pady=20)

# Another label without the style for comparison
lbl2 = Label(root, text='Normal Label')
lbl2.pack(pady=20)

root.mainloop()
