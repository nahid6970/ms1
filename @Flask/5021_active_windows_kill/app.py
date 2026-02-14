from flask import Flask, render_template, redirect, url_for, flash
import win32gui
import win32con
import sys

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def get_active_windows():
    windows = []
    def enum_handler(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            # Filter out empty titles and common system windows if necessary
            # For now, let's just show everything with a title
            if title:
                windows.append({'hwnd': hwnd, 'title': title})
    win32gui.EnumWindows(enum_handler, None)
    # Sort by title
    windows.sort(key=lambda x: x['title'].lower())
    return windows

@app.route('/')
def index():
    windows = get_active_windows()
    return render_template('index.html', windows=windows)

@app.route('/close/<int:hwnd>')
def close_window(hwnd):
    try:
        # Use PostMessage to send WM_CLOSE to the window
        # This is generally safer than TerminateProcess as it allows the app to save work
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    except Exception as e:
        print(f"Error closing window {hwnd}: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = 21
    print(f"Starting Flask app on port {port}...")
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"Failed to start server on port {port}: {e}")
        print("Note: Port 21 may require administrative privileges or is already in use.")
        sys.exit(1)
