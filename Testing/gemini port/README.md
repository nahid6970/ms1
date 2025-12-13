# Gemini CLI Dashboard

A beautiful web interface for interacting with Google's Gemini AI through the command line.

## Features

- 📊 Real-time token usage tracking
- 💬 Interactive chat interface
- 📈 Session statistics and analytics
- ⚙️ Model selection and parameter controls
- 📜 Chat history management
- 🔧 Export conversations
- 🎨 Modern, responsive UI

## Prerequisites

1. **Python 3.7+** installed
2. **Gemini CLI** installed and configured

### Installing Gemini CLI

**Option 1: NPM (Recommended)**
```bash
npm install -g @google/gemini-cli
```

Then configure your API key:
```bash
gemini config set apiKey YOUR_API_KEY
```

**Option 2: Python**
```bash
pip install google-generativeai
```

Then set environment variable:
```bash
set GOOGLE_API_KEY=your_api_key_here
```

## Quick Start

### Option 1: Using the Launcher (Windows)

Simply double-click `start.bat` - it will:
- Check dependencies
- Install missing packages
- Start the server
- Open your browser automatically

### Option 2: Manual Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python gemini_server.py
```

3. Open your browser to:
```
http://localhost:4785
```

## Usage

1. **Test Connection**: Click "Test Connection" to verify Gemini CLI is working
2. **Select Model**: Choose from available Gemini models
3. **Adjust Settings**: Set temperature and max tokens
4. **Start Chatting**: Type your message and press Enter (Shift+Enter for new line)
5. **Monitor Stats**: Watch token usage and response times in real-time

## Configuration

### Custom CLI Command

If your Gemini CLI uses a different command, edit `gemini_server.py` line ~50:

```python
commands = [
    ['your-custom-command', 'args', message],
    # Add your command format here
]
```

### Port Configuration

To change the port (default 4785), edit the last line in `gemini_server.py`:

```python
app.run(debug=True, port=4785)  # Change port here
```

## Troubleshooting

### "Gemini CLI not found"
- Make sure you've installed: `pip install google-generativeai`
- Verify it works in terminal: `gemini --version`

### "Cannot connect to server"
- Ensure `gemini_server.py` is running
- Check if port 5000 is available
- Look for error messages in the terminal

### "API key not configured"
- Set environment variable: `set GOOGLE_API_KEY=your_key`
- Or configure through Gemini CLI setup

## API Endpoints

The Flask server provides these endpoints:

- `POST /api/chat` - Send message to Gemini
- `GET /api/stats` - Get session statistics
- `POST /api/reset` - Reset statistics
- `GET /api/test` - Test CLI connection

## License

MIT License - feel free to modify and use as needed!

## Tips

- Use keyboard shortcuts: Enter to send, Shift+Enter for new line
- Export important conversations using the Export button
- Monitor token usage to stay within limits
- Adjust temperature for more creative (higher) or focused (lower) responses
