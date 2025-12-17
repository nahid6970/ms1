# Whisper Transcription Guide

Complete guide for transcribing audio/video files using OpenAI's Whisper models locally and on Google Colab.

## What is Whisper?

Whisper is OpenAI's open-source automatic speech recognition (ASR) model that runs entirely offline. It supports 99 languages including excellent support for English and Bengali.

## Model Sizes & Performance

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| tiny | 39 MB | Fastest | Basic | Quick tests |
| base | 74 MB | Fast | Good | General use |
| small | 244 MB | Medium | Better | Balanced |
| medium | 769 MB | Slower | Very Good | High quality |
| large-v3 | 1550 MB | Slowest | **Best** | Production |

## Hardware Requirements

### Local Machine (Ryzen 5 3400G example)
- **CPU**: Any modern processor (4+ cores recommended)
- **RAM**: 4-8GB minimum, 16GB for large models
- **Storage**: 150MB-1.5GB per model
- **Time**: 15-25 minutes for 1 hour audio (large model)

### Google Colab (Free)
- **GPU**: Tesla T4 (when available)
- **Time**: 2-5 minutes for 1 hour audio with GPU
- **Limitations**: 12-hour sessions, 90-minute idle timeout

## Available Scripts

This repository includes two optimized transcription scripts:

### 1. Faster-Whisper Script (Recommended)
**File**: `faster_whisper_transcribe.py`

**Features**:
- 2-4x faster than normal Whisper
- Better GPU optimization
- Advanced quality settings (beam_size=5, best_of=5)
- Automatic device detection (GPU/CPU)
- Timestamp-included output

**Output**: `wipp_faster_whisper_transcript.txt`

### 2. Normal Whisper Script
**File**: `normal_whisper_transcribe.py`

**Features**:
- Standard OpenAI Whisper implementation
- More stable and widely tested
- Creates both simple and detailed transcripts
- Automatic device detection

**Output**: 
- `wipp_normal_whisper_transcript.txt` (simple)
- `wipp_normal_whisper_detailed.txt` (with timestamps)

## How to Use in Google Colab

### Step 1: Setup
1. Open [Google Colab](https://colab.research.google.com)
2. Enable GPU: Runtime → Change runtime type → Hardware accelerator → GPU
3. Create a new notebook

### Step 2: Upload Files
1. Upload your audio/video file named exactly `wipp.mp3` or `wipp.mp4`
2. Upload one of the transcription scripts

### Step 3: Run Transcription
```python
# For faster-whisper (recommended)
exec(open('faster_whisper_transcribe.py').read())

# OR for normal whisper
exec(open('normal_whisper_transcribe.py').read())
```

### Step 4: Download Results
The script will automatically save transcripts to your Colab home directory. Download them before your session ends.

## Supported File Formats

Both scripts automatically detect and work with:
- `.mp3` (audio)
- `.mp4` (video)
- `.wav` (audio)
- `.m4a` (audio)

## Language Support

### Excellent Support
- English (`en`)
- Bengali (`bn`)

### Auto-Detection
Both scripts automatically detect the language. You can also force a specific language by modifying the script:

```python
# Force Bengali
segments, info = model.transcribe(audio_file, language="bn")

# Force English
segments, info = model.transcribe(audio_file, language="en")
```

## Local Installation (Alternative)

If you want to run locally instead of Colab:

### Install Faster-Whisper
```bash
pip install faster-whisper
```

### Install Normal Whisper
```bash
pip install openai-whisper
```

### Command Line Usage (Normal Whisper only)
```bash
# Basic transcription
whisper audio.mp3 --model large-v3

# Specify language
whisper audio.mp3 --model large-v3 --language bn

# Custom output directory
whisper audio.mp3 --model large-v3 --output_dir ./transcripts
```

## Performance Comparison

### 1-Hour Audio Transcription Times

| Setup | Faster-Whisper | Normal Whisper |
|-------|----------------|----------------|
| Colab GPU | 2-3 minutes | 4-6 minutes |
| Colab CPU | 8-12 minutes | 15-20 minutes |
| Local Ryzen 5 3400G | 10-15 minutes | 15-25 minutes |

## Tips for Best Results

### Audio Quality
- Use clear, high-quality audio
- Minimize background noise
- Single speaker works better than multiple speakers

### Model Selection
- Use `large-v3` for best accuracy
- Use `medium` if speed is more important
- Use `base` for quick tests

### Google Colab Tips
- Enable GPU for 4-8x speed improvement
- Process files in batches during free tier limits
- Download results immediately (sessions expire)
- Upload files at start of session

## Troubleshooting

### Common Issues

**"FP16 is not supported on CPU"**
- This is just a warning, not an error
- Whisper automatically falls back to FP32
- Enable GPU in Colab to use FP16

**"No wipp.mp3 or wipp.mp4 found"**
- Ensure file is named exactly `wipp.mp3` or `wipp.mp4`
- Upload to the home directory (default in Colab)
- Check file extension matches

**Session Disconnected**
- Colab free tier has 90-minute idle timeout
- Keep browser tab active during transcription
- Download results immediately

**Out of Memory**
- Use smaller model (`medium` instead of `large-v3`)
- Restart Colab session
- Process shorter audio segments

## Cost Comparison

| Method | Cost | Speed | Quality |
|--------|------|-------|---------|
| Google Colab Free | Free | Fast (with GPU) | Excellent |
| Local Processing | Free | Medium | Excellent |
| Cloud APIs | $0.006/minute | Very Fast | Good |

## Advanced Usage

### Batch Processing Multiple Files
Modify the scripts to process multiple files by changing the `find_wipp_file()` function to return a list of files.

### Custom Output Formats
Both scripts can be modified to output:
- SRT subtitles
- VTT subtitles  
- JSON with detailed metadata
- Word-level timestamps

### Integration with Other Tools
- Use with video editing software for subtitles
- Integrate with translation services
- Combine with speaker diarization tools

## Conclusion

For most users transcribing English and Bengali content:

1. **Use Google Colab** with GPU enabled
2. **Choose faster-whisper script** for best performance
3. **Use large-v3 model** for highest accuracy
4. **Process files in batches** to maximize free tier usage

The combination of Whisper's accuracy and Colab's free GPU access makes this an excellent solution for offline transcription needs.