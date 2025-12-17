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
    
    # Save transcript
    base_name = Path(audio_file).stem
    transcript_file = Path.home() / f"{base_name}_normal_whisper_transcript.txt"
    
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(result["text"])
    
    # Save detailed transcript with timestamps
    detailed_file = Path.home() / f"{base_name}_normal_whisper_detailed.txt"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"]
            f.write(f"[{start:.2f}s -> {end:.2f}s] {text}\n")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n✅ Transcription completed!")
    print(f"⏱️  Time taken: {duration:.2f} seconds")
    print(f"🌍 Language detected: {result['language']}")
    print(f"📄 Simple transcript saved to: {transcript_file}")
    print(f"📄 Detailed transcript saved to: {detailed_file}")
    
    # Display first few lines
    print("\n📝 First few lines of transcript:")
    print("-" * 50)
    lines = result["text"][:500] + "..." if len(result["text"]) > 500 else result["text"]
    print(lines)
    
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