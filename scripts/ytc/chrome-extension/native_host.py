#!/usr/bin/env python3
"""
Native messaging host for YTC Subtitle Extractor Chrome Extension
Handles yt-dlp execution and subtitle processing
"""

import sys
import json
import struct
import subprocess
import os
import re
import time


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


def parse_subtitle_time(time_str):
    """Convert subtitle timestamp to seconds (HH:MM:SS,mmm or HH:MM:SS.mmm)"""
    try:
        time_str = time_str.replace(',', '.')
        parts = time_str.split('.')
        time_part = parts[0]
        
        time_components = time_part.split(':')
        if len(time_components) == 3:
            hours, minutes, seconds = map(int, time_components)
            return hours * 3600 + minutes * 60 + seconds
        elif len(time_components) == 2:
            minutes, seconds = map(int, time_components)
            return minutes * 60 + seconds
        else:
            return int(time_components[0])
    except:
        return 0


def parse_time_input(time_str):
    """Convert time string to seconds. Accepts: '3062', '51:02', '1:30:45'"""
    if not time_str or not time_str.strip():
        return None
    
    time_str = time_str.strip()
    
    if time_str.isdigit():
        return int(time_str)
    
    if ':' in time_str:
        parts = time_str.split(':')
        try:
            if len(parts) == 2:  # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except ValueError:
            return None
    
    return None


def convert_to_txt(file_path, time_range=None):
    """Convert SRT/VTT to clean TXT with optional time filtering"""
    try:
        txt_path = os.path.splitext(file_path)[0] + ".txt"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        entries = []
        current_entry = {"start": 0, "end": 0, "text": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for timestamp line
            if "-->" in line:
                try:
                    time_parts = line.split("-->")
                    start_str = time_parts[0].strip()
                    end_str = time_parts[1].strip()
                    
                    current_entry["start"] = parse_subtitle_time(start_str)
                    current_entry["end"] = parse_subtitle_time(end_str)
                except:
                    continue
            elif re.fullmatch(r'\d+', line):
                # Subtitle index - save previous entry
                if current_entry["text"]:
                    entries.append(current_entry.copy())
                    current_entry = {"start": 0, "end": 0, "text": ""}
            elif not line.startswith("WEBVTT") and not line.startswith("Kind:") and not line.startswith("Language:"):
                # Subtitle text
                line = re.sub(r'<[^>]+>', '', line)
                line = line.strip()
                if line:
                    if current_entry["text"]:
                        current_entry["text"] += " " + line
                    else:
                        current_entry["text"] = line
        
        # Add last entry
        if current_entry["text"]:
            entries.append(current_entry)
        
        # Filter by time range if specified
        if time_range:
            start_sec, end_sec = time_range
            filtered_entries = []
            for entry in entries:
                if entry["end"] >= start_sec and entry["start"] <= end_sec:
                    filtered_entries.append(entry)
            entries = filtered_entries
        
        # Extract text and remove duplicates
        clean_lines = []
        for entry in entries:
            text = entry["text"]
            if not clean_lines or clean_lines[-1] != text:
                clean_lines.append(text)
        
        # Rolling fix for partial duplicates
        final_lines = []
        for line in clean_lines:
            if final_lines and line.startswith(final_lines[-1]):
                final_lines[-1] = line
            else:
                final_lines.append(line)

        # Create final text content
        txt_content = "\n".join(final_lines)
        
        # Write to file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        # Remove original file
        try:
            os.remove(file_path)
        except:
            pass
        
        return txt_content
    except Exception as e:
        send_message({"success": False, "error": f"Conversion error: {str(e)}"})
        return None


def process_subtitles(save_dir, format_type, time_range, start_time):
    """Process downloaded subtitles (convert to TXT if needed)"""
    txt_content = None
    try:
        for filename in os.listdir(save_dir):
            if filename.endswith(".srt") or filename.endswith(".vtt"):
                full_path = os.path.join(save_dir, filename)
                
                # Check if file was created after download started
                if os.path.getmtime(full_path) > start_time - 5:
                    if format_type == 'txt':
                        txt_content = convert_to_txt(full_path, time_range)
    except Exception as e:
        send_message({"success": False, "error": f"Processing error: {str(e)}"})
    
    return txt_content


def execute_download(message):
    """Execute yt-dlp command"""
    try:
        command = message['command']
        format_type = message.get('format', 'srt')
        copy_to_clipboard = message.get('copyToClipboard', False)
        use_timeline = message.get('useTimeline', False)
        start_time_str = message.get('startTime', '')
        end_time_str = message.get('endTime', '')
        save_dir = message.get('saveDir', '')
        
        # Parse time range
        time_range = None
        if use_timeline:
            start = parse_time_input(start_time_str)
            end = parse_time_input(end_time_str)
            time_range = (
                start if start is not None else 0,
                end if end is not None else float('inf')
            )
        
        # Record start time for file filtering
        download_start = time.time()
        
        # Execute yt-dlp
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
        
        # Process subtitles if needed
        txt_content = None
        if format_type == 'txt' or time_range:
            txt_content = process_subtitles(save_dir, format_type, time_range, download_start)
        
        # Copy to clipboard if requested
        clipboard_copied = False
        if copy_to_clipboard and format_type == 'txt' and txt_content:
            try:
                import pyperclip
                pyperclip.copy(txt_content)
                clipboard_copied = True
            except ImportError:
                # Fallback to Windows clip command
                try:
                    process = subprocess.Popen(
                        ['clip'],
                        stdin=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )
                    process.communicate(input=txt_content.encode('utf-16le'))
                    clipboard_copied = True
                except:
                    pass
        
        send_message({
            "success": True, 
            "message": "Subtitles extracted successfully",
            "clipboardCopied": clipboard_copied
        })
        
    except Exception as e:
        send_message({"success": False, "error": str(e)})


def main():
    """Main loop for native messaging"""
    while True:
        try:
            message = read_message()
            execute_download(message)
        except Exception as e:
            send_message({"success": False, "error": str(e)})
            sys.exit(1)


if __name__ == '__main__':
    main()
