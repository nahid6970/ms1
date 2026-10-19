#!/usr/bin/env python3
"""
Native messaging host for YTC Video Downloader Chrome Extension
"""

import sys
import json
import struct
import subprocess
import os
import re


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


def is_youtube_url(url):
    """Check if URL is a YouTube video URL"""
    youtube_patterns = [
        r'^(https?://)?(www\.)?youtube\.com/',
        r'^(https?://)?(www\.)?youtu\.be/',
        r'^(https?://)?(www\.)?youtube-nocookie\.com/',
    ]
    return any(re.match(pattern, url, re.IGNORECASE) for pattern in youtube_patterns)


def is_facebook_url(url):
    """Check if URL is a Facebook video URL"""
    facebook_patterns = [
        r'^(https?://)?(www\.)?facebook\.com/',
        r'^(https?://)?(www\.)?fb\.watch/',
        r'^(https?://)?(www\.)?fb\.com/',
        r'^(https?://)?m\.facebook\.com/',
        r'^(https?://)?web\.facebook\.com/',
    ]
    return any(re.match(pattern, url, re.IGNORECASE) for pattern in facebook_patterns)


def build_extractor_args(url):
    """Build extractor-args only for YouTube URLs"""
    if is_youtube_url(url):
        return ['--extractor-args', 'youtube:player_client=default']
    return []


def build_auth_args(message):
    """Build authentication arguments from the message (passed by the extension)"""
    auth_method = message.get('authMethod', 'none')
    
    if auth_method == 'browser':
        browser = message.get('browser', 'chrome')
        return ['--cookies-from-browser', browser]
    elif auth_method == 'file':
        cookie_file = message.get('cookieFile', '')
        if cookie_file:
            return ['--cookies', cookie_file]
    
    return []


def fetch_formats(message):
    """Fetch available video, audio, and combined formats"""
    try:
        url = message['url']
        
        command = ['yt-dlp', '--no-playlist', '--dump-json']
        command.extend(build_extractor_args(url))
        command.extend(build_auth_args(message))
        command.append(url)
        
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
        combined_formats = []
        
        for f in formats:
            filesize = f.get('filesize') or f.get('filesize_approx', 0)
            size_mb = f"{filesize / (1024*1024):.1f}MB" if filesize else "N/A"
            
            has_video = f.get('vcodec') and f.get('vcodec') != 'none'
            has_audio = f.get('acodec') and f.get('acodec') != 'none'
            
            if has_video and not has_audio:
                # Video-only stream
                video_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A'),
                    'size': size_mb,
                    'type': 'video'
                })
            elif has_audio and not has_video:
                # Audio-only stream
                audio_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'abr': f.get('abr', 'N/A'),
                    'size': size_mb,
                    'type': 'audio'
                })
            elif has_video and has_audio:
                # Combined video+audio stream (common on Facebook)
                combined_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A'),
                    'size': size_mb,
                    'type': 'combined'
                })
        
        send_message({
            "success": True,
            "videoFormats": video_formats,
            "audioFormats": audio_formats,
            "combinedFormats": combined_formats
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
        
        # Add /best fallback for combined-format sites (e.g. Facebook)
        if is_facebook_url(url):
            format_str = f'{format_str}/best'
        
        command = [
            'yt-dlp',
            '--no-playlist',
            '-f', format_str,
            '-o', f'{save_dir}/%(title)s.%(ext)s',
            '--newline'
        ]
        
        # Add extractor-args only for YouTube URLs
        command.extend(build_extractor_args(url))
        
        # Add authentication
        command.extend(build_auth_args(message))
        
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
