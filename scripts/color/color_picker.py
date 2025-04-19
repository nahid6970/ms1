import tkinter as tk
import pyautogui
import pyperclip
import threading
import keyboard

def update_color():
    while True:
        try:
            x, y = pyautogui.position()
            color = pyautogui.screenshot().getpixel((x, y))
            hex_color = '{:02x}{:02x}{:02x}'.format(*color)
            color_label.config(text=hex_color, bg=f'#{hex_color}')
            color_label_white.config(text=hex_color, bg=f'#{hex_color}')
            move_window(x, y)
        except Exception as e:
            print(f"Error in update_color: {e}")

def move_window(mouse_x, mouse_y):
    window_offset = 10
    screen_width = ROOT.winfo_screenwidth()
    screen_height = ROOT.winfo_screenheight()
    window_width = ROOT.winfo_width()
    window_height = ROOT.winfo_height()
    
    # Calculate the adjusted window position
    x = min(max(mouse_x, 0), screen_width - window_width)
    y = min(max(mouse_y + window_offset, 0), screen_height - window_height)
    
    ROOT.geometry(f"+{x}+{y}")

def copy_color():
    x, y = pyautogui.position()
    color = pyautogui.screenshot().getpixel((x, y))
    hex_color = '{:02x}{:02x}{:02x}'.format(*color)
    pyperclip.copy(hex_color)

def close_window():
    ROOT.destroy()

ROOT = tk.Tk()
ROOT.title("Color Picker")
ROOT.configure(bg="#282c34")
ROOT.attributes('-topmost', True)
ROOT.overrideredirect(True)

box1 = tk.Frame(ROOT, bg="#1d2027")
box1.pack(side="right", anchor="center", pady=(0, 0), padx=(0, 0))

color_label_white = tk.Label(box1, font=("JetBrainsMono NF", 10, "bold"), fg="white", bg="#1d2027", width=10, height=3)
color_label_white.pack(side="left")

color_label = tk.Label(box1, font=("JetBrainsMono NF", 10, "bold"), fg="black", bg="#1d2027", width=10, height=3)
color_label.pack(side="left")

# Create a separate thread for updating the color and moving window
thread = threading.Thread(target=update_color, daemon=True)
thread.start()

# Bind events
keyboard.add_hotkey("ctrl+c", copy_color)
keyboard.add_hotkey("esc", close_window)
print("Hotkeys registered")

ROOT.mainloop()



# import tkinter as tk
# import pyautogui
# import pyperclip
# import threading
# import keyboard

# def update_color():
#     while True:
#         try:
#             x, y = pyautogui.position()
#             color = pyautogui.screenshot().getpixel((x, y))
#             hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
#             color_label.config(bg=hex_color)
#             color_label_white.config(bg=hex_color)
#             move_window(x, y)
#         except Exception as e:
#             print(f"Error in update_color: {e}")

# def move_window(mouse_x, mouse_y):
#     window_offset = 10
#     screen_width = ROOT.winfo_screenwidth()
#     screen_height = ROOT.winfo_screenheight()
#     window_width = ROOT.winfo_width()
#     window_height = ROOT.winfo_height()
    
#     # Calculate the adjusted window position
#     x = min(max(mouse_x, 0), screen_width - window_width)
#     y = min(max(mouse_y + window_offset, 0), screen_height - window_height)
    
#     ROOT.geometry(f"+{x}+{y}")

# def copy_color():
#     x, y = pyautogui.position()
#     color = pyautogui.screenshot().getpixel((x, y))
#     hex_color = '{:02x}{:02x}{:02x}'.format(*color)
#     pyperclip.copy(hex_color)

# def close_window():
#     ROOT.destroy()

# ROOT = tk.Tk()
# ROOT.title("Color Picker")
# ROOT.configure(bg="#282c34")
# ROOT.attributes('-topmost', True)
# ROOT.overrideredirect(True)

# box1 = tk.Frame(ROOT, bg="#1d2027")
# box1.pack(side="right", anchor="center", pady=(0, 0), padx=(0, 0))

# color_label_white = tk.Label(box1, font=("JetBrainsMono NF", 10, "bold"), fg="white", bg="#1d2027", width=10, height=3)
# color_label_white.pack(side="left")

# color_label = tk.Label(box1, font=("JetBrainsMono NF", 10, "bold"), fg="black", bg="#1d2027", width=10, height=3)
# color_label.pack(side="left")

# # Create a separate thread for updating the color and moving window
# thread = threading.Thread(target=update_color, daemon=True)
# thread.start()

# # Bind events
# keyboard.add_hotkey("ctrl+space", copy_color)
# keyboard.add_hotkey("esc", close_window)
# print("Hotkeys registered")

# ROOT.mainloop()




# # import tkinter as tk
# # import pyautogui
# # import pyperclip
# # import threading
# # import keyboard

# # def update_color():
# #     while True:
# #         try:
# #             x, y = pyautogui.position()
# #             color = pyautogui.screenshot().getpixel((x, y))
# #             hex_color = '#{:02x}{:02x}{:02x}'.format(*color)
# #             color_label.config(text=f"Color: {hex_color}", bg=hex_color)
# #             color_label_white.config(text=f"Color: {hex_color}", bg=hex_color)
# #             move_window(x, y)
# #         except Exception as e:
# #             print(f"Error in update_color: {e}")

# # def move_window(mouse_x, mouse_y):
# #     window_offset = 10
# #     screen_width = ROOT.winfo_screenwidth()
# #     screen_height = ROOT.winfo_screenheight()
# #     window_width = ROOT.winfo_width()
# #     window_height = ROOT.winfo_height()
    
# #     # Calculate the adjusted window position
# #     x = min(max(mouse_x, 0), screen_width - window_width)
# #     y = min(max(mouse_y + window_offset, 0), screen_height - window_height)
    
# #     ROOT.geometry(f"+{x}+{y}")

# # def copy_color():
# #     color_text = color_label.cget("text")
# #     hex_color = color_text.split(": ")[1]
# #     pyperclip.copy(hex_color)

# # def close_window():
# #     ROOT.destroy()

# # # def close_window_on_click(event):
# # #     # Check if the click occurred outside the window
# # #     if event.widget == ROOT:
# # #         close_window()

# # ROOT = tk.Tk()
# # ROOT.title("Color Picker")
# # ROOT.configure(bg="#282c34")
# # ROOT.attributes('-topmost', True)
# # ROOT.overrideredirect(True)

# # box1 = tk.Frame(ROOT, bg="#1d2027")
# # box1.pack(side="right", anchor="center", pady=(0, 0), padx=(0, 0))

# # color_label_white = tk.Label(box1, text="Color: ", font=("JetBrainsMono NF", 10, "bold"), fg="white", bg="#1d2027")
# # color_label_white.pack(side="left")

# # color_label = tk.Label(box1, text="Color: ", font=("JetBrainsMono NF", 10, "bold"), fg="black", bg="#1d2027")
# # color_label.pack(side="left")

# # # LB_x = tk.Label(box1, bg="#ff0000", fg="#FFFFFF", font=("JetBrainsMono NF", 10, "bold"), text="X")
# # # LB_x.pack(side="left")
# # # LB_x.bind("<Button-1>", close_window)

# # # Create a separate thread for updating the color and moving window
# # thread = threading.Thread(target=update_color, daemon=True)
# # thread.start()

# # # Bind events
# # # ROOT.bind("<Button-1>", close_window_on_click)

# # keyboard.add_hotkey("ctrl+space", copy_color)
# # keyboard.add_hotkey("esc", close_window)
# # print("Hotkeys registered")

# # ROOT.mainloop()
