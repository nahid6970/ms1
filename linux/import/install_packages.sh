# Function to install necessary packages using yay
install_packages() {
    clear
    echo -e "${GREEN}Updating package database...${NC}"
    sudo pacman -Sy --noconfirm
    echo -e "${GREEN}Installing Necessary Packages...${NC}"
    sudo pacman -S --needed \
        bash bat chafa curl eza fastfetch fzf \
        lsd lua-language-server neovim \
        openssh python rclone sshpass wget \
        which zoxide yazi zsh stow expac numlockx \
        rsync ttf-jetbrains-mono-nerd ttf-jetbrains-mono \
        thefuck feh screenfetch sed grep jq rofi conky \
        htop firefox dunst mypy pcmanfm thunar thunar-archive-plugin thunar-volman \
        vlc audacious \
        foot starship 
}