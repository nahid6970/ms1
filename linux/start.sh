#!/bin/bash

# Kill any running Xorg or Wayland sessions
if pgrep Xorg > /dev/null; then
    killall Xorg
fi

if pgrep Hyprland > /dev/null; then
    killall Hyprland
fi

# Display the menu
echo "Select a desktop environment:"
echo "1) KDE Plasma"
echo "2) GNOME"
echo "3) XFCE"
echo "4) Hyprland"
echo "5) DWM"
echo "6) Xmonad"
echo "7) Qtile"
echo -n "Enter your choice (1-7): "
read choice

# Start the selected desktop environment
case $choice in
    1)
        echo "Starting KDE Plasma..."
        exec startplasma-x11
        ;;
    2)
        echo "Starting GNOME..."
        exec gnome-session
        ;;
    3)
        echo "Starting XFCE..."
        exec startxfce4
        ;;
    4)
        echo "Starting Hyprland..."
        exec Hyprland
        ;;
    5)
        echo "Starting DWM..."
        exec startx dwm
        ;;
    6)
        echo "Starting Xmonad..."
        exec startx xmonad
        ;;
    7)
        echo "Starting Qtile..."

        # Start a new DBus session and export env vars
        eval "$(dbus-launch --sh-syntax)"
        export DBUS_SESSION_BUS_ADDRESS
        export DBUS_SESSION_BUS_PID

        # Start dunst inside the same DBus session
        XWAYLAND_FORCE=1 dunst &

        export QT_QPA_PLATFORM=wayland

        # Important: start Qtile *inside* the same dbus session
        exec qtile start -b wayland
        ;;

esac
