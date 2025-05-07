from flask import Flask, send_file
from threading import Thread

# List of files to serve with their respective ports
file_routes = [
    {'path': r'C:\ms1\archlinux\os.sh', 'port': 7710},
    {'path': r'C:\ms1\startup.py', 'port': 7711},
    {'path': r'C:\ms1\Ultimate_Gui.py', 'port': 7713},
]

# Function to create a new Flask app for each file
def create_app(file_path):
    app = Flask(__name__)

    @app.route('/')
    def serve_file():
        return send_file(file_path, as_attachment=True)

    return app

# Function to run each Flask app on a separate port
def run_app(app, port):
    app.run(host='0.0.0.0', port=port, debug=False)

# Start a thread for each file and port
for route in file_routes:
    app = create_app(route['path'])
    Thread(target=run_app, args=(app, route['port'])).start()
