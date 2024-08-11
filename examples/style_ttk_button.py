from tkinter import *
from tkinter.ttk import *

root = Tk()
root.geometry('400x300')

# Create a style object
style = Style()

# Configure a custom style for TButton
style.configure('Custom.TButton', 
                font=('Helvetica', 12, 'bold'), 
                background='lightblue', 
                foreground='blue', 
                borderwidth=5, 
                relief='raised',
                padding=(10, 5),
                width=20,
                anchor='center')

# Map different states to styles
style.map('Custom.TButton', 
          background=[('active', 'blue'), ('disabled', 'grey')],
          foreground=[('active', 'white'), ('disabled', 'darkgrey')],
          relief=[('pressed', 'sunken'), ('active', 'raised')],
          bordercolor=[('active', 'green'), ('disabled', 'red')],
          focuscolor=[('focus', 'red'), ('!focus', 'blue')])

# Create a button using the custom style
btn = Button(root, text='Styled Button', style='Custom.TButton')
btn.pack(pady=20)

# Another button without the style for comparison
btn2 = Button(root, text='Normal Button')
btn2.pack(pady=20)

root.mainloop()
