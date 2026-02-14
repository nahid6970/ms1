from flask import Flask, render_template, redirect, url_for, flash
import win32gui
import win32con
import win32process
import psutil
import sys
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_active_windows():
    groups = defaultdict(list)
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
                
                groups[app_name].append({'hwnd': hwnd, 'title': title})
    
    win32gui.EnumWindows(enum_handler, None)
    
    # Sort windows within groups and the groups themselves
    sorted_groups = []
    for app_name in sorted(groups.keys()):
        windows = sorted(groups[app_name], key=lambda x: x['title'].lower())
        sorted_groups.append({'app_name': app_name, 'windows': windows})
    
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
