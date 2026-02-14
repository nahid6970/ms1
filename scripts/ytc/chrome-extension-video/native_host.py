#!/usr/bin/env python3
"""
Native messaging host for YTC Video Downloader Chrome Extension
"""

import sys
import json
import struct
import subprocess
import os


def send_message(message):
    """Send a message to the Chrome extension"""
    encoded_message = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()


def read_message():
    """Read a message from the Chrome extension"""
    text_length_bytes = sys.stdin.buffer.read(4)
    if len(text_length_bytes) == 0:
        sys.exit(0)
    
    text_length = struct.unpack('I', text_length_bytes)[0]
    text = sys.stdin.buffer.read(text_length).decode('utf-8')
    return json.loads(text)


def build_auth_args():
    """Build authentication arguments from settings"""
    settings = chrome.storage.sync.get(['authMethod', 'browser', 'cookieFile'])
    auth_method = settings.get('authMethod', 'none')
    
    if auth_method == 'browser':
        browser = settings.get('browser', 'chrome')
        return ['--cookies-from-browser', browser]
    elif auth_method == 'file':
        cookie_file = settings.get('cookieFile', '')
        if cookie_file:
            return ['--cookies', cookie_file]
    
    return []


def fetch_formats(message):
    """Fetch available video and audio formats"""
    try:
        url = message['url']
        
        command = ['yt-dlp', '--dump-json', '--extractor-args', 'youtube:player_client=default', url]
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            send_message({"success": False, "error": stderr})
            return
        
        video_info = json.loads(stdout)
        formats = video_info.get('formats', [])
        
        video_formats = []
        audio_formats = []
        
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('acodec') == 'none':
                video_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A')
                })
            elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                audio_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'abr': f.get('abr', 'N/A')
                })
        
        send_message({
            "success": True,
            "videoFormats": video_formats,
            "audioFormats": audio_formats
        })
        
    except Exception as e:
        send_message({"success": False, "error": str(e)})


def download_video(message):
    """Download video with selected formats"""
    try:
        url = message['url']
        video_format = message['videoFormat']
        audio_format = message['audioFormat']
        download_subs = message.get('downloadSubs', False)
        sub_lang = message.get('subLang', 'en')
        save_dir = message['saveDir']
        
        # Build format string
        if video_format == 'best' and audio_format == 'best':
            format_str = 'bestvideo+bestaudio/best'
        elif video_format == 'best':
            format_str = f'bestvideo+{audio_format}'
        elif audio_format == 'best':
            format_str = f'{video_format}+bestaudio'
        else:
            format_str = f'{video_format}+{audio_format}'
        
        command = [
            'yt-dlp',
            '-f', format_str,
            '-o', f'{save_dir}/%(title)s.%(ext)s',
            '--extractor-args', 'youtube:player_client=default',
            '--newline'
        ]
        
        # Add subtitle options
        if download_subs:
            command.extend(['--write-subs', '--sub-langs', f'{sub_lang}.*'])
        
        command.append(url)
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        # Parse progress
        import re
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            if line:
                # Parse download progress
                match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
                if match:
                    percent = float(match.group(1))
                    send_message({
                        "progress": True,
                        "percent": percent,
                        "status": f"{percent:.1f}%"
                    })
        
        if process.returncode != 0:
            stderr = process.communicate()[1]
            send_message({"success": False, "error": stderr})
            return
        
        send_message({"success": True, "message": "Video downloaded successfully"})
        
    except Exception as e:
        send_message({"success": False, "error": str(e)})


def main():
    """Main loop for native messaging"""
    while True:
        try:
            message = read_message()
            action = message.get('action')
            
            if action == 'fetchFormats':
                fetch_formats(message)
            elif action == 'downloadVideo':
                download_video(message)
            else:
                send_message({"success": False, "error": "Unknown action"})
                
        except Exception as e:
            send_message({"success": False, "error": str(e)})
            sys.exit(1)


if __name__ == '__main__':
    main()
