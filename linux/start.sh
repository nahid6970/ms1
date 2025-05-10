#!/bin/bash

# Function to install the chosen desktop environment
start_os() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    echo -e "4) Hyprland"
    echo -e "5) DWM"
    echo -e "6) Xmonad + Xmobar"
    echo -e "7) qtile"
    echo -e "8) None (CLI only)"
    read -p "Enter the number (1-6): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing KDE Plasma...${NC}"

            ;;
        2)
            echo -e "${GREEN}Installing GNOME...${NC}"

            ;;
        3)
            echo -e "${GREEN}Installing XFCE...${NC}"

            ;;
        4)
            echo -e "${YELLOW}Installing Hyprland...${NC}"

            ;;
        5)
            echo -e "${YELLOW}Installing DWM.${NC}"
            ;;
        6)
            echo -e "${YELLOW}Installing Xmonad + Xmobar.${NC}"

            ;;
        7)
            echo -e "${YELLOW}Installing qtile.${NC}"
            qtile start
            ;;
        8)
            echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac

    echo -e "${GREEN}Desktop environment installation complete.${NC}"
}

start_os
