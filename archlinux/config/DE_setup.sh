# Function to install the chosen desktop environment
install_desktop_environment() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    echo -e "4) Hyprland"
    echo -e "5) None (CLI only)"
    read -p "Enter the number (1-4): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing KDE Plasma...${NC}"
            sudo pacman -S --noconfirm --needed plasma kde-gtk-config dolphin konsole plasma-desktop sddm
            # sudo yay -S sddm-theme-sugar-candy
            sudo systemctl enable sddm
            # Final full system upgrade
            sudo pacman -Syu
            ;;
        2)
            echo -e "${GREEN}Installing GNOME...${NC}"
            pacman -Sy --noconfirm --needed gnome gnome-tweaks gnome-terminal gdm
            systemctl enable gdm
            ;;
        3)
            echo -e "${GREEN}Installing XFCE...${NC}"
            pacman -Sy --noconfirm --needed  xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
            systemctl enable lightdm
            ;;
        4)
            echo -e "${YELLOW}Installing Hyprland...${NC}"
            # Install essential packages
            sudo pacman -S --needed foot hyprland xdg-desktop-portal xdg-desktop-portal-hyprland wayland wlroots gtk3 sddm
            sudo pacman -S --needed waybar wofi xorg-xwayland hyprpaper hyprlock grim slurp wl-clipboard
            sudo systemctl enable sddm
            ;;
        5)
            echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac

    echo -e "${GREEN}Desktop environment installation complete.${NC}"
}

install_desktop_environment
