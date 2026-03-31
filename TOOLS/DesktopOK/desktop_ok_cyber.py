import sys
import os
import json
import ctypes
import struct
import win32gui
import win32api
import win32con
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QGroupBox, QFormLayout, QListWidget, QComboBox, 
                             QStackedWidget, QFrame)
from PyQt6.QtCore import Qt, QSize
from commctrl import (LVM_GETITEMCOUNT, LVM_GETITEMPOSITION, LVM_SETITEMPOSITION, 
                      LVM_GETITEMTEXTW, LVIF_TEXT)

# --- PALETTE ---
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

# --- CONSTANTS FOR WINDOWS API ---
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
MEM_COMMIT = 0x1000
MEM_RELEASE = 0x8000
PAGE_READWRITE = 0x04

class LVITEM(ctypes.Structure):
    _fields_ = [
        ("mask", ctypes.c_uint),
        ("iItem", ctypes.c_int),
        ("iSubItem", ctypes.c_int),
        ("state", ctypes.c_uint),
        ("stateMask", ctypes.c_uint),
        ("pszText", ctypes.c_void_p),
        ("cchTextMax", ctypes.c_int),
        ("iImage", ctypes.c_int),
        ("lParam", ctypes.c_void_p),
        ("iIndent", ctypes.c_int),
        ("iGroupId", ctypes.c_int),
        ("cColumns", ctypes.c_uint),
        ("puColumns", ctypes.c_void_p),
        ("piColFmt", ctypes.c_void_p),
        ("iGroup", ctypes.c_int),
    ]

