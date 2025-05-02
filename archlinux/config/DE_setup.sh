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
            sudo pacman -S --noconfirm plasma kde-gtk-config dolphin konsole plasma-desktop sddm

            echo -e "${GREEN}Installing Sugar Candy theme for SDDM from AUR...${NC}"
            yay -S --noconfirm sddm-theme-sugar-candy

            # Set Sugar Candy as the default SDDM theme
            sudo sed -i '/^Current=/d' /etc/sddm.conf 2>/dev/null
            sudo sed -i '/^\[Theme\]/a Current=sugar-candy' /etc/sddm.conf 2>/dev/null || \
            sudo bash -c 'echo -e "[Theme]\nCurrent=sugar-candy" >> /etc/sddm.conf'

            # Enable SDDM display manager
            sudo systemctl enable sddm

            # Final full system upgrade
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
