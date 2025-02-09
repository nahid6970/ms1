import os
import shutil
import psutil
import subprocess
import ctypes

def is_admin():
    """Check if the script is running as an administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def find_locked_process(folder_path):
    """Find which process is locking the folder using Sysinternals' handle.exe"""
    handle_exe = r"C:\msBackups\sysinternals\SysinternalsSuite\handle.exe"  # Change this to the actual path of handle.exe

    if not os.path.exists(handle_exe):
        print("Error: handle.exe not found. Download it from https://docs.microsoft.com/en-us/sysinternals/downloads/handle")
        return []

    try:
        result = subprocess.run([handle_exe, folder_path], capture_output=True, text=True)
        output = result.stdout

        locked_processes = []
        for line in output.split("\n"):
            if "pid:" in line.lower():
                parts = line.split()
                pid = next((int(p.split(":")[1]) for p in parts if "pid:" in p.lower()), None)
                if pid:
                    process_name = psutil.Process(pid).name()
                    locked_processes.append((pid, process_name))

        return locked_processes
    except Exception as e:
        print(f"Error running handle.exe: {e}")
        return []

def delete_folder(folder_path):
    """Attempt to delete the folder and check for locking processes if deletion fails."""
    try:
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete '{folder_path}': {e}")

        locked_processes = find_locked_process(folder_path)
        if locked_processes:
            print("\nProcesses preventing deletion:")
            for pid, name in locked_processes:
                print(f" - PID: {pid}, Name: {name}")
        else:
            print("Could not identify the locking process. Try running as Administrator.")

if __name__ == "__main__":
    if not is_admin():
        print("Warning: Run this script as Administrator for better results.")

    folder = input("Enter the folder path to delete: ").strip()

    if os.path.exists(folder):
        delete_folder(folder)
    else:
        print("Folder does not exist.")
