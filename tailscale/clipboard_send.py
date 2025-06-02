from flask import Flask
import subprocess
import time
import threading
import requests

app = Flask(__name__)
PC_SERVER_URL = "http://192.168.0.101:5001/"
last_clipboard = ""

def get_clipboard():
    try:
        return subprocess.check_output(["termux-clipboard-get"]).decode("utf-8").strip()
    except Exception as e:
        print("Clipboard read error:", e)
        return ""

def send_to_pc(text):
    try:
        requests.post(PC_SERVER_URL, data={'text': text})
        print(f"Sent to PC: {text}")
    except Exception as e:
        print("Failed to send:", e)

def monitor_clipboard():
    global last_clipboard
    while True:
        text = get_clipboard()
        if text and text != last_clipboard:
            last_clipboard = text
            send_to_pc(text)
        time.sleep(1)

@app.route("/")
def index():
    return "Termux clipboard sender is running."

if __name__ == "__main__":
    threading.Thread(target=monitor_clipboard, daemon=True).start()
    app.run(host="0.0.0.0", port=8000)
