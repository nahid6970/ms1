import argparse
import subprocess
import pyautogui
from datetime import datetime

def rclone_sync():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\sync.ps1"])

def windows_terminal():
    subprocess.Popen(["wt"])

def powertoys_ruler():
    pyautogui.hotkey('win', 'shift', 'm')

def powertoys_color_picker():
    pyautogui.hotkey('win', 'shift', 'c')

def powertoys_TextExtract():
    pyautogui.hotkey('win', 'shift', 't')

def capture2text():
    pyautogui.hotkey('win', 'ctrl', 'alt', 'shift', 'q')

def powertoys_mouse_crosshair():
    pyautogui.hotkey('win', 'alt', 'p')

def stop_wsa():
    subprocess.Popen(["powershell", "Stop-Process -Name WsaClient -Force"])

def main(args):
    if args.action == 'rclone_sync':
        rclone_sync()
    elif args.action == 'windows_terminal':
        windows_terminal()
    elif args.action == 'powertoys_ruler':
        powertoys_ruler()
    elif args.action == 'powertoys_TextExtract':
        powertoys_TextExtract()
    elif args.action == 'capture2text':
        capture2text()
    elif args.action == 'powertoys_mouse_crosshair':
        powertoys_mouse_crosshair()
    elif args.action == 'stop_wsa':
        stop_wsa()
    elif args.action == 'powertoys_color_picker':
        powertoys_color_picker()
    else:
        print("Invalid action")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Utility Buttons Command Line Interface")
    parser.add_argument("action", type=str, help="Action to perform")
    args = parser.parse_args()
    main(args)
