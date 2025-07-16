import os
import http.server
import socketserver
import requests
import json
import datetime
import re
import hashlib

PORT = 8000
OLLAMA_HOST = "http://localhost:11434"

os.chdir(os.path.dirname(os.path.abspath(__file__)))


class CodeExtractor:
    def __init__(self):
        self.language_extensions = {
            'python': '.py',
            'javascript': '.js',
            'js': '.js',
            'typescript': '.ts',
            'ts': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c++': '.cpp',
            'c': '.c',
            'csharp': '.cs',
            'c#': '.cs',
            'php': '.php',
            'ruby': '.rb',
            'go': '.go',
            'rust': '.rs',
            'kotlin': '.kt',
            'swift': '.swift',
            'scala': '.scala',
            'html': '.html',
            'css': '.css',
            'scss': '.scss',
            'sass': '.sass',
            'sql': '.sql',
            'bash': '.sh',
            'shell': '.sh',
            'powershell': '.ps1',
            'r': '.r',
            'matlab': '.m',
            'perl': '.pl',
            'lua': '.lua',
            'dart': '.dart',
            'json': '.json',
            'xml': '.xml',
            'yaml': '.yaml',
            'yml': '.yml',
            'dockerfile': '.dockerfile',
            'makefile': '.makefile',
            'markdown': '.md',
            'md': '.md',
            'text': '.txt',
            'txt': '.txt'
        }
    
    def extract_code_blocks(self, text):
        """Extract code blocks from markdown-style text"""
        code_blocks = []
        
        # Pattern to match code blocks with optional language specification
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for language, code in matches:
            if code.strip():  # Only process non-empty code blocks
                code_blocks.append({
                    'language': language.lower() if language else 'text',
                    'code': code.strip()
                })
        
        return code_blocks
    
    def generate_filename(self, code, language, context=""):
        """Generate a meaningful filename based on code content and context"""
        # Try to extract meaningful names from code
        filename_hints = []
        
        # Language-specific filename extraction
        if language in ['python', 'py']:
            # Look for class names, function names, or script purpose
            class_match = re.search(r'class\s+(\w+)', code)
            function_match = re.search(r'def\s+(\w+)', code)
            if class_match:
                filename_hints.append(class_match.group(1).lower())
            elif function_match:
                filename_hints.append(function_match.group(1).lower())
        
        elif language in ['javascript', 'js', 'typescript', 'ts']:
            # Look for function names, class names, or variable names
            function_match = re.search(r'function\s+(\w+)', code)
            class_match = re.search(r'class\s+(\w+)', code)
            const_match = re.search(r'const\s+(\w+)', code)
            if function_match:
                filename_hints.append(function_match.group(1).lower())
            elif class_match:
                filename_hints.append(class_match.group(1).lower())
            elif const_match:
                filename_hints.append(const_match.group(1).lower())
        
        elif language in ['java', 'csharp', 'c#']:
            # Look for class names
            class_match = re.search(r'(?:public\s+)?class\s+(\w+)', code)
            if class_match:
                filename_hints.append(class_match.group(1).lower())
        
        elif language in ['html']:
            # Look for title or main content
            title_match = re.search(r'<title>(.*?)</title>', code, re.IGNORECASE)
            if title_match:
                title = re.sub(r'[^\w\s-]', '', title_match.group(1).strip())
                filename_hints.append(title.lower().replace(' ', '_'))
        
        elif language in ['css', 'scss', 'sass']:
            # Look for main selectors or components
            selector_match = re.search(r'\.([a-zA-Z][\w-]*)', code)
            if selector_match:
                filename_hints.append(selector_match.group(1).lower())
        
        # Extract context from the conversation or prompt
        if context:
            # Look for meaningful words in context
            context_words = re.findall(r'\b[a-zA-Z]{3,}\b', context.lower())
            # Filter out common words
            common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'had', 'but', 'words', 'use', 'each', 'which', 'their', 'time', 'will', 'about', 'write', 'would', 'there', 'into', 'could', 'state', 'only', 'new', 'year', 'some', 'take', 'come', 'these', 'know', 'see', 'him', 'two', 'how', 'its', 'who', 'did', 'yes', 'his', 'been', 'or', 'when', 'much', 'no', 'may', 'what', 'them', 'where', 'much', 'sign', 'the', 'every', 'does', 'got', 'united', 'left', 'try', 'good', 'this', 'right', 'move', 'way', 'she', 'they', 'not', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us'}
            meaningful_words = [word for word in context_words if word not in common_words and len(word) > 3]
            filename_hints.extend(meaningful_words[:2])  # Take first 2 meaningful words
        
        # Generate filename
        if filename_hints:
            base_name = '_'.join(filename_hints[:3])  # Use max 3 parts
            base_name = re.sub(r'[^\w\s-]', '', base_name)  # Remove special chars
            base_name = re.sub(r'\s+', '_', base_name)  # Replace spaces with underscores
        else:
            # Fallback to generic names based on language
            base_name = f"{language}_code" if language != 'text' else "code"
        
        # Ensure filename is not too long
        if len(base_name) > 30:
            base_name = base_name[:30]
        
        return base_name
    
    def get_file_extension(self, language):
        """Get file extension for a given language"""
        return self.language_extensions.get(language.lower(), '.txt')
    
    def save_code_blocks(self, text, context=""):
        """Extract and save code blocks from text"""
        code_blocks = self.extract_code_blocks(text)
        
        if not code_blocks:
            return []
        
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home', 'generated_code')
        os.makedirs(save_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []
        
        # If multiple blocks of same language, add counter
        language_counters = {}
        
        for i, block in enumerate(code_blocks):
            language = block['language']
            code = block['code']
            
            # Count occurrences of each language
            if language in language_counters:
                language_counters[language] += 1
            else:
                language_counters[language] = 1
            
            # Generate filename
            base_name = self.generate_filename(code, language, context)
            extension = self.get_file_extension(language)
            
            # Add counter if multiple files of same language
            if language_counters[language] > 1:
                filename = f"{base_name}_{language_counters[language]}_{timestamp}{extension}"
            else:
                filename = f"{base_name}_{timestamp}{extension}"
            
            # Ensure filename is unique
            file_path = os.path.join(save_dir, filename)
            counter = 1
            while os.path.exists(file_path):
                name_without_ext = filename.rsplit('.', 1)[0]
                ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
                filename = f"{name_without_ext}_v{counter}.{ext}" if ext else f"{name_without_ext}_v{counter}"
                file_path = os.path.join(save_dir, filename)
                counter += 1
            
            # Save the file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                
                saved_files.append({
                    'filename': filename,
                    'path': file_path,
                    'language': language,
                    'size': len(code)
                })
                
                print(f"Saved {language} code to {file_path}")
            
            except Exception as e:
                print(f"Error saving {filename}: {e}")
        
        return saved_files


class OllamaProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.code_extractor = CodeExtractor()
        self.conversation_context = ""
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path.startswith("/api"):
            self._proxy_request()
        elif self.path == "/":
            self.path = "index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api"):
            self._proxy_request()
        else:
            self.send_response(404)
            self.end_headers()

    def _proxy_request(self):
        try:
            api_url = f"{OLLAMA_HOST}{self.path}"
            headers = {h: self.headers[h] for h in self.headers}

            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Extract context from request for better filename generation
                try:
                    request_data = json.loads(post_data.decode('utf-8'))
                    if 'messages' in request_data:
                        # Get the last user message for context
                        user_messages = [msg['content'] for msg in request_data['messages'] if msg['role'] == 'user']
                        if user_messages:
                            self.conversation_context = user_messages[-1]
                except:
                    pass
                
                response = requests.post(api_url, data=post_data, headers=headers, stream=True)
            else:
                response = requests.get(api_url, headers=headers, stream=True)

            self.send_response(response.status_code)
            for key, value in response.headers.items():
                if key.lower() not in ('transfer-encoding', 'content-encoding'):
                    self.send_header(key, value)
            self.end_headers()

            full_response_content = b''
            for chunk in response.iter_content(chunk_size=8192):
                self.wfile.write(chunk)
                full_response_content += chunk

            if self.command == 'POST' and (self.path == '/api/chat' or self.path == '/api/generate'):
                try:
                    generated_text = ""
                    # Ollama's streaming response consists of multiple JSON objects, separated by newlines.
                    lines = full_response_content.decode('utf-8', errors='ignore').strip().split('\n')
                    
                    for line in lines:
                        try:
                            json_data = json.loads(line)
                            # For /api/chat
                            if 'message' in json_data and 'content' in json_data['message']:
                                generated_text += json_data['message']['content']
                            # For /api/generate
                            elif 'response' in json_data:
                                generated_text += json_data['response']

                            # When the stream is done, save the complete text
                            if json_data.get('done'):
                                if generated_text.strip():
                                    saved_files = self.code_extractor.save_code_blocks(
                                        generated_text, 
                                        self.conversation_context
                                    )
                                    
                                    if saved_files:
                                        print(f"Generated {len(saved_files)} file(s):")
                                        for file_info in saved_files:
                                            print(f"  - {file_info['filename']} ({file_info['language']}, {file_info['size']} chars)")
                                    else:
                                        print("No code blocks found in response")
                                
                                # Reset for the next potential message in the same connection
                                generated_text = ""
                        except json.JSONDecodeError:
                            # Ignore lines that are not valid JSON
                            continue
                except Exception as e:
                    print(f"Error processing and saving Ollama response: {e}")

        except Exception as e:
            self.send_error(500, f"Proxy Error: {e}")


# Create the generated_code directory if it doesn't exist
code_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home', 'generated_code')
os.makedirs(code_dir, exist_ok=True)

with socketserver.TCPServer(("", PORT), OllamaProxyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Generated code will be saved to: {code_dir}")
    httpd.serve_forever()