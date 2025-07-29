import webview
import threading
import time
from app import app

def run_app():
    app.run(port=4050)

if __name__ == '__main__':
    t = threading.Thread(target=run_app)
    t.daemon = True
    t.start()
    time.sleep(2) # Give the Flask server a moment to start

    webview.create_window('Status Bar', 'http://127.0.0.1:4050', frameless=True)
    print("Attempting to load URL: http://127.0.0.1:4050")
    webview.start()
