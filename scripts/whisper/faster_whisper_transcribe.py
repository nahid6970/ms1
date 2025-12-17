#!/usr/bin/env python3
"""
Faster-Whisper Transcription Script for Google Colab
Automatically finds wipp.mp3 or wipp.mp4 in home directory and transcribes it
"""

import os
import glob
import time
from pathlib import Path

# Install required packages
print("Installing faster-whisper...")
os.system("pip install -q faster-whisper")

print("Importing libraries...")
from faster_whisper import WhisperModel

def find_wipp_file():
    """Find wipp.mp3 or wipp.mp4 in home directory"""
    home_dir = Path.home()
    
    # Look for both mp3 and mp4 files
    patterns = ['wipp.mp3', 'wipp.mp4', 'wipp.wav', 'wipp.m4a']
    
    for pattern in patterns:
        file_path = home_dir / pattern
        if file_path.exists():
            print(f"Found file: {file_path}")
            return str(file_path)
    
    print("No wipp.mp3 or wipp.mp4 found in home directory")
    print(f"Looking in: {home_dir}")
    return None

def transcribe_with_faster_whisper(audio_file):
    """Transcribe using faster-whisper with best settings"""
    print("Loading Faster-Whisper large-v3 model...")
    
    # Use GPU if available, otherwise CPU
    device = "cuda" if os.system("nvidia-smi > /dev/null 2>&1") == 0 else "cpu"
    compute_type = "float16" if device == "cuda" else "float32"
    
    print(f"Using device: {device}")
    
    model = WhisperModel(
        "large-v3", 
        device=device, 
        compute_type=compute_type
    )
    
    print("Starting transcription...")
    start_time = time.time()
    
    # Transcribe with best quality settings
    segments, info = model.transcribe(
        audio_file,
        beam_size=5,
        best_of=5,
        temperature=0.0,
        language=None  # Auto-detect
    )
    
    # Save transcript
    base_name = Path(audio_file).stem
    transcript_file = Path.home() / f"{base_name}_faster_whisper_transcript.txt"
    
    with open(transcript_file, 'w', encoding='utf-8') as f:
        for segment in segments:
            f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}\n")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Transcription completed!")
    print(f"⏱️  Time taken: {duration:.2f} seconds")
    print(f"🌍 Language detected: {info.language}")
    print(f"📄 Transcript saved to: {transcript_file}")
    
    # Display first few lines
    print("\n📝 First few lines of transcript:")
    print("-" * 50)
    with open(transcript_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:5]
        for line in lines:
            print(line.strip())
    
    return transcript_file

def main():
    print("🚀 Faster-Whisper Transcription Script")
    print("=" * 50)
    
    # Find the audio/video file
    audio_file = find_wipp_file()
    if not audio_file:
        print("❌ Please upload wipp.mp3 or wipp.mp4 to the home directory")
        return
    
    # Transcribe
    try:
        transcript_file = transcribe_with_faster_whisper(audio_file)
        print(f"\n🎉 All done! Check your transcript at: {transcript_file}")
    except Exception as e:
        print(f"❌ Error during transcription: {e}")

if __name__ == "__main__":
    main()