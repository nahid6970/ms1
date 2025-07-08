#!/bin/bash

# Check if zenity is installed
if ! command -v zenity &> /dev/null; then
    echo "The 'zenity' utility is not installed. Please install it to run this script."
    # Attempt to offer installation for common package managers
    if command -v pacman &> /dev/null; then
        echo "You can install it with: sudo pacman -S zenity"
    elif command -v apt-get &> /dev/null; then
        echo "You can install it with: sudo apt-get install zenity"
    elif command -v dnf &> /dev/null; then
        echo "You can install it with: sudo dnf install zenity"
    fi
    exit 1
fi

# Function to display a message box after a command
function show_result {
    zenity --info --title="Command Output" --text="$1" --width=500 --height=300
}

# Main menu loop
while true; do
    main_choice=$(zenity --list \
        --title="Main Menu" --text="Select a category:" \
        --column="ID" --column="Category" \
        1 "System Management" \
        2 "Package Management" \
        3 "System Information" \
        0 "Exit")

    # Exit if the user closes the dialog or clicks cancel
    if [ -z "$main_choice" ]; then
        break
    fi

    case $main_choice in
        1)
            while true; do
                sys_choice=$(zenity --list \
                    --title="System Management" --text="Select a command:" \
                    --column="ID" --column="Action" \
                    1 "Update System (pacman -Syu)" \
                    2 "Clean Package Cache (pacman -Scc)" \
                    3 "List Orphaned Packages" \
                    0 "Back to Main Menu")

                if [ -z "$sys_choice" ]; then break; fi
                case $sys_choice in
                    1)
                        gnome-terminal -- sudo pacman -Syu
                        show_result "System update process finished."
                        ;;
                    2)
                        sudo pacman -Scc --noconfirm
                        show_result "Package cache cleaned."
                        ;;
                    3)
                        orphans=$(pacman -Qtdq)
                        if [ -z "$orphans" ]; then
                            show_result "No orphaned packages found."
                        else
                            zenity --text-info --title="Orphaned Packages" --filename=<(echo "$orphans")
                        fi
                        ;;
                    0)
                        break
                        ;;
                esac
            done
            ;;
        2)
            while true; do
                pkg_choice=$(zenity --list \
                    --title="Package Management" --text="Select a command:" \
                    --column="ID" --column="Action" \
                    1 "Install AUR Helper (yay)" \
                    2 "List Explicitly Installed Packages" \
                    3 "Find package providing a file" \
                    0 "Back to Main Menu")

                if [ -z "$pkg_choice" ]; then break; fi
                case $pkg_choice in
                    1)
                        if ! command -v yay &> /dev/null; then
                            zenity --question --text="Yay is not installed. Do you want to clone and build it now?" && \
                            gnome-terminal -- bash -c "git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si; exec bash"
                        else
                            show_result "Yay is already installed."
                        fi
                        ;;
                    2)
                        packages=$(pacman -Qe)
                        zenity --text-info --title="Explicitly Installed Packages" --filename=<(echo "$packages")
                        ;;
                    3)
                        file_path=$(zenity --entry --title="Input" --text="Enter the full path to the file:")
                        if [ -n "$file_path" ]; then
                            owner=$(sudo pacman -Qo "$file_path" 2>&1)
                            show_result "$owner"
                        fi
                        ;;
                    0)
                        break
                        ;;
                esac
            done
            ;;
        3)
            while true; do
                info_choice=$(zenity --list \
                    --title="System Information" --text="Select a command:" \
                    --column="ID" --column="Action" \
                    1 "Show System Info (neofetch)" \
                    2 "Show Disk Usage (df -h)" \
                    3 "Show Running Processes (htop)" \
                    0 "Back to Main Menu")

                if [ -z "$info_choice" ]; then break; fi
                case $info_choice in
                    1)
                        if ! command -v neofetch &> /dev/null; then
                            zenity --question --text="neofetch is not installed. Install it?" && sudo pacman -S neofetch
                        fi
                        gnome-terminal -- bash -c "neofetch; exec bash"
                        ;;
                    2)
                        usage=$(df -h)
                        zenity --text-info --title="Disk Usage" --filename=<(echo "$usage")
                        ;;
                    3)
                        if ! command -v htop &> /dev/null; then
                            zenity --question --text="htop is not installed. Install it?" && sudo pacman -S htop
                        fi
                        gnome-terminal -- htop
                        ;;
                    0)
                        break
                        ;;
                esac
            done
            ;;
        0)
            echo "Exiting."
            break
            ;;
    esac
done
