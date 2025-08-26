from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import winreg
import json
import subprocess
import threading
from datetime import datetime

app = Flask(__name__)

class StartupManager:
    def __init__(self):
        self.json_file = os.path.join(os.path.dirname(__file__), "startup_items.json")
        
    def load_items(self):
        """Load items from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Failed to load items: {e}")
            return []

    def save_items(self, items):
        """Save items to JSON file"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save items: {e}")
            return False

    def filter_existing_items(self, items):
        """Filter out items with no valid paths."""
        filtered_items = []
        for item in items:
            for path in item["paths"]:
                if os.path.exists(path):
                    filtered_items.append({
                        "type": item["type"],
                        "name": item["name"],
                        "paths": [path],
                        "Command": item.get("Command", ""),
                        "ExecutableType": item.get("ExecutableType", "other"),
                    })
                    break
        return filtered_items

    def is_checked(self, item):
        """Check if item is in Windows startup registry"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_READ) as reg_key:
                try:
                    winreg.QueryValueEx(reg_key, item["name"])
                    return True
                except FileNotFoundError:
                    return False
        except WindowsError:
            return False

    def toggle_startup(self, item):
        """Toggle startup status of an item"""
        reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        try:
            if self.is_checked(item):
                # Remove from startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    winreg.DeleteValue(reg_key, item["name"])
                return {"success": True, "action": "disabled"}
            else:
                # Add to startup
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS) as reg_key:
                    path = item["paths"][0]
                    command = item.get("Command", "")
                    executable_type = item.get("ExecutableType", "other")

                    # Build command based on executable type
                    if executable_type == "pythonw":
                        full_command = f'"{path}" {command}'
                    elif executable_type == "pwsh":
                        full_command = f'"{path}" -Command {command}'
                    elif executable_type == "cmd":
                        full_command = f'"{path}" /c {command}'
                    elif executable_type == "powershell":
                        full_command = f'"{path}" -Command {command}'
                    else:
                        if command:
                            full_command = f'"{path}" {command}'
                        else:
                            full_command = f'"{path}"'
                    
                    winreg.SetValueEx(reg_key, item["name"], 0, winreg.REG_SZ, full_command)
                return {"success": True, "action": "enabled"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def launch_item(self, item):
        """Launch an item"""
        try:
            path = item["paths"][0]
            command = item.get("Command", "")
            executable_type = item.get("ExecutableType", "other")
            
            if executable_type == "pythonw":
                full_command = f'"{path}" {command}'
            elif executable_type == "pwsh":
                full_command = f'"{path}" -Command {command}'
            elif executable_type == "cmd":
                full_command = f'"{path}" /c {command}'
            elif executable_type == "powershell":
                full_command = f'"{path}" -Command {command}'
            else:
                if command:
                    full_command = f'"{path}" {command}'
                else:
                    full_command = f'"{path}"'
            
            subprocess.Popen(full_command, shell=True)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

# Initialize the startup manager
startup_manager = StartupManager()

@app.route('/')
def index():
    """Main page"""
    items = startup_manager.filter_existing_items(startup_manager.load_items())
    
    # Separate and sort items
    commands = sorted([item for item in items if item["type"] == "Command"], key=lambda x: x["name"].lower())
    apps = sorted([item for item in items if item["type"] == "App"], key=lambda x: x["name"].lower())
    
    # Add startup status to each item
    for item in commands + apps:
        item['is_enabled'] = startup_manager.is_checked(item)
    
    return render_template('index.html', commands=commands, apps=apps)

@app.route('/api/toggle/<item_name>', methods=['POST'])
def toggle_startup(item_name):
    """Toggle startup status of an item"""
    items = startup_manager.load_items()
    item = next((item for item in items if item["name"] == item_name), None)
    
    if not item:
        return jsonify({"success": False, "error": "Item not found"})
    
    result = startup_manager.toggle_startup(item)
    return jsonify(result)

@app.route('/api/launch/<item_name>', methods=['POST'])
def launch_item(item_name):
    """Launch an item"""
    items = startup_manager.load_items()
    item = next((item for item in items if item["name"] == item_name), None)
    
    if not item:
        return jsonify({"success": False, "error": "Item not found"})
    
    result = startup_manager.launch_item(item)
    return jsonify(result)

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all items with their status"""
    items = startup_manager.filter_existing_items(startup_manager.load_items())
    
    for item in items:
        item['is_enabled'] = startup_manager.is_checked(item)
    
    return jsonify(items)

