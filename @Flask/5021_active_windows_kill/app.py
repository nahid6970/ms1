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
        
        # Fill background with white to avoid black background if alpha is ignored
        brush = win32gui.CreateSolidBrush(win32api.RGB(255, 255, 255))
        win32gui.FillRect(mem_dc.GetSafeHdc(), (0, 0, width, height), brush)
        win32gui.DeleteObject(brush)
        
        win32gui.DrawIconEx(mem_dc.GetSafeHdc(), 0, 0, hicon, width, height, 0, None, win32con.DI_NORMAL)
        
        bmp_info = bmp.GetInfo()
        bmp_str = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_str, 'raw', 'BGRX', 0, 1)
        
        mem_dc.DeleteDC()
        src_dc.DeleteDC()
        win32gui.ReleaseDC(0, hdc)

        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except:
        return None

def get_active_windows():
    groups = defaultdict(list)
    memo_icons = {}

    def enum_handler(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    app_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    app_name = "Unknown"
                
                if app_name not in memo_icons:
                    memo_icons[app_name] = get_icon_as_base64(hwnd)
                
                groups[app_name].append({
                    'hwnd': hwnd, 
                    'title': title
                })
    
    win32gui.EnumWindows(enum_handler, None)
    
    sorted_groups = []
    for app_name in sorted(groups.keys()):
        windows = sorted(groups[app_name], key=lambda x: x['title'].lower())
        sorted_groups.append({
            'app_name': app_name, 
            'windows': windows,
            'icon': memo_icons.get(app_name)
        })
    
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
