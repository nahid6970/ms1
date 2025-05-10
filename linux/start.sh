echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
echo -e "1) KDE Plasma"
echo -e "2) GNOME"
echo -e "3) XFCE"
echo -e "4) Hyprland"
echo -e "5) DWM"
echo -e "6) Xmonad + Xmobar"
echo -e "7) qtile"
echo -e "8) None (CLI only)"
read -p "Enter the number (1-8): " DE_CHOICE

case $DE_CHOICE in
    1) export DESKTOP_ENV=kde ;;
    2) export DESKTOP_ENV=gnome ;;
    3) export DESKTOP_ENV=xfce ;;
    4) export DESKTOP_ENV=hyprland ;;
    5) export DESKTOP_ENV=dwm ;;
    6) export DESKTOP_ENV=xmonad ;;
    7) export DESKTOP_ENV=qtile ;;
    8) export DESKTOP_ENV=none ;;
    *) echo -e "${RED}Invalid choice. No desktop environment set.${NC}"; exit 1 ;;
esac

echo "export DESKTOP_ENV=$DESKTOP_ENV" >> ~/.bash_profile
