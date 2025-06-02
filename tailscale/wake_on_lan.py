from flask import Flask, render_template_string, redirect, url_for
import os

app = Flask(__name__)

# PC Details
TARGET_MAC = "A8:5E:45:55:AD:30"
TARGET_IP = "192.168.0.101"
TARGET_PORT = 9

# HTML UI
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Wake PC</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding-top: 50px; }
        button { font-size: 24px; padding: 10px 40px; }
    </style>
</head>
<body>
    <h1>Wake PC</h1>
    <form method="POST" action="/wake">
        <button type="submit">💻 Wake PC</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML)

@app.route("/wake", methods=["POST"])
def wake():
    send_magic_packet(TARGET_MAC)
    return redirect(url_for('index'))

def send_magic_packet(mac):
    # Linux/Mac: use socket directly
    import socket
    mac_bytes = bytes.fromhex(mac.replace(':', ''))
    packet = b'\xff' * 6 + mac_bytes * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(packet, ('<broadcast>', TARGET_PORT))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
