from flask import Flask, jsonify, request, send_from_directory
import psutil
from flask_cors import CORS
import os

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

if __name__ == '__main__':
    app.run(port=4050)
