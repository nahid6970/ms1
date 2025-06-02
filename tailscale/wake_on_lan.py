from flask import Flask, request, jsonify, render_template_string
import socket

app = Flask(__name__)

# PC details
TARGET_MAC = 'A8:5E:45:55:AD:30'
TARGET_IP = '192.168.0.101'
PORT = 9

def send_wol(mac):
    mac_bytes = bytes.fromhex(mac.replace(':', ''))
    packet = b'\xff' * 6 + mac_bytes * 16
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(packet, (TARGET_IP, PORT))

# HTML page with a wake button
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Wake PC</title>
</head>
<body style="font-family:sans-serif; text-align:center; padding-top:50px;">
    <h2>Wake PC via Tailscale</h2>
    <form action="/wake" method="post">
        <button type="submit" style="padding:10px 20px; font-size:18px;">Wake PC</button>
    </form>
    {% if result %}
    <p style="color:green; font-weight:bold;">{{ result }}</p>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        try:
            send_wol(TARGET_MAC)
            result = "Magic packet sent!"
        except Exception as e:
            result = f"Error: {str(e)}"
    return render_template_string(HTML_PAGE, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011)
