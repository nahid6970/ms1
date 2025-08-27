from flask import Flask, render_template, request, jsonify
import subprocess
import json
import os
import threading
import time

app = Flask(__name__)

# Store active PowerShell processes - with persistent working directory
class PowerShellSession:
    def __init__(self):
        self.current_directory = os.path.expanduser('~')  # Start in home directory
    
    def execute_command(self, command):
        """Execute a command in PowerShell with persistent directory"""
        try:
            # Handle cd commands specially to maintain directory state
            if command.strip().lower().startswith('cd ') or command.strip().lower() == 'cd':
                return self._handle_cd_command(command.strip())
            
            # For other commands, run in the current directory
            result = subprocess.run(
                ['powershell', '-Command', command],
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
            full_output.append(f"Location: {self.current_directory}")
            
            final_output = '\n'.join(full_output) if full_output else 'Command completed successfully'
            has_error = bool(result.returncode != 0 or errors)
            
            return final_output, has_error
            
        except subprocess.TimeoutExpired:
            return "Command timed out (30 seconds)", True
        except Exception as e:
            return f"Error executing command: {str(e)}", True
    
    def _handle_cd_command(self, command):
        """Handle cd command to maintain directory state"""
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
            gap: 10px;
        }
        
        .header h1 {
            font-size: 18px;
            font-weight: normal;
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
        <h1>🔷 PowerShell Web Terminal</h1>
        <span style="font-size: 12px; opacity: 0.8;">Local Session - Port 5555</span>
    </div>
    
    <div class="terminal-container">
        <div id="terminal-output" class="terminal-output">
            <div class="output-text">PowerShell Web Terminal Ready</div>
            <div class="output-text">Type your PowerShell commands below...</div>
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
        
        let commandHistory = [];
        let historyIndex = -1;
        
        function addToOutput(content, className = 'output-text') {
            const div = document.createElement('div');
            div.className = className;
            div.textContent = content;
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
            
            // Add command to history
            commandHistory.unshift(command);
            if (commandHistory.length > 100) {
                commandHistory = commandHistory.slice(0, 100);
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
        
        commandInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                executeCommand();
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                if (historyIndex < commandHistory.length - 1) {
                    historyIndex++;
                    commandInput.value = commandHistory[historyIndex];
                }
            } else if (event.key === 'ArrowDown') {
                event.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    commandInput.value = commandHistory[historyIndex];
                } else if (historyIndex === 0) {
                    historyIndex = -1;
                    commandInput.value = '';
                }
            }
        });
        
        // Focus input on page load
        commandInput.focus();
        
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
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=5555, debug=True)