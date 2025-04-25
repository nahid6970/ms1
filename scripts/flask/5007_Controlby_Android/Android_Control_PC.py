from flask import Flask, request, render_template, redirect, url_for
import subprocess

app = Flask(__name__)

COMMANDS = {
    "Display 1": "C:\\msBackups\\Display\\DisplaySwitch.exe /internal",
    "Display 2": "C:\\msBackups\\Display\\DisplaySwitch.exe /external",
    "Display 1 KillApps": "C:\\ms1\\scripts\\Autohtokey\\Command\\monitor_1.ahk && taskkill /IM python.exe /IM notepad++.exe /IM dnplayer.exe /F",
    "Show IP Config": "ipconfig",
    "Open Notepad": "start notepad",
    "Open Calculator": "start calc",
    "System Info": "systeminfo",
    "Shutdown": "shutdown /s /t 0",
    "Restart": "shutdown /r /t 0",
    "Sign Out": "shutdown /l"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cmd = request.form['command']
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            pass
        # Redirect to prevent re-submitting the form on refresh
        return redirect(url_for('index'))

    return render_template("index.html", commands=COMMANDS)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007, debug=True)
