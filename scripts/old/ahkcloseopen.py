import os
import psutil

# Specify the path to the AHK script file
ahk_script_path = r"C:\ms1\scripts\ahkscripts.ahk"

# Find and terminate the "AutoHotkeyU64" process
for process in psutil.process_iter(['pid', 'name']):
    if process.info['name'] == "AutoHotkeyU64.exe":
        try:
            psutil.Process(process.info['pid']).terminate()
        except:
            pass

# Open the AHK script file
try:
    os.startfile(ahk_script_path)
except:
    pass
