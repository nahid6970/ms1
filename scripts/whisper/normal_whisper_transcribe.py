#!/usr/bin/env python3
"""
Normal Whisper Transcription Script for Google Colab
Automatically finds wipp.mp3 or wipp.mp4 in home directory and transcribes it
"""

import os
import glob
import time
from pathlib import Path

# Install required packages
print("Installing OpenAI Whisper...")
os.system("pip install -q openai-whisper")

print("Importing libraries...")
import whisper

def find_wipp_file():
    """Find wipp.mp3 or wipp.mp4 in multiple locations including Google Drive"""
    # Check if Google Drive is already mounted
    drive_mounted = Path('/content/drive/MyDrive').exists()
    
    # Search locations in order of preference
    search_dirs = [Path.cwd()]  # Current directory first
    
    if drive_mounted:
        # Add common Google Drive locations
        drive_locations = [
            Path('/content/drive/MyDrive'),
            Path('/content/drive/MyDrive/Colab Notebooks'),
            Path('/content/drive/MyDrive/Videos'),
            Path('/content/drive/MyDrive/Audio'),
        ]
        search_dirs.extend(drive_locations)
    
    # Add home directory as fallback
    search_dirs.append(Path.home())
    
    # Look for audio/video files
    patterns = ['wipp.mp3', 'wipp.mp4', 'wipp.wav', 'wipp.m4a']
    
    print("Searching for wipp files...")
    for search_dir in search_dirs:
        if search_dir.exists():
            print(f"Checking: {search_dir}")
            for pattern in patterns:
                file_path = search_dir / pattern
                if file_path.exists():
                    file_size = file_path.stat().st_size / (1024*1024)  # MB
                    print(f"✅ Found file: {file_path}")
                    print(f"📏 File size: {file_size:.1f} MB")
                    return str(file_path)
    
    print("❌ No wipp.mp3 or wipp.mp4 found in any location")
    print("📁 Searched locations:")
    for d in search_dirs:
        print(f"   - {d}")
    print("\n💡 Tips:")
    print("   - Upload your file to Google Drive")
    print("   - Name it 'wipp.mp4' or 'wipp.mp3'")
    print("   - Place it in MyDrive root or MyDrive/Videos folder")
    return None

def transcribe_with_normal_whisper(audio_file):
    """Transcribe using normal whisper"""
    print("Loading Normal Whisper large-v3 model...")
    
    # Use GPU if available
    device = "cuda" if os.system("nvidia-smi > /dev/null 2>&1") == 0 else "cpu"
    print(f"Using device: {device}")
    
    model = whisper.load_model("large-v3", device=device)
    
    print("Starting transcription...")
    start_time = time.time()
    
    # Transcribe
    result = model.transcribe(
        audio_file,
        language=None,  # Auto-detect
        task="transcribe"
    )
    
    # Save transcript in same directory as input file
    audio_path = Path(audio_file)
    base_name = audio_path.stem
    transcript_file = audio_path.parent / f"{base_name}_normal_whisper_transcript.txt"
    
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(result["text"])
    
    # Save detailed transcript with timestamps
    detailed_file = audio_path.parent / f"{base_name}_normal_whisper_detailed.txt"
    total_segments = len(result["segments"])
    print(f"Processing {total_segments} segments...")
    
    with open(detailed_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result["segments"]):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"[{start:.2f}s -> {end:.2f}s] {text}\n")
            if (i + 1) % 50 == 0:  # Progress update every 50 segments
                print(f"Processed {i + 1}/{total_segments} segments...")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Transcription completed!")
    print(f"⏱️  Time taken: {duration:.2f} seconds")
    print(f"🌍 Language detected: {result['language']}")
    print(f"📊 Total segments: {total_segments}")
    print(f"📄 Simple transcript saved to: {transcript_file}")
    print(f"📄 Detailed transcript saved to: {detailed_file}")
    
    # Check file sizes
    simple_size = transcript_file.stat().st_size
    detailed_size = detailed_file.stat().st_size
    
    with open(detailed_file, 'r', encoding='utf-8') as f:
        detailed_lines = f.readlines()
        total_lines = len(detailed_lines)
    
    print(f"📏 Simple file size: {simple_size:,} bytes")
    print(f"📏 Detailed file size: {detailed_size:,} bytes")
    print(f"📝 Total lines in detailed: {total_lines}")
    
    # Display first and last few lines from detailed transcript
    print("\n📝 First 10 lines of detailed transcript:")
    print("-" * 50)
    for line in detailed_lines[:10]:
        print(line.strip())
    
    if total_lines > 20:
        print("\n📝 Last 5 lines of detailed transcript:")
        print("-" * 50)
        for line in detailed_lines[-5:]:
            print(line.strip())
    
    return transcript_file, detailed_file

def main():
    print("🚀 Normal Whisper Transcription Script")
    print("=" * 50)
    
    # Find the audio/video file
    audio_file = find_wipp_file()
    if not audio_file:
        print("❌ Please upload wipp.mp3 or wipp.mp4 to the home directory")
        return
    
    # Transcribe
    try:
        transcript_files = transcribe_with_normal_whisper(audio_file)
        print(f"\n🎉 All done! Check your transcripts:")
        for file in transcript_files:
            print(f"   📄 {file}")
    except Exception as e:
        print(f"❌ Error during transcription: {e}")

if __name__ == "__main__":
    main()