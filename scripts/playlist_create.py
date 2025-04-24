import os
import random

# Configuration
song_folder = r"D:\song"
output_file = r"C:\Users\nahid\Desktop\playlist.dpl"
ignore_folders = {
    os.path.join(song_folder, ".stfolder"),
    os.path.join(song_folder, "stanely")
}
ignore_extensions = {".jpg", ".png", ".jpeg", ".gif", ".bmp", ".webp", ".mp3"}

# Collect all valid files recursively
all_files = []
for root, dirs, files in os.walk(song_folder):
    dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_folders]
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext not in ignore_extensions:
            full_path = os.path.join(root, file)
            all_files.append(full_path)

# Shuffle the file list to randomize order
random.shuffle(all_files)

# Write to output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("DAUMPLAYLIST\n")
    for index, file_path in enumerate(all_files, start=1):
        f.write(f"{index}*file*{file_path}\n")

print(f"Randomized playlist created with {len(all_files)} items at {output_file}")
