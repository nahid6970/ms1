from flask import Flask, request, render_template_string, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Whitelisted commands
COMMANDS = {
    "List Files": "dir",
    "Show IP Config": "ipconfig",
    "Open Notepad": "start notepad",
    "Open Calculator": "start calc",
    "System Info": "systeminfo",
    "Display 2": "C:/msBackups/Display/DisplaySwitch.exe /external"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Windows Command Center</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e1e2f;
            color: #f8f8f2;
            padding: 20px;
            margin: 0;
        }
        h2 {
            color: #50fa7b;
            text-align: center;
        }
        .container {
            display: flex;
            justify-content: space-between;
            max-width: 1000px;
            margin: 40px auto;
            gap: 20px;
        }
        .commands {
            flex: 1;
            background-color: #282a36;
            padding: 20px;
            border-radius: 8px;
        }
        .commands button {
            display: block;
            width: 100%;
            margin: 10px 0;
            padding: 12px;
            background-color: #44475a;
            color: #f8f8f2;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.2s;
        }
        .commands button:hover {
            background-color: #6272a4;
        }
        .output {
            flex: 2;
            background-color: #282a36;
            padding: 20px;
            border-radius: 8px;
        }
        .output h3 {
            color: #8be9fd;
            margin-top: 0;
        }
        pre {
            background-color: #1e1e2f;
            color: #f1fa8c;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 600px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <h2>🚀 Windows Command Center</h2>
    <div class="container">
        <form method="post" class="commands">
            {% for label, cmd in commands.items() %}
                <button type="submit" name="command" value="{{ cmd }}">{{ label }}</button>
            {% endfor %}
        </form>
        <div class="output">
            <h3>🖥 Output:</h3>
            <pre>{{ output }}</pre>
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cmd = request.form['command']
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            session['output'] = result.stdout + result.stderr
        except Exception as e:
            session['output'] = f"Error: {e}"
        return redirect(url_for('index'))

    output = session.pop('output', '')
    return render_template_string(HTML_TEMPLATE, commands=COMMANDS, output=output)

if __name__ == '__main__':
    app.run(debug=True, port=5006)
