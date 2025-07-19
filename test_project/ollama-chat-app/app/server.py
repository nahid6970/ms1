# server.py  (complete, ready to use)
import os
import http.server
import socketserver
import requests
import json
import datetime
import re
import hashlib
from rag_system import NomicRAGSystem

PORT = 8000
OLLAMA_HOST = "http://localhost:11434"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 1. Load the instruction file once at startup and initialize RAG
# ---------------------------------------------------------------------------
INSTRUCTION_FILE = os.path.join(os.path.dirname(__file__), "instruction.txt")
SYSTEM_MESSAGE = ""
if os.path.isfile(INSTRUCTION_FILE):
    with open(INSTRUCTION_FILE, encoding="utf-8") as f:
        SYSTEM_MESSAGE = f.read().strip()
else:
    print("Warning: instruction.txt not found; no system prompt injected.")

# Initialize RAG system
try:
    rag_system = NomicRAGSystem()
    print("RAG system initialized successfully")
except Exception as e:
    print(f"Warning: Could not initialize RAG system: {e}")
    rag_system = None

# ---------------------------------------------------------------------------
# 2. CodeExtractor with filename-from-first-line support
# ---------------------------------------------------------------------------
class CodeExtractor:
    def __init__(self):
        self.language_extensions = {
            'python': '.py', 'javascript': '.js', 'js': '.js',
            'typescript': '.ts', 'ts': '.ts', 'java': '.java',
            'cpp': '.cpp', 'c++': '.cpp', 'c': '.c',
            'csharp': '.cs', 'c#': '.cs', 'php': '.php',
            'ruby': '.rb', 'go': '.go', 'rust': '.rs',
            'kotlin': '.kt', 'swift': '.swift', 'scala': '.scala',
            'html': '.html', 'css': '.css', 'scss': '.scss',
            'sass': '.sass', 'sql': '.sql', 'bash': '.sh',
            'shell': '.sh', 'powershell': '.ps1', 'r': '.r',
            'matlab': '.m', 'perl': '.pl', 'lua': '.lua',
            'dart': '.dart', 'json': '.json', 'xml': '.xml',
            'yaml': '.yaml', 'yml': '.yml', 'dockerfile': '.dockerfile',
            'makefile': '.makefile', 'markdown': '.md', 'md': '.md',
            'text': '.txt', 'txt': '.txt'
        }

    def extract_code_blocks(self, text):
        """Extract markdown ```lang ... ``` blocks."""
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        blocks = []
        for lang, code in matches:
            if code.strip():
                blocks.append({
                    'language': lang.lower() if lang else 'text',
                    'code': code.strip()
                })
        return blocks

    # -----------------------------------------------------------------------
    # 2a. Read filename directive from first line
    # -----------------------------------------------------------------------
    # filename: fixed_extractor.py

    def extract_filename_from_code(self, code: str, language: str) -> str | None:
        lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
        if not lines:
            return None
        first = lines[0]

        comment_styles = {
            'python': ('#',), 'py': ('#',),
            'javascript': ('//', '/*'), 'js': ('//', '/*'),
            'typescript': ('//', '/*'), 'ts': ('//', '/*'),
            'java': ('//', '/*'), 'cpp': ('//', '/*'), 'c': ('//', '/*'),
            'css': ('/*',), 'html': ('<!--',), 'php': ('//', '#', '/*'),
            'ruby': ('#',), 'go': ('//', '/*'), 'rust': ('//', '/*'),
            'swift': ('//', '/*'), 'kotlin': ('//', '/*'), 'scala': ('//', '/*'),
            'shell': ('#',), 'bash': ('#',), 'sql': ('--',),
            'yaml': ('#',), 'yml': ('#',), 'json': ('//',),
            'dockerfile': ('#',), 'makefile': ('#',), 'markdown': ('<!--',),
            'md': ('<!--',), 'text': ('#',), 'txt': ('#',)
        }
        
        prefixes = comment_styles.get(language.lower(), ('#',))
        
        for prefix in prefixes:
            if first.startswith(prefix):
                # Extract the content between the comment markers
                directive = first[len(prefix):].strip()
                
                # Handle different comment closing styles
                if prefix == '<!--' and directive.endswith('-->'):
                    directive = directive[:-3].strip()
                elif prefix == '/*' and directive.endswith('*/'):
                    directive = directive[:-2].strip()
                
                # Look for filename directive
                m = re.fullmatch(r'filename:\s*([^\s]+)', directive, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
        
        return None

    # -----------------------------------------------------------------------
    # 2b. Generate filename (directive wins, then context, then heuristic)
    # -----------------------------------------------------------------------
    def generate_filename(self, code, language, context="") -> str:
        # Priority 1: directive inside code
        direct = self.extract_filename_from_code(code, language)
        if direct and self.is_valid_filename(direct):
            return direct.rsplit('.', 1)[0]

        # Priority 2: explicit filename in context
        ctx = self.find_filename_in_context(language, context)
        if ctx:
            return ctx.rsplit('.', 1)[0]

        # Priority 3: heuristic
        hints = []
        if language in {'python', 'py'}:
            m = re.search(r'class\s+(\w+)', code) or re.search(r'def\s+(\w+)', code)
            if m:
                hints.append(m.group(1).lower())
        elif language in {'javascript', 'js', 'typescript', 'ts'}:
            m = (re.search(r'function\s+(\w+)', code) or
                 re.search(r'class\s+(\w+)', code) or
                 re.search(r'const\s+(\w+)', code))
            if m:
                hints.append(m.group(1).lower())
        elif language in {'java', 'csharp', 'c#'}:
            m = re.search(r'(?:public\s+)?class\s+(\w+)', code)
            if m:
                hints.append(m.group(1).lower())
        elif language == 'html':
            m = re.search(r'<title>(.*?)</title>', code, re.I)
            if m:
                title = re.sub(r'[^\w\s-]', '', m.group(1).strip()).lower().replace(' ', '_')
                if title and title != 'document':
                    hints.append(title)
        elif language in {'css', 'scss', 'sass'}:
            if re.search(r'\.hero', code):
                hints.append('style')
            elif re.search(r'body\s*{', code):
                hints.append('main')

        if context:
            for kw in ['website', 'portfolio', 'landing', 'dashboard', 'blog', 'shop', 'app', 'game',
                       'calculator', 'todo', 'form', 'login', 'profile', 'admin', 'home', 'about',
                       'contact', 'gallery', 'menu', 'navbar', 'footer', 'header', 'main', 'index']:
                if kw in context.lower():
                    hints.append(kw)
                    break

        if hints:
            base = '_'.join(dict.fromkeys(hints))[:25]
            base = re.sub(r'[^\w-]', '_', base)
            return base

        # Fallback
        std = {'html': 'index', 
                'css': 'style', 
                'js': 'script', 
                'python': 'main',
                'java': 'Main',
                'c': 'main',
                'cpp': 'main'}
        return std.get(language, language)

    def is_valid_filename(self, name: str) -> bool:
        if not name or len(name) < 3:
            return False
        base = name.split('.')[0].lower()
        return base not in {'file', 'code', 'test', 'temp', 'example', 'sample'}

    def find_filename_in_context(self, language: str, context: str) -> str | None:
        if not context:
            return None
        ext = self.get_file_extension(language)
        patterns = [
            rf'\b(\w+(?:[-_]\w+)*{re.escape(ext)})\b',
            rf'["\'](\w+(?:[-_]\w+)*{re.escape(ext)})["\']',
            rf'(?:file|create|save|name|call|as)\s+["\']?(\w+(?:[-_]\w+)*{re.escape(ext)})["\']?'
        ]
        for p in patterns:
            m = re.search(p, context, re.I)
            if m:
                return m.group(1)
        return None

    def get_file_extension(self, language):
        return self.language_extensions.get(language.lower(), '.txt')

    def save_code_blocks(self, text, context=""):
        blocks = self.extract_code_blocks(text)
        if not blocks:
            return []
        save_dir = os.path.expanduser('~/desktop/ollama_code_gen')
        os.makedirs(save_dir, exist_ok=True)
        saved = []
        for block in blocks:
            base = self.generate_filename(block['code'], block['language'], context)
            ext = self.get_file_extension(block['language'])
            filename = f"{base}{ext}"
            path = os.path.join(save_dir, filename)
            counter = 1
            while os.path.exists(path):
                filename = f"{base}_v{counter}{ext}"
                path = os.path.join(save_dir, filename)
                counter += 1
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(block['code'])
                saved.append({'filename': filename, 'path': path,
                              'language': block['language'], 'size': len(block['code'])})
                print(f"Saved {block['language']} code to {path}")
            except Exception as e:
                print(f"Error saving {filename}: {e}")
        return saved

# ---------------------------------------------------------------------------
# 3. HTTP proxy that prepends the system prompt to every chat request
# ---------------------------------------------------------------------------
class OllamaProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.code_extractor = CodeExtractor()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/rag"):
            self._handle_rag_request()
        elif self.path.startswith("/api"):
            self._proxy_request()
        elif self.path == "/":
            self.path = "index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/rag"):
            self._handle_rag_request()
        elif self.path.startswith("/api"):
            self._proxy_request()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def _handle_rag_request(self):
        """Handle RAG-specific API requests"""
        if not rag_system:
            self.send_error(503, "RAG system not available")
            return
        
        try:
            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                if self.path == '/api/rag/add_document':
                    content = data.get('content', '')
                    metadata = data.get('metadata', {})
                    chunk_ids = rag_system.add_document(content, metadata)
                    response = {'success': True, 'chunk_ids': chunk_ids}
                
                elif self.path == '/api/rag/add_file':
                    file_path = data.get('file_path', '')
                    metadata = data.get('metadata', {})
                    chunk_ids = rag_system.add_file(file_path, metadata)
                    response = {'success': True, 'chunk_ids': chunk_ids}
                
                elif self.path == '/api/rag/search':
                    query = data.get('query', '')
                    n_results = data.get('n_results', 5)
                    results = rag_system.search(query, n_results)
                    response = {'success': True, 'results': results}
                
                elif self.path == '/api/rag/clear':
                    rag_system.clear_collection()
                    response = {'success': True, 'message': 'Collection cleared'}
                
                else:
                    self.send_error(404, "RAG endpoint not found")
                    return
            
            elif self.command == 'GET':
                if self.path == '/api/rag/documents':
                    documents = rag_system.list_documents()
                    response = {'success': True, 'documents': documents}
                else:
                    self.send_error(404, "RAG endpoint not found")
                    return
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"RAG Error: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode('utf-8'))

    def _proxy_request(self):
        try:
            api_url = f"{OLLAMA_HOST}{self.path}"
            headers = {h: self.headers[h] for h in self.headers}

            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)

                # ---- inject system message, RAG context, and handle options ----
                if self.path in ('/api/chat', '/api/generate'):
                    try:
                        payload = json.loads(post_data.decode('utf-8'))
                        
                        # Extract user-defined options from the request
                        user_options = payload.pop('options', {})
                        
                        # Get user query for RAG
                        user_query = ""
                        if 'messages' in payload and payload['messages']:
                            # Get the last user message
                            for msg in reversed(payload['messages']):
                                if msg.get('role') == 'user':
                                    user_query = msg.get('content', '')
                                    break
                        elif 'prompt' in payload:
                            user_query = payload['prompt']
                        
                        # Get RAG context if available and query is meaningful
                        rag_context = ""
                        if rag_system and user_query and len(user_query.strip()) > 10:
                            try:
                                rag_context = rag_system.get_context(user_query, n_results=3, max_context_length=1500)
                                if rag_context:
                                    print(f"RAG context retrieved for query: {user_query[:50]}...")
                            except Exception as e:
                                print(f"RAG context retrieval failed: {e}")
                        
                        # Build enhanced system message
                        enhanced_system_message = SYSTEM_MESSAGE
                        if rag_context:
                            enhanced_system_message += f"\n\n# RELEVANT CONTEXT:\n{rag_context}\n\nUse the above context to provide more accurate and informed responses when relevant to the user's query."

                        # Inject enhanced system message
                        if enhanced_system_message:
                            if 'messages' in payload:      # /api/chat
                                if not payload.get('messages') or payload['messages'][0].get('role') != 'system':
                                    payload['messages'].insert(0, {'role': 'system', 'content': enhanced_system_message})
                                else:
                                    payload['messages'][0]['content'] = f"{enhanced_system_message}\n\n{payload['messages'][0]['content']}"
                            elif 'prompt' in payload:      # /api/generate
                                payload['system'] = enhanced_system_message
                        
                        # Add the options back into the payload for Ollama
                        if user_options:
                            payload['options'] = user_options

                        post_data = json.dumps(payload).encode('utf-8')
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Could not process payload for {self.path}: {e}. Proxying original request.")
                # -------------------------------------------------

                response = requests.post(api_url, data=post_data, headers=headers, stream=True)
            else:
                response = requests.get(api_url, headers=headers, stream=True)

            self.send_response(response.status_code)
            for k, v in response.headers.items():
                if k.lower() not in {'transfer-encoding', 'content-encoding'}:
                    self.send_header(k, v)
            self.end_headers()

            full = b''
            for chunk in response.iter_content(8192):
                self.wfile.write(chunk)
                full += chunk

            if self.command == 'POST' and (self.path == '/api/chat' or self.path == '/api/generate'):
                try:
                    text = ""
                    for line in full.decode('utf-8', errors='ignore').splitlines():
                        try:
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                text += data['message']['content']
                            elif 'response' in data:
                                text += data['response']
                            if data.get('done') and text.strip():
                                self.code_extractor.save_code_blocks(text)
                                text = ""
                        except json.JSONDecodeError:
                            continue
                except Exception as e:
                    print("Error processing response:", e)

        except Exception as e:
            self.send_error(500, f"Proxy Error: {e}")

# ---------------------------------------------------------------------------
# 4. Serve forever
# ---------------------------------------------------------------------------
code_dir = os.path.expanduser('~/desktop/ollama_code_gen')
os.makedirs(code_dir, exist_ok=True)

with socketserver.TCPServer(("", PORT), OllamaProxyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Generated code will be saved to: {code_dir}")
    httpd.serve_forever()