"""
Run once to register the native messaging host with Chrome on Windows.
Usage: python install_host.py <EXTENSION_ID>
The extension ID can be found at chrome://extensions after loading the unpacked extension.
"""
import sys
import os
import json
import winreg

MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'com.delta.reveal_explorer.json')
HOST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'host.py')
LAUNCHER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_host.bat')
REG_KEY = r'Software\Google\Chrome\NativeMessagingHosts\com.delta.reveal_explorer'

def install(extension_ids):
    # Patch extension ID in manifest
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)

    manifest['allowed_origins'] = [f'chrome-extension://{extension_id}/' for extension_id in extension_ids]
    # Chrome starts native messaging hosts as programs. A Python source file is
    # not directly executable on Windows, so give Chrome a quiet batch launcher.
    launcher = '@echo off\r\n"{}" "{}" %*\r\n'.format(
        sys.executable.replace('"', '""'),
        HOST_PATH.replace('"', '""'),
    )
    with open(LAUNCHER_PATH, 'w', encoding='utf-8', newline='') as launcher_file:
        launcher_file.write(launcher)

    manifest['path'] = LAUNCHER_PATH

    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Write registry key pointing to the manifest
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_KEY)
    winreg.SetValueEx(key, '', 0, winreg.REG_SZ, MANIFEST_PATH)
    winreg.CloseKey(key)
    print(f'[OK] Registered native messaging host.')
    print(f'     Manifest: {MANIFEST_PATH}')
    for extension_id in extension_ids:
        print(f'     Extension: chrome-extension://{extension_id}/')

if __name__ == '__main__':
    extension_ids = [value.strip() for value in sys.argv[1:] if value.strip()]
    if not extension_ids:
        print('Usage: python install_host.py <EXTENSION_ID> [<EXTENSION_ID> ...]')
        print('Load the unpacked extension in Chrome first to obtain its ID.')
        sys.exit(1)
    invalid_ids = [extension_id for extension_id in extension_ids
                   if len(extension_id) != 32 or not all('a' <= c <= 'p' for c in extension_id)]
    if invalid_ids:
        print('Invalid Chrome extension ID(s): ' + ', '.join(invalid_ids))
        sys.exit(1)
    install(extension_ids)
