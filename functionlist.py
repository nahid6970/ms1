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
