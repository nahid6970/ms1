#!/bin/bash

#! import list
for file in ~/ms1/linux/import/*.sh; do [[ -r "$file" ]] && source "$file" || echo "Error sourcing $file" >&2; done
#! C:\ms1\linux\import\compositors.sh
#! C:\ms1\linux\import\container.sh
#! C:\ms1\linux\import\sddm.sh
#! C:\ms1\linux\import\StatusBar.sh
#! C:\ms1\linux\import\store.sh
#! C:\ms1\linux\import\tty.sh
#! C:\ms1\linux\import\wallpaper.sh

# Define some color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Menu items: description : function : color
menu_items=(
    "Git Pull [ms1] + Copy Config     : update_ms1_repo All_Configs :$GREEN"
    # "Copy Config Files                : All_Configs                 :$GREEN"
    "Initial Setup (sddm + wallpaper) : sddm_setup wallpaper        :$GREEN"
    "Install Necessary Packages       : install_packages            :$GREEN"
    "Desktop Environment              : desktop_environment         :$GREEN" #! C:\ms1\linux\desktop_environment.sh
    "Compositor + Utilities           : compositor_setup            :$GREEN" #! C:\ms1\linux\import\compositors.sh
    "Status Bar                       : install_bar                 :$GREEN"
    # "X-Org/X11                      : xorg                        :$GREEN"
    # "Wayland                        : wayland                     :$GREEN"
    "YAY Setup                        : setup_yay                   :$GREEN"
    "TTY Setup                        : tty_numlock_setup           :$GREEN"
    "Store Setup                      : store_setup                 :$GREEN"
    "Container                        : Container_setup             :$GREEN"
    "About                            : about_device                :$GREEN"
    "Rclone-Decrypt                   : rclone_decrypt              :$RED"
    "Rclone-linux_binary              : rclone_copy_linuxbin        :$RED"
    "GPU Drivers                      : check_gpu_drivers           :$GREEN"
    # "Hyprland                         : setup_hyprland_full         :$GREEN"
    # "Hyprland Config                  : hyperland_config            :$GREEN"
    # "Rofi for Hyprland                : rofi_install_wayland        :$GREEN"
    "Neovim Config                    : nvim_config                 :$GREEN"
    "Enable Numlock                   : enable_early_numlock        :$GREEN"
    # "DWM Setup                        : dwm_wm                      :$GREEN"
    # "DWM Config                       : dwm_config                  :$GREEN"
    # "DWM ST                           : dwm_statusbar               :$GREEN"
    # "DWM Distrotube                   : distrotube_dwm_config       :$GREEN"
    "SDDM                             : sddm_setup                  :$GREEN"
    "Arch Install                     : arch_install                :$GREEN"
    # "bottles                        : not_yet_choosen             :$GREEN"
    # "wine                           : not_yet_choosen             :$GREEN"
    # "Lutris                         : not_yet_choosen             :$GREEN"
    # "steam                          : not_yet_choosen             :$GREEN"
    # "Heroic Games Launcher          : check_gpu_drivers           :$GREEN"
)

# Special hotkey items
declare -A hotkeys=(
    [c]="Close_script"
    [e]="exit_script"
    [x]="test_test"
)

All_Configs(){
echo Set All configs

cp -a "$HOME/ms1/linux/config/bashrc" "$HOME/.bashrc"
cp -a "$HOME/ms1/linux/config/autostart.sh" "$HOME/autostart.sh"

cp -a "$HOME/ms1/linux/config/.config/hypr" "$HOME/.config/" #! C:\ms1\linux\config\.config\hypr\hyprland.conf
cp -a "$HOME/ms1/linux/config/.config/xmonad" "$HOME/.xmonad" #! C:\ms1\linux\config\.config\xmonad\xmonad.hs
cp -a "$HOME/ms1/linux/config/.config/qtile" "$HOME/.config" #! C:\ms1\linux\config\.config\qtile\config.py

cp -a "$HOME/ms1/linux/config/.config/conky" "$HOME/.config/" #! C:\ms1\linux\config\.config\conky\conky_hyprland.conf
cp -a "$HOME/ms1/linux/config/.config/foot" "$HOME/.config/" #! C:\ms1\linux\config\.config\foot\foot.ini
cp -a "$HOME/ms1/linux/config/.config/waybar" "$HOME/.config/" #! C:\ms1\linux\config\.config\waybar\config.jsonc
cp -a "$HOME/ms1/linux/config/.config/wofi" "$HOME/.config/"
cp -a "$HOME/ms1/linux/config/.config/dunst" "$HOME/.config/" #! C:\ms1\linux\config\.config\dunst\dunstrc
cp -a "$HOME/ms1/linux/config/.config/starship/starship.toml" "$HOME/.config" #! C:\ms1\linux\config\.config\starship\starship.toml

# source $HOME/autostart.sh
# echo -e "${RED}Please run 'source ~/.bashrc' to apply changes to your current shell.${NC}"
source "$HOME/.bashrc"
}


arch_install(){
    archinstall --config $HOME/ms1/linux/arch_setup_config/user_configuration.json --creds $HOME/ms1/linux/arch_setup_config/user_credentials.json
}

# Generic function to display a submenu
# $1: Menu title (string)
# $2: Name of the menu items array (string)
display_submenu() {
    local title="$1"
    local -n items_array="$2" # Use nameref to get the array

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
            function=$(echo "$function" | xargs)
            # Check if function exists before calling
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

# ██████╗ ██╗███████╗██████╗ ██╗      █████╗ ██╗   ██╗    ███████╗███╗   ██╗██╗   ██╗██╗██████╗  ██████╗ ███╗   ██╗███╗   ███╗███████╗███╗   ██╗████████╗
# ██╔══██╗██║██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝    ██╔════╝████╗  ██║██║   ██║██║██╔══██╗██╔═══██╗████╗  ██║████╗ ████║██╔════╝████╗  ██║╚══██╔══╝
# ██║  ██║██║███████╗██████╔╝██║     ███████║ ╚████╔╝     █████╗  ██╔██╗ ██║██║   ██║██║██████╔╝██║   ██║██╔██╗ ██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║
# ██║  ██║██║╚════██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝      ██╔══╝  ██║╚██╗██║╚██╗ ██╔╝██║██╔══██╗██║   ██║██║╚██╗██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║
# ██████╔╝██║███████║██║     ███████╗██║  ██║   ██║       ███████╗██║ ╚████║ ╚████╔╝ ██║██║  ██║╚██████╔╝██║ ╚████║██║ ╚═╝ ██║███████╗██║ ╚████║   ██║
# ╚═════╝ ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚══════╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝
desktop_environments=(
    "KDE Plasma     :install_kde     :$GREEN"
    "GNOME          :install_gnome   :$GREEN"
    "XFCE           :install_xfce    :$GREEN"
    "Hyprland       :install_hyprland:$GREEN"
    "DWM            :install_dwm     :$GREEN"
    "Xmonad + Xmobar:install_xmonad  :$GREEN"
    "qtile          :install_qtile   :$GREEN"
    "None (CLI only):skip_install    :$YELLOW"
)
# Function to install the chosen desktop environment
desktop_environment() {
    source ~/ms1/linux/os_imports/wallpaper.sh
    source ~/ms1/linux/os_imports/sddm.sh
    display_submenu "Which desktop environment would you like to install?" "desktop_environments"
}

install_kde() {
    echo -e "${GREEN}Installing KDE Plasma...${NC}"
    sudo pacman -S --noconfirm --needed plasma kde-gtk-config dolphin konsole plasma-desktop sddm
    yay -S --needed sddm-theme-sugar-candy
    sudo systemctl enable sddm
    # Ask about theme
    read -p "Do you want to install and set up the Sugar Candy SDDM theme? (y/n): " THEME_CHOICE
    if [[ "$THEME_CHOICE" =~ ^[Yy]$ ]]; then
        sddm_theme
    else
        sddm_numlock
    fi
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
    sudo pacman -S --needed  xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
    sudo systemctl enable lightdm
    sudo pacman -Syu
}

install_hyprland() {
    echo -e "${YELLOW}Installing Hyprland...${NC}"
    #! for hyprland need to enable 3d accelaration in the virtual io
    # Install essential packages
    sudo pacman -S --needed foot kitty hyprland xdg-desktop-portal xdg-desktop-portal-hyprland wayland wayland-utils wlroots gtk3
    sudo pacman -S --needed waybar wofi xorg-xwayland hyprpaper hyprlock grim slurp wl-clipboard
    sudo pacman -S --needed qt5-wayland qt6-wayland rofi-wayland

    echo "📜 Setting environment variables..."
    PROFILE_FILE="$HOME/.bash_profile"
    grep -q XDG_SESSION_TYPE "$PROFILE_FILE" || cat >> "$PROFILE_FILE" <<'EOF'
# Hyprland env
export XDG_SESSION_TYPE=wayland
export XDG_CURRENT_DESKTOP=Hyprland
export QT_QPA_PLATFORM=wayland
export MOZ_ENABLE_WAYLAND=1
EOF
    echo "✅ Updated: $PROFILE_FILE"
    echo "🎉 Setup complete! Now run:"
    echo "➡️  source ~/.bash_profile"
    echo "➡️  Hyprland"

    sudo pacman -Syu
}

install_dwm() {
    echo -e "${YELLOW}Installing DWM.${NC}"
}

install_xmonad() {
    echo -e "${YELLOW}Installing Xmonad + Xmobar.${NC}"
    #! compton vs picom --for arch select picom [these are compositor for x11 --compton is for ubuntu]
    sudo pacman -S --needed xmonad xmonad-utils xmonad-contrib xmobar xterm dmenu nitrogen picom gnome-terminal
    mkdir -p $HOME/.xmonad
    cp ~/ms1/linux/config/xmonad/xmonad.hs ~/.xmonad/
    sddm_setup
    wallpaper
}

install_qtile() {
    echo -e "${YELLOW}Installing qtile.${NC}"
    sudo pacman -S --needed qtile python-pywlroots xorg-xwayland kitty dmenu picom network-manager-applet volumeicon mypy
    sudo pacman -S --needed rofi-wayland
    yay -S --needed qtile-extras
}

skip_install() {
    echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
}

#  ██████╗ ██████╗ ███╗   ███╗██████╗  ██████╗ ███████╗██╗████████╗ ██████╗ ██████╗
# ██╔════╝██╔═══██╗████╗ ████║██╔══██╗██╔═══██╗██╔════╝██║╚══██╔══╝██╔═══██╗██╔══██╗
# ██║     ██║   ██║██╔████╔██║██████╔╝██║   ██║███████╗██║   ██║   ██║   ██║██████╔╝
# ██║     ██║   ██║██║╚██╔╝██║██╔═══╝ ██║   ██║╚════██║██║   ██║   ██║   ██║██╔══██╗
# ╚██████╗╚██████╔╝██║ ╚═╝ ██║██║     ╚██████╔╝███████║██║   ██║   ╚██████╔╝██║  ██║
#  ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝      ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
compositor_func=(
    "Sway - A tiling Wayland compositor and drop-in replacement for i3.                       :sway_cont     :$GREEN"
    "Wayfire - A 3D Wayland compositor with Compiz-like effects.                              :wayfire_cont  :$GREEN"
    "Hyprland - A dynamic tiling Wayland compositor with modern features.                     :hyprland_cont :$GREEN"
    "Weston - The reference Wayland compositor, primarily for testing.                        :weston_cont   :$GREEN"
    "river - A dynamic tiling compositor inspired by dwm.                                     :river_cont    :$GREEN"
    "Xorg - The legacy display server, required for many traditional X11 applications.        :xorg_cont     :$GREEN"
    "Picom (Xorg/X11) - A compositor for X11, providing shadows, transparency, and animations.:picom_cont    :$GREEN"
    "Extra tools - Useful Wayland utilities (wlr-randr, grim, slurp).                         :extras_cont   :$GREEN"
)
compositor_setup() {
    display_submenu "Setup Setup Compositor?" "compositor_func"
}

sway_cont() {
    sudo pacman -S --needed sway waybar
}

wayfire_cont() {
    yay -S --needed wayfire wcm wf-shell
}

hyprland_cont() {
    yay -S --needed hyprland hyprpaper waybar-hyprland
}

weston_cont() {
    sudo pacman -S --needed weston
}

river_cont() {
    sudo pacman -S --needed river
}

xorg_cont() {
    sudo pacman -S --needed xorg-server xorg-xinit xorg-xwayland xorg-apps
}

picom_cont() {
    sudo pacman -S --needed picom
}

extras_cont() {
    sudo pacman -S --needed wlr-randr grim slurp
}

# ██████╗ ██╗███████╗██████╗ ██╗      █████╗ ██╗   ██╗    ███████╗███████╗██████╗ ██╗   ██╗███████╗██████╗     ██████╗ ██████╗  ██████╗ ████████╗ ██████╗  ██████╗ ██████╗ ██╗     ███████╗
# ██╔══██╗██║██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝    ██╔════╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔═══██╗██║     ██╔════╝
# ██║  ██║██║███████╗██████╔╝██║     ███████║ ╚████╔╝     ███████╗█████╗  ██████╔╝██║   ██║█████╗  ██████╔╝    ██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║██║     ██║   ██║██║     ███████╗
# ██║  ██║██║╚════██║██╔═══╝ ██║     ██╔══██║  ╚██╔╝      ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██╔══╝  ██╔══██╗    ██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║██║     ██║   ██║██║     ╚════██║
# ██████╔╝██║███████║██║     ███████╗██║  ██║   ██║       ███████║███████╗██║  ██║ ╚████╔╝ ███████╗██║  ██║    ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╗╚██████╔╝███████╗███████║
# ╚═════╝ ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝       ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚══════╝
xorg(){
    sudo pacman -S --needed xorg xorg-xinit xorg-xwayland
    sudo pacman -S --needed xorg-apps mesa xf86-video-intel xf86-video-amdgpu xf86-input-libinput #! optional but useful
}
wayland(){
    sudo pacman -S --needed wayland wayland-protocols wayland-utils xdg-desktop-portal xdg-desktop-portal-wlr wlroots libinput gtk3 qt5-wayland xorg-xwayland waybar wofi grim slurp wl-clipboard swaylock
}

# ██████╗  █████╗  ██████╗██╗  ██╗ █████╗  ██████╗ ███████╗███████╗
# ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔══██╗██╔════╝ ██╔════╝██╔════╝
# ██████╔╝███████║██║     █████╔╝ ███████║██║  ███╗█████╗  ███████╗
# ██╔═══╝ ██╔══██║██║     ██╔═██╗ ██╔══██║██║   ██║██╔══╝  ╚════██║
# ██║     ██║  ██║╚██████╗██║  ██╗██║  ██║╚██████╔╝███████╗███████║
# ╚═╝     ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝
package_install_items=(
    "Install Base Packages :install_base_packages :$GREEN"
    "Install Fonts         :install_fonts         :$GREEN"
    "Install Utilities     :install_utilities     :$GREEN"
    "Install Media Packages:install_media_packages:$GREEN"
)

install_base_packages() {
    echo -e "${GREEN}Installing Base Packages...${NC}"
    sudo pacman -S --needed bash bat chafa curl eza fastfetch fzf \
                            lsd lua-language-server neovim openssh \
                            python rclone sshpass wget which zoxide yazi zsh \
                            stow expac numlockx rsync thefuck feh screenfetch \
                            sed grep jq rofi conky htop firefox dunst mypy \
                            pcmanfm thunar thunar-archive-plugin thunar-volman \
                            foot starship
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

# Function to install necessary packages using yay
install_packages() {
    clear
    echo -e "${GREEN}Updating package database...${NC}"
    sudo pacman -Sy --noconfirm
    display_submenu "Install Packages Submenu" "package_install_items"
}

# ███╗   ██╗██╗   ██╗███╗   ███╗██╗  ██╗███████╗██╗   ██╗    ███████╗███████╗████████╗██╗   ██╗██████╗
# ████╗  ██║██║   ██║████╗ ████║██║ ██╔╝██╔════╝╚██╗ ██╔╝    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
# ██╔██╗ ██║██║   ██║██╔████╔██║█████╔╝ █████╗   ╚████╔╝     ███████╗█████╗     ██║   ██║   ██║██████╔╝
# ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔═██╗ ██╔══╝    ╚██╔╝      ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝
# ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██║  ██╗███████╗   ██║       ███████║███████╗   ██║   ╚██████╔╝██║
# ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝       ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝
tty_setup=(
    "Auto Login            :enable_tty_autologin  :$GREEN"
    "Numlock Enable        :enable_numlock_on_tty :$GREEN"
    "Disable Terminal Bell :disable_bell          :$GREEN"
    "TTY Font              :tty_font              :$GREEN"
)
# Function to install the chosen desktop environment
tty_numlock_setup() {
    source ~/ms1/linux/os_imports/wallpaper.sh
    source ~/ms1/linux/os_imports/sddm.sh
    display_submenu "Setup TTy & NumLock?" "tty_setup"
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

    echo "Reloading systemd and restarting getty@tty1..."
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl restart getty@tty1

    echo "✅ Auto-login setup complete for user: $user on tty1."
}

enable_numlock_on_tty() {
    if ! command -v numlockx &> /dev/null; then
        echo "Installing numlockx package..."
        sudo pacman -S --noconfirm numlockx
    fi

    echo "Creating numlock script..."
    sudo tee /usr/local/bin/numlock > /dev/null <<EOF
#!/bin/bash
for tty in /dev/tty{1..6}
do
    /usr/bin/setleds -D +num < "$tty"
done
EOF
    sudo chmod +x /usr/local/bin/numlock

    echo "Creating systemd service..."
    sudo tee /etc/systemd/system/numlock.service > /dev/null <<EOF
[Unit]
Description=Enable NumLock on TTYs
[Service]
ExecStart=/usr/local/bin/numlock
StandardInput=tty
RemainAfterExit=yes
[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable numlock.service
    sudo systemctl start numlock.service

    echo "Creating getty service drop-in configuration..."
    sudo mkdir -p /etc/systemd/system/getty@.service.d
    sudo tee /etc/systemd/system/getty@.service.d/activate-numlock.conf > /dev/null <<EOF
[Service]
ExecStartPre=/bin/sh -c 'setleds -D +num < /dev/%I'
EOF

    sudo systemctl daemon-reload
    sudo systemctl restart systemd-logind.service

    echo "NumLock has been enabled on TTYs. The systemd service is now active."
}

disable_bell() {
    echo "Disabling terminal bell..."

    echo 'set bell-style none' >> ~/.inputrc
    bind -f ~/.inputrc

    if [ "$(id -u)" -eq 0 ]; then
        echo 'set bell-style none' >> /etc/inputrc
    else
        echo "To disable system-wide bell, run:"
        echo "  echo 'set bell-style none' | sudo tee -a /etc/inputrc"
    fi

    echo "blacklist pcspkr" | sudo tee /etc/modprobe.d/nobeep.conf > /dev/null
    sudo rmmod pcspkr 2>/dev/null

    echo "Bell disabled. Reboot or re-login for full effect."
}

# Function to list and preview TTY fonts
tty_font() {
    FONT_DIR="/usr/share/kbd/consolefonts"
    echo "Available TTY Fonts:"

    # Check if the font directory exists
    if [ ! -d "$FONT_DIR" ]; then
        echo "Console font directory not found."
        return 1
    fi

    # Use fzf for interactive font selection
    selected_font=$(find "$FONT_DIR" -type f -name '*.psf*' | fzf --preview 'setfont {} && echo -e "\033[1;32mPreview: {}\033[0m"' --preview-window=up:5)

    # If a font is selected, set it as the current font
    if [ -n "$selected_font" ]; then
        sudo setfont "$selected_font"
        echo "Font changed to: $(basename "$selected_font")"
    else
        echo "No font selected."
    fi
}

#*  ██████╗ ██████╗ ███╗   ██╗████████╗ █████╗ ██╗███╗   ██╗███████╗██████╗
#* ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██║████╗  ██║██╔════╝██╔══██╗
#* ██║     ██║   ██║██╔██╗ ██║   ██║   ███████║██║██╔██╗ ██║█████╗  ██████╔╝
#* ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██║██║██║╚██╗██║██╔══╝  ██╔══██╗
#* ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║██║██║ ╚████║███████╗██║  ██║
#*  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
container_function=(
    "Steam   :steam_cont    :$GREEN"
    "Lutris  :lutris_cont   :$GREEN"
    "Bottles :bottles_cont  :$GREEN"
)
# Function to install the chosen desktop environment
Container_setup() {
    display_submenu "Setup Container?" "container_function"
}

steam_cont() {
    sudo pacman -S --needed steam
}
lutris_cont() {
    sudo pacman -S --needed lutris
}
bottles_cont() {
    yay -S --needed bottles 
}

# ██████╗  ██████╗██╗      ██████╗ ███╗   ██╗███████╗
# ██╔══██╗██╔════╝██║     ██╔═══██╗████╗  ██║██╔════╝
# ██████╔╝██║     ██║     ██║   ██║██╔██╗ ██║█████╗
# ██╔══██╗██║     ██║     ██║   ██║██║╚██╗██║██╔══╝
# ██║  ██║╚██████╗███████╗╚██████╔╝██║ ╚████║███████╗
# ╚═╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
rclone_decrypt() {
    # remove te ntfy file
    clear
    echo "Decreypt rclone conf ...."
    sudo pacman -S --needed python-pycryptodomex
    python ~/ms1/termux/locker/locker.py --decrypt ~/ms1/asset/rclone/rclone.conf.enc

    echo -e "Copying rclone.conf"
    mkdir -p "$HOME/.config/rclone"
    cp "$HOME/ms1/asset/rclone/rclone.conf" "$HOME/.config/rclone"
}

rclone_copy_linuxbin() {
    # remove te ntfy file
    clear
    
    echo "Copy Linux binary files ...."
    rclone sync o0:/msBackups/linux_binary/ $HOME/linux_binary/ -P --check-first --transfers=10 --track-renames --fast-list
    
    curl -L -o "$HOME/linux_binary/wallpaper/wallpaper1.jpg" "https://www.skyweaver.net/images/media/wallpapers/wallpaper1.jpg"
    echo 'Downloading WallPaper Complete'
}

# Function to create an rclone folder and copy rclone.conf file
rclone_setup() {
    clear
    RCLONE_CONFIG_DIR="$HOME/.config/rclone"
    SOURCE_CONF_FILE="$HOME/storage/shared/rclone.conf"
    # Create the rclone folder if it doesn't exist
    echo -e "Creating rclone configuration directory at $RCLONE_CONFIG_DIR..."
    mkdir -p "$RCLONE_CONFIG_DIR" || {
        echo -e "Failed to create rclone directory. Please check permissions."
        return 1
    }
    echo -e "Directory created or already exists: $RCLONE_CONFIG_DIR"
    # Copy rclone.conf to the new directory
    echo -e "Copying rclone.conf from $SOURCE_CONF_FILE to $RCLONE_CONFIG_DIR..."
    if [ -f "$SOURCE_CONF_FILE" ]; then
        cp "$SOURCE_CONF_FILE" "$RCLONE_CONFIG_DIR/" || {
            echo -e "Failed to copy rclone.conf. Please check permissions or the file path."
            return 1
        }
        echo -e "rclone.conf copied successfully to $RCLONE_CONFIG_DIR"
    else
        echo -e "Source file $SOURCE_CONF_FILE does not exist. Please ensure the file exists."
        return 1
    fi
}

# Function to restore songs from the web using rclone
Restore_Songs() {
    clear
    DEST_DIR="$HOME/storage/shared/song"
    REMOTE="gu:/song"
    # Sync the songs from the remote to the destination directory
    echo -e "Starting rclone sync from $REMOTE to $DEST_DIR..."
    rclone sync "$REMOTE" "$DEST_DIR" -P --check-first --transfers=1 --track-renames --fast-list || {
        echo -e "Failed to sync songs from $REMOTE to $DEST_DIR. Please check your rclone configuration."
        return 1
    }
    echo -e "Songs restored successfully from $REMOTE to $DEST_DIR"
}

#  █████╗ ██╗   ██╗██████╗     ███████╗███████╗████████╗██╗   ██╗██████╗
# ██╔══██╗██║   ██║██╔══██╗    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
# ███████║██║   ██║██████╔╝    ███████╗█████╗     ██║   ██║   ██║██████╔╝
# ██╔══██║██║   ██║██╔══██╗    ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝
# ██║  ██║╚██████╔╝██║  ██║    ███████║███████╗   ██║   ╚██████╔╝██║
# ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝    ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝
setup_yay() {
    clear
    echo -e "${CYAN}Installing yay (AUR helper)...${NC}"
    # Install prerequisites
    sudo pacman -Sy --needed --noconfirm base-devel git
    # Clone yay repository
    if [ ! -d "/tmp/yay" ]; then
        git clone https://aur.archlinux.org/yay.git /tmp/yay
    fi
    # Build and install yay
    cd /tmp/yay || exit
    makepkg -si --noconfirm
    echo -e "${GREEN}yay has been installed successfully.${NC}"
}

#  █████╗ ██████╗ ██████╗ ██╗     ██╗ ██████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗    ███████╗███████╗████████╗██╗   ██╗██████╗
# ██╔══██╗██╔══██╗██╔══██╗██║     ██║██╔════╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║    ██╔════╝██╔════╝╚══██╔══╝██║   ██║██╔══██╗
# ███████║██████╔╝██████╔╝██║     ██║██║     ███████║   ██║   ██║██║   ██║██╔██╗ ██║    ███████╗█████╗     ██║   ██║   ██║██████╔╝
# ██╔══██║██╔═══╝ ██╔═══╝ ██║     ██║██║     ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║    ╚════██║██╔══╝     ██║   ██║   ██║██╔═══╝
# ██║  ██║██║     ██║     ███████╗██║╚██████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║    ███████║███████╗   ██║   ╚██████╔╝██║
# ╚═╝  ╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝ ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝╚══════╝   ╚═╝    ╚═════╝ ╚═╝
# Neovim setup function
nvim_setup() {
    clear
    echo -e "${BLUE}Setting up Neovim configuration...${NC}"
    # Create the Neovim config directory if it doesn't exist
    mkdir -p "$NVIM_CONFIG_DEST"
    # Copy the init.lua file to the Neovim config directory
    cp "$NVIM_INIT_SOURCE" "$NVIM_CONFIG_DEST/init.lua"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Neovim configuration setup successfully.${NC}"
    else
        echo -e "${RED}Failed to set up Neovim configuration.${NC}"
    fi
    curl -o /data/data/com.termux/files/usr/bin/install-in-mason  https://raw.githubusercontent.com/Amirulmuuminin/setup-mason-for-termux/main/install-in-mason
    chmod +x /data/data/com.termux/files/usr/bin/install-in-mason
    install-in-mason lua-language-server
}

# ████████╗ ██████╗  ██████╗ ██╗     ███████╗
# ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
#    ██║   ██║   ██║██║   ██║██║     ███████╗
#    ██║   ██║   ██║██║   ██║██║     ╚════██║
#    ██║   ╚██████╔╝╚██████╔╝███████╗███████║
#    ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
list_recent_packages() {
    echo -e "${GREEN}Listing recently installed packages...${NC}"
    expac --timefmt='%Y-%m-%d %H:%M:%S' '%l\t%n' | sort -r
}

quick_file_search() {
    clear
    local file_name=$1
    local search_dir=${2:-$PWD}
    if [ -z "$file_name" ]; then
        echo "Usage: quick_file_search <file_name> [directory]"
        return 1
    fi
    echo "Searching for $file_name in $search_dir..."
    find "$search_dir" -type f -name "$file_name"
}

network_speed_test() {
    clear
    echo "Testing network speed..."
    if command -v speedtest &> /dev/null; then
        speedtest
    else
        echo "speedtest-cli not installed. Installing now..."
        sudo apt install -y speedtest-cli
        speedtest
    fi
}

list_large_files() {
    clear
    local target_dir=${1:-$PWD}
    echo "Finding large files in $target_dir..."
    find "$target_dir" -type f -exec du -h {} + | sort -rh | head -n 10
}

# ██╗███╗   ██╗███████╗ ██████╗
# ██║████╗  ██║██╔════╝██╔═══██╗
# ██║██╔██╗ ██║█████╗  ██║   ██║
# ██║██║╚██╗██║██╔══╝  ██║   ██║
# ██║██║ ╚████║██║     ╚██████╔╝
# ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝
about_device() {
    clear
    fastfetch
}

check_gpu_drivers() {
    echo -e "${GREEN}Detecting GPU and checking AMD drivers...${NC}"
    
    GPU_INFO=$(lspci | grep -E "VGA|3D")
    echo -e "${YELLOW}Detected GPU: ${GPU_INFO}${NC}"
    
    if echo "$GPU_INFO" | grep -qi "AMD"; then
        echo -e "${YELLOW}AMD GPU detected.${NC}"
        
        missing_pkgs=()

        for pkg in mesa mesa-vulkan-drivers vulkan-radeon lib32-vulkan-radeon lib32-mesa; do
            if ! pacman -Q "$pkg" &>/dev/null; then
                echo -e "${RED}$pkg is missing.${NC}"
                missing_pkgs+=("$pkg")
            else
                echo -e "${GREEN}$pkg is installed.${NC}"
            fi
        done

        if [ ${#missing_pkgs[@]} -ne 0 ]; then
            echo -e "${YELLOW}Some AMD GPU drivers are missing. Install them now? (y/n)${NC}"
            read -rp "> " answer
            if [[ "$answer" =~ ^[Yy]$ ]]; then
                yay -S --noconfirm "${missing_pkgs[@]}"
            else
                echo -e "${RED}Skipping driver installation.${NC}"
            fi
        else
            echo -e "${GREEN}All required AMD GPU drivers are installed.${NC}"
        fi
    else
        echo -e "${YELLOW}Non-AMD GPU detected. Skipping AMD driver check.${NC}"
    fi
}

#!  ██████╗ ██╗████████╗
#! ██╔════╝ ██║╚══██╔══╝
#! ██║  ███╗██║   ██║
#! ██║   ██║██║   ██║
#! ╚██████╔╝██║   ██║
#!  ╚═════╝ ╚═╝   ╚═╝
update_ms1_repo() {
    clear
    local ms1_folder="$HOME/ms1"
    if [ -d "$ms1_folder" ]; then
        echo "Changing directory to $ms1_folder..."
        cd "$ms1_folder" || {
            echo "Failed to change directory to $ms1_folder."
            return 1
        }
        echo "Pulling latest changes from the repository..."
        git pull || {
            echo "Failed to pull changes. Please check your repository setup."
            return 1
        }
        echo "Repository updated successfully."
    else
        echo "The folder $ms1_folder does not exist."
        return 1
    fi
}

# ██████╗ ███████╗███████╗███████╗██████╗ ███████╗███╗   ██╗ ██████╗███████╗
# ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔════╝████╗  ██║██╔════╝██╔════╝
# ██████╔╝█████╗  █████╗  █████╗  ██████╔╝█████╗  ██╔██╗ ██║██║     █████╗
# ██╔══██╗██╔══╝  ██╔══╝  ██╔══╝  ██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══╝
# ██║  ██║███████╗██║     ███████╗██║  ██║███████╗██║ ╚████║╚██████╗███████╗
# ╚═╝  ╚═╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
# Function to handle exit
Close_script() {
    clear
    echo -e "${GREEN}Exiting the script. Goodbye!${NC}"
    exit 0
}

exit_script() {
    # Stop the Termux service
    am startservice -a com.termux.service_stop com.termux/.app.TermuxService
    # Exit the current shell session
    exit
}

#  ██████╗ ██████╗ ███████╗ ██████╗ ██╗     ███████╗████████╗███████╗
# ██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██║     ██╔════╝╚══██╔══╝██╔════╝
# ██║   ██║██████╔╝███████╗██║   ██║██║     █████╗     ██║   █████╗
# ██║   ██║██╔══██╗╚════██║██║   ██║██║     ██╔══╝     ██║   ██╔══╝
# ╚██████╔╝██████╔╝███████║╚██████╔╝███████╗███████╗   ██║   ███████╗
#  ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝╚══════╝   ╚═╝   ╚══════╝

ntfy_remove() {
    # remove te ntfy file
    clear
    echo "Deleting g00:ntfy file ...."
    rclone delete g00:ntfy
}

# for termux
welcome_remove() {
    # remove te ntfy file
    clear
    echo "Removing Welcome Page ...."
    touch .hushlogin
}

# hyperland_config() {
#     # Auto-generate default config if missing
#     CONFIG_DIR="$HOME/.config/hypr"
#     CONFIG_FILE="$CONFIG_DIR/hyprland.conf"
#     # Launch Hyprland once in a nested session to generate config (safe in VMs or TTYs)
#     if [ ! -f "$CONFIG_FILE" ]; then
#         echo "Generating Hyprland config using hyprland..."
#         mkdir -p "$CONFIG_DIR"
#         Hyprland
#         sleep 2
#         pkill Hyprland
#     fi
#     # Replace kitty with foot if config exists
#     if [ -f "$CONFIG_FILE" ]; then
#         echo "Replacing 'kitty' with 'foot' in config..."
#         sed -i 's/kitty/foot/g' "$CONFIG_FILE"
#     else
#         echo "❌ Could not find hyprland.conf to patch."
#     fi
# }

nvim_config() {
    # Auto-generate default config if missing
ln -sf "$HOME/ms1/linux/config/nvim/" "$HOME/.config/nvim"
}

enable_early_numlock() {
  echo -e "${CYAN}📦 Installing mkinitcpio-numlock from AUR...${NC}"
  yay -S --noconfirm --needed mkinitcpio-numlock

  echo -e "${CYAN}🛠️ Adding 'numlock' hook to /etc/mkinitcpio.conf...${NC}"
  if grep -q "HOOKS=.*numlock" /etc/mkinitcpio.conf; then
    echo -e "${YELLOW}⚠️ 'numlock' hook already present in HOOKS. Skipping modification.${NC}"
  else
    # Use sed to insert numlock before encrypt or block
    sudo sed -i -E 's/(HOOKS=.*)(encrypt|block)/\1numlock \2/' /etc/mkinitcpio.conf
    echo -e "${GREEN}✅ 'numlock' hook added before encrypt/block.${NC}"
  fi

  echo -e "${CYAN}🔄 Regenerating initramfs...${NC}"
  sudo mkinitcpio -P

  echo -e "${GREEN}✅ Early NumLock enabled via initramfs hook.${NC}"
}

rofi_install_wayland() {
  echo -e "${CYAN}📦 Installing Rofi wayland version not x11...${NC}"
    # yay -S --needed rofi-lbonn-wayland
    sudo pacman -S --needed rofi-wayland
  echo -e "${GREEN}✅ Rofi Installed.${NC}"
  echo -e "${GREEN}✅ run Rofi -show drun to launch.${NC}"
}

dwm_wm() {
    yay -S --needed dwm st dmenu xorg-xsetroot sddm
    sudo systemctl enable sddm

    echo -e "📝 Setting up DWM with SDDM and custom wallpaper..."

    # Step 1: Install feh if not already installed
    if ! command -v feh &>/dev/null; then
        echo -e "📦 Installing 'feh'..."
        sudo pacman -S --noconfirm feh
    fi

    # Step 2: Download wallpaper
    WALLPAPER_DIR="$HOME/Pictures/wallpapers"
    mkdir -p "$WALLPAPER_DIR"
    WALLPAPER_PATH="$WALLPAPER_DIR/wallpaper1.jpg"
    echo -e "🌐 Downloading wallpaper..."
    curl -L -o "$WALLPAPER_PATH" "https://www.skyweaver.net/images/media/wallpapers/wallpaper1.jpg"

    # Step 3: Set wallpaper in .xprofile
    echo -e "🌄 Setting wallpaper using feh..."
    grep -qxF "feh --bg-scale \"$WALLPAPER_PATH\"" ~/.xprofile || echo "feh --bg-scale \"$WALLPAPER_PATH\"" >> ~/.xprofile

    # Step 4: Create or update DWM .desktop entry for SDDM
    echo -e "📝 Writing /usr/share/xsessions/dwm.desktop..."
    sudo bash -c "cat > /usr/share/xsessions/dwm.desktop <<EOF
[Desktop Entry]
Encoding=UTF-8
Name=DWM
Comment=Dynamic Window Manager
Exec=dwm
Icon=dwm
Type=XSession
EOF"

#! there is no config file to edit so have to download config edit and then rebuild
# git clone https://git.suckless.org/dwm ~/suckless/dwm
# git clone https://git.suckless.org/st ~/suckless/st

    echo -e "✅ Setup complete! Select 'DWM' in SDDM and reboot to apply the wallpaper."
}

dwm_config() {
    echo Configure DWM
# > "$HOME/.xinitrc"  #! Clears the file
rsync -a --delete "$HOME/ms1/config/dwm/dwm/.xinitrc" "$HOME/.xinitrc"
rsync -a --delete "$HOME/ms1/config/dwm/dwm/.xprofile" "$HOME/.xprofile"
# rsync -a --delete "$HOME/ms1/archlinux/dwm/autostart.sh" "$HOME/autostart.sh"

    # Step 5: Ensure .xprofile is sourced (for some setups)
    if ! grep -q 'source ~/.xprofile' ~/.xinitrc; then
        echo "source ~/.xprofile" >> ~/.xinitrc
    fi
}

dwm_statusbar() {
    cd ~/
    echo Configure DWM Statusbar
    yay -S --needed git base-devel lemonbar libinih
    git clone https://github.com/domsson/succade.git
    # Change into the succade directory
    cd succade || { echo "Failed to enter succade directory"; return 1; }
    # Make the build script executable
    chmod +x ./build
    # Run the build script
    ./build
    # Create the config directory
    mkdir -p ~/.config/succade
    # Copy the example config to the proper location
    cp ./cfg/example1.ini ~/.config/succade/succaderc
    # Make succade executable
    chmod +x ./bin/succade
    # Move succade to a directory in your PATH (e.g., ~/.local/bin/)
    cp ./bin/succade ~/.local/bin/
    # Confirm installation success
    echo "Succade has been successfully installed!"
} #! failed ?


dwmblocks_torrinfail(){
    git clone https://github.com/torrinfail/dwmblocks.git #! has a issue in the dwmblocks.c which i fixed in my ms1/archlinux/dwblocks
    #! so dont use this one
}

distrotube_dwm(){
    cd ~/
    mkdir -p opt
    cd opt
    # yay -S --needed dwm-distrotube-git dwmblocks-distrotube-git st-distrotube-git dmenu-distrotube-git #! cant find them in yay even though he said its in the yay aur
    git clone https://gitlab.com/dwt1/st-distrotube.git
    git clone https://gitlab.com/dwt1/dwm-distrotube.git
    git clone https://gitlab.com/dwt1/dwmblocks-distrotube.git
    git clone https://gitlab.com/dwt1/dmenu-distrotube.git
}

distrotube_dwm_config(){
    cd ~/ms1/linux/config/dwm/dwmblocks_dt_fixed/
    make
    sudo make clean install
    chmod +x scripts/*
}



while true; do
    echo ""
    echo -e "${YELLOW}Select an option:${NC}"
    # Show menu items with numbers
    for i in "${!menu_items[@]}"; do
        IFS=":" read -r description function color <<< "${menu_items[$i]}"
        echo -e "${color}$((i+1))) $description${NC}"
    done
    # Show hotkey items
    echo -e "$RED c) Close"
    echo -e " e) Exit"
    echo -e " x) Test${NC}"
    echo ""
    read -p "Enter choice: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#menu_items[@]} )); then
        IFS=":" read -r _ function _ <<< "${menu_items[$((choice-1))]}"
        function=$(echo "$function" | xargs)
        for cmd in $function; do
            $cmd
        done
    elif [[ -n "${hotkeys[$choice]}" ]]; then
        ${hotkeys[$choice]}
    else
        echo -e "${RED}Invalid option. Please try again.${NC}"
    fi
    source "$HOME/ms1/linux/os.sh"
done

