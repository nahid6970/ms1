from flask import Flask, render_template_string, Response, request, jsonify
import pyaudio
import threading
import queue
import time
import json

app = Flask(__name__)

# Global variables
audio_queue = queue.Queue()
is_streaming = False
audio_settings = {
    'sample_rate': 44100,
    'channels': 2,
    'chunk_size': 1024,
    'format': pyaudio.paInt16,
    'bitrate': 128
}
stream_thread = None
audio_stream = None

def audio_callback():
    """Audio recording callback function"""
    global is_streaming, audio_queue
    
    p = pyaudio.PyAudio()
    
    # Get default input device
    try:
        stream = p.open(
            format=audio_settings['format'],
            channels=audio_settings['channels'],
            rate=audio_settings['sample_rate'],
            input=True,
            frames_per_buffer=audio_settings['chunk_size']
        )
        
        while is_streaming:
            try:
                data = stream.read(audio_settings['chunk_size'], exception_on_overflow=False)
                if not audio_queue.full():
                    audio_queue.put(data)
                else:
                    # Clear old data if queue is full
                    try:
                        audio_queue.get_nowait()
                        audio_queue.put(data)
                    except queue.Empty:
                        pass
            except Exception as e:
                print(f"Audio read error: {e}")
                break
                
    except Exception as e:
        print(f"Audio device error: {e}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

def generate_audio():
    """Generator function for audio streaming"""
    global audio_queue
    
    while is_streaming:
        try:
            # Get audio data with timeout
            data = audio_queue.get(timeout=1.0)
            yield data
        except queue.Empty:
            # Send silence if no audio data
            silence = b'\x00' * (audio_settings['chunk_size'] * audio_settings['channels'] * 2)
            yield silence
        except Exception as e:
            print(f"Audio generation error: {e}")
            break

@app.route('/')
def index():
    """Main page with audio controls"""
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Audio Streamer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 2.5em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .control-section {
            margin: 25px 0;
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            background: #f8f9fa;
        }
        
        .control-section h3 {
            color: #444;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 120px;
        }
        
        .start-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
        }
        
        .start-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        .stop-btn {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            color: white;
        }
        
        .hear-btn {
            background: linear-gradient(45deg, #2196F3, #1976D2);
            color: white;
        }
        
        .hear-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
        }
        
        .hear-btn.playing {
            background: linear-gradient(45deg, #FF9800, #F57C00);
        }
        
        .stop-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4);
        }
        
        .setting-group {
            display: flex;
            align-items: center;
            margin: 15px 0;
            gap: 15px;
        }
        
        .setting-group label {
            min-width: 120px;
            font-weight: 600;
            color: #555;
        }
        
        select, input[type="range"] {
            flex: 1;
            padding: 8px 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        
        select:focus, input:focus {
            border-color: #667eea;
            outline: none;
        }
        
        input[type="range"] {
            height: 6px;
            background: #ddd;
            border-radius: 3px;
            padding: 0;
        }
        
        .status {
            text-align: center;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: 600;
            font-size: 18px;
        }
        
        .status.streaming {
            background: linear-gradient(45deg, #4CAF50, #81C784);
            color: white;
        }
        
        .status.stopped {
            background: linear-gradient(45deg, #f44336, #e57373);
            color: white;
        }
        
        .audio-controls {
            text-align: center;
            margin: 20px 0;
        }
        
        audio {
            width: 100%;
            max-width: 400px;
            margin: 10px 0;
        }
        
        .stream-url {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 8px;
            font-family: monospace;
            word-break: break-all;
            margin: 10px 0;
        }
        
        .quality-indicator {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        
        .quality-low { background: #ffeb3b; color: #333; }
        .quality-medium { background: #ff9800; color: white; }
        .quality-high { background: #4caf50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 PC Audio Streamer</h1>
        
        <div id="status" class="status stopped">
            Stream Stopped
        </div>
        
        <div class="control-section">
            <h3>🎛️ Stream Controls</h3>
            <div class="button-group">
                <button class="start-btn" onclick="startStream()">Start Streaming</button>
                <button class="stop-btn" onclick="stopStream()">Stop Streaming</button>
                <button class="hear-btn" onclick="toggleAudio()" id="hearBtn" style="display: none;">🎧 Hear Stream</button>
            </div>
            
            <div class="audio-controls">
                <audio id="audioPlayer" controls style="display: none;">
                    <source id="audioSource" src="" type="audio/wav">
                    Your browser does not support audio streaming.
                </audio>
                <div class="stream-url" id="streamUrl" style="display: none;">
                    Stream URL: <span id="urlText"></span>
                </div>
            </div>
        </div>
        
        <div class="control-section">
            <h3>⚙️ Audio Settings</h3>
            
            <div class="setting-group">
                <label for="sampleRate">Sample Rate:</label>
                <select id="sampleRate" onchange="updateSettings()">
                    <option value="22050">22.05 kHz (Low)</option>
                    <option value="44100" selected>44.1 kHz (CD Quality)</option>
                    <option value="48000">48 kHz (Professional)</option>
                </select>
                <span class="quality-indicator quality-medium" id="sampleQuality">Medium</span>
            </div>
            
            <div class="setting-group">
                <label for="bitrate">Bitrate (kbps):</label>
                <input type="range" id="bitrate" min="64" max="320" value="128" step="32" onchange="updateBitrate()">
                <span id="bitrateValue">128 kbps</span>
                <span class="quality-indicator quality-medium" id="bitrateQuality">Medium</span>
            </div>
            
            <div class="setting-group">
                <label for="channels">Channels:</label>
                <select id="channels" onchange="updateSettings()">
                    <option value="1">Mono</option>
                    <option value="2" selected>Stereo</option>
                </select>
            </div>
            
            <div class="setting-group">
                <label for="chunkSize">Buffer Size:</label>
                <select id="chunkSize" onchange="updateSettings()">
                    <option value="512">512 (Low Latency)</option>
                    <option value="1024" selected>1024 (Balanced)</option>
                    <option value="2048">2048 (High Quality)</option>
                </select>
            </div>
        </div>
        
        <div class="control-section">
            <h3>📱 Connection Info</h3>
            <p><strong>Server Port:</strong> 5017</p>
            <p><strong>Stream Endpoint:</strong> /audio_stream</p>
            <p><strong>Control Interface:</strong> This page</p>
            <p><strong>Android Access:</strong> Use your PC's IP address with port 5017</p>
        </div>
    </div>

    <script>
        let isStreaming = false;
        
        function updateStatus(streaming) {
            const status = document.getElementById('status');
            const audioPlayer = document.getElementById('audioPlayer');
            const streamUrl = document.getElementById('streamUrl');
            const urlText = document.getElementById('urlText');
            const hearBtn = document.getElementById('hearBtn');
            
            isStreaming = streaming;
            
            if (streaming) {
                status.textContent = 'Stream Active 🔴';
                status.className = 'status streaming';
                
                // Show hear button and stream URL
                const streamUrlPath = window.location.origin + '/audio_stream';
                document.getElementById('audioSource').src = streamUrlPath;
                urlText.textContent = streamUrlPath;
                hearBtn.style.display = 'inline-block';
                streamUrl.style.display = 'block';
                audioPlayer.load();
            } else {
                status.textContent = 'Stream Stopped ⏹️';
                status.className = 'status stopped';
                hearBtn.style.display = 'none';
                streamUrl.style.display = 'none';
                audioPlayer.pause();
                hearBtn.textContent = '🎧 Hear Stream';
                hearBtn.className = 'hear-btn';
            }
        }
        
        function toggleAudio() {
            const audioPlayer = document.getElementById('audioPlayer');
            const hearBtn = document.getElementById('hearBtn');
            
            if (audioPlayer.paused) {
                // Force reload the audio source to get fresh stream
                const streamUrlPath = window.location.origin + '/audio_stream?t=' + Date.now();
                document.getElementById('audioSource').src = streamUrlPath;
                audioPlayer.load();
                
                audioPlayer.play().then(() => {
                    hearBtn.textContent = '🔇 Stop Hearing';
                    hearBtn.className = 'hear-btn playing';
                }).catch(error => {
                    console.error('Error playing audio:', error);
                    alert('Error playing audio. Try refreshing the page or check if your browser supports audio streaming.');
                });
            } else {
                audioPlayer.pause();
                hearBtn.textContent = '🎧 Hear Stream';
                hearBtn.className = 'hear-btn';
            }
        }
        
        function startStream() {
            fetch('/start_stream', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'started') {
                        updateStatus(true);
                    } else {
                        alert('Failed to start stream: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error starting stream');
                });
        }
        
        function stopStream() {
            fetch('/stop_stream', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    updateStatus(false);
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }
        
        function updateSettings() {
            const settings = {
                sample_rate: parseInt(document.getElementById('sampleRate').value),
                channels: parseInt(document.getElementById('channels').value),
                chunk_size: parseInt(document.getElementById('chunkSize').value),
                bitrate: parseInt(document.getElementById('bitrate').value)
            };
            
            fetch('/update_settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Settings updated:', data);
                updateQualityIndicators();
            })
            .catch(error => {
                console.error('Error updating settings:', error);
            });
        }
        
        function updateBitrate() {
            const bitrate = document.getElementById('bitrate').value;
            document.getElementById('bitrateValue').textContent = bitrate + ' kbps';
            updateSettings();
        }
        
        function updateQualityIndicators() {
            const sampleRate = parseInt(document.getElementById('sampleRate').value);
            const bitrate = parseInt(document.getElementById('bitrate').value);
            
            // Update sample rate quality indicator
            const sampleQuality = document.getElementById('sampleQuality');
            if (sampleRate <= 22050) {
                sampleQuality.textContent = 'Low';
                sampleQuality.className = 'quality-indicator quality-low';
            } else if (sampleRate <= 44100) {
                sampleQuality.textContent = 'Medium';
                sampleQuality.className = 'quality-indicator quality-medium';
            } else {
                sampleQuality.textContent = 'High';
                sampleQuality.className = 'quality-indicator quality-high';
            }
            
            // Update bitrate quality indicator
            const bitrateQuality = document.getElementById('bitrateQuality');
            if (bitrate <= 96) {
                bitrateQuality.textContent = 'Low';
                bitrateQuality.className = 'quality-indicator quality-low';
            } else if (bitrate <= 192) {
                bitrateQuality.textContent = 'Medium';
                bitrateQuality.className = 'quality-indicator quality-medium';
            } else {
                bitrateQuality.textContent = 'High';
                bitrateQuality.className = 'quality-indicator quality-high';
            }
        }
        
        // Check stream status on page load
        window.onload = function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    updateStatus(data.streaming);
                    updateQualityIndicators();
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                });
        };
        
        // Auto-refresh status every 5 seconds
        setInterval(function() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    if (data.streaming !== isStreaming) {
                        updateStatus(data.streaming);
                    }
                })
                .catch(error => {
                    console.error('Error checking status:', error);
                });
        }, 5000);
    </script>
