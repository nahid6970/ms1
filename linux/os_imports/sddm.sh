RED='\033[0;31m'
GREEN='\033[0;32m'

# Function to configure SDDM with optional Sugar Candy theme and NumLock
sddm_setup() {
  echo -e "${RED}🔧 Installing SDDM if not already present...${NC}"
  sudo pacman -S --needed sddm

  echo -e "${CYAN}🔧 Choose setup option:${NC}"
  echo -e "1) NumLock only"
  echo -e "2) NumLock + SDDM Sugar Candy theme"
  read -rp "Enter your choice (1/2): " choice

  # Check for valid input
  if [[ "$choice" != "1" && "$choice" != "2" ]]; then
    echo -e "${RED}❌ Invalid choice. Exiting.${NC}"
    return 1
  fi

  # Configure NumLock only
  if [[ "$choice" == "1" ]]; then
    echo -e "${CYAN}📝 Configuring /etc/sddm.conf to enable NumLock...${NC}"
    sudo bash -c 'cat > /etc/sddm.conf <<EOF
[General]
Numlock=on
EOF'
    echo -e "${GREEN}✅ NumLock enabled in /etc/sddm.conf.${NC}"
  else
    # Configure NumLock + SDDM theme
    echo -e "${CYAN}📦 Installing Sugar Candy theme...${NC}"
    if ! pacman -Q sddm-theme-sugar-candy &>/dev/null; then
      yay -S --noconfirm --needed sddm-theme-sugar-candy
    else
      echo -e "${GREEN}✅ sddm-theme-sugar-candy is already installed.${NC}"
    fi

    echo -e "${CYAN}📝 Configuring /etc/sddm.conf with theme and NumLock settings...${NC}"
    sudo bash -c 'cat > /etc/sddm.conf <<EOF
[Theme]
Current=Sugar-Candy

[General]
Numlock=on
EOF'
    echo -e "${GREEN}✅ SDDM theme set to Sugar-Candy and NumLock enabled.${NC}"
  fi

  # Enable SDDM service
  echo -e "${CYAN}🚀 Enabling SDDM to start on boot...${NC}"
  sudo systemctl enable sddm
  echo -e "${GREEN}✅ SDDM service enabled.${NC}"
}




# sddm_theme() {
#   echo "📦 Installing Sugar Candy theme..."
#   if ! pacman -Q sddm-theme-sugar-candy &>/dev/null; then
#     yay -S --noconfirm --needed sddm sddm-theme-sugar-candy
#   else
#     echo "✅ sddm-theme-sugar-candy is already installed."
#   fi

#   echo "📝 Configuring /etc/sddm.conf..."
#   sudo bash -c 'cat > /etc/sddm.conf <<EOF
# [Theme]
# Current=Sugar-Candy

# [General]
# Numlock=on
# EOF'

#   echo "✅ SDDM theme set to Sugar-Candy and NumLock enabled."
# }