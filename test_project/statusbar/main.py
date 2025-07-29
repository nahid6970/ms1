import subprocess
import sys
import os

def main():
    # Get the absolute path to the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Start the Flask server as a separate process
    py_executable = sys.executable
    app_path = os.path.join(script_dir, "app.py")
    server_process = subprocess.Popen([py_executable, app_path])

    # Construct the absolute file path for index.html
    index_path = os.path.join(script_dir, "index.html").replace("\\", "/")
    url = f"file:///{index_path}"

    # Command to open Chrome in app mode
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe" # Standard path
    if not os.path.exists(chrome_path):
        # Try another common path for Chrome
        chrome_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"

    # Launch Chrome in app mode
    browser_process = subprocess.Popen([chrome_path, f"--app={url}"])

    # Wait for the browser process to close, then terminate the server
    browser_process.wait()
    server_process.terminate()

if __name__ == '__main__':
    main()