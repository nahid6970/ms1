from flask import Flask, render_template, redirect, url_for, flash
import win32gui
import win32con
import win32process
import win32api
import win32ui
import psutil
import sys
import base64
import io
from PIL import Image
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_icon_as_base64(hwnd):
    try:
        hicon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_SMALL, 0)
        if hicon == 0:
            hicon = win32gui.SendMessage(hwnd, win32con.WM_GETICON, win32con.ICON_BIG, 0)
        if hicon == 0:
            hicon = win32gui.GetClassLong(hwnd, win32con.GCL_HICONSM)
        if hicon == 0:
            hicon = win32gui.GetClassLong(hwnd, win32con.GCL_HICON)
        
        if hicon == 0:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            proc = psutil.Process(pid)
            exe_path = proc.exe()
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if small:
                hicon = small[0]
                for h in large: win32gui.DestroyIcon(h)
                for h in small[1:]: win32gui.DestroyIcon(h)
            elif large:
                hicon = large[0]
                for h in large[1:]: win32gui.DestroyIcon(h)

        if hicon == 0:
            return None

        hdc = win32gui.GetDC(0)
        src_dc = win32ui.CreateDCFromHandle(hdc)
        mem_dc = src_dc.CreateCompatibleDC()
        
        width = win32api.GetSystemMetrics(win32con.SM_CXSMICON)
        height = win32api.GetSystemMetrics(win32con.SM_CYSMICON)
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(src_dc, width, height)
        mem_dc.SelectObject(bmp)
        
        # Use DrawIconEx with DI_NORMAL to preserve alpha if present
        win32gui.DrawIconEx(mem_dc.GetSafeHdc(), 0, 0, hicon, width, height, 0, None, win32con.DI_NORMAL)
        
        bmp_info = bmp.GetInfo()
        bmp_str = bmp.GetBitmapBits(True)
        # Use RGBA and BGRA to handle the alpha channel correctly
        img = Image.frombuffer('RGBA', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRA', 0, 1)
        
        mem_dc.DeleteDC()
        src_dc.DeleteDC()
        win32gui.ReleaseDC(0, hdc)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG") # PNG supports transparency
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except:
        return None

BLOCKLIST = [
    "ShellExperienceHost.exe",
    "StartMenuExperienceHost.exe",
    "SearchHost.exe",
    "Widgets.exe",
    "TextInputHost.exe",
    "Taskmgr.exe",
    "explorer.exe",
    "SystemSettings.exe",
    "ApplicationFrameHost.exe",
    "RuntimeBroker.exe",
    "DllHost.exe",
    "Conhost.exe",
    "Sihost.exe",
    "SmartScreen.exe",
    "SettingSyncHost.exe",
    "ctfmon.exe",
    "lsass.exe",
    "csrss.exe",
    "wininit.exe",
    "services.exe",
    "winlogon.exe",
    "smss.exe",
    "fontdrvhost.exe",
    "dwm.exe",
    "Memory Compression",
]

def get_active_windows():
    groups = defaultdict(list)
    memo_icons = {}

    def enum_handler(hwnd, lParam):
        is_visible = win32gui.IsWindowVisible(hwnd)
        title = win32gui.GetWindowText(hwnd)
        
        if title:
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                app_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app_name = "Unknown"

            # Filter by blocklist
            if app_name in BLOCKLIST:
                return

            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            parent = win32gui.GetParent(hwnd)
            owner = win32gui.GetWindow(hwnd, win32con.GW_OWNER)
            
            is_tool = ex_style & win32con.WS_EX_TOOLWINDOW
            
            if is_visible or (parent == 0 and owner == 0 and not is_tool):
                if not is_visible:
                    # Stricter check for invisible windows
                    if title in ["Program Manager", "Settings"]:
                        return

                if app_name not in memo_icons:
                    memo_icons[app_name] = get_icon_as_base64(hwnd)
                
                groups[app_name].append({
                    'hwnd': hwnd, 
                    'title': title
                })
    
    win32gui.EnumWindows(enum_handler, None)
    
    sorted_groups = []
    for app_name in groups.keys():
        windows = sorted(groups[app_name], key=lambda x: x['title'].lower())
        sorted_groups.append({
            'app_name': app_name, 
            'windows': windows,
            'icon': memo_icons.get(app_name)
        })
    
    # Sort: Multiple windows first, then by app name
    sorted_groups.sort(key=lambda x: (len(x['windows']) == 1, x['app_name'].lower()))
    
    return sorted_groups

@app.route('/')
def index():
    groups = get_active_windows()
    return render_template('index.html', groups=groups)

@app.route('/close/<int:hwnd>')
def close_window(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process = psutil.Process(pid)
        process.kill()
    except Exception as e:
        print(f"Error killing window {hwnd}: {e}")
    
    return redirect(url_for('index'))

@app.route('/kill_app/<name>')
def kill_app(name):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == name:
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = 5021
    print(f"Starting Flask app on port {port}...")
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Failed to start server on port {port}: {e}")
        sys.exit(1)
