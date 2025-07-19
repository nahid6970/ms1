# server.py  (complete, ready to use)
import os
import http.server
import socketserver
import requests
import json
import datetime
import re
import hashlib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# In-memory vector store
class VectorStore:
    def __init__(self):
        self.documents = []  # Stores {'text': '...', 'embedding': [...]}

    def add_document(self, text, embedding):
        self.documents.append({'text': text, 'embedding': embedding})

    def find_similar_documents(self, query_embedding, k=3):
        if not self.documents:
            return []
        
        similarities = []
        for doc in self.documents:
            # Ensure both are numpy arrays for cosine_similarity
            doc_embedding = np.array(doc['embedding']).reshape(1, -1)
            q_embedding = np.array(query_embedding).reshape(1, -1)
            
            sim = cosine_similarity(doc_embedding, q_embedding)[0][0]
            similarities.append((sim, doc['text']))
        
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [text for sim, text in similarities[:k]]

PORT = 8000
OLLAMA_HOST = "http://localhost:11434"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 1. Load the instruction file once at startup
# ---------------------------------------------------------------------------
INSTRUCTION_FILE = os.path.join(os.path.dirname(__file__), "instruction.txt")
SYSTEM_MESSAGE = ""
if os.path.isfile(INSTRUCTION_FILE):
    with open(INSTRUCTION_FILE, encoding="utf-8") as f:
        SYSTEM_MESSAGE = f.read().strip()
