from flask import Flask, request, jsonify
from wakeonlan import send_magic_packet
import logging

app = Flask(__name__)

# Configure logging for better debugging
logging.basicConfig(level=logging.D EBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# PC Details
PC_MAC_ADDRESS = "A8:5E:45:55:AD:30"
PC_BROADCAST_IP = "192.168.0.255" # Typically the broadcast IP for your subnet
PC_PORT = 9

@app.route('/')
def index():
    return "Welcome to the Wake-on-LAN Flask app! Use /wake to send the magic packet."

@app.route('/wake', methods=['POST'])
def wake_pc():
    app.logger.info(f"Received request to wake PC.")
    try:
        # Send the magic packet
        send_magic_packet(PC_MAC_ADDRESS, ip_address=PC_BROADCAST_IP, port=PC_PORT)
        app.logger.info(f"Magic packet sent to MAC: {PC_MAC_ADDRESS}, IP: {PC_BROADCAST_IP}, Port: {PC_PORT}")
        return jsonify({"status": "success", "message": f"Magic packet sent to {PC_MAC_ADDRESS}"}), 200
    except Exception as e:
        app.logger.error(f"Error sending magic packet: {e}")
        return jsonify({"status": "error", "message": f"Failed to send magic packet: {str(e)}"}), 500

if __name__ == '__main__':
    # It's crucial to bind to 0.0.0.0 so it's accessible from other devices
    # within your Tailscale network.
    app.run(host='0.0.0.0', port=5000, debug=False) # Set debug=False for production