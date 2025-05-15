#!/bin/bash

compositor_setup() {

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Choose setup option:${NC}"
echo -e "1) Sway - A tiling Wayland compositor and drop-in replacement for i3."
echo -e "2) Wayfire - A 3D Wayland compositor with Compiz-like effects."
echo -e "3) Hyprland - A dynamic tiling Wayland compositor with modern features."
echo -e "4) Weston - The reference Wayland compositor, primarily for testing."
echo -e "5) river - A dynamic tiling compositor inspired by dwm."
echo -e "6) Xorg - The legacy display server, required for many traditional X11 applications."
echo -e "7) Picom (Xorg/X11) - A compositor for X11, providing shadows, transparency, and animations."
echo -e "8) Extra tools - Useful Wayland utilities (wlr-randr, grim, slurp)."
read -rp "Enter your choice (1/2/3/4/5/6/7/8): " choice

sway_cont() {
    clear
    sudo pacman -S --needed sway waybar
}

wayfire_cont() {
    clear
    sudo pacman -S --needed wayfire wcm wf-shell
}

hyprland_cont() {
    clear
    yay -S --needed hyprland hyprpaper waybar-hyprland
}

weston_cont() {
    clear
    sudo pacman -S --needed weston
}

river_cont() {
    clear
    sudo pacman -S --needed river
}

xorg_cont() {
    clear
    sudo pacman -S --needed xorg-server xorg-xinit xorg-xwayland xorg-apps
}

picom_cont() {
    clear
    sudo pacman -S --needed picom
}

extras_cont() {
    clear
    sudo pacman -S --needed wlr-randr grim slurp
}

case $choice in
    1) sway_cont ;;
    2) wayfire_cont ;;
    3) hyprland_cont ;;
    4) weston_cont ;;
    5) river_cont ;;
    6) xorg_cont ;;
    7) picom_cont ;;
    8) extras_cont ;;
    *) echo "Invalid choice." ;;
esac

}
