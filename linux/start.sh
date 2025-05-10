#!/bin/bash

# Clear any existing desktop session
# killall Xorg

# Start the selected desktop environment
case $1 in
    kde)
        exec startplasma-x11
        ;;
    gnome)
        exec gnome-session
        ;;
    xfce)
        exec startxfce4
        ;;
    hyprland)
        exec Hyprland
        ;;
    dwm)
        exec dwm
        ;;
    xmonad)
        exec xmonad
        ;;
    qtile)
        exec qtile start
        ;;
    *)
        echo "Invalid choice or desktop environment not installed."
        ;;
esac
