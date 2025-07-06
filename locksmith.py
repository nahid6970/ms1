import psutil
import os
import sys
from pathlib import Path

def get_processes_using_path(target_path):
    """
    Find all processes that are using the specified file or folder.
    Returns a list of tuples (process, files_in_use)
    """
    target_path = os.path.abspath(target_path)
    processes_using_path = []
    
    print(f"Scanning for processes using: {target_path}")
    print("This may take a moment...\n")
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Get all open files for this process
            files = proc.open_files()
            matching_files = []
            
            for file_info in files:
                file_path = os.path.abspath(file_info.path)
                
                # Check if the file is the target or inside the target folder
                if file_path == target_path or file_path.startswith(target_path + os.sep):
                    matching_files.append(file_path)
            
            if matching_files:
                processes_using_path.append((proc, matching_files))
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Skip processes we can't access
            continue
        except Exception as e:
            # Skip any other errors
            continue
    
    return processes_using_path

def display_processes(processes_using_path):
    """Display the processes and files they're using"""
    if not processes_using_path:
        print("No processes found using the specified path.")
        return False
    
    print(f"Found {len(processes_using_path)} process(es) using the path:\n")
    
    for i, (proc, files) in enumerate(processes_using_path, 1):
        try:
            print(f"{i}. Process: {proc.info['name']} (PID: {proc.info['pid']})")
            print(f"   Command: {' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'}")
            print(f"   Files in use:")
            for file_path in files:
                print(f"     - {file_path}")
            print()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"{i}. Process no longer accessible (PID: {proc.pid})")
            print()
    
    return True

def terminate_process(proc):
    """Terminate a process safely"""
    try:
        proc_name = proc.info['name']
        proc_pid = proc.info['pid']
        
        print(f"Terminating {proc_name} (PID: {proc_pid})...")
        
        # Try graceful termination first
        proc.terminate()
        
        # Wait up to 3 seconds for graceful termination
        try:
            proc.wait(timeout=3)
            print(f"✓ Process {proc_name} (PID: {proc_pid}) terminated successfully.")
            return True
        except psutil.TimeoutExpired:
            # Force kill if graceful termination fails
            print(f"Graceful termination failed. Force killing {proc_name} (PID: {proc_pid})...")
            proc.kill()
            proc.wait()
            print(f"✓ Process {proc_name} (PID: {proc_pid}) force killed.")
            return True
            
    except (psutil.NoSuchProcess):
        print(f"Process no longer exists.")
        return True
    except psutil.AccessDenied:
        print(f"✗ Access denied. Cannot terminate process {proc_name} (PID: {proc_pid}).")
        print("  Try running the script as administrator.")
        return False
    except Exception as e:
        print(f"✗ Error terminating process: {e}")
        return False

def main():
    print("=== Process File/Folder Usage Finder ===\n")
    
    # Get the target path from user
    while True:
        target_path = input("Enter the file or folder path: ").strip().strip('"\'')
        
        if not target_path:
            print("Please enter a valid path.")
            continue
        
        # Check if path exists
        if not os.path.exists(target_path):
            print(f"Path '{target_path}' does not exist.")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return
            continue
        
        break
    
    # Find processes using the path
    processes_using_path = get_processes_using_path(target_path)
    
    # Display results
    if not display_processes(processes_using_path):
        return
    
    # Ask user what to do
    while True:
        print("Options:")
        print("1. Terminate specific process(es)")
        print("2. Terminate all processes")
        print("3. Refresh/Rescan")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            # Terminate specific processes
            print("\nEnter the process number(s) to terminate (comma-separated):")
            process_nums = input("Process numbers: ").strip()
            
            try:
                nums = [int(x.strip()) for x in process_nums.split(',')]
                valid_nums = [n for n in nums if 1 <= n <= len(processes_using_path)]
                
                if not valid_nums:
                    print("No valid process numbers entered.")
                    continue
                
                print(f"\nTerminating {len(valid_nums)} process(es)...")
                for num in valid_nums:
                    proc, files = processes_using_path[num - 1]
                    terminate_process(proc)
                
                print("\nRescanning...")
                processes_using_path = get_processes_using_path(target_path)
                display_processes(processes_using_path)
                
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
        
        elif choice == '2':
            # Terminate all processes
            confirm = input(f"\nAre you sure you want to terminate all {len(processes_using_path)} process(es)? (y/n): ")
            if confirm.lower() == 'y':
                print(f"\nTerminating all {len(processes_using_path)} process(es)...")
                for proc, files in processes_using_path:
                    terminate_process(proc)
                
                print("\nRescanning...")
                processes_using_path = get_processes_using_path(target_path)
                display_processes(processes_using_path)
        
        elif choice == '3':
            # Refresh
            print("\nRescanning...")
            processes_using_path = get_processes_using_path(target_path)
            if not display_processes(processes_using_path):
                break
        
        elif choice == '4':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        input("Press Enter to exit...")