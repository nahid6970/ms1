#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Test the exact same logic as app.py
def test_launch():
    # Simulate a Flask item
    item = {
        "name": "Flask - 5001 - Text",
        "paths": ["C:\\Users\\nahid\\scoop\\apps\\python312\\current\\pythonw.exe"],
        "Command": "C:\\Users\\nahid\\ms\\ms1\\scripts\\flask\\5001_share_text\\share_text.py",
        "ExecutableType": "pythonw"
    }
    
    # Same logic as app.py
    path = item["paths"][0]
    command = item.get("Command", "")
    executable_type = item.get("ExecutableType", "other")
    
    # Auto-detect executable type if not set and path contains pythonw.exe
    if executable_type == "other" and "pythonw.exe" in path.lower():
        executable_type = "pythonw"
    
    full_command = ""
    if executable_type == "pythonw":
        full_command = f'"{path}" {command}'
    elif executable_type == "pwsh":
        full_command = f'"{path}" -Command {command}'
    elif executable_type == "cmd":
        full_command = f'"{path}" /c {command}'
    elif executable_type == "powershell":
        full_command = f'"{path}" -Command {command}'
    elif executable_type == "ahk_v2":
        full_command = f'"C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe" "{path}" {command}'
    else: # other
        if command:
            full_command = f'"{path}" {command}'
        else:
            full_command = f'"{path}"'
    
    print(f"Item: {item['name']}")
    print(f"Path: {path}")
    print(f"Command: {command}")
    print(f"ExecutableType: {executable_type}")
    print(f"Full command: {full_command}")
    print(f"Final os.system command: start \"\" {full_command}")
    print()
    
    # Test if the Python script exists
    if os.path.exists(command):
        print(f"✓ Python script exists: {command}")
    else:
        print(f"✗ Python script NOT found: {command}")
    
    # Test if pythonw.exe exists
    if os.path.exists(path):
        print(f"✓ pythonw.exe exists: {path}")
    else:
        print(f"✗ pythonw.exe NOT found: {path}")
    
    print("\nTesting launch...")
    try:
        # Execute the command using os.system - same as app.py
        result = os.system(f'start "" {full_command}')
        print(f"os.system result: {result}")
        if result == 0:
            print("✓ Launch command executed successfully")
        else:
            print(f"✗ Launch command failed with code: {result}")
    except Exception as e:
        print(f"✗ Exception during launch: {e}")

if __name__ == "__main__":
    test_launch()