#!/usr/bin/env python3
import os
import subprocess
import time
import requests

def test_flask_launch():
    """Test launching a Flask app and verify it's working"""
    
    # Flask app details
    item = {
        "name": "Flask - 5001 - Text",
        "paths": ["C:\\Users\\nahid\\scoop\\apps\\python312\\current\\pythonw.exe"],
        "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5001_share_text\\share_text.py",
        "ExecutableType": "pythonw"
    }
    
    path = item["paths"][0]
    command = item.get("Command", "")
    executable_type = item.get("ExecutableType", "other")
    
    if executable_type == "pythonw":
        full_command = f'"{path}" {command}'
    
    print(f"Testing launch of: {item['name']}")
    print(f"Command: {full_command}")
    
    # Method 1: os.system (startup.py method)
    print("\n=== Testing os.system method (startup.py) ===")
    result = os.system(f'start "" {full_command}')
    print(f"os.system result: {result}")
    
    # Wait a bit for the app to start
    time.sleep(3)
    
    # Test if the app is responding
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        print(f"✓ App is responding! Status: {response.status_code}")
    except Exception as e:
        print(f"✗ App not responding: {e}")
    
    print("\n=== Testing subprocess.Popen method (app.py) ===")
    
    # Kill any existing process first
    os.system("taskkill /f /im pythonw.exe 2>nul")
    time.sleep(2)
    
    # Method 2: subprocess.Popen (app.py method)
    try:
        subprocess.Popen(
            full_command,
            shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
            close_fds=True
        )
        print("subprocess.Popen executed")
    except Exception as e:
        print(f"subprocess.Popen failed: {e}")
        # Fallback
        os.system(f'start "" {full_command}')
        print("Fallback to os.system")
    
    # Wait a bit for the app to start
    time.sleep(3)
    
    # Test if the app is responding
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        print(f"✓ App is responding! Status: {response.status_code}")
    except Exception as e:
        print(f"✗ App not responding: {e}")

if __name__ == "__main__":
    test_flask_launch()