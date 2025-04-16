from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

COMMANDS = {
    "List Files": "dir",
    "Show IP Config": "ipconfig",
    "Open Notepad": "start notepad",
    "Open Calculator": "start calc",
    "System Info": "systeminfo"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cmd = request.form['command']
        try:
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            pass
    return render_template("index.html", commands=COMMANDS)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007, debug=True)
