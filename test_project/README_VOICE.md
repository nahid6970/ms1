# Voice Input App

A cyberpunk-themed voice input application using Python and PyQt6.

## Requirements

```bash
pip install PyQt6 SpeechRecognition pyaudio pyperclip pyautogui pynput
```

## Usage

```bash
python voice_input.py
```

## Features

- 🎤 Voice recording with Google Speech Recognition
- 🌐 Language toggle (English/Bengali)
- 📌 Pin window (Always on Top)
- ⚡ Auto-paste to active window
- 📋 Copy to clipboard
- 🔄 Restart button
- 💾 Settings saved to `voice_config.json`
- 🎨 Cyberpunk theme

## Controls

- **RECORD / Alt+H**: Start/stop voice recording (works globally)
- **COPY**: Copy output to clipboard
- **CLEAR**: Clear output text
- **RESTART**: Restart the application

## Language Support

- English (en-US)
- Bengali (bn-BD)

Language preference is saved automatically.
