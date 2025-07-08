#!/bin/bash

# Arch Linux Tools Menu v1.0
# A GUI menu system for common Arch Linux tools and utilities

# Check if zenity is installed
if ! command -v zenity &> /dev/null; then
    echo "Error: zenity is required but not installed."
    echo "Please install it with: sudo pacman -S zenity"
    exit 1
fi

# Function to run command in new terminal
run_in_terminal() {
    local cmd="$1"
    local title="$2"
    
    # Try different terminal emulators
    if command -v alacritty &> /dev/null; then
        alacritty -t "$title" -e bash -c "$cmd; echo 'Press Enter to continue...'; read" &
    elif command -v kitty &> /dev/null; then
        kitty --title "$title" bash -c "$cmd; echo 'Press Enter to continue...'; read" &
    elif command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title "$title" -- bash -c "$cmd; echo 'Press Enter to continue...'; read" &
    elif command -v xterm &> /dev/null; then
        xterm -T "$title" -e bash -c "$cmd; echo 'Press Enter to continue...'; read" &
    else
        zenity --error --text="No suitable terminal emulator found!"
        return 1
    fi
}

# Function to run command as root in terminal
run_as_root() {
    local cmd="$1"
    local title="$2"
    
    # Check if user can sudo
    if ! sudo -n true 2>/dev/null; then
        # Prompt for password
        if ! sudo -v; then
            zenity --error --text="Administrator privileges required!"
            return 1
        fi
    fi
    
    run_in_terminal "sudo $cmd" "$title"
}

# Define menu structure with commands
declare -A menu_structure

# System Management
menu_structure["System Management|System Update"]="pacman -Syu"
menu_structure["System Management|Clean Package Cache"]="pacman -Sc"
menu_structure["System Management|Remove Orphaned Packages"]="pacman -Rns \$(pacman -Qtdq)"
menu_structure["System Management|Systemd Services Status"]="systemctl --type=service --state=running"
menu_structure["System Management|Disk Usage Analyzer"]="df -h && echo && du -sh /home/* 2>/dev/null"
menu_structure["System Management|System Logs"]="journalctl -n 50"
menu_structure["System Management|Failed Services"]="systemctl --failed"
menu_structure["System Management|Memory Usage"]="free -h && echo && ps aux --sort=-%mem | head -10"

# Package Management
menu_structure["Package Management|Search Packages"]="echo 'Enter package name:' && read pkg && pacman -Ss \$pkg"
menu_structure["Package Management|Install Package"]="echo 'Enter package name:' && read pkg && pacman -S \$pkg"
menu_structure["Package Management|Remove Package"]="echo 'Enter package name:' && read pkg && pacman -R \$pkg"
menu_structure["Package Management|List Installed Packages"]="pacman -Q | less"
menu_structure["Package Management|Package Information"]="echo 'Enter package name:' && read pkg && pacman -Qi \$pkg"
menu_structure["Package Management|List Package Files"]="echo 'Enter package name:' && read pkg && pacman -Ql \$pkg"
menu_structure["Package Management|Check Package Updates"]="checkupdates"
menu_structure["Package Management|Downgrade Package"]="echo 'Note: downgrade tool required' && echo 'Enter package name:' && read pkg && downgrade \$pkg"

# System Information
menu_structure["System Information|System Overview"]="neofetch || screenfetch || inxi -Fxz"
menu_structure["System Information|CPU Information"]="lscpu"
menu_structure["System Information|Memory Information"]="free -h && echo && cat /proc/meminfo | head -20"
menu_structure["System Information|Disk Information"]="lsblk && echo && df -h"
menu_structure["System Information|Network Interfaces"]="ip addr show"
menu_structure["System Information|USB Devices"]="lsusb"
menu_structure["System Information|PCI Devices"]="lspci"
menu_structure["System Information|Kernel Information"]="uname -a && echo && cat /proc/version"

# Network Tools
menu_structure["Network Tools|Network Configuration"]="ip addr show && echo && ip route show"
menu_structure["Network Tools|WiFi Networks"]="nmcli dev wifi list"
menu_structure["Network Tools|Network Connections"]="nmcli connection show"
menu_structure["Network Tools|Ping Test"]="echo 'Enter hostname/IP:' && read host && ping -c 4 \$host"
menu_structure["Network Tools|Port Scan"]="echo 'Enter hostname/IP:' && read host && nmap -sS \$host"
menu_structure["Network Tools|Network Statistics"]="netstat -tuln"
menu_structure["Network Tools|Firewall Status"]="ufw status || iptables -L"
menu_structure["Network Tools|DNS Lookup"]="echo 'Enter domain:' && read domain && dig \$domain"

# Development Tools
menu_structure["Development Tools|Git Status"]="git status"
menu_structure["Development Tools|Git Log"]="git log --oneline -10"
menu_structure["Development Tools|Python Version"]="python --version && python3 --version"
menu_structure["Development Tools|Node.js Version"]="node --version && npm --version"
menu_structure["Development Tools|Docker Status"]="docker ps -a"
menu_structure["Development Tools|Docker Images"]="docker images"
menu_structure["Development Tools|Virtual Environments"]="conda info --envs 2>/dev/null || echo 'Conda not installed'"
menu_structure["Development Tools|Development Packages"]="pacman -Qs base-devel"

