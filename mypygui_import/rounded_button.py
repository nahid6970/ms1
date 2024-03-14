import tkinter as tk

class RoundedButton(tk.Canvas):

    def __init__(self, master=None, text:str="", radius=25, btnforeground="#000000", btnbackground="#ffffff", clicked=None, width=None, height=None, font=None, **kwargs):
        super(RoundedButton, self).__init__(master, **kwargs)
        self.config(bg=self.master["bg"])
        self.btnbackground = btnbackground
        self.clicked = clicked

        self.radius = radius

        self.circle = self.create_oval(0, 0, 0, 0, tags="button", fill=btnbackground)
        self.text = self.create_text(0, 0, text=text, tags="button", fill=btnforeground, font=font, justify="center")

        self.tag_bind("button", "<ButtonPress>", self.border)
        self.tag_bind("button", "<ButtonRelease>", self.border)
        self.bind("<Configure>", self.resize)

        if width:
            self["width"] = width
        if height:
            self["height"] = height

        text_rect = self.bbox(self.text)
        if int(self["width"]) < text_rect[2]-text_rect[0]:
            self["width"] = (text_rect[2]-text_rect[0]) + 10

        if int(self["height"]) < text_rect[3]-text_rect[1]:
            self["height"] = (text_rect[3]-text_rect[1]) + 10

    def resize(self, event):
        text_bbox = self.bbox(self.text)

        if event.width < text_bbox[2]-text_bbox[0]:
            width = text_bbox[2]-text_bbox[0] + 30
        else:
            width = event.width

        if event.height < text_bbox[3]-text_bbox[1]:
            height = text_bbox[3]-text_bbox[1] + 30
        else:
            height = event.height

        self.coords(self.circle, 5, 5, width-5, height-5)

        bbox = self.bbox(self.circle)

        x = ((bbox[2]-bbox[0])/2) - ((text_bbox[2]-text_bbox[0])/2)
        y = ((bbox[3]-bbox[1])/2) - ((text_bbox[3]-text_bbox[1])/2)

        self.moveto(self.text, x, y)

    def border(self, event):
        if event.type == "4":
            self.itemconfig(self.circle, fill="#d2d6d3")
            if self.clicked is not None:
                self.clicked()
        else:
            self.itemconfig(self.circle, fill=self.btnbackground)

def func():
    print("Button pressed")





root = tk.Tk()
root.title("Unicode Display")





# Create the rounded button
btn = RoundedButton(root, text="Click Me!", radius=100, btnbackground="#0078ff", width=100, height=100, btnforeground="#ffffff", clicked=func, font=("agency", 10))
btn.pack(expand=True, fill="both")


root.mainloop()