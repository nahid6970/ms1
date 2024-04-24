import os
import subprocess
import random

def add_media_to_potplayer(directory):
    media_files = []
    # Walk through the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.mp4', '.avi',"mkv")):  # Check for audio and video files
                media_files.append(os.path.join(root, file))

    # Shuffle the list of media files randomly
    random.shuffle(media_files)

    # Check if there are any media files
    if not media_files:
        print("No media files found in the directory.")
        return

    # Launch PotPlayer with media files
    potplayer_path = r"C:\Program Files\PotPlayer\PotPlayerMini64.exe"  # PotPlayer executable path
    subprocess.Popen([potplayer_path] + media_files)

if __name__ == "__main__":
    directory = r"D:\song"  # Change this directory accordingly
    add_media_to_potplayer(directory)
