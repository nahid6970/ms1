import tkinter as tk
from tkinter import ttk
import subprocess
import os


def run_command(command, wait=False, hide=False):
    """Runs a command using subprocess."""
    creation_flags = subprocess.CREATE_NO_WINDOW if hide and os.name == 'nt' else 0
    if wait:
        subprocess.run(command, creationflags=creation_flags)
    else:
        subprocess.Popen(command, creationflags=creation_flags)

def kill_process(process_name):
    """Kills a process by name."""
    if os.name == 'nt':  # For Windows
        run_command(['taskkill', '/f', '/im', process_name], hide=True)
    else:  # For other operating systems (like Linux, macOS) you might use 'pkill' or 'killall'
        run_command(['pkill', '-f', process_name], hide=True) # Consider using a more specific method

def start_python_st():
    """Starts Python with a specific script, keeping the terminal open for errors."""
    subprocess.Popen(['python', 'C:\\ms1\\mypygui.py']) # Simple way to run, might not keep terminal open

def restart_explorer():
    """Restarts explorer.exe."""
    if os.name == 'nt':
        run_command(['taskkill', '/f', '/im', 'explorer.exe'], wait=True, hide=True)
        subprocess.Popen(['start', 'explorer.exe'])
    else:
        print("Restarting explorer is specific to Windows.")

def run_script(path, hide=False):
    """Runs an external script in a new window using subprocess.Popen."""
    creationflags = subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    startupinfo = None

    if os.name == 'nt' and hide:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    if path.lower().endswith('.py'):
        subprocess.Popen(['python', path], startupinfo=startupinfo, creationflags=creationflags)
    elif path.lower().endswith('.ps1'):
        subprocess.Popen(['powershell', '-ExecutionPolicy', 'Bypass', '-File', path],
                         startupinfo=startupinfo, creationflags=creationflags)
    elif path.lower().endswith('.ahk'):
        subprocess.Popen([path], startupinfo=startupinfo, creationflags=creationflags)
    else:
        subprocess.Popen([path], startupinfo=startupinfo, creationflags=creationflags)



