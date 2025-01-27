import os
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
# Timeout for command execution (in seconds)
COMMAND_TIMEOUT = 30

# ANSI escape codes for color
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"
RESET = "\033[0m"

# Ensure the script starts in the home directory
HOME_DIR = os.path.expanduser("~")
os.chdir(HOME_DIR)
print(f"Working directory set to: {os.getcwd()}")

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

def execute_command(command, unique_id):
    """Executes the given command in PowerShell and writes its output to a local file."""
    try:
        # Replace 'cc' with '&&' in the command
        transformed_command = command.replace(" cc ", " && ")
        print(f"Executing transformed command: {transformed_command}")

        # Start the PowerShell command process
        process = subprocess.Popen(
            [POWERSHELL_PATH, "-Command", transformed_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",  # Force UTF-8 encoding
            errors="replace"  # Replace invalid characters
        )

        try:
            # Wait for the process to complete or timeout
            stdout, stderr = process.communicate(timeout=COMMAND_TIMEOUT)
        except subprocess.TimeoutExpired:
            # Kill the process if it exceeds the timeout
            process.kill()
            stdout, stderr = "", f"Command exceeded {COMMAND_TIMEOUT} seconds and was terminated."

        # Write the color-coded output to the local file
        with open(LOCAL_OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"{GREEN}Command ID: {unique_id}{RESET}\n")
            f.write(f"{BLUE}Executed Command: {transformed_command}{RESET}\n\n")
            f.write(stdout if stdout else "No output returned.\n")
            if stderr:
                f.write("\nError Output:\n")
                f.write(stderr)
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
            # Extract the unique ID and command from the remote file
            try:
                unique_id, cmd = command.split(":", 1)
                execute_command(cmd.strip(), unique_id)
                upload_output_file()
                last_command = command
            except ValueError:
                print(f"{RED}Error parsing command: {command}{RESET}")
        time.sleep(CHECK_INTERVAL)
