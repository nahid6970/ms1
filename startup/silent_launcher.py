import sys
import subprocess

if len(sys.argv) < 2:
    sys.exit("No command or app provided to launch.")

target = sys.argv[1]

try:
    if target.endswith(".exe"):
        subprocess.Popen(target, shell=True)  # Launch the app
    else:
        subprocess.run(target, shell=True)  # Execute the command
except Exception as e:
    with open("C:\\ms1\\silent_launcher.log", "a") as log_file:
        log_file.write(f"Error launching {target}: {e}\n")
