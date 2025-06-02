from flask import Flask
import socket

app = Flask(__name__)

# PC Details
TARGET_MAC = "A8:5E:45:55:AD:30"
TARGET_PORT = 9

def send_magic_packet(mac):
    mac_bytes = bytes.fromhex(mac.replace(':', ''))
    packet = b'\xff' * 6 + mac_bytes * 16
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(packet, ('<broadcast>', TARGET_PORT))

if __name__ == "__main__":
    send_magic_packet(TARGET_MAC)  # send magic packet once on start
    app.run(host="0.0.0.0", port=5003)
