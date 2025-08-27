from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import winreg
import json
import subprocess
import threading
from datetime import datetime

# Try to import win32com.client, fallback if not available
try:
    import win32com.client
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("pywin32 not available, shortcuts will not be resolved")

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

                    # Auto-detect executable type if not set and path contains pythonw.exe
                    if executable_type == "other" and "pythonw.exe" in path.lower():
                        executable_type = "pythonw"

                    # Build command based on executable type
                    if executable_type == "pythonw":
                        full_command = f'"{path}" {command}'
                    elif executable_type == "pwsh":
                        full_command = f'"{path}" -Command {command}'
                    elif executable_type == "cmd":
                        full_command = f'"{path}" /c {command}'
                    elif executable_type == "powershell":
                        full_command = f'"{path}" -Command {command}'
                    elif executable_type == "ahk_v2":
                        full_command = f'"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe" "{path}" {command}'
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
        """Launch an item - using exact same method as startup.py"""
        try:
            # Retrieve the first path, the command, and the executable type
            path = item["paths"][0]
            command = item.get("Command", "")
            executable_type = item.get("ExecutableType", "other")
            
            # Auto-detect executable type if not set and path contains pythonw.exe
            if executable_type == "other" and "pythonw.exe" in path.lower():
                executable_type = "pythonw"
            
            full_command = ""
            if executable_type == "pythonw":
                full_command = f'"{path}" {command}'
            elif executable_type == "pwsh":
                full_command = f'"{path}" -Command {command}'
            elif executable_type == "cmd":
                full_command = f'"{path}" /c {command}'
            elif executable_type == "powershell":
                full_command = f'"{path}" -Command {command}'
            elif executable_type == "ahk_v2":
                full_command = f'"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe" "{path}" {command}'
            else: # other
                if command:
                    full_command = f'"{path}" {command}'
                else:
                    full_command = f'"{path}"'
            
            os.system(f'start "" {full_command}')
            
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

def resolve_shortcut_powershell(shortcut_path):
    """Resolve a .lnk shortcut using PowerShell"""
    try:
        # Use PowerShell to resolve the shortcut
        ps_command = f'''
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut("{shortcut_path}")
        Write-Output "TARGET:$($shortcut.TargetPath)"
        Write-Output "ARGS:$($shortcut.Arguments)"
        Write-Output "WORKDIR:$($shortcut.WorkingDirectory)"
        '''
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            target_path = ""
            arguments = ""
            working_dir = ""
            
            for line in lines:
                if line.startswith("TARGET:"):
                    target_path = line[7:].strip()
                elif line.startswith("ARGS:"):
                    arguments = line[5:].strip()
                elif line.startswith("WORKDIR:"):
                    working_dir = line[8:].strip()
            
            if target_path:
                # If target path is relative, try to make it absolute using working directory
                if not os.path.isabs(target_path) and working_dir:
                    target_path = os.path.join(working_dir, target_path)
                
                return {
                    "target": target_path,
                    "arguments": arguments,
                    "working_dir": working_dir
                }
        
        print(f"PowerShell shortcut resolution failed: {result.stderr}")
        return None
        
    except Exception as e:
        print(f"Error resolving shortcut with PowerShell {shortcut_path}: {e}")
        return None

def resolve_shortcut(shortcut_path):
    """Resolve a .lnk shortcut to its target path"""
    # Try PowerShell method first (more reliable)
    result = resolve_shortcut_powershell(shortcut_path)
    if result:
        return result
    
    # Fallback to win32com if available
    if not WIN32_AVAILABLE:
        return None
        
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        target_path = shortcut.Targetpath
        arguments = shortcut.Arguments
        working_directory = shortcut.WorkingDirectory
        
        # If target path is relative, try to make it absolute using working directory
        if target_path and not os.path.isabs(target_path) and working_directory:
            target_path = os.path.join(working_directory, target_path)
        
        return {
            "target": target_path,
            "arguments": arguments,
            "working_dir": working_directory
        }
    except Exception as e:
        print(f"Error resolving shortcut {shortcut_path}: {e}")
        return None

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
                files_in_folder = os.listdir(folder)
                print(f"Scanning folder: {folder}")
                print(f"Found {len(files_in_folder)} files: {files_in_folder}")
                
                for filename in files_in_folder:
                    file_path = os.path.join(folder, filename)
                    
                    # Skip directories and non-executable files
                    if os.path.isfile(file_path):
                        name, ext = os.path.splitext(filename)
                        
                        # Check if it's an executable type
                        if ext.lower() in ['.exe', '.bat', '.cmd', '.lnk', '.url']:
                            print(f"Found executable file: {filename} (type: {ext.lower()})")
                            # Skip if already exists in our items
                            if name.lower() not in existing_names:
                                actual_path = file_path
                                command_args = ""
                                executable_type = "other"
                                original_shortcut = None
                                
                                # Handle shortcuts
                                if ext.lower() == '.lnk':
                                    original_shortcut = file_path
                                    shortcut_info = resolve_shortcut(file_path)
                                    
                                    if shortcut_info and shortcut_info["target"] and os.path.exists(shortcut_info["target"]):
                                        # Successfully resolved shortcut
                                        actual_path = shortcut_info["target"]
                                        command_args = shortcut_info["arguments"] or ""
                                        
                                        # Determine executable type based on target
                                        target_ext = os.path.splitext(actual_path)[1].lower()
                                        if "python" in actual_path.lower():
                                            executable_type = "pythonw"
                                        elif target_ext in ['.ps1'] or "powershell" in actual_path.lower():
                                            executable_type = "pwsh"
                                        elif target_ext in ['.bat', '.cmd']:
                                            executable_type = "cmd"
                                    else:
                                        # Fallback: use shortcut path as-is
                                        print(f"Could not resolve shortcut {file_path}, using as-is")
                                        actual_path = file_path
                                        executable_type = "other"
                                
                                # Determine item type
                                if ext.lower() == '.exe' or (ext.lower() == '.lnk' and actual_path.endswith('.exe')):
                                    item_type = "App"
                                else:
                                    item_type = "Command"
                                
                                # Add item (check if actual path exists, or use original for shortcuts)
                                path_to_check = actual_path if ext.lower() != '.lnk' or os.path.exists(actual_path) else file_path
                                
                                if os.path.exists(path_to_check):
                                    found_items.append({
                                        "name": name,
                                        "type": item_type,
                                        "path": actual_path,
                                        "command": command_args,
                                        "executable_type": executable_type,
                                        "extension": ext.lower(),
                                        "folder": "System" if "ProgramData" in folder else "User",
                                        "original_shortcut": original_shortcut
                                    })
                                    print(f"Added item: {name} -> {actual_path}")
                                else:
                                    print(f"Path does not exist: {path_to_check}")
                            else:
                                print(f"Item already exists: {name}")
                        else:
                            print(f"Skipping non-executable file: {filename}")
        except Exception as e:
            print(f"Error scanning folder {folder}: {e}")
            continue
    
    return jsonify({
        "success": True,
        "items": found_items,
        "count": len(found_items)
    })

