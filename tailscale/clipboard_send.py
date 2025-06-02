from flask import Flask, request
import time
import threading
import requests
import pyperclip

app = Flask(__name__)
last_clipboard = ""

# Set your PC's Flask server IP here
PC_SERVER_URL = "http://192.168.0.101:5001/"

def monitor_clipboard():
    global last_clipboard
    while True:
        try:
            current = pyperclip.paste()
            if current and current != last_clipboard:
                last_clipboard = current
                print(f"[Copied] {current}")
                send_to_pc(current)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

def send_to_pc(text):
    try:
        response = requests.post(PC_SERVER_URL, data={'text': text})
        print("Sent to PC:", response.status_code)
    except Exception as e:
        print("Failed to send:", e)

@app.route('/')
def status():
    return "Android clipboard sender running."

if __name__ == '__main__':
    # Start clipboard monitor in background
    threading.Thread(target=monitor_clipboard, daemon=True).start()
    app.run(host='0.0.0.0', port=8000)
