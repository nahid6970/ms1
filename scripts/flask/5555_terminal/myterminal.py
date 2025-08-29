from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os
import threading
import time
from datetime import datetime

app = Flask(__name__)

# Store active PowerShell processes - with persistent working directory
class PowerShellSession:
    def __init__(self):
        self.current_directory = os.path.expanduser('~')  # Start in home directory
        self.app_directory = os.path.dirname(os.path.abspath(__file__))
        self.history_file = os.path.join(self.app_directory, '.pwsh_web_history.json')
        self.command_history = self._load_history()
        self.profile_loaded = False
        self.profile_error = None
        self.profile_path = os.path.join(self.app_directory, 'Microsoft.PowerShell_profile.ps1')
        
        # Try to load PowerShell profile on initialization
        self._load_profile()
    
    def _load_profile(self):
        """Load PowerShell profile if it exists"""
        self.profile_error = None
        try:
            if os.path.exists(self.profile_path):
                print(f"Found PowerShell profile: {self.profile_path}")
                # First, validate the profile syntax
                validate_result = subprocess.run(
                    ['powershell', '-Command', f'Get-Command -Syntax; $null = Get-Content "{self.profile_path}" | ForEach-Object {{ [System.Management.Automation.PSParser]::Tokenize($_, [ref]$null) }}'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                # Try to load the profile
                result = subprocess.run(
                    ['powershell', '-Command', f'. "{self.profile_path}"'],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    cwd=self.current_directory,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                
                if result.returncode == 0:
                    self.profile_loaded = True
                    print("✓ PowerShell profile loaded successfully")
                    if result.stdout.strip():
                        print(f"Profile output: {result.stdout.strip()}")
                else:
                    self.profile_error = result.stderr.strip()
                    print(f"✗ Error loading profile: {self.profile_error}")
                    print("Tip: Check your PowerShell profile for syntax errors")
                    print(f"Profile location: {self.profile_path}")
            else:
                print(f"ℹ No PowerShell profile found at: {self.profile_path}")
        except Exception as e:
            self.profile_error = str(e)
            print(f"Exception loading profile: {e}")
    
    def _load_history(self):
        """Load command history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('commands', [])
            return []
        except Exception as e:
            print(f"Error loading history: {e}")
            return []
    
    def _save_history(self):
        """Save command history to file"""
        try:
            history_data = {
                'commands': self.command_history[-1000:],  # Keep only last 1000 commands
                'last_updated': datetime.now().isoformat(),
                'current_directory': self.current_directory
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _add_to_history(self, command):
        """Add command to history"""
        if command.strip():
            # If command exists, remove it to re-add it at the end
            if command in self.command_history:
                self.command_history.remove(command)
            self.command_history.append(command)
            self._save_history()
    
    def get_history(self):
        """Get command history in reverse order (latest first)"""
        return self.command_history[::-1]
    
    def get_profile_status(self):
        """Get profile loading status"""
        return {
            'profile_loaded': self.profile_loaded,
            'profile_path': self.profile_path,
            'profile_exists': os.path.exists(self.profile_path),
            'profile_error': self.profile_error
        }
    
    def execute_command(self, command):
        """Execute a command in PowerShell with persistent directory"""
        # Add to history before executing
        self._add_to_history(command)
        
        try:
            # Handle cd commands specially to maintain directory state
            if command.strip().lower().startswith('cd ') or command.strip().lower() == 'cd':
                return self._handle_cd_command(command.strip())
            
            # Build the command with profile loading
            full_command = command
            if self.profile_loaded and os.path.exists(self.profile_path):
                # Load profile before executing the command
                full_command = f'. "{self.profile_path}"; {command}'
            
            # For other commands, run in the current directory
            result = subprocess.run(
                ['powershell', '-Command', full_command],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.current_directory,  # Run in current directory
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            output = result.stdout.strip() if result.stdout else ''
            errors = result.stderr.strip() if result.stderr else ''
            
            # Combine output and errors
            full_output = []
            if output:
                full_output.append(output)
            if errors:
                full_output.append(errors)
            
            # Show current directory
            full_output.append(f"<span class=\"command-text\">Location: {self.current_directory}</span>")
            
            final_output = '\n'.join(full_output) if full_output else 'Command completed successfully'
            has_error = bool(result.returncode != 0 or errors)
            
            return final_output, has_error
            
        except subprocess.TimeoutExpired:
            return "Command timed out (30 seconds)", True
        except Exception as e:
            return f"Error executing command: {str(e)}", True
    
    def _handle_cd_command(self, command):
        """Handle cd command to maintain directory state"""
        # Add to history
        self._add_to_history(command)
        
        try:
            parts = command.split(' ', 1)
            if len(parts) == 1:  # Just 'cd' - go to home directory
                if os.name == 'nt':
                    new_path = os.path.expanduser('~')
                else:
                    new_path = os.path.expanduser('~')
            else:
                target = parts[1].strip().strip('"').strip("'")
                
                # Handle special cases
                if target == '..':
                    new_path = os.path.dirname(self.current_directory)
                elif target == '.':
                    new_path = self.current_directory
                elif target.endswith(':') and len(target) == 2:  # Drive letter like 'c:'
                    new_path = target.upper() + '\\'
                elif os.path.isabs(target):
                    new_path = target
                else:
                    new_path = os.path.join(self.current_directory, target)
            
            # Normalize and validate path
            new_path = os.path.abspath(new_path)
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_directory = new_path
                # Save updated directory to history file
                self._save_history()
                return f"Location: {self.current_directory}", False
            else:
                return f"cd: cannot access '{target}': No such file or directory\nLocation: {self.current_directory}", True
                
        except Exception as e:
            return f"Error changing directory: {str(e)}\nLocation: {self.current_directory}", True

    def delete_from_history(self, command):
        """Delete a command from history"""
        if command.strip() and command in self.command_history:
            self.command_history.remove(command)
            self._save_history()
            return True
        return False

# Global session (you could extend this to support multiple sessions)
pwsh_session = PowerShellSession()

@app.route('/')
def index():
    return render_template('terminal.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.json
    command = data.get('command', '').strip()
    
    if not command:
        return jsonify({
            'output': '',
            'error': False
        })
    
    # Execute the command
    output, has_error = pwsh_session.execute_command(command)
    
    return jsonify({
        'output': output,
        'error': has_error
    })

@app.route('/history', methods=['GET'])
def get_history():
    """Get command history"""
    return jsonify({
        'history': pwsh_session.get_history()
    })

@app.route('/history/delete', methods=['POST'])
def delete_history():
    """Delete a command from history"""
    data = request.json
    command = data.get('command', '').strip()
    if pwsh_session.delete_from_history(command):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Command not found in history'})

@app.route('/profile-status', methods=['GET'])
def get_profile_status():
    """Get PowerShell profile status"""
    return jsonify(pwsh_session.get_profile_status())

@app.route('/reload-profile', methods=['POST'])
def reload_profile():
    """Reload PowerShell profile"""
    pwsh_session._load_profile()
    return jsonify(pwsh_session.get_profile_status())





if __name__ == '__main__':
    print("Starting PowerShell Web Terminal on http://localhost:5555")
    profile_status = pwsh_session.get_profile_status()
    if profile_status['profile_loaded']:
        print(f"✓ PowerShell profile loaded: {profile_status['profile_path']}")
    elif profile_status['profile_exists']:
        print(f"✗ PowerShell profile found but failed to load: {profile_status['profile_path']}")
        if profile_status.get('profile_error'):
            print(f"   Error: {profile_status['profile_error']}")
        print("   Tip: Fix the syntax error in your profile and use the reload button in the web interface")
    else:
        print(f"ℹ No PowerShell profile found: {profile_status['profile_path']}")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5555, debug=True)