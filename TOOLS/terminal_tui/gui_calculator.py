import tkinter as tk
from tkinter import messagebox
import math

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FX-991ES Style Calculator")
        self.geometry("350x450")
        self.result_var = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        # Display
        display = tk.Entry(self, textvariable=self.result_var, font=('Arial', 24), bd=10, insertwidth=4, width=14, justify='right')
        display.grid(row=0, column=0, columnspan=4, pady=20)

        # Buttons
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row = 1
        col = 0
        for btn in buttons:
            action = lambda x=btn: self.on_click(x)
            tk.Button(self, text=btn, width=5, height=2, font=('Arial', 14), command=action).grid(row=row, column=col, sticky='nsew')
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        tk.Button(self, text='C', width=20, height=2, font=('Arial', 14), command=self.clear).grid(row=row, column=0, columnspan=4, sticky='nsew')

    def on_click(self, char):
        if char == '=':
            try:
                result = eval(self.result_var.get())
                self.result_var.set(result)
            except Exception:
                messagebox.showerror("Error", "Invalid Input")
                self.result_var.set("")
        else:
            self.result_var.set(self.result_var.get() + char)

    def clear(self):
        self.result_var.set("")

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
