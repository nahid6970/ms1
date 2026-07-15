import os
import queue
import re
import subprocess
import threading
import time
from flask import Flask, request, send_from_directory, redirect, url_for, flash, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Configure Flask for better performance
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_TIMEOUT'] = 300  # 5 minutes timeout

# Folder to store files permanently — reads from Tray Manager settings if available
import json as _json
_TRAY_SETTINGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tray_settings.json')
_TRAY_SETTINGS = os.path.normpath(_TRAY_SETTINGS)

DESKTOP_PATH = os.path.expanduser('~/Desktop')
SHARE_FOLDER = os.path.join(DESKTOP_PATH, 'ShareFolder')  # default

if os.path.exists(_TRAY_SETTINGS):
    try:
        with open(_TRAY_SETTINGS) as _f:
            SHARE_FOLDER = _json.load(_f).get('upload_files', {}).get('save_folder', SHARE_FOLDER)
    except Exception:
        pass

if not os.path.exists(SHARE_FOLDER):
    os.makedirs(SHARE_FOLDER)

app.config['SHARE_FOLDER'] = SHARE_FOLDER

NOTIFICATION_LOCK = threading.Lock()
ACTIVE_NOTIFICATION_SLOTS = set()
NOTIFICATION_QUEUE = queue.Queue()
NOTIFICATION_MANAGER_STARTED = False

def create_safe_filename(filename):
    """
    Create a safe filename that preserves spaces and most special characters
    while removing only truly dangerous characters. Handles directory paths.
    """
    # Split path into components to handle directories
    path_parts = filename.split('/')
    safe_parts = []
    
    for part in path_parts:
        if not part:  # Skip empty parts
            continue
            
        # Remove dangerous characters but preserve spaces and common symbols
        safe_part = re.sub(r'[<>:"|?*\x00-\x1f]', '_', part)
        # Prevent directory traversal
        safe_part = safe_part.replace('..', '_')
        # Remove leading/trailing whitespace and dots
        safe_part = safe_part.strip('. ')
        # Ensure part is not empty
        if not safe_part:
            safe_part = 'unnamed'
            
        safe_parts.append(safe_part)
    
    # Rejoin with forward slashes (works on both Windows and Unix)
    safe_filename = '/'.join(safe_parts) if safe_parts else 'unnamed_file'
    return safe_filename

def get_notification_slot():
    with NOTIFICATION_LOCK:
        slot = 0
        while slot in ACTIVE_NOTIFICATION_SLOTS:
            slot += 1
        ACTIVE_NOTIFICATION_SLOTS.add(slot)
        return slot

def release_notification_slot(slot):
    with NOTIFICATION_LOCK:
        ACTIVE_NOTIFICATION_SLOTS.discard(slot)

def shorten_notification_filename(filename, max_length=34):
    file_name = filename.replace("\\", "/").split("/")[-1]
    if len(file_name) <= max_length:
        return file_name
    return f"{file_name[:max_length - 3]}..."

def open_file_folder(file_path):
    """Open Windows Explorer with the uploaded file selected."""
    if os.name != "nt":
        return

    normalized_path = os.path.abspath(os.path.normpath(file_path))
    folder_path = normalized_path if os.path.isdir(normalized_path) else os.path.dirname(normalized_path)
    if os.path.isfile(normalized_path):
        subprocess.Popen(["explorer.exe", "/select,", normalized_path])
        return

    if folder_path and os.path.exists(folder_path):
        os.startfile(folder_path)
    else:
        subprocess.Popen(["explorer", app.config["SHARE_FOLDER"]])

