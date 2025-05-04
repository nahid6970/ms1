# Function to install the chosen desktop environment
display_manager() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) SDDM"
    echo -e "2) GDM"
    echo -e "3) LightDM"
    echo -e "4) None (CLI only)"
    read -p "Enter the number (1-4): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing SDDM...${NC}"
            sudo pacman -S --noconfirm --needed sddm
            sudo yay -S sddm-theme-sugar-candy
            sudo systemctl enable sddm
            sudo pacman -Syu
            ;;
        2)
            echo -e "${GREEN}Installing gdm...${NC}"
            sudo pacman -Sy --noconfirm --needed gdm
            yay -S --needed extension-manager
            sudo systemctl enable gdm
            sudo pacman -Syu
            echo -e "${GREEN}Install these extensions +OpenBar +PaperWM${NC}"
            ;;
        3)
            echo -e "${GREEN}Installing LightDM...${NC}"
            sudo pacman -S --needed lightdm lightdm-gtk-greeter
            sudo systemctl enable lightdm
            sudo pacman -Syu
            ;;
        4)
            echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac

    echo -e "${GREEN}Desktop environment installation complete.${NC}"
}

display_manager
