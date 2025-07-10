#!/bin/bash

# ==============================================================================
#
#                           Arch Linux Setup Script
#
#   A comprehensive script to set up and configure an Arch Linux environment,
#   including desktop environments, packages, utilities, and custom configs.
#
# ==============================================================================

# ------------------------------------------------------------------------------
# Globals & Imports
# ------------------------------------------------------------------------------

# Import external script libraries
for file in ~/ms1/linux/import/*.sh; do
    [[ -r "$file" ]] && source "$file" || echo "Error sourcing $file" >&2
done

# Define color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ------------------------------------------------------------------------------
# Menu Definitions
# ------------------------------------------------------------------------------

# Menu items: "Description : function_name(s) : color"
menu_items=(
    "Git Pull [ms1] + Copy Config     : update_ms1_repo All_Configs :$GREEN"
    "Initial Setup (sddm + wallpaper) : sddm_setup wallpaper        :$GREEN"
    "Install Necessary Packages       : install_packages            :$GREEN"
    "Display & Graphics Setup         : display_setup_menu          :$CYAN"
    "YAY Setup                        : setup_yay                   :$GREEN"
    "TTY Setup                        : tty_numlock_setup           :$GREEN"
    "Store Setup                      : store_setup                 :$GREEN"
    "Container                        : Container_setup             :$GREEN"
    "About                            : about_device                :$GREEN"
    "Rclone-Decrypt                   : rclone_decrypt              :$RED"
    "Rclone-linux_binary              : rclone_copy_linuxbin        :$RED"
    "GPU Drivers                      : check_gpu_drivers           :$GREEN"
    "Neovim Config                    : nvim_config                 :$GREEN"
    "Enable Numlock                   : enable_early_numlock        :$GREEN"
    "SDDM                             : sddm_setup                  :$GREEN"
    "Arch Install                     : arch_install                :$GREEN"
)

# Special hotkey items: "[key]=function_name"
declare -A hotkeys=(
    [c]="Close_script"
    [e]="exit_script"
    [x]="test_test"
)

#* ==========================================================
#*
#*                           CORE & SYSTEM FUNCTIONS
#*
#* ==========================================================

#! ---------------------------------------------------------
#! Core Menu Logic
#! ---------------------------------------------------------

# Generic function to display a submenu
# $1: Menu title (string)
# $2: Name of the menu items array (string, passed by reference)
display_submenu() {
    local title="$1"
    local -n items_array="$2" # Use nameref to get the array by its name

    while true; do
        clear
        echo -e "${CYAN}${title}${NC}"

        for i in "${!items_array[@]}"; do
            IFS=":" read -r description function color <<< "${items_array[$i]}"
            echo -e "${color}$((i+1))) $description${NC}"
        done
        echo -e "${RED}q) Quit to main menu${NC}"

        read -p "Enter choice: " choice

        if [[ "$choice" == "q" ]]; then
            break
        elif [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#items_array[@]} )); then
            IFS=":" read -r _ function _ <<< "${items_array[$((choice-1))]}"
            function=$(echo "$function" | xargs) # Trim whitespace
            if declare -f "$function" > /dev/null; then
                $function
            else
                echo -e "${RED}Error: Function '$function' not found.${NC}"
            fi
            read -p "Press Enter to continue..."
        else
            echo -e "${RED}Invalid option. Please try again.${NC}"
            read -p "Press Enter to continue..."
        fi
    done
}

#! ---------------------------------------------------------
#! System Configuration & Setup
#! ---------------------------------------------------------

All_Configs(){
    echo "Setting all configs..."
    cp -a "$HOME/ms1/linux/config/bashrc" "$HOME/.bashrc"
    cp -a "$HOME/ms1/linux/config/autostart.sh" "$HOME/autostart.sh"
    cp -a "$HOME/ms1/linux/config/.config/hypr" "$HOME/.config/"
    cp -a "$HOME/ms1/linux/config/.config/xmonad" "$HOME/.xmonad"
    cp -a "$HOME/ms1/linux/config/.config/qtile" "$HOME/.config"
    cp -a "$HOME/ms1/linux/config/.config/conky" "$HOME/.config/"
    cp -a "$HOME/ms1/linux/config/.config/foot" "$HOME/.config/"
    cp -a "$HOME/ms1/linux/config/.config/waybar" "$HOME/.config/"
    cp -a "$HOME/ms1/linux/config/.config/wofi" "$HOME/.config/"
    cp -a "$HOME/ms1/linux/config/.config/dunst" "$HOME/.config/"
    cp -a "$HOME/ms1/linux/config/.config/starship/starship.toml" "$HOME/.config"
    source "$HOME/.bashrc"
    echo -e "${GREEN}All configurations applied.${NC}"
}

arch_install(){
    echo -e "${YELLOW}Starting Arch Linux installation...${NC}"
    archinstall --config "$HOME/ms1/linux/arch_setup_config/user_configuration.json" --creds "$HOME/ms1/linux/arch_setup_config/user_credentials.json"
}

setup_yay() {
    clear
    echo -e "${CYAN}Installing yay (AUR helper)...${NC}"
    sudo pacman -Sy --needed --noconfirm base-devel git
    if [ ! -d "/tmp/yay" ]; then
        git clone https://aur.archlinux.org/yay.git /tmp/yay
    fi
    cd /tmp/yay || exit
    makepkg -si --noconfirm
    echo -e "${GREEN}yay has been installed successfully.${NC}"
}

update_ms1_repo() {
    clear
    local ms1_folder="$HOME/ms1"
    if [ -d "$ms1_folder" ]; then
        echo "Changing directory to $ms1_folder and pulling updates..."
        cd "$ms1_folder" && git pull || { echo "Git pull failed."; return 1; }
        echo "Repository updated successfully."
    else
        echo "The folder $ms1_folder does not exist."
        return 1
    fi
}

#* ===================================================================
#*
#*                       DESKTOP & UI CONFIGURATION
#*
#* ===================================================================

#! -----------------------------------------------------------
#! Main Display & Graphics Menu
#! -----------------------------------------------------------

display_menu_items=(
    "Display Server (X11/Wayland)    :display_server_menu   :$GREEN"
    "Desktop Environment             :desktop_environment_menu :$GREEN"
    "Window Manager / Compositor     :wm_compositor_menu    :$GREEN"
    "Status Bar                      :statusbar_menu        :$GREEN"
)

display_setup_menu() {
    display_submenu "Display & Graphics Setup" "display_menu_items"
}

#! ------------------------------------------------------
#! Display Servers
#! ------------------------------------------------------

display_server_menu_items=(
    "Install Xorg (X11)                :install_xorg      :$GREEN"
    "Install Wayland Core Components   :install_wayland   :$GREEN"
)

display_server_menu() {
    display_submenu "Select a Display Server" "display_server_menu_items"
}

install_xorg() { 
    echo -e "${GREEN}Installing Xorg Server...${NC}"
    sudo pacman -S --needed xorg-server xorg-xinit xorg-xwayland xorg-apps mesa xf86-video-intel xf86-video-amdgpu xf86-input-libinput; 
}

install_wayland(){
    echo -e "${GREEN}Installing Wayland Core Components...${NC}"
    sudo pacman -S --needed wayland wayland-protocols wayland-utils xdg-desktop-portal xdg-desktop-portal-wlr wlroots libinput gtk3 qt5-wayland xorg-xwayland
}

#! -------------------------------------------------------------------
#! Desktop Environments
#! -------------------------------------------------------------------

desktop_environment_menu_items=(
    "KDE Plasma     :install_kde     :$GREEN"
    "GNOME          :install_gnome   :$GREEN"
    "XFCE           :install_xfce    :$GREEN"
    "None (CLI only):skip_install    :$YELLOW"
)

desktop_environment_menu() {
    display_submenu "Select a Desktop Environment" "desktop_environment_menu_items"
}

install_kde() {
    echo -e "${GREEN}Installing KDE Plasma...${NC}"
    sudo pacman -S --noconfirm --needed plasma kde-gtk-config dolphin konsole plasma-desktop sddm
    yay -S --needed sddm-theme-sugar-candy
    sudo systemctl enable sddm
    read -p "Do you want to install and set up the Sugar Candy SDDM theme? (y/n): " THEME_CHOICE
    if [[ "$THEME_CHOICE" =~ ^[Yy]$ ]]; then sddm_theme; else sddm_numlock; fi
    sudo pacman -Syu
}

install_gnome() {
    echo -e "${GREEN}Installing GNOME...${NC}"
    sudo pacman -Sy --noconfirm --needed gnome gnome-tweaks gnome-terminal gdm
    yay -S --needed extension-manager
    sudo systemctl enable gdm
    sudo pacman -Syu
    echo -e "${GREEN}Install these extensions +OpenBar +PaperWM${NC}"
}

install_xfce() {
    echo -e "${GREEN}Installing XFCE...${NC}"
    sudo pacman -S --needed xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
    sudo systemctl enable lightdm
    sudo pacman -Syu
}

skip_install() {
    echo -e "${YELLOW}Skipping installation.${NC}"
}

#! ------------------------------------------------------------------
#! Window Managers & Compositors
#! ------------------------------------------------------------------

wm_compositor_menu_items=(
    "Hyprland (Wayland) :install_hyprland :$GREEN"
    "DWM (X11)          :install_dwm      :$GREEN"
    "Xmonad (X11)       :install_xmonad   :$GREEN"
    "qtile (X11/Wayland):install_qtile    :$GREEN"
    "Sway (Wayland)     :install_sway     :$GREEN"
    "Wayfire (Wayland)  :install_wayfire  :$GREEN"
    "river (Wayland)    :install_river    :$GREEN"
    "Weston (Wayland)   :install_weston   :$GREEN"
    "Picom (X11)        :install_picom    :$GREEN"
)

wm_compositor_menu() {
    display_submenu "Select a Window Manager / Compositor" "wm_compositor_menu_items"
}

install_hyprland() {
    echo -e "${YELLOW}Installing Hyprland...${NC}"
    install_wayland # Ensure Wayland core is installed
    sudo pacman -S --needed foot kitty hyprland xdg-desktop-portal-hyprland
    sudo pacman -S --needed waybar wofi xorg-xwayland hyprpaper hyprlock grim slurp wl-clipboard
    sudo pacman -S --needed qt5-wayland qt6-wayland rofi-wayland
    echo "📜 Setting environment variables in .bash_profile..."
    PROFILE_FILE="$HOME/.bash_profile"
    grep -q XDG_SESSION_TYPE "$PROFILE_FILE" || cat >> "$PROFILE_FILE" <<'EOF'
export XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=Hyprland
export QT_QPA_PLATFORM=wayland
export MOZ_ENABLE_WAYLAND=1
EOF
    echo "🎉 Setup complete! Run 'source ~/.bash_profile' and then 'Hyprland'."
    sudo pacman -Syu
}

install_dwm() {
    echo -e "${YELLOW}Installing DWM...${NC}"
    install_xorg # Ensure Xorg is installed
    yay -S --needed dwm st dmenu xorg-xsetroot sddm
    sudo systemctl enable sddm
    echo -e "📝 Setting up DWM with SDDM and custom wallpaper..."
    if ! command -v feh &>/dev/null; then sudo pacman -S --noconfirm feh; fi
    WALLPAPER_DIR="$HOME/Pictures/wallpapers" && mkdir -p "$WALLPAPER_DIR"
    WALLPAPER_PATH="$WALLPAPER_DIR/wallpaper1.jpg"
    curl -L -o "$WALLPAPER_PATH" "https://www.skyweaver.net/images/media/wallpapers/wallpaper1.jpg"
    grep -qxF "feh --bg-scale \"$WALLPAPER_PATH\"" ~/.xprofile || echo "feh --bg-scale \"$WALLPAPER_PATH\"" >> ~/.xprofile
    sudo bash -c "cat > /usr/share/xsessions/dwm.desktop <<EOF
[Desktop Entry]
Encoding=UTF-8
Name=DWM
Comment=Dynamic Window Manager
Exec=dwm
Icon=dwm
Type=XSession
EOF"
    echo -e "✅ Setup complete! Select 'DWM' in SDDM and reboot."
}

install_xmonad() {
    echo -e "${YELLOW}Installing Xmonad + Xmobar...${NC}"
    install_xorg # Ensure Xorg is installed
    sudo pacman -S --needed xmonad xmonad-utils xmonad-contrib xmobar xterm dmenu nitrogen picom gnome-terminal
    mkdir -p "$HOME/.xmonad"
    cp ~/ms1/linux/config/xmonad/xmonad.hs ~/.xmonad/
    sddm_setup
    wallpaper
}

install_qtile() {
    echo -e "${YELLOW}Installing qtile...${NC}"
    sudo pacman -S --needed qtile python-pywlroots xorg-xwayland kitty dmenu picom network-manager-applet volumeicon mypy
    sudo pacman -S --needed rofi-wayland
    yay -S --needed qtile-extras
}

install_sway() { sudo pacman -S --needed sway waybar; }
install_wayfire() { yay -S --needed wayfire wcm wf-shell; }
install_weston() { sudo pacman -S --needed weston; }
install_river() { sudo pacman -S --needed river; }
install_picom() { sudo pacman -S --needed picom; }

#! ---------------------------------------------------------------
#! Status Bars
#! ---------------------------------------------------------------
statusbar_menu_items=(
    "Waybar - Highly customizable bar for Wayland           :install_waybar   :$GREEN"
    "Polybar - Popular, feature-rich bar for X11            :install_polybar  :$GREEN"
    "Lemonbar (bar) - Minimalist, scriptable X11 bar        :install_lemonbar :$GREEN"
    "Xmobar - Minimalistic, text-based X11 bar (Haskell)    :install_xmobar   :$GREEN"
    "Dzen2 - Lightweight, scriptable X11 bar                :install_dzen2    :$GREEN"
    "Tint2 - Lightweight panel and taskbar for X11          :install_tint2    :$GREEN"
)
statusbar_menu() {
    display_submenu "Setup Statusbar" "statusbar_menu_items"
}

install_waybar() { sudo pacman -S --needed waybar; }
install_polybar() { sudo pacman -S --needed polybar; }
install_lemonbar() { sudo pacman -S --needed lemonbar; }
install_xmobar() { sudo pacman -S --needed xmobar; }
install_dzen2() { sudo pacman -S --needed dzen; }
install_tint2() { sudo pacman -S --needed tint2; }

# ====================================================================
#
#                           PACKAGE MANAGEMENT
#
# ====================================================================

package_install_items=(
    "Install Base Packages :install_base_packages :$GREEN"
    "Install Fonts         :install_fonts         :$GREEN"
    "Install Utilities     :install_utilities     :$GREEN"
    "Install Media Packages:install_media_packages:$GREEN"
)
install_packages() {
    clear
    echo -e "${GREEN}Updating package database...${NC}"
    sudo pacman -Sy --noconfirm
    display_submenu "Install Packages Submenu" "package_install_items"
}

install_base_packages() {
    echo -e "${GREEN}Installing Base Packages...${NC}"
    sudo pacman -S --needed bash bat chafa curl eza fastfetch fzf lsd lua-language-server neovim openssh python rclone sshpass wget which zoxide yazi zsh stow expac numlockx rsync thefuck feh screenfetch sed grep jq rofi conky htop firefox dunst mypy pcmanfm thunar thunar-archive-plugin thunar-volman foot starship
}

install_fonts() {
    echo -e "${GREEN}Installing Fonts...${NC}"
    sudo pacman -S --needed ttf-jetbrains-mono-nerd ttf-jetbrains-mono
}

install_utilities() {
    echo -e "${GREEN}Installing Utilities...${NC}"
    sudo pacman -S --needed rsync
}

install_media_packages() {
    echo -e "${GREEN}Installing Media Packages...${NC}"
    sudo pacman -S --needed vlc audacious
}

# ==============================================================================
#
#                           TTY & CONSOLE
#
# ==============================================================================

tty_setup=(
    "Auto Login            :enable_tty_autologin  :$GREEN"
    "Numlock Enable        :enable_numlock_on_tty :$GREEN"
    "Disable Terminal Bell :disable_bell          :$GREEN"
    "TTY Font              :tty_font              :$GREEN"
)
tty_numlock_setup() {
    display_submenu "Setup TTY & NumLock" "tty_setup"
}

enable_tty_autologin() {
    local user=${1:-$USER}
    local service_dir="/etc/systemd/system/getty@tty1.service.d"
    local override_file="$service_dir/override.conf"
    echo "Setting up auto-login for user: $user on tty1..."
    sudo mkdir -p "$service_dir"
    sudo bash -c "cat > '$override_file'" <<EOF
[Service]
ExecStart=
ExecStart=-/usr/bin/agetty --autologin $user --noclear %I $TERM
EOF
    sudo systemctl daemon-reexec && sudo systemctl daemon-reload && sudo systemctl restart getty@tty1
    echo "✅ Auto-login setup complete for user: $user on tty1."
}

enable_numlock_on_tty() {
    if ! command -v numlockx &> /dev/null; then sudo pacman -S --noconfirm numlockx; fi
    sudo tee /usr/local/bin/numlock > /dev/null <<'EOF'
#!/bin/bash
for tty in /dev/tty{1..6}; do /usr/bin/setleds -D +num < "$tty"; done
EOF
    sudo chmod +x /usr/local/bin/numlock
    sudo tee /etc/systemd/system/numlock.service > /dev/null <<'EOF'
[Unit]
Description=Enable NumLock on TTYs
[Service]
ExecStart=/usr/local/bin/numlock
StandardInput=tty
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload && sudo systemctl enable numlock.service && sudo systemctl start numlock.service
    sudo mkdir -p /etc/systemd/system/getty@.service.d
    sudo tee /etc/systemd/system/getty@.service.d/activate-numlock.conf > /dev/null <<'EOF'
[Service]
ExecStartPre=/bin/sh -c 'setleds -D +num < /dev/%I'
EOF
    sudo systemctl daemon-reload && sudo systemctl restart systemd-logind.service
    echo "NumLock has been enabled on TTYs."
}

disable_bell() {
    echo "Disabling terminal bell..."
    echo 'set bell-style none' >> ~/.inputrc && bind -f ~/.inputrc
    echo 'set bell-style none' | sudo tee -a /etc/inputrc
    echo "blacklist pcspkr" | sudo tee /etc/modprobe.d/nobeep.conf > /dev/null
    sudo rmmod pcspkr 2>/dev/null
    echo "Bell disabled. Reboot or re-login for full effect."
}

tty_font() {
    local FONT_DIR="/usr/share/kbd/consolefonts"
    if [ ! -d "$FONT_DIR" ]; then echo "Console font directory not found."; return 1; fi
    local selected_font
    selected_font=$(find "$FONT_DIR" -type f -name '*.psf*' | fzf --preview 'setfont {} && echo -e "\033[1;32mPreview: {}\033[0m"' --preview-window=up:5)
    if [ -n "$selected_font" ]; then
        sudo setfont "$selected_font"
        echo "Font changed to: $(basename "$selected_font")"
    else
        echo "No font selected."
    fi
}

enable_early_numlock() {
  echo -e "${CYAN}📦 Installing mkinitcpio-numlock from AUR...${NC}"
  yay -S --noconfirm --needed mkinitcpio-numlock
  echo -e "${CYAN}🛠️ Adding 'numlock' hook to /etc/mkinitcpio.conf...${NC}"
  if grep -q "HOOKS=.*numlock" /etc/mkinitcpio.conf; then
    echo -e "${YELLOW}⚠️ 'numlock' hook already present. Skipping.${NC}"
  else
    sudo sed -i -E 's/(HOOKS=.*)(encrypt|block)/\1numlock \2/' /etc/mkinitcpio.conf
    echo -e "${GREEN}✅ 'numlock' hook added.${NC}"
  fi
  echo -e "${CYAN}🔄 Regenerating initramfs...${NC}"
  sudo mkinitcpio -P
  echo -e "${GREEN}✅ Early NumLock enabled.${NC}"
}

#* ===============================================================
#*
#*                       APPLICATIONS & CONTAINERS
#*
#* ===============================================================

container_function=(
    "Steam     :steam_cont       :$GREEN"
    "Lutris    :lutris_cont      :$GREEN"
    "Bottles   :bottles_cont     :$GREEN"
    "Wine      :install_wine     :$GREEN"
    "Wine64    :install_wine_64  :$GREEN"
)
Container_setup() {
    display_submenu "Setup Container" "container_function"
}

steam_cont() { sudo pacman -S --needed steam; }
lutris_cont() { sudo pacman -S --needed lutris; }
bottles_cont() { yay -S --needed bottles; }

install_wine() {
  echo "Installing Wine (32-bit prefix)..."
  sudo pacman -S --needed wine wine-mono wine-gecko winetricks lib32-mesa lib32-mpg123 lib32-openal
  WINEPREFIX="$HOME/.wine" wineboot --init
  winetricks -q corefonts vcrun2019
  echo "Wine installation and setup complete."
}

install_wine_64() {
  if ! command -v wine &>/dev/null; then
    echo "Wine is not installed. Installing..."
    sudo pacman -S --needed wine wine-mono wine-gecko winetricks lib32-mesa lib32-mpg123 lib32-openal
  fi
  export WINEARCH=win64
  export WINEPREFIX="$HOME/.wine64"
  if [ ! -d "$WINEPREFIX" ]; then
    echo "Creating 64-bit Wine prefix at $WINEPREFIX..."
    wineboot --init
  fi
  if command -v winetricks &>/dev/null; then
    winetricks -q corefonts vcrun2019
  fi
  echo "Wine 64-bit setup complete."
}

#* ====================================================================
#*
#*                           UTILITIES & TOOLS
#*
#* ====================================================================

#! -------------------------------------------------------------------
#! Rclone & Cloud
#! -------------------------------------------------------------------

rclone_decrypt() {
    clear
    echo "Decrypting rclone.conf..."
    sudo pacman -S --needed python-pycryptodomex
    python ~/ms1/termux/locker/locker.py --decrypt ~/ms1/asset/rclone/rclone.conf.enc
    echo "Copying rclone.conf to ~/.config/rclone/"
    mkdir -p "$HOME/.config/rclone"
    cp "$HOME/ms1/asset/rclone/rclone.conf" "$HOME/.config/rclone"
}

rclone_copy_linuxbin() {
    clear
    echo "Copying Linux binary files from cloud..."
    rclone sync o0:/msBackups/linux_binary/ "$HOME/linux_binary/" -P --check-first --transfers=10 --track-renames --fast-list
    curl -L -o "$HOME/linux_binary/wallpaper/wallpaper1.jpg" "https://www.skyweaver.net/images/media/wallpapers/wallpaper1.jpg"
    echo 'Downloading Wallpaper Complete'
}

rclone_setup() {
    clear
    local RCLONE_CONFIG_DIR="$HOME/.config/rclone"
    local SOURCE_CONF_FILE="$HOME/storage/shared/rclone.conf"
    mkdir -p "$RCLONE_CONFIG_DIR"
    if [ -f "$SOURCE_CONF_FILE" ]; then
        cp "$SOURCE_CONF_FILE" "$RCLONE_CONFIG_DIR/"
        echo "rclone.conf copied successfully."
    else
        echo "Source file $SOURCE_CONF_FILE does not exist."
        return 1
    fi
}

Restore_Songs() {
    clear
    local DEST_DIR="$HOME/storage/shared/song"
    local REMOTE="gu:/song"
    echo "Syncing songs from $REMOTE to $DEST_DIR..."
    rclone sync "$REMOTE" "$DEST_DIR" -P --check-first --transfers=1 --track-renames --fast-list
    echo "Songs restored successfully."
}

ntfy_remove() {
    clear
    echo "Deleting g00:ntfy file..."
    rclone delete g00:ntfy
}

#! ----------------------------------------------------------
#! Development & Editors
#! ----------------------------------------------------------

nvim_config() {
    echo "Linking Neovim configuration..."
    ln -sf "$HOME/ms1/linux/config/nvim/" "$HOME/.config/nvim"
    echo "Neovim configuration linked."
}

# Termux-specific nvim setup
nvim_setup() {
    clear
    echo -e "${BLUE}Setting up Neovim configuration for Termux...${NC}"
    mkdir -p "$NVIM_CONFIG_DEST"
    cp "$NVIM_INIT_SOURCE" "$NVIM_CONFIG_DEST/init.lua"
    curl -o /data/data/com.termux/files/usr/bin/install-in-mason https://raw.githubusercontent.com/Amirulmuuminin/setup-mason-for-termux/main/install-in-mason
    chmod +x /data/data/com.termux/files/usr/bin/install-in-mason
    install-in-mason lua-language-server
}

# ------------------------------------------------------------------------------
# DWM Specific Functions
# ------------------------------------------------------------------------------

dwm_config() {
    echo "Configuring DWM..."
    rsync -a --delete "$HOME/ms1/config/dwm/dwm/.xinitrc" "$HOME/.xinitrc"
    rsync -a --delete "$HOME/ms1/config/dwm/dwm/.xprofile" "$HOME/.xprofile"
    if ! grep -q 'source ~/.xprofile' ~/.xinitrc; then
        echo "source ~/.xprofile" >> ~/.xinitrc
    fi
}

dwm_statusbar() {
    echo "Configuring DWM Statusbar (succade)..."
    cd ~/ || return
    yay -S --needed git base-devel lemonbar libinih
    git clone https://github.com/domsson/succade.git
    cd succade || { echo "Failed to enter succade directory"; return 1; }
    chmod +x ./build && ./build
    mkdir -p ~/.config/succade
    cp ./cfg/example1.ini ~/.config/succade/succaderc
    chmod +x ./bin/succade
    cp ./bin/succade ~/.local/bin/
    echo "Succade has been successfully installed!"
}

distrotube_dwm_config(){
    echo "Building and installing DistroTube's DWM blocks..."
    cd ~/ms1/linux/config/dwm/dwmblocks_dt_fixed/ || return
    make && sudo make clean install
    chmod +x scripts/*
    echo "DT DWM blocks installed."
}

# ---------------------------------------------
# System Info & Diagnostics
# ---------------------------------------------

about_device() {
    clear
    fastfetch
}

check_gpu_drivers() {
    echo -e "${GREEN}Detecting GPU and checking drivers...${NC}"
    GPU_INFO=$(lspci | grep -E "VGA|3D")
    echo -e "${YELLOW}Detected GPU: ${GPU_INFO}${NC}"
    if echo "$GPU_INFO" | grep -qi "AMD"; then
        echo -e "${YELLOW}AMD GPU detected.${NC}"
        missing_pkgs=()
        for pkg in mesa mesa-vulkan-drivers vulkan-radeon lib32-vulkan-radeon lib32-mesa; do
            if ! pacman -Q "$pkg" &>/dev/null; then
                missing_pkgs+=("$pkg")
            fi
        done
        if [ ${#missing_pkgs[@]} -ne 0 ]; then
            echo -e "${YELLOW}Missing AMD drivers: ${missing_pkgs[*]}. Install them? (y/n)${NC}"
            read -rp "> " answer
            if [[ "$answer" =~ ^[Yy]$ ]]; then yay -S --noconfirm "${missing_pkgs[@]}"; fi
        else
            echo -e "${GREEN}All required AMD GPU drivers are installed.${NC}"
        fi
    else
        echo -e "${YELLOW}Non-AMD GPU detected. Skipping AMD driver check.${NC}"
    fi
}

list_recent_packages() {
    echo -e "${GREEN}Listing recently installed packages...${NC}"
    expac --timefmt='%Y-%m-%d %H:%M:%S' '%l\t%n' | sort -r
}

network_speed_test() {
    clear
    echo "Testing network speed..."
    if ! command -v speedtest &> /dev/null; then
        sudo apt install -y speedtest-cli
    fi
    speedtest
}

list_large_files() {
    clear
    local target_dir=${1:-$PWD}
    echo "Finding top 10 largest files in $target_dir..."
    find "$target_dir" -type f -exec du -h {} + | sort -rh | head -n 10
}

rofi_install_wayland() {
  echo -e "${CYAN}📦 Installing Rofi (Wayland)...${NC}"
  sudo pacman -S --needed rofi-wayland
  echo -e "${GREEN}✅ Rofi Installed. Run with 'rofi -show drun'.${NC}"
}

# ---------------------------------------------------------
# Script Control
# ---------------------------------------------------------

Close_script() {
    clear
    echo -e "${GREEN}Exiting the script. Goodbye!${NC}"
    exit 0
}

exit_script() {
    # For Termux specifically
    am startservice -a com.termux.service_stop com.termux/.app.TermuxService
    exit
}

welcome_remove() {
    # For Termux specifically
    clear
    echo "Creating .hushlogin to disable welcome message..."
    touch "$HOME/.hushlogin"
}

# =================================================================
#
#                               MAIN EXECUTION
#
# =================================================================

main() {
    while true; do
        clear
        echo -e "${YELLOW}Select an option:${NC}"
        # Show numbered menu items
        for i in "${!menu_items[@]}"; do
            IFS=":" read -r description function color <<< "${menu_items[$i]}"
            echo -e "${color}$((i+1))) $description${NC}"
        done
        # Show hotkey items
        echo -e "${RED}c) Close${NC}"
        echo -e "${RED}e) Exit (Termux)${NC}"
        echo -e "${RED}x) Test${NC}"
        echo ""
        read -p "Enter choice: " choice

        if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#menu_items[@]} )); then
            IFS=":" read -r _ function _ <<< "${menu_items[$((choice-1))]}"
            function=$(echo "$function" | xargs) # Trim whitespace
            # Execute all space-separated functions
            for cmd in $function; do
                if declare -f "$cmd" > /dev/null; then
                    $cmd
                else
                    echo -e "${RED}Error: Command '$cmd' not found.${NC}"
                fi
            done
            read -p "Press Enter to return to the menu..."
        elif [[ -n "${hotkeys[$choice]}" ]]; then
            ${hotkeys[$choice]}
        else
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 2
        fi
    done
}

# Run the main menu
main