</body>
</html>
    """
    return render_template_string(html_template)

@app.route('/start_stream', methods=['POST'])
def start_stream():
    """Start audio streaming"""
    global is_streaming, stream_thread
    
    if is_streaming:
        return jsonify({'status': 'already_running', 'message': 'Stream is already active'})
    
    try:
        is_streaming = True
        stream_thread = threading.Thread(target=audio_callback, daemon=True)
        stream_thread.start()
        return jsonify({'status': 'started', 'message': 'Audio streaming started'})
    except Exception as e:
        is_streaming = False
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    """Stop audio streaming"""
    global is_streaming
    
    is_streaming = False
    
    # Clear the audio queue
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break
    
    return jsonify({'status': 'stopped', 'message': 'Audio streaming stopped'})

@app.route('/audio_stream')
def audio_stream():
    """Stream audio data with proper WAV headers"""
    if not is_streaming:
        return Response("Stream not active", status=404)
    
    def generate_wav_stream():
        # WAV header for streaming
        def create_wav_header():
            sample_rate = audio_settings['sample_rate']
            channels = audio_settings['channels']
            bits_per_sample = 16
            
            # WAV header (44 bytes)
            header = b'RIFF'
            header += b'\xff\xff\xff\xff'  # File size (placeholder)
            header += b'WAVE'
            header += b'fmt '
            header += (16).to_bytes(4, 'little')  # Subchunk1Size
            header += (1).to_bytes(2, 'little')   # AudioFormat (PCM)
            header += channels.to_bytes(2, 'little')
            header += sample_rate.to_bytes(4, 'little')
            header += (sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little')  # ByteRate
            header += (channels * bits_per_sample // 8).to_bytes(2, 'little')  # BlockAlign
            header += bits_per_sample.to_bytes(2, 'little')
            header += b'data'
            header += b'\xff\xff\xff\xff'  # Subchunk2Size (placeholder)
            
            return header
        
        # Send WAV header first
        yield create_wav_header()
        
        # Stream audio data
        for chunk in generate_audio():
            if chunk:
                yield chunk
    
    return Response(
        generate_wav_stream(),
        mimetype='audio/wav',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'audio/wav',
            'Accept-Ranges': 'none'
        }
    )

@app.route('/status')
def get_status():
    """Get current streaming status and settings"""
    return jsonify({
        'streaming': is_streaming,
        'settings': audio_settings
    })

@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update audio settings"""
    global audio_settings
    
    try:
        new_settings = request.get_json()
        
        # Validate and update settings
        if 'sample_rate' in new_settings:
            audio_settings['sample_rate'] = new_settings['sample_rate']
        if 'channels' in new_settings:
            audio_settings['channels'] = new_settings['channels']
        if 'chunk_size' in new_settings:
            audio_settings['chunk_size'] = new_settings['chunk_size']
        if 'bitrate' in new_settings:
            audio_settings['bitrate'] = new_settings['bitrate']
        
        return jsonify({'status': 'updated', 'settings': audio_settings})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    print("PC Audio Streamer Server")
    print("=" * 40)
    print(f"Starting server on port 5017...")
    print(f"Access the control panel at: http://localhost:5017")
    print(f"Audio stream endpoint: http://localhost:5017/audio_stream")
    print(f"For Android access, use your PC's IP address instead of localhost")
    print("=" * 40)
    
    # Allow connections from any IP address
    app.run(host='0.0.0.0', port=5017, debug=False, threaded=True)