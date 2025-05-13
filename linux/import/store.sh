#!/bin/bash

store_setup() {

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Choose setup option:${NC}"
echo -e "1) Flatpak + bauh"
echo -e "2) Snap Store"
read -rp "Enter your choice (1/2): " choice

flatpak_store() {
    clear
    sudo pacman -S --needed flatpak
    flatpak remote-add --if-not-exists --user flathub https://dl.flathub.org/repo/flathub.flatpakrepo
    yay -S --needed bauh
    echo "Flatpak with bauh Store Installed"
}

snap_store() {
    clear
    git clone https://aur.archlinux.org/snapd.git
    cd snapd
    makepkg -si
    sudo systemctl enable --now snapd.socket
    sudo systemctl enable --now snapd.apparmor.service
}



case $choice in
    1) flatpak_store ;;
    2) snap_store ;;
    *) echo "Invalid choice." ;;
esac

}
