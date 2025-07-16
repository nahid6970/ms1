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
    
    def find_explicit_filename(self, language: str, context: str) -> str | None:
        """
        Look for 'something.extension' in the context where
        extension matches the language we are about to save.
        Returns the exact filename if found, else None.
        """
        ext = self.get_file_extension(language)          # '.css', '.py', …
        if ext == '.txt':
            return None                                  # unknown extensions ignored

        # 1) Whole-word file name:  style.css, main.py, etc.
        pattern = rf'\b([\w-]+{re.escape(ext)})\b'
        match = re.search(pattern, context, re.IGNORECASE)
        if match:
            return match.group(1)

        # 2) Full path:  /css/style.css  -> style.css
        pattern_path = rf'[/\\]([\w-]+{re.escape(ext)})(?:\s|$)'
        match = re.search(pattern_path, context, re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def generate_filename(self, code, language, context=""):
        """Generate a meaningful filename based on code content and context"""
        explicit = self.find_explicit_filename(language, context)
        if explicit:
            return explicit.rsplit('.', 1)[0]  # strip extension; rest of code adds it again
        
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
                clean_title = title.lower().replace(' ', '_')
                if clean_title and clean_title != 'document':
                    filename_hints.append(clean_title)
            
            # Look for main page identifiers
            if 'hero' in code.lower():
                filename_hints.append('landing')
            elif 'about' in code.lower():
                filename_hints.append('about')
            elif 'contact' in code.lower():
                filename_hints.append('contact')
        
        elif language in ['css', 'scss', 'sass']:
            # Look for main selectors or components
            body_match = re.search(r'body\s*{', code)
            header_match = re.search(r'header\s*{', code)
            nav_match = re.search(r'nav\s*{', code)
            hero_match = re.search(r'\.hero', code)
            
            if hero_match:
                filename_hints.append('styles')
            elif body_match or header_match:
                filename_hints.append('main')
            elif nav_match:
                filename_hints.append('navigation')
        
        # Enhanced context extraction
        if context:
            # Look for specific project-related keywords
            project_keywords = ['website', 'portfolio', 'landing', 'dashboard', 'blog', 'shop', 'store', 'app', 'game', 'calculator', 'todo', 'form', 'login', 'profile', 'admin', 'home', 'about', 'contact', 'gallery', 'menu', 'navbar', 'footer', 'header', 'main', 'index']
            
            context_lower = context.lower()
            for keyword in project_keywords:
                if keyword in context_lower:
                    filename_hints.append(keyword)
                    break
            
            # Look for action words that might indicate file purpose
            action_words = ['create', 'build', 'make', 'design', 'develop']
            for action in action_words:
                if action in context_lower:
                    # Look for what comes after the action word
                    pattern = fr'{action}\s+(?:a\s+)?(\w+)'
                    match = re.search(pattern, context_lower)
                    if match and match.group(1) not in ['basic', 'simple', 'website', 'page']:
                        filename_hints.append(match.group(1))
        
        # Generate filename with priority to code content over context
        if filename_hints:
            # Remove duplicates while preserving order
            unique_hints = []
            for hint in filename_hints:
                if hint not in unique_hints:
                    unique_hints.append(hint)
            
            base_name = '_'.join(unique_hints[:2])  # Use max 2 parts for cleaner names
            base_name = re.sub(r'[^\w\s-]', '', base_name)  # Remove special chars
            base_name = re.sub(r'\s+', '_', base_name)  # Replace spaces with underscores
        else:
            # Fallback to standard names based on language
            standard_names = {
                'html': 'index',
                'css': 'styles',
                'js': 'script',
                'javascript': 'script',
                'python': 'main',
                'java': 'Main',
                'c': 'main',
                'cpp': 'main'
            }
            base_name = standard_names.get(language, language)
        
        # Ensure filename is not too long
        if len(base_name) > 25:
            base_name = base_name[:25]
        
        return base_name
    
    def get_file_extension(self, language):
        """Get file extension for a given language"""
        return self.language_extensions.get(language.lower(), '.txt')
    
    def save_code_blocks(self, text, context=""):
        """Extract and save code blocks from text"""
        code_blocks = self.extract_code_blocks(text)
        
        if not code_blocks:
            return []
        
        save_dir = r'C:\Users\nahid\ollama_code_gen'
        os.makedirs(save_dir, exist_ok=True)

        
        saved_files = []
        
        # Group blocks by language to handle naming better
        language_groups = {}
        for block in code_blocks:
            lang = block['language']
            if lang not in language_groups:
                language_groups[lang] = []
            language_groups[lang].append(block)
        
        for language, blocks in language_groups.items():
            for i, block in enumerate(blocks):
                code = block['code']
                
                # Generate filename
                base_name = self.generate_filename(code, language, context)
                extension = self.get_file_extension(language)
                
                # Add number suffix only if multiple blocks of same language
                if len(blocks) > 1:
                    filename = f"{base_name}_{i+1}{extension}"
                else:
                    filename = f"{base_name}{extension}"
                
                # Ensure filename is unique (in case of conflicts)
                file_path = os.path.join(save_dir, filename)
                counter = 1
                while os.path.exists(file_path):
                    name_without_ext = filename.rsplit('.', 1)[0]
                    ext = '.' + filename.rsplit('.', 1)[1] if '.' in filename else ''
                    filename = f"{name_without_ext}_v{counter}{ext}"
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