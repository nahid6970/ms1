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
        self.instructions_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'naming_instructions.txt')
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
        
        # Reverse mapping for extension to language
        self.extension_to_language = {}
        for lang, ext in self.language_extensions.items():
            if ext not in self.extension_to_language:
                self.extension_to_language[ext] = lang
    
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
    
    def load_naming_instructions(self):
        """Load and parse naming instructions from the text file"""
        if not os.path.exists(self.instructions_file):
            return []
        
        try:
            with open(self.instructions_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                return []
            
            instructions = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line and re.match(r'^\d+\.', line):
                    # Extract the instruction number and text
                    match = re.match(r'^(\d+)\.\s*(.*)', line)
                    if match:
                        instruction_num = int(match.group(1))
                        instruction_text = match.group(2).strip()
                        instructions.append({
                            'number': instruction_num,
                            'instruction': instruction_text
                        })
            
            # Sort by instruction number
            instructions.sort(key=lambda x: x['number'])
            print(f"Loaded {len(instructions)} naming instructions from {self.instructions_file}")
            return instructions
            
        except Exception as e:
            print(f"Error loading naming instructions: {e}")
            return []
    
    def apply_naming_instructions(self, code, language, context=""):
        """Apply the naming instructions from the text file"""
        instructions = self.load_naming_instructions()
        
        if not instructions:
            print("No naming instructions found, using default logic")
            return None
        
        print(f"Applying {len(instructions)} naming instructions...")
        
        # Variables that instructions can reference
        variables = {
            'code': code,
            'language': language,
            'context': context.lower() if context else "",
            'extension': self.get_file_extension(language)
        }
        
        filename = None
        
        for instruction in instructions:
            instruction_text = instruction['instruction'].lower()
            print(f"  Step {instruction['number']}: {instruction['instruction']}")
            
            try:
                # Instruction 1: Look for filename in code comments/top of script
                if instruction['number'] == 1 and 'filename' in instruction_text and ('top' in instruction_text or 'script' in instruction_text):
                    filename = self.extract_filename_from_code_top(code, language)
                    if filename:
                        print(f"    Found filename in code: {filename}")
                        break
                
                # Instruction 2: Look for filename in context
                elif instruction['number'] == 2 and 'context' in instruction_text:
                    filename = self.find_filename_in_context(language, context)
                    if filename:
                        print(f"    Found filename in context: {filename}")
                        break
                
                # Instruction 3: Look for specific patterns
                elif instruction['number'] == 3 and 'pattern' in instruction_text:
                    filename = self.extract_filename_from_patterns(code, language, context)
                    if filename:
                        print(f"    Found filename from patterns: {filename}")
                        break
                
                # Instruction 4: Use class/function names
                elif instruction['number'] == 4 and ('class' in instruction_text or 'function' in instruction_text):
                    filename = self.extract_filename_from_code_structure(code, language)
                    if filename:
                        print(f"    Found filename from code structure: {filename}")
                        break
                
                # Instruction 5: Use project context
                elif instruction['number'] == 5 and 'project' in instruction_text:
                    filename = self.extract_filename_from_project_context(context)
                    if filename:
                        print(f"    Found filename from project context: {filename}")
                        break
                
                # Custom instruction handling - look for specific keywords
                elif 'use' in instruction_text and 'default' in instruction_text:
                    filename = self.get_default_filename(language)
                    if filename:
                        print(f"    Using default filename: {filename}")
                        break
                
                # Custom instruction - look for specific naming patterns
                elif 'prefix' in instruction_text:
                    prefix_match = re.search(r'prefix\s+"([^"]+)"', instruction['instruction'])
                    if prefix_match:
                        prefix = prefix_match.group(1)
                        base_name = self.generate_filename(code, language, context)
                        filename = f"{prefix}_{base_name}"
                        print(f"    Applied prefix: {filename}")
                        break
                
                # Custom instruction - look for suffix
                elif 'suffix' in instruction_text:
                    suffix_match = re.search(r'suffix\s+"([^"]+)"', instruction['instruction'])
                    if suffix_match:
                        suffix = suffix_match.group(1)
                        base_name = self.generate_filename(code, language, context)
                        filename = f"{base_name}_{suffix}"
                        print(f"    Applied suffix: {filename}")
                        break
                
                # Add more custom instruction handlers as needed
                
            except Exception as e:
                print(f"    Error applying instruction {instruction['number']}: {e}")
                continue
        
        return filename
    
    def extract_filename_from_code_top(self, code, language):
        """Extract filename from comments at the top of the code"""
        lines = code.split('\n')[:10]  # Check first 10 lines
        
        comment_patterns = {
            'python': r'#\s*(?:filename|file):\s*([^\s]+)',
            'javascript': r'//\s*(?:filename|file):\s*([^\s]+)',
            'js': r'//\s*(?:filename|file):\s*([^\s]+)',
            'css': r'/\*\s*(?:filename|file):\s*([^\s]+)\s*\*/',
            'html': r'<!--\s*(?:filename|file):\s*([^\s]+)\s*-->',
            'java': r'//\s*(?:filename|file):\s*([^\s]+)',
            'cpp': r'//\s*(?:filename|file):\s*([^\s]+)',
            'c': r'//\s*(?:filename|file):\s*([^\s]+)',
        }
        
        pattern = comment_patterns.get(language, r'#\s*(?:filename|file):\s*([^\s]+)')
        
        for line in lines:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                filename = match.group(1).strip()
                if self.is_valid_filename(filename):
                    return filename.split('.')[0]  # Return without extension
        
        return None
    
    def extract_filename_from_patterns(self, code, language, context):
        """Extract filename from specific patterns in code or context"""
        # Look for common patterns like "Create X", "Build Y", "Make Z"
        patterns = [
            r'create\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?([a-zA-Z_][a-zA-Z0-9_]*)',
            r'build\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?([a-zA-Z_][a-zA-Z0-9_]*)',
            r'make\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?([a-zA-Z_][a-zA-Z0-9_]*)',
            r'save\s+(?:as\s+)?(?:file\s+)?(?:named\s+)?([a-zA-Z_][a-zA-Z0-9_]*)',
        ]
        
        search_text = f"{context} {code}".lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, search_text, re.IGNORECASE)
            if matches:
                filename = matches[0].strip()
                if self.is_valid_filename(filename + '.tmp'):
                    return filename
        
        return None
    
    def extract_filename_from_code_structure(self, code, language):
        """Extract filename from code structure (classes, functions, etc.)"""
        if language in ['python', 'py']:
            class_match = re.search(r'class\s+(\w+)', code)
            if class_match:
                return class_match.group(1).lower()
            
            function_match = re.search(r'def\s+(\w+)', code)
            if function_match and function_match.group(1) != '__init__':
                return function_match.group(1).lower()
        
        elif language in ['javascript', 'js', 'typescript', 'ts']:
            class_match = re.search(r'class\s+(\w+)', code)
            if class_match:
                return class_match.group(1).lower()
            
            function_match = re.search(r'function\s+(\w+)', code)
            if function_match:
                return function_match.group(1).lower()
        
        elif language in ['java', 'csharp', 'c#']:
            class_match = re.search(r'(?:public\s+)?class\s+(\w+)', code)
            if class_match:
                return class_match.group(1).lower()
        
        return None
    
    def extract_filename_from_project_context(self, context):
        """Extract filename from project context"""
        if not context:
            return None
        
        project_keywords = {
            'landing': 'landing',
            'portfolio': 'portfolio',
            'dashboard': 'dashboard',
            'login': 'login',
            'register': 'register',
            'profile': 'profile',
            'settings': 'settings',
            'admin': 'admin',
            'home': 'home',
            'about': 'about',
            'contact': 'contact',
            'gallery': 'gallery',
            'shop': 'shop',
            'store': 'store',
            'cart': 'cart',
            'checkout': 'checkout',
            'blog': 'blog',
            'news': 'news',
            'calculator': 'calculator',
            'todo': 'todo',
            'form': 'form',
            'navbar': 'navbar',
            'header': 'header',
            'footer': 'footer',
            'sidebar': 'sidebar',
            'menu': 'menu',
        }
        
        context_lower = context.lower()
        for keyword, filename in project_keywords.items():
            if keyword in context_lower:
                return filename
        
        return None
    
    def get_default_filename(self, language):
        """Get default filename for a language"""
        defaults = {
            'html': 'index',
            'css': 'styles',
            'js': 'script',
            'javascript': 'script',
            'python': 'main',
            'java': 'Main',
            'c': 'main',
            'cpp': 'main',
            'typescript': 'app',
            'ts': 'app',
        }
        
        return defaults.get(language, language)
        """Search for explicit filenames in the context that match the language"""
        if not context:
            return None
        
        # Get the expected extension for this language
        expected_extension = self.get_file_extension(language)
        
        # Create patterns to match filenames with the expected extension
        # This will match things like "style.css", "script.js", "main.py", etc.
        patterns = [
            # Direct filename mentions with extension
            rf'(\w+(?:[-_]\w+)*\{re.escape(expected_extension)})',
            # Filenames mentioned in quotes
            rf'["\'](\w+(?:[-_]\w+)*\{re.escape(expected_extension)})["\']',
            # Filenames mentioned with "file", "create", "save", etc.
            rf'(?:file|create|save|name|call|as)\s+["\']?(\w+(?:[-_]\w+)*\{re.escape(expected_extension)})["\']?',
            # Filenames mentioned with "named" or "called"
            rf'(?:named|called)\s+["\']?(\w+(?:[-_]\w+)*\{re.escape(expected_extension)})["\']?',
        ]
        
        context_lower = context.lower()
        
        for pattern in patterns:
            matches = re.findall(pattern, context_lower, re.IGNORECASE)
            if matches:
                # Return the first match, clean it up
                filename = matches[0].strip()
                if filename and self.is_valid_filename(filename):
                    return filename
        
        # Also check for alternative extensions that might map to the same language
        alt_extensions = self.get_alternative_extensions(language)
        for alt_ext in alt_extensions:
            for pattern in patterns:
                alt_pattern = pattern.replace(re.escape(expected_extension), re.escape(alt_ext))
                matches = re.findall(alt_pattern, context_lower, re.IGNORECASE)
                if matches:
                    filename = matches[0].strip()
                    if filename and self.is_valid_filename(filename):
                        return filename
        
        return None
    
    def get_alternative_extensions(self, language):
        """Get alternative extensions for a language"""
        alternatives = {
            'javascript': ['.js', '.mjs', '.cjs'],
            'js': ['.js', '.mjs', '.cjs'],
            'typescript': ['.ts', '.tsx'],
            'ts': ['.ts', '.tsx'],
            'python': ['.py', '.pyw'],
            'css': ['.css', '.scss', '.sass'],
            'html': ['.html', '.htm'],
            'java': ['.java'],
            'cpp': ['.cpp', '.cc', '.cxx'],
            'c++': ['.cpp', '.cc', '.cxx'],
            'c': ['.c', '.h'],
            'csharp': ['.cs'],
            'c#': ['.cs'],
        }
        
        return alternatives.get(language, [])
    
    def is_valid_filename(self, filename):
        """Check if the filename is valid (not too generic or problematic)"""
        if not filename or len(filename) < 3:
            return False
        
        # Avoid overly generic names
        generic_names = ['file', 'code', 'test', 'temp', 'example', 'sample']
        base_name = filename.split('.')[0].lower()
        
        return base_name not in generic_names
    
    def generate_filename(self, code, language, context=""):
        """Generate a meaningful filename based on code content and context"""
        # First, try to apply naming instructions from the text file
        instruction_filename = self.apply_naming_instructions(code, language, context)
        if instruction_filename:
            return instruction_filename
        
        # If no instructions or instructions didn't produce a filename, fall back to context detection
        context_filename = self.find_filename_in_context(language, context)
        if context_filename:
            print(f"Found explicit filename in context: {context_filename}")
            return context_filename.split('.')[0]  # Return without extension
        
        # If no explicit filename found, proceed with the original logic
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
        
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'home', 'generated_code')
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
                
                # Generate filename (now with context filename detection)
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