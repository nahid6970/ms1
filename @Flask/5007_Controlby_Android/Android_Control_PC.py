from flask import Flask, request, render_template, redirect, url_for, jsonify
import subprocess
import threading
import time
import json
import tempfile
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
try:
    app.json.sort_keys = False
except AttributeError:
    pass

COMMANDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commands.json')

DEFAULT_COMMANDS = {
    "Display 1": {
        "command": "C:\\@delta\\msBackups\\Display\\DisplaySwitch.exe /internal",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "Display 2": {
        "command": "C:\\@delta\\msBackups\\Display\\DisplaySwitch.exe /external",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "Display 1 KillApps": {
        "command": "C:\\@delta\\ms1\\scripts\\Autohtokey\\Command\\monitor_1.ahk && taskkill /IM python.exe /IM notepad++.exe /IM dnplayer.exe /F",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "Show IP Config": {
        "command": "ipconfig",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "Open Notepad": {
        "command": "start notepad",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "Open Calculator": {
        "command": "start calc",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "System Info": {
        "command": "systeminfo",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#cad13d",
        "bgColor": "#1e293b"
    },
    "Shutdown": {
        "command": "shutdown /s /t 0",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#ef4444",
        "bgColor": "#1e293b"
    },
    "Restart": {
        "command": "shutdown /r /t 0",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#ef4444",
        "bgColor": "#1e293b"
    },
    "Sign Out": {
        "command": "shutdown /l",
        "textColor": "#f8fafc",
        "cmdColor": "#64748b",
        "accentColor": "#ef4444",
        "bgColor": "#1e293b"
    }
}

def load_commands():
    if not os.path.exists(COMMANDS_FILE):
        save_commands(DEFAULT_COMMANDS)
        return DEFAULT_COMMANDS
    try:
        with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Migrate old formats
        migrated = False
        for k, v in list(data.items()):
            if isinstance(v, str):
                data[k] = {
                    "command": v,
                    "textColor": "#f8fafc",
                    "cmdColor": "#64748b",
                    "accentColor": "#cad13d",
                    "bgColor": "#1e293b"
                }
                migrated = True
            elif isinstance(v, dict):
                # Ensure all dynamic keys exist
                if "bgColor" not in v:
                    v["bgColor"] = "#1e293b"
                    migrated = True
                if "textColor" not in v:
                    v["textColor"] = "#f8fafc"
                    migrated = True
                if "cmdColor" not in v:
                    v["cmdColor"] = "#64748b"
                    migrated = True
                if "accentColor" not in v:
                    v["accentColor"] = "#cad13d"
                    migrated = True
                if "cmdType" not in v:
                    v["cmdType"] = "command"
                    migrated = True
                    
        if migrated:
            save_commands(data)
        return data
    except Exception as e:
        print(f"Error loading commands: {e}")
        return DEFAULT_COMMANDS

def save_commands(commands):
    try:
        with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(commands, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving commands: {e}")

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
        
        # Check command type
        cmd_type = "command"
        commands = load_commands()
        if label in commands:
            cmd_type = commands[label].get("cmdType", "command")
            
        if cmd_type == "ahk":
            command_outputs.append(f"Executing AHK Shortcut: {cmd}")
            # Create a temporary ahk script
            fd, temp_path = tempfile.mkstemp(suffix=".ahk")
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(f'#Requires AutoHotkey v2.0\nSend("{cmd}")\n')
            
            # Execute the script
            result = subprocess.run(f'start /wait "" "{temp_path}"', shell=True, capture_output=True, text=True, timeout=10)
            
            # Cleanup
            try:
                os.remove(temp_path)
            except:
                pass
        else:
            # Execute normal command
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
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        command_outputs.append(f"[{timestamp}] Command timed out after 30 seconds")
        command_outputs.append("-" * 50)
    except Exception as e:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        command_outputs.append(f"[{timestamp}] Error executing command: {str(e)}")
        command_outputs.append("-" * 50)

@app.route('/', methods=['GET', 'POST'])
def index():
    commands = load_commands()
    if request.method == 'POST':
        cmd = request.form.get('command')
        if cmd:
            # Find the label for this command
            label = "Unknown Command"
            for k, v in commands.items():
                v_cmd = v.get('command') if isinstance(v, dict) else v
                if v_cmd == cmd:
                    label = k
                    break
            
            # Execute command in background thread
            thread = threading.Thread(target=execute_command, args=(cmd, label))
            thread.daemon = True
            thread.start()
            
            # Redirect to prevent re-submitting the form on refresh
            return redirect(url_for('index'))

    return render_template("index.html", commands=commands, outputs=command_outputs)

@app.route('/get_output')
def get_output():
    """API endpoint to get latest command outputs"""
    return jsonify({"outputs": command_outputs})

@app.route('/run_command', methods=['POST'])
def run_command_api():
    """API endpoint to run a command asynchronously"""
    data = request.get_json() or {}
    cmd = data.get('command')
    label = data.get('label', 'Unknown Command')
    
    if not cmd:
        return jsonify({"success": False, "error": "No command provided"}), 400
        
    thread = threading.Thread(target=execute_command, args=(cmd, label))
    thread.daemon = True
    thread.start()
    return jsonify({"success": True})

@app.route('/add_command', methods=['POST'])
def add_command():
    """API endpoint to add a custom command"""
    data = request.get_json() or {}
    label = data.get('label', '').strip()
    cmd = data.get('command', '').strip()
    
    if not label or not cmd:
        return jsonify({"success": False, "error": "Both label and command are required"}), 400
        
    commands = load_commands()
    if label in commands:
        return jsonify({"success": False, "error": "A command with this label already exists"}), 400
        
    commands[label] = {
        "command": cmd,
        "cmdType": data.get('cmdType', 'command'),
        "textColor": data.get('textColor', '#f8fafc'),
        "cmdColor": data.get('cmdColor', '#64748b'),
        "accentColor": data.get('accentColor', '#cad13d'),
        "bgColor": data.get('bgColor', '#1e293b')
    }
    save_commands(commands)
    return jsonify({"success": True, "commands": commands})

@app.route('/delete_command', methods=['POST'])
def delete_command():
    """API endpoint to delete a custom command"""
    data = request.get_json() or {}
    label = data.get('label', '').strip()
    
    if not label:
        return jsonify({"success": False, "error": "Label is required"}), 400
        
    commands = load_commands()
    if label in commands:
        del commands[label]
        save_commands(commands)
        return jsonify({"success": True, "commands": commands})
        
    return jsonify({"success": False, "error": "Command not found"}), 404

@app.route('/save_commands', methods=['POST'])
def save_commands_api():
    """API endpoint to persist full commands list (useful for drag-n-drop reordering, edits, etc.)"""
    data = request.get_json() or {}
    commands = data.get('commands')
    
    if not isinstance(commands, dict):
        return jsonify({"success": False, "error": "Invalid format, must be a dictionary"}), 400
        
    save_commands(commands)
    return jsonify({"success": True, "commands": commands})

@app.route('/clear_output', methods=['POST'])
def clear_output():
    """API endpoint to clear output history"""
    global command_outputs
    command_outputs.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007, debug=True)