else:
    print("Warning: instruction.txt not found; no system prompt injected.")

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
        self.vector_store = VectorStore() # Initialize the vector store
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
        if self.path.startswith("/api/embed"):
            self._handle_embed_request()
        elif self.path.startswith("/api/rag_load"):
            self._handle_rag_load_documents()
        elif self.path.startswith("/api/rag_chat"):
            self._handle_rag_chat_request()
        elif self.path.startswith("/api"):
            self._proxy_request()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_embed_request(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))

            model_name = payload.get('model', 'nomic-embed-text') # Default to nomic-embed-text
            prompt = payload.get('prompt')

            if not prompt:
                self.send_error(400, "Bad Request: 'prompt' is required.")
                return

            ollama_embed_url = f"{OLLAMA_HOST}/api/embeddings"
            embed_payload = {"model": model_name, "prompt": prompt}
            
            embed_response = requests.post(ollama_embed_url, json=embed_payload)
            embed_response.raise_for_status()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(embed_response.content)

        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON.")
        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Ollama Embedding Error: {e}")
        except Exception as e:
            self.send_error(500, f"Server Error: {e}")

    def _handle_rag_load_documents(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            directory = payload.get('directory')

            if not directory:
                self.send_error(400, "Bad Request: 'directory' is required.")
                return

            if not os.path.isdir(directory):
                self.send_error(400, f"Bad Request: Directory {directory} not found.")
                return

            self.vector_store = VectorStore() # Clear existing documents
            loaded_count = 0
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.txt', '.md')):
                        file_path = os.path.join(root, file)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            chunks = self._chunk_text(content) # Simple chunking for now
                            for chunk in chunks:
                                embedding = self._get_embedding(chunk)
                                if embedding:
                                    self.vector_store.add_document(chunk, embedding)
                                    loaded_count += 1
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'success', 'loaded_documents': loaded_count}).encode('utf-8'))

        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON.")
        except Exception as e:
            self.send_error(500, f"Server Error: {e}")

    def _handle_rag_chat_request(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))

            user_query = payload.get('query')
            chat_history = payload.get('history', [])
            model = payload.get('model')
            options = payload.get('options', {})

            if not user_query:
                self.send_error(400, "Bad Request: 'query' is required.")
                return
            
            query_embedding = self._get_embedding(user_query)
            if not query_embedding:
                self.send_error(500, "Failed to generate embedding for query.")
                return

            relevant_docs = self.vector_store.find_similar_documents(query_embedding)
            context = "\n\n".join(relevant_docs)

            # Augment the user query with retrieved context
            augmented_query = f"Based on the following information:\n\n{context}\n\nAnswer the question: {user_query}"

            # Prepare messages for Ollama chat API
            messages = []
            if SYSTEM_MESSAGE:
                messages.append({'role': 'system', 'content': SYSTEM_MESSAGE})
            
            # Add previous chat history
            for msg in chat_history:
                messages.append(msg)
            
            messages.append({'role': 'user', 'content': augmented_query})

            ollama_chat_url = f"{OLLAMA_HOST}/api/chat"
            chat_payload = {
                'model': model,
                'messages': messages,
                'stream': True,
                'options': options
            }

            response = requests.post(ollama_chat_url, json=chat_payload, stream=True)
            response.raise_for_status()

            self.send_response(response.status_code)
            for k, v in response.headers.items():
                if k.lower() not in {'transfer-encoding', 'content-encoding'}:
                    self.send_header(k, v)
            self.end_headers()

            full_response_content = ""
            for chunk in response.iter_content(8192):
                self.wfile.write(chunk)
                full_response_content += chunk.decode('utf-8', errors='ignore')
            
            # Save code blocks from the full response
            if full_response_content.strip():
                self.code_extractor.save_code_blocks(full_response_content)

        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON.")
        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Ollama Chat Error: {e}")
        except Exception as e:
            self.send_error(500, f"Server Error: {e}")

    def _chunk_text(self, text, chunk_size=500, chunk_overlap=50):
        # A very basic text chunking strategy
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - chunk_overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks

    def _handle_embed_request(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))

            model_name = payload.get('model', 'nomic-embed-text') # Default to nomic-embed-text
            prompt = payload.get('prompt')

            if not prompt:
                self.send_error(400, "Bad Request: 'prompt' is required.")
                return

            ollama_embed_url = f"{OLLAMA_HOST}/api/embeddings"
            embed_payload = {"model": model_name, "prompt": prompt}
            
            embed_response = requests.post(ollama_embed_url, json=embed_payload)
            embed_response.raise_for_status()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(embed_response.content)

        except json.JSONDecodeError:
            self.send_error(400, "Bad Request: Invalid JSON.")
        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Ollama Embedding Error: {e}")
        except Exception as e:
            self.send_error(500, f"Server Error: {e}")

    def _proxy_request(self):
        try:
            api_url = f"{OLLAMA_HOST}{self.path}"
            headers = {h: self.headers[h] for h in self.headers}

            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)

                # ---- inject system message and handle options ----
                if self.path in ('/api/chat', '/api/generate'):
                    try:
                        payload = json.loads(post_data.decode('utf-8'))
                        
                        # Extract user-defined options from the request
                        user_options = payload.pop('options', {})

                        # Inject system message
                        if SYSTEM_MESSAGE:
                            if 'messages' in payload:      # /api/chat
                                if not payload.get('messages') or payload['messages'][0].get('role') != 'system':
                                    payload['messages'].insert(0, {'role': 'system', 'content': SYSTEM_MESSAGE})
                                else:
                                    payload['messages'][0]['content'] = f"{SYSTEM_MESSAGE}\n\n{payload['messages'][0]['content']}"
                            elif 'prompt' in payload:      # /api/generate
                                payload['system'] = SYSTEM_MESSAGE
                        
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

    def _get_embedding(self, text, model="nomic-embed-text"):
        try:
            response = requests.post(f"{OLLAMA_HOST}/api/embeddings",
                                     json={'model': model, 'prompt': text})
            response.raise_for_status()
            return response.json()['embedding']
        except requests.exceptions.RequestException as e:
            print(f"Error getting embedding from Ollama: {e}")
            return None

# ---------------------------------------------------------------------------
# 4. Serve forever
# ---------------------------------------------------------------------------
code_dir = os.path.expanduser('~/desktop/ollama_code_gen')
os.makedirs(code_dir, exist_ok=True)

with socketserver.TCPServer(("", PORT), OllamaProxyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Generated code will be saved to: {code_dir}")
    httpd.serve_forever()