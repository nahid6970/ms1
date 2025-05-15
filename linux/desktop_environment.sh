#!/bin/bash

# import list
source ~/ms1/linux/os_imports/wallpaper.sh
source ~/ms1/linux/os_imports/sddm.sh

# Function to install the chosen desktop environment
desktop_environment() {
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
            sudo pacman -S --noconfirm --needed plasma kde-gtk-config dolphin konsole plasma-desktop sddm
            yay -S --needed sddm-theme-sugar-candy
            sudo systemctl enable sddm
            
            # Ask about theme
            read -p "Do you want to install and set up the Sugar Candy SDDM theme? (y/n): " THEME_CHOICE
            if [[ "$THEME_CHOICE" =~ ^[Yy]$ ]]; then
                sddm_theme  # Assuming sddm_theme is for theme setup
            else
                sddm_numlock  # Assuming sddm_numlock handles the NumLock configuration
            fi

            sudo pacman -Syu
            ;;
        2)
            echo -e "${GREEN}Installing GNOME...${NC}"
            sudo pacman -Sy --noconfirm --needed gnome gnome-tweaks gnome-terminal gdm
            yay -S --needed extension-manager
            sudo systemctl enable gdm
            sudo pacman -Syu
            echo -e "${GREEN}Install these extensions +OpenBar +PaperWM${NC}"
            ;;
        3)
            echo -e "${GREEN}Installing XFCE...${NC}"
            sudo pacman -S --needed  xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
            sudo systemctl enable lightdm
            sudo pacman -Syu
            ;;
        4)
            echo -e "${YELLOW}Installing Hyprland...${NC}"
            #! for hyprland need to enable 3d accelaration in the virtual io
            # Install essential packages
            sudo pacman -S --needed foot kitty hyprland xdg-desktop-portal xdg-desktop-portal-hyprland wayland wayland-utils wlroots gtk3
            sudo pacman -S --needed waybar wofi xorg-xwayland hyprpaper hyprlock grim slurp wl-clipboard
            sudo pacman -S --needed qt5-wayland qt6-wayland rofi-wayland

            echo "📜 Setting environment variables..."
            PROFILE_FILE="$HOME/.bash_profile"
            grep -q XDG_SESSION_TYPE "$PROFILE_FILE" || cat >> "$PROFILE_FILE" <<'EOF'
# Hyprland env
export XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=Hyprland
export QT_QPA_PLATFORM=wayland
export MOZ_ENABLE_WAYLAND=1
EOF
            echo "✅ Updated: $PROFILE_FILE"
            echo "🎉 Setup complete! Now run:"
            echo "➡️  source ~/.bash_profile"
            echo "➡️  Hyprland"

            sudo pacman -Syu
            ;;
        5)
            echo -e "${YELLOW}Installing DWM.${NC}"
            ;;
        6)
            echo -e "${YELLOW}Installing Xmonad + Xmobar.${NC}"
            #! compton vs picom --for arch select picom [these are compositor for x11 --compton is for ubuntu]
            sudo pacman -S --needed xmonad xmonad-utils xmonad-contrib xmobar xterm dmenu nitrogen picom gnome-terminal
            mkdir -p $HOME/.xmonad
            cp ~/ms1/linux/config/xmonad/xmonad.hs ~/.xmonad/
            sddm_setup
            wallpaper
            ;;
        7)
            echo -e "${YELLOW}Installing qtile.${NC}"
            sudo pacman -S --needed qtile python-pywlroots xorg-xwayland kitty dmenu picom network-manager-applet volumeicon mypy
            rclone copy "$HOME/ms1/linux/config/.config/qtile" "$HOME/.config/qtile"

            # qtile start #!xorg/x11
            # qtile start -b wayland #!wayland

            # sddm_setup
            # wallpaper
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

desktop_environment
