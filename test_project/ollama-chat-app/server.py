import os
import sys
import http.server
import socketserver
import requests
import subprocess
import json
import threading
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
        elif self.path == "/api/stop_all_models":
            self._handle_stop_all_models()
        elif self.path == "/api/restart_server":
            self._handle_restart_server()  # <-- NEW
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

    def _handle_stop_all_models(self):
        try:
            result = subprocess.run(
                ["powershell", "-File", "ollama_stop_models.ps1"],
                capture_output=True,
                text=True,
                check=True
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Successfully executed ollama_stop_models.ps1",
                "stdout": result.stdout,
                "stderr": result.stderr
            }).encode())

        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": f"Error executing PowerShell script: {e}",
                "stdout": e.stdout,
                "stderr": e.stderr
            }).encode())
        except Exception as e:
            self.send_error(500, f"An unexpected error occurred: {e}")

    def _handle_restart_server(self):
        """
        Stop every running model and then restart this script.
        The parent exits immediately so the port becomes free.
        """
        try:
            # 1) Stop all models first
            subprocess.run(
                ["powershell", "-File", "ollama_stop_models.ps1"],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Could not stop models – aborting restart",
                "stdout": e.stdout,
                "stderr": e.stderr
            }).encode())
            return
        except Exception as e:
            self.send_error(500, f"Unexpected error while stopping models: {e}")
            return

        # 2) Spawn a detached child that will re-launch the server
        try:
            py = sys.executable
            script = os.path.abspath(__file__)

            DETACHED_PROCESS = 0x00000008
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            subprocess.Popen(
                [py, script],
                cwd=os.getcwd(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                creationflags=CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "message": "Server will restart in ~1 second"
            }).encode())

            # 3) Parent exits so the port is free
            threading.Thread(target=lambda: os._exit(0), daemon=True).start()

        except Exception as e:
            self.send_error(500, f"Could not spawn restart process: {e}")

    def _proxy_request(self):
        try:
            api_url = f"{OLLAMA_HOST}{self.path}"
            headers = {h: self.headers[h] for h in self.headers}

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