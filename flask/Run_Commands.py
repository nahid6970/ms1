from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

# Whitelisted commands (label: actual command)
COMMANDS = {
    "List Files": "dir",
    "Show IP Config": "ipconfig",
    "Open Notepad": "start notepad",
    "Open Calculator": "start calc",
    "System Info": "systeminfo"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Windows Command Center</title>
</head>
<body>
    <h2>Run a Windows Command</h2>
    <form method="post">
        {% for label, cmd in commands.items() %}
            <button type="submit" name="command" value="{{ cmd }}">{{ label }}</button><br><br>
        {% endfor %}
    </form>
    <hr>
    <h3>Output:</h3>
    <pre>{{ output }}</pre>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ""
    if request.method == 'POST':
        cmd = request.form['command']
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
        except Exception as e:
            output = f"Error: {e}"
    return render_template_string(HTML_TEMPLATE, commands=COMMANDS, output=output)

if __name__ == '__main__':
    app.run(debug=True, port=5006)

