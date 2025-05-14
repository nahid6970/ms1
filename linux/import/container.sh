#!/bin/bash

container_setup() {

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Choose setup option:${NC}"
echo -e "1) Steam"
echo -e "2) Lutris"
echo -e "3) Bottles"
read -rp "Enter your choice (1/2/3): " choice

lutris_cont() {
    clear
    sudo pacman -S --needed lutris
}

steam_cont() {
    clear
    sudo pacman -S --needed steam
}

bottles_cont() {
    clear
    sudo pacman -S --needed bottles 
}



case $choice in
    1) steam_cont ;;
    2) lutris_cont ;;
    3) bottles_cont ;;
    *) echo "Invalid choice." ;;
esac

}
