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
    """Check if URL is a Facebook video / group / reel / post URL"""
    facebook_patterns = [
        r'^(https?://)?(www\.)?facebook\.com/',
        r'^(https?://)?(www\.)?fb\.watch/',
        r'^(https?://)?(www\.)?fb\.com/',
        r'^(https?://)?m\.facebook\.com/',
        r'^(https?://)?web\.facebook\.com/',
        r'^(https?://)?(www\.)?facebook\.com/groups/',
        r'^(https?://)?(www\.)?facebook\.com/.*/videos/',
        r'^(https?://)?(www\.)?facebook\.com/.*/posts/',
        r'^(https?://)?(www\.)?facebook\.com/reel/',
        r'^(https?://)?(www\.)?facebook\.com/watch',
    ]
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in facebook_patterns)


def is_facebook_group_url(url):
    """Detect private/public Facebook group content (needs auth more often)"""
    return bool(re.search(
        r'facebook\.com/groups/|facebook\.com/.*/permalink|facebook\.com/.*/posts/',
        url, re.IGNORECASE
    ))


def _impersonate_available():
    """Return True if yt-dlp has a usable Chrome impersonate target (needs curl_cffi)."""
    try:
        result = subprocess.run(
            ['yt-dlp', '--list-impersonate-targets'],
            capture_output=True,
            text=True,
            timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        out = (result.stdout or '') + (result.stderr or '')
        # Look for a Chrome target that is NOT marked unavailable
        for line in out.splitlines():
            lower = line.lower()
            if 'chrome' in lower and 'curl_cffi' in lower and 'not available' not in lower:
                return True
    except Exception:
        pass
    return False


def build_extractor_args(url):
    """Build extractor-args for YouTube and Facebook.

    Facebook private/group videos often need --impersonate (curl_cffi)
    in addition to cookies, otherwise yt-dlp gets "Cannot parse data".
    """
    args = []
    if is_youtube_url(url):
        args.extend(['--extractor-args', 'youtube:player_client=default'])
    if is_facebook_url(url) and _impersonate_available():
        # chrome-99 is the target that most often works with Facebook + cookies
        args.extend(['--impersonate', 'chrome-99'])
    return args


def build_auth_args(message):
    """Build authentication arguments from the message (passed by the extension).

    For private Facebook groups, cookies are required.
    Prefer Firefox or a cookies.txt file — Chrome's cookie store is often
    unreadable by yt-dlp due to app-bound encryption (since ~2024).
    """
    auth_method = message.get('authMethod', 'none')
    
    if auth_method == 'browser':
        browser = message.get('browser', 'chrome')
        # Firefox is more reliable for Facebook private content
        return ['--cookies-from-browser', browser]
    elif auth_method == 'file':
        cookie_file = message.get('cookieFile', '')
        if cookie_file and os.path.isfile(cookie_file):
            return ['--cookies', cookie_file]
        # Fall through so caller sees a clear error later
    
    return []


def fetch_formats(message):
    """Fetch available video, audio, and combined formats"""
    try:
        url = message['url']
        auth_method = message.get('authMethod', 'none')
        
        # Private Facebook groups almost always need auth
        if is_facebook_group_url(url) and auth_method == 'none':
            send_message({
                "success": False,
                "error": (
                    "This looks like a Facebook group/post URL. Private group videos "
                    "require authentication.\n\n"
                    "Go to Settings → Authentication → choose:\n"
                    "• Browser Cookies (prefer Firefox — Chrome cookies often fail)\n"
                    "• or Cookie File (export with 'Get cookies.txt LOCALLY')\n\n"
                    "Then try FETCH FORMATS again."
                )
            })
            return
        
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
            err = (stderr or '').strip() or 'Unknown yt-dlp error'
            lower = err.lower()
            # Only show Facebook-specific hints for Facebook URLs
            if is_facebook_url(url) and any(x in lower for x in (
                'login required', 'only available for registered',
                'cannot parse data', "content isn't available",
                'please log in', 'cookies', 'impersonate'
            )):
                err = (
                    f"{err}\n\n"
                    "Tip for private Facebook groups:\n"
                    "1. Install browser impersonation support:\n"
                    "   pip install -U \"yt-dlp[default,curl-cffi]\"\n"
                    "2. Use Cookie File (export while logged into Facebook) or Firefox cookies\n"
                    "3. Update yt-dlp: yt-dlp -U\n"
                    "4. Confirm: yt-dlp --list-impersonate-targets  (Chrome should NOT say 'not available')"
                )
            elif is_youtube_url(url) and any(x in lower for x in (
                'sign in', 'bot', '429', 'too many requests', 'cookies'
            )):
                err = (
                    f"{err}\n\n"
                    "Tip for YouTube bot detection:\n"
                    "1. In Settings → Authentication → Browser Cookies → Chrome or Firefox\n"
                    "2. Make sure you are logged into YouTube in that browser\n"
                    "3. If rate-limited (429), wait a few minutes and try again"
                )
            send_message({"success": False, "error": err})
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
                video_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'resolution': f.get('resolution', 'N/A'),
                    'size': size_mb,
                    'type': 'video'
                })
            elif has_audio and not has_video:
                audio_formats.append({
                    'id': f['format_id'],
                    'ext': f['ext'],
                    'abr': f.get('abr', 'N/A'),
                    'size': size_mb,
                    'type': 'audio'
                })
            elif has_video and has_audio:
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
        
        # Facebook (especially groups) often only exposes combined streams
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
