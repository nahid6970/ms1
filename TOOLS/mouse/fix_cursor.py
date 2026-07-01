#!/usr/bin/env python3
"""
Windows Mouse Cursor Fixer & Spotlight
--------------------------------------
A command-line tool to instantly fix a disappearing or invisible mouse cursor
on Windows by forcing graphics driver/compositor refreshes, resetting pointer schemes,
triggering software rendering, temporarily expanding cursor size, and drawing a
visual spotlight (like PowerToys Find My Mouse).

Author: Antigravity AI
"""

import sys
import os
import time
import ctypes
import argparse
import subprocess
import winreg

# Win32 API Constants
SPI_SETCURSORS = 0x0057
SPI_GETMOUSETRAILS = 0x005E
SPI_SETMOUSETRAILS = 0x005D
SPIF_SENDCHANGE = 0x0002
SPIF_UPDATEINIFILE = 0x0001

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
    script = os.path.abspath(sys.argv[0])
    args = ' '.join(sys.argv[1:])
    print("[*] Requesting administrator privileges...")
    
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {args}', None, 1
    )
    if int(ret) > 32:
        print("[+] Admin process spawned successfully.")
        sys.exit(0)
    else:
        print("[-] Elevation failed or was cancelled by user.")
        sys.exit(1)

def get_mouse_pos():
    """Get the current cursor coordinates."""
    pt = POINT()
    if ctypes.windll.user32.GetCursorPos(ctypes.byref(pt)):
        return pt.x, pt.y
    return 0, 0


def reload_system_cursors():
    """
    Forces Windows to reload the cursor scheme from the registry.
    This fixes situations where the cursor gets stuck in a hidden/empty state.
    """
    print("[*] Phase 2: Forcing Windows to reload system cursor scheme...")
    user32 = ctypes.windll.user32
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
    get_res = user32.SystemParametersInfoW(SPI_GETMOUSETRAILS, 0, ctypes.byref(original_trails), 0)
    
    if not get_res:
        print("[-] Could not retrieve current mouse trails setting. Attempting direct toggle.")
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

def get_current_cursor_size():
    """Get the user's current cursor base size from Registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors", 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "CursorBaseSize")
            return value
    except FileNotFoundError:
        return 32  # Standard default
    except Exception:
        return 32

def set_cursor_size(size):
    """Set the system cursor size in the Registry and notify Windows to refresh."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Cursors", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "CursorBaseSize", 0, winreg.REG_DWORD, size)
        
        # Standard refresh
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETCURSORS, 0, None, SPIF_SENDCHANGE | SPIF_UPDATEINIFILE)
        # Undocumented Accessibility resize refresh
        ctypes.windll.user32.SystemParametersInfoW(0x2029, 0, ctypes.c_void_p(size), SPIF_SENDCHANGE | SPIF_UPDATEINIFILE)
        return True
    except Exception as e:
        print(f"[-] Failed to update cursor size to {size}: {e}")
        return False

def show_spotlight_overlay(duration_ms=1500):
    """
    Creates a semi-transparent screen overlay with a transparent spotlight hole
    around the cursor location, styled with a glowing ring (PowerToys Find My Mouse style).
    """
    try:
        import tkinter as tk
    except ImportError:
        print("[-] Tkinter library not available. Skipping visual spotlight overlay.")
        return False

    print(f"[*] Displaying spotlight overlay for {duration_ms}ms...")
    
    root = tk.Tk()
    root.title("Mouse Spotlight Overlay")
    
    # Configure transparent, borderless, topmost window spanning the full screen
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    root.geometry(f"{screen_w}x{screen_h}+0+0")
    
    # Set the root background to black and establish window transparency
    root.configure(bg="black")
    root.attributes("-alpha", 0.5)  # 50% screen dimming overlay
    
    # Define a magenta color key for transparency holes
    trans_color = "#FF00FF"
    root.wm_attributes("-transparentcolor", trans_color)
    
    canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Locate mouse cursor
    mx, my = get_mouse_pos()
    
    # Draw transparent spotlight circle (using the transparency color key)
    radius = 80
    canvas.create_oval(
        mx - radius, my - radius,
        mx + radius, my + radius,
        fill=trans_color, outline=trans_color
    )
    
    # Draw a stylish glowing rings around the spotlight
    canvas.create_oval(
        mx - radius, my - radius,
        mx + radius, my + radius,
        outline="#00BFFF", width=3  # Deep Sky Blue border
    )
    
    # Visual pulse ring
    canvas.create_oval(
        mx - (radius + 10), my - (radius + 10),
        mx + (radius + 10), my + (radius + 10),
        outline="#1E90FF", width=1  # Dodger Blue outer pulse ring
    )
    
    # Close overlay window automatically
    root.after(duration_ms, root.destroy)
    root.mainloop()
    return True

def restart_explorer():
    """Restarts explorer.exe to reset shell composition and overlays."""
    print("[*] Restarting Windows Explorer...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, text=True)
        time.sleep(1.0)
        subprocess.Popen(["explorer.exe"], shell=True)
        print("[+] Windows Explorer restarted successfully.")
        return True
    except Exception as e:
        print(f"[-] Failed to restart Windows Explorer: {e}")
        return False

def restart_hid_service():
    """Restarts Human Interface Device Service (hidserv). Requires Admin."""
    if not is_admin():
        print("[-] HID Service restart requires Administrator privileges.")
        return False
        
    print("[*] Restarting Human Interface Device Service (hidserv)...")
    try:
        cmd = ["powershell", "-Command", "Restart-Service -Name 'hidserv' -Force"]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
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
        "--no-spotlight", action="store_true",
        help="Disable the visual spotlight overlay around the cursor"
    )
    parser.add_argument(
        "--no-resize", action="store_true",
        help="Disable the temporary cursor size expansion"
    )
    parser.add_argument(
        "--duration", type=int, default=1500,
        help="Duration in milliseconds for the spotlight and size expansion (default: 1500)"
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

    reload_system_cursors()
    print("-" * 40)
    toggle_mouse_trails()
    
    # Temporary cursor resizing (PowerToys style find-your-mouse feedback)
    original_size = get_current_cursor_size()
    resize_active = not args.no_resize
    
    if resize_active:
        print("-" * 40)
        print(f"[*] Temporarily expanding cursor size (Original: {original_size}px)...")
        set_cursor_size(128)  # Set to a huge size
        
    # Visual Spotlight Overlay
    if not args.no_spotlight:
        print("-" * 40)
        show_spotlight_overlay(duration_ms=args.duration)
        
    # Restore size if changed
    if resize_active:
        print("-" * 40)
        print(f"[*] Restoring original cursor size ({original_size}px)...")
        set_cursor_size(original_size)
        
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
