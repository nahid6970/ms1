#!/usr/bin/env python3
"""
PyQt6 conversion of mypygui.py with individual button styling
A comprehensive system monitoring and utility GUI application
"""

import sys
import os
import time
import threading
import subprocess
import psutil
from datetime import datetime
from queue import Queue
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                            QVBoxLayout, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint
from PyQt6.QtGui import QFont, QPalette, QColor, QMouseEvent, QFontDatabase

def calculate_time_to_appear(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to appear: {elapsed_time:.2f} seconds")

start_time = time.time()

# Github status
# Define your repositories here
queue = Queue()
repos = [
    {"name": "ms1", "path": "C:\\@delta\\ms1", "label": "ms1"},
    {"name": "db", "path": "C:\\@delta\\db", "label": "db"},
    {"name": "test", "path": "C:\\Users\\nahid\\ms\\test", "label": "test"},
    # {"name": "ms2", "path": "C:\\ms2", "label": "2"},
    # {"name": "ms3", "path": "C:\\ms3", "label": "3"},
    # Add more as needed
]

status_labels = {}

def check_git_status(git_path, queue):
    if not os.path.exists(git_path):
        queue.put((git_path, "Invalid", "#000000"))
        return
    os.chdir(git_path)
    git_status = subprocess.run(["git", "status"], capture_output=True, text=True)
    
    label_text = next((r["label"] for r in repos if r["path"] == git_path), "?")
    
    if "nothing to commit, working tree clean" in git_status.stdout:
        queue.put((git_path, label_text, "#00ff21"))  # Green
    else:
        queue.put((git_path, label_text, "#fe1616"))  # Red


def show_git_changes(git_path):
    if not os.path.exists(git_path):
        print("Invalid path")
        return
    os.chdir(git_path)
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "git status && git diff --stat"])

def git_backup(event):
    commands = " ; ".join([f"{r['path']}\\scripts\\Github\\{r['name']}u.ps1" for r in repos])
    subprocess.Popen([
        "Start", "pwsh", "-NoExit", "-Command",
        f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; {commands} ; cd ~}}"
    ], shell=True)

def delete_git_lock_files(event=None):
    for repo in repos:
        lock_file = os.path.join(repo["path"], ".git", "index.lock")
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"Deleted: {lock_file}")
            else:
                print(f"File not found: {lock_file}")
        except Exception as e:
            print(f"Error deleting {lock_file}: {e}")

def update_status():
    while True:
        for repo in repos:
            check_git_status(repo["path"], queue)
        time.sleep(1)

def update_gui():
    while True:
        try:
            git_path, text, color = queue.get_nowait()
            for repo in repos:
                if git_path == repo["path"]:
                    status_labels[repo["name"]].config(text=text, fg=color)
        except:
            pass
        time.sleep(0.1)



class SystemInfoThread(QThread):
    """Background thread for system information updates"""
    info_updated = pyqtSignal(dict)
    
    def run(self):
        while True:
            try:
                cpu_usage = psutil.cpu_percent(interval=1)
                ram_usage = psutil.virtual_memory().percent
                
                # Network speed calculation
                net_io = psutil.net_io_counters()
                if hasattr(self, 'last_bytes_sent'):
                    upload_speed = (net_io.bytes_sent - self.last_bytes_sent) / (1024 * 1024)
                    download_speed = (net_io.bytes_recv - self.last_bytes_recv) / (1024 * 1024)
                else:
                    upload_speed = download_speed = 0
                
                self.last_bytes_sent = net_io.bytes_sent
                self.last_bytes_recv = net_io.bytes_recv
                
                # Disk usage
                try:
                    disk_c_usage = psutil.disk_usage('C:').percent
                    disk_d_usage = psutil.disk_usage('D:').percent if os.path.exists('D:') else 0
                except:
                    disk_c_usage = disk_d_usage = 0
                
                info = {
                    'cpu': cpu_usage,
                    'ram': ram_usage,
                    'upload': upload_speed,
                    'download': download_speed,
                    'disk_c': disk_c_usage,
                    'disk_d': disk_d_usage
                }
                
                self.info_updated.emit(info)
                time.sleep(1)
            except Exception as e:
                print(f"Error in system info thread: {e}")
                time.sleep(1)

