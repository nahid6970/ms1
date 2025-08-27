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
            # Avoid duplicates in history
            if command not in self.command_history:
                self.command_history.append(command)
            self._save_history()
    
    def get_history(self):
        """Get command history"""
        return self.command_history
    
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

@app.route('/profile-status', methods=['GET'])
def get_profile_status():
    """Get PowerShell profile status"""
    return jsonify(pwsh_session.get_profile_status())

@app.route('/reload-profile', methods=['POST'])
def reload_profile():
    """Reload PowerShell profile"""
    pwsh_session._load_profile()
    return jsonify(pwsh_session.get_profile_status())

# HTML Template (inline for simplicity)
terminal_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerShell Web Terminal</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #1e1e1e;
            color: #ffffff;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: #0078d4;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .header h1 {
            font-size: 18px;
            font-weight: normal;
        }
        
        .profile-status {
            font-size: 12px;
            opacity: 0.8;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .profile-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }
        
        .profile-loaded {
            background-color: #4CAF50;
        }
        
        .profile-not-loaded {
            background-color: #ff6b6b;
        }
        
        .reload-btn {
            background: transparent;
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        
        .reload-btn:hover {
            background: rgba(255,255,255,0.1);
        }
        
        .reload-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .terminal-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            padding: 20px;
            overflow: hidden;
        }
        
        .terminal-output {
            flex: 1;
            background: #000000;
            border: 1px solid #333;
            padding: 15px;
            overflow-y: auto;
            margin-bottom: 10px;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.4;
        }
        
        .terminal-input-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .prompt {
            color: #0078d4;
            font-weight: bold;
        }
        
        .terminal-input {
            flex: 1;
            background: #2d2d30;
            border: 1px solid #3e3e42;
            color: #ffffff;
            padding: 8px 12px;
            font-family: inherit;
            font-size: 14px;
            border-radius: 3px;
        }
        
        .terminal-input:focus {
            outline: none;
            border-color: #0078d4;
            box-shadow: 0 0 0 1px #0078d4;
        }
        
        .execute-btn {
            background: #0078d4;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 3px;
            cursor: pointer;
            font-family: inherit;
        }
        
        .execute-btn:hover {
            background: #106ebe;
        }
        
        .execute-btn:disabled {
            background: #666;
            cursor: not-allowed;
        }
        
        .command-line {
            color: #ffffff;
            margin-bottom: 5px;
        }
        
        .command-text {
            color: #ffff00;
        }
        
        .output-text {
            color: #ffffff;
            margin-bottom: 10px;
        }
        
        .error-text {
            color: #ff6b6b;
            margin-bottom: 10px;
        }
        
        .success-text {
            color: #4CAF50;
            margin-bottom: 10px;
        }
        
        .loading {
            color: #888;
            font-style: italic;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e1e1e;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #555;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #777;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-left">
            <h1>🔷 PowerShell Web Terminal</h1>
            <span style="font-size: 12px; opacity: 0.8;">Local Session - Port 5555</span>
        </div>
        <div class="profile-status" id="profile-status">
            <span class="profile-indicator profile-not-loaded"></span>
            <span>Profile: Loading...</span>
            <button id="reload-profile-btn" class="reload-btn" title="Reload PowerShell Profile">🔄</button>
        </div>
    </div>
    
    <div class="terminal-container">
        <div id="terminal-output" class="terminal-output">
            <div id="profile-info" class="output-text" style="margin-top: 10px;"></div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #333;">
            </div>
        </div>
        
        <div class="terminal-input-container">
            <span class="prompt">PS></span>
            <input type="text" id="command-input" class="terminal-input" placeholder="Enter PowerShell command..." autocomplete="off">
            <button id="execute-btn" class="execute-btn">Execute</button>
        </div>
    </div>

    <script>
        const outputDiv = document.getElementById('terminal-output');
        const commandInput = document.getElementById('command-input');
        const executeBtn = document.getElementById('execute-btn');
        const profileStatus = document.getElementById('profile-status');
        const profileInfo = document.getElementById('profile-info');
        const reloadProfileBtn = document.getElementById('reload-profile-btn');
        
        let commandHistory = [];
        let historyIndex = -1;
        
        // Load profile status
        async function loadProfileStatus() {
            try {
                const response = await fetch('/profile-status');
                const status = await response.json();
                updateProfileDisplay(status);
            } catch (error) {
                console.error('Error loading profile status:', error);
                const indicator = profileStatus.querySelector('.profile-indicator');
                const text = profileStatus.querySelector('span:last-child');
                indicator.className = 'profile-indicator profile-not-loaded';
                text.textContent = 'Profile: Error';
            }
        }
        
        function updateProfileDisplay(status) {
            const indicator = profileStatus.querySelector('.profile-indicator');
            const text = profileStatus.querySelector('span:nth-child(2)');
            
            if (status.profile_loaded) {
                indicator.className = 'profile-indicator profile-loaded';
                text.textContent = 'Profile: Loaded';
                profileInfo.innerHTML = `✓ PowerShell profile loaded successfully<br>📁 ${status.profile_path}`;
                profileInfo.className = 'success-text';
            } else if (status.profile_exists && status.profile_error) {
                indicator.className = 'profile-indicator profile-not-loaded';
                text.textContent = 'Profile: Error';
                profileInfo.innerHTML = `✗ PowerShell profile has syntax errors:<br>📁 ${status.profile_path}<br>🔴 ${status.profile_error}<br><br>💡 Fix the syntax error and click the reload button (🔄) to try again.`;
                profileInfo.className = 'error-text';
            } else if (status.profile_exists) {
                indicator.className = 'profile-indicator profile-not-loaded';
                text.textContent = 'Profile: Error';
                profileInfo.innerHTML = `⚠ PowerShell profile found but failed to load<br>📁 ${status.profile_path}`;
                profileInfo.className = 'error-text';
            } else {
                indicator.className = 'profile-indicator profile-not-loaded';
                text.textContent = 'Profile: Not Found';
                profileInfo.innerHTML = `ℹ No PowerShell profile found<br>📁 Expected at: ${status.profile_path}`;
                profileInfo.className = 'output-text';
            }
        }
        
        // Reload profile
        async function reloadProfile() {
            reloadProfileBtn.disabled = true;
            reloadProfileBtn.textContent = '⏳';
            
            try {
                const response = await fetch('/reload-profile', { method: 'POST' });
                const status = await response.json();
                updateProfileDisplay(status);
                
                // Add reload message to terminal
                if (status.profile_loaded) {
                    addToOutput('✓ PowerShell profile reloaded successfully', 'success-text');
                } else if (status.profile_error) {
                    addToOutput(`✗ Failed to reload profile: ${status.profile_error}`, 'error-text');
                } else {
                    addToOutput('⚠ Profile reload attempted but still not loaded', 'error-text');
                }
            } catch (error) {
                addToOutput(`Error reloading profile: ${error.message}`, 'error-text');
            } finally {
                reloadProfileBtn.disabled = false;
                reloadProfileBtn.textContent = '🔄';
            }
        }
        
        // Load command history on page load
        async function loadHistory() {
            try {
                const response = await fetch('/history');
                const result = await response.json();
                commandHistory = result.history || [];
                console.log(`Loaded ${commandHistory.length} commands from history`);
            } catch (error) {
                console.error('Error loading history:', error);
            }
        }
        
        function addToOutput(content, className = 'output-text') {
            const div = document.createElement('div');
            div.className = className;
            div.innerHTML = content;
            outputDiv.appendChild(div);
            outputDiv.scrollTop = outputDiv.scrollHeight;
        }
        
        function addCommandToOutput(command) {
            const div = document.createElement('div');
            div.className = 'command-line';
            div.innerHTML = `<span class="prompt">PS></span> <span class="command-text">${command}</span>`;
            outputDiv.appendChild(div);
        }
        
        async function executeCommand() {
            const command = commandInput.value.trim();
            if (!command) return;
            
            // Add command to local history (it's also saved server-side)
            if (commandHistory[commandHistory.length - 1] !== command) {
                commandHistory.push(command);
            }
            historyIndex = -1;
            
            // Show command in output
            addCommandToOutput(command);
            
            // Clear input and disable button
            commandInput.value = '';
            executeBtn.disabled = true;
            executeBtn.textContent = 'Executing...';
            
            // Show loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            loadingDiv.textContent = 'Executing command...';
            outputDiv.appendChild(loadingDiv);
            outputDiv.scrollTop = outputDiv.scrollHeight;
            
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ command: command })
                });
                
                const result = await response.json();
                
                // Remove loading indicator
                outputDiv.removeChild(loadingDiv);
                
                // Add output
                if (result.output) {
                    const className = result.error ? 'error-text' : 'output-text';
                    addToOutput(result.output, className);
                }
                
            } catch (error) {
                // Remove loading indicator
                outputDiv.removeChild(loadingDiv);
                addToOutput(`Error: ${error.message}`, 'error-text');
            } finally {
                // Re-enable button
                executeBtn.disabled = false;
                executeBtn.textContent = 'Execute';
                commandInput.focus();
            }
        }
        
        // Event listeners
        executeBtn.addEventListener('click', executeCommand);
        reloadProfileBtn.addEventListener('click', reloadProfile);
        
        commandInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                executeCommand();
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    commandInput.value = commandHistory[commandHistory.length - 1 - historyIndex];
                }
            } else if (event.key === 'ArrowDown') {
                event.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    commandInput.value = commandHistory[commandHistory.length - 1 - historyIndex];
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    commandInput.value = '';
                }
            }
        });
        
        // Load history and profile status when page loads
        Promise.all([loadHistory(), loadProfileStatus()]).then(() => {
            // Focus input after everything is loaded
            commandInput.focus();
        });
        
        // Clear command
        commandInput.addEventListener('keydown', function(event) {
            if (event.ctrlKey && event.key === 'l') {
                event.preventDefault();
                outputDiv.innerHTML = `
                    <div class="output-text">Terminal cleared</div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #333;"></div>
                `;
            }
        });
    </script>
</body>
</html>
'''

# Create templates directory and file
import os
if not os.path.exists('templates'):
    os.makedirs('templates')

with open('templates/terminal.html', 'w', encoding='utf-8') as f:
    f.write(terminal_html)

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