def show_upload_notification(filename, file_path):
    """Show a small clickable Windows-style notification above the taskbar."""
    if os.name != "nt":
        return

    size_str = ""
    size_bytes = 0
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            temp_size = float(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if temp_size < 1024.0:
                    size_str = f"{temp_size:.1f} {unit}" if unit != 'B' else f"{int(temp_size)} B"
                    break
                temp_size /= 1024.0
    except Exception:
        pass
    if not size_str:
        size_str = "0 B"

    import datetime
    arrival_time = datetime.datetime.now().strftime("%I:%M%p").lstrip('0').lower()

    start_notification_manager()
    NOTIFICATION_QUEUE.put((filename, file_path, size_bytes, size_str, arrival_time))

def update_upload_progress(filename, percent, size_bytes=0):
    """Notify the system about current upload progress of a file."""
    if os.name != "nt":
        return

    start_notification_manager()
    NOTIFICATION_QUEUE.put(("progress", filename, percent, size_bytes))

def start_notification_manager():
    global NOTIFICATION_MANAGER_STARTED

    with NOTIFICATION_LOCK:
        if NOTIFICATION_MANAGER_STARTED:
            return
        NOTIFICATION_MANAGER_STARTED = True

    threading.Thread(target=notification_manager_worker, daemon=True).start()

def notification_manager_worker():
    try:
        import tkinter as tk
        from tkinter import font as tkfont
    except Exception as e:
        print(f"Notification startup error: {e}")
        return

    try:
        root = tk.Tk()
        root.withdraw()

        body_font = tkfont.Font(family="Segoe UI", size=-12)
        title_font = tkfont.Font(family="Segoe UI", size=-14, weight="bold")
        list_font = tkfont.Font(family="Segoe UI", size=-12)

        notifications_data = []  # List of dicts: {"id": int, "filename": str, "file_path": str}
        notification_counter = 0

        # Colors
        bg = "#111111"
        border = "#333333"
        text = "#f3f3f3"
        muted = "#bdbdbd"
        accent = "#0078d4"
        red_color = "#ff4d4d"
        red_hover = "#ff1a1a"
        item_hover_bg = "#2a2a2a"

        card_window = None

        width = 360
        max_height = 450
        min_height = 120
        margin_right = 18
        margin_bottom = 54

        def update_card_position():
            if not card_window or not card_window.winfo_exists():
                return
            card_window.update_idletasks()
            natural_height = card_window.winfo_reqheight()
            h = min(natural_height, 480)
            
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = screen_width - width - margin_right
            y = screen_height - h - margin_bottom
            card_window.geometry(f"{width}x{h}+{x}+{y}")

        def rebuild_ui():
            nonlocal card_window
            if not card_window or not card_window.winfo_exists():
                card_window = tk.Toplevel(root)
                card_window.overrideredirect(True)
                card_window.attributes("-topmost", True)
                card_window.configure(bg=bg)

            # Clear all widgets in card_window
            for widget in card_window.winfo_children():
                widget.destroy()

            # Main container with a nice border
            outer_frame = tk.Frame(card_window, bg=bg, highlightthickness=1, highlightbackground=accent)
            outer_frame.pack(fill="both", expand=True)

            # Header Frame
            header_frame = tk.Frame(outer_frame, bg=bg, height=45)
            header_frame.pack(fill="x", side="top", padx=12, pady=6)
            
            title_lbl = tk.Label(
                header_frame,
                text="Upload Notifications",
                bg=bg,
                fg=text,
                font=title_font,
                anchor="w"
            )
            title_lbl.pack(side="left", fill="y")

            # Small close window button (top right)
            close_win_btn = tk.Button(
                header_frame,
                text="×",
                bg=bg,
                fg=muted,
                activebackground=bg,
                activeforeground=text,
                relief="flat",
                bd=0,
                font=tkfont.Font(family="Segoe UI", size=-18),
                command=close_card,
                cursor="hand2"
            )
            close_win_btn.pack(side="right", fill="y", padx=5)

            # If empty
            if not notifications_data:
                empty_lbl = tk.Label(
                    outer_frame,
                    text="No new notifications",
                    bg=bg,
                    fg=muted,
                    font=body_font
                )
                empty_lbl.pack(fill="both", expand=True, pady=20)
                update_card_position()
                card_window.deiconify()
                return

            # Footer Frame (packed first at the bottom to prevent gaps and overlay issues)
            footer_frame = tk.Frame(outer_frame, bg=bg, height=35)
            footer_frame.pack(fill="x", side="bottom", padx=12, pady=6)

            total_count = len(notifications_data)

            # Left side: Counter showing total files
            if total_count > 0:
                counter_text = f"Total: {total_count} files"
                counter_lbl = tk.Label(
                    footer_frame,
                    text=counter_text,
                    bg=bg,
                    fg=muted,
                    font=body_font,
                    anchor="w"
                )
                counter_lbl.pack(side="left", fill="y")

            # Right side: Clear text button in RED fg
            clear_btn = tk.Button(
                footer_frame,
                text="Clear",
                bg=bg,
                fg=red_color,
                activebackground=bg,
                activeforeground=red_hover,
                font=body_font,
                relief="flat",
                bd=0,
                cursor="hand2",
                command=clear_all
            )
            clear_btn.pack(side="right", fill="y")

            # List container: scrollable canvas without visible scrollbar scroll widget
            list_container = tk.Frame(outer_frame, bg=bg)
            list_container.pack(fill="both", expand=True, padx=6)

            canvas = tk.Canvas(list_container, bg=bg, highlightthickness=0)
            canvas.pack(fill="both", expand=True)

            scrollable_frame = tk.Frame(canvas, bg=bg)
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=width - 20)

            # Bind mouse wheel for scrolling (without showing scrollbar UI)
            def _on_mousewheel(event):
                # Only scroll if content is larger than the visible canvas height
                if canvas.winfo_height() < scrollable_frame.winfo_height():
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            
            def bind_mousewheel(widget):
                widget.bind("<MouseWheel>", _on_mousewheel)
                for child in widget.winfo_children():
                    bind_mousewheel(child)

            # Build list items (md list styling) - newest files at the top
            for item in reversed(notifications_data):
                item_frame = tk.Frame(scrollable_frame, bg=bg, cursor="hand2")
                item_frame.pack(fill="x", pady=2, padx=4)

                # Determine sizes, colors and labels based on status
                if item.get("status") == "uploading":
                    bullet_color = "#eab308"  # Yellow for progress
                    size_color = "#eab308"
                    size_text = f"Uploading: {item.get('percent', 0)}%"
                    sep_text = ""
                    time_text = ""
                else:
                    # Determine bullet color based on file extension
                    ext = os.path.splitext(item["filename"])[1].lower()
                    if ext == '.pdf':
                        bullet_color = "#ef4444"  # Red
                    elif ext in ['.txt', '.md', '.doc', '.docx']:
                        bullet_color = "#00bcf2"  # Blue/Cyan
                    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
                        bullet_color = "#ec4899"  # Pink/Purple
                    elif ext in ['.zip', '.rar', '.tar', '.gz', '.7z']:
                        bullet_color = "#f97316"  # Orange
                    elif ext in ['.mp3', '.wav', '.mp4', '.mkv', '.avi']:
                        bullet_color = "#d946ef"  # Magenta
                    else:
                        bullet_color = "#10b981"  # Emerald Green

                    # Determine size color based on bytes
                    sb = item.get("size_bytes", 0)
                    if sb < 1024 * 1024:  # Under 1 MB
                        size_color = "#a3a3a3"  # Soft muted silver
                    elif sb < 10 * 1024 * 1024:  # 1 MB - 10 MB
                        size_color = "#3b82f6"  # Bright Blue
                    elif sb < 50 * 1024 * 1024:  # 10 MB - 50 MB
                        size_color = "#f97316"  # Orange
                    else:  # Over 50 MB
                        size_color = "#ef4444"  # Red
                    
                    size_text = item['size_str']
                    sep_text = " • "
                    time_text = item['arrival_time']

                bullet_lbl = tk.Label(
                    item_frame,
                    text="•",
                    bg=bg,
                    fg=bullet_color,
                    font=list_font,
                    anchor="w"
                )
                bullet_lbl.pack(side="left", padx=(4, 6))

                # Time label on right
                time_lbl = tk.Label(
                    item_frame,
                    text=time_text,
                    bg=bg,
                    fg=muted,
                    font=list_font,
                    anchor="e"
                )
                time_lbl.pack(side="right", padx=(0, 6) if time_text else 0)

                # Separator bullet
                sep_lbl = tk.Label(
                    item_frame,
                    text=sep_text,
                    bg=bg,
                    fg="#444444",
                    font=list_font
                )
                sep_lbl.pack(side="right")

                # Size/Progress label
                size_lbl = tk.Label(
                    item_frame,
                    text=size_text,
                    bg=bg,
                    fg=size_color,
                    font=list_font,
                    anchor="e"
                )
                size_lbl.pack(side="right")

                display_name = shorten_notification_filename(item["filename"], max_length=28)
                name_lbl = tk.Label(
                    item_frame,
                    text=display_name,
                    bg=bg,
                    fg=text,
                    font=list_font,
                    anchor="w",
                    justify="left"
                )
                name_lbl.pack(side="left")

                # Dots label fills the expand area in between
                dots_lbl = tk.Label(
                    item_frame,
                    text="............................................................",
                    bg=bg,
                    fg="#333333",  # Subtle grey dots
                    font=list_font,
                    anchor="w"
                )
                dots_lbl.pack(side="left", fill="x", expand=True, padx=4)

                def make_click_cmd(it=item):
                    return lambda e=None: click_item(it)

                # Bind hover events for smooth UI interaction
                def make_hover_enter(frame=item_frame, blbl=bullet_lbl, nlbl=name_lbl, dlbl=dots_lbl, tlbl=time_lbl, slbl=sep_lbl, szlbl=size_lbl):
                    return lambda e: [
                        frame.configure(bg=item_hover_bg), 
                        blbl.configure(bg=item_hover_bg), 
                        nlbl.configure(bg=item_hover_bg),
                        dlbl.configure(bg=item_hover_bg),
                        tlbl.configure(bg=item_hover_bg),
                        slbl.configure(bg=item_hover_bg),
                        szlbl.configure(bg=item_hover_bg)
                    ]
                def make_hover_leave(frame=item_frame, blbl=bullet_lbl, nlbl=name_lbl, dlbl=dots_lbl, tlbl=time_lbl, slbl=sep_lbl, szlbl=size_lbl):
                    return lambda e: [
                        frame.configure(bg=bg), 
                        blbl.configure(bg=bg), 
                        nlbl.configure(bg=bg),
                        dlbl.configure(bg=bg),
                        tlbl.configure(bg=bg),
                        slbl.configure(bg=bg),
                        szlbl.configure(bg=bg)
                    ]

                item_frame.bind("<Enter>", make_hover_enter())
                item_frame.bind("<Leave>", make_hover_leave())
                item_frame.bind("<Button-1>", make_click_cmd())
                bullet_lbl.bind("<Button-1>", make_click_cmd())
                name_lbl.bind("<Button-1>", make_click_cmd())
                dots_lbl.bind("<Button-1>", make_click_cmd())
                time_lbl.bind("<Button-1>", make_click_cmd())
                sep_lbl.bind("<Button-1>", make_click_cmd())
                size_lbl.bind("<Button-1>", make_click_cmd())

            bind_mousewheel(canvas)
            update_card_position()
            card_window.deiconify()

        def click_item(item):
            if item.get("status") == "uploading":
                return
            open_file_folder(item["file_path"])
            remove_item(item)

        def remove_item(item):
            if item in notifications_data:
                notifications_data.remove(item)
            if not notifications_data:
                close_card()
            else:
                rebuild_ui()

        def clear_all():
            notifications_data.clear()
            close_card()

        def close_card():
            nonlocal card_window
            if card_window and card_window.winfo_exists():
                card_window.destroy()
            card_window = None

        def poll_notifications():
            added_any = False
            nonlocal notification_counter
            while True:
                try:
                    item_tuple = NOTIFICATION_QUEUE.get_nowait()
                except queue.Empty:
                    break

                if len(item_tuple) == 4 and item_tuple[0] == "progress":
                    _, filename, percent, size_bytes = item_tuple
                    
                    # Calculate size_str
                    temp_size = float(size_bytes)
                    size_str = ""
                    for unit in ['B', 'KB', 'MB', 'GB']:
                        if temp_size < 1024.0:
                            size_str = f"{temp_size:.1f} {unit}" if unit != 'B' else f"{int(temp_size)} B"
                            break
                        temp_size /= 1024.0
                    if not size_str:
                        size_str = "0 B"

                    # Find existing item
                    existing = None
                    for it in notifications_data:
                        if it["filename"] == filename and it.get("status") == "uploading":
                            existing = it
                            break
                    
                    if existing:
                        existing["percent"] = percent
                        existing["size_bytes"] = size_bytes
                        existing["size_str"] = size_str
                    else:
                        notification_counter += 1
                        import datetime
                        arrival_time = datetime.datetime.now().strftime("%I:%M%p").lstrip('0').lower()
                        notifications_data.append({
                            "id": notification_counter,
                            "filename": filename,
                            "file_path": "",
                            "size_bytes": size_bytes,
                            "size_str": size_str,
                            "arrival_time": arrival_time,
                            "status": "uploading",
                            "percent": percent
                        })
                    added_any = True

                else:
                    # Final/completed item
                    if len(item_tuple) == 5:
                        filename, file_path, size_bytes, size_str, arrival_time = item_tuple
                    elif len(item_tuple) == 4:
                        filename, file_path, size_str, arrival_time = item_tuple
                        size_bytes = 0
                    else:
                        filename, file_path = item_tuple
                        size_str = "0 B"
                        size_bytes = 0
                        import datetime
                        arrival_time = datetime.datetime.now().strftime("%I:%M%p").lstrip('0').lower()

                    # Find existing uploading item and upgrade it
                    existing = None
                    for it in notifications_data:
                        if it["filename"] == filename and it.get("status") == "uploading":
                            existing = it
                            break
                    
                    if existing:
                        existing["status"] = "completed"
                        existing["file_path"] = file_path
                        existing["size_bytes"] = size_bytes
                        existing["size_str"] = size_str
                        existing["arrival_time"] = arrival_time
                    else:
                        notification_counter += 1
                        notifications_data.append({
                            "id": notification_counter,
                            "filename": filename,
                            "file_path": file_path,
                            "size_bytes": size_bytes,
                            "size_str": size_str,
                            "arrival_time": arrival_time,
                            "status": "completed"
                        })
                    added_any = True

            if added_any:
                rebuild_ui()

            root.after(100, poll_notifications)

        poll_notifications()
        root.mainloop()
    except Exception as e:
        print(f"Notification manager error: {e}")

