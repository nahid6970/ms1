import curses
import os
import sys
import subprocess
from typing import Dict, List, Callable, Optional, Tuple
import threading
import time

class WindowsUtil:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_selection = 0
        self.current_submenu_selection = 0
        self.in_submenu = False
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Selected
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Title
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Error
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warning
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Info
        
        # Hide cursor
        curses.curs_set(0)
        
        # Unified menu structure
        self.menu_data = [
            {
                "title": "Git Update",
                "description": "Update the ms1 repository",
                "action": self.update_ms1_repo
            },
            {
                "title": "System Information",
                "description": "View detailed system information and monitoring",
                "submenu": [
                    {"title": "Show System Info", "action": ("systeminfo", "Showing system information")},
                    {"title": "Hardware Info", "action": ("powershell -Command \"Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors\"", "Showing hardware information")},
                    {"title": "Network Info", "action": ("ipconfig /all", "Showing network information")},
                    {"title": "Process Monitor", "action": ("powershell -Command \"Get-Process | Sort-Object CPU -Descending | Select-Object -First 20\"", "Opening process monitor")},
                    {"title": "Disk Usage", "action": ("powershell -Command \"Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name='Size(GB)';Expression={[math]::Round($_.Size/1GB,2)}}, @{Name='FreeSpace(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}\"", "Showing disk usage")},
                ]
            },
            {
                "title": "Package Management",
                "description": "Manage Windows packages with Scoop and Chocolatey",
                "submenu": [
                    {"title": "Update Scoop", "action": ("scoop update", "Updating Scoop")},
                    {"title": "Install Scoop", "action": ("powershell -Command \"Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex\"", "Installing Scoop package manager")},
                    {"title": "Install Necessary Packages",
                        "action": (
                            "scoop install ack & "
                            "scoop install adb & "
                            "scoop install bat & "
                            "scoop install capture2text & "
                            "scoop install ditto & "
                            "scoop install ffmpeg & "
                            "scoop install highlight & "
                            "scoop install kitty & "
                            "scoop install neovim & "
                            "scoop install putty & "
                            "scoop install rssguard & "
                            "scoop install rufus & "
                            "scoop install yt-dlp",
                            "Installing Scoop packages"
                        )
                    },
                    {"title": "Remove Package", "action": self.remove_package},
                    {"title": "Search Packages", "action": self.search_packages},
                    {"title": "List Installed", "action": ("scoop list", "Listing installed packages")},
                    {"title": "Clean Cache", "action": ("scoop cache rm *", "Cleaning package cache")},
                    {"title": "Package Info", "action": self.package_info},
                ]
            },
            {
                "title": "System Maintenance",
                "description": "System cleanup and maintenance tasks",
                "submenu": [
                    {"title": "Windows Update", "action": ("powershell -Command \"Get-WindowsUpdate -Install -AcceptAll\"", "Running Windows Update")},
                    {"title": "Clean Temp Files", "action": ("powershell -Command \"Get-ChildItem -Path $env:TEMP -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue\"", "Cleaning temporary files")},
                    {"title": "Check Disk", "action": ("chkdsk C: /f", "Checking disk for errors")},
                    {"title": "System File Check", "action": ("sfc /scannow", "Running system file checker")},
                    {"title": "DISM Health Check", "action": ("DISM /Online /Cleanup-Image /CheckHealth", "Checking system image health")},
                    {"title": "Check Services", "action": ("powershell -Command \"Get-Service | Where-Object {$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'}\"", "Checking stopped services")},
                    {"title": "Manage Startup Programs", "action": ("powershell -Command \"Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location\"", "Managing startup programs")},
                ]
            },
            {
                "title": "Development Tools",
                "description": "Install common development tools and environments",
                "submenu": [
                    {"title": "Install Git", "action": ("scoop install git", "Installing Git")},
                    {"title": "Install Node.js", "action": ("scoop install nodejs", "Installing Node.js and npm")},
                    {"title": "Install Python", "action": ("scoop install python", "Installing Python")},
                    {"title": "Install Visual Studio Code", "action": ("scoop install vscode", "Installing Visual Studio Code")},
                    {"title": "Install Build Tools", "action": ("scoop install mingw", "Installing MinGW build tools")},
                ]
            },
            {
                "title": "Github-Projects",
                "description": "Install common development tools and environments",
                "submenu": [
                    {"title": "ChrisTitus WinUtility", "action": ('cmd /c start pwsh -Command "iwr -useb https://christitus.com/win | iex"', "Run Chris Titus Tech's Windows Utility")},
                    {"title": "Microsoft Activation Scripts (MAS)", "action": ('cmd /c start pwsh -Command "irm https://get.activated.win | iex"', "Run Microsoft Activation Scripts")},
                    {"title": "WIMUtil", "action": ('cmd /c start pwsh -Command "irm \'https://github.com/memstechtips/WIMUtil/raw/main/src/WIMUtil.ps1\' | iex"', "Run WIMUtil from GitHub")},
                    {"title": "Harden Windows Security Using GUI", "action": ('cmd /c start pwsh -Command "(irm \'https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1\')+\'P\'|iex"', "Harden Windows Security using GUI")},
                    {"title": "Winhance", "action": ( 'powershell -Command "Start-Process pwsh -ArgumentList \'-NoExit\', \'-Command irm https://github.com/memstechtips/Winhance/raw/main/Winhance.ps1 | iex\' -Verb RunAs"', "Run Winhance Utility as Admin" ) },
                    { "title": "AppControl Manager", "action": ( 'powershell -Command "Start-Process pwsh -ArgumentList \'-NoExit\', \'-Command (irm https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1)^+\'AppControl\' ^| iex\' -Verb RunAs"', "Run AppControl Manager as Admin" ) }
                ]
            },
            {
                "title": "Quit",
                "description": "Exit ArchUtil",
                "action": "quit"
            }
        ]
    
    def get_terminal_size(self):
        """Get terminal dimensions"""
        return self.stdscr.getmaxyx()
    
    def draw_border(self, win, title=""):
        """Draw border around window with optional title"""
        win.box()
        if title:
            win.addstr(0, 2, f" {title} ", curses.color_pair(2) | curses.A_BOLD)
    
    def draw_main_menu(self, win):
        """Draw the main menu on the left side"""
        win.clear()
        self.draw_border(win, "WindowsUtil - Main Menu")
        
        height, width = win.getmaxyx()
        
        for i, item in enumerate(self.menu_data):
            y = 2 + i
            if y >= height - 1:
                break
                
            if i == self.current_selection:
                win.addstr(y, 2, f">> {item['title']}", curses.color_pair(1) | curses.A_BOLD)
            else:
                win.addstr(y, 2, f"  {item['title']}")
        
        # Add navigation help
        help_y = height - 3
        win.addstr(help_y, 2, "↑↓: Navigate", curses.color_pair(6))
        win.addstr(help_y + 1, 2, "→: Enter | q: Quit", curses.color_pair(6))
        
        win.refresh()
    
    def draw_submenu(self, win):
        """Draw the submenu on the right side"""
        win.clear()
        
        if self.current_selection >= len(self.menu_data):
            return
            
        main_item = self.menu_data[self.current_selection]
        
        self.draw_border(win, main_item['title'])
        
        height, width = win.getmaxyx()
        
        submenu_items = main_item.get("submenu", [])
        action = main_item.get("action")

        if action == "quit":
            win.addstr(2, 2, "Press Enter to quit", curses.color_pair(4))
        elif submenu_items:
            # Draw submenu items
            for i, item in enumerate(submenu_items):
                y = 2 + i
                if y >= height - 5:
                    break
                
                if self.in_submenu and i == self.current_submenu_selection:
                    win.addstr(y, 2, f">> {item['title']}", curses.color_pair(1) | curses.A_BOLD)
                else:
                    win.addstr(y, 2, f"  {item['title']}")
        
        # Always add description if available, unless it's a quit action (handled above)
        if action != "quit":
            desc_y = height - 4
            desc = main_item.get("description", "")
            # Word wrap description
            if len(desc) > width - 4:
                desc = desc[:width-7] + "..."
            win.addstr(desc_y, 2, desc, curses.color_pair(6))
        
        # Add navigation help
        help_y = height - 2
        if self.in_submenu:
            win.addstr(help_y, 2, "↑↓: Navigate | ←: Back | Enter: Execute", curses.color_pair(6))
        elif action and not submenu_items: # If it's an action item without a submenu
            win.addstr(help_y, 2, "Enter: Execute | ←: Back", curses.color_pair(6))
        else:
            win.addstr(help_y, 2, "→: Enter submenu", curses.color_pair(6))
        
        win.refresh()
    
    def draw_status_bar(self, win):
        """Draw status bar at the bottom"""
        win.clear()
        height, width = win.getmaxyx()
        
        status_text = "WindowsUtil v1.0 - Windows System Utility"
        win.addstr(0, 2, status_text, curses.color_pair(2) | curses.A_BOLD)
        
        # Add system info (Windows doesn't have load average, show memory usage instead)
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_text = f"RAM: {memory.percent:.1f}%"
            win.addstr(0, width - len(memory_text) - 2, memory_text, curses.color_pair(6))
        except:
            pass
        
        win.refresh()
    
    def execute_command(self, command: str, description: str = ""):
        """Execute a command in a new window"""
        # Save current state
        curses.def_prog_mode()
        curses.endwin()

        # ANSI escape codes for colors
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        RESET = '\033[0m'

        # Clear the screen before executing the command
        os.system('cls' if os.name == 'nt' else 'clear')
        
        try:
            print(f"\n{BLUE}{description}{RESET}")
            print(f"Command: {command}")
            
            # Execute command
            result = subprocess.run(command, shell=True)
            
            if result.returncode == 0:
                print(f"\n{GREEN}✓ Success: {description}{RESET}")
            else:
                print(f"\n{RED}✗ Command failed with exit code: {result.returncode}{RESET}")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
            input("Press Enter to continue...")
        finally:
            # Restore curses mode
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def handle_submenu_action(self):
        """Handle submenu item selection"""
        main_item = self.menu_data[self.current_selection]
        submenu = main_item.get("submenu", [])
        
        if not submenu or self.current_submenu_selection >= len(submenu):
            return
            
        selected_item = submenu[self.current_submenu_selection]
        action = selected_item.get("action")
        
        if action:
            if callable(action):
                action()
            else:
                command, description = action
                self.execute_command(command, description)
    
    def necessarypkgs(self):
        """Install essential packages"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            self.execute_command(f"scoop install vim nano", f"Installing vim, nano")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)

    def install_package(self):
        """Install a package with user input"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter package name: ").strip()
            if package:
                self.execute_command(f"scoop install {package}", f"Installing {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def remove_package(self):
        """Remove a package with user input"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter package name: ").strip()
            if package:
                self.execute_command(f"scoop uninstall {package}", f"Removing {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def search_packages(self):
        """Search packages with user input"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            query = input("Enter search term: ").strip()
            if query:
                self.execute_command(f"scoop search {query}", f"Searching for '{query}'")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def package_info(self):
        """Show package information"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter package name: ").strip()
            if package:
                self.execute_command(f"scoop info {package}", f"Package info for {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def install_chocolatey_package(self):
        """Install Chocolatey package with user input"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter Chocolatey package name: ").strip()
            if package:
                self.execute_command(f"choco install {package} -y", f"Installing Chocolatey package {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def search_chocolatey(self):
        """Search Chocolatey packages"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            query = input("Enter search term: ").strip()
            if query:
                self.execute_command(f"choco search {query}", f"Searching Chocolatey for '{query}'")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def remove_chocolatey_package(self):
        """Remove Chocolatey package"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter Chocolatey package name: ").strip()
            if package:
                self.execute_command(f"choco uninstall {package} -y", f"Removing Chocolatey package {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)

    def update_ms1_repo(self):
        """Update the ms1 repository"""
        curses.def_prog_mode()
        curses.endwin()

        # ANSI escape codes for colors
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        try:
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{BLUE}Updating ms1 repository...{RESET}")
            # Get the current script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Try to find git repository root
            git_root = None
            current_dir = script_dir
            # Search up the directory tree for .git folder
            while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
                if os.path.exists(os.path.join(current_dir, '.git')):
                    git_root = current_dir
                    break
                current_dir = os.path.dirname(current_dir)
            
            if not git_root:
                print(f"{RED}Error: Not inside a git repository{RESET}")
                print(f"Current directory: {script_dir}")
                input("Press Enter to continue...")
                return
            
            print(f"Found git repository at: {git_root}")
            
            # Change to git repository directory
            os.chdir(git_root)
            
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                                capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{RED}Error: Not a valid git repository{RESET}")
                input("Press Enter to continue...")
                return
            
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                capture_output=True, text=True)
            if result.stdout.strip():
                print(f"{YELLOW}Warning: You have uncommitted changes:{RESET}")
                print(result.stdout)
                response = input("Continue with git pull? This might cause conflicts. (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("Operation cancelled.")
                    input("Press Enter to continue...")
                    return
            
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                capture_output=True, text=True)
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                print(f"Current branch: {current_branch}")
            else:
                print(f"{YELLOW}Warning: Could not determine current branch{RESET}")
            
            # Fetch latest changes
            print("Fetching latest changes...")
            result = subprocess.run(['git', 'fetch'], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{RED}Error fetching changes: {result.stderr}{RESET}")
                input("Press Enter to continue...")
                return
            
            # Pull changes - let git handle the output formatting
            print("Pulling changes...")
            result = subprocess.run(['git', 'pull'], text=True)
            
            if result.returncode == 0:
                print(f"\n{GREEN}✓ Git pull completed successfully{RESET}")
            else:
                print(f"\n{RED}✗ Git pull failed with exit code: {result.returncode}{RESET}")
                if "merge conflict" in (result.stderr or "").lower():
                    print(f"{YELLOW}You have merge conflicts. Please resolve them manually.{RESET}")
            
            input("\nPress Enter to continue...")
            
        except FileNotFoundError:
            print(f"{RED}Error: Git is not installed or not in PATH{RESET}")
            input("Press Enter to continue...")
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
            input("Press Enter to continue...")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def run(self):
        """Main application loop"""
        while True:
            # Get terminal size
            max_y, max_x = self.get_terminal_size()
            
            # Calculate window sizes
            left_width = max_x // 2
            right_width = max_x - left_width
            menu_height = max_y - 2
            
            # Create windows
            left_win = curses.newwin(menu_height, left_width, 0, 0)
            left_win.keypad(True)
            right_win = curses.newwin(menu_height, right_width, 0, left_width)
            status_win = curses.newwin(2, max_x, max_y - 2, 0)
            
            # Draw interface
            self.draw_main_menu(left_win)
            self.draw_submenu(right_win)
            self.draw_status_bar(status_win)
            
            # Handle input
            try:
                key = left_win.getch()
                
                if key == ord('q') or key == 27:  # q or ESC
                    break
                elif key == curses.KEY_UP:
                    if self.in_submenu:
                        self.current_submenu_selection = max(0, self.current_submenu_selection - 1)
                    else:
                        self.current_selection = max(0, self.current_selection - 1)
                elif key == curses.KEY_DOWN:
                    if self.in_submenu:
                        main_item = self.menu_data[self.current_selection]
                        submenu = main_item.get("submenu", [])
                        if submenu:
                            max_sub = len(submenu) - 1
                            self.current_submenu_selection = min(max_sub, self.current_submenu_selection + 1)
                    else:
                        self.current_selection = min(len(self.menu_data) - 1, self.current_selection + 1)
                elif key == curses.KEY_RIGHT:
                    if not self.in_submenu:
                        main_item = self.menu_data[self.current_selection]
                        if main_item.get("submenu"):
                            self.in_submenu = True
                            self.current_submenu_selection = 0
                elif key == curses.KEY_LEFT:
                    if self.in_submenu:
                        self.in_submenu = False
                elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:  # Enter
                    main_item = self.menu_data[self.current_selection]
                    if main_item.get("action") == "quit":
                        break
                    elif self.in_submenu:
                        self.handle_submenu_action()
                    else:
                        # Check if the main item has a direct action
                        if callable(main_item.get("action")):
                            main_item["action"]()
                        # Enter submenu if available
                        elif main_item.get("submenu"):
                            self.in_submenu = True
                            self.current_submenu_selection = 0
                
            except KeyboardInterrupt:
                break

def main():
    """Main entry point"""
    def app(stdscr):
        windowsutil = WindowsUtil(stdscr)
        windowsutil.run()
    
    try:
        curses.wrapper(app)
    except KeyboardInterrupt:
        print("\nExiting WindowsUtil...")
        sys.exit(0)

if __name__ == "__main__":
    main()