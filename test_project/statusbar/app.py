from flask import Flask, jsonify, request, send_from_directory
import psutil
from flask_cors import CORS
import os
import webview.screen
import threading
import time

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

# Serve static files (CSS, JS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)

# Serve the main HTML file
@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

@app.route('/usage')
def get_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    return jsonify(cpu_usage=cpu_usage, ram_usage=ram_usage)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    shutdown_server()
    return 'Server shutting down...'

def start_flask_app():
    app.run(port=4050)

if __name__ == '__main__':
    t = threading.Thread(target=start_flask_app)
    t.daemon = True
    t.start()
    time.sleep(2) # Give the Flask server a moment to start

    window_width = 500
    window_height = 40
    screen_width = webview.screens[0].width
    x_coordinate = int((screen_width / 2) - (window_width / 2))

    webview.create_window('Status Bar', 'http://127.0.0.1:4050', frameless=True, x=x_coordinate, y=0, width=window_width, height=window_height)
    print("Attempting to load URL: http://127.0.0.1:4050")
    webview.start()