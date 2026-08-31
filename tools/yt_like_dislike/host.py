"""
Native messaging host for YT Analyzer.
Chrome communicates via stdin/stdout using 4-byte length-prefixed JSON messages.
We read one message (contains the YouTube URL) then launch app.py and exit.
"""
import sys
import json
import struct
import subprocess
import os

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

def main():
    msg = read_message()
    url = (msg or {}).get('url', '')

    app_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    args = [sys.executable, app_py]
    if url:
        args += ['--url', url]

    subprocess.Popen(args, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
    send_message({'ok': True})

if __name__ == '__main__':
    main()
