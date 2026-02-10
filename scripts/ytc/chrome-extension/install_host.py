#!/usr/bin/env python3
"""
Installer for YTC Subtitle Extractor Native Messaging Host
Run this script to register the native host with Chrome
"""

import os
import sys
import json
import winreg


def install_native_host():
    """Install the native messaging host for Chrome"""
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    host_path = os.path.join(script_dir, 'native_host.py')
    
    # Create a batch file wrapper for Windows
    batch_path = os.path.join(script_dir, 'native_host.bat')
    with open(batch_path, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'python "{host_path}" %*\n')
    
    print(f"✓ Created batch wrapper at: {batch_path}")
    
    # Create the manifest for native messaging
    manifest = {
        "name": "com.ytc.subtitle_extractor",
        "description": "YTC Subtitle Extractor Native Host",
        "path": batch_path,
        "type": "stdio",
        "allowed_origins": [
            "chrome-extension://YOUR_EXTENSION_ID_HERE/"
        ]
    }
    
    # Save manifest
    manifest_path = os.path.join(script_dir, 'com.ytc.subtitle_extractor.json')
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✓ Created manifest at: {manifest_path}")
    
    # Register with Windows Registry (for Chrome)
    try:
        key_path = r"SOFTWARE\Google\Chrome\NativeMessagingHosts\com.ytc.subtitle_extractor"
        
        # Create the registry key
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, manifest_path)
        winreg.CloseKey(key)
        
        print(f"✓ Registered with Chrome registry")
        print(f"\nRegistry path: HKEY_CURRENT_USER\\{key_path}")
        
    except Exception as e:
        print(f"✗ Failed to register with Chrome: {e}")
        return False
    
    print("\n" + "="*60)
    print("INSTALLATION COMPLETE!")
    print("="*60)
    print("\nNEXT STEPS:")
    print("1. Load the extension in Chrome:")
    print("   - Go to chrome://extensions/")
    print("   - Enable 'Developer mode'")
    print("   - Click 'Load unpacked'")
    print(f"   - Select folder: {script_dir}")
    print("\n2. Copy the Extension ID from chrome://extensions/")
    print("\n3. Edit the manifest file and replace YOUR_EXTENSION_ID_HERE:")
    print(f"   {manifest_path}")
    print("\n4. Reload the extension in Chrome")
    print("\n5. Configure settings in the extension (save directory, etc.)")
    print("\nREQUIREMENTS:")
    print("- yt-dlp must be installed and in PATH")
    print("  Install: pip install yt-dlp")
    print("="*60)
    
    return True


if __name__ == '__main__':
    if os.name != 'nt':
        print("This installer is for Windows only.")
        print("For other platforms, manually register the native host.")
        sys.exit(1)
    
    install_native_host()
