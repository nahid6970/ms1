
import soundcard as sc
import wave
from flask import Flask, Response, render_template, jsonify
import io

app = Flask(__name__)

# --- Configuration ---
PORT = 5017
CHANNELS = 2
# Using a large number for frames in the WAV header to simulate a live stream
WAVE_FRAMES_LIMIT = 2**31 - 1 

def get_audio_devices():
    """Gets a list of all available input devices, including loopback."""
    devices = []
    all_mics = sc.all_microphones(include_loopback=True)
    for mic in all_mics:
        try:
            # Probing the microphone to check if it's a valid device
            with mic.recorder(samplerate=48000):
                pass
            devices.append({'id': mic.id, 'name': mic.name})
        except Exception as e:
            print(f"Could not use device {mic.name}: {e}")
    return devices

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/devices')
def list_devices():
    """Returns a JSON list of available audio devices."""
    devices = get_audio_devices()
    return jsonify(devices)

def generate_wav_header(samplerate, channels, bit_depth=16):
    """Generates a WAV file header for streaming."""
    header = io.BytesIO()
    with wave.open(header, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(bit_depth // 8)
        wf.setframerate(samplerate)
        wf.setnframes(WAVE_FRAMES_LIMIT)
    return header.getvalue()

def generate_audio(device_id, samplerate, blocksize):
    """A generator function that records and yields audio chunks."""
    try:
        yield generate_wav_header(samplerate, CHANNELS)
        
        mic = sc.get_microphone(id=device_id, include_loopback=True)
        
        with mic.recorder(samplerate=samplerate, channels=CHANNELS, blocksize=blocksize) as rec:
            print(f"Starting stream from '{rec.device}' with samplerate {samplerate}...")
            while True:
                data = rec.record(numframes=blocksize)
                yield data.tobytes()
    except Exception as e:
        print(f"Error in audio stream: {e}")
    finally:
        print("Audio stream stopped.")

@app.route('/audio.wav')
def audio_stream():
    """Streams audio data in WAV format."""
    # Get parameters from query string, with defaults
    device_id = request.args.get('device', sc.default_speaker().id)
    samplerate = int(request.args.get('samplerate', 44100))
    blocksize = int(request.args.get('blocksize', 2048))

    return Response(
        generate_audio(device_id, samplerate, blocksize),
        mimetype='audio/wav'
    )

if __name__ == '__main__':
    print("Available audio devices:")
    for device in get_audio_devices():
        print(f"  - ID: {device['id']}, Name: {device['name']}")
    
    print(f"\n--- Starting Flask server on http://0.0.0.0:{PORT} ---")
    app.run(host='0.0.0.0', port=PORT, debug=True, threaded=True)
