from flask import Flask, send_file
from threading import Thread

# List of HTML files to serve with their respective ports
html_routes = [
    {'path': r'C:\Users\nahid\ms\db\5000_myhome\myhome.html', 'port': 6001},
    {'path': r'C:\Users\nahid\ms\db\5000_myhome\mycell.html', 'port': 6002},
]

# Function to create a new Flask app for each HTML file
def create_app(file_path):
    app = Flask(__name__)

    @app.route('/')
    def serve_page():
        return send_file(file_path)

    return app

# Function to run each Flask app on a separate port
def run_app(app, port):
    app.run(host='0.0.0.0', port=port, debug=False)

# Start a thread for each HTML file and port
if __name__ == '__main__':
    print("Starting web servers...")
    for route in html_routes:
        app = create_app(route['path'])
        print(f"Serving {route['path']} on http://0.0.0.0:{route['port']}")
        Thread(target=run_app, args=(app, route['port'])).start()
    print("\nServers running! Access from your Android using your PC's IP address.")
    print("Example: http://192.168.1.x:5000")
