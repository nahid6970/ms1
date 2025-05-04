# Function to install SDDM theme
sddm_theme() {
  echo -e "${CYAN}📦 Installing Sugar Candy theme...${NC}"
  if ! pacman -Q sddm-theme-sugar-candy &>/dev/null; then
    yay -S --noconfirm --needed sddm sddm-theme-sugar-candy
  else
    echo -e "${GREEN}✅ sddm-theme-sugar-candy is already installed.${NC}"
  fi

  echo -e "${CYAN}📝 Configuring /etc/sddm.conf...${NC}"
  sudo bash -c 'cat > /etc/sddm.conf <<EOF
[Theme]
Current=Sugar-Candy

[General]
Numlock=on
EOF'

  echo -e "${GREEN}✅ SDDM theme set to Sugar-Candy and NumLock enabled.${NC}"
}

# Function to install the chosen desktop environment
display_manager() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) SDDM"
    echo -e "2) GDM"
    echo -e "3) LightDM"
    echo -e "4) LXDM"
    echo -e "5) XDM"
    echo -e "6) None (CLI only)"
    read -p "Enter the number (1-6): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing SDDM...${NC}"
            sudo pacman -S --noconfirm --needed sddm
            sudo systemctl enable sddm
            sudo systemctl disable gdm lightdm lxdm xdm
            sudo pacman -Syu

            # Ask about theme
            read -p "Do you want to install and set up the Sugar Candy SDDM theme? (y/n): " THEME_CHOICE
            if [[ "$THEME_CHOICE" =~ ^[Yy]$ ]]; then
                sddm_theme
            else
                echo -e "${YELLOW}Skipping SDDM theme installation.${NC}"
                # Write Numlock configuration if theme is skipped
                echo -e "${CYAN}📝 Configuring /etc/sddm.conf for Numlock...${NC}"
                sudo bash -c 'cat > /etc/sddm.conf <<EOF
[General]
Numlock=on
EOF'
                echo -e "${GREEN}✅ NumLock enabled in /etc/sddm.conf.${NC}"
            fi
            ;;
        2)
            echo -e "${GREEN}Installing gdm...${NC}"
            sudo pacman -Sy --noconfirm --needed gdm
            yay -S --needed extension-manager
            sudo systemctl enable gdm
            sudo systemctl disable sddm lightdm lxdm xdm
            sudo pacman -Syu
            echo -e "${GREEN}Install these extensions: +OpenBar +PaperWM${NC}"
            ;;
        3)
            echo -e "${GREEN}Installing LightDM...${NC}"
            sudo pacman -S --needed lightdm lightdm-gtk-greeter
            sudo systemctl enable lightdm
            sudo systemctl disable sddm gdm lxdm xdm
            sudo pacman -Syu
            ;;
        4)
            echo -e "${GREEN}Installing LXDM...${NC}"
            sudo pacman -S --needed lxdm
            sudo systemctl enable lxdm
            sudo systemctl disable sddm gdm lightdm xdm
            sudo pacman -Syu
            ;;
        5)
            echo -e "${GREEN}Installing XDM...${NC}"
            sudo pacman -S --needed xdm
            sudo systemctl enable xdm
            sudo systemctl disable sddm gdm lightdm lxdm
            sudo pacman -Syu
            ;;
        6)
            echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac

    echo -e "${GREEN}Desktop environment installation complete.${NC}"
}
