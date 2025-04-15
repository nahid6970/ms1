from flask import Flask, request, render_template_string, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'some_secret'  # Needed for session

COMMAND_GROUPS = {
    "System Commands": {
        "IP Config": {
            "cmd": "ipconfig",
            "admin": False
        },
        "System Info": {
            "cmd": "systeminfo",
            "admin": False
        }
    },
    "Tools": {
        "Open Notepad": {
            "cmd": "start notepad",
            "admin": False
        },
        "Open Calculator": {
            "cmd": "start calc",
            "admin": False
        }
    },
    "Display": {
        "Switch to Display 1": {
            "cmd": "C:/msBackups/Display/DisplaySwitch.exe /internal",
            "admin": False
        },
        "Switch to Display 2": {
            "cmd": "C:/msBackups/Display/DisplaySwitch.exe /external",
            "admin": False
        }
    },
    "File Management": {
        "List Files": {
            "cmd": "dir",
            "admin": False
        }
    },
    "Firewall Settings": {
        "Allow Port 5006": {
            "cmd": 'Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "New-NetFirewallRule -DisplayName \'Allow_Port_5006\' -Direction Inbound -Protocol TCP -LocalPort 5006 -Action Allow -Profile Any"',
            "admin": True
        }
    }
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Windows Command Center</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            padding: 20px;
            gap: 30px;
            background-color: #1e1e1e; /* Dark background */
            color: #d4d4d4; /* Light text */
        }
        .left, .right {
            flex: 1;
        }
        .group {
            margin-bottom: 15px;
        }
        .group > button {
            width: 100%;
            padding: 10px;
            background-color: #333; /* Dark button background */
            color: #f0f0f0; /* Light button text */
            border: none;
            text-align: left;
            cursor: pointer;
            font-weight: bold;
        }
        .submenu {
            display: none;
            margin-top: 5px;
            padding-left: 10px;
        }
        .submenu button {
            display: block;
            width: 100%;
            margin: 5px 0;
            padding: 8px;
            border: 1px solid #555; /* Darker border */
            background-color: #444; /* Darker submenu button */
            color: #f0f0f0; /* Light submenu text */
            cursor: pointer;
        }
        pre {
            background-color: #282828; /* Dark pre background */
            padding: 15px;
            border: 1px solid #555; /* Darker border */
            color: #d4d4d4; /* Light pre text */
        }
    </style>
</head>
<body>
    <div class="left">
        <form method="post">
            {% for group, commands in command_groups.items() %}
            <div class="group">
                <button type="button" onclick="toggleSubmenu('submenu{{ loop.index }}')">{{ group }}</button>
                <div class="submenu" id="submenu{{ loop.index }}">
                    {% for label in commands.keys() %}
                        <button type="submit" name="command" value="{{ label }}">
                            {{ label }} {% if commands[label].admin %}(Admin){% endif %}
                        </button>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </form>
    </div>
    <div class="right">
        <h3>Output:</h3>
        <pre>{{ output }}</pre>
    </div>

    <script>
        function toggleSubmenu(id) {
            var el = document.getElementById(id);
            el.style.display = el.style.display === 'block' ? 'none' : 'block';
        }
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'output' not in session:
        session['output'] = ""

    if request.method == 'POST':
        selected_label = request.form['command']
        output = ""
        found = False

        for group in COMMAND_GROUPS.values():
            for label, info in group.items():
                if label == selected_label:
                    cmd = info["cmd"]
                    if info.get("admin"):
                        try:
                            subprocess.run(
                                ['powershell', '-Command', cmd],
                                shell=True
                            )
                            output = f"✅ Ran admin command: {label}"
                        except Exception as e:
                            output = f"❌ Admin command error: {e}"
                    else:
                        try:
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                            output = result.stdout + result.stderr
                        except Exception as e:
                            output = f"❌ Error: {e}"
                    session['output'] = output
                    found = True
                    break
            if found:
                break

        return redirect(url_for('index'))

    return render_template_string(HTML_TEMPLATE, command_groups=COMMAND_GROUPS, output=session['output'])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006, debug=True)