# AUR Helpers
menu_structure["AUR Helpers|Yay - Search AUR"]="echo 'Enter package name:' && read pkg && yay -Ss \$pkg"
menu_structure["AUR Helpers|Yay - Install AUR Package"]="echo 'Enter package name:' && read pkg && yay -S \$pkg"
menu_structure["AUR Helpers|Yay - Update AUR Packages"]="yay -Sua"
menu_structure["AUR Helpers|Paru - Search AUR"]="echo 'Enter package name:' && read pkg && paru -Ss \$pkg"
menu_structure["AUR Helpers|Paru - Install AUR Package"]="echo 'Enter package name:' && read pkg && paru -S \$pkg"
menu_structure["AUR Helpers|Paru - Update AUR Packages"]="paru -Sua"
menu_structure["AUR Helpers|List AUR Packages"]="pacman -Qm"
menu_structure["AUR Helpers|AUR Package Information"]="echo 'Enter AUR package name:' && read pkg && yay -Si \$pkg || paru -Si \$pkg"

# Global variables for menu state
declare -A expanded_categories
declare -a menu_display

# Function to build menu display
build_menu_display() {
    menu_display=()
    
    # Get all categories
    local categories=()
    for key in "${!menu_structure[@]}"; do
        local category="${key%|*}"
        if [[ ! " ${categories[*]} " =~ " ${category} " ]]; then
            categories+=("$category")
        fi
    done
    
    # Sort categories
    IFS=$'\n' sorted_categories=($(sort <<<"${categories[*]}")); unset IFS
    
    # Build display
    for category in "${sorted_categories[@]}"; do
        if [[ "${expanded_categories[$category]}" == "true" ]]; then
            menu_display+=("[-] $category")
            
            # Get submenus for this category
            local submenus=()
            for key in "${!menu_structure[@]}"; do
                if [[ "$key" == "$category|"* ]]; then
                    local submenu="${key#*|}"
                    submenus+=("$submenu")
                fi
            done
            
            # Sort submenus and add to display
            IFS=$'\n' sorted_submenus=($(sort <<<"${submenus[*]}")); unset IFS
            for submenu in "${sorted_submenus[@]}"; do
                menu_display+=("    → $submenu")
            done
        else
            menu_display+=("[+] $category")
        fi
    done
}

# Function to execute tool
execute_tool() {
    local category="$1"
    local tool="$2"
    
    local key="$category|$tool"
    local command="${menu_structure[$key]}"
    
    if [[ -z "$command" ]]; then
        zenity --error --text="Command not found for: $tool"
        return
    fi
    
    # Show confirmation dialog
    if zenity --question --title="Execute Tool" --text="Execute: $tool\n\nCommand: $command" --width=400; then
        # Check if command requires root privileges
        if [[ "$command" == *"pacman -S"* ]] || [[ "$command" == *"pacman -R"* ]] || [[ "$command" == *"pacman -Syu"* ]] || [[ "$command" == *"pacman -Sc"* ]]; then
            run_as_root "$command" "$tool"
        else
            run_in_terminal "$command" "$tool"
        fi
    fi
}

# Function to show main menu
show_main_menu() {
    while true; do
        build_menu_display
        
        local selected_item
        selected_item=$(zenity --list \
            --title="Arch Linux Tools v1.0 - Tree Menu" \
            --text="Click [+] to expand categories, click → to run tools:" \
            --column="Menu" \
            --width=600 \
            --height=500 \
            "${menu_display[@]}" \
            2>/dev/null)
        
        if [[ -z "$selected_item" ]]; then
            # User cancelled or closed dialog
            break
        fi
        
        # Handle selection
        if [[ "$selected_item" == "[+] "* ]]; then
            # Expand category
            local category="${selected_item#[+] }"
            expanded_categories["$category"]="true"
        elif [[ "$selected_item" == "[-] "* ]]; then
            # Collapse category
            local category="${selected_item#[-] }"
            expanded_categories["$category"]="false"
        elif [[ "$selected_item" == "    → "* ]]; then
            # Execute tool
            local tool="${selected_item#    → }"
            
            # Find which category this tool belongs to
            local tool_category=""
            for key in "${!menu_structure[@]}"; do
                if [[ "$key" == *"|$tool" ]]; then
                    tool_category="${key%|*}"
                    break
                fi
            done
            
            if [[ -n "$tool_category" ]]; then
                execute_tool "$tool_category" "$tool"
            fi
        fi
    done
}

# Function to show about dialog
show_about() {
    zenity --info \
        --title="About Arch Linux Tools" \
        --text="Arch Linux Tools Menu v1.0\n\nA GUI tree menu system for common Arch Linux tools and utilities.\n\nRequires: zenity, terminal emulator\nOptional: yay, paru, neofetch, nmap\n\nClick [+] to expand categories\nClick → to execute tools" \
        --width=350
}

# Function to show help
show_help() {
    zenity --info \
        --title="Help - Arch Linux Tools" \
        --text="Usage:\n\n1. Click [+] to expand a category\n2. Click [-] to collapse a category\n3. Click → to execute a tool\n4. Confirm execution in the dialog\n5. Commands run in a new terminal window\n\nNote: Some commands require root privileges and will prompt for your password." \
        --width=400
}

# Check for command line arguments
case "${1:-}" in
    --help|-h)
        echo "Arch Linux Tools Menu v1.0"
        echo "Usage: $0 [--help|--about]"
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --about       Show about dialog"
        echo ""
        echo "Run without arguments to start the GUI menu."
        exit 0
        ;;
    --about)
        show_about
        exit 0
        ;;
    *)
        # Start main menu
        show_main_menu
        ;;
esac