import os
import sys
import ctypes
from ctypes import wintypes, Structure, byref, sizeof, create_unicode_buffer
import psutil

# Windows API constants
MAX_PATH = 260
CCH_RM_MAX_APP_NAME = 255
CCH_RM_MAX_SVC_NAME = 63
RM_INVALID_TS_SESSION = 0xFFFFFFFF
RM_INVALID_PROCESS = 0xFFFFFFFF

# Restart Manager API structures
class RM_UNIQUE_PROCESS(Structure):
    _fields_ = [
        ("dwProcessId", wintypes.DWORD),
        ("ProcessStartTime", wintypes.FILETIME)
    ]

class RM_PROCESS_INFO(Structure):
    _fields_ = [
        ("Process", RM_UNIQUE_PROCESS),
        ("strAppName", wintypes.WCHAR * CCH_RM_MAX_APP_NAME),
        ("strServiceShortName", wintypes.WCHAR * CCH_RM_MAX_SVC_NAME),
        ("ApplicationType", wintypes.DWORD),
        ("AppStatus", wintypes.ULONG),
        ("TSSessionId", wintypes.DWORD),
        ("bRestartable", wintypes.BOOL)
    ]

# Load Windows DLLs
try:
    rstrtmgr = ctypes.windll.rstrtmgr
    kernel32 = ctypes.windll.kernel32
    
    # Define function signatures
    rstrtmgr.RmStartSession.argtypes = [
        ctypes.POINTER(wintypes.DWORD),  # pSessionHandle
        wintypes.DWORD,                  # dwSessionFlags
        ctypes.POINTER(wintypes.WCHAR)   # strSessionKey
    ]
    rstrtmgr.RmStartSession.restype = wintypes.DWORD
    
    rstrtmgr.RmEndSession.argtypes = [wintypes.DWORD]
    rstrtmgr.RmEndSession.restype = wintypes.DWORD
    
    rstrtmgr.RmRegisterResources.argtypes = [
        wintypes.DWORD,                           # dwSessionHandle
        wintypes.UINT,                            # nFiles
        ctypes.POINTER(ctypes.POINTER(wintypes.WCHAR)),  # rgsFileNames
        wintypes.UINT,                            # nApplications
        ctypes.POINTER(RM_UNIQUE_PROCESS),        # rgApplications
        wintypes.UINT,                            # nServices
        ctypes.POINTER(ctypes.POINTER(wintypes.WCHAR))   # rgsServiceNames
    ]
    rstrtmgr.RmRegisterResources.restype = wintypes.DWORD
    
    rstrtmgr.RmGetList.argtypes = [
        wintypes.DWORD,                    # dwSessionHandle
        ctypes.POINTER(wintypes.UINT),     # pnProcInfoNeeded
        ctypes.POINTER(wintypes.UINT),     # pnProcInfo
        ctypes.POINTER(RM_PROCESS_INFO),   # rgAffectedApps
        ctypes.POINTER(wintypes.DWORD)     # lpdwRebootReasons
    ]
    rstrtmgr.RmGetList.restype = wintypes.DWORD
    
    API_AVAILABLE = True
    
except (OSError, AttributeError):
    print("Warning: Restart Manager API not available. Using fallback methods.")
    API_AVAILABLE = False

