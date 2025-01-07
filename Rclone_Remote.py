import subprocess
import time

# Cloud file to read commands from
REMOTE_COMMAND_FILE = r"g00:\Remote_Control\Command.txt"
# Local file for storing command output
LOCAL_OUTPUT_FILE = r"C:\msBackups\Remote_Control\output.txt"
# Cloud file to upload command output
REMOTE_OUTPUT_FILE = r"g00:\Remote_Control\output.txt"
# Path to the latest PowerShell executable
POWERSHELL_PATH = r"C:\Program Files\PowerShell\7\pwsh.exe"
# Time interval to check for updates (in seconds)
CHECK_INTERVAL = 1

def read_remote_file():
    """Reads the content of the remote file using rclone cat."""
    try:
        result = subprocess.run(["rclone", "cat", REMOTE_COMMAND_FILE], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error reading remote file: {result.stderr}")
            return ""
    except Exception as e:
        print(f"Error: {e}")
        return ""

def execute_command(command):
    """Executes the given command in PowerShell and writes its output to a local file."""
    try:
        print(f"Executing: {command}")
        # Execute the command using PowerShell with -NoProfile
        result = subprocess.run(
            [POWERSHELL_PATH, "-Command", command],
            capture_output=True,
            text=True
        )
        # Write the output to the local file
        with open(LOCAL_OUTPUT_FILE, "w") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\nError Output:\n")
                f.write(result.stderr)
    except Exception as e:
        print(f"Error executing command: {e}")

def upload_output_file():
    """Uploads the local output file to the cloud drive."""
    try:
        result = subprocess.run(
            ["rclone", "copyto", LOCAL_OUTPUT_FILE, REMOTE_OUTPUT_FILE],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("Output uploaded successfully.")
        else:
            print(f"Error uploading output: {result.stderr}")
    except Exception as e:
        print(f"Error during upload: {e}")

if __name__ == "__main__":
    last_command = ""
    print(f"Monitoring remote file: {REMOTE_COMMAND_FILE}")
    while True:
        command = read_remote_file()
        if command and command != last_command:  # Check if the command is new
            execute_command(command)
            upload_output_file()
            last_command = command
        time.sleep(CHECK_INTERVAL)
