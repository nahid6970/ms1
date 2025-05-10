#!/bin/bash

# Kill any running Xorg or Wayland sessions
if pgrep Xorg > /dev/null; then
    killall Xorg
fi

if pgrep Hyprland > /dev/null; then
    killall Hyprland
fi

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <desktop_environment>"
    echo "Available options: kde, gnome, xfce, hyprland, dwm, xmonad, qtile"
    exit 1
fi

# Start the selected desktop environment
case $1 in
    kde)
        echo "Starting KDE Plasma..."
        exec startplasma-x11
        ;;
    gnome)
        echo "Starting GNOME..."
        exec gnome-session
        ;;
    xfce)
        echo "Starting XFCE..."
        exec startxfce4
        ;;
    hyprland)
        echo "Starting Hyprland..."
        exec Hyprland
        ;;
    dwm)
        echo "Starting DWM..."
        exec startx dwm
        ;;
    xmonad)
        echo "Starting Xmonad..."
        exec startx xmonad
        ;;
    qtile)
        echo "Starting Qtile..."
        exec startx qtile
        ;;
    *)
        echo "Invalid choice or desktop environment not installed."
        exit 1
        ;;
esac
