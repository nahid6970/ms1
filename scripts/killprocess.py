#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A faster, Python-based process killer using psutil and fzf.
This script lists running processes, allows for interactive multi-selection via fzf,
and terminates the selected processes.
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import threading

try:
    import psutil
except ImportError:
    print("Error: psutil library not found.", file=sys.stderr)
    print("Please install it using: pip install psutil", file=sys.stderr)
    sys.exit(1)

def get_process_info(proc):
    """
    Get process information in a thread-safe manner.
    """
    try:
        # Get all info in one call to minimize system calls
        info = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'memory_percent'])
        
        # If cmdline is empty, use an empty string
        cmdline = ' '.join(info['cmdline']) if info['cmdline'] else ''
        
        return {
            'pid': info['pid'],
            'name': info['name'],
            'memory': info['memory_percent'] or 0.0,
            'cmdline': cmdline
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None

def get_processes_fast():
    """
    Gets a list of processes with their PID, name, memory usage, and command line.
    Uses memory usage instead of CPU for faster loading and multithreading for performance.
    """
    processes = list(psutil.process_iter())
    
    # Use ThreadPoolExecutor to process multiple processes concurrently
    with ThreadPoolExecutor(max_workers=min(32, len(processes))) as executor:
        results = list(executor.map(get_process_info, processes))
    
    # Filter out None results and sort by memory usage
    procs = [p for p in results if p is not None]
    return sorted(procs, key=lambda x: x['memory'], reverse=True)

def run_fzf_selection(procs):
    """
    Formats the process list, runs fzf for user selection, and returns selected PIDs.
    """
    # Define header and format each process line for fzf
    header = f"{'PID':<10}{'Name':<30}{'Memory%':<10}{'CommandLine'}"
    proc_lines = [
        f"{p['pid']:<10}{p['name']:<30}{p['memory']:<10.2f}{p['cmdline']:.120}" # Truncate long command lines
        for p in procs
    ]
    
    fzf_input = "\n".join([header] + proc_lines).encode('utf-8')

    try:
        # Execute fzf with multi-select and a preview window
        fzf_command = [
            'fzf', 
            '-m', 
            '--header-lines=1', # Treat the first line as a header
            '--preview', 'echo {}', 
            '--preview-window=up:1',
            '--height=80%'  # Limit height for better performance
        ]
        fzf_proc = subprocess.Popen(
            fzf_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = fzf_proc.communicate(input=fzf_input)

        if fzf_proc.returncode != 0:
            # fzf was likely cancelled (e.g., by pressing Esc)
            # Check if fzf is not installed
            err_str = stderr.decode('utf-8', errors='ignore').lower()
            if "command not found" in err_str or "'fzf' is not recognized" in err_str:
                print("Error: fzf is not installed or not in your PATH.", file=sys.stderr)
                print("Please install it from: https://github.com/junegunn/fzf", file=sys.stderr)
                sys.exit(1)
            return [] # No selection

        selected_lines = stdout.decode('utf-8').strip().split('\n')
        if not selected_lines or not selected_lines[0]:
            return [] # No selection

        # Extract PIDs from the selected lines
        pids_to_kill = []
        for line in selected_lines:
            try:
                pid = int(line.strip().split()[0])
                pids_to_kill.append(pid)
            except (ValueError, IndexError):
                continue # Ignore lines that don't parse correctly
        return pids_to_kill

    except FileNotFoundError:
        print("Error: fzf is not installed or not in your PATH.", file=sys.stderr)
        print("Please install it from: https://github.com/junegunn/fzf", file=sys.stderr)
        sys.exit(1)

def terminate_processes(pids):
    """
    Terminates a list of processes by their PIDs.
    """
    if not pids:
        print("No processes selected to terminate.")
        return

    for pid in pids:
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            proc.kill()
            print(f"Process '{proc_name}' (PID: {pid}) was terminated.")
        except psutil.NoSuchProcess:
            print(f"Process with PID {pid} no longer exists.")
        except psutil.AccessDenied:
            print(f"Access denied to terminate process with PID {pid}. Try running as administrator.", file=sys.stderr)
        except Exception as e:
            print(f"Failed to terminate process with PID {pid}: {e}", file=sys.stderr)

if __name__ == "__main__":
    print("Gathering process information...")
    processes = get_processes_fast()
    
    if not processes:
        print("Could not retrieve any running processes.")
        sys.exit(0)
        
    pids_to_terminate = run_fzf_selection(processes)
    terminate_processes(pids_to_terminate)