class HoverLabel(QLabel):
    """Custom label with hover effects and click handling"""
    
    def __init__(self, text="", custom_style="", hover_style="", 
                 font_size=16, font_family=None):
        super().__init__(text)
        
        # Get the best available font
        if font_family is None:
            font_family = self.get_best_font()
        
        # Store styles
        self.default_style = custom_style if custom_style else f"""
            QLabel {{
                color: #ffffff;
                background-color: #1d2027;
                font: bold {font_size}px '{font_family}';
                padding: 2px 3px;
                border-radius: 3px;
                text-align: center;
            }}
        """
        
        self.hover_style = hover_style if hover_style else f"""
            QLabel {{
                color: #ffffff;
                background-color: #2d3037;
                font: bold {font_size}px '{font_family}';
                padding: 2px 3px;
                border-radius: 3px;
                text-align: center;
            }}
        """
        
        # Click handlers
        self.left_click_command = None
        self.right_click_command = None
        self.ctrl_left_click_command = None
        self.ctrl_right_click_command = None
        
        # Set initial style
        self.setStyleSheet(self.default_style)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def enterEvent(self, event):
        """Mouse enter event"""
        self.setStyleSheet(self.hover_style)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse leave event"""
        self.setStyleSheet(self.default_style)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse clicks"""
        modifiers = QApplication.keyboardModifiers()
        
        if event.button() == Qt.MouseButton.LeftButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier and self.ctrl_left_click_command:
                self.ctrl_left_click_command()
            elif self.left_click_command:
                self.left_click_command()
        elif event.button() == Qt.MouseButton.RightButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier and self.ctrl_right_click_command:
                self.ctrl_right_click_command()
            elif self.right_click_command:
                self.right_click_command()
        
        super().mousePressEvent(event)
    
    def bind_left_click(self, command):
        """Bind left click command"""
        self.left_click_command = command
    
    def bind_right_click(self, command):
        """Bind right click command"""
        self.right_click_command = command
    
    def bind_ctrl_left_click(self, command):
        """Bind Ctrl+left click command"""
        self.ctrl_left_click_command = command
    
    def bind_ctrl_right_click(self, command):
        """Bind Ctrl+right click command"""
        self.ctrl_right_click_command = command
    
    @staticmethod
    def get_best_font():
        """Get the best available monospace font"""
        available_fonts = QFontDatabase.families()
        
        # Priority list of fonts to try
        preferred_fonts = [
            "JetBrainsMono Nerd Font Propo",
            "JetBrainsMono Nerd Font",
            "JetBrainsMono Nerd Font Mono", 
            "JetBrainsMono Nerd Font",
            "JetBrains Mono",
            "Consolas",
            "Courier New",
            "monospace"
        ]
        
        for font_name in preferred_fonts:
            if font_name in available_fonts:
                return font_name
        
        return "Consolas"  # Final fallback

