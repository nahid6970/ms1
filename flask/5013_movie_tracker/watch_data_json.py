import os
import time
import psutil
from datetime import datetime
import traceback

# Directory to monitor (current directory where this script is)
WATCH_DIR = os.path.dirname(os.path.abspath(__file__))
WATCH_FILE = os.path.join(WATCH_DIR, "data.json")
LOG_FILE = os.path.join(WATCH_DIR, "data_json_watcher.log")

def log_message(message):
    """Write message to log file and print to console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def get_file_info(filepath):
    """Get detailed information about who created/modified the file"""
    try:
        stat_info = os.stat(filepath)
        size = stat_info.st_size
        modified_time = datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        info = f"File: {filepath}\n"
        info += f"  Size: {size} bytes\n"
        info += f"  Modified: {modified_time}\n"
        
        return info
    except Exception as e:
        return f"Error getting file info: {e}\n"

def get_processes_with_file_open(filepath):
    """Find all processes that have the file open"""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
            try:
                # Check if process has the file open
                for item in proc.open_files():
                    if item.path.lower() == filepath.lower():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A',
                            'cwd': proc.info['cwd']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        log_message(f"Error scanning processes: {e}")
    
    return processes

def get_python_processes():
    """Get all running Python processes"""
    python_procs = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                    python_procs.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline,
                        'cwd': proc.info['cwd']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        log_message(f"Error getting Python processes: {e}")
    
    return python_procs

def main():
    log_message("=" * 80)
    log_message("File Watcher Started")
    log_message(f"Monitoring: {WATCH_FILE}")
    log_message(f"Log file: {LOG_FILE}")
    log_message("=" * 80)
    
    file_existed = os.path.exists(WATCH_FILE)
    
    if file_existed:
        log_message("WARNING: data.json already exists at startup!")
        log_message(get_file_info(WATCH_FILE))
    
    try:
        while True:
            current_exists = os.path.exists(WATCH_FILE)
            
            # File was created
            if not file_existed and current_exists:
                log_message("\n" + "!" * 80)
                log_message("ALERT: data.json was just CREATED!")
                log_message("!" * 80)
                
                # Get file info
                log_message(get_file_info(WATCH_FILE))
                
                # Find processes with file open
                log_message("\nProcesses with data.json open:")
                procs_with_file = get_processes_with_file_open(WATCH_FILE)
                if procs_with_file:
                    for proc in procs_with_file:
                        log_message(f"  PID: {proc['pid']}")
                        log_message(f"  Name: {proc['name']}")
                        log_message(f"  Command: {proc['cmdline']}")
                        log_message(f"  Working Dir: {proc['cwd']}")
                        log_message("  ---")
                else:
                    log_message("  No processes currently have the file open")
                
                # List all Python processes
                log_message("\nAll running Python processes:")
                python_procs = get_python_processes()
                for proc in python_procs:
                    log_message(f"  PID: {proc['pid']} | {proc['name']}")
                    log_message(f"    Command: {proc['cmdline']}")
                    log_message(f"    Working Dir: {proc['cwd']}")
                    
                    # Highlight if it's running app.py
                    if 'app.py' in proc['cmdline']:
                        log_message("    >>> POSSIBLE CULPRIT: Running app.py <<<")
                    log_message("  ---")
                
                log_message("!" * 80 + "\n")
            
            # File was deleted
            elif file_existed and not current_exists:
                log_message("INFO: data.json was deleted")
            
            file_existed = current_exists
            time.sleep(1)  # Check every second
            
    except KeyboardInterrupt:
        log_message("\nFile Watcher Stopped by user")
    except Exception as e:
        log_message(f"\nERROR: {e}")
        log_message(traceback.format_exc())

if __name__ == "__main__":
    main()
