"""
Native messaging host for Reveal In Explorer.
Chrome communicates via stdin/stdout using 4-byte length-prefixed JSON messages.
We read one message (contains the file:/// URL), convert it to a Windows path,
then run explorer.exe /select,"<path>" and exit.
"""
import sys
import json
import struct
import subprocess
import os
import urllib.parse


def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) < 4:
        return None
    length = struct.unpack('<I', raw_length)[0]
    return json.loads(sys.stdin.buffer.read(length).decode('utf-8'))


def send_message(data):
    encoded = json.dumps(data).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('<I', len(encoded)))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


def file_url_to_windows_path(file_url):
    """
    Convert a file:/// URL to a Windows filesystem path.
    Example: file:///C:/Users/nahid/Downloads/file.pdf -> C:\\Users\\nahid\\Downloads\\file.pdf
    """
    if not file_url:
        return ''

    parsed = urllib.parse.urlparse(file_url)
    # url.path is like /C:/Users/nahid/Downloads/file.pdf
    path = urllib.parse.unquote(parsed.path)

    # Strip leading slashes, then convert forward slashes to backslashes
    path = path.lstrip('/')
    path = path.replace('/', '\\')

    return path


def main():
    msg = read_message()
    url = (msg or {}).get('url', '')

    path = file_url_to_windows_path(url)
    if not path:
        send_message({'ok': False, 'error': 'Could not parse file URL.'})
        return

    if not os.path.exists(path):
        send_message({'ok': False, 'error': f'File not found: {path}'})
        return

    # explorer.exe /select,"C:\path\to\file.pdf"  — opens Explorer with the file selected
    subprocess.Popen(
        ['explorer.exe', '/select,', path],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    send_message({'ok': True})


if __name__ == '__main__':
    main()
