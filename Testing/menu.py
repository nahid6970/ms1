#!/usr/bin/env python3
"""
ArchUtil - A LinUtil-inspired dynamic TUI menu system for Arch Linux
Features arrow key navigation with live submenu preview
"""

import curses
import os
import sys
import subprocess
from typing import Dict, List, Callable, Optional, Tuple
import threading
import time

class ArchUtil:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_selection = 0
        self.current_submenu_selection = 0
        self.in_submenu = False
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Selected
        curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Title
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Error
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warning
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Info
        
        # Hide cursor
        curses.curs_set(0)
        
        # Menu structure
        self.main_menu = [
            "System Information",
            "Package Management", 
            "System Maintenance",
            "AUR Helper",
            "Development Tools",
            "Quit"
        ]
        
        self.submenus = {
            "System Information": [
                "Show System Info",
                "Hardware Info",
                "Network Info",
                "Process Monitor",
                "Disk Usage"
            ],
            "Package Management": [
                "Update System",
                "Install Package",
                "Remove Package", 
                "Search Packages",
                "List Installed",
                "Clean Cache",
                "Package Info"
            ],
            "System Maintenance": [
                "Update Mirrors",
                "Clean System Logs",
                "Check Filesystem",
                "Update Locate DB",
                "Rebuild Initramfs",
                "Check Services",
                "Manage Startup Services"
            ],
            "AUR Helper": [
                "Install yay",
                "Update AUR Packages",
                "Install AUR Package",
                "Search AUR",
                "Remove AUR Package",
                "List AUR Packages"
            ],
            "Development Tools": [
                "Install Git",
                "Install VSCode",
                "Install Docker",
                "Install Node.js",
                "Install Python Tools",
                "Install Build Tools"
            ]
        }
        
        self.menu_descriptions = {
            "System Information": "View detailed system information and monitoring",
            "Package Management": "Manage Arch packages with pacman",
            "System Maintenance": "System cleanup and maintenance tasks",
            "AUR Helper": "Manage AUR packages with yay helper",
            "Development Tools": "Install common development tools and environments",
            "Quit": "Exit ArchUtil"
        }
    
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
        self.draw_border(win, "ArchUtil - Main Menu")
        
        height, width = win.getmaxyx()
        
        for i, item in enumerate(self.main_menu):
            y = 2 + i
            if y >= height - 1:
                break
                
            if i == self.current_selection:
                win.addstr(y, 2, f"  {item}", curses.color_pair(1) | curses.A_BOLD)
            else:
                win.addstr(y, 2, f"  {item}")
        
        # Add navigation help
        help_y = height - 3
        win.addstr(help_y, 2, "↑↓: Navigate", curses.color_pair(6))
        win.addstr(help_y + 1, 2, "→: Enter | q: Quit", curses.color_pair(6))
        
        win.refresh()
    
    def draw_submenu(self, win):
        """Draw the submenu on the right side"""
        win.clear()
        
        if self.current_selection >= len(self.main_menu):
            return
            
        main_item = self.main_menu[self.current_selection]
        
        if main_item == "Quit":
            self.draw_border(win, "Quit")
            win.addstr(2, 2, "Press Enter to quit", curses.color_pair(4))
            win.refresh()
            return
        
        if main_item not in self.submenus:
            return
            
        self.draw_border(win, main_item)
        
        height, width = win.getmaxyx()
        submenu_items = self.submenus[main_item]
        
        # Draw submenu items
        for i, item in enumerate(submenu_items):
            y = 2 + i
            if y >= height - 5:
                break
                
            if self.in_submenu and i == self.current_submenu_selection:
                win.addstr(y, 2, f"  {item}", curses.color_pair(1) | curses.A_BOLD)
            else:
                win.addstr(y, 2, f"  {item}")
        
        # Add description
        if main_item in self.menu_descriptions:
            desc_y = height - 4
            desc = self.menu_descriptions[main_item]
            # Word wrap description
            if len(desc) > width - 4:
                desc = desc[:width-7] + "..."
            win.addstr(desc_y, 2, desc, curses.color_pair(6))
        
        # Add navigation help
        help_y = height - 2
        if self.in_submenu:
            win.addstr(help_y, 2, "↑↓: Navigate | ←: Back | Enter: Execute", curses.color_pair(6))
        else:
            win.addstr(help_y, 2, "→: Enter submenu", curses.color_pair(6))
        
        win.refresh()
    
    def draw_status_bar(self, win):
        """Draw status bar at the bottom"""
        win.clear()
        height, width = win.getmaxyx()
        
        status_text = "ArchUtil v1.0 - Arch Linux System Utility"
        win.addstr(0, 2, status_text, curses.color_pair(2) | curses.A_BOLD)
        
        # Add system info
        try:
            load_avg = os.getloadavg()
            load_text = f"Load: {load_avg[0]:.2f}"
            win.addstr(0, width - len(load_text) - 2, load_text, curses.color_pair(6))
        except:
            pass
        
        win.refresh()
    
    def execute_command(self, command: str, description: str = ""):
        """Execute a command in a new window"""
        # Save current state
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            print(f"\n{description}")
            print(f"Command: {command}")
            
            response = input("\nProceed? (y/N): ").strip().lower()
            if response != 'y':
                print("Operation cancelled.")
                input("Press Enter to continue...")
                return
            
            # Execute command
            result = subprocess.run(command, shell=True)
            
            if result.returncode == 0:
                print(f"\n✓ Success: {description}")
            else:
                print(f"\n✗ Command failed with exit code: {result.returncode}")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"Error: {e}")
            input("Press Enter to continue...")
        finally:
            # Restore curses mode
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def handle_submenu_action(self):
        """Handle submenu item selection"""
        if self.current_selection >= len(self.main_menu):
            return
            
        main_item = self.main_menu[self.current_selection]
        
        if main_item not in self.submenus:
            return
            
        submenu_items = self.submenus[main_item]
        
        if self.current_submenu_selection >= len(submenu_items):
            return
            
        selected_item = submenu_items[self.current_submenu_selection]
        
        # Define actions for each submenu item
        actions = {
            # System Information
            "Show System Info": ("uname -a && lsb_release -a 2>/dev/null || cat /etc/os-release && free -h && df -h", "Showing system information"),
            "Hardware Info": ("lshw -short 2>/dev/null || lscpu && lsmem", "Showing hardware information"),
            "Network Info": ("ip addr show && ss -tuln", "Showing network information"),
            "Process Monitor": ("htop || top", "Opening process monitor"),
            "Disk Usage": ("df -h && du -sh /home/* 2>/dev/null", "Showing disk usage"),
            
            # Package Management
            "Update System": ("sudo pacman -Syu", "Updating system packages"),
            "Install Package": self.install_package,
            "Remove Package": self.remove_package,
            "Search Packages": self.search_packages,
            "List Installed": ("pacman -Q | less", "Listing installed packages"),
            "Clean Cache": ("sudo pacman -Sc", "Cleaning package cache"),
            "Package Info": self.package_info,
            
            # System Maintenance
            "Update Mirrors": ("sudo reflector --verbose --latest 10 --protocol https --sort rate --save /etc/pacman.d/mirrorlist", "Updating mirrors"),
            "Clean System Logs": ("sudo journalctl --vacuum-time=7d", "Cleaning system logs"),
            "Check Filesystem": ("sudo fsck -f /", "Checking filesystem"),
            "Update Locate DB": ("sudo updatedb", "Updating locate database"),
            "Rebuild Initramfs": ("sudo mkinitcpio -P", "Rebuilding initramfs"),
            "Check Services": ("systemctl --failed && systemctl list-unit-files --state=enabled", "Checking services"),
            "Manage Startup Services": ("sudo systemctl list-unit-files --type=service", "Managing startup services"),
            
            # AUR Helper
            "Install yay": ("cd /tmp && git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si", "Installing yay AUR helper"),
            "Update AUR Packages": ("yay -Syu", "Updating AUR packages"),
            "Install AUR Package": self.install_aur_package,
            "Search AUR": self.search_aur,
            "Remove AUR Package": self.remove_aur_package,
            "List AUR Packages": ("yay -Qm", "Listing AUR packages"),
            
            # Development Tools
            "Install Git": ("sudo pacman -S git", "Installing Git"),
            "Install VSCode": ("yay -S visual-studio-code-bin", "Installing Visual Studio Code"),
            "Install Docker": ("sudo pacman -S docker docker-compose", "Installing Docker"),
            "Install Node.js": ("sudo pacman -S nodejs npm", "Installing Node.js and npm"),
            "Install Python Tools": ("sudo pacman -S python-pip python-virtualenv", "Installing Python tools"),
            "Install Build Tools": ("sudo pacman -S base-devel", "Installing build tools")
        }
        
        if selected_item in actions:
            action = actions[selected_item]
            if callable(action):
                action()
            else:
                command, description = action
                self.execute_command(command, description)
    
    def install_package(self):
        """Install a package with user input"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter package name: ").strip()
            if package:
                self.execute_command(f"sudo pacman -S {package}", f"Installing {package}")
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
                self.execute_command(f"sudo pacman -R {package}", f"Removing {package}")
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
                self.execute_command(f"pacman -Ss {query}", f"Searching for '{query}'")
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
                self.execute_command(f"pacman -Si {package} || pacman -Qi {package}", f"Package info for {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def install_aur_package(self):
        """Install AUR package with user input"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter AUR package name: ").strip()
            if package:
                self.execute_command(f"yay -S {package}", f"Installing AUR package {package}")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def search_aur(self):
        """Search AUR packages"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            query = input("Enter search term: ").strip()
            if query:
                self.execute_command(f"yay -Ss {query}", f"Searching AUR for '{query}'")
        finally:
            curses.reset_prog_mode()
            curses.curs_set(0)
    
    def remove_aur_package(self):
        """Remove AUR package"""
        curses.def_prog_mode()
        curses.endwin()
        
        try:
            package = input("Enter AUR package name: ").strip()
            if package:
                self.execute_command(f"yay -R {package}", f"Removing AUR package {package}")
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
                        main_item = self.main_menu[self.current_selection]
                        if main_item in self.submenus:
                            max_sub = len(self.submenus[main_item]) - 1
                            self.current_submenu_selection = min(max_sub, self.current_submenu_selection + 1)
                    else:
                        self.current_selection = min(len(self.main_menu) - 1, self.current_selection + 1)
                elif key == curses.KEY_RIGHT:
                    if not self.in_submenu:
                        main_item = self.main_menu[self.current_selection]
                        if main_item in self.submenus:
                            self.in_submenu = True
                            self.current_submenu_selection = 0
                elif key == curses.KEY_LEFT:
                    if self.in_submenu:
                        self.in_submenu = False
                elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:  # Enter
                    if self.main_menu[self.current_selection] == "Quit":
                        break
                    elif self.in_submenu:
                        self.handle_submenu_action()
                    else:
                        # Enter submenu
                        main_item = self.main_menu[self.current_selection]
                        if main_item in self.submenus:
                            self.in_submenu = True
                            self.current_submenu_selection = 0
                
            except KeyboardInterrupt:
                break

def main():
    """Main entry point"""
    def app(stdscr):
        archutil = ArchUtil(stdscr)
        archutil.run()
    
    try:
        curses.wrapper(app)
    except KeyboardInterrupt:
        print("\nExiting ArchUtil...")
        sys.exit(0)

if __name__ == "__main__":
    main()