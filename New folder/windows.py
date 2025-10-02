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
        
        # Clean and organized menu structure
        self.menu_data = self._build_menu_structure()
    
    def _build_menu_structure(self):
        """Build the menu structure in a clean, organized way"""
        return [
            # ═══════════════════════════════════════════════════════════════
            # GIT OPERATIONS
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Git Update",
                "description": "Update the ms1 repository",
                "action": {
                    "powershell": [
                        "Write-Host 'Updating ms1 repository...' -ForegroundColor Blue",
                        "$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path",
                        "$gitRoot = $null",
                        "$currentDir = $scriptDir",
                        "while ($currentDir -ne (Split-Path -Parent $currentDir)) {",
                        "    if (Test-Path (Join-Path $currentDir '.git')) {",
                        "        $gitRoot = $currentDir",
                        "        break",
                        "    }",
                        "    $currentDir = Split-Path -Parent $currentDir",
                        "}",
                        "if (-not $gitRoot) {",
                        "    Write-Host 'Error: Not inside a git repository' -ForegroundColor Red",
                        "    Write-Host \"Current directory: $scriptDir\"",
                        "    Read-Host 'Press Enter to continue'",
                        "    return",
                        "}",
                        "Write-Host \"Found git repository at: $gitRoot\"",
                        "Set-Location $gitRoot",
                        "$status = git status --porcelain",
                        "if ($status) {",
                        "    Write-Host 'Warning: You have uncommitted changes:' -ForegroundColor Yellow",
                        "    Write-Host $status",
                        "    $response = Read-Host 'Continue with git pull? This might cause conflicts. (y/N)'",
                        "    if ($response -notmatch '^[yY]') {",
                        "        Write-Host 'Operation cancelled.'",
                        "        Read-Host 'Press Enter to continue'",
                        "        return",
                        "    }",
                        "}",
                        "$branch = git branch --show-current",
                        "Write-Host \"Current branch: $branch\"",
                        "Write-Host 'Fetching latest changes...'",
                        "git fetch",
                        "Write-Host 'Pulling changes...'",
                        "git pull",
                        "Write-Host 'Git pull completed!' -ForegroundColor Green",
                        "Read-Host 'Press Enter to continue'"
                    ],
                    "description": "Update Git Repository"
                }
            },
            
            # ═══════════════════════════════════════════════════════════════
            # SYSTEM INFORMATION
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "System Information",
                "description": "View detailed system information and monitoring",
                "submenu": [
                    {
                        "title": "Show System Info", 
                        "action": ("systeminfo", "Showing system information")
                    },
                    {
                        "title": "Hardware Info", 
                        "action": (
                            "powershell -Command \"Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors\"", 
                            "Showing hardware information"
                        )
                    },
                    {
                        "title": "Network Info", 
                        "action": ("ipconfig /all", "Showing network information")
                    },
                    {
                        "title": "Process Monitor", 
                        "action": (
                            "powershell -Command \"Get-Process | Sort-Object CPU -Descending | Select-Object -First 20\"", 
                            "Opening process monitor"
                        )
                    },
                    {
                        "title": "Disk Usage", 
                        "action": (
                            "powershell -Command \"Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name='Size(GB)';Expression={[math]::Round($_.Size/1GB,2)}}, @{Name='FreeSpace(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}\"", 
                            "Showing disk usage"
                        )
                    },
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # PACKAGE MANAGEMENT
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Package Management",
                "description": "Manage Windows packages with Scoop and Chocolatey",
                "submenu": [
                    {
                        "title": "Update Scoop", 
                        "action": ("scoop update", "Updating Scoop")
                    },
                    {
                        "title": "Install Scoop", 
                        "action": (
                            "powershell -Command \"Set-ExecutionPolicy RemoteSigned -Scope CurrentUser; irm get.scoop.sh | iex\"", 
                            "Installing Scoop package manager"
                        )
                    },
                    {
                        "title": "Install Essential Packages", 
                        "action": {
                            "commands": [
                                "scoop install ack",
                                "scoop install adb", 
                                "scoop install bat",
                                "scoop install capture2text",
                                "scoop install ditto",
                                "scoop install ffmpeg",
                                "scoop install highlight",
                                "scoop install kitty",
                                "scoop install neovim",
                                "scoop install putty",
                                "scoop install rssguard",
                                "scoop install rufus",
                                "scoop install yt-dlp"
                            ],
                            "description": "Installing Essential Scoop Packages"
                        }
                    },
                    {
                        "title": "Remove Package", 
                        "action": {
                            "powershell": [
                                "$package = Read-Host 'Enter package name to remove'",
                                "if ($package) { scoop uninstall $package }"
                            ],
                            "description": "Remove a Scoop package"
                        }
                    },
                    {
                        "title": "Search Packages", 
                        "action": {
                            "powershell": [
                                "$query = Read-Host 'Enter search term'",
                                "if ($query) { scoop search $query }"
                            ],
                            "description": "Search for Scoop packages"
                        }
                    },
                    {
                        "title": "List Installed", 
                        "action": ("scoop list", "Listing installed packages")
                    },
                    {
                        "title": "Clean Cache", 
                        "action": ("scoop cache rm *", "Cleaning package cache")
                    },
                    {
                        "title": "Package Info", 
                        "action": {
                            "powershell": [
                                "$package = Read-Host 'Enter package name for info'",
                                "if ($package) { scoop info $package }"
                            ],
                            "description": "Show package information"
                        }
                    },
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # SYSTEM MAINTENANCE
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "System Maintenance",
                "description": "System cleanup and maintenance tasks",
                "submenu": [
                    {
                        "title": "Windows Update", 
                        "action": (
                            "powershell -Command \"Get-WindowsUpdate -Install -AcceptAll\"", 
                            "Running Windows Update"
                        )
                    },
                    {
                        "title": "Clean Temp Files", 
                        "action": {
                            "powershell": [
                                "Write-Host 'Cleaning temporary files...' -ForegroundColor Yellow",
                                "Get-ChildItem -Path $env:TEMP -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue",
                                "Write-Host 'Cleaning Windows temp folder...' -ForegroundColor Yellow", 
                                "Get-ChildItem -Path C:\\Windows\\Temp -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue",
                                "Write-Host 'Cleaning browser cache...' -ForegroundColor Yellow",
                                "Get-ChildItem -Path \"$env:LOCALAPPDATA\\Microsoft\\Windows\\INetCache\" -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue",
                                "Write-Host 'Cleanup completed!' -ForegroundColor Green"
                            ],
                            "description": "System Cleanup Script"
                        }
                    },
                    {
                        "title": "Check Disk", 
                        "action": ("chkdsk C: /f", "Checking disk for errors")
                    },
                    {
                        "title": "System File Check", 
                        "action": ("sfc /scannow", "Running system file checker")
                    },
                    {
                        "title": "DISM Health Check", 
                        "action": ("DISM /Online /Cleanup-Image /CheckHealth", "Checking system image health")
                    },
                    {
                        "title": "Check Services", 
                        "action": (
                            "powershell -Command \"Get-Service | Where-Object {$_.Status -eq 'Stopped' -and $_.StartType -eq 'Automatic'}\"", 
                            "Checking stopped services"
                        )
                    },
                    {
                        "title": "Manage Startup Programs", 
                        "action": (
                            "powershell -Command \"Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location\"", 
                            "Managing startup programs"
                        )
                    },
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # DEVELOPMENT TOOLS
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Development Tools",
                "description": "Install common development tools and environments",
                "submenu": [
                    {
                        "title": "Install Git", 
                        "action": ("scoop install git", "Installing Git")
                    },
                    {
                        "title": "Install Node.js", 
                        "action": ("scoop install nodejs", "Installing Node.js and npm")
                    },
                    {
                        "title": "Install Python", 
                        "action": ("scoop install python", "Installing Python")
                    },
                    {
                        "title": "Install Visual Studio Code", 
                        "action": ("scoop install vscode", "Installing Visual Studio Code")
                    },
                    {
                        "title": "Install Build Tools", 
                        "action": ("scoop install mingw", "Installing MinGW build tools")
                    },
                    {
                        "title": "Install Complete Dev Environment", 
                        "action": {
                            "commands": [
                                "scoop install git",
                                "scoop install nodejs",
                                "scoop install python",
                                "scoop install vscode",
                                "scoop install mingw",
                                "scoop install docker",
                                "scoop install postman"
                            ],
                            "description": "Installing Complete Development Environment"
                        }
                    },
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # SYMBOLIC LINKS (MKLINK)
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Symbolic Links (mklink)",
                "description": "Create symbolic links for configuration files and applications",
                "submenu": [
                    {
                        "title": "Komorebi", 
                        "action": {
                            "powershell": [
                                "Write-Host 'Initially after creating with quickstart have to run komorebi with the default profile then we can mklink' -ForegroundColor Green",
                                "Write-Host 'It will try to replace ms1 komorebi profile just let it and then copy it from git and paste the code in' -ForegroundColor Green",
                                "komorebic quickstart",
                                "Remove-Item 'C:\\Users\\nahid\\komorebi.json' -ErrorAction SilentlyContinue",
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\komorebi.json' -Target 'C:\\Users\\nahid\\ms\\ms1\\asset\\komorebi\\komorebi.json' -Force"
                            ],
                            "description": "Setup Komorebi configuration symbolic link"
                        }
                    },
                    {
                        "title": "Reference.py", 
                        "action": {
                            "powershell": [
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\scoop\\apps\\python312\\current\\Lib\\Reference.py' -Target 'C:\\Users\\nahid\\ms\\ms1\\Reference.py' -Force"
                            ],
                            "description": "Create symbolic link for Python Reference.py"
                        }
                    },
                    {
                        "title": "PowerShell Profile", 
                        "action": {
                            "powershell": [
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1' -Target 'C:\\Users\\nahid\\ms\\ms1\\asset\\Powershell\\Microsoft.PowerShell_profile.ps1' -Force"
                            ],
                            "description": "Create symbolic link for PowerShell profile"
                        }
                    },
                    {
                        "title": "Prowlarr", 
                        "action": {
                            "powershell": [
                                "winget install TeamProwlarr.Prowlarr",
                                "Write-Host 'Do it with manual Restore!' -ForegroundColor Green",
                                "Start-Process 'C:\\Users\\nahid\\ms\\msBackups\\ARR_timely'"
                            ],
                            "description": "Install Prowlarr and open backup restore location"
                        }
                    },
                    {
                        "title": "Radarr", 
                        "action": {
                            "powershell": [
                                "winget install TeamRadarr.Radarr",
                                "Write-Host 'Do it with manual Restore!' -ForegroundColor Green",
                                "Start-Process 'C:\\Users\\nahid\\ms\\msBackups\\ARR_timely'"
                            ],
                            "description": "Install Radarr and open backup restore location"
                        }
                    },
                    {
                        "title": "RssGuard", 
                        "action": {
                            "powershell": [
                                "scoop install rssguard",
                                "Stop-Process -Name 'rssguard' -ErrorAction SilentlyContinue",
                                "Remove-Item 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\database' -Recurse -ErrorAction SilentlyContinue",
                                "Remove-Item 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\config' -Recurse -ErrorAction SilentlyContinue",
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\config' -Target 'C:\\Users\\nahid\\ms\\msBackups\\@mklink\\rssguard\\config' -Force",
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\database' -Target 'C:\\Users\\nahid\\ms\\msBackups\\@mklink\\rssguard\\database' -Force"
                            ],
                            "description": "Setup RssGuard with symbolic links to backup data"
                        }
                    },
                    {
                        "title": "Sonarr", 
                        "action": {
                            "powershell": [
                                "winget install TeamSonarr.Sonarr",
                                "Write-Host 'Do it with manual Restore!' -ForegroundColor Green",
                                "Start-Process 'C:\\Users\\nahid\\ms\\msBackups\\ARR_timely'"
                            ],
                            "description": "Install Sonarr and open backup restore location"
                        }
                    },
                    {
                        "title": "Terminal Profile", 
                        "action": {
                            "powershell": [
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\AppData\\Local\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json' -Target 'C:\\Users\\nahid\\ms\\ms1\\asset\\terminal\\settings.json' -Force"
                            ],
                            "description": "Create symbolic link for Windows Terminal settings"
                        }
                    },
                    {
                        "title": "VSCode", 
                        "action": {
                            "powershell": [
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\AppData\\Roaming\\Code\\User\\keybindings.json' -Target 'C:\\Users\\nahid\\ms\\ms1\\asset\\vscode\\keybindings.json' -Force",
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\AppData\\Roaming\\Code\\User\\settings.json' -Target 'C:\\Users\\nahid\\ms\\ms1\\asset\\vscode\\settings.json' -Force"
                            ],
                            "description": "Create symbolic links for VSCode settings and keybindings"
                        }
                    }
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # FIREWALL PORTS
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Firewall Ports",
                "description": "Manage Windows Firewall rules for specific ports",
                "submenu": [
                    {
                        "title": "Port 22 [SSH]", 
                        "action": {
                            "powershell": [
                                "New-NetFirewallRule -DisplayName 'Allow_Port_22' -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Profile Any",
                                "Write-Host 'Port 22 (SSH) has been opened in Windows Firewall' -ForegroundColor Green"
                            ],
                            "description": "Open port 22 for SSH connections"
                        }
                    },
                    {
                        "title": "Port 5000", 
                        "action": {
                            "powershell": [
                                "New-NetFirewallRule -DisplayName 'Allow_Port_5000' -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Any",
                                "Write-Host 'Port 5000 has been opened in Windows Firewall' -ForegroundColor Green"
                            ],
                            "description": "Open port 5000 in Windows Firewall"
                        }
                    },
                    {
                        "title": "Port 5001", 
                        "action": {
                            "powershell": [
                                "New-NetFirewallRule -DisplayName 'Allow_Port_5001' -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow -Profile Any",
                                "Write-Host 'Port 5001 has been opened in Windows Firewall' -ForegroundColor Green"
                            ],
                            "description": "Open port 5001 in Windows Firewall"
                        }
                    },
                    {
                        "title": "Port 5002", 
                        "action": {
                            "powershell": [
                                "New-NetFirewallRule -DisplayName 'Allow_Port_5002' -Direction Inbound -Protocol TCP -LocalPort 5002 -Action Allow -Profile Any",
                                "Write-Host 'Port 5002 has been opened in Windows Firewall' -ForegroundColor Green"
                            ],
                            "description": "Open port 5002 in Windows Firewall"
                        }
                    },
                    {
                        "title": "View All Firewall Rules", 
                        "action": {
                            "powershell": [
                                "Get-NetFirewallRule | Where-Object {$_.DisplayName -like 'Allow_Port_*'} | Select-Object DisplayName, Direction, Action, Enabled | Format-Table -AutoSize"
                            ],
                            "description": "Display all custom port firewall rules"
                        }
                    },
                    {
                        "title": "Remove Custom Port Rules", 
                        "action": {
                            "powershell": [
                                "$rules = Get-NetFirewallRule | Where-Object {$_.DisplayName -like 'Allow_Port_*'}",
                                "if ($rules) {",
                                "    Write-Host 'Found custom port rules:' -ForegroundColor Yellow",
                                "    $rules | Select-Object DisplayName | Format-Table -AutoSize",
                                "    $confirm = Read-Host 'Do you want to remove all custom port rules? (y/N)'",
                                "    if ($confirm -match '^[yY]') {",
                                "        $rules | Remove-NetFirewallRule",
                                "        Write-Host 'All custom port rules have been removed' -ForegroundColor Green",
                                "    } else {",
                                "        Write-Host 'Operation cancelled' -ForegroundColor Yellow",
                                "    }",
                                "} else {",
                                "    Write-Host 'No custom port rules found' -ForegroundColor Yellow",
                                "}"
                            ],
                            "description": "Remove all custom port firewall rules"
                        }
                    }
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # APPLICATION SETUP
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Application Setup",
                "description": "Configure and setup various applications with custom settings",
                "submenu": [
                    {
                        "title": "Jackett + qBittorrent", 
                        "action": {
                            "powershell": [
                                "# cd C:\\Users\\nahid",
                                "Write-Host 'Step 1: open qbittorrent -> view -> search engine -> Go To search engine tab -> search plugin -> check for updates -> now nova3 folder will be added' -ForegroundColor Green",
                                "Write-Host 'Step 2: Start Jackett and add the necessary indexes to the list' -ForegroundColor Green",
                                "Write-Host 'Step 3: Copy jacket api from webui to jackett.json' -ForegroundColor Green",
                                "Start-Process 'C:\\Users\\nahid\\AppData\\Local\\qBittorrent\\nova3\\engines'"
                            ],
                            "description": "Setup Jackett and qBittorrent integration"
                        }
                    },
                    {
                        "title": "LDPlayer", 
                        "action": {
                            "powershell": [
                                "Remove-Item 'C:\\Users\\nahid\\AppData\\Roaming\\XuanZhi9\\cache\\*' -Recurse -ErrorAction SilentlyContinue",
                                "New-NetFirewallRule -DisplayName '@Block_Ld9BoxHeadless_OutInbound' -Direction Outbound -Program 'C:\\LDPlayer\\LDPlayer9\\dnplayer.exe' -Action Block -Enabled True",
                                "Write-Host 'LDPlayer cache cleared and network blocked' -ForegroundColor Green"
                            ],
                            "description": "Clean LDPlayer cache and block network access"
                        }
                    },
                    {
                        "title": "Neovim Config 1", 
                        "action": {
                            "powershell": [
                                "Write-Host 'Setting up Neovim...' -ForegroundColor Yellow",
                                "Remove-Item -Force -Recurse -Verbose 'C:\\Users\\nahid\\AppData\\Local\\nvim' -ErrorAction SilentlyContinue",
                                "Remove-Item -Force -Recurse -Verbose 'C:\\Users\\nahid\\AppData\\Local\\nvim-data' -ErrorAction SilentlyContinue",
                                "New-Item -ItemType Directory -Path 'C:\\Users\\nahid\\AppData\\Local\\nvim' -Force",
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\AppData\\Local\\nvim\\init.lua' -Target 'C:\\Users\\nahid\\ms\\ms1\\linux\\linux\\neovim\\init.lua' -Force",
                                "Write-Host 'Neovim configuration 1 setup complete' -ForegroundColor Green"
                            ],
                            "description": "Setup Neovim with configuration 1 (init.lua)"
                        }
                    },
                    {
                        "title": "Neovim Config 2", 
                        "action": {
                            "powershell": [
                                "Write-Host 'Setting up Neovim...' -ForegroundColor Yellow",
                                "Remove-Item -Force -Recurse -Verbose 'C:\\Users\\nahid\\AppData\\Local\\nvim' -ErrorAction SilentlyContinue",
                                "Remove-Item -Force -Recurse -Verbose 'C:\\Users\\nahid\\AppData\\Local\\nvim-data' -ErrorAction SilentlyContinue",
                                "New-Item -ItemType Directory -Path 'C:\\Users\\nahid\\AppData\\Local\\nvim' -Force",
                                "New-Item -ItemType SymbolicLink -Path 'C:\\Users\\nahid\\AppData\\Local\\nvim\\init.lua' -Target 'C:\\Users\\nahid\\ms\\ms1\\linux\\linux\\neovim\\init2.lua' -Force",
                                "Write-Host 'Neovim configuration 2 setup complete' -ForegroundColor Green"
                            ],
                            "description": "Setup Neovim with configuration 2 (init2.lua)"
                        }
                    },
                    {
                        "title": "Notepad++ Theme Setup", 
                        "action": {
                            "powershell": [
                                "Set-Location 'C:\\Users\\nahid'",
                                "Write-Host 'Dracula Theme' -ForegroundColor Blue",
                                "git clone https://github.com/dracula/notepad-plus-plus.git",
                                "Start-Process 'C:\\Users\\nahid\\notepad-plus-plus'",
                                "# Write-Host 'Material Theme' -ForegroundColor Blue",
                                "# git clone https://github.com/Codextor/npp-material-theme.git",
                                "# Start-Process 'C:\\Users\\nahid\\npp-material-theme'",
                                "Start-Process \"$env:AppData\\Notepad++\\themes\"",
                                "Write-Host 'step1: Copy Example.xml from github folder to %AppData%\\Notepad++\\themes' -ForegroundColor Green",
                                "Write-Host 'step2: Restart Notepad++' -ForegroundColor Green",
                                "Write-Host 'step3: Dracula will be available in Settings > Style Configurator' -ForegroundColor Green"
                            ],
                            "description": "Setup Dracula theme for Notepad++ with installation instructions"
                        }
                    },
                    {
                        "title": "PotPlayer Register", 
                        "action": {
                            "powershell": [
                                "Start-Process 'C:\\Users\\nahid\\ms\\ms1\\asset\\potplayer\\PotPlayerMini64.reg' -Verbose",
                                "Write-Host 'PotPlayer registry settings applied' -ForegroundColor Green"
                            ],
                            "description": "Apply PotPlayer registry settings"
                        }
                    }
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # GITHUB PROJECTS
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "GitHub Projects",
                "description": "Run popular Windows utilities and scripts from GitHub",
                "submenu": [
                    {
                        "title": "ChrisTitus WinUtility", 
                        "action": {
                            "powershell": [
                                "Start-Process powershell -ArgumentList '-NoExit', '-Command iwr -useb https://christitus.com/win | iex' -Verb RunAs"
                            ],
                            "description": "Run Chris Titus Tech's Windows Utility as Admin"
                        }
                    },
                    {
                        "title": "Microsoft Activation Scripts (MAS)", 
                        "action": {
                            "powershell": [
                                "Start-Process powershell -ArgumentList '-NoExit', '-Command irm https://get.activated.win | iex' -Verb RunAs"
                            ],
                            "description": "Run Microsoft Activation Scripts as Admin"
                        }
                    },
                    {
                        "title": "WIMUtil", 
                        "action": {
                            "powershell": [
                                "Start-Process powershell -ArgumentList '-NoExit', '-Command irm https://github.com/memstechtips/WIMUtil/raw/main/src/WIMUtil.ps1 | iex' -Verb RunAs"
                            ],
                            "description": "Run WIMUtil from GitHub as Admin"
                        }
                    },
                    {
                        "title": "Harden Windows Security GUI", 
                        "action": {
                            "powershell": [
                                "Start-Process powershell -ArgumentList '-NoExit', '-ExecutionPolicy Bypass', '-Command', 'irm https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1 | iex; P' -Verb RunAs"
                            ],
                            "description": "Run Harden Windows Security GUI as Admin"
                        }
                    },
                    {
                        "title": "Winhance", 
                        "action": {
                            "powershell": [
                                "Start-Process powershell -ArgumentList '-NoExit', '-Command irm https://github.com/memstechtips/Winhance/raw/main/Winhance.ps1 | iex' -Verb RunAs"
                            ],
                            "description": "Run Winhance Utility as Admin"
                        }
                    },
                    {
                        "title": "AppControl Manager", 
                        "action": {
                            "powershell": [
                                "Start-Process powershell -ArgumentList '-NoExit', '-ExecutionPolicy Bypass', '-Command', 'irm https://raw.githubusercontent.com/HotCakeX/Harden-Windows-Security/main/Harden-Windows-Security.ps1 | iex; AppControl' -Verb RunAs"
                            ],
                            "description": "Run AppControl Manager as Admin"
                        }
                    }
                ]
            },
            
            # ═══════════════════════════════════════════════════════════════
            # EXIT
            # ═══════════════════════════════════════════════════════════════
            {
                "title": "Quit",
                "description": "Exit WindowsUtil",
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
    
    def execute_command(self, command, description: str = ""):
        """Execute a command or list of commands in a new window"""
        # Save current state
        curses.def_prog_mode()
        curses.endwin()

        # ANSI escape codes for colors
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'

        # Clear the screen before executing the command
        os.system('cls' if os.name == 'nt' else 'clear')
        
        try:
            print(f"\n{BLUE}{description}{RESET}")
            
            # Handle different command types
            if isinstance(command, list):
                # Multiple commands
                print("Executing multiple commands...")
                failed_commands = []
                
                for i, cmd in enumerate(command, 1):
                    print(f"\n{YELLOW}[{i}/{len(command)}] {cmd}{RESET}")
                    result = subprocess.run(cmd, shell=True)
                    
                    if result.returncode == 0:
                        print(f"{GREEN}✓ Command {i} completed successfully{RESET}")
                    else:
                        print(f"{RED}✗ Command {i} failed with exit code: {result.returncode}{RESET}")
                        failed_commands.append((i, cmd))
                
                # Summary
                if failed_commands:
                    print(f"\n{RED}Summary: {len(failed_commands)} command(s) failed:{RESET}")
                    for i, cmd in failed_commands:
                        print(f"  {i}: {cmd}")
                else:
                    print(f"\n{GREEN}✓ All commands completed successfully{RESET}")
                    
            elif isinstance(command, str):
                # Single command
                print(f"Command: {command}")
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
    
    def execute_powershell_script(self, commands: List[str], description: str = ""):
        """Execute multiple PowerShell commands as a script"""
        # Create a temporary PowerShell script
        script_content = "\n".join(commands)
        
        # Save current state
        curses.def_prog_mode()
        curses.endwin()

        # ANSI escape codes for colors
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        RED = '\033[91m'
        RESET = '\033[0m'

        # Clear the screen before executing
        os.system('cls' if os.name == 'nt' else 'clear')
        
        try:
            print(f"\n{BLUE}{description}{RESET}")
            print("PowerShell Script Content:")
            print("-" * 40)
            print(script_content)
            print("-" * 40)
            
            # Execute the PowerShell script
            result = subprocess.run(
                ["powershell", "-Command", script_content],
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print(f"\n{GREEN}✓ PowerShell script completed successfully{RESET}")
            else:
                print(f"\n{RED}✗ PowerShell script failed with exit code: {result.returncode}{RESET}")
            
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
            elif isinstance(action, tuple) and len(action) == 2:
                command, description = action
                self.execute_command(command, description)
            elif isinstance(action, dict):
                # Handle inline command definitions
                if "commands" in action:
                    # List of commands
                    commands = action["commands"]
                    description = action.get("description", "Executing commands")
                    self.execute_command(commands, description)
                elif "powershell" in action:
                    # PowerShell script
                    ps_commands = action["powershell"]
                    description = action.get("description", "Executing PowerShell script")
                    self.execute_powershell_script(ps_commands, description)
            else:
                # Handle other action types if needed
                pass
    
    
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