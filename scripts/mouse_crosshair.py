import pyautogui
import tkinter as tk
import threading

# Function to calculate distance between two points
def distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def update_crosshair():
    # Get current mouse position
    mouse_x, mouse_y = pyautogui.position()
    
    # Clear previous crosshair
    canvas.delete("crosshair")
    
    # Draw crosshair lines if they are a certain distance away from the mouse pointer
    threshold_distance = 20  # Adjust this value as needed
    sample_interval = 5      # Adjust this value as needed
    
    for x in range(0, root.winfo_screenwidth(), sample_interval):
        if distance(x, mouse_y, mouse_x, mouse_y) > threshold_distance:
            canvas.create_line(x, mouse_y, x + 3, mouse_y, fill="red", tags="crosshair")
            
    for y in range(0, root.winfo_screenheight(), sample_interval):
        if distance(mouse_x, y, mouse_x, mouse_y) > threshold_distance:
            canvas.create_line(mouse_x, y, mouse_x, y + 3, fill="red", tags="crosshair")

    # Schedule the next update
    root.after_cancel(update_crosshair.after_id)
    update_crosshair.after_id = root.after(1, update_crosshair)

# Function to update crosshair in a separate thread
def update_crosshair_thread():
    update_crosshair.after_id = root.after(1, update_crosshair)

# Create a tkinter window
root = tk.Tk()
root.title("Crosshair Pointer")
root.attributes("-transparent", "blue")  # Make the window transparent
root.attributes("-fullscreen", True)     # Fullscreen mode

# Set the window background color to transparent
root.config(bg='blue')

