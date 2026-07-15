#!/usr/bin/env python3
"""
Installation script for YTC Video Downloader Chrome Extension
"""

import os
import sys
import json
import winreg
import shutil

def get_extension_id():
    """Get the extension ID from user"""
    print("\n=== YTC VIDEO DOWNLOADER - INSTALLATION ===\n")
    print("1. Load the extension in Chrome (chrome://extensions)")
    print("2. Enable 'Developer mode'")
    print("3. Copy the Extension ID\n")
    
    ext_id = input("Enter Extension ID: ").strip()
    return ext_id

def install_native_host(ext_id):
    """Install native messaging host"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Update manifest
    manifest_path = os.path.join(script_dir, "com.ytc.video_downloader.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    manifest['allowed_origins'] = [f"chrome-extension://{ext_id}/"]
    manifest['path'] = os.path.join(script_dir, "native_host.bat")
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Register in Windows Registry
    try:
        key_path = r"Software\Google\Chrome\NativeMessagingHosts\com.ytc.video_downloader"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, manifest_path)
        winreg.CloseKey(key)
        print(f"\n✓ Native host registered successfully!")
        print(f"✓ Manifest: {manifest_path}")
        return True
    except Exception as e:
        print(f"\n✗ Failed to register: {e}")
        return False

def main():
    ext_id = get_extension_id()
    
    if not ext_id:
        print("Error: Extension ID is required")
        sys.exit(1)
    
    if install_native_host(ext_id):
        print("\n=== INSTALLATION COMPLETE ===")
        print("\nRestart Chrome and test the extension!")
    else:
        print("\n=== INSTALLATION FAILED ===")
        sys.exit(1)

if __name__ == '__main__':
    main()
