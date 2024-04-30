from datetime import datetime
from PIL import Image, ImageTk
from pyadl import ADLManager
from time import strftime
# from tkinter import Canvas, Scrollbar
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
import ctypes
import keyboard
import os
import psutil
import pyautogui
import subprocess
import sys
import threading
import time
import tkinter as tk
import win32gui
import win32process


# def start_bar_1(event):
#     subprocess.Popen(["cmd /c start C:\\ms1\\scripts\\python\\bar_1.py"], shell=True)
def start_bar_1(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\scripts\\python\\bar_1.py", "-WindowStyle", "Hidden"], shell=True)

def start_shortcut(event):
    subprocess.Popen(["powershell", "start-process", "C:\\ms1\\shortcut.py", "-WindowStyle", "Hidden"], shell=True)

def start_backup(event):
    subprocess.Popen(["Start", "pwsh",  "-NoExit", "-Command", "& {$host.UI.RawUI.WindowTitle='GiTSync' ; C:\\ms1\\backup.ps1 ; C:\\ms1\\scripts\\Github\\ms1u.ps1 ; C:\\ms1\\scripts\\Github\\ms2u.ps1 ; cd ~}"], shell=True)

def start_fzf_c():
    subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; fzf --preview=\'highlight -O ansi -l {}\'"'], shell=True)

def start_fzf_d():
    subprocess.Popen(["powershell", "-Command", 'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; fzf --preview=\'bat {}\'"'], shell=True)

def start_ack_c():
    input_text = insert_input()  # Assuming insert_input() is a function that returns the desired input
    subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd C:\\ ; ack {input_text}"'], shell=True)

def start_ack_d():
    input_text = insert_input()  # Assuming insert_input() is a function that returns the desired input
    subprocess.Popen(["powershell", "-Command", f'Start-Process powershell -ArgumentList "-NoExit -Command cd D:\\ ; ack {input_text}"'], shell=True)

def start_find_file():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])

def start_find_pattern():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_file.ps1"])

def start_find_size():
    subprocess.Popen(["powershell", "start", "C:\\ms1\\scripts\\find\\find_size.ps1"])
