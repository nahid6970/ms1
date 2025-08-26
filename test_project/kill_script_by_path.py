import sys
import subprocess
import psutil
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QFont, QColor
import os

class ProcessManager:
    def __init__(self):
        # Define your target processes here
        self.target_processes = {
            r"C:\Users\nahid\ms\ms1\scripts\flask\5000_myhome\app.py": "MyHome",
            r"C:\Users\nahid\ms\ms1\scripts\flask\5001_share_text\share_text.py": "5001_share_text",
            r"C:\Users\nahid\ms\ms1\scripts\flask\5002_upload_files\upload_files.py": "5002_upload_files"
        }
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.create_icon()
        self.tray_icon.setIcon(self.icon)
        self.tray_icon.setToolTip("Process Manager")
        
        # Connect left click to show menu
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        
        # Create persistent menu
        self.menu = QMenu()
        self.create_menu()
        
        # Timer to refresh menu periodically (only when menu is not visible)
        self.timer = QTimer()
        self.timer.timeout.connect(self.auto_refresh_check)
        self.timer.start(5000)  # Check every 5 seconds
        
    def create_icon(self):
        """Create a red 'K' icon for the tray"""
        # Create a larger pixmap for better quality
        size = 32
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set font for the 'K'
        font = QFont("Arial", int(size * 0.7), QFont.Bold)
        painter.setFont(font)
        
        # Set red color for the text
        painter.setPen(QColor(220, 20, 20))  # Red color
        
        # Draw the 'K' centered
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "K")
        
        painter.end()
        
        self.icon = QIcon(pixmap)
        
    def auto_refresh_check(self):
        """Only refresh if menu is not visible"""
        if not self.menu.isVisible():
            self.update_menu()
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon clicks"""
        if reason == QSystemTrayIcon.Trigger:  # Left click
            self.show_menu()
        elif reason == QSystemTrayIcon.Context:  # Right click
            self.show_menu()
    
    def show_menu(self):
        """Show the menu at cursor position"""
        cursor = self.app.desktop().cursor().pos()
        self.menu.popup(cursor)
    
    def create_menu(self):
        """Create the context menu"""
        # Clear existing menu items
        self.menu.clear()
        
        running_processes = self.find_target_processes()
        
        if running_processes:
            # Add running process items
            for process_info in running_processes:
                file_path, display_name, pid, process_name = process_info
                action_text = f"🔴 {display_name} - {process_name} (PID: {pid})"
                action = QAction(action_text, self.app)
                action.triggered.connect(lambda checked, p=pid, name=display_name: self.kill_process(p, name))
                self.menu.addAction(action)
        else:
            # Show "No target processes running" when none are found
            no_process_action = QAction("⚫ No target processes running", self.app)
            no_process_action.setEnabled(False)
            self.menu.addAction(no_process_action)
        
        self.menu.addSeparator()
        
        # Add refresh action
        refresh_action = QAction("🔄 Refresh", self.app)
        refresh_action.triggered.connect(self.update_menu)
        self.menu.addAction(refresh_action)
        
        # Add quit action
        quit_action = QAction("❌ Quit", self.app)
        quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(quit_action)
        
        # Set the menu to the tray icon (but don't rely on it for showing)
        self.tray_icon.setContextMenu(self.menu)
    
    def find_target_processes(self):
        """Find running processes that match our target file paths"""
        running_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Check if this is a Python process
                    if proc.info['name'] and 'python' in proc.info['name'].lower():
                        cmdline = proc.info['cmdline']
                        if cmdline and len(cmdline) > 1:
                            # Get the script path (usually the second argument after python.exe)
                            script_path = None
                            for arg in cmdline[1:]:
                                if arg.endswith('.py'):
                                    script_path = os.path.abspath(arg)
                                    break
                            
                            if script_path:
                                # Check if this script path matches any of our targets
                                for target_path, display_name in self.target_processes.items():
                                    if os.path.abspath(target_path).lower() == script_path.lower():
                                        running_processes.append((
                                            target_path,
                                            display_name,
                                            proc.info['pid'],
                                            proc.info['name']
                                        ))
                                        break
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process might have died or we don't have access
                    continue
                except Exception as e:
                    # Skip any other errors
                    continue
        
        except Exception as e:
            print(f"Error finding processes: {e}")
        
        return running_processes
    
    def kill_process(self, pid, display_name):
        """Kill the process by PID"""
        try:
            # First verify the process still exists
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.update_menu()
                return
            
            if sys.platform == "win32":
                # Use taskkill on Windows
                try:
                    kill_command = f"taskkill /PID {pid} /F"
                    result = subprocess.check_output(kill_command, shell=True, text=True, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    # Silently handle errors - process might already be terminated
                    pass
            else:
                # Use kill on Linux/Mac
                try:
                    subprocess.run(f'kill -9 {pid}', shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    # Silently handle errors
                    pass
            
            # Wait a moment and update menu
            import time
            time.sleep(1)
            self.update_menu()
            
        except Exception as e:
            # Silently handle any other errors
            pass
    
    def update_menu(self):
        """Update the context menu with current process status"""
        self.create_menu()
    
    def show_message(self, title, message):
        """Show a tray notification"""
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 3000)
    
    def quit_app(self):
        """Quit the application"""
        self.timer.stop()
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        """Run the application"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", "System tray not available on this system.")
            return
        
        self.tray_icon.show()
        
        return self.app.exec_()

if __name__ == "__main__":
    # Check if required modules are installed
    try:
        import psutil
        from PyQt5.QtWidgets import QApplication
    except ImportError as e:
        print(f"Required module not installed: {e}")
        print("Please install required modules:")
        print("pip install psutil PyQt5")
        sys.exit(1)
    
    process_manager = ProcessManager()
    sys.exit(process_manager.run())