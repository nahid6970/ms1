from flask import Flask, request, render_template, redirect, url_for, jsonify
import subprocess
import threading
import time

app = Flask(__name__)

COMMANDS = {
    "Display 1": "C:\\msBackups\\Display\\DisplaySwitch.exe /internal",
    "Display 2": "C:\\msBackups\\Display\\DisplaySwitch.exe /external",
    "Display 1 KillApps": "C:\\Users\\nahid\\ms\\ms1\\scripts\\Autohtokey\\Command\\monitor_1.ahk && taskkill /IM python.exe /IM notepad++.exe /IM dnplayer.exe /F",
    "Show IP Config": "ipconfig",
    "Open Notepad": "start notepad",
    "Open Calculator": "start calc",
    "System Info": "systeminfo",
    "Shutdown": "shutdown /s /t 0",
    "Restart": "shutdown /r /t 0",
    "Sign Out": "shutdown /l"
}

# Store command outputs
command_outputs = []

def execute_command(cmd, label):
    """Execute command and capture output"""
    global command_outputs
    
    try:
        # Clear previous output
        command_outputs.clear()
        
        # Add timestamp and command info
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        command_outputs.append(f"[{timestamp}] Executing: {label}")
        command_outputs.append(f"Command: {cmd}")
        command_outputs.append("-" * 50)
        
        # Execute command and capture output
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            command_outputs.append(f"Output:\n{result.stdout.strip()}")
        if result.stderr:
            command_outputs.append(f"Error:\n{result.stderr.strip()}")
        if result.returncode != 0:
            command_outputs.append(f"Command failed with exit code: {result.returncode}")
        else:
            command_outputs.append("Command completed successfully")
            
        command_outputs.append("-" * 50)
        command_outputs.append("Ready for next command...")
            
    except subprocess.TimeoutExpired:
        command_outputs.append(f"[{timestamp}] Command timed out after 30 seconds")
        command_outputs.append("-" * 50)
    except Exception as e:
        command_outputs.append(f"[{timestamp}] Error executing command: {str(e)}")
        command_outputs.append("-" * 50)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        cmd = request.form['command']
        # Find the label for this command
        label = next((k for k, v in COMMANDS.items() if v == cmd), "Unknown Command")
        
        # Execute command in background thread
        thread = threading.Thread(target=execute_command, args=(cmd, label))
        thread.daemon = True
        thread.start()
        
        # Redirect to prevent re-submitting the form on refresh
        return redirect(url_for('index'))

    return render_template("index.html", commands=COMMANDS, outputs=command_outputs)

@app.route('/get_output')
def get_output():
    """API endpoint to get latest command outputs"""
    return jsonify({"outputs": command_outputs})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007, debug=True)