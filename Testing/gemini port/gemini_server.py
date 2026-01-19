from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import time
import re
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Set working directory for Gemini CLI
WORKING_DIR = r"C:\@delta\ms1\Testing\geminiTesting"
os.makedirs(WORKING_DIR, exist_ok=True)

# Load system prompt
SYSTEM_PROMPT_FILE = 'system_prompt.md'
SYSTEM_PROMPT = ""
if os.path.exists(SYSTEM_PROMPT_FILE):
    with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        SYSTEM_PROMPT = f.read().strip()

# Store session data
session_data = {
    'messages': [],
    'total_input_tokens': 0,
    'total_output_tokens': 0,
    'message_count': 0,
    'response_times': []
}

def estimate_tokens(text):
    """Rough token estimation (4 chars ≈ 1 token)"""
    return len(text) // 4

def parse_gemini_output(output):
    """Parse Gemini CLI output to extract response and token info"""
    lines = output.strip().split('\n')
    response_text = []
    tokens_info = {}
    skip_patterns = [
        '[STARTUP]', 'Loaded cached', 'Recording metric', 'StartupProfiler'
    ]
    
    for line in lines:
        # Skip only startup profiler and debug lines
        if any(skip in line for skip in skip_patterns):
            continue
        
        # Look for token usage patterns
        if 'token' in line.lower():
            # Try to extract numbers
            numbers = re.findall(r'\d+', line)
            if numbers:
                if 'input' in line.lower():
                    tokens_info['input'] = int(numbers[0])
                elif 'output' in line.lower():
                    tokens_info['output'] = int(numbers[0])
        else:
            # Add non-empty lines to response
            if line.strip():
                response_text.append(line.strip())
    
    # Clean up response
    cleaned = '\n'.join(response_text).strip()
    
    return cleaned, tokens_info

