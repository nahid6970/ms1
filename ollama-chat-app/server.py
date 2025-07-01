import http.server
import socketserver
import requests
import json

PORT = 8000
OLLAMA_HOST = "http://localhost:11434"

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
        if self.path.startswith("/api"):
            self._proxy_request()
        else:
            self.send_response(404)
            self.end_headers()

    def _proxy_request(self):
        try:
            api_url = f"{OLLAMA_HOST}{self.path}"
            
            # Copy request headers from the client
            headers = {h: self.headers[h] for h in self.headers}
            headers['Host'] = 'localhost:11434' # Set the correct host for Ollama

            if self.command == 'POST':
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                response = requests.post(api_url, data=post_data, headers=headers, stream=True)
            else: # GET
                response = requests.get(api_url, headers=headers, stream=True)

            # Send response status code
            self.send_response(response.status_code)

            # Send headers
            for key, value in response.headers.items():
                # Skip headers that can cause issues with proxying
                if key.lower() not in ('transfer-encoding', 'content-encoding'):
                    self.send_header(key, value)
            self.end_headers()

            # Stream the response back to the client
            for chunk in response.iter_content(chunk_size=8192):
                self.wfile.write(chunk)

        except Exception as e:
            self.send_error(500, f"Proxy Error: {e}")


with socketserver.TCPServer(("", PORT), OllamaProxyHandler) as httpd:
    print(f"Serving at port {PORT}")
    print(f"Open http://localhost:{PORT} in your browser.")
    httpd.serve_forever()