# Create a canvas
canvas = tk.Canvas(root, bg="blue", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

# Start the crosshair update thread
update_thread = threading.Thread(target=update_crosshair_thread, daemon=True)
update_thread.start()

# Exit the program when closing the window
root.protocol("WM_DELETE_WINDOW", root.quit)

# Start the main loop
root.mainloop()


# import pyautogui
# import tkinter as tk
# import threading

# # Function to calculate distance between two points
# def distance(x1, y1, x2, y2):
#     return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# def update_crosshair():
#     # Get current mouse position
#     mouse_x, mouse_y = pyautogui.position()
    
#     # Clear previous crosshair
#     canvas.delete("crosshair")
    
#     # Draw crosshair lines if they are a certain distance away from the mouse pointer
#     threshold_distance = 20  # Adjust this value as needed
#     sample_interval = 5      # Adjust this value as needed
    
#     for x in range(0, root.winfo_screenwidth(), sample_interval):
#         if distance(x, mouse_y, mouse_x, mouse_y) > threshold_distance:
#             canvas.create_line(x, mouse_y, x + 3, mouse_y, fill="red", tags="crosshair")
            
#     for y in range(0, root.winfo_screenheight(), sample_interval):
#         if distance(mouse_x, y, mouse_x, mouse_y) > threshold_distance:
#             canvas.create_line(mouse_x, y, mouse_x, y + 3, fill="red", tags="crosshair")

#     # Schedule the next update after 10 milliseconds
#     root.after(10, update_crosshair)

# # Function to update crosshair in a separate thread
# def update_crosshair_thread():
#     while True:
#         update_crosshair()

# # Create a tkinter window
# root = tk.Tk()
# root.title("Crosshair Pointer")
# root.attributes('-topmost', True)  # Set always on top

# root.attributes("-transparent", "blue")  # Make the window transparent
# root.attributes("-fullscreen", True)     # Fullscreen mode

# # Set the window background color to transparent
# root.config(bg='blue')

# # Create a canvas
# canvas = tk.Canvas(root, bg="blue", highlightthickness=0)
# canvas.pack(fill=tk.BOTH, expand=True)

# # Start the crosshair update thread
# update_thread = threading.Thread(target=update_crosshair_thread, daemon=True)
# update_thread.start()

# # Exit the program when closing the window
# root.protocol("WM_DELETE_WINDOW", root.quit)

# # Start the main loop
# root.mainloop()



# # import pyautogui
# # import tkinter as tk
# # import threading

# # # Function to calculate distance between two points
# # def distance(x1, y1, x2, y2):
# #     return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# # def update_crosshair():
# #     # Get current mouse position
# #     mouse_x, mouse_y = pyautogui.position()
    
# #     # Clear previous crosshair
# #     canvas.delete("crosshair")
    
# #     # Draw crosshair lines if they are a certain distance away from the mouse pointer
# #     threshold_distance = 20  # Adjust this value as needed
    
# #     for x in range(root.winfo_screenwidth()):
# #         if distance(x, mouse_y, mouse_x, mouse_y) > threshold_distance:
# #             canvas.create_line(x, mouse_y, x + 1, mouse_y, fill="red", tags="crosshair")
            
# #     for y in range(root.winfo_screenheight()):
# #         if distance(mouse_x, y, mouse_x, mouse_y) > threshold_distance:
# #             canvas.create_line(mouse_x, y, mouse_x, y + 1, fill="red", tags="crosshair")

# #     # Schedule the next update
# #     root.after(10, update_crosshair)

# # def start_update_thread():
# #     # Create a thread to run the update_crosshair function
# #     update_thread = threading.Thread(target=update_crosshair)
# #     update_thread.daemon = True
# #     update_thread.start()

# # # Create a tkinter window
# # root = tk.Tk()
# # root.title("Crosshair Pointer")
# # root.attributes('-topmost', True)  # Set always on top

# # root.attributes("-transparent", "blue")  # Make the window transparent
# # root.attributes("-fullscreen", True)     # Fullscreen mode

# # # Set the window background color to transparent
# # root.config(bg='blue')

# # # Create a canvas
# # canvas = tk.Canvas(root, bg="blue", highlightthickness=0)
# # canvas.pack(fill=tk.BOTH, expand=True)

# # # Start the crosshair update thread
# # start_update_thread()

# # # Exit the program when closing the window
# # root.protocol("WM_DELETE_WINDOW", root.quit)

# # # Start the main loop
# # root.mainloop()












# # # import pyautogui
# # # import tkinter as tk

# # # # Function to calculate distance between two points
# # # def distance(x1, y1, x2, y2):
# # #     return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# # # def update_crosshair():
# # #     # Get current mouse position
# # #     mouse_x, mouse_y = pyautogui.position()
    
# # #     # Clear previous crosshair
# # #     canvas.delete("crosshair")
    
# # #     # Draw crosshair lines if they are a certain distance away from the mouse pointer
# # #     threshold_distance = 20  # Adjust this value as needed
    
# # #     for x in range(root.winfo_screenwidth()):
# # #         if distance(x, mouse_y, mouse_x, mouse_y) > threshold_distance:
# # #             canvas.create_line(x, mouse_y, x + 1, mouse_y, fill="red", tags="crosshair")
            
# # #     for y in range(root.winfo_screenheight()):
# # #         if distance(mouse_x, y, mouse_x, mouse_y) > threshold_distance:
# # #             canvas.create_line(mouse_x, y, mouse_x, y + 1, fill="red", tags="crosshair")
    
# # #     # Update every 10 milliseconds
# # #     root.after(10, update_crosshair)

# # # # Create a tkinter window
# # # root = tk.Tk()
# # # root.title("Crosshair Pointer")
# # # root.attributes("-transparent", "blue")  # Make the window transparent
# # # root.attributes("-fullscreen", True)     # Fullscreen mode

# # # # Set the window background color to transparent
# # # root.config(bg='blue')

# # # # Create a canvas
# # # canvas = tk.Canvas(root, bg="blue", highlightthickness=0)
# # # canvas.pack(fill=tk.BOTH, expand=True)

# # # # Update crosshair initially
# # # update_crosshair()

# # # # Exit the program when closing the window
# # # root.protocol("WM_DELETE_WINDOW", root.quit)

# # # # Start the main loop
# # # root.mainloop()















# # # # import pyautogui
# # # # import tkinter as tk

# # # # def update_crosshair():
# # # #     # Get current mouse position
# # # #     x, y = pyautogui.position()
    
# # # #     # Clear previous crosshair
# # # #     canvas.delete("crosshair")
    
# # # #     # Draw horizontal line
# # # #     canvas.create_line(0, y, root.winfo_screenwidth(), y, fill="red", tags="crosshair")
    
# # # #     # Draw vertical line
# # # #     canvas.create_line(x, 0, x, root.winfo_screenheight(), fill="red", tags="crosshair")
    
# # # #     # Update every 10 milliseconds
# # # #     root.after(10, update_crosshair)

# # # # # Create a tkinter window
# # # # root = tk.Tk()
# # # # root.title("Crosshair Pointer")
# # # # root.attributes("-transparent", "blue")  # Make the window transparent
# # # # root.attributes("-topmost", True)        # Keep the window on top

# # # # # Set the window background color to transparent
# # # # root.config(bg='blue')

# # # # # Disable window resizing
# # # # root.resizable(False, False)

# # # # # Set window dimensions to cover the whole screen
# # # # root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

# # # # # Create a canvas
# # # # canvas = tk.Canvas(root, bg="blue", highlightthickness=0)
# # # # canvas.pack(fill=tk.BOTH, expand=True)

# # # # # Update crosshair initially
# # # # update_crosshair()

# # # # # Make the window non-interactive
# # # # root.attributes("-fullscreen", True)
# # # # root.overrideredirect(True)

# # # # # Exit the program when pressing Escape key
# # # # def exit_fullscreen(event):
# # # #     if event.keysym == "Escape":
# # # #         root.destroy()
# # # # root.bind("<Key>", exit_fullscreen)

# # # # # Start the main loop
# # # # root.mainloop()
