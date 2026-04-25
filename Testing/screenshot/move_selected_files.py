import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox

import pythoncom
import win32clipboard
import win32com.client
import win32gui
import win32process
from pywinauto import Desktop


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "folders.json")
PHOTOS_TITLE_SUFFIXES = [
    " - Microsoft Photos",
    " - Photos",
]


def load_folders():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not data:
                    return []
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], str):
                    return [{"path": p, "color": "#00ff41"} for p in data]
                return data
    except Exception as e:
        print(f"Error loading config: {e}")
    return []


def save_folders(folders):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(folders, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Could not save config: {e}")


def get_foreground_window_info():
    hwnd = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(hwnd).strip()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    process_name = ""
    try:
        import psutil

        process_name = psutil.Process(pid).name()
    except Exception:
        pass

    return {
        "hwnd": hwnd,
        "title": title,
        "pid": pid,
        "process_name": process_name.lower(),
    }


def normalize_paths(paths):
    seen = set()
    normalized = []
    for raw_path in paths:
        try:
            path = str(Path(raw_path).resolve())
        except Exception:
            path = os.path.abspath(raw_path)
        key = os.path.normcase(path)
        if key in seen:
            continue
        if os.path.isfile(path):
            seen.add(key)
            normalized.append(path)
    return normalized


def get_paths_from_args():
    if len(sys.argv) <= 1:
        return []
    return normalize_paths(sys.argv[1:])


def get_clipboard_files():
    files = []
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            files = list(win32clipboard.GetClipboardData(win32clipboard.CF_HDROP))
    except Exception:
        return []
    finally:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
    return normalize_paths(files)


def iter_explorer_windows():
    pythoncom.CoInitialize()
    shell = win32com.client.Dispatch("Shell.Application")
    for window in shell.Windows():
        try:
            hwnd = int(window.HWND)
        except Exception:
            continue
        yield window, hwnd


def get_explorer_selected_files(prefer_hwnd=None):
    fallback = []
    for window, hwnd in iter_explorer_windows():
        try:
            selected = [item.Path for item in window.Document.SelectedItems()]
        except Exception:
            continue

        selected = normalize_paths(selected)
        if not selected:
            continue

        if prefer_hwnd and hwnd == prefer_hwnd:
            return selected

        if not fallback:
            fallback = selected
    return fallback


def get_explorer_locations():
    locations = []
    seen = set()
    for window, _hwnd in iter_explorer_windows():
        try:
            folder = window.Document.Folder.Self.Path
        except Exception:
            continue
        if not folder or not os.path.isdir(folder):
            continue
        key = os.path.normcase(folder)
        if key in seen:
            continue
        seen.add(key)
        locations.append(folder)
    return locations


def get_photos_window_file(info):
    title = info["title"]
    if not title:
        return []

    for suffix in PHOTOS_TITLE_SUFFIXES:
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()
            break

    if not title or title.lower() in {"photos", "microsoft photos"}:
        return []

    possible_dirs = get_explorer_locations()
    for folder in possible_dirs:
        candidate = os.path.join(folder, title)
        if os.path.isfile(candidate):
            return [candidate]

    try:
        window = Desktop(backend="uia").window(handle=info["hwnd"])
        texts = set()
        for element in window.descendants(control_type="Text"):
            value = (element.window_text() or "").strip()
            if value:
                texts.add(value)
        for text in texts:
            if os.path.isfile(text):
                return [text]
    except Exception:
        pass

    return []


def detect_selected_files():
    paths = get_paths_from_args()
    if paths:
        return paths

    info = get_foreground_window_info()
    paths = get_explorer_selected_files(prefer_hwnd=info["hwnd"])
    if paths:
        return paths

    if "photos" in info["process_name"] or info["process_name"] == "applicationframehost.exe":
        paths = get_photos_window_file(info)
        if paths:
            return paths

    paths = get_clipboard_files()
    if paths:
        return paths

    return []


def build_renamed_path(destination):
    folder = os.path.dirname(destination)
    stem = Path(destination).stem
    suffix = Path(destination).suffix
    counter = 1

    while True:
        candidate = os.path.join(folder, f"{stem} ({counter}){suffix}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


class ConflictDialog:
    def __init__(self, parent, source_path, destination_path):
        self.result = None
        self.source_path = source_path
        self.destination_path = destination_path

        self.window = tk.Toplevel(parent)
        self.window.title("Name Conflict")
        self.window.configure(bg="#0e0e0e")
        self.window.attributes("-topmost", True)
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()

        frame = tk.Frame(self.window, bg="#0e0e0e", padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="File already exists",
            font=("JetBrains Mono", 11, "bold"),
            bg="#0e0e0e",
            fg="#ffcc00",
        ).pack(anchor="w")

        tk.Label(
            frame,
            text=os.path.basename(source_path),
            font=("JetBrains Mono", 10),
            bg="#0e0e0e",
            fg="#ffffff",
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(10, 4))

        tk.Label(
            frame,
            text=destination_path,
            font=("JetBrains Mono", 8),
            bg="#0e0e0e",
            fg="#9f9f9f",
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 12))

        buttons = tk.Frame(frame, bg="#0e0e0e")
        buttons.pack(fill="x")

        tk.Button(
            buttons,
            text="Rename",
            command=lambda: self.finish("rename"),
            font=("JetBrains Mono", 9),
            bg="#00ff41",
            fg="#000000",
            relief="flat",
            padx=12,
            cursor="hand2",
        ).pack(side="left")

        tk.Button(
            buttons,
            text="Skip",
            command=lambda: self.finish("skip"),
            font=("JetBrains Mono", 9),
            bg="#2a2a2a",
            fg="#ffffff",
            relief="flat",
            padx=12,
            cursor="hand2",
        ).pack(side="left", padx=(8, 0))

        self.window.bind("<Escape>", lambda _e: self.finish("skip"))
        self.center(parent)

    def center(self, parent):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        if parent.winfo_viewable():
            x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        else:
            x = (self.window.winfo_screenwidth() - width) // 2
            y = (self.window.winfo_screenheight() - height) // 2
        self.window.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def finish(self, result):
        self.result = result
        self.window.destroy()

    def show(self):
        self.window.wait_window()
        return self.result


class FolderChooser:
    def __init__(self, folders, file_paths):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.choice = None
        self.folders = folders
        self.file_paths = file_paths
        self.edit_mode = False
        self.is_dialog_open = False

        self.bg_color = "#0e0e0e"
        self.fg_color = "#ffffff"
        self.accent_main = "#00ff41"
        self.accent_edit = "#ffcc00"

        self.font_name = "JetBrainsMono NFP"
        self.font_main = (self.font_name, 10)
        self.font_icon = (self.font_name, 36)
        self.font_small = (self.font_name, 8)
        self.font_title = (self.font_name + " Bold", 11)

        self.root.config(bg=self.accent_main)

        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=1, pady=1)

        self.header = tk.Frame(self.container, bg=self.bg_color, cursor="fleur")
        self.header.pack(fill="x", padx=15, pady=(15, 5))

        self.label_title = tk.Label(
            self.header,
            text=f"MOVE {len(file_paths)} FILE{'S' if len(file_paths) != 1 else ''}",
            font=self.font_title,
            bg=self.bg_color,
            fg=self.accent_main,
            cursor="arrow",
        )
        self.label_title.pack(side="left")

        self.btn_edit_toggle = tk.Button(
            self.header,
            text="EDIT: OFF",
            command=self.toggle_edit_mode,
            font=self.font_small,
            bg="#1a1a1a",
            fg="#666666",
            activebackground=self.accent_edit,
            activeforeground="black",
            relief="flat",
            bd=0,
            padx=10,
            cursor="hand2",
        )
        self.btn_edit_toggle.pack(side="right")

        self.header.bind("<ButtonPress-1>", self.start_move)
        self.header.bind("<B1-Motion>", self.do_move)

        preview_text = "\n".join(os.path.basename(path) for path in file_paths[:3])
        if len(file_paths) > 3:
            preview_text += f"\n+{len(file_paths) - 3} more"
        self.label_preview = tk.Label(
            self.container,
            text=preview_text,
            font=self.font_small,
            bg=self.bg_color,
            fg="#8f8f8f",
            justify="left",
            anchor="w",
        )
        self.label_preview.pack(fill="x", padx=15)

        self.list_container = tk.Frame(self.container, bg=self.bg_color)
        self.list_container.pack(fill="both", expand=True, padx=10, pady=10)
        self.render_folders()

        self.footer = tk.Frame(self.container, bg=self.bg_color)
        self.footer.pack(fill="x", pady=(0, 10))

        self.btn_close = tk.Button(
            self.footer,
            text="EXIT [ESC]",
            command=self.root.destroy,
            font=self.font_small,
            bg=self.bg_color,
            fg="#555555",
            activebackground="#ff0000",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=20,
            cursor="hand2",
        )
        self.btn_close.pack()

        self.update_window_size()
        self.root.bind("<Escape>", lambda _e: self.root.destroy())
        self.root.bind("<FocusOut>", self.on_focus_out)
        self.root.after(100, self.force_focus)

    def begin_dialog(self):
        self.is_dialog_open = True
        try:
            self.root.grab_release()
        except Exception:
            pass

    def end_dialog(self):
        self.is_dialog_open = False
        self.force_focus()

    def on_focus_out(self, _event):
        if self.is_dialog_open:
            return
        if self.root.focus_displayof() is None:
            self.root.destroy()

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        color = self.accent_edit if self.edit_mode else "#666666"
        text = "EDIT: ON" if self.edit_mode else "EDIT: OFF"
        self.btn_edit_toggle.config(fg=color, text=text)
        self.render_folders()

    def update_window_size(self):
        self.list_container.update_idletasks()
        width = 820
        total_items = len(self.folders) + 1
        rows = max(1, (total_items + 4) // 5)
        height = 155 + (rows * 135)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - width / 2)
        center_y = int(screen_height / 2 - height / 2)
        self.root.geometry(f"{width}x{height}+{center_x}+{center_y}")

    def render_folders(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        items = []
        for i, folder_data in enumerate(self.folders):
            icon = folder_data.get("icon", "\ueaf7")
            items.append((folder_data["path"], folder_data["color"], icon, i))

        for idx, (path, color, icon, folder_index) in enumerate(items):
            row = idx // 5
            col = idx % 5
            self.create_folder_card(path, color, icon, row, col, folder_index)

        next_idx = len(items)
        self.create_add_button(next_idx // 5, next_idx % 5)

    def create_folder_card(self, path, color, icon, row, col, index):
        card = tk.Frame(self.list_container, bg="#1a1a1a", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        name = os.path.basename(path) or path

        icon_label = tk.Label(card, text=icon, font=self.font_icon, bg="#1a1a1a", fg=color)
        icon_label.pack(pady=(5, 0))

        name_label = tk.Label(
            card,
            text=name.upper()[:16],
            font=self.font_main,
            bg="#1a1a1a",
            fg=self.fg_color,
        )
        name_label.pack()

        if self.edit_mode:
            card.config(highlightbackground=self.accent_edit, highlightthickness=1)

            col_label = tk.Label(card, text="C", font=self.font_small, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            col_label.place(x=10, y=94)
            col_label.bind("<Button-1>", lambda _e, i=index: self.change_folder_color(i))

            icon_edit = tk.Label(card, text="I", font=self.font_small, bg="#1a1a1a", fg=self.accent_edit, cursor="hand2")
            icon_edit.place(x=70, y=94)
            icon_edit.bind("<Button-1>", lambda _e, i=index: self.change_folder_icon(i))

            delete_label = tk.Label(card, text="X", font=self.font_small, bg="#1a1a1a", fg="#ff4444", cursor="hand2")
            delete_label.place(x=128, y=94)
            delete_label.bind("<Button-1>", lambda _e, i=index: self.remove_folder(i))

        widgets = [card, icon_label, name_label]
        for widget in widgets:
            if not self.edit_mode:
                widget.bind("<Button-1>", lambda _e, p=path: self.set_choice(p))
                widget.bind("<Button-3>", lambda _e, p=path: self.open_explorer(p))
                widget.config(cursor="hand2")

            widget.bind("<Enter>", lambda _e, c=card: self.on_hover(c))
            widget.bind("<Leave>", lambda _e, c=card: self.on_leave(c))

    def create_add_button(self, row, col):
        card = tk.Frame(self.list_container, bg="#121212", width=150, height=120)
        card.grid(row=row, column=col, padx=5, pady=5)
        card.pack_propagate(False)

        icon_label = tk.Label(card, text="+", font=(self.font_name, 36), bg="#121212", fg="#444444")
        icon_label.pack(expand=True)

        card.bind("<Button-1>", lambda _e: self.add_new_folder())
        icon_label.bind("<Button-1>", lambda _e: self.add_new_folder())

        for widget in [card, icon_label]:
            widget.bind("<Enter>", lambda _e: self.on_add_hover(card, icon_label))
            widget.bind("<Leave>", lambda _e: self.on_add_leave(card, icon_label))
            widget.config(cursor="hand2")

    def on_add_hover(self, card, label):
        card.config(bg="#1a1a1a")
        label.config(bg="#1a1a1a")

    def on_add_leave(self, card, label):
        card.config(bg="#121212")
        label.config(bg="#121212")

    def on_hover(self, card):
        if not self.edit_mode:
            card.config(bg="#252525")
            for widget in card.winfo_children():
                widget.config(bg="#252525")

    def on_leave(self, card):
        if not self.edit_mode:
            card.config(bg="#1a1a1a")
            for widget in card.winfo_children():
                widget.config(bg="#1a1a1a")

    def open_explorer(self, path):
        if os.path.exists(path):
            subprocess.run(["explorer", os.path.normpath(path)], check=False)

    def change_folder_color(self, index):
        self.begin_dialog()
        color = colorchooser.askcolor(
            title="Choose Folder Color",
            initialcolor=self.folders[index]["color"],
            parent=self.root,
        )[1]
        self.end_dialog()
        if color:
            self.folders[index]["color"] = color
            save_folders(self.folders)
            self.render_folders()

    def change_folder_icon(self, index):
        from tkinter import simpledialog

        self.begin_dialog()
        new_icon = simpledialog.askstring(
            "Folder Icon",
            "Paste new icon glyph:",
            initialvalue=self.folders[index].get("icon", "\ueaf7"),
            parent=self.root,
        )
        self.end_dialog()
        if new_icon:
            self.folders[index]["icon"] = new_icon
            save_folders(self.folders)
            self.render_folders()

    def remove_folder(self, index):
        self.begin_dialog()
        confirm = messagebox.askyesno("Confirm", "Remove this folder from list?", parent=self.root)
        self.end_dialog()
        if confirm:
            self.folders.pop(index)
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def add_new_folder(self):
        self.begin_dialog()
        path = filedialog.askdirectory(title="Select Folder to Add", parent=self.root)
        self.end_dialog()
        if path:
            self.begin_dialog()
            color = colorchooser.askcolor(title="Choose Folder Color", initialcolor="#00ff41", parent=self.root)[1]
            self.end_dialog()
            if not color:
                color = "#00ff41"
            self.folders.append({"path": path, "color": color})
            save_folders(self.folders)
            self.render_folders()
            self.update_window_size()

    def force_focus(self):
        self.root.focus_force()
        self.root.lift()
        self.root.focus_set()
        try:
            self.root.grab_set()
        except Exception:
            pass

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{x}+{y}")

    def set_choice(self, folder):
        self.choice = folder
        self.root.withdraw()
        self.root.quit()

    def get_choice(self):
        self.root.mainloop()
        return self.choice


def move_files(file_paths, destination_folder):
    moved = []
    skipped = []
    renamed = []
    dialog_root = tk.Tk()
    dialog_root.withdraw()
    dialog_root.attributes("-topmost", True)

    try:
        os.makedirs(destination_folder, exist_ok=True)

        for source_path in file_paths:
            filename = os.path.basename(source_path)
            destination_path = os.path.join(destination_folder, filename)

            if os.path.exists(destination_path):
                dialog = ConflictDialog(dialog_root, source_path, destination_path)
                decision = dialog.show()
                dialog_root.focus_force()

                if decision == "skip":
                    skipped.append(source_path)
                    continue

                destination_path = build_renamed_path(destination_path)
                renamed.append((source_path, destination_path))

            shutil.move(source_path, destination_path)
            moved.append(destination_path)
    finally:
        dialog_root.destroy()

    return moved, skipped, renamed


def show_results(moved, skipped, renamed):
    temp_root = tk.Tk()
    temp_root.withdraw()

    lines = [f"Moved: {len(moved)}"]
    if renamed:
        lines.append(f"Renamed: {len(renamed)}")
    if skipped:
        lines.append(f"Skipped: {len(skipped)}")

    messagebox.showinfo("Move Complete", "\n".join(lines), parent=temp_root)
    temp_root.destroy()


def show_error(message):
    temp_root = tk.Tk()
    temp_root.withdraw()
    messagebox.showerror("Move Selected Files", message, parent=temp_root)
    temp_root.destroy()


def main():
    try:
        file_paths = detect_selected_files()
        if not file_paths:
            show_error(
                "No files detected.\n\n"
                "Use one of these:\n"
                "- select files in File Explorer before launching\n"
                "- pass file paths from AutoHotkey as arguments\n"
                "- copy files first so the script can read them from the clipboard"
            )
            return

        folders = load_folders()
        chooser = FolderChooser(folders, file_paths)
        destination = chooser.get_choice()
        if not destination:
            return

        moved, skipped, renamed = move_files(file_paths, destination)
        chooser.root.destroy()
        show_results(moved, skipped, renamed)
    except Exception:
        import traceback

        show_error(traceback.format_exc())


if __name__ == "__main__":
    main()