def find_locking_processes_rm(file_path):
    """
    Use Windows Restart Manager API to find processes locking a file/folder
    This is the same method used by PowerToys LockSmith
    """
    if not API_AVAILABLE:
        return []
    
    try:
        # Normalize path
        file_path = os.path.abspath(file_path)
        
        print(f"Using Restart Manager API to find processes locking: {file_path}")
        print("This is the same method used by PowerToys LockSmith...\n")
        
        # Start a restart manager session
        session_handle = wintypes.DWORD()
        session_key = create_unicode_buffer(64)
        
        result = rstrtmgr.RmStartSession(byref(session_handle), 0, session_key)
        if result != 0:
            print(f"Failed to start Restart Manager session. Error: {result}")
            return []
        
        try:
            # Register the file/folder with restart manager
            file_list = (ctypes.POINTER(wintypes.WCHAR) * 1)()
            file_list[0] = ctypes.cast(create_unicode_buffer(file_path), ctypes.POINTER(wintypes.WCHAR))
            
            result = rstrtmgr.RmRegisterResources(
                session_handle,
                1,  # nFiles
                file_list,
                0,  # nApplications
                None,
                0,  # nServices
                None
            )
            
            if result != 0:
                print(f"Failed to register resource. Error: {result}")
                return []
            
            # Get the list of processes
            proc_info_needed = wintypes.UINT()
            proc_info = wintypes.UINT()
            reboot_reasons = wintypes.DWORD()
            
            # First call to get the required buffer size
            result = rstrtmgr.RmGetList(
                session_handle,
                byref(proc_info_needed),
                byref(proc_info),
                None,
                byref(reboot_reasons)
            )
            
            if proc_info_needed.value == 0:
                print("No processes found using the file/folder.")
                return []
            
            # Second call to get the actual process list
            process_info_array = (RM_PROCESS_INFO * proc_info_needed.value)()
            proc_info.value = proc_info_needed.value
            
            result = rstrtmgr.RmGetList(
                session_handle,
                byref(proc_info_needed),
                byref(proc_info),
                process_info_array,
                byref(reboot_reasons)
            )
            
            if result != 0:
                print(f"Failed to get process list. Error: {result}")
                return []
            
            # Extract process information
            processes = []
            for i in range(proc_info.value):
                proc_info_item = process_info_array[i]
                processes.append({
                    'name': proc_info_item.strAppName,
                    'pid': proc_info_item.Process.dwProcessId,
                    'type': 'RestartManager',
                    'restartable': bool(proc_info_item.bRestartable),
                    'app_type': proc_info_item.ApplicationType,
                    'status': proc_info_item.AppStatus
                })
            
            return processes
            
        finally:
            # Clean up the session
            rstrtmgr.RmEndSession(session_handle)
            
    except Exception as e:
        print(f"Error using Restart Manager API: {e}")
        return []

