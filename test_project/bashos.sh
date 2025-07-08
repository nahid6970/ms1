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

# Define menu structure
declare -A menu_categories=(
    ["System Management"]="system_management"
    ["Package Management"]="package_management"
    ["System Information"]="system_info"
    ["Network Tools"]="network_tools"
    ["Development Tools"]="dev_tools"
    ["AUR Helpers"]="aur_helpers"
)

# System Management submenu
declare -A system_management=(
    ["System Update"]="pacman -Syu"
    ["Clean Package Cache"]="pacman -Sc"
    ["Remove Orphaned Packages"]="pacman -Rns \$(pacman -Qtdq)"
    ["Systemd Services Status"]="systemctl --type=service --state=running"
    ["Disk Usage Analyzer"]="df -h && echo && du -sh /home/* 2>/dev/null"
    ["System Logs"]="journalctl -n 50"
    ["Failed Services"]="systemctl --failed"
    ["Memory Usage"]="free -h && echo && ps aux --sort=-%mem | head -10"
)

# Package Management submenu
declare -A package_management=(
    ["Search Packages"]="echo 'Enter package name:' && read pkg && pacman -Ss \$pkg"
    ["Install Package"]="echo 'Enter package name:' && read pkg && pacman -S \$pkg"
    ["Remove Package"]="echo 'Enter package name:' && read pkg && pacman -R \$pkg"
    ["List Installed Packages"]="pacman -Q | less"
    ["Package Information"]="echo 'Enter package name:' && read pkg && pacman -Qi \$pkg"
    ["List Package Files"]="echo 'Enter package name:' && read pkg && pacman -Ql \$pkg"
    ["Check Package Updates"]="checkupdates"
    ["Downgrade Package"]="echo 'Note: downgrade tool required' && echo 'Enter package name:' && read pkg && downgrade \$pkg"
)

# System Information submenu
declare -A system_info=(
    ["System Information"]="neofetch || screenfetch || inxi -Fxz"
    ["CPU Information"]="lscpu"
    ["Memory Information"]="free -h && echo && cat /proc/meminfo | head -20"
    ["Disk Information"]="lsblk && echo && df -h"
    ["Network Interfaces"]="ip addr show"
    ["USB Devices"]="lsusb"
    ["PCI Devices"]="lspci"
    ["Kernel Information"]="uname -a && echo && cat /proc/version"
)

# Network Tools submenu
declare -A network_tools=(
    ["Network Configuration"]="ip addr show && echo && ip route show"
    ["WiFi Networks"]="nmcli dev wifi list"
    ["Network Connections"]="nmcli connection show"
    ["Ping Test"]="echo 'Enter hostname/IP:' && read host && ping -c 4 \$host"
    ["Port Scan"]="echo 'Enter hostname/IP:' && read host && nmap -sS \$host"
    ["Network Statistics"]="netstat -tuln"
    ["Firewall Status"]="ufw status || iptables -L"
    ["DNS Lookup"]="echo 'Enter domain:' && read domain && dig \$domain"
)

# Development Tools submenu
declare -A dev_tools=(
    ["Git Status"]="git status"
    ["Git Log"]="git log --oneline -10"
    ["Python Version"]="python --version && python3 --version"
    ["Node.js Version"]="node --version && npm --version"
    ["Docker Status"]="docker ps -a"
    ["Docker Images"]="docker images"
    ["Virtual Environments"]="conda info --envs 2>/dev/null || echo 'Conda not installed'"
    ["Development Packages"]="pacman -Qs base-devel"
)

# AUR Helpers submenu
declare -A aur_helpers=(
    ["Yay - Search AUR"]="echo 'Enter package name:' && read pkg && yay -Ss \$pkg"
    ["Yay - Install AUR Package"]="echo 'Enter package name:' && read pkg && yay -S \$pkg"
    ["Yay - Update AUR Packages"]="yay -Sua"
    ["Paru - Search AUR"]="echo 'Enter package name:' && read pkg && paru -Ss \$pkg"
    ["Paru - Install AUR Package"]="echo 'Enter package name:' && read pkg && paru -S \$pkg"
    ["Paru - Update AUR Packages"]="paru -Sua"
    ["List AUR Packages"]="pacman -Qm"
    ["AUR Package Information"]="echo 'Enter AUR package name:' && read pkg && yay -Si \$pkg || paru -Si \$pkg"
)

# Function to show category selection
show_main_menu() {
    local categories=()
    for category in "${!menu_categories[@]}"; do
        categories+=("$category")
    done
    
    # Sort categories for consistent display
    IFS=$'\n' sorted_categories=($(sort <<<"${categories[*]}")); unset IFS
    
    local selected_category
    while true; do
        selected_category=$(zenity --list \
            --title="Arch Linux Tools v1.0" \
            --text="Select a category:" \
            --column="Categories" \
            --width=400 \
            --height=300 \
            "${sorted_categories[@]}" \
            2>/dev/null)
        
        if [[ -z "$selected_category" ]]; then
            # User cancelled or closed dialog
            break
        fi
        
        show_submenu "$selected_category"
    done
}

# Function to show submenu based on category
show_submenu() {
    local category="$1"
    local category_key="${menu_categories[$category]}"
    
    if [[ -z "$category_key" ]]; then
        zenity --error --text="Unknown category: $category"
        return
    fi
    
    # Get reference to the appropriate associative array
    local -n submenu_ref="$category_key"
    
    local tools=()
    for tool in "${!submenu_ref[@]}"; do
        tools+=("$tool")
    done
    
    # Sort tools for consistent display
    IFS=$'\n' sorted_tools=($(sort <<<"${tools[*]}")); unset IFS
    
    local selected_tool
    while true; do
        selected_tool=$(zenity --list \
            --title="$category - Tools" \
            --text="Select a tool to run:" \
            --column="Tools" \
            --width=500 \
            --height=400 \
            "${sorted_tools[@]}" \
            "« Back to Categories" \
            2>/dev/null)
        
        if [[ -z "$selected_tool" ]]; then
            # User cancelled or closed dialog
            break
        elif [[ "$selected_tool" == "« Back to Categories" ]]; then
            # User wants to go back
            break
        fi
        
        execute_tool "$selected_tool" "$category_key"
    done
}

# Function to execute selected tool
execute_tool() {
    local tool="$1"
    local category_key="$2"
    
    # Get reference to the appropriate associative array
    local -n submenu_ref="$category_key"
    
    local command="${submenu_ref[$tool]}"
    
    if [[ -z "$command" ]]; then
        zenity --error --text="Unknown tool: $tool"
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

# Function to show about dialog
show_about() {
    zenity --info \
        --title="About Arch Linux Tools" \
        --text="Arch Linux Tools Menu v1.0\n\nA GUI menu system for common Arch Linux tools and utilities.\n\nRequires: zenity, terminal emulator\nOptional: yay, paru, neofetch, nmap\n\nDouble-click tools to execute them." \
        --width=350
}

# Function to show help
show_help() {
    zenity --info \
        --title="Help - Arch Linux Tools" \
        --text="Usage:\n\n1. Select a category from the main menu\n2. Choose a tool from the submenu\n3. Confirm execution\n4. Commands run in a new terminal window\n\nNote: Some commands require root privileges and will prompt for your password.\n\nUse '« Back to Categories' to return to the main menu." \
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