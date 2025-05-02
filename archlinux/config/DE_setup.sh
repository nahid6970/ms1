# Function to install the chosen desktop environment
install_desktop_environment() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    echo -e "4) Hyprland (3d ACC + Log in 2/3 times to work) kitty/alacritty doesnt work on vms"
    echo -e "5) None (CLI only)"
    read -p "Enter the number (1-4): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing KDE Plasma...${NC}"
            sudo pacman -S --noconfirm plasma kde-gtk-config dolphin konsole plasma-desktop sddm
            # sudo yay -S sddm-theme-sugar-candy
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
            echo -e "${YELLOW}Installing Hyprland...${NC}"
            # Install essential packages
            sudo pacman -S --needed foot hyprland xdg-desktop-portal-hyprland wayland wlroots gtk3
            sudo pacman -S --needed waybar wofi xorg-xwayland hyprpaper hyprlock grim slurp wl-clipboard
            # Auto-generate default config if missing
            CONFIG_DIR="$HOME/.config/hypr"
            CONFIG_FILE="$CONFIG_DIR/hyprland.conf"
            # Launch Hyprland once in a nested session to generate config (safe in VMs or TTYs)
            if [ ! -f "$CONFIG_FILE" ]; then
                echo "Generating Hyprland config using hyprland..."
                mkdir -p "$CONFIG_DIR"
                Hyprland
                sleep 2
                pkill Hyprland
            fi
            # Replace kitty with foot if config exists
            if [ -f "$CONFIG_FILE" ]; then
                echo "Replacing 'kitty' with 'foot' in config..."
                sed -i 's/kitty/foot/g' "$CONFIG_FILE"
            else
                echo "❌ Could not find hyprland.conf to patch."
            fi
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
