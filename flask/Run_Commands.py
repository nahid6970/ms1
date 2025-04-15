from flask import Flask, request, render_template_string, redirect, url_for, session
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Make sure to change this to something secure

# Grouped command structure: { "Group Label": { "Sub-Label": "command" } }
COMMAND_GROUPS = {
    "System Commands": {
        "IP Config": "ipconfig",
        "System Info": "systeminfo"
    },
    "Tools": {
        "Open Notepad": "start notepad",
        "Open Calculator": "start calc"
    },
    "Display Settings": {
        "Switch to Display 1": "C:/msBackups/Display/DisplaySwitch.exe /internal",
        "Switch to Display 2": "C:/msBackups/Display/DisplaySwitch.exe /external"
    },
    "File Management": {
        "List Files": "dir"
    }
}

# Admin command to allow port 5006 through the firewall
ADMIN_COMMANDS = {
    "Allow Port 5006": 'Start-Process powershell -Verb RunAs -ArgumentList "-NoExit", "New-NetFirewallRule -DisplayName \'Allow_Port_5006\' -Direction Inbound -Protocol TCP -LocalPort 5006 -Action Allow -Profile Any"'
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
            margin: 0;
            padding: 20px;
        }
        h2 {
            color: #50fa7b;
            text-align: center;
        }
        .container {
            display: flex;
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
        .group {
            margin-bottom: 10px;
        }
        .group > button {
            width: 100%;
            background-color: #6272a4;
            color: white;
            border: none;
            padding: 10px;
            margin-bottom: 5px;
            cursor: pointer;
            font-weight: bold;
            border-radius: 5px;
            text-align: left;
        }
        .submenu {
            display: none;
            margin-top: 5px;
            margin-left: 10px;
        }
        .submenu button {
            background-color: #44475a;
            margin: 5px 0;
            padding: 8px;
            width: 100%;
            color: white;
            border: none;
            border-radius: 5px;
            text-align: left;
            cursor: pointer;
        }
        .submenu button:hover {
            background-color: #7083b8;
        }
        .output {
            flex: 2;
            background-color: #282a36;
            padding: 20px;
            border-radius: 8px;
        }
        .output h3 {
            color: #8be9fd;
        }
        pre {
            background-color: #1e1e2f;
            color: #f1fa8c;
            padding: 15px;
            border-radius: 5px;
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 600px;
            overflow-y: auto;
        }
    </style>
    <script>
        function toggleSubmenu(id) {
            const el = document.getElementById(id);
            if (el.style.display === 'block') {
                el.style.display = 'none';
                removeFromOpenSubmenus(id);
            } else {
                el.style.display = 'block';
                addToOpenSubmenus(id);
            }
        }
        function addToOpenSubmenus(id) {
            let openSubmenus = JSON.parse(localStorage.getItem('openSubmenus') || '[]');
            if (!openSubmenus.includes(id)) {
                openSubmenus.push(id);
                localStorage.setItem('openSubmenus', JSON.stringify(openSubmenus));
            }
        }
        function removeFromOpenSubmenus(id) {
            let openSubmenus = JSON.parse(localStorage.getItem('openSubmenus') || '[]');
            openSubmenus = openSubmenus.filter(function(item) { return item !== id; });
            localStorage.setItem('openSubmenus', JSON.stringify(openSubmenus));
        }
        document.addEventListener("DOMContentLoaded", function() {
            let openSubmenus = JSON.parse(localStorage.getItem('openSubmenus') || '[]');
            openSubmenus.forEach(function(id) {
                let el = document.getElementById(id);
                if (el) {
                    el.style.display = 'block';
                }
            });
        });
    </script>
</head>
<body>
    <h2>🚀 Windows Command Center</h2>
    <div class="container">
        <div class="commands">
            <form method="post">
                {% for group, subcmds in commands.items() %}
                    <div class="group">
                        <button type="button" onclick="toggleSubmenu('{{ loop.index }}')">{{ group }}</button>
                        <div class="submenu" id="{{ loop.index }}">
                            {% for label, cmd in subcmds.items() %}
                                <button type="submit" name="command" value="{{ cmd }}">{{ label }}</button>
                            {% endfor %}
                        </div>
                    </div>
                {% endfor %}
                <hr><h3>🔐 Admin Commands</h3>
                {% for label in admin_commands %}
                    <button type="submit" name="admin_command" value="{{ label }}">{{ label }}</button><br><br>
                {% endfor %}
            </form>
        </div>
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
        # Regular commands
        if 'command' in request.form:
            cmd = request.form['command']
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                session['output'] = result.stdout + result.stderr
            except Exception as e:
                session['output'] = f"❌ Error: {e}"

        # Admin commands
        elif 'admin_command' in request.form:
            cmd_label = request.form['admin_command']
            if cmd_label in ADMIN_COMMANDS:
                try:
                    subprocess.run(
                        ['powershell', '-Command', ADMIN_COMMANDS[cmd_label]],
                        shell=True
                    )
                    session['output'] = f"✅ Ran admin command: {cmd_label}"
                except Exception as e:
                    session['output'] = f"❌ Error: {e}"
            else:
                session['output'] = "Unknown admin command"
        
        return redirect(url_for('index'))

    output = session.pop('output', '')
    return render_template_string(HTML_TEMPLATE, commands=COMMAND_GROUPS, admin_commands=ADMIN_COMMANDS.keys(), output=output)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5006, debug=True)
