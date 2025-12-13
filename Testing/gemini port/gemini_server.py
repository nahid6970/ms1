from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import time
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

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
    
    for line in lines:
        # Skip startup profiler and debug lines
        if any(skip in line for skip in ['[STARTUP]', 'Loaded cached', 'Recording metric', 'StartupProfiler']):
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
    
    return '\n'.join(response_text).strip(), tokens_info

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
            # Try different CLI command formats
            # For npm @google/gemini-cli
            commands = [
                ['gemini', message],  # npm global install
                ['npx', '@google/gemini-cli', message],  # npx version
                ['node_modules/.bin/gemini', message],  # local install
                ['gemini', 'chat', message],  # alternative format
                ['gemini-cli', '--prompt', message],  # Python version
                ['python', '-m', 'gemini', message],  # Python module
            ]
            
            result = None
            error_messages = []
            
            for cmd in commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        shell=True  # Enable shell for Windows compatibility
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        break
                    else:
                        error_messages.append(f"{' '.join(cmd)}: {result.stderr[:100]}")
                except FileNotFoundError as e:
                    error_messages.append(f"{' '.join(cmd)}: Not found")
                    continue
                except Exception as e:
                    error_messages.append(f"{' '.join(cmd)}: {str(e)[:100]}")
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

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Test if Gemini CLI is available"""
    try:
        # Try npm version first
        commands = [
            ['gemini', '--version'],
            ['gemini', '--help'],
            ['npx', '@google/gemini-cli', '--version'],
        ]
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                
                if result.returncode == 0:
                    version_info = result.stdout.strip() or result.stderr.strip()
                    return jsonify({
                        'status': 'success',
                        'message': 'Gemini CLI is available',
                        'version': version_info[:200] if version_info else 'Version info not available',
                        'command': ' '.join(cmd)
                    })
            except:
                continue
        
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
