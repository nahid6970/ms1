#!/bin/bash

# Check if dialog is installed
if ! command -v dialog &> /dev/null; then
    echo "The 'dialog' utility is not installed. Please install it to run this script."
    echo "You can install it with: sudo pacman -S dialog"
    exit 1
fi

# Function to display a message box after a command
function show_result {
    dialog --title "Command Output" --msgbox "$1" 20 70
}

# Main menu loop
while true; do
    main_choice=$(dialog --clear --backtitle "Arch Linux Tools" \
        --title "Main Menu" \
        --menu "Select a category:" 15 50 3 \
        1 "System Management" \
        2 "Package Management" \
        3 "System Information" \
        0 "Exit" \
        2>&1 >/dev/tty)

    clear
    case $main_choice in
        1)
            while true; do
                sys_choice=$(dialog --clear --backtitle "Arch Linux Tools" \
                    --title "System Management" \
                    --menu "Select a command:" 15 50 4 \
                    1 "Update System (pacman -Syu)" \
                    2 "Clean Package Cache (pacman -Scc)" \
                    3 "List Orphaned Packages" \
                    0 "Back to Main Menu" \
                    2>&1 >/dev/tty)

                clear
                case $sys_choice in
                    1)
                        sudo pacman -Syu
                        show_result "System update process finished."
                        ;;
                    2)
                        sudo pacman -Scc
                        show_result "Package cache cleaned."
                        ;;
                    3)
                        orphans=$(pacman -Qtdq)
                        if [ -z "$orphans" ]; then
                            show_result "No orphaned packages found."
                        else
                            show_result "Orphaned Packages:\n\n$orphans"
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
                pkg_choice=$(dialog --clear --backtitle "Arch Linux Tools" \
                    --title "Package Management" \
                    --menu "Select a command:" 15 60 4 \
                    1 "Install AUR Helper (yay)" \
                    2 "List Explicitly Installed Packages" \
                    3 "Find package providing a file" \
                    0 "Back to Main Menu" \
                    2>&1 >/dev/tty)

                clear
                case $pkg_choice in
                    1)
                        if ! command -v yay &> /dev/null; then
                            git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si
                            show_result "Yay has been installed."
                        else
                            show_result "Yay is already installed."
                        fi
                        ;;
                    2)
                        packages=$(pacman -Qe)
                        dialog --title "Explicitly Installed Packages" --msgbox "$packages" 20 70
                        ;;
                    3)
                        file_path=$(dialog --title "Input" --inputbox "Enter the full path to the file:" 8 60 2>&1 >/dev/tty)
                        if [ -n "$file_path" ]; then
                            owner=$(sudo pacman -Qo "$file_path")
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
                info_choice=$(dialog --clear --backtitle "Arch Linux Tools" \
                    --title "System Information" \
                    --menu "Select a command:" 15 50 4 \
                    1 "Show System Info (neofetch)" \
                    2 "Show Disk Usage (df -h)" \
                    3 "Show Running Processes (htop)" \
                    0 "Back to Main Menu" \
                    2>&1 >/dev/tty)

                clear
                case $info_choice in
                    1)
                        if ! command -v neofetch &> /dev/null; then
                            sudo pacman -S neofetch
                        fi
                        neofetch
                        read -p "Press Enter to continue..."
                        ;;
                    2)
                        df -h
                        read -p "Press Enter to continue..."
                        ;;
                    3)
                        if ! command -v htop &> /dev/null; then
                            sudo pacman -S htop
                        fi
                        htop
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