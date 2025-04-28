#!/bin/bash

# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Menu items (only numbers now!)
menu_items=(
    "1:Install KDE Plasma:install_kde:$BLUE"
    "2:Install GNOME:install_gnome:$BLUE"
    "3:Install XFCE:install_xfce:$BLUE"
    "4:Install Sway (Wayland):install_sway:$BLUE"
    "5:Exit:exit_script:$RED"
)

# Your functions
install_kde() {
    echo -e "${GREEN}Installing KDE Plasma...${NC}"
    # Your install commands here
}
install_gnome() {
    echo -e "${GREEN}Installing GNOME...${NC}"
    # Your install commands here
}
install_xfce() {
    echo -e "${GREEN}Installing XFCE...${NC}"
    # Your install commands here
}
install_sway() {
    echo -e "${GREEN}Installing Sway (Wayland)...${NC}"
    # Your install commands here
}
exit_script() {
    echo -e "${RED}Exiting...${NC}"
    exit 0
}

# Show menu
while true; do
    echo ""
    echo -e "${YELLOW}Select an option:${NC}"
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description function color <<< "$item"
        echo -e "${color}$number) $description${NC}"
    done

    echo ""
    read -p "Enter choice: " choice

    valid_choice=false
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description function color <<< "$item"
        if [ "$choice" = "$number" ]; then
            valid_choice=true
            $function
            break
        fi
    done

    if [ "$valid_choice" = false ]; then
        echo -e "${RED}Invalid option. Please try again.${NC}"
    fi
done
