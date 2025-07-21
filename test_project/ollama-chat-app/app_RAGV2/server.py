# server.py  (complete, ready to use)
import os
import http.server
import socketserver
import requests
import json
import datetime
import re
import hashlib
import sqlite3
import numpy as np
from pathlib import Path
import mimetypes
import urllib.parse

PORT = 8000
OLLAMA_HOST = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text:latest"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 1. Settings management
# ---------------------------------------------------------------------------
SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'instructions': []
    }

def save_settings_to_file(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)

current_settings = load_settings()

def get_active_system_message():
    """Build system message from active instructions"""
    active_instructions = [
        instr['content'] for instr in current_settings['instructions'] 
        if instr.get('enabled', True)
    ]
    return '\n\n'.join(active_instructions) if active_instructions else ""

# ---------------------------------------------------------------------------
# 2. RAG System with Ollama Embeddings
# ---------------------------------------------------------------------------
class RAGSystem:
    def __init__(self, db_path="rag_database.db"):
        self.db_path = db_path
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing documents and embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_index INTEGER,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_embedding(self, text):
        """Get embedding from Ollama using nomic-embed-text model"""
        try:
            response = requests.post(f"{OLLAMA_HOST}/api/embeddings", 
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text
                })
            
            if response.status_code == 200:
                return response.json()["embedding"]
            else:
                print(f"Embedding error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return None
    
    def chunk_text(self, text):
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            if len(chunk_words) < self.chunk_size:
                break
        
        return chunks
    
    def add_document(self, filename, content, metadata=None):
        """Add a document to the RAG system"""
        if metadata is None:
            metadata = {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert document
        cursor.execute('''
            INSERT INTO documents (filename, content, metadata)
            VALUES (?, ?, ?)
        ''', (filename, content, json.dumps(metadata)))
        
        document_id = cursor.lastrowid
        
        # Chunk the content
        chunks = self.chunk_text(content)
        chunk_ids = []
        
        for i, chunk in enumerate(chunks):
            # Get embedding for chunk
            embedding = self.get_embedding(chunk)
            if embedding is None:
                print(f"Failed to get embedding for chunk {i} of {filename}")
                continue
            
            # Store embedding as bytes
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            
            # Insert chunk
            chunk_metadata = {
                **metadata,
                'filename': filename,
                'chunk_index': i,
                'chunk_count': len(chunks)
            }
            
            cursor.execute('''
                INSERT INTO chunks (document_id, chunk_index, content, embedding, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (document_id, i, chunk, embedding_bytes, json.dumps(chunk_metadata)))
            
            chunk_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        return {
            'document_id': document_id,
            'chunk_ids': chunk_ids,
            'chunks_created': len(chunk_ids)
        }
    
    def search(self, query, n_results=5):
        """Search for similar chunks using cosine similarity"""
        query_embedding = self.get_embedding(query)
        if query_embedding is None:
            return []
        
        query_vector = np.array(query_embedding, dtype=np.float32)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, content, embedding, metadata FROM chunks WHERE embedding IS NOT NULL')
        rows = cursor.fetchall()
        
        similarities = []
        for row in rows:
            chunk_id, content, embedding_bytes, metadata_str = row
            
            # Convert bytes back to numpy array
            chunk_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            
            # Calculate cosine similarity
            similarity = np.dot(query_vector, chunk_embedding) / (
                np.linalg.norm(query_vector) * np.linalg.norm(chunk_embedding)
            )
            
            similarities.append({
                'id': chunk_id,
                'content': content,
                'similarity': similarity,
                'distance': 1 - similarity,
                'metadata': json.loads(metadata_str) if metadata_str else {}
            })
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        conn.close()
        return similarities[:n_results]
    
    def get_documents(self):
        """Get all documents in the collection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT d.id, d.filename, d.metadata, d.created_at, COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN chunks c ON d.id = c.document_id
            GROUP BY d.id, d.filename, d.metadata, d.created_at
            ORDER BY d.created_at DESC
        ''')
        
        rows = cursor.fetchall()
        documents = []
        
        for row in rows:
            doc_id, filename, metadata_str, created_at, chunk_count = row
            documents.append({
                'id': doc_id,
                'filename': filename,
                'metadata': json.loads(metadata_str) if metadata_str else {},
                'created_at': created_at,
                'chunk_count': chunk_count
            })
        
        conn.close()
        return documents
    
    def clear_collection(self):
        """Clear all documents and chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chunks')
        cursor.execute('DELETE FROM documents')
        
        conn.commit()
        conn.close()
        
        return True
    
    def read_file(self, file_path):
        """Read and return file content based on file type"""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file extension
            ext = path.suffix.lower()
            
            # Read text files
            if ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.xml']:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {ext}")
                
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")
    
    def add_file(self, file_path, metadata=None):
        """Add a single file to the RAG system"""
        content = self.read_file(file_path)
        filename = Path(file_path).name
        
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'file_path': str(file_path),
            'file_size': len(content),
            'file_type': Path(file_path).suffix.lower()
        })
        
        return self.add_document(filename, content, metadata)
    
    def add_directory(self, directory_path, metadata=None, recursive=True, file_extensions=None):
        """Add all files from a directory to the RAG system"""
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json']
        
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        added_files = {}
        
        # Get files based on recursive setting
        if recursive:
            files = directory.rglob('*')
        else:
            files = directory.iterdir()
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                try:
                    result = self.add_file(str(file_path), metadata)
                    added_files[str(file_path)] = result['chunk_ids']
                except Exception as e:
                    print(f"Error adding file {file_path}: {e}")
                    continue
        
        return {
            'added_files': added_files,
            'total_files': len(added_files)
        }

# Initialize RAG system
rag_system = RAGSystem()

# ---------------------------------------------------------------------------
# 3. CodeExtractor with filename-from-first-line support
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
        if self.path.startswith("/api"):
            self._proxy_request()
        elif self.path == "/":
            self.path = "index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/settings/save':
            self._handle_settings_save()
        elif self.path == '/api/rag/search':
            self._handle_rag_search()
        elif self.path == '/api/rag/add_file':
            self._handle_rag_add_file()
        elif self.path == '/api/rag/add_directory':
            self._handle_rag_add_directory()
        elif self.path == '/api/rag/clear':
            self._handle_rag_clear()
        elif self.path.startswith("/api"):
            self._proxy_request()
        else:
            self.send_response(404)
            self.end_headers()

    def _proxy_request(self):
        global current_settings
        current_settings = load_settings() # Ensure latest settings are loaded for each request
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

                        # Get user query for RAG search
                        user_query = ""
                        if 'messages' in payload and payload['messages']:
                            # Get the last user message
                            for msg in reversed(payload['messages']):
                                if msg.get('role') == 'user':
                                    user_query = msg.get('content', '')
                                    break
                        elif 'prompt' in payload:
                            user_query = payload['prompt']

                        # Perform RAG search if we have documents and a query
                        rag_context = ""
                        if user_query.strip():
                            try:
                                # Check if we have any documents
                                documents = rag_system.get_documents()
                                if documents:
                                    # Search for relevant content
                                    search_results = rag_system.search(user_query, n_results=3)
                                    if search_results:
                                        rag_context = "\n\n--- RELEVANT CONTEXT FROM KNOWLEDGE BASE ---\n"
                                        for i, result in enumerate(search_results):
                                            similarity_percent = result['similarity'] * 100
                                            rag_context += f"\nContext {i+1} (Relevance: {similarity_percent:.1f}%):\n"
                                            rag_context += f"Source: {result['metadata'].get('filename', 'Unknown')}\n"
                                            rag_context += f"Content: {result['content']}\n"
                                        rag_context += "\n--- END CONTEXT ---\n\n"
                                        print(f"Added RAG context from {len(search_results)} relevant chunks")
                            except Exception as e:
                                print(f"RAG search error: {e}")

                        # Inject system message
                        # Prioritize system_instructions from payload, otherwise use active instructions from settings
                        system_message_content = ""
                        if 'system_instructions' in payload:
                            active_payload_instructions = [
                                instr['content'] for instr in payload['system_instructions'] 
                                if instr.get('enabled', True)
                            ]
                            system_message_content = '\n\n'.join(active_payload_instructions)
                            del payload['system_instructions'] # Remove from payload before sending to Ollama
                        else:
                            system_message_content = get_active_system_message()

                        # Add RAG context to system message
                        if rag_context:
                            rag_instruction = "You have access to relevant information from the knowledge base. Use this context to provide accurate and detailed answers. If the context doesn't contain relevant information for the user's question, respond normally based on your training."
                            system_message_content = f"{system_message_content}\n\n{rag_instruction}{rag_context}" if system_message_content else f"{rag_instruction}{rag_context}"

                        if system_message_content:
                            print(f"Using system message with RAG context: {len(system_message_content)} characters")
                            if 'messages' in payload:      # /api/chat
                                if not payload.get('messages') or payload['messages'][0].get('role') != 'system':
                                    payload['messages'].insert(0, {'role': 'system', 'content': system_message_content})
                                else:
                                    payload['messages'][0]['content'] = f"{system_message_content}\n\n{payload['messages'][0]['content']}"
                            elif 'prompt' in payload:      # /api/generate
                                payload['system'] = system_message_content
                        
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

    def do_GET(self):
        if self.path == '/api/rag/documents':
            self._handle_rag_documents()
        elif self.path.startswith("/api"):
            self._proxy_request()
        elif self.path == "/":
            self.path = "index.html"
            super().do_GET()
        else:
            super().do_GET()

    def _handle_settings_save(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            settings_data = json.loads(post_data.decode('utf-8'))['settings']
            save_settings_to_file(settings_data)
            global current_settings
            current_settings = load_settings() # Reload settings after saving
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error saving settings: {e}")

    def _handle_rag_search(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '')
            n_results = data.get('n_results', 5)
            
            if not query:
                self.send_error(400, "Query is required")
                return
            
            results = rag_system.search(query, n_results)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'results': results}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Search error: {e}")

    def _handle_rag_add_file(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            file_path = data.get('file_path', '')
            metadata = data.get('metadata', {})
            
            if not file_path:
                self.send_error(400, "File path is required")
                return
            
            result = rag_system.add_file(file_path, metadata)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'document_id': result['document_id'],
                'chunk_ids': result['chunk_ids'],
                'chunks_created': result['chunks_created']
            }).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Add file error: {e}")

    def _handle_rag_add_directory(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            directory_path = data.get('directory_path', '')
            metadata = data.get('metadata', {})
            recursive = data.get('recursive', True)
            file_extensions = data.get('file_extensions', ['.txt', '.md', '.py', '.js', '.html', '.css', '.json'])
            
            if not directory_path:
                self.send_error(400, "Directory path is required")
                return
            
            result = rag_system.add_directory(directory_path, metadata, recursive, file_extensions)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'added_files': result['added_files'],
                'total_files': result['total_files']
            }).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Add directory error: {e}")

    def _handle_rag_documents(self):
        try:
            documents = rag_system.get_documents()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'documents': documents}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Get documents error: {e}")

    def _handle_rag_clear(self):
        try:
            rag_system.clear_collection()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Clear collection error: {e}")

# ---------------------------------------------------------------------------
# 4. Serve forever
# ---------------------------------------------------------------------------
code_dir = os.path.expanduser('~/desktop/ollama_code_gen')
os.makedirs(code_dir, exist_ok=True)

with socketserver.TCPServer(("", PORT), OllamaProxyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print(f"Generated code will be saved to: {code_dir}")
    httpd.serve_forever()