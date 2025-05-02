# Function to install the chosen desktop environment
install_desktop_environment() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    echo -e "4) None (CLI only)"
    read -p "Enter the number (1-4): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing KDE Plasma...${NC}"
            # pacman -Sy --noconfirm plasma kde-gtk-config dolphin konsole plasma-desktop sddm
            sudo pacman -S plasma kde-gtk-config dolphin konsole plasma-desktop sddm
            sudo systemctl enable sddm
            sudo pacman -Syu
            ;;
        2)
            echo -e "${GREEN}Installing GNOME...${NC}"
            pacman -Sy --noconfirm gnome gnome-tweaks gnome-terminal gdm
            systemctl enable gdm
            ;;
        3)
            echo -e "${GREEN}Installing XFCE...${NC}"
            pacman -Sy --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
            systemctl enable lightdm
            ;;
        4)
            echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
            ;;
        5)
            echo -e "${YELLOW}Installing Hyprland...${NC}"
            sudo pacman -S kitty
            sudo pacman -S hyprland xdg-desktop-portal-hyprland wayland wlroots
            sudo pacman -S waybar wofi foot xorg-xwayland
            sudo pacman -S hyprpaper hyprlock grim slurp wl-clipboard
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac

    echo -e "${GREEN}Desktop environment installation complete.${NC}"
}

install_desktop_environment
