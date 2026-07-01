#!/usr/bin/env python3
"""
Windows Mouse Cursor Fixer
--------------------------
A command-line tool to instantly fix a disappearing or invisible mouse cursor
on Windows by forcing graphics driver/compositor refreshes, resetting pointer schemes,
and triggering software rendering fallbacks.

Author: Antigravity AI
"""

import sys
import os
import time
import ctypes
import argparse
import subprocess

# Win32 API Constants
SPI_SETCURSORS = 0x0057
SPI_GETMOUSETRAILS = 0x005E
SPI_SETMOUSETRAILS = 0x005D
SPIF_SENDCHANGE = 0x0002

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    """Re-run the current script with administrator privileges."""
    # Get current script path and arguments
    script = os.path.abspath(sys.argv[0])
    args = ' '.join(sys.argv[1:])
    print("[*] Requesting administrator privileges...")
    
    # Run ShellExecute to trigger UAC prompt
    # "runas" verb requests elevation
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {args}', None, 1
    )
    if int(ret) > 32:
        print("[+] Admin process spawned successfully.")
        sys.exit(0)
    else:
        print("[-] Elevation failed or was cancelled by user.")
        sys.exit(1)

def jiggle_mouse():
    """
    Slightly moves the cursor position and returns it to trigger
    system-wide mousemove rendering updates.
    """
    print("[*] Phase 1: Jiggling mouse cursor to trigger pointer updates...")
    user32 = ctypes.windll.user32
    
    # Get current position
    pt = POINT()
    if not user32.GetCursorPos(ctypes.byref(pt)):
        print("[-] Failed to get current cursor position.")
        return False
        
    original_x, original_y = pt.x, pt.y
    print(f"    Current position: ({original_x}, {original_y})")
    
    # Move mouse by 15 pixels in a small square to trigger OS and browser updates
    offsets = [(15, 0), (15, 15), (0, 15), (0, 0)]
    for dx, dy in offsets:
        user32.SetCursorPos(original_x + dx, original_y + dy)
        time.sleep(0.05)
        
    # Return to original position
    user32.SetCursorPos(original_x, original_y)
    print("[+] Mouse jiggle complete.")
    return True

def reload_system_cursors():
    """
    Forces Windows to reload the cursor scheme from the registry.
    This fixes situations where the cursor gets stuck in a hidden/empty state.
    """
    print("[*] Phase 2: Forcing Windows to reload system cursor scheme...")
    user32 = ctypes.windll.user32
    
    # SPI_SETCURSORS (0x0057) tells Windows to reload the registry settings for cursors
    result = user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE)
    if result:
        print("[+] System cursor scheme reloaded successfully.")
        return True
    else:
        print("[-] Failed to reload system cursor scheme.")
        return False

def toggle_mouse_trails():
    """
    Toggles Windows pointer trails on and off.
    Enabling pointer trails temporarily forces Windows to switch from GPU hardware-based cursor 
    overlays to CPU software-rendered cursors. This bypasses common browser CSS/GPU compositing bugs.
    """
    print("[*] Phase 3: Toggling mouse pointer trails to reset compositing layers...")
    user32 = ctypes.windll.user32
    
    # Get original trail settings
    original_trails = ctypes.c_int(0)
    # For GETMOUSETRAILS, pvParam points to the int buffer
    get_res = user32.SystemParametersInfoW(SPI_GETMOUSETRAILS, 0, ctypes.byref(original_trails), 0)
    
    if not get_res:
        print("[-] Could not retrieve current mouse trails setting. Attempting direct toggle.")
        # Default to disabling if we can't read, but let's try setting directly
        original_val = 0
    else:
        original_val = original_trails.value
        print(f"    Current trail count: {original_val} (0 or 1 means disabled)")

    # Enable trails (setting to 3) to force software cursor renderer
    print("    Enabling software rendering overlay (Trails = 3)...")
    user32.SystemParametersInfoW(SPI_SETMOUSETRAILS, 3, None, SPIF_SENDCHANGE)
    time.sleep(0.2)
    
    # Reset back to original value (or 0 if it was disabled)
    print(f"    Restoring original mouse trails setting ({original_val})...")
    user32.SystemParametersInfoW(SPI_SETMOUSETRAILS, original_val, None, SPIF_SENDCHANGE)
    
    print("[+] Pointer trails toggle complete.")
    return True

def restart_explorer():
    """
    Restarts explorer.exe. This forces a shell restart which rebuilds
    the mouse compositor state.
    """
    print("[*] Phase 4: Restarting Windows Explorer...")
    try:
        # Gracefully stop explorer, then force kill if needed
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, text=True)
        time.sleep(1.0)
        # Start explorer as a detached background process
        subprocess.Popen(["explorer.exe"], shell=True)
        print("[+] Windows Explorer restarted successfully.")
        return True
    except Exception as e:
        print(f"[-] Failed to restart Windows Explorer: {e}")
        return False

def restart_hid_service():
    """
    Restarts the Human Interface Device Service (hidserv).
    Requires administrator privileges.
    """
    if not is_admin():
        print("[-] HID Service restart requires Administrator privileges.")
        return False
        
    print("[*] Phase 5: Restarting Human Interface Device Service (hidserv)...")
    try:
        # Run PowerShell command to restart hidserv
        cmd = ["powershell", "-Command", "Restart-Service -Name 'hidserv' -Force"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[+] Human Interface Device Service restarted successfully.")
        return True
    except Exception as e:
        print(f"[-] Failed to restart HID Service: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Fixes disappearing or invisible mouse cursor issues on Windows."
    )
    parser.add_argument(
        "--explorer", action="store_true", 
        help="Include Windows Explorer restart (reloads taskbar/desktop UI)"
    )
    parser.add_argument(
        "--service", action="store_true", 
        help="Include HID Service restart (requires Administrator privileges)"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Perform all fixes, including Explorer and HID Service restarts (requires Admin)"
    )
    
    args = parser.parse_args()
    
    # If all is specified, toggle both flags
    if args.all:
        args.explorer = True
        args.service = True
        
    # Check if admin is needed for HID Service restart and elevate if not already admin
    if args.service and not is_admin():
        run_as_admin()
        
    print("=" * 60)
    print("           WINDOWS MOUSE CURSOR RECOVERY TOOL")
    print("=" * 60)
    
    # Execute standard safe fixes
    jiggle_mouse()
    print("-" * 40)
    reload_system_cursors()
    print("-" * 40)
    toggle_mouse_trails()
    
    # Execute advanced fixes if requested
    if args.explorer:
        print("-" * 40)
        restart_explorer()
        
    if args.service:
        print("-" * 40)
        restart_hid_service()
        
    print("=" * 60)
    print("[+] Done! If the cursor is still invisible, try the following:")
    print("    1. Press Ctrl + Alt + Delete, then press Esc.")
    print("    2. Press Win + Ctrl + Shift + B (restarts display drivers).")
    print("    3. If this happens in Chrome/Edge, disable Hardware Acceleration in browser settings.")
    print("=" * 60)

if __name__ == "__main__":
    main()