@app.route('/api/delete-shortcut', methods=['POST'])
def delete_shortcut():
    """Delete a shortcut file from the startup folder"""
    try:
        data = request.get_json()
        shortcut_path = data.get('shortcut_path')
        
        if not shortcut_path:
            return jsonify({'success': False, 'error': 'No shortcut path provided'})
        
        if not os.path.exists(shortcut_path):
            return jsonify({'success': False, 'error': 'Shortcut file not found'})
        
        # Delete the shortcut file
        os.remove(shortcut_path)
        print(f"Deleted shortcut: {shortcut_path}")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully deleted shortcut: {os.path.basename(shortcut_path)}'
        })
    except Exception as e:
        print(f"Error deleting shortcut: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete-matching-shortcuts', methods=['POST'])
def delete_matching_shortcuts():
    """Delete shortcuts from startup folders that match existing items in the startup list"""
    try:
        # Get existing startup items
        existing_items = startup_manager.load_items()
        existing_names = {item["name"].lower() for item in existing_items}
        
        startup_folders = [
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
            r"C:\Users\nahid\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
        ]
        
        deleted_shortcuts = []
        errors = []
        
        for folder in startup_folders:
            try:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        if filename.lower().endswith('.lnk'):
                            file_path = os.path.join(folder, filename)
                            name = os.path.splitext(filename)[0]
                            
                            # Check if this shortcut matches an existing item
                            if name.lower() in existing_names:
                                try:
                                    os.remove(file_path)
                                    deleted_shortcuts.append({
                                        'name': name,
                                        'path': file_path,
                                        'folder': os.path.basename(folder)
                                    })
                                    print(f"Deleted matching shortcut: {file_path}")
                                except Exception as e:
                                    errors.append(f"Failed to delete {file_path}: {str(e)}")
                                    print(f"Error deleting {file_path}: {e}")
            except Exception as e:
                errors.append(f"Error scanning folder {folder}: {str(e)}")
                print(f"Error scanning folder {folder}: {e}")
        
        return jsonify({
            'success': True,
            'deleted_shortcuts': deleted_shortcuts,
            'deleted_count': len(deleted_shortcuts),
            'errors': errors,
            'error_count': len(errors)
        })
    except Exception as e:
        print(f"Error in delete_matching_shortcuts: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # For pythonw.exe compatibility - suppress all console output and run silently
    import logging
    import sys
    
    try:
        # Redirect stdout and stderr to suppress all output when using pythonw.exe
        if sys.executable.endswith('pythonw.exe'):
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
        
        # Disable Flask and Werkzeug logging
        logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
        app.logger.setLevel(logging.CRITICAL)
        
        # Try to run Flask, with fallback port handling
        try:
            app.run(debug=False, host='0.0.0.0', port=4999, use_reloader=False, threaded=True)
        except OSError as port_error:
            # If port 4999 is busy, try port 5000
            if "Address already in use" in str(port_error):
                app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
            else:
                raise
        
    except Exception as e:
        # If running with pythonw.exe, errors won't be visible, so try to log to a file
        try:
            error_log = os.path.join(os.path.dirname(__file__), 'flask_error.log')
            with open(error_log, 'a') as f:
                f.write(f"{datetime.now()}: Flask startup error: {str(e)}\n")
        except:
            pass  # If we can't even log, just fail silently