class DesktopManager:
    @staticmethod
    def get_listview_hwnd():
        # Step 1: Try Progman
        progman = win32gui.FindWindow("Progman", "Program Manager")
        def find_lv(parent):
            shell_view = win32gui.FindWindowEx(parent, 0, "SHELLDLL_DefView", None)
            if shell_view:
                return win32gui.FindWindowEx(shell_view, 0, "SysListView32", "FolderView")
            return None

        lv = find_lv(progman)
        if lv: return lv

        # Step 2: Try WorkerW (often happens after wallpaper changes)
        def callback(hwnd, results):
            if win32gui.GetClassName(hwnd) == "WorkerW":
                view = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
                if view:
                    results.append(win32gui.FindWindowEx(view, 0, "SysListView32", "FolderView"))
        
        results = []
        win32gui.EnumWindows(callback, results)
        for res in results:
            if res: return res
            
        return None

    @staticmethod
    def get_icon_positions():
        hwnd = DesktopManager.get_listview_hwnd()
        if not hwnd: 
            print("ERROR: Could not find Desktop ListView")
            return {}
        
        count = win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT, 0, 0)
        print(f"DEBUG: Found {count} items on desktop")
        
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, False, pid)
        
        # Buffers in remote process
        pos_mem = ctypes.windll.kernel32.VirtualAllocEx(process, 0, 8, MEM_COMMIT, PAGE_READWRITE)
        text_mem = ctypes.windll.kernel32.VirtualAllocEx(process, 0, 1024, MEM_COMMIT, PAGE_READWRITE)
        item_mem = ctypes.windll.kernel32.VirtualAllocEx(process, 0, ctypes.sizeof(LVITEM), MEM_COMMIT, PAGE_READWRITE)
        
        icons = {}
        for i in range(count):
            # Position
            win32gui.SendMessage(hwnd, LVM_GETITEMPOSITION, i, pos_mem)
            pos_data = ctypes.create_string_buffer(8)
            ctypes.windll.kernel32.ReadProcessMemory(process, pos_mem, pos_data, 8, None)
            x, y = struct.unpack("ll", pos_data)
            
            # Text/Name
            lv_item = LVITEM()
            lv_item.mask = LVIF_TEXT
            lv_item.iItem = i
            lv_item.pszText = text_mem
            lv_item.cchTextMax = 512
            
            ctypes.windll.kernel32.WriteProcessMemory(process, item_mem, ctypes.byref(lv_item), ctypes.sizeof(LVITEM), None)
            win32gui.SendMessage(hwnd, LVM_GETITEMTEXTW, i, item_mem)
            
            name_buffer = ctypes.create_string_buffer(1024)
            ctypes.windll.kernel32.ReadProcessMemory(process, text_mem, name_buffer, 1024, None)
            name = name_buffer.raw.decode("utf-16").split("\0")[0]
            
            # If name is empty, try to use a placeholder or index to avoid losing it
            if not name:
                name = f"UNNAMED_ICON_{i}"
                
            icons[name] = {"x": x, "y": y}

        ctypes.windll.kernel32.VirtualFreeEx(process, pos_mem, 0, MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(process, text_mem, 0, MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(process, item_mem, 0, MEM_RELEASE)
        ctypes.windll.kernel32.CloseHandle(process)
        return icons

    @staticmethod
    def restore_icon_positions(icon_map):
        hwnd = DesktopManager.get_listview_hwnd()
        if not hwnd: return
        
        # Explorer often caches positions; LVM_SETITEMPOSITION works best when auto-arrange is off.
        for name, pos in icon_map.items():
            idx = DesktopManager._find_icon_index(hwnd, name)
            if idx != -1:
                # MAKELONG for 32-bit compatibility if needed, but x,y are usually enough
                win32gui.SendMessage(hwnd, LVM_SETITEMPOSITION, idx, win32api.MAKELONG(pos['x'], pos['y']))
        
        win32gui.InvalidateRect(hwnd, None, True)

    @staticmethod
    def _find_icon_index(hwnd, name):
        pid = ctypes.c_ulong()
        ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, False, pid)
        
        text_mem = ctypes.windll.kernel32.VirtualAllocEx(process, 0, 1024, MEM_COMMIT, PAGE_READWRITE)
        item_mem = ctypes.windll.kernel32.VirtualAllocEx(process, 0, ctypes.sizeof(LVITEM), MEM_COMMIT, PAGE_READWRITE)
        
        count = win32gui.SendMessage(hwnd, LVM_GETITEMCOUNT, 0, 0)
        found_idx = -1
        
        for i in range(count):
            lv_item = LVITEM()
            lv_item.mask = LVIF_TEXT
            lv_item.iItem = i
            lv_item.pszText = text_mem
            lv_item.cchTextMax = 512
            
            ctypes.windll.kernel32.WriteProcessMemory(process, item_mem, ctypes.byref(lv_item), ctypes.sizeof(LVITEM), None)
            win32gui.SendMessage(hwnd, LVM_GETITEMTEXTW, i, item_mem)
            
            name_buffer = ctypes.create_string_buffer(1024)
            ctypes.windll.kernel32.ReadProcessMemory(process, text_mem, name_buffer, 1024, None)
            curr_name = name_buffer.raw.decode("utf-16").split("\0")[0]
            
            if curr_name == name or (not curr_name and name == f"UNNAMED_ICON_{i}"):
                found_idx = i
                break
                
        ctypes.windll.kernel32.VirtualFreeEx(process, text_mem, 0, MEM_RELEASE)
        ctypes.windll.kernel32.VirtualFreeEx(process, item_mem, 0, MEM_RELEASE)
        ctypes.windll.kernel32.CloseHandle(process)
        return found_idx

class WindowManager:
    @staticmethod
    def get_open_windows():
        windows = []
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                style = win32api.GetWindowLong(hwnd, win32con.GWL_STYLE)
                # Filter out tool windows or non-apps if needed
                if not (style & win32con.WS_CHILD):
                    rect = win32gui.GetWindowRect(hwnd)
                    windows.append({
                        "title": win32gui.GetWindowText(hwnd),
                        "class": win32gui.GetClassName(hwnd),
                        "x": rect[0],
                        "y": rect[1],
                        "w": rect[2] - rect[0],
                        "h": rect[3] - rect[1]
                    })
        win32gui.EnumWindows(callback, None)
        return windows

    @staticmethod
    def restore_windows(window_list):
        for win_data in window_list:
            hwnd = win32gui.FindWindow(win_data["class"], win_data["title"])
            if hwnd:
                win32gui.MoveWindow(hwnd, win_data["x"], win_data["y"], win_data["w"], win_data["h"], True)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CYBER_DESKTOP_OK v1.0")
        self.resize(500, 600)
        self.data_path = os.path.join(os.path.dirname(__file__), "layouts.json")
        self.layouts = self.load_data()

        # Apply Global Theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QFrame#MainContainer {{ background-color: {CP_BG}; }}

            QLineEdit, QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px;       
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {CP_CYAN}; }}

            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 8px 16px; font-weight: bold;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton#ActionBtn {{
                background-color: {CP_PANEL}; border: 1px solid {CP_CYAN}; color: {CP_CYAN};
            }}
            QPushButton#ActionBtn:hover {{
                background-color: {CP_CYAN}; color: black;
            }}
            QPushButton#RestartBtn {{
                background-color: {CP_DIM}; border: 1px solid {CP_RED}; color: {CP_RED};
            }}
            QPushButton#RestartBtn:hover {{
                background-color: {CP_RED}; color: white;
            }}

            QListWidget {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; color: {CP_YELLOW}; outline: none;
            }}
            QListWidget::item {{ padding: 10px; border-bottom: 1px solid #222; }}
            QListWidget::item:selected {{ background-color: {CP_DIM}; color: {CP_CYAN}; border-left: 3px solid {CP_CYAN}; }}

            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 15px; padding-top: 15px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}    
        """)

        # Main Stack for Screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Screen 1: Home
        self.home_screen = QWidget()
        self.init_home()
        self.stack.addWidget(self.home_screen)

        # Screen 2: Settings
        self.settings_screen = QWidget()
        self.init_settings()
        self.stack.addWidget(self.settings_screen)

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_path, "w") as f:
            json.dump(self.layouts, f, indent=4)

    def init_home(self):
        layout = QVBoxLayout(self.home_screen)
        
        header = QLabel("SYSTEM :: DESKTOP_ICON_MANAGER")
        header.setStyleSheet(f"color: {CP_CYAN}; font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        # Layout List
        layout.addWidget(QLabel("SAVED_LAYOUTS:"))
        self.list_widget = QListWidget()
        self.refresh_list()
        layout.addWidget(self.list_widget)

        # Controls
        btn_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("NEW_LAYOUT_NAME...")
        btn_layout.addWidget(self.name_input)
        
        save_btn = QPushButton("SAVE_CURRENT")
        save_btn.setObjectName("ActionBtn")
        save_btn.clicked.connect(self.save_current_layout)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        action_layout = QHBoxLayout()
        restore_btn = QPushButton("RESTORE_SELECTED")
        restore_btn.clicked.connect(self.restore_selected_layout)
        action_layout.addWidget(restore_btn)

        delete_btn = QPushButton("DELETE_SELECTED")
        delete_btn.setStyleSheet(f"color: {CP_RED};")
        delete_btn.clicked.connect(self.delete_selected_layout)
        action_layout.addWidget(delete_btn)
        layout.addLayout(action_layout)

        # Bottom Bar
        bottom_layout = QHBoxLayout()
        settings_btn = QPushButton("SETTINGS")
        settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        
        restart_btn = QPushButton("RESTART")
        restart_btn.setObjectName("RestartBtn")
        restart_btn.clicked.connect(self.restart_app)
        
        bottom_layout.addWidget(settings_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(restart_btn)
        layout.addLayout(bottom_layout)

    def init_settings(self):
        layout = QVBoxLayout(self.settings_screen)
        
        header = QLabel("SYSTEM :: CONFIGURATION")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)

        grp = QGroupBox("RESOLUTION_SET")
        form = QFormLayout()
        
        self.res_combo = QComboBox()
        self.populate_resolutions()
        form.addRow("TARGET_RESOLUTION:", self.res_combo)
        
        apply_res_btn = QPushButton("APPLY_RESOLUTION")
        apply_res_btn.clicked.connect(self.apply_resolution)
        form.addRow("", apply_res_btn)
        
        grp.setLayout(form)
        layout.addWidget(grp)

        # Custom section (empty as requested)
        custom_grp = QGroupBox("CUSTOM_MODULES")
        custom_layout = QVBoxLayout()
        custom_layout.addWidget(QLabel("NO_MODULES_LOADED..."))
        custom_grp.setLayout(custom_layout)
        layout.addWidget(custom_grp)

        layout.addStretch()
        
        back_btn = QPushButton("BACK_TO_HOME")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(back_btn)

    def populate_resolutions(self):
        resolutions = []
        i = 0
        while True:
            try:
                devmode = win32api.EnumDisplaySettings(None, i)
                res = f"{devmode.PelsWidth}x{devmode.PelsHeight}"
                if res not in resolutions:
                    resolutions.append(res)
                i += 1
            except:
                break
        self.res_combo.addItems(sorted(resolutions, key=lambda x: int(x.split('x')[0]), reverse=True))

    def apply_resolution(self):
        res = self.res_combo.currentText()
        w, h = map(int, res.split('x'))
        try:
            devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
            devmode.PelsWidth = w
            devmode.PelsHeight = h
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT
            win32api.ChangeDisplaySettings(devmode, 0)
        except Exception as e:
            print(f"Error changing resolution: {e}")

    def save_current_layout(self):
        name = self.name_input.text().strip()
        if not name:
            name = f"Layout_{len(self.layouts)+1}"
        
        icons = DesktopManager.get_icon_positions()
        windows = WindowManager.get_open_windows()
        
        self.layouts[name] = {
            "icons": icons,
            "windows": windows
        }
        self.save_data()
        self.refresh_list()
        self.name_input.clear()

    def restore_selected_layout(self):
        item = self.list_widget.currentItem()
        if item:
            name = item.text()
            if name in self.layouts:
                layout_data = self.layouts[name]
                
                # Handle legacy data vs new structure
                if "icons" in layout_data:
                    DesktopManager.restore_icon_positions(layout_data["icons"])
                    if "windows" in layout_data:
                        WindowManager.restore_windows(layout_data["windows"])
                else:
                    # Legacy data support
                    DesktopManager.restore_icon_positions(layout_data)

    def delete_selected_layout(self):
        item = self.list_widget.currentItem()
        if item:
            name = item.text()
            if name in self.layouts:
                del self.layouts[name]
                self.save_data()
                self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        self.list_widget.addItems(self.layouts.keys())

    def restart_app(self):
        os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
