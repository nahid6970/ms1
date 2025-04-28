#!/bin/bash

# Define color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Dummy functions
setup_user_password() {
    echo -e "${GREEN}Setting up username and password...${NC}"
    # Example commands:
    read -rp "Enter username: " username
    useradd -m "$username"
    passwd "$username"
    usermod -aG wheel "$username"
    echo "%wheel ALL=(ALL) ALL" >> /etc/sudoers
}

install_base_system() {
    echo -e "${GREEN}Installing base system...${NC}"
    # pacstrap /mnt base linux linux-firmware etc...
}

install_aur_helper() {
    echo -e "${GREEN}Installing yay (AUR helper)...${NC}"
    # git clone and install yay
}

install_desktop_environment() {
    echo -e "${GREEN}Installing Desktop Environment...${NC}"
    echo "1) KDE Plasma"
    echo "2) GNOME"
    echo "3) XFCE"
    echo "4) Sway (Wayland)"
    read -rp "Choose Desktop (1-4): " de_choice
    case "$de_choice" in
        1) echo "Installing KDE..." ;;
        2) echo "Installing GNOME..." ;;
        3) echo "Installing XFCE..." ;;
        4) echo "Installing Sway..." ;;
        *) echo -e "${RED}Invalid desktop choice.${NC}" ;;
    esac
}

finalize_installation() {
    echo -e "${GREEN}Finalizing installation...${NC}"
    # generate fstab, etc
}

exit_script() {
    echo -e "${RED}Exiting script. Goodbye!${NC}"
    exit 0
}

# The Menu
while true; do
    echo ""
    echo -e "${YELLOW}Select an option:${NC}"
    echo -e "${BLUE}1) Setup Username & Password${NC}"
    echo -e "${BLUE}2) Install Base System${NC}"
    echo -e "${BLUE}3) Install AUR Helper (yay)${NC}"
    echo -e "${BLUE}4) Install Desktop Environment${NC}"
    echo -e "${BLUE}5) Finalize Installation${NC}"
    echo -e "${RED}e) Exit${NC}"
    echo ""

    read -rp "Enter choice: " choice

    case "$choice" in
        1) setup_user_password ;;
        2) install_base_system ;;
        3) install_aur_helper ;;
        4) install_desktop_environment ;;
        5) finalize_installation ;;
        e|E) exit_script ;;
        *) echo -e "${RED}Invalid option. Please try again.${NC}" ;;
    esac
done
