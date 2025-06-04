import subprocess
import requests

PC_SERVER_URL = "http://192.168.0.101:5001/"

def get_clipboard():
    try:
        return subprocess.check_output(["termux-clipboard-get"]).decode("utf-8").strip()
    except Exception as e:
        print("Clipboard read error:", e)
        return ""

def send_to_pc(text):
    try:
        response = requests.post(PC_SERVER_URL, data={'text': text})
        print("Sent:", text)
        print("Response:", response.text)
    except Exception as e:
        print("Send error:", e)

text = get_clipboard()
if text:
    send_to_pc(text)
