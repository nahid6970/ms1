import os
import http.server
import socketserver
import requests
import subprocess
import json
from bs4 import BeautifulSoup

PORT = 8000
OLLAMA_HOST = "http://localhost:11434"

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class OllamaProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api"):
            self._proxy_request()
        elif self.path == "/":
            self.path = "index.html"
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/stop_model":
            self._handle_stop_model()
        elif self.path.startswith("/api"):
            self._proxy_request()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_stop_model(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data)
            model_name = body.get("model")

            if not model_name:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Model name is required')
                return

            result = subprocess.run(
                ["ollama", "stop", model_name],
                capture_output=True,
                text=True
            )

            self.send_response(200 if result.returncode == 0 else 500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }).encode())

        except Exception as e:
            self.send_error(500, f"Error stopping model: {e}")

    def _proxy_request(self):
        try:
            api_url = f"{OLLAMA_HOST}{self.path}"
            headers = {h: self.headers[h] for h in self.headers}
            # headers['Host'] = 'localhost:11434' #! it tells to only respone to my pc

            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                response = requests.post(api_url, data=post_data, headers=headers, stream=True)
            else:
                response = requests.get(api_url, headers=headers, stream=True)

            self.send_response(response.status_code)
            for key, value in response.headers.items():
                if key.lower() not in ('transfer-encoding', 'content-encoding'):
                    self.send_header(key, value)
            self.end_headers()

            for chunk in response.iter_content(chunk_size=8192):
                self.wfile.write(chunk)

        except Exception as e:
            self.send_error(500, f"Proxy Error: {e}")

    

with socketserver.TCPServer(("", PORT), OllamaProxyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
