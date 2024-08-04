import tkinter as tk
from tkinter import messagebox
import psutil
import pyautogui

# List of predetermined applications and their display names
apps = {
    "cmd.exe"            :"\uebc4 CMD",
    "code.exe"           :"\ue70c VSCode",
    "komorebi.exe"       :"\uf2d2 Komorebi",
    "pwsh.exe"           :"\uea85 PowershellCore",
    "powershell.exe"     :"\uea85 Powershell",
    "python.exe"         :"\ue73c Python",
    "sonarr.exe"         :"\udb84\udfb4 Sonarr",
    "radarr.exe"         :"\udb81\udfde Radarr",
}

def update_status():
    for app, display_name in apps.items():
        running = any(proc.name().lower() == app.lower() for proc in psutil.process_iter())
        color = "green" if running else "red"
        label = labels[app]
        label.config(fg=color)
        
        if running:
            label.bind("<Button-1>", lambda e, app=app: kill_process(app))
        else:
            label.unbind("<Button-1>")

def kill_process(app):
    for proc in psutil.process_iter():
        if proc.name().lower() == app.lower():
            proc.kill()
            messagebox.showinfo("Process Killed", f"{apps[app]} has been killed")
            break
    update_status()

def center_and_press_alt_2(window):
    def center_window():
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    def press_alt_2():
        pyautogui.hotkey('alt', '2')
    center_window()
    window.after(25, press_alt_2)

root = tk.Tk()
root.title("Process Manager")

labels = {}
row = 0
col = 0
for app, display_name in apps.items():
    label = tk.Label(root, text=display_name, font=("JetBrainsmono nfp", 18,"bold"), width=20, height=5, relief="solid", highlightbackground="blue", highlightcolor="blue", highlightthickness=2, bd=0, padx=5, pady=5)
    label.grid(row=row, column=col, padx=10, pady=10)
    labels[app] = label


    col += 1
    if col == 5:  # Move to next row after 5 columns
        row += 1
        col = 0

update_status()
center_and_press_alt_2(root)
root.mainloop()
