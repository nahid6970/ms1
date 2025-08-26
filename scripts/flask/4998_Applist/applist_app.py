from flask import Flask, render_template, request, jsonify
import json
import os
import subprocess
import threading

app = Flask(__name__)

# Configuration
DATA_FILE = r"C:\Users\nahid\ms\ms1\scripts\flask\4998_Applist\data.json"

def load_applications():
    """Load applications from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            apps = json.load(f)
            # Sort applications by name
            apps.sort(key=lambda x: x.get("name", "").lower())
            return apps
    return []

def save_applications(apps):
    """Save applications to JSON file"""
    serializable_apps = []
    for app in apps:
        serializable_apps.append({
            "name": app["name"],
            "scoop_name": app["scoop_name"],
            "scoop_path": app["scoop_path"],
            "winget_name": app["winget_name"],
            "winget_path": app["winget_path"]
        })
    with open(DATA_FILE, "w") as f:
        json.dump(serializable_apps, f, indent=4)

def check_installation_status(app):
    """Check if application is installed via Scoop or Winget"""
    scoop_installed = os.path.exists(app["scoop_path"]) if app["scoop_path"] else False
    winget_installed = os.path.exists(app["winget_path"]) if app["winget_path"] else False
    
    return {
        "installed": scoop_installed or winget_installed,
        "scoop_installed": scoop_installed,
        "winget_installed": winget_installed,
        "source": "both" if (scoop_installed and winget_installed) else ("scoop" if scoop_installed else ("winget" if winget_installed else None)),
        "display": "[S]" if scoop_installed and not winget_installed else "[W]" if winget_installed and not scoop_installed else "[S][W]" if (scoop_installed and winget_installed) else "[X]"
    }

@app.route('/')
def index():
    """Main page showing all applications"""
    applications = load_applications()
    
    # Add installation status to each app
    for app in applications:
        app["status"] = check_installation_status(app)
    
    return render_template('applist.html', applications=applications)

@app.route('/api/apps')
def get_apps():
    """API endpoint to get all applications"""
    applications = load_applications()
    
    # Add installation status to each app
    for app in applications:
        app["status"] = check_installation_status(app)
    
    return jsonify(applications)

@app.route('/api/install/<app_name>', methods=['POST'])
def install_app(app_name):
    """Install application via Scoop or Winget"""
    try:
        applications = load_applications()
        app = next((a for a in applications if a["name"] == app_name), None)
        
        if not app:
            return jsonify({"success": False, "error": "Application not found"})
        
        data = request.get_json()
        source = data.get('source', 'auto')
        
        if source == 'scoop' and app["scoop_name"]:
            cmd = f'pwsh -Command "scoop install {app["scoop_name"]}"'
        elif source == 'winget' and app["winget_name"]:
            cmd = f'winget install {app["winget_name"]}'
        else:
            # Auto-select based on availability
            if app["scoop_name"]:
                cmd = f'pwsh -Command "scoop install {app["scoop_name"]}"'
                source = 'scoop'
            elif app["winget_name"]:
                cmd = f'winget install {app["winget_name"]}'
                source = 'winget'
            else:
                return jsonify({"success": False, "error": "No installation method available"})
        
        # Run installation in new terminal window
        def run_install():
            # Create a new terminal window to show the output
            terminal_cmd = f'start "Installing {app_name}" cmd /k "{cmd}"'
            subprocess.Popen(terminal_cmd, shell=True)
        
        thread = threading.Thread(target=run_install)
        thread.start()
        
        return jsonify({"success": True, "message": f"Installing {app_name} via {source} in new terminal"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/uninstall/<app_name>', methods=['POST'])
def uninstall_app(app_name):
    """Uninstall application via Scoop or Winget"""
    try:
        applications = load_applications()
        app = next((a for a in applications if a["name"] == app_name), None)
        
        if not app:
            return jsonify({"success": False, "error": "Application not found"})
        
        data = request.get_json()
        source = data.get('source', 'auto')
        
        if source == 'scoop' and app["scoop_name"]:
            cmd = f'pwsh -Command "scoop uninstall {app["scoop_name"]}"'
        elif source == 'winget' and app["winget_name"]:
            cmd = f'winget uninstall {app["winget_name"]}'
        else:
            # Auto-select based on what's installed
            status = check_installation_status(app)
            if status["source"] == "scoop":
                cmd = f'pwsh -Command "scoop uninstall {app["scoop_name"]}"'
                source = 'scoop'
            elif status["source"] == "winget":
                cmd = f'winget uninstall {app["winget_name"]}'
                source = 'winget'
            else:
                return jsonify({"success": False, "error": "Application not installed"})
        
        # Run uninstallation in new terminal window
        def run_uninstall():
            # Create a new terminal window to show the output
            terminal_cmd = f'start "Uninstalling {app_name}" cmd /k "{cmd}"'
            subprocess.Popen(terminal_cmd, shell=True)
        
        thread = threading.Thread(target=run_uninstall)
        thread.start()
        
        return jsonify({"success": True, "message": f"Uninstalling {app_name} via {source} in new terminal"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/open-location/<app_name>', methods=['POST'])
def open_location(app_name):
    """Open file location in explorer"""
    try:
        applications = load_applications()
        app = next((a for a in applications if a["name"] == app_name), None)
        
        if not app:
            return jsonify({"success": False, "error": "Application not found"})
        
        data = request.get_json()
        source = data.get('source', 'auto')
        
        if source == 'scoop' and app["scoop_path"] and os.path.exists(app["scoop_path"]):
            cmd = f'explorer /select,"{app["scoop_path"]}"'
        elif source == 'winget' and app["winget_path"] and os.path.exists(app["winget_path"]):
            cmd = f'explorer /select,"{app["winget_path"]}"'
        else:
            # Auto-select based on what exists
            if app["scoop_path"] and os.path.exists(app["scoop_path"]):
                cmd = f'explorer /select,"{app["scoop_path"]}"'
            elif app["winget_path"] and os.path.exists(app["winget_path"]):
                cmd = f'explorer /select,"{app["winget_path"]}"'
            else:
                return jsonify({"success": False, "error": "No valid path found"})
        
        subprocess.Popen(cmd, shell=True)
        return jsonify({"success": True, "message": f"Opening location for {app_name}"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/add', methods=['POST'])
def add_app():
    """Add new application"""
    try:
        data = request.get_json()
        
        new_app = {
            "name": data.get("name", "").strip(),
            "scoop_name": data.get("scoop_name", "").strip(),
            "scoop_path": data.get("scoop_path", "").strip(),
            "winget_name": data.get("winget_name", "").strip(),
            "winget_path": data.get("winget_path", "").strip()
        }
        
        if not new_app["name"]:
            return jsonify({"success": False, "error": "App name is required"})
        
        applications = load_applications()
        
        # Check if app already exists
        if any(app["name"] == new_app["name"] for app in applications):
            return jsonify({"success": False, "error": "Application already exists"})
        
        applications.append(new_app)
        save_applications(applications)
        
        return jsonify({"success": True, "message": f"Added {new_app['name']} successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/edit/<app_name>', methods=['POST'])
def edit_app(app_name):
    """Edit existing application"""
    try:
        data = request.get_json()
        applications = load_applications()
        
        app = next((a for a in applications if a["name"] == app_name), None)
        if not app:
            return jsonify({"success": False, "error": "Application not found"})
        
        # Update app data
        app["name"] = data.get("name", app["name"]).strip()
        app["scoop_name"] = data.get("scoop_name", app["scoop_name"]).strip()
        app["scoop_path"] = data.get("scoop_path", app["scoop_path"]).strip()
        app["winget_name"] = data.get("winget_name", app["winget_name"]).strip()
        app["winget_path"] = data.get("winget_path", app["winget_path"]).strip()
        
        if not app["name"]:
            return jsonify({"success": False, "error": "App name is required"})
        
        save_applications(applications)
        
        return jsonify({"success": True, "message": f"Updated {app['name']} successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/delete/<app_name>', methods=['DELETE'])
def delete_app(app_name):
    """Delete application"""
    try:
        applications = load_applications()
        
        # Find and remove the app
        applications = [app for app in applications if app["name"] != app_name]
        save_applications(applications)
        
        return jsonify({"success": True, "message": f"Deleted {app_name} successfully"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4998)