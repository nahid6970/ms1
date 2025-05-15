#!/bin/bash

install_bar() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color

    echo -e "${GREEN}Choose a status bar to install:${NC}"
    echo -e "1) Waybar - Highly customizable bar for Wayland compositors"
    echo -e "2) Polybar - Popular, feature-rich bar for X11 and Wayland (via XWayland)"
    echo -e "3) Lemonbar (bar) - Minimalist, scriptable X11 bar"
    echo -e "4) Xmobar - Minimalistic, text-based X11 bar (Haskell-based)"
    echo -e "5) Dzen2 - Lightweight, scriptable X11 bar"
    echo -e "6) Tint2 - Lightweight panel and taskbar for X11"
    read -rp "Enter your choice (1-6): " choice

    case $choice in
        1)
            echo "Installing Waybar..."
            sudo pacman -S --needed waybar
            ;;
        2)
            echo "Installing Polybar..."
            sudo pacman -S --needed polybar
            ;;
        3)
            echo "Installing Lemonbar..."
            sudo pacman -S --needed lemonbar
            ;;
        4)
            echo "Installing Xmobar..."
            sudo pacman -S --needed xmobar
            ;;
        5)
            echo "Installing Dzen2..."
            sudo pacman -S --needed dzen
            ;;
        6)
            echo "Installing Tint2..."
            sudo pacman -S --needed tint2
            ;;
        *)
            echo "Invalid choice."
            ;;
    esac
}

install_bar
