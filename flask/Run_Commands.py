from flask import Flask, request, render_template_string, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session to work

# Whitelisted commands (label: actual command)
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
            padding: 40px;
            text-align: center;
        }
        h2 {
            color: #50fa7b;
        }
        form {
            margin: 20px auto;
            max-width: 600px;
        }
        button {
            width: 90%;
            margin: 10px auto;
            padding: 12px 20px;
            background-color: #282a36;
            color: #f8f8f2;
            border: 1px solid #44475a;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        button:hover {
            background-color: #44475a;
        }
        pre {
            background-color: #282a36;
            color: #f1fa8c;
            padding: 20px;
            border-radius: 5px;
            text-align: left;
            white-space: pre-wrap;
            word-break: break-all;
            max-width: 800px;
            margin: 20px auto;
        }
        hr {
            border-color: #6272a4;
        }
    </style>
</head>
<body>
    <h2>🚀 Windows Command Center</h2>
    <form method="post">
        {% for label, cmd in commands.items() %}
            <button type="submit" name="command" value="{{ cmd }}">{{ label }}</button>
        {% endfor %}
    </form>
    <hr>
    <h3>🖥 Output:</h3>
    <pre>{{ output }}</pre>
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
