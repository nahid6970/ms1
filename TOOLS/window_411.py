import tkinter as tk
import customtkinter as ctk
import win32gui
import win32process
import win32con
import psutil
import subprocess
import ctypes

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

drag_data = {"x": 0, "y": 0}

def get_all_windows():
    windows = []
    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        cls = win32gui.GetClassName(hwnd)
        visible = win32gui.IsWindowVisible(hwnd)
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            exe = proc.name()
            exe_path = proc.exe()
        except Exception:
            exe = "N/A"
            exe_path = "N/A"
            pid = 0
        rect = win32gui.GetWindowRect(hwnd)
        windows.append({
            "hwnd": hwnd,
            "title": title or "(no title)",
            "class": cls,
            "visible": visible,
            "exe": exe,
            "exe_path": exe_path,
            "pid": pid,
            "rect": rect,
        })
    win32gui.EnumWindows(callback, None)
    return windows

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Window 411")
        self.geometry("1100x650")
        self.overrideredirect(True)
        self.resizable(True, True)
        self._all_windows = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Title bar
        title_bar = ctk.CTkFrame(self, height=36, fg_color="#1a1a2e", corner_radius=0)
        title_bar.pack(fill="x")
        title_bar.bind("<ButtonPress-1>", self._start_drag)
        title_bar.bind("<B1-Motion>", self._do_drag)

        ctk.CTkLabel(title_bar, text="  🪟 Window 411", font=("Segoe UI", 13, "bold"),
                     text_color="#e0e0ff").pack(side="left", padx=8)

        ctk.CTkButton(title_bar, text="✕", width=36, height=28, fg_color="transparent",
                      hover_color="#c0392b", command=self.destroy,
                      font=("Segoe UI", 13)).pack(side="right", padx=4, pady=4)

        # Toolbar
        toolbar = ctk.CTkFrame(self, height=40, fg_color="#12121e", corner_radius=0)
        toolbar.pack(fill="x")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        ctk.CTkEntry(toolbar, textvariable=self.search_var, placeholder_text="🔍 Search title / exe / class...",
                     width=320, height=30).pack(side="left", padx=8, pady=5)

        self.filter_var = tk.StringVar(value="All")
        ctk.CTkSegmentedButton(toolbar, values=["All", "Visible", "Hidden"],
                               variable=self.filter_var, command=lambda _: self._apply_filter(),
                               width=200).pack(side="left", padx=4)

        ctk.CTkButton(toolbar, text="⟳ Refresh", width=90, height=30,
                      command=self.refresh).pack(side="left", padx=8)

        self.count_label = ctk.CTkLabel(toolbar, text="", font=("Segoe UI", 11),
                                        text_color="#888")
        self.count_label.pack(side="right", padx=12)

        # Main area
        main = ctk.CTkFrame(self, fg_color="#0d0d1a", corner_radius=0)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=3)
        main.columnconfigure(1, weight=2)
        main.rowconfigure(0, weight=1)

        # Left: table
        left = ctk.CTkFrame(main, fg_color="#0d0d1a", corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(6,3), pady=6)
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Header row
        cols = [("HWND", 90), ("Title", 220), ("Class", 160), ("EXE", 120), ("Vis", 45)]
        hdr = ctk.CTkFrame(left, fg_color="#1a1a2e", corner_radius=4)
        hdr.grid(row=0, column=0, sticky="ew", pady=(0,2))
        for i, (col, w) in enumerate(cols):
            ctk.CTkLabel(hdr, text=col, font=("Segoe UI", 11, "bold"),
                         text_color="#aaaaff", width=w, anchor="w").grid(row=0, column=i, padx=4, pady=3)

        # Listbox area
        list_frame = ctk.CTkScrollableFrame(left, fg_color="#0d0d1a", corner_radius=4)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        self.list_frame = list_frame
        self.row_frames = []

        # Right: detail panel
        right = ctk.CTkFrame(main, fg_color="#111122", corner_radius=8)
        right.grid(row=0, column=1, sticky="nsew", padx=(3,6), pady=6)
        right.columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Window Details", font=("Segoe UI", 13, "bold"),
                     text_color="#aaaaff").pack(pady=(10,4))

        self.detail_box = ctk.CTkTextbox(right, font=("Consolas", 11), fg_color="#0a0a18",
                                         text_color="#d0d0ff", wrap="word", state="disabled")
        self.detail_box.pack(fill="both", expand=True, padx=8, pady=(0,6))

        # Action buttons
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(fill="x", padx=8, pady=(0,8))

        ctk.CTkButton(btn_frame, text="👁 Show", width=80, height=28,
                      command=self._show_window).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🙈 Hide", width=80, height=28,
                      command=self._hide_window).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📋 Copy", width=80, height=28,
                      command=self._copy_details).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🔍 Focus", width=80, height=28,
                      command=self._focus_window).pack(side="left", padx=2)

        self.selected_win = None

    def refresh(self):
        self._all_windows = get_all_windows()
        self._apply_filter()

    def _apply_filter(self):
        q = self.search_var.get().lower()
        vis_filter = self.filter_var.get()
        filtered = []
        for w in self._all_windows:
            if vis_filter == "Visible" and not w["visible"]:
                continue
            if vis_filter == "Hidden" and w["visible"]:
                continue
            if q and not any(q in str(w[k]).lower() for k in ("title", "exe", "class")):
                continue
            filtered.append(w)

        # Clear rows
        for f in self.row_frames:
            f.destroy()
        self.row_frames.clear()

        for i, w in enumerate(filtered):
            bg = "#13132a" if i % 2 == 0 else "#0d0d1a"
            row = ctk.CTkFrame(self.list_frame, fg_color=bg, corner_radius=2, height=26)
            row.grid(row=i, column=0, sticky="ew", pady=1)
            row.columnconfigure(1, weight=1)

            vis_icon = "🟢" if w["visible"] else "🔴"
            vals = [str(w["hwnd"]), w["title"][:30], w["class"][:22], w["exe"][:18], vis_icon]
            widths = [90, 220, 160, 120, 45]
            for j, (val, wd) in enumerate(zip(vals, widths)):
                lbl = ctk.CTkLabel(row, text=val, font=("Segoe UI", 10),
                                   text_color="#ccccee", width=wd, anchor="w")
                lbl.grid(row=0, column=j, padx=4, pady=2)
                lbl.bind("<Button-1>", lambda e, win=w, r=row: self._select(win, r))
            row.bind("<Button-1>", lambda e, win=w, r=row: self._select(win, r))
            self.row_frames.append(row)

        self.count_label.configure(text=f"{len(filtered)} windows")

    def _select(self, win, row):
        self.selected_win = win
        # Highlight
        for f in self.row_frames:
            f.configure(fg_color="#13132a" if self.row_frames.index(f) % 2 == 0 else "#0d0d1a")
        row.configure(fg_color="#2a2a5a")
        # Show details
        details = (
            f"HWND      : {win['hwnd']}\n"
            f"Title     : {win['title']}\n"
            f"Class     : {win['class']}\n"
            f"Visible   : {'Yes' if win['visible'] else 'No'}\n"
            f"EXE       : {win['exe']}\n"
            f"PID       : {win['pid']}\n"
            f"EXE Path  : {win['exe_path']}\n"
            f"Rect      : {win['rect']}\n"
        )
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        self.detail_box.insert("1.0", details)
        self.detail_box.configure(state="disabled")

    def _show_window(self):
        if self.selected_win:
            win32gui.ShowWindow(self.selected_win["hwnd"], win32con.SW_SHOW)
            self.refresh()

    def _hide_window(self):
        if self.selected_win:
            win32gui.ShowWindow(self.selected_win["hwnd"], win32con.SW_HIDE)
            self.refresh()

    def _focus_window(self):
        if self.selected_win:
            hwnd = self.selected_win["hwnd"]
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)

    def _copy_details(self):
        if self.selected_win:
            self.clipboard_clear()
            self.clipboard_append(self.detail_box.get("1.0", "end"))

    def _start_drag(self, e):
        drag_data["x"] = e.x
        drag_data["y"] = e.y

    def _do_drag(self, e):
        x = self.winfo_x() + e.x - drag_data["x"]
        y = self.winfo_y() + e.y - drag_data["y"]
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