def create_control_panel_without_tab_border():
    root = tk.Tk()
    root.title("Control Panel")
    root.attributes("-topmost", True)
    root.config(bg="#86b2f4") # Set the main window background to red (for the border effect)
    root.overrideredirect(True)  # Remove default borders

    # Create a main frame with black background to hold the content
    content_frame = ttk.Frame(root, style="Content.TFrame")
    content_frame.pack(padx=2, pady=2, expand=True, fill="both") # Add padding to show the red border

    # Style for the content frame (black background)
    style = ttk.Style()
    style.theme_use('default') # Try a different theme (e.g.,'winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
    style.configure("Content.TFrame", background="#555555")

    style.configure("TNotebook", tabposition='n')
    style.configure("TNotebook",
                        background="#272727",
                        foreground="#c0c0c0",                   
                        borderwidth=0)
    style.configure("TNotebook.Tab",
                        background="#333333",
                        foreground="#ffffff",
                        focuscolor="#666666",
                        borderwidth=0                            
                        )
    style.map('TNotebook.Tab',background=[("selected",'#56570b')],
                        highlightbackground =[("active","#333")],                                    
                                lightcolor=[("selected", "#333333")],
                                foreground=[("active","#4f5a69")])

    style.configure("TFrame", background="black")
    style.configure("TLabel", background="black", foreground="white")

    default_font = ("Jetbrainsmono nfp", 12, "bold")
    large_font = ("Jetbrainsmono nfp", 30, "bold")
    medium_font = ("Jetbrainsmono nfp", 20, "bold")

    padx = 20
    pady = 20

    # --- Tab Control ---
    notebook = ttk.Notebook(content_frame)
    notebook.pack(expand=True, fill="both")

    # --- Main Tab ---
    main_tab = ttk.Frame(notebook, style="Content.TFrame")

    ROW_1 = tk.Frame(main_tab, bg="#555555")
    ROW_1.grid(row=0, column=0, sticky="n")

    # Komorebic Section
    komorebic_save_button = tk.Label(ROW_1, text="Komorebic Save", width=20, bg="#ffa114", relief="solid", borderwidth=1, font=default_font, fg="black")
    komorebic_save_button.grid(row=0, column=0, padx=5, pady=pady)
    komorebic_save_button.bind("<Button-1>", lambda event: run_command(["komorebic", "quick-save-resize"], wait=True, hide=True))

    komorebic_load_button = tk.Label(ROW_1, text="Komorebic Load", width=20, bg="#ffa114", relief="solid", borderwidth=1, font=default_font, fg="black")
    komorebic_load_button.grid(row=0, column=1, padx=5, pady=pady)
    komorebic_load_button.bind("<Button-1>", lambda event: run_command(["komorebic", "quick-load-resize"], wait=True, hide=True))

    # Kill Processes Section
    ROW_2 = tk.Frame(main_tab, bg="#555555")
    ROW_2.grid(row=1, column=0, sticky="n")

    def add_kill_button(parent, text, proc_name):
        b = tk.Label(parent, text=text, width=3, bg="#f30000", fg="#ffffff", relief="solid", borderwidth=1, font=large_font)
        b.pack(side="left", padx=5)
        b.bind("<Button-1>", lambda e: kill_process(proc_name))

    add_kill_button(ROW_2, "", "python.exe")
    add_kill_button(ROW_2, "󱂬", "komorebi.exe")
    add_kill_button(ROW_2, "", "explorer.exe")
    add_kill_button(ROW_2, "", "cmd.exe")
    add_kill_button(ROW_2, "󰨊", "powershell.exe")
    add_kill_button(ROW_2, "", "pwsh.exe")

    # Utility Scripts Section
    ROW_3 = tk.Frame(main_tab, bg="#555555")
    ROW_3.grid(row=2, column=0, sticky="n")



    def start_flask_scripts_silently():
        scripts = [
            r"C:\ms1\flask\Browse_PC_Files\Browse_PC_Files.py",
            r"C:\ms1\flask\GameARR\SeperateFiles\GameARR.py",
            r"C:\ms1\flask\share_text\share_text.py",
            r"C:\ms1\flask\upload_files.py",
        ]
        for script in scripts:
            subprocess.Popen(
                ["python", script],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    ROW_FOR_Start = tk.Frame(main_tab, bg="#555555")
    ROW_FOR_Start.grid(row=2, column=0, sticky="w", padx=(65,0))

    Python_flask_Scripts_Button = tk.Label(ROW_FOR_Start, text="", width=3, bg="#14ff91", fg="#000000", relief="solid", borderwidth=1, font=large_font)
    Python_flask_Scripts_Button.grid(row=1, column=0, padx=5, pady=5)
    Python_flask_Scripts_Button.bind("<Button-1>", lambda event: start_flask_scripts_silently())

    Komorebi_Start_Button = tk.Label(ROW_FOR_Start, text="󱂬", width=3, bg="#14ff91", fg="#000000", relief="solid", borderwidth=1, font=large_font)
    Komorebi_Start_Button.grid(row=1, column=1, padx=5, pady=5)
    Komorebi_Start_Button.bind("<Button-1>", lambda event: run_command(["komorebi.exe"], hide=True))

    restart_explorer_button = tk.Label(ROW_FOR_Start, text="", width=3, bg="#14ff91", fg="#000000", relief="solid", borderwidth=1, font=large_font)
    restart_explorer_button.grid(row=1, column=2, padx=5, pady=5)
    restart_explorer_button.bind("<Button-1>", lambda event: restart_explorer())

    # AHK-Scripts Section
    ROW_3 = tk.Frame(main_tab, bg="#555555")
    ROW_3.grid(row=3, column=0, sticky="n")

    text_grab_button = tk.Label(ROW_3, text="", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    text_grab_button.grid(row=0, column=0, padx=5, pady=5)
    text_grab_button.bind("<Button-1>", lambda event: (root.destroy(), root.after(500, lambda: run_command(['powershell', '-Command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("#+f")']))))

    crosshair_button = tk.Label(ROW_3, text="", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    crosshair_button.grid(row=0, column=1, padx=5, pady=5)
    crosshair_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\xy\\XY_CroosHair.py", hide=True))

    locker_button = tk.Label(ROW_3, text="", width=2, bg="#31ffc1", fg="#eb3d30", relief="solid", borderwidth=1, font=medium_font)
    locker_button.grid(row=0, column=2, padx=5, pady=5)
    locker_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\Locker.py", hide=True))

    # AHK-Scripts Section
    BOX_4 = tk.Frame(main_tab, bg="#555555")
    BOX_4.grid(row=4, column=0, sticky="n")

    ahk_scripts_label = tk.Label(BOX_4, text="AHK-Scripts", width=20, relief="solid", borderwidth=1, font=default_font)
    ahk_scripts_label.grid(row=3, column=0, padx=5, pady=5)

    ahk_converter_button = tk.Label(BOX_4, text="AhkConverter", width=20, bg="#32ec44", fg="black", font=default_font)
    ahk_converter_button.grid(row=3, column=1, padx=5, pady=5)
    ahk_converter_button.bind("<Button-1>", lambda event: (root.destroy(), run_script("C:\\msBackups\\Autohotkey\\AHK_converter\\QuickConvertorV2_scintilla.ahk", hide=True)))

    uia_v2_button = tk.Label(BOX_4, text="UIA-V2", width=20, bg="#32ec44", fg="black", font=default_font)
    uia_v2_button.grid(row=3, column=2, padx=5, pady=5)
    uia_v2_button.bind("<Button-1>", lambda event: (root.destroy(), run_script("C:\\ms1\\scripts\\ahk\\UIA_v2\\Lib\\UIA.ahk", hide=True)))

    # Python Section
    python_label = tk.Label(BOX_4, text="Python", width=20, relief="solid", borderwidth=1, font=default_font)
    python_label.grid(row=5, column=0, padx=5, pady=5)

    mypygui_h_button = tk.Label(BOX_4, text="mypygui-H", width=20, bg="#32ec44", fg="black", font=default_font)
    mypygui_h_button.grid(row=5, column=1, padx=5, pady=5)
    mypygui_h_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\mypygui.py", hide=True))

    mypygui_s_button = tk.Label(BOX_4, text="mypygui-S", width=20, bg="#32ec44", fg="black", font=default_font)
    mypygui_s_button.grid(row=5, column=2, padx=5, pady=5)
    mypygui_s_button.bind("<Button-1>", lambda event: start_python_st())

    notebook.add(main_tab, text="Main")

    # --- ffmpeg Tab ---
    ffmpeg_tab = ttk.Frame(notebook, style="Content.TFrame")

    # FFmpeg Scripts Section
    ffmpeg_trim_button = tk.Label(ffmpeg_tab, text="", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    ffmpeg_trim_button.grid(row=0, column=0, padx=5, pady=5)
    ffmpeg_trim_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\ffmpeg\\trim.ps1", hide=False))

    ffmpeg_convert_button = tk.Label(ffmpeg_tab, text="", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    ffmpeg_convert_button.grid(row=0, column=1, padx=5, pady=5)
    ffmpeg_convert_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\ffmpeg\\convert.ps1", hide=False))

    ffmpeg_merge_button = tk.Label(ffmpeg_tab, text="󰕩", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    ffmpeg_merge_button.grid(row=0, column=2, padx=5, pady=5)
    ffmpeg_merge_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\ffmpeg\\merge.ps1", hide=False))

    ffmpeg_vid_dim_button = tk.Label(ffmpeg_tab, text="", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    ffmpeg_vid_dim_button.grid(row=0, column=3, padx=5, pady=5)
    ffmpeg_vid_dim_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\ffmpeg\\vid_dim.ps1", hide=False))

    ffmpeg_img_dim_button = tk.Label(ffmpeg_tab, text="", width=2, bg="#31ffc1", fg="#000000", relief="solid", borderwidth=1, font=medium_font)
    ffmpeg_img_dim_button.grid(row=0, column=4, padx=5, pady=5)
    ffmpeg_img_dim_button.bind("<Button-1>", lambda event: run_script("C:\\ms1\\scripts\\ffmpeg\\img_dim.ps1", hide=False))

    notebook.add(ffmpeg_tab, text="ffmpeg")



    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    create_control_panel_without_tab_border()