@app.route('/')
def index():
    return send_file('gemini-dashboard.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'gemini-pro')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        start_time = time.time()
        
        # Call Gemini CLI - adjust this command based on your CLI setup
        # Common formats:
        # gemini chat "your message"
        # gemini-cli --model gemini-pro --prompt "your message"
        # python -m gemini "your message"
        
        try:
            # Prepend system prompt to message (keep it short)
            full_message = message
            if SYSTEM_PROMPT:
                full_message = f"{SYSTEM_PROMPT} {message}"
            
            # Try different CLI command formats
            # For npm @google/gemini-cli with YOLO mode (auto-approve tools)
            # Using positional argument for one-shot mode (non-interactive by default)
            commands = [
                ['gemini', '--yolo', '--model', model, full_message],  # npm with auto-approve, one-shot
                ['gemini', '--approval-mode', 'yolo', '--model', model, full_message],  # explicit approval mode
                ['gemini', '--model', model, full_message],  # npm global install (fallback)
            ]
            
            result = None
            error_messages = []
            
            for cmd in commands:
                try:
                    # Create the command string properly for shell execution
                    # Last argument is always the message
                    base_args = cmd[:-1]
                    msg = cmd[-1]
                    # Escape quotes in the message
                    escaped_msg = msg.replace('"', '\\"')
                    cmd_str = ' '.join(base_args) + f' "{escaped_msg}"'
                    
                    # Use Popen for better control
                    process = subprocess.Popen(
                        cmd_str,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        text=True,
                        shell=True,
                        cwd=WORKING_DIR
                    )
                    
                    # Send empty input and close stdin immediately
                    try:
                        stdout, stderr = process.communicate(input='', timeout=30)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        stdout, stderr = process.communicate()
                        error_messages.append(f"{cmd_str[:50]}: Timeout")
                        continue
                    
                    if process.returncode == 0 and stdout.strip():
                        result = subprocess.CompletedProcess(
                            args=cmd_str,
                            returncode=process.returncode,
                            stdout=stdout,
                            stderr=stderr
                        )
                        break
                    else:
                        error_messages.append(f"{cmd_str[:50]}: {stderr[:100]}")
                except FileNotFoundError as e:
                    error_messages.append(f"{cmd_str[:50]}: Not found")
                    continue
                except Exception as e:
                    error_messages.append(f"{cmd_str[:50]}: {str(e)[:100]}")
                    continue
            
            if result is None or result.returncode != 0 or not result.stdout.strip():
                # If CLI not found, provide helpful error
                return jsonify({
                    'error': 'Gemini CLI not working',
                    'message': 'Tried multiple commands but none worked',
                    'attempts': error_messages,
                    'suggestion': 'Make sure: 1) npm install -g @google/gemini-cli is installed, 2) API key is configured'
                }), 500
            
            response_time = int((time.time() - start_time) * 1000)
            
            # Parse output
            response_text, tokens_info = parse_gemini_output(result.stdout)
            
            # Estimate tokens if not provided by CLI
            input_tokens = tokens_info.get('input', estimate_tokens(message))
            output_tokens = tokens_info.get('output', estimate_tokens(response_text))
            
            # Update session data
            session_data['messages'].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            session_data['messages'].append({
                'role': 'assistant',
                'content': response_text,
                'timestamp': datetime.now().isoformat()
            })
            session_data['total_input_tokens'] += input_tokens
            session_data['total_output_tokens'] += output_tokens
            session_data['message_count'] += 1
            session_data['response_times'].append(response_time)
            
            return jsonify({
                'response': response_text,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'response_time': response_time,
                'model': model
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Request timeout'}), 504
        except Exception as e:
            return jsonify({'error': f'CLI execution error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get current session statistics"""
    avg_response_time = 0
    if session_data['response_times']:
        avg_response_time = sum(session_data['response_times']) // len(session_data['response_times'])
    
    return jsonify({
        'total_input_tokens': session_data['total_input_tokens'],
        'total_output_tokens': session_data['total_output_tokens'],
        'session_tokens': session_data['total_input_tokens'] + session_data['total_output_tokens'],
        'message_count': session_data['message_count'],
        'avg_response_time': avg_response_time,
        'messages': session_data['messages'][-10:]  # Last 10 messages
    })

@app.route('/api/reset', methods=['POST'])
def reset_stats():
    """Reset session statistics"""
    session_data['messages'] = []
    session_data['total_input_tokens'] = 0
    session_data['total_output_tokens'] = 0
    session_data['message_count'] = 0
    session_data['response_times'] = []
    return jsonify({'status': 'success'})

@app.route('/api/quota', methods=['GET'])
def get_quota_stats():
    """Get Gemini API quota stats via CLI"""
    try:
        # Run gemini interactive mode and send /stats
        cmd = 'gemini'
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            cwd=WORKING_DIR
        )
        
        # Send /stats command and exit
        # We also send /model to verify connectivity if stats fails? No, just stats.
        stdout, stderr = process.communicate(input='/stats\n/exit\n', timeout=15)
        
        if process.returncode != 0:
             # Try with --yolo just in case it behaves differently, though unlikely for interactive
             pass

        # Parse the output to find the stats table
        # We look for "Model Usage" or "Reqs" or "Usage left"
        output = stdout + "\n" + stderr
        
        # Extract the relevant part (heuristically)
        # If we find the table headers
        if "Model Usage" in output:
            return jsonify({
                'status': 'success',
                'output': output,
                'raw': True
            })
            
        return jsonify({
            'status': 'success',
            'output': output,
            'message': 'Command ran but table not found',
            'raw': True
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout fetching stats'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update server settings"""
    global WORKING_DIR
    try:
        data = request.json
        new_working_dir = data.get('workingDir')
        
        if new_working_dir:
            # Update working directory
            WORKING_DIR = new_working_dir
            os.makedirs(WORKING_DIR, exist_ok=True)
            
        return jsonify({
            'status': 'success',
            'message': 'Settings updated',
            'workingDir': WORKING_DIR
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/system-prompt', methods=['GET'])
def get_system_prompt():
    """Get current system prompt"""
    try:
        if os.path.exists(SYSTEM_PROMPT_FILE):
            with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({
                'status': 'success',
                'prompt': content,
                'file': SYSTEM_PROMPT_FILE
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'System prompt file not found'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/system-prompt', methods=['POST'])
def update_system_prompt():
    """Update system prompt"""
    global SYSTEM_PROMPT
    try:
        data = request.json
        new_prompt = data.get('prompt', '')
        
        # Save to file
        with open(SYSTEM_PROMPT_FILE, 'w', encoding='utf-8') as f:
            f.write(new_prompt)
        
        # Update in memory
        SYSTEM_PROMPT = new_prompt.strip()
        
        return jsonify({
            'status': 'success',
            'message': 'System prompt updated'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Test if Gemini CLI is available"""
    try:
        # Test with a simple echo command that should work
        cmd = ['gemini', '--yolo', 'say "test"']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
                cwd=WORKING_DIR
            )
            
            if result.returncode == 0:
                return jsonify({
                    'status': 'success',
                    'message': 'Gemini CLI is connected and working',
                    'version': 'YOLO mode enabled'
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': f'Gemini CLI error: {result.stderr[:200]}'
                }), 500
        except subprocess.TimeoutExpired:
            return jsonify({
                'status': 'error',
                'message': 'Connection test timed out'
            }), 504
        except FileNotFoundError:
            return jsonify({
                'status': 'error',
                'message': 'Gemini CLI not found. Install with: npm install -g @google/gemini-cli'
            }), 404
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Gemini CLI Dashboard Server...")
    print("📊 Dashboard available at: http://localhost:4785")
    print("💡 Make sure Gemini CLI is installed and configured")
    print("\nPress Ctrl+C to stop the server\n")
    app.run(debug=True, port=4785)