# HTML template within the Python file (instead of an external index.html)
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="shortcut icon" href="https://cdn-icons-png.flaticon.com/512/2840/2840124.png" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Awesome File Share</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

        :root {
            --primary-color: #4CAF50;
            --primary-hover-color: #45a049;
            --danger-color: #FF5733;
            --danger-hover-color: #C70039;
            --background-color: #eef1f5;
            --card-background-color: #ffffff;
            --text-color: #333;
            --light-text-color: #777;
            --border-color: #ddd;
            --shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }

        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 40px 20px;
            background-color: var(--background-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }

        .container {
            background-color: var(--card-background-color);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 30px 40px;
            width: 100%;
            max-width: 700px;
            box-sizing: border-box;
            margin-bottom: 30px;
        }

        h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 30px;
            font-weight: 700;
        }

        form {
            margin-bottom: 25px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        input[type="file"] {
            padding: 12px;
            font-size: 1rem;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            background-color: #f9f9f9;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }

        input[type="file"]::-webkit-file-upload-button {
            background-color: var(--primary-color);
            color: white;
            padding: 8px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            margin-right: 15px;
            transition: background-color 0.3s ease;
        }

        input[type="file"]::-webkit-file-upload-button:hover {
            background-color: var(--primary-hover-color);
        }

        .button-container {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 15px;
        }

        button {
            padding: 12px 25px;
            font-size: 1rem;
            font-weight: 600;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        button:hover {
            transform: translateY(-2px);
        }

        button.upload-button {
            background-color: var(--primary-color);
        }

        button.upload-button:hover {
            background-color: var(--primary-hover-color);
        }

        button.clean-button {
            background-color: var(--danger-color);
        }

        button.clean-button:hover {
            background-color: var(--danger-hover-color);
        }

        .circular-progress-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 30px;
            margin-bottom: 20px;
        }

        .circular-progress {
            position: relative;
            width: 150px;
            height: 150px;
            border-radius: 50%;
            background: conic-gradient(var(--primary-color) 0%, #e0e0e0 0%);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
        }

        .circular-progress::before {
            content: '';
            position: absolute;
            width: 120px; /* Inner circle size */
            height: 120px;
            border-radius: 50%;
            background-color: var(--card-background-color);
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .progress-percentage {
            position: relative; /* To ensure it's above the pseudo-element */
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--text-color);
            z-index: 1; /* Ensure text is on top */
        }

        #upload-status {
            margin-top: 20px;
            padding: 15px;
            background-color: #f0f8ff;
            border: 1px solid #cceeff;
            border-radius: 8px;
            text-align: center;
            color: var(--light-text-color);
            min-height: 50px; /* Ensure some height even when empty */
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        #upload-status p {
            margin: 0;
            font-weight: 500;
            color: var(--primary-color);
        }
        #upload-status p.error {
            color: var(--danger-color);
        }


        .file-list-section {
            background-color: var(--card-background-color);
            border-radius: 12px;
            box-shadow: var(--shadow);
            padding: 30px 40px;
            width: 100%;
            max-width: 700px;
            box-sizing: border-box;
        }

        .file-list-section h2 {
            text-align: center;
            color: var(--primary-color);
            margin-bottom: 25px;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
        }

        .file-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        .file-item:last-child {
            border-bottom: none;
        }

        .download-link {
            color: #007BFF;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }

        .download-link:hover {
            color: #0056b3;
            text-decoration: underline;
        }
        
        .flash-messages {
            list-style: none;
            padding: 0;
            margin: 0 0 20px 0;
        }
        .flash {
            font-weight: bold;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid;
            text-align: center;
        }
        .flash.success {
            color: var(--primary-color);
            background-color: #e6ffe6;
            border-color: var(--primary-color);
        }
        .flash.error {
            color: var(--danger-color);
            background-color: #ffe6e6;
            border-color: var(--danger-color);
        }
        .flash.warning {
            color: #FFA500; /* Orange */
            background-color: #fffacd; /* LemonChiffon */
            border-color: #FFD700; /* Gold */
        }
        .flash.info {
            color: #4682B4; /* SteelBlue */
            background-color: #e0f2f7; /* Light blue */
            border-color: #B0E0E6; /* PowderBlue */
        }
    </style>
</head>
<body>

    <div class="container">
        <h1>Awesome File Share</h1>

        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <ul class="flash-messages">
                    {% for category, message in messages %}
                        <li class="flash {{ category }}">{{ message }}</li>
                    {% endfor %}
                </ul>
            {% endif %}
        {% endwith %}

        <form id="upload-form">
            <input type="file" id="file-input" name="files" multiple required>

            <div class="button-container">
                <button type="submit" class="upload-button">Upload Files</button>
            </div>
        </form>

        <form id="clean-form" method="POST" action="/clean">
            <div class="button-container">
                <button type="submit" class="clean-button">Clean Directory</button>
            </div>
        </form>

        <div class="circular-progress-wrapper">
            <div class="circular-progress" id="circular-progress">
                <div class="progress-percentage" id="progress-percentage">0%</div>
            </div>
            <div id="upload-status">Upload status will appear here.</div>
        </div>
    </div>

    <div class="container file-list-section">
        <h2>Available Files</h2>
        <ul class="file-list">
            {% if files %}
                {% for file in files %}
                    <li class="file-item">
                        <a class="download-link" href="/uploads/{{ file }}">{{ file }}</a>
                    </li>
                {% endfor %}
            {% else %}
                <li class="file-item" style="justify-content: center; color: var(--light-text-color);">No files available.</li>
            {% endif %}
        </ul>
    </div>

    <script>
        document.getElementById("upload-form").addEventListener("submit", async function(event) {
            event.preventDefault();

            var files = document.getElementById("file-input").files;
            var totalFiles = files.length;
            if (totalFiles === 0) {
                alert("Please select at least one file to upload.");
                return;
            }

            var uploadedFilesCount = 0;
            var uploadStatusDiv = document.getElementById("upload-status");
            var progressCircle = document.getElementById("circular-progress");
            var progressText = document.getElementById("progress-percentage");

            uploadStatusDiv.innerHTML = `<p>Starting upload...</p>`;
            progressText.innerText = "0%";
            progressCircle.style.background = 'conic-gradient(var(--primary-color) 0%, #e0e0e0 0%)';

            for (var i = 0; i < totalFiles; i++) {
                var file = files[i];
                var formData = new FormData();
                formData.append("file", file); // Changed 'files' to 'file' as we are sending one at a time

                uploadStatusDiv.innerHTML = `<p>Preparing to upload: <strong>${file.name}</strong></p>`;

                try {
                    await new Promise((resolve, reject) => {
                        var xhr = new XMLHttpRequest();
                        xhr.open("POST", "/", true);

                        xhr.upload.onprogress = function(event) {
                            if (event.lengthComputable) {
                                var percentComplete = (event.loaded / event.total) * 100;
                                
                                // Calculate overall progress considering files already uploaded
                                var overallProgress = ((uploadedFilesCount * 100) + percentComplete) / totalFiles;
                                
                                progressCircle.style.background = `conic-gradient(var(--primary-color) ${overallProgress}%, #e0e0e0 ${overallProgress}%)`;
                                progressText.innerText = `${Math.round(overallProgress)}%`;

                                uploadStatusDiv.innerHTML = `<p>Uploading <strong>${file.name}</strong>: ${Math.round(percentComplete)}%</p>`;

                                // Send progress update to server (throttled to avoid spamming)
                                var pctRounded = Math.round(percentComplete);
                                if (!xhr.lastProgressTime || (Date.now() - xhr.lastProgressTime > 150) || pctRounded === 100) {
                                    xhr.lastProgressTime = Date.now();
                                    fetch('/upload-progress', {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({
                                            filename: file.name,
                                            percent: pctRounded,
                                            size_bytes: event.total
                                        })
                                    }).catch(() => {});
                                }
                            }
                        };

                        xhr.onload = function() {
                            if (xhr.status === 200) {
                                uploadedFilesCount++;
                                uploadStatusDiv.innerHTML = `<p style="color: var(--primary-color);"><strong>${file.name}</strong> uploaded successfully!</p>`;
                                resolve();
                            } else {
                                uploadStatusDiv.innerHTML = `<p class="error">Error uploading <strong>${file.name}</strong>. Status: ${xhr.status}</p>`;
                                alert("Error uploading " + file.name + "! Status: " + xhr.status);
                                reject(new Error(`Upload failed with status ${xhr.status}`));
                            }
                        };

                        xhr.onerror = function() {
                            uploadStatusDiv.innerHTML = `<p class="error">Network error during upload of <strong>${file.name}</strong>.</p>`;
                            alert("Network error during upload of " + file.name);
                            reject(new Error("Network error"));
                        };

                        xhr.send(formData);
                    });
                } catch (error) {
                    console.error("Upload process error:", error);
                    // Continue to next file even if one fails, or break if desired
                }
            }

            // After all files attempt to upload
            if (uploadedFilesCount === totalFiles) {
                uploadStatusDiv.innerHTML = `<p style="color: var(--primary-color);">All files uploaded successfully!</p>`;
            } else if (uploadedFilesCount > 0) {
                uploadStatusDiv.innerHTML = `<p class="error">Finished with ${uploadedFilesCount} of ${totalFiles} files uploaded successfully.</p>`;
            } else {
                 uploadStatusDiv.innerHTML = `<p class="error">No files were uploaded successfully.</p>`;
            }
            
            // Give a moment for the user to see the final status before reloading
            setTimeout(() => {
                window.location.reload(); 
            }, 1500); // Reload after 1.5 seconds
        });
    </script>

</body>
</html>
'''

@app.route("/upload-progress", methods=["POST"])
def upload_progress():
    data = request.json or {}
    filename = data.get("filename")
    percent = data.get("percent", 0)
    size_bytes = data.get("size_bytes", 0)
    if filename:
        update_upload_progress(filename, percent, size_bytes)
    return '', 204

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash("No file selected for upload.", "error")
                return '', 400 

            # Check if original filename is provided (from Android app)
            original_filename = request.form.get('original_filename')
            if original_filename:
                # Use original filename but make it safe for filesystem
                filename = create_safe_filename(original_filename)
            else:
                # Fallback to secure_filename for web uploads
                filename = secure_filename(file.filename)
            
            # Create directory structure if filename contains path separators
            file_path = os.path.join(app.config['SHARE_FOLDER'], filename)
            directory = os.path.dirname(file_path)
            if directory and directory != app.config['SHARE_FOLDER']:
                os.makedirs(directory, exist_ok=True)

            try:
                # Handle duplicate filenames by adding a number
                counter = 1
                base_name, extension = os.path.splitext(filename)
                original_file_path = file_path
                while os.path.exists(file_path):
                    filename = f"{base_name} ({counter}){extension}"
                    file_path = os.path.join(app.config['SHARE_FOLDER'], filename)
                    counter += 1
                
                # Save file with progress tracking for large files
                start_time = time.time()
                file.save(file_path)
                end_time = time.time()
                
                # Log upload info for debugging
                file_size = os.path.getsize(file_path)
                upload_time = end_time - start_time
                speed = file_size / upload_time if upload_time > 0 else 0
                
                print(f"✅ Uploaded: {filename} ({file_size} bytes) in {upload_time:.2f}s ({speed/1024:.1f} KB/s)")
                show_upload_notification(filename, file_path)
                
                flash(f"File '{filename}' uploaded successfully.", "success")
                return '', 200  # Success
            except Exception as e:
                print(f"❌ Upload error for '{filename}': {e}")
                flash(f"Server error saving '{filename}': {e}", "error")
                return '', 500 # Internal Server Error
        else:
            flash("No file part in the request.", "error")
            return '', 400

    files = os.listdir(app.config['SHARE_FOLDER'])
    files.sort() 
    return render_template_string(html_template, files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['SHARE_FOLDER'], filename)
    except FileNotFoundError:
        flash("File not found.", "error")
        return redirect(url_for('index'))

@app.route('/clean', methods=["POST"])
def clean():
    success_count = 0
    error_count = 0
    for filename in os.listdir(app.config['SHARE_FOLDER']):
        file_path = os.path.join(app.config['SHARE_FOLDER'], filename)
        try:
            os.remove(file_path)
            success_count += 1
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
            error_count += 1
    
    if success_count > 0 and error_count == 0:
        flash(f"All {success_count} files have been successfully deleted.", "success")
    elif success_count > 0 and error_count > 0:
        flash(f"Deleted {success_count} files, but encountered errors with {error_count} files.", "warning")
    elif error_count > 0:
        flash("Could not delete any files due to errors.", "error")
    else:
        flash("No files to delete.", "info")

    return redirect(url_for('index'))

if __name__ == "__main__":
    # Optimized server settings for better performance
    app.run(
        host="0.0.0.0", 
        port=5002, 
        debug=False,  # Disable debug for better performance
        threaded=True,  # Enable threading for concurrent requests
        use_reloader=False  # Disable auto-reloader for stability
    )