class IconLabel(HoverLabel):
    """Special label for Nerd Font icons with optimized padding"""
    
    def __init__(self, icon_text="", color="#ffffff", bg_color="#1d2027", 
                 hover_color="#1d2027", hover_bg_color="#ffffff", font_size=16):
        
        # Get the best available font
        font_family = self.get_best_font()
        
        # Custom style for icons with minimal padding and perfect centering
        custom_style = f"""
            QLabel {{
                color: {color};
                background-color: {bg_color};
                font: bold {font_size}px '{font_family}';
                padding: 1px 1px;
                border-radius: 3px;
                text-align: center;
                qproperty-alignment: AlignCenter;
                min-width: {font_size + 4}px;
                max-width: {font_size + 8}px;
            }}
        """
        
        hover_style = f"""
            QLabel {{
                color: {hover_color};
                background-color: {hover_bg_color};
                font: bold {font_size}px '{font_family}';
                padding: 1px 1px;
                border-radius: 3px;
                text-align: center;
                qproperty-alignment: AlignCenter;
                min-width: {font_size + 4}px;
                max-width: {font_size + 8}px;
            }}
        """
        
        super().__init__(icon_text, custom_style, hover_style, font_size, font_family)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.init_ui()
        self.setup_system_monitoring()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Python GUI - PyQt6")
        self.setFixedSize(1920, 39)
        
        # Remove window frame and set always on top
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # Set window position (bottom of screen)
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() // 2 - 1920 // 2
        y = 993
        self.move(x, y)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1d2027;
                border: 1px solid red;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.setSpacing(5)
        
        # Create left and right sections
        self.create_left_section(main_layout)
        self.create_right_section(main_layout)
        
    def create_left_section(self, main_layout):
        """Create the left section with system info and tools"""
        left_frame = QFrame()
        left_layout = QHBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # System uptime
        self.uptime_label = QLabel("00:00:00")
        self.uptime_label.setStyleSheet("""
            QLabel {
                color: #6bc0f8;
                background-color: #1d2027;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
            }
        """)
        left_layout.addWidget(self.uptime_label)
        
        # OS Button
        os_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #59e3a7;
                    background-color: #1d2027;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #59e3a7;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        os_btn.bind_left_click(lambda: self.run_script("windows.py"))
        os_btn.bind_ctrl_left_click(lambda: self.edit_script("windows.py"))
        os_btn.bind_right_click(lambda: self.run_script("windows_alt.py"))
        left_layout.addWidget(os_btn)
        
        # Update Button
        update_btn = IconLabel("", 
            color="#16a2ff", 
            bg_color="#1d2027",
            hover_color="#ffffff", 
            hover_bg_color="#16a2ff",
            font_size=20
        )
        update_btn.bind_left_click(lambda: self.run_script("update.ps1"))
        update_btn.bind_ctrl_left_click(lambda: self.edit_script("update.ps1"))
        left_layout.addWidget(update_btn)
        
        # Tools Button
        tools_btn = IconLabel("", 
            color="#ffffff", 
            bg_color="#1d2027",
            hover_color="#1d2027", 
            hover_bg_color="#ffffff",
            font_size=20
        )
        tools_btn.bind_left_click(lambda: self.run_script("tools.py"))
        tools_btn.bind_ctrl_left_click(lambda: self.edit_script("tools.py"))
        left_layout.addWidget(tools_btn)
        
        # Startup Button
        startup_btn = IconLabel("", 
            color="#10b153", 
            bg_color="#1d2027",
            hover_color="#ffffff", 
            hover_bg_color="#10b153",
            font_size=25
        )
        startup_btn.bind_left_click(lambda: self.run_script("startup.py"))
        startup_btn.bind_ctrl_left_click(lambda: self.edit_script("startup.py"))
        left_layout.addWidget(startup_btn)
        
        # App Management Button
        app_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #26b2f3;
                    background-color: #1d2027;
                    font: bold 25px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #26b2f3;
                    font: bold 25px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        app_btn.bind_left_click(lambda: self.run_script("applist.py"))
        app_btn.bind_ctrl_left_click(lambda: self.edit_script("applist.py"))
        app_btn.bind_right_click(lambda: self.run_script("app_store.py"))
        app_btn.bind_ctrl_right_click(lambda: self.edit_script("app_store.py"))
        left_layout.addWidget(app_btn)
        
        # Rclone Button
        rclone_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #fcfcfc;
                    background-color: #1d2027;
                    font: bold 25px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #1d2027;
                    background-color: #fcfcfc;
                    font: bold 25px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        rclone_btn.bind_left_click(lambda: self.run_script("rclone_Script.py"))
        rclone_btn.bind_ctrl_left_click(lambda: self.edit_script("rclone_Script.py"))
        left_layout.addWidget(rclone_btn)
        
        # Folder Button
        folder_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #ffd900;
                    background-color: #1d2027;
                    font: bold 25px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #1d2027;
                    background-color: #ffd900;
                    font: bold 25px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        folder_btn.bind_left_click(lambda: self.run_script("folder.py"))
        folder_btn.bind_ctrl_left_click(lambda: self.edit_script("folder.py"))
        left_layout.addWidget(folder_btn)
        
        # Position/CrossHair Button
        pos_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #1d2027;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #1d2027;
                    background-color: #ffffff;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        pos_btn.bind_left_click(lambda: self.run_script("XY_CroosHair.py"))
        pos_btn.bind_ctrl_left_click(lambda: self.edit_script("XY_CroosHair.py"))
        pos_btn.bind_right_click(lambda: self.run_script("XY_CroosHairGemini.py"))
        pos_btn.bind_ctrl_right_click(lambda: self.edit_script("XY_CroosHairGemini.py"))
        left_layout.addWidget(pos_btn)
        
        # Color Tool Button
        color_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #c588fd;
                    background-color: #1d2027;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #c588fd;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        color_btn.bind_left_click(lambda: self.run_script("color_picker.py"))
        color_btn.bind_ctrl_left_click(lambda: self.edit_script("color_picker.py"))
        color_btn.bind_right_click(lambda: self.run_script("color_pallet_rand_fg_bgFF00.py"))
        color_btn.bind_ctrl_right_click(lambda: self.edit_script("color_pallet_rand_fg_bgFF00.py"))
        left_layout.addWidget(color_btn)
        
        # Info Button
        info_btn = HoverLabel("", 
            custom_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #1d2027;
                    font: bold 20px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #1d2027;
                    background-color: #ffffff;
                    font: bold 20px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        info_btn.bind_left_click(lambda: self.run_script("info.py"))
        info_btn.bind_ctrl_left_click(lambda: self.edit_script("info.py"))
        left_layout.addWidget(info_btn)
        
        # Virtual Monitor Button
        vm_btn = HoverLabel("2nd", 
            custom_style="""
                QLabel {
                    color: #8ab9ff;
                    background-color: #1d2027;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #8ab9ff;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        vm_btn.bind_left_click(lambda: self.run_script("2nd_Monitor.py"))
        vm_btn.bind_ctrl_left_click(lambda: self.edit_script("2nd_Monitor.py"))
        left_layout.addWidget(vm_btn)
        
        # Git Backup All Icon
        bkup = HoverLabel("\udb80\udea2", 
            custom_style="""
                QLabel {
                    color: #009fff;
                    background-color: #1d2027;
                    font: bold 18px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #009fff;
                    font: bold 18px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        bkup.bind_left_click(self.git_backup)
        left_layout.addWidget(bkup)
        
        # Add repo-specific labels and bindings dynamically
        self.repo_labels = {}
        for repo in repos:
            label = HoverLabel(repo["label"], 
                custom_style="""
                    QLabel {
                        color: #FFFFFF;
                        background-color: #1d2027;
                        font: bold 12px 'JetBrainsMono Nerd Font';
                        padding: 2px 4px;
                        border-radius: 3px;
                    }
                """,
                hover_style="""
                    QLabel {
                        color: #1d2027;
                        background-color: #FFFFFF;
                        font: bold 12px 'JetBrainsMono Nerd Font';
                        padding: 2px 4px;
                        border-radius: 3px;
                    }
                """
            )
            
            # Bind click events
            repo_path = repo["path"]
            label.bind_left_click(lambda p=repo_path: subprocess.Popen(
                ["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; cd {p.replace(os.sep, '/')} ; gitter}}"], shell=True
            ))
            label.bind_ctrl_left_click(lambda p=repo_path: subprocess.Popen(
                f'explorer "{p}"', shell=True
            ))
            label.bind_right_click(lambda p=repo_path: subprocess.Popen('start pwsh -NoExit -Command "lazygit"', cwd=p, shell=True))
            label.bind_ctrl_right_click(lambda p=repo_path: subprocess.Popen(
                ["Start", "pwsh", "-NoExit", "-Command", f"& {{$host.UI.RawUI.WindowTitle='Git Restore' ; cd {p.replace(os.sep, '/')} ; git restore . }}"], shell=True
            ))
            
            left_layout.addWidget(label)
            self.repo_labels[repo["name"]] = label
            status_labels[repo["name"]] = label
        
        # Git Lock File Cleaner Icon
        DelGitIgnore = HoverLabel("\udb82\udde7", 
            custom_style="""
                QLabel {
                    color: #ffffff;
                    background-color: #1d2027;
                    font: bold 18px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """,
            hover_style="""
                QLabel {
                    color: #1d2027;
                    background-color: #ffffff;
                    font: bold 18px 'JetBrainsMono Nerd Font';
                    padding: 2px 4px;
                    border-radius: 3px;
                }
            """
        )
        DelGitIgnore.bind_left_click(self.delete_git_lock_files)
        left_layout.addWidget(DelGitIgnore)
        
        main_layout.addWidget(left_frame)
        
    def create_right_section(self, main_layout):
        """Create the right section with system monitoring"""
        right_frame = QFrame()
        right_layout = QHBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Add stretch to push right section to the right
        main_layout.addStretch()
        
        # CPU Usage
        self.cpu_label = QLabel("0%")
        self.cpu_label.setStyleSheet("""
            QLabel {
                color: #14bcff;
                background-color: #1d2027;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 40px;
            }
        """)
        right_layout.addWidget(self.cpu_label)
        
        # RAM Usage
        self.ram_label = QLabel("0%")
        self.ram_label.setStyleSheet("""
            QLabel {
                color: #ff934b;
                background-color: #1d2027;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 40px;
            }
        """)
        right_layout.addWidget(self.ram_label)
        
        # GPU Usage (placeholder)
        self.gpu_label = QLabel("0%")
        self.gpu_label.setStyleSheet("""
            QLabel {
                color: #00ff21;
                background-color: #1d2027;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 40px;
            }
        """)
        right_layout.addWidget(self.gpu_label)
        
        # Disk C Usage
        self.disk_c_label = QLabel(" 0%")
        self.disk_c_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #044568;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 50px;
            }
        """)
        right_layout.addWidget(self.disk_c_label)
        
        # Disk D Usage
        self.disk_d_label = QLabel(" 0%")
        self.disk_d_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #044568;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 50px;
            }
        """)
        right_layout.addWidget(self.disk_d_label)
        
        # Upload Speed
        self.upload_label = QLabel("▲ 0.00")
        self.upload_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #1d2027;
                font: bold 14px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 60px;
            }
        """)
        right_layout.addWidget(self.upload_label)
        
        # Download Speed
        self.download_label = QLabel("▼ 0.00")
        self.download_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #1d2027;
                font: bold 14px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
                min-width: 60px;
            }
        """)
        right_layout.addWidget(self.download_label)
        
        # Current Time
        self.time_label = QLabel()
        self.time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: #1d2027;
                font: bold 16px 'JetBrainsMono Nerd Font';
                padding: 2px 8px;
                border-radius: 3px;
            }
        """)
        right_layout.addWidget(self.time_label)
        
        main_layout.addWidget(right_frame)
        
    def setup_system_monitoring(self):
        """Setup system monitoring thread"""
        self.system_thread = SystemInfoThread()
        self.system_thread.info_updated.connect(self.update_system_info)
        self.system_thread.start()
        
    def setup_timers(self):
        """Setup update timers"""
        # Uptime timer
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)  # Update every second
        
        # Time timer
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)  # Update every second
        
        # Git status timer
        self.git_timer = QTimer()
        self.git_timer.timeout.connect(self.update_git_status_gui)
        self.git_timer.start(500)  # Update every 500ms (less frequent)
        
        # Start background threads for git status
        self.start_git_monitoring()
    
    def start_git_monitoring(self):
        """Start git status monitoring threads"""
        # Initialize status tracking
        self.last_git_status = {}
        for repo in repos:
            self.last_git_status[repo["name"]] = None
        
        # Start background threads
        status_thread = threading.Thread(target=update_status, daemon=True)
        status_thread.start()
        
    def update_system_info(self, info):
        """Update system information labels"""
        # CPU
        cpu = info['cpu']
        self.cpu_label.setText(f"{cpu:.1f}%")
        if cpu > 80:
            self.cpu_label.setStyleSheet("""
                QLabel {
                    color: #1d2027;
                    background-color: #14bcff;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 40px;
                }
            """)
        else:
            self.cpu_label.setStyleSheet("""
                QLabel {
                    color: #14bcff;
                    background-color: #1d2027;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 40px;
                }
            """)
        
        # RAM
        ram = info['ram']
        self.ram_label.setText(f"{ram:.1f}%")
        if ram > 80:
            self.ram_label.setStyleSheet("""
                QLabel {
                    color: #1d2027;
                    background-color: #ff934b;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 40px;
                }
            """)
        else:
            self.ram_label.setStyleSheet("""
                QLabel {
                    color: #ff934b;
                    background-color: #1d2027;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 40px;
                }
            """)
        
        # Disk usage
        disk_c = info['disk_c']
        self.disk_c_label.setText(f" {disk_c:.1f}%")
        if disk_c > 90:
            self.disk_c_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #f12c2f;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 50px;
                }
            """)
        
        disk_d = info['disk_d']
        self.disk_d_label.setText(f" {disk_d:.1f}%")
        if disk_d > 90:
            self.disk_d_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background-color: #f12c2f;
                    font: bold 16px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 50px;
                }
            """)
        
        # Network speeds
        upload = info['upload']
        download = info['download']
        
        self.upload_label.setText(f"▲ {upload:.2f}")
        self.download_label.setText(f"▼ {download:.2f}")
        
        # Color coding for network speeds
        for label, speed in [(self.upload_label, upload), (self.download_label, download)]:
            if speed < 0.1:
                bg_color = "#1d2027"
                fg_color = "#ffffff"
            elif speed < 0.5:
                bg_color = "#A8E4A8"
                fg_color = "#000000"
            elif speed < 1:
                bg_color = "#67D567"
                fg_color = "#000000"
            else:
                bg_color = "#32AB32"
                fg_color = "#000000"
            
            label.setStyleSheet(f"""
                QLabel {{
                    color: {fg_color};
                    background-color: {bg_color};
                    font: bold 14px 'JetBrainsMono Nerd Font';
                    padding: 2px 8px;
                    border-radius: 3px;
                    min-width: 60px;
                }}
            """)
    
    def update_uptime(self):
        """Update system uptime"""
        try:
            uptime_seconds = psutil.boot_time()
            current_time = datetime.now().timestamp()
            uptime = current_time - uptime_seconds
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f" {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.uptime_label.setText(uptime_str)
        except Exception as e:
            print(f"Error updating uptime: {e}")
    
    def update_time(self):
        """Update current time"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
    
    def git_backup(self):
        """Execute git backup for all repositories"""
        commands = " ; ".join([f"{r['path']}\\scripts\\Github\\{r['name']}u.ps1" for r in repos])
        subprocess.Popen([
            "Start", "pwsh", "-NoExit", "-Command",
            f"& {{$host.UI.RawUI.WindowTitle='GiTSync' ; {commands} ; cd ~}}"
        ], shell=True)
    
    def delete_git_lock_files(self):
        """Delete git lock files from all repositories"""
        for repo in repos:
            lock_file = os.path.join(repo["path"], ".git", "index.lock")
            try:
                if os.path.exists(lock_file):
                    os.remove(lock_file)
                    print(f"Deleted: {lock_file}")
                else:
                    print(f"File not found: {lock_file}")
            except Exception as e:
                print(f"Error deleting {lock_file}: {e}")
    
    def update_git_status_gui(self):
        """Update git status in GUI"""
        try:
            while not queue.empty():
                git_path, text, color = queue.get_nowait()
                for repo in repos:
                    if git_path == repo["path"] and repo["name"] in self.repo_labels:
                        # Check if status actually changed
                        current_status = (text, color)
                        if self.last_git_status.get(repo["name"]) == current_status:
                            continue  # Skip if no change
                        
                        # Update tracking
                        self.last_git_status[repo["name"]] = current_status
                        
                        label = self.repo_labels[repo["name"]]
                        # Update the label text
                        label.setText(text)
                        
                        # Update both default and hover styles with new color
                        new_default_style = f"""
                            QLabel {{
                                color: {color};
                                background-color: #1d2027;
                                font: bold 12px 'JetBrainsMono Nerd Font';
                                padding: 2px 4px;
                                border-radius: 3px;
                            }}
                        """
                        
                        new_hover_style = f"""
                            QLabel {{
                                color: #1d2027;
                                background-color: {color};
                                font: bold 12px 'JetBrainsMono Nerd Font';
                                padding: 2px 4px;
                                border-radius: 3px;
                            }}
                        """
                        
                        # Update the label's stored styles
                        label.default_style = new_default_style
                        label.hover_style = new_hover_style
                        
                        # Only apply default style if not currently being hovered
                        if not label.underMouse():
                            label.setStyleSheet(new_default_style)
        except Exception as e:
            pass
    
    def run_script(self, script_name):
        """Run a script file"""
        try:
            # Adjust paths as needed for your system
            script_path = f"C:\\@delta\\ms1\\scripts\\{script_name}"
            subprocess.Popen(f'cmd /c start "{script_path}"', shell=True)
        except Exception as e:
            print(f"Error running script {script_name}: {e}")
    
    def edit_script(self, script_name):
        """Edit a script file in VS Code"""
        try:
            script_path = f"C:\\@delta\\ms1\\scripts\\{script_name}"
            subprocess.Popen(f'cmd /c code "{script_path}"', shell=True)
        except Exception as e:
            print(f"Error editing script {script_name}: {e}")
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

def main():
    """Main application entry point"""
    # PyQt6 handles high DPI automatically, no need to set attributes
    
    app = QApplication(sys.argv)
    
    # Check available fonts and set default font
    available_fonts = QFontDatabase.families()
    
    # Try different variations of the font name
    font_names = ["JetBrainsMono Nerd Font", "JetBrainsMono Nerd Font Mono", "JetBrainsMono Nerd Font", "JetBrains Mono", "Consolas"]
    selected_font = "Consolas"  # Fallback font
    
    for font_name in font_names:
        if font_name in available_fonts:
            selected_font = font_name
            print(f"Using font: {selected_font}")
            break
    else:
        print(f"JetBrainsMono Nerd Font not found. Available fonts: {[f for f in available_fonts if 'jet' in f.lower() or 'mono' in f.lower()]}")
        print(f"Using fallback font: {selected_font}")
    
    # Set application default font
    app.setFont(QFont(selected_font, 12))
    
    # Set application properties
    app.setApplicationName("Python GUI - PyQt6")
    app.setApplicationVersion("1.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Calculate startup time
    calculate_time_to_appear(start_time)
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
