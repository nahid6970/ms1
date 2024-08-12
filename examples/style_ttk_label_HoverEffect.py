
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
                background='green', 
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




    ("BookmarkLine"                ,"Bookmark Line")                   ,
    ("Bookmarklistall"             ,"? Bookmark list All")             ,
    ("BracketsGoTo"                ,"Brackets GoTo")                   ,
    ("BracketsRemove"              ,"Brackets Remove")                 ,
    ("BracketsSelect"              ,"Brackets Select")                 ,
    ("AlignMultiCoulmnsbySeparator","Align Multi Coulmns by Separator"),
    ("ChangeAllOccurrences"        ,"Change All Occurrences")          ,
    ("Comment"                     ,"Comment")                         ,
    ("CommentSelection"            ,"Comment Selection")               ,
    ("DeleteLine"                  ,"Delete Line")                     ,
    ("Keyboard_Shortcut"           ,"VSCODE Keyboard Shortcut")        ,
    ("LineJoin"                    ,"Line Join")                       ,
    ("Minimap"                     ,"Minimap")                         ,
    ("NewWindow"                   ,"New Window")                      ,
    ("remove_dup_lines"            ,"Remove Dup Lines")                ,
    ("RemoveFromSelection"         ,"Remove From Selection")           ,
    ("SelectNext"                  ,"Select Next")                     ,
    ("SelectPrevious"              ,"Select Previous")                 ,
    ("SortLinesAscending"          ,"Sort Lines Ascending")            ,
    ("SplitSameDocument"           ,"Split Same Document")             ,
    ("TableFormatProperly"         ,"Table Format Properly")           ,
    ("TableFormatProperly2"        ,"Table Format Properly 2")         ,
    ("UnComment"                   ,"UnComment")                       ,




Series = HoverButton(Excel_frame, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Series"]), text="\udb81\udc8b")
Series.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Fit_Row = HoverButton(Excel_frame, bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0, command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Fit_Row"]), text="\udb82\udc37")
Fit_Row.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))

Fit_Column = HoverButton(Excel_frame, text="\udb82\udc35", bg="#000000", fg="#FFFFFF", height=1, width=0, bd=0, highlightthickness=0,
                         tooltip_text="Adjust Column",tooltip_delay=100,tooltip_font_size=12,
                         command=lambda:subprocess.Popen(["powershell", "python c:/ms1/HotKeys.py Fit_Column"]))
Fit_Column.pack(side="top", anchor="center", padx=(0,0), pady=(0,0))