import io
import wave
import numpy as np
import pyaudio
from flask import Flask, Response
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL  # Importing CLSCTX_ALL

app = Flask(__name__)

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024

# Initialize audio stream
p = pyaudio.PyAudio()

# Get the default audio device
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # Now CLSCTX_ALL is defined

# Create a stream to capture audio
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Generate audio from the system output
def generate_audio():
    while True:
        data = stream.read(CHUNK)
        # You can apply modifications here (e.g., change format, compression, etc.)
        yield data

@app.route("/audio")
def stream_audio():
    return Response(generate_audio(), mimetype="audio/wav")

@app.route("/")
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>System Audio Streaming</title>
    </head>
    <body>
        <h1>Stream System Audio</h1>
        <audio controls autoplay>
            <source src="/audio" type="audio/wav">
            Your browser does not support the audio element.
        </audio>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5003)