def find_locking_processes_alternative(file_path):
    """
    Alternative method using Windows API calls similar to LockSmith
    """
    try:
        file_path = os.path.abspath(file_path)
        processes = []
        
        print(f"Using alternative Windows API method for: {file_path}")
        print("Checking all running processes...\n")
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if process has the file/folder open
                try:
                    files = proc.open_files()
                    for f in files:
                        if file_path.lower() in f.path.lower():
                            processes.append({
                                'name': proc.info['name'],
                                'pid': proc.info['pid'],
                                'type': 'OpenFile',
                                'path': f.path,
                                'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                            })
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
                
                # Check current working directory
                try:
                    cwd = proc.cwd()
                    if cwd and file_path.lower() in cwd.lower():
                        processes.append({
                            'name': proc.info['name'],
                            'pid': proc.info['pid'],
                            'type': 'WorkingDirectory',
                            'path': cwd,
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                        })
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
                
                # Check memory maps (DLLs, etc.)
                try:
                    maps = proc.memory_maps()
                    for m in maps:
                        if hasattr(m, 'path') and m.path and file_path.lower() in m.path.lower():
                            processes.append({
                                'name': proc.info['name'],
                                'pid': proc.info['pid'],
                                'type': 'MemoryMap',
                                'path': m.path,
                                'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                            })
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
                
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
        
        # Remove duplicates based on PID
        unique_processes = []
        seen_pids = set()
        for proc in processes:
            if proc['pid'] not in seen_pids:
                unique_processes.append(proc)
                seen_pids.add(proc['pid'])
        
        return unique_processes
        
    except Exception as e:
        print(f"Error in alternative method: {e}")
        return []

def display_processes(processes):
    """Display found processes with enhanced information"""
    if not processes:
        print("No processes found using the specified path.")
        return False
    
    print(f"Found {len(processes)} process(es) using the path:\n")
    
    for i, proc in enumerate(processes, 1):
        print(f"{i}. Process: {proc['name']} (PID: {proc['pid']})")
        print(f"   Detection Method: {proc['type']}")
        
        if 'restartable' in proc:
            print(f"   Restartable: {'Yes' if proc['restartable'] else 'No'}")
        
        if 'app_type' in proc:
            app_types = {0: 'Unknown', 1: 'MainWindow', 2: 'OtherWindow', 3: 'Service', 4: 'Explorer', 5: 'Console', 6: 'Critical'}
            print(f"   Application Type: {app_types.get(proc['app_type'], 'Unknown')}")
        
        if 'path' in proc:
            print(f"   Path: {proc['path']}")
        
        if 'cmdline' in proc:
            print(f"   Command Line: {proc['cmdline']}")
        
        print()
    
    return True

def terminate_process_by_pid(pid, name):
    """Terminate a process by PID with enhanced error handling"""
    try:
        print(f"Terminating {name} (PID: {pid})...")
        
        # Check if process exists
        if not psutil.pid_exists(pid):
            print(f"Process {name} (PID: {pid}) no longer exists.")
            return True
        
        proc = psutil.Process(pid)
        
        # Get process info before termination
        try:
            proc_name = proc.name()
            proc_status = proc.status()
        except psutil.NoSuchProcess:
            print(f"Process {name} (PID: {pid}) no longer exists.")
            return True
        
        # Try graceful termination first
        proc.terminate()
        
        # Wait for termination
        try:
            proc.wait(timeout=5)
            print(f"✓ Process {proc_name} (PID: {pid}) terminated successfully.")
            return True
        except psutil.TimeoutExpired:
            print(f"Graceful termination timed out. Force killing {proc_name} (PID: {pid})...")
            proc.kill()
            try:
                proc.wait(timeout=3)
                print(f"✓ Process {proc_name} (PID: {pid}) force killed.")
                return True
            except psutil.TimeoutExpired:
                print(f"✗ Failed to kill process {proc_name} (PID: {pid}).")
                return False
            
    except psutil.NoSuchProcess:
        print(f"Process {name} (PID: {pid}) no longer exists.")
        return True
    except psutil.AccessDenied:
        print(f"✗ Access denied. Cannot terminate {name} (PID: {pid}).")
        print("  Try running the script as administrator.")
        return False
    except Exception as e:
        print(f"✗ Error terminating process: {e}")
        return False

def main():
    print("=== File Lock Finder (PowerToys LockSmith Style) ===")
    print("Uses Windows Restart Manager API - the same method as PowerToys LockSmith\n")
    
    # Check if running as administrator
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("⚠️  Warning: Not running as administrator. Some processes may not be detected.")
            print("   For best results, run this script as administrator.\n")
    except:
        pass
    
    # Get target path
    while True:
        target_path = input("Enter the file or folder path: ").strip().strip('"\'')
        
        if not target_path:
            print("Please enter a valid path.")
            continue
        
        if not os.path.exists(target_path):
            print(f"Path '{target_path}' does not exist.")
            retry = input("Try again? (y/n): ").lower()
            if retry != 'y':
                return
            continue
        
        break
    
    # Choose detection method
    print("\nChoose detection method:")
    print("1. Restart Manager API (PowerToys LockSmith method) - Most accurate")
    print("2. Alternative method (psutil + Windows API)")
    
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == '1':
            processes = find_locking_processes_rm(target_path)
            break
        elif choice == '2':
            processes = find_locking_processes_alternative(target_path)
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    # Display results
    if not display_processes(processes):
        print("\nTips if no processes are found:")
        print("1. Make sure you're running as administrator")
        print("2. Try closing Windows Explorer windows showing the folder")
        print("3. Check if antivirus is scanning the files")
        print("4. Use Windows Resource Monitor (resmon.exe) -> Disk tab")
        print("5. Sometimes a simple restart resolves stubborn locks")
        return
    
    # Handle termination
    while True:
        print("\nOptions:")
        print("1. Terminate specific process(es)")
        print("2. Terminate all processes")
        print("3. Refresh/Rescan")
        print("4. Exit")
        
        action = input("\nEnter your choice (1-4): ").strip()
        
        if action == '1':
            # Terminate specific processes
            nums_input = input("Enter process number(s) to terminate (comma-separated): ").strip()
            try:
                nums = [int(x.strip()) for x in nums_input.split(',')]
                valid_nums = [n for n in nums if 1 <= n <= len(processes)]
                
                if not valid_nums:
                    print("No valid process numbers entered.")
                    continue
                
                for num in valid_nums:
                    proc = processes[num - 1]
                    terminate_process_by_pid(proc['pid'], proc['name'])
                
                # Rescan
                print("\nRescanning...")
                if choice == '1':
                    processes = find_locking_processes_rm(target_path)
                else:
                    processes = find_locking_processes_alternative(target_path)
                
                display_processes(processes)
                
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas.")
        
        elif action == '2':
            # Terminate all
            confirm = input(f"Terminate all {len(processes)} process(es)? (y/n): ")
            if confirm.lower() == 'y':
                for proc in processes:
                    terminate_process_by_pid(proc['pid'], proc['name'])
                
                print("\nRescanning...")
                if choice == '1':
                    processes = find_locking_processes_rm(target_path)
                else:
                    processes = find_locking_processes_alternative(target_path)
                
                display_processes(processes)
        
        elif action == '3':
            # Refresh
            print("Rescanning...")
            if choice == '1':
                processes = find_locking_processes_rm(target_path)
            else:
                processes = find_locking_processes_alternative(target_path)
            
            if not display_processes(processes):
                break
        
        elif action == '4':
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