@app.route('/add', methods=['POST'])
def add_item():
    """Add new item API endpoint"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('path'):
        return jsonify({"success": False, "error": "Name and Path are required"})
    
    # Check if path exists
    if not os.path.exists(data['path']):
        return jsonify({"success": False, "error": "The specified path does not exist"})
    
    # Check if item already exists
    items = startup_manager.load_items()
    if any(item["name"] == data['name'] for item in items):
        return jsonify({"success": False, "error": "An item with this name already exists"})
    
    # Create new item
    new_item = {
        "name": data['name'],
        "type": data.get('type', 'App'),
        "paths": [data['path']],
        "Command": data.get('command', ''),
        "ExecutableType": data.get('executable_type', 'other')
    }
    
    items.append(new_item)
    if startup_manager.save_items(items):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to save item"})

@app.route('/edit/<item_name>', methods=['POST'])
def edit_item(item_name):
    """Edit item API endpoint"""
    items = startup_manager.load_items()
    item = next((item for item in items if item["name"] == item_name), None)
    
    if not item:
        return jsonify({"success": False, "error": "Item not found"})
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('path'):
        return jsonify({"success": False, "error": "Name and Path are required"})
    
    # Check if path exists
    if not os.path.exists(data['path']):
        return jsonify({"success": False, "error": "The specified path does not exist"})
    
    # Update item
    for i, stored_item in enumerate(items):
        if stored_item["name"] == item_name:
            items[i] = {
                "name": data['name'],
                "type": data.get('type', 'App'),
                "paths": [data['path']],
                "Command": data.get('command', ''),
                "ExecutableType": data.get('executable_type', 'other')
            }
            break
    
    if startup_manager.save_items(items):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to save item"})

@app.route('/api/delete/<item_name>', methods=['DELETE'])
def delete_item(item_name):
    """Delete an item"""
    items = startup_manager.load_items()
    item = next((item for item in items if item["name"] == item_name), None)
    
    if not item:
        return jsonify({"success": False, "error": "Item not found"})
    
    # Remove from startup if enabled
    if startup_manager.is_checked(item):
        startup_manager.toggle_startup(item)
    
    # Remove from items list
    items = [stored_item for stored_item in items if stored_item["name"] != item_name]
    
    if startup_manager.save_items(items):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to delete item"})

@app.route('/api/copy-registry-path', methods=['POST'])
def copy_registry_path():
    """Copy registry path to clipboard (placeholder - requires client-side implementation)"""
    registry_path = "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    return jsonify({"success": True, "path": registry_path})

@app.route('/api/scan-startup-folders', methods=['GET'])
def scan_startup_folders():
    """Scan Windows startup folders for items"""
    startup_folders = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
        r"C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    ]
    
    found_items = []
    existing_items = startup_manager.load_items()
    existing_names = {item["name"].lower() for item in existing_items}
    
    for folder in startup_folders:
        try:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    
                    # Skip directories and non-executable files
                    if os.path.isfile(file_path):
                        name, ext = os.path.splitext(filename)
                        
                        # Check if it's an executable type
                        if ext.lower() in ['.exe', '.bat', '.cmd', '.lnk', '.url']:
                            # Skip if already exists in our items
                            if name.lower() not in existing_names:
                                item_type = "App" if ext.lower() == '.exe' else "Command"
                                
                                found_items.append({
                                    "name": name,
                                    "type": item_type,
                                    "path": file_path,
                                    "extension": ext.lower(),
                                    "folder": "System" if "ProgramData" in folder else "User"
                                })
        except Exception as e:
            print(f"Error scanning folder {folder}: {e}")
            continue
    
    return jsonify({
        "success": True,
        "items": found_items,
        "count": len(found_items)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4999)