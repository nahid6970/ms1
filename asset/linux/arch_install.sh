#!/bin/bash

# Define some color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Dummy functions for now
setup_user_password() {
    echo -e "${GREEN}Setting up username and password...${NC}"
    # Actual user/password setup commands here
}

install_base_system() {
    echo -e "${GREEN}Installing base system...${NC}"
    # Actual base install commands here
}

install_aur_helper() {
    echo -e "${GREEN}Installing AUR helper (yay)...${NC}"
    # Actual AUR helper install here
}

install_desktop_environment() {
    echo -e "${GREEN}Installing Desktop Environment...${NC}"
    # You can add sub-options here if you want
}

finalize_installation() {
    echo -e "${GREEN}Finalizing installation...${NC}"
    # Final touches here
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
