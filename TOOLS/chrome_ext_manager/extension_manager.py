#!/usr/bin/env python3
"""
Chrome Extension Data Manager
Runs a local HTTP server that receives JSON data from Chrome extensions
and saves them to organized directories.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from pathlib import Path
import logging

# Configuration
HOST = 'localhost'
PORT = 8765
DATA_DIR = Path('./extension_data')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExtensionHandler(BaseHTTPRequestHandler):
    """Handle requests from Chrome extensions"""
    
    def _set_cors_headers(self):
        """Set CORS headers to allow extension communication"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests with JSON data"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            # Extract extension info
            extension_name = data.get('extension_name', 'unknown')
            file_name = data.get('file_name', 'data.json')  # Custom filename
            save_data = data.get('data', {})
            
            # Ensure filename ends with .json
            if not file_name.endswith('.json'):
                file_name += '.json'
            
            # Create directory for this extension
            extension_dir = DATA_DIR / extension_name
            extension_dir.mkdir(parents=True, exist_ok=True)
            
            # Use custom filename
            filepath = extension_dir / file_name
            
            # Save the data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved data from '{extension_name}' to {filepath}")
            
            # Send success response
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'success',
                'message': f'Data saved to {filepath}',
                'filepath': str(filepath)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.send_response(500)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_GET(self):
        """Handle GET requests - health check"""
        if self.path == '/health':
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'running',
                'message': 'Extension Manager is active'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to use custom logger"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    """Start the extension manager server"""
    # Create data directory
    DATA_DIR.mkdir(exist_ok=True)
    
    # Start server
    server = HTTPServer((HOST, PORT), ExtensionHandler)
    logger.info(f"Extension Manager running on http://{HOST}:{PORT}")
    logger.info(f"Data will be saved to: {DATA_DIR.absolute()}")
    logger.info("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        server.shutdown()


if __name__ == '__main__':
    main()
