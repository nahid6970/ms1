"""
Run once to register the native messaging host with Chrome on Windows.
Usage: python install_host.py <EXTENSION_ID>
The extension ID can be found at chrome://extensions after loading the unpacked extension.
"""
import sys
import os
import json
import winreg

MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'com.delta.yt_analyzer.json')
REG_KEY = r'Software\Google\Chrome\NativeMessagingHosts\com.delta.yt_analyzer'

def install(extension_id):
    # Patch extension ID in manifest
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)

    manifest['allowed_origins'] = [f'chrome-extension://{extension_id}/']
    # Ensure host.py path uses the python interpreter directly
    manifest['path'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'host.py')

    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Write registry key pointing to the manifest
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY)
    winreg.SetValueEx(key, '', 0, winreg.REG_SZ, MANIFEST_PATH)
    winreg.CloseKey(key)
    print(f'[OK] Registered native messaging host.')
    print(f'     Manifest: {MANIFEST_PATH}')
    print(f'     Extension: chrome-extension://{extension_id}/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python install_host.py <EXTENSION_ID>')
        print('Find your extension ID at chrome://extensions')
        sys.exit(1)
    install(sys.argv[1].strip())
