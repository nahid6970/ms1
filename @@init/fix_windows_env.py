import os
import sys
import ctypes
import subprocess
import winreg

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_long_paths():
    print("[*] Checking Long Paths support...")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
        winreg.CloseKey(key)
        if val == 1:
            print("    [OK] Long Paths are ENABLED.")
            return True
        else:
            print("    [WARN] Long Paths are DISABLED.")
            return False
    except FileNotFoundError:
        print("    [WARN] Long Paths registry key not found.")
        return False

def fix_long_paths():
    print("    [FIX] Enabling Long Paths...")
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\FileSystem", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "LongPathsEnabled", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
        print("    [SUCCESS] Fixed.")
    except Exception as e:
        print(f"    [FAIL] Failed: {e}")

def check_execution_policy():
    print("[*] Checking PowerShell Execution Policy...")
    try:
        # Check CurrentUser scope
        cmd = ["powershell", "-Command", "Get-ExecutionPolicy -Scope CurrentUser"]
        out = subprocess.check_output(cmd).decode().strip()
        print(f"    Current Policy (User): {out}")
        
        if out in ["RemoteSigned", "Unrestricted", "Bypass"]:
            print("    [OK] User Execution Policy is good.")
            return True
        else:
            print(f"    [WARN] User Execution Policy is '{out}' (Restricted?). Scripts may fail.")
            return False
    except Exception as e:
        print(f"    [FAIL] Failed to check: {e}")
        return False

def fix_execution_policy():
    print("    [FIX] Setting Execution Policy to RemoteSigned (CurrentUser)...")
    try:
        cmd = ["powershell", "-Command", "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"]
        subprocess.check_call(cmd)
        print("    [SUCCESS] Fixed.")
    except Exception as e:
        print(f"    [FAIL] Failed: {e}")

def check_developer_mode():
    print("[*] Checking Developer Mode...")
    # This is harder to check directly via registry reliably across all Win versions, 
    # but we can try checking the symlink privilege.
    # SeCreateSymbolicLinkPrivilege is normally only for Admins unless Dev Mode is on.
    
    # Alternative: Reg key HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock\AllowDevelopmentWithoutDevLicense
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(key, "AllowDevelopmentWithoutDevLicense")
        winreg.CloseKey(key)
        if val == 1:
            print("    [OK] Developer Mode appears ENABLED (Registry).")
            return True
        else:
            print("    [WARN] Developer Mode appears DISABLED.")
            return False
    except FileNotFoundError:
        print("    [WARN] Developer Mode registry key not found.")
        return False

def check_python_symlink():
    print("[*] Checking Symlink Creation...")
    test_link = "test_symlink_check.lnk"
    test_target = "test_target.txt"
    try:
        with open(test_target, "w") as f: f.write("test")
        os.symlink(test_target, test_link)
        print("    [OK] Symlinks work.")
        os.remove(test_link)
        os.remove(test_target)
        return True
    except OSError as e:
        print(f"    [WARN] Symlinks Failed: {e}")
        print("           (This often requires Developer Mode or Admin)")
        if os.path.exists(test_target): os.remove(test_target)
        return False

def run_diagnostics():
    print("====================================")
    print("   WINDOWS SCRIPTING HEALTH CHECK   ")
    print("====================================")
    
    if not is_admin():
        print("\n[!] WARNING: Not running as Administrator.")
        print("    Some fixes cannot be applied automatically.")
        print("    Please right-click this script/terminal and 'Run as Administrator'.\n")
    
    # 1. Long Paths
    if not check_long_paths() and is_admin():
        fix_long_paths()
        
    # 2. Execution Policy
    if not check_execution_policy():
         # We can fix CurrentUser policy even without Admin usually
         fix_execution_policy()
         
    # 3. Developer Mode (Info only, hard to toggle programmatically safely)
    check_developer_mode()
    
    # 4. Symlinks
    check_python_symlink()
    
    print("\n------------------------------------")
    print("RECOMMENDATIONS:")
    print("------------------------------------")
    print("1. If 'Developer Mode' is disabled, enable it in Windows Settings -> Update & Security -> For developers.")
    print("   -> This allows symlinks without Admin execution.")
    print("2. If Python scripts fail to find files, 'Long Paths' might be the culprit.")
    print("3. Always install Python with 'Add Python to PATH' checked.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    # If running directly (not imported), we can try to re-launch as admin if needed
    # But usually better to let user see the status first.
    try:
        run_diagnostics()
    except Exception as e:
        print(f"Critial Error: {e}")
        input()
