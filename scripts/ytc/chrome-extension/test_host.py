#!/usr/bin/env python3
"""
Test script to verify native host installation
"""

import winreg
import os
import json

def test_installation():
    """Test if the native host is properly installed"""
    
    print("="*60)
    print("TESTING NATIVE HOST INSTALLATION")
    print("="*60)
    
    # Check registry
    try:
        key_path = r"SOFTWARE\Google\Chrome\NativeMessagingHosts\com.ytc.subtitle_extractor"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
        manifest_path = winreg.QueryValueEx(key, "")[0]
        winreg.CloseKey(key)
        
        print(f"\n✓ Registry entry found")
        print(f"  Path: HKEY_CURRENT_USER\\{key_path}")
        print(f"  Manifest: {manifest_path}")
        
        # Check if manifest file exists
        if os.path.exists(manifest_path):
            print(f"\n✓ Manifest file exists")
            
            # Read and validate manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            print(f"\n✓ Manifest is valid JSON")
            print(f"  Name: {manifest.get('name')}")
            print(f"  Type: {manifest.get('type')}")
            print(f"  Path: {manifest.get('path')}")
            
            # Check if host script exists
            host_path = manifest.get('path')
            if os.path.exists(host_path):
                print(f"\n✓ Host script exists: {host_path}")
            else:
                print(f"\n✗ Host script NOT FOUND: {host_path}")
                return False
            
            # Check allowed origins
            origins = manifest.get('allowed_origins', [])
            print(f"\n  Allowed origins:")
            for origin in origins:
                print(f"    - {origin}")
                if "YOUR_EXTENSION_ID_HERE" in origin:
                    print(f"\n⚠ WARNING: You need to replace YOUR_EXTENSION_ID_HERE")
                    print(f"  1. Load extension in Chrome")
                    print(f"  2. Copy Extension ID from chrome://extensions/")
                    print(f"  3. Edit {manifest_path}")
                    print(f"  4. Replace YOUR_EXTENSION_ID_HERE with actual ID")
                    print(f"  5. Reload extension")
            
            # Check if yt-dlp is available
            print(f"\n  Checking yt-dlp...")
            import subprocess
            try:
                result = subprocess.run(['yt-dlp', '--version'], 
                                      capture_output=True, 
                                      text=True,
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    print(f"✓ yt-dlp is installed: {result.stdout.strip()}")
                else:
                    print(f"✗ yt-dlp not working properly")
                    return False
            except FileNotFoundError:
                print(f"✗ yt-dlp NOT FOUND in PATH")
                print(f"  Install: pip install yt-dlp")
                return False
            
            print(f"\n" + "="*60)
            print("✓ INSTALLATION LOOKS GOOD!")
            print("="*60)
            
            if "YOUR_EXTENSION_ID_HERE" in str(origins):
                print("\nNEXT STEP: Update Extension ID in manifest")
            else:
                print("\nYou should be ready to use the extension!")
            
            return True
            
        else:
            print(f"\n✗ Manifest file NOT FOUND: {manifest_path}")
            return False
            
    except FileNotFoundError:
        print(f"\n✗ Registry entry NOT FOUND")
        print(f"  Run: python install_host.py")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

if __name__ == '__main__':
    test_installation()
