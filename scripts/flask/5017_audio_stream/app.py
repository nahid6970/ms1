from flask import Flask, render_template, Response, request, jsonify
import pyaudio
import threading
import queue
import time
import json
import subprocess
import sys

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
virtual_cable_available = False

def check_virtual_cable():
    """Check if VB-Audio Virtual Cable is installed"""
    global virtual_cable_available
    p = pyaudio.PyAudio()
    
    try:
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            device_name = device_info['name'].lower()
            
            if ('cable' in device_name and 'output' in device_name) or 'virtual' in device_name:
                if device_info['maxInputChannels'] > 0:
                    virtual_cable_available = True
                    print(f"Virtual audio device found: {device_info['name']}")
                    break
    except Exception as e:
        print(f"Error checking for virtual cable: {e}")
    finally:
        p.terminate()
    
    return virtual_cable_available

def setup_system_audio_capture():
    """Setup system to route audio through virtual cable"""
    if not virtual_cable_available:
        return False
    
    try:
        # This would require additional Windows API calls to automatically
        # set the default audio device to virtual cable
        # For now, we'll provide instructions to the user
        return True
    except Exception as e:
        print(f"Error setting up system audio: {e}")
        return False

def get_virtual_audio_device():
    """Get the virtual audio device for recording"""
    p = pyaudio.PyAudio()
    
    try:
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            device_name = device_info['name'].lower()
            
            # Look for virtual cable output (which we use as input)
            if (('cable' in device_name and 'output' in device_name) or 
                ('virtual' in device_name and device_info['maxInputChannels'] > 0)):
                print(f"Using virtual device: {device_info['name']}")
                return i
                
    except Exception as e:
        print(f"Error finding virtual device: {e}")
    finally:
        p.terminate()
    
    return None

def audio_callback():
    """Audio recording callback function using virtual audio device"""
    global is_streaming, audio_queue
    
    p = pyaudio.PyAudio()
    
    # Get virtual audio device
    device_index = get_virtual_audio_device()
    
    if device_index is None:
        print("No virtual audio device found!")
        return
    
    try:
        device_info = p.get_device_info_by_index(device_index)
        print(f"Recording from: {device_info['name']}")
        
        # Use device's native settings
        channels = min(audio_settings['channels'], device_info['maxInputChannels'])
        sample_rate = min(audio_settings['sample_rate'], int(device_info['defaultSampleRate']))
        
        stream = p.open(
            format=audio_settings['format'],
            channels=channels,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=audio_settings['chunk_size']
        )
        
        print(f"Stream opened: {channels} channels, {sample_rate} Hz")
        
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
        if 'stream' in locals() and stream:
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
    return render_template('index.html')

@app.route('/check_setup')
def check_setup():
    """Check if virtual audio cable is available"""
    cable_available = check_virtual_cable()
    return jsonify({
        'virtual_cable_available': cable_available,
        'message': 'Virtual Cable Ready' if cable_available else 'Install VB-Audio Virtual Cable'
    })

@app.route('/start_stream', methods=['POST'])
def start_stream():
    """Start audio streaming"""
    global is_streaming, stream_thread
    
    if is_streaming:
        return jsonify({'status': 'already_running', 'message': 'Stream is already active'})
    
    if not virtual_cable_available:
        return jsonify({'status': 'error', 'message': 'Virtual audio cable not available. Please install VB-Audio Virtual Cable.'})
    
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
        'settings': audio_settings,
        'virtual_cable_available': virtual_cable_available
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
    
    # Check for virtual cable on startup
    if check_virtual_cable():
        print("✅ Virtual Audio Cable detected!")
        print("Ready to stream system audio")
    else:
        print("❌ Virtual Audio Cable not found")
        print("Please install VB-Audio Virtual Cable for system audio capture")
        print("Download from: https://vb-audio.com/Cable/")
    
    print(f"Starting server on port 5017...")
    print(f"Access the control panel at: http://localhost:5017")
    print(f"For Android access, use your PC's IP address instead of localhost")
    print("=" * 40)
    
    # Allow connections from any IP address
    app.run(host='0.0.0.0', port=5017, debug=False, threaded=True)