#!/usr/bin/env python3

import json
import os
import sys
import webbrowser
import subprocess
import platform
from pathlib import Path
import http.server
import socketserver
import urllib.parse
import threading
import time
import base64
import hashlib
import secrets
import requests

class InteractiveGoogleOAuthManager:
    def __init__(self):
        self.redirect_uri = "http://localhost:8789/callback"
        self.auth_server = None
        self.auth_code = None
        self.auth_error = None
        self.credentials = None
        self.tokens = {}
        
        # Available Google services
        self.services = {
            "1": {"name": "Gmail", "url": "https://mail.google.com", "key": "gmail"},
            "2": {"name": "Google Drive", "url": "https://drive.google.com", "key": "drive"},
            "3": {"name": "Google Calendar", "url": "https://calendar.google.com", "key": "calendar"},
            "4": {"name": "Google Photos", "url": "https://photos.google.com", "key": "photos"},
            "5": {"name": "YouTube", "url": "https://youtube.com", "key": "youtube"},
            "6": {"name": "Google Docs", "url": "https://docs.google.com", "key": "docs"},
            "7": {"name": "Google Sheets", "url": "https://sheets.google.com", "key": "sheets"},
            "8": {"name": "Google Slides", "url": "https://slides.google.com", "key": "slides"},
            "9": {"name": "Google Keep", "url": "https://keep.google.com", "key": "keep"},
            "10": {"name": "Google Maps", "url": "https://maps.google.com", "key": "maps"}
        }
        
        self.scopes = [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/calendar.readonly"
        ]
    
    def load_client_secret(self, file_path):
        """Load credentials from downloaded client_secret.json file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Check if it's a valid client secret file
            if 'web' in data:
                creds = data['web']
            elif 'installed' in data:
                creds = data['installed']
            else:
                print("❌ Invalid client secret file format")
                return False
                
            self.credentials = {
                "client_id": creds['client_id'],
                "client_secret": creds['client_secret']
            }
            
            print(f"✅ Client credentials loaded successfully")
            print(f"   Client ID: {self.credentials['client_id'][:50]}...")
            return True
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON file: {file_path}")
            return False
        except KeyError as e:
            print(f"❌ Missing required field in credentials: {e}")
            return False
    
    def get_client_secret_file(self):
        """Interactive prompt to get client secret file"""
        print("🔑 Google OAuth Client Secret Setup")
        print("=" * 50)
        
        while True:
            print("\nPlease provide your Google OAuth client secret file:")
            print("1. Enter full path to client_secret.json")
            print("2. Place client_secret.json in current directory and press Enter")
            print("3. Exit")
            
            choice = input("\nYour choice (1-3): ").strip()
            
            if choice == "1":
                file_path = input("Enter full path to client_secret.json: ").strip()
                if file_path.startswith('"') and file_path.endswith('"'):
                    file_path = file_path[1:-1]  # Remove quotes
                if self.load_client_secret(file_path):
                    return True
                    
            elif choice == "2":
                default_files = ["client_secret.json", "credentials.json", "oauth_client.json"]
                found = False
                
                for filename in default_files:
                    if os.path.exists(filename):
                        if self.load_client_secret(filename):
                            found = True
                            break
                
                if not found:
                    print("❌ No client secret file found in current directory")
                    print(f"   Looking for: {', '.join(default_files)}")
                else:
                    return True
                    
            elif choice == "3":
                print("👋 Goodbye!")
                return False
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    def generate_pkce_pair(self):
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    def start_auth_server(self):
        """Start local server for OAuth callback"""
        class AuthHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, oauth_manager, *args, **kwargs):
                self.oauth_manager = oauth_manager
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                if self.path.startswith('/callback'):
                    parsed_url = urllib.parse.urlparse(self.path)
                    params = urllib.parse.parse_qs(parsed_url.query)
                    
                    if 'code' in params:
                        self.oauth_manager.auth_code = params['code'][0]
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        success_html = """
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authentication Success</title>
                            <style>
                                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                                .success { color: #28a745; font-size: 24px; }
                                .message { color: #666; margin: 20px 0; }
                            </style>
                        </head>
                        <body>
                            <div class="success">✅ Authentication Successful!</div>
                            <div class="message">You can close this tab now and return to the terminal.</div>
                            <script>
                                setTimeout(function() {
                                    window.close();
                                }, 3000);
                            </script>
                        </body>
                        </html>
                        """
                        self.wfile.write(success_html.encode())
                    elif 'error' in params:
                        error = params['error'][0]
                        self.oauth_manager.auth_error = error
                        self.send_response(400)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        
                        error_html = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <title>Authentication Error</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                                .error {{ color: #dc3545; font-size: 24px; }}
                                .message {{ color: #666; margin: 20px 0; }}
                                .solution {{ background: #f8f9fa; padding: 20px; margin: 20px; border-radius: 5px; text-align: left; }}
                            </style>
                        </head>
                        <body>
                            <div class="error">❌ Authentication Error</div>
                            <div class="message">Error: {error}</div>
                            <div class="solution">
                                <h3>If you see "access_denied" or "app not verified":</h3>
                                <ol>
                                    <li>Go to Google Cloud Console</li>
                                    <li>Navigate to OAuth consent screen</li>
                                    <li>Add your email as a test user, OR</li>
                                    <li>Click "Publish App" to make it public</li>
                                </ol>
                            </div>
                        </body>
                        </html>
                        """
                        self.wfile.write(error_html.encode())
                    else:
                        self.send_error(400, "Authorization failed")
                else:
                    self.send_error(404, "Not found")
            
            def log_message(self, format, *args):
                pass
        
        handler = lambda *args, **kwargs: AuthHandler(self, *args, **kwargs)
        
        try:
            with socketserver.TCPServer(("", 8789), handler) as httpd:
                self.auth_server = httpd
                httpd.serve_forever()
        except OSError as e:
            print(f"❌ Error starting server on port 8789: {e}")
            return False
    
    def get_authorization_url(self):
        """Generate OAuth authorization URL"""
        code_verifier, code_challenge = self.generate_pkce_pair()
        self.code_verifier = code_verifier
        
        scopes = " ".join(self.scopes)
        
        auth_params = {
            "client_id": self.credentials["client_id"],
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": scopes,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "offline",
            "prompt": "select_account"
        }
        
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(auth_params)
    
    def exchange_code_for_tokens(self, auth_code):
        """Exchange authorization code for tokens"""
        token_url = "https://oauth2.googleapis.com/token"
        
        token_data = {
            "client_id": self.credentials["client_id"],
            "client_secret": self.credentials["client_secret"],
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_verifier
        }
        
        try:
            response = requests.post(token_url, data=token_data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error exchanging code for tokens: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Get user information"""
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get("https://www.googleapis.com/oauth2/v2/userinfo", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Error getting user info: {e}")
            return None
    
    def authenticate(self):
        """Perform OAuth authentication"""
        print("\n🔐 Starting Google OAuth Authentication")
        print("=" * 50)
        
        # Start server in background
        server_thread = threading.Thread(target=self.start_auth_server, daemon=True)
        server_thread.start()
        time.sleep(1)
        
        # Get auth URL and open browser
        auth_url = self.get_authorization_url()
        print("🌐 Opening browser for authentication...")
        print("   Please sign in with your Google account")
        
        self.open_in_browser(auth_url)
        
        # Wait for callback
        print("⏳ Waiting for authentication (check your browser)...")
        timeout = 120
        start_time = time.time()
        
        while not self.auth_code and not self.auth_error and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        if self.auth_error:
            print(f"❌ Authentication error: {self.auth_error}")
            if self.auth_error == "access_denied":
                print("\n🔧 Solution:")
                print("1. Go to Google Cloud Console")
                print("2. Navigate to 'OAuth consent screen'")
                print("3. Add your email as a test user, OR")
                print("4. Click 'Publish App' to make it public")
            return False
        
        if not self.auth_code:
            print("❌ Authentication timed out")
            return False
        
        print("✅ Authorization received, getting tokens...")
        
        # Exchange for tokens
        self.tokens = self.exchange_code_for_tokens(self.auth_code)
        if not self.tokens:
            return False
        
        # Get user info
        user_info = self.get_user_info(self.tokens["access_token"])
        if not user_info:
            return False
        
        print(f"🎉 Successfully authenticated as: {user_info['email']}")
        print(f"   Name: {user_info['name']}")
        
        self.user_info = user_info
        return True
    
    def open_in_browser(self, url):
        """Open URL in default browser"""
        try:
            # Try to open in incognito mode
            system = platform.system().lower()
            
            if system == "windows":
                chrome_paths = [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                ]
                for path in chrome_paths:
                    if os.path.exists(path):
                        subprocess.run([path, "--incognito", url], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return
            elif system == "darwin":
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                if os.path.exists(chrome_path):
                    subprocess.run([chrome_path, "--incognito", url], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
            elif system == "linux":
                chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser"]
                for path in chrome_paths:
                    if os.path.exists(path):
                        subprocess.run([path, "--incognito", url], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        return
            
            # Fallback to default browser
            webbrowser.open(url)
            
        except Exception:
            webbrowser.open(url)
    
    def show_service_menu(self):
        """Show interactive service selection menu"""
        print(f"\n🚀 Welcome, {self.user_info['name']}!")
        print("=" * 50)
        print("Select a Google service to open:")
        print()
        
        for key, service in self.services.items():
            print(f"{key:2}. {service['name']}")
        
        print()
        print("0. Exit")
        print("r. Re-authenticate")
        
        while True:
            choice = input(f"\nYour choice (0-{len(self.services)} or 'r'): ").strip().lower()
            
            if choice == "0":
                print("👋 Goodbye!")
                return False
            elif choice == "r":
                print("🔄 Re-authenticating...")
                return "reauth"
            elif choice in self.services:
                service = self.services[choice]
                print(f"🌐 Opening {service['name']} in incognito mode...")
                self.open_in_browser(service["url"])
                print(f"✅ {service['name']} opened successfully!")
                print("\nPress Enter to continue or choose another service...")
                input()
                return True
            else:
                print("❌ Invalid choice. Please try again.")
    
    def run(self):
        """Main interactive loop"""
        print("🔐 Interactive Google OAuth Manager")
        print("=" * 50)
        
        # Get client secret file
        if not self.get_client_secret_file():
            return
        
        while True:
            # Authenticate
            if not self.authenticate():
                retry = input("\n❌ Authentication failed. Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    break
                continue
            
            # Show service menu
            while True:
                result = self.show_service_menu()
                if result == "reauth":
                    break  # Go back to authentication
                elif result == False:
                    return  # Exit completely
                # If result == True, continue showing menu

def main():
    try:
        # Check if requests is available
        import requests
    except ImportError:
        print("❌ Required package 'requests' not found.")
        print("Please install it using: pip install requests")
        return
    
    manager = InteractiveGoogleOAuthManager()
    manager.run()

if __name__ == "__main__":
    main()

# "step_1": "Go to https://console.cloud.google.com/",
# "step_2": "Create a new project or select existing one",
# "step_3": "Enable Google+ API or Google Identity API",
# "step_4": "Go to 'Credentials' > 'Create Credentials' > 'OAuth 2.0 Client ID'",
# "step_5": "Select 'Web Application' as application type",
# "step_6": "Add 'http://localhost:8080/callback' to authorized redirect URIs",
# "step_7": "Copy client_id and client_secret to this config file",
# "step_8": "Remove this setup_instructions section after setup"
# "step_9": "Publish it"