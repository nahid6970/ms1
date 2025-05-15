#!/bin/bash

#! import list
for file in ~/ms1/linux/import/*.sh; do [[ -r "$file" ]] && source "$file" || echo "Error sourcing $file" >&2; done


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
    "Git Pull [ms1]                   : update_ms1_repo       :$GREEN"
    "Initial Setup (sddm + wallpaper) : sddm_setup wallpaper  :$GREEN"
    "Copy bashrc                      : copy_files            :$GREEN"
    "Install Necessary Packages       : install_packages      :$GREEN"
    "Desktop Environment 󰹯            : desktop_environment   :$GREEN" #! C:\ms1\linux\desktop_environment.sh
    "Compositor + Utilities 󰹯         : compositor_setup      :$GREEN" #! C:\ms1\linux\import\compositors.sh
    "Status Bar 󰹯                     : install_bar           :$GREEN"
    # "X-Org/X11                        : xorg                  :$GREEN"
    # "Wayland                          : wayland               :$GREEN"
    "Config All Necessary PKG         : All_Configs           :$GREEN"
    "YAY Setup                        : setup_yay             :$GREEN"
    "TTY Setup 󰹯                      : tty_setup             :$GREEN"
    "Store Setup 󰹯                    : store_setup           :$GREEN"
    "Container 󰹯                      : container_setup       :$GREEN"
    "About                            : about_device          :$GREEN"
    "Rclone-Decrypt                   : rclone_decrypt        :$RED"
    "Rclone-linux_binary              : rclone_copy_linuxbin  :$RED"
    "GPU Drivers                      : check_gpu_drivers     :$GREEN"
    "Hyprland                         : setup_hyprland_full   :$GREEN"
    "Hyprland Config                  : hyperland_config      :$GREEN"
    "Rofi for Hyprland                : rofi_install_wayland  :$GREEN"
    "Neovim Config                    : nvim_config           :$GREEN"
    "Enable Numlock                   : enable_early_numlock  :$GREEN"
    "DWM Setup                        : dwm_wm                :$GREEN"
    "DWM Config                       : dwm_config            :$GREEN"
    "DWM ST                           : dwm_statusbar         :$GREEN"
    "DWM Distrotube                   : distrotube_dwm_config :$GREEN"
    "SDDM                             : sddm_setup            :$GREEN"
    "Arch Install                     : arch_install          :$GREEN"
    # "bottles                        : not_yet_choosen       :$GREEN"
    # "wine                           : not_yet_choosen       :$GREEN"
    # "Lutris                         : not_yet_choosen       :$GREEN"
    # "steam                          : not_yet_choosen       :$GREEN"
    # "Heroic Games Launcher          : check_gpu_drivers     :$GREEN"
)

# Special hotkey items
declare -A hotkeys=(
    [c]="Close_script"
    [e]="exit_script"
    [x]="test_test"
)

arch_install(){
    archinstall --config $HOME/ms1/linux/arch_setup_config/user_configuration.json --creds $HOME/ms1/linux/arch_setup_config/user_credentials.json
}


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
cp -a "$HOME/ms1/linux/config/.config/starship/starship.toml" "$HOME/.config" #! C:\ms1\linux\config\.config\starship\starship.toml

# source $HOME/autostart.sh
}


xorg(){
    sudo pacman -S --needed xorg xorg-xinit xorg-xwayland
    sudo pacman -S --needed xorg-apps mesa xf86-video-intel xf86-video-amdgpu xf86-input-libinput #! optional but useful
}

wayland(){
    sudo pacman -S --needed wayland wayland-protocols wayland-utils xdg-desktop-portal xdg-desktop-portal-wlr wlroots libinput gtk3 qt5-wayland xorg-xwayland waybar wofi grim slurp wl-clipboard swaylock
}

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
}

list_recent_packages() {
    echo -e "${GREEN}Listing recently installed packages...${NC}"
    expac --timefmt='%Y-%m-%d %H:%M:%S' '%l\t%n' | sort -r
}

# Copy .bashrc and termux.properties
copy_files() {
    clear
    echo -e "${CYAN}Copying .bashrc...${NC}"
    cp $HOME/ms1/linux/config/bashrc $HOME/.bashrc

    echo -e "${GREEN}.bashrc copied.${NC}"
    echo -e "${RED}Please run 'source ~/.bashrc' to apply changes to your current shell.${NC}"
}

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



about_device() {
    clear
    fastfetch
}



ntfy_remove() {
    # remove te ntfy file
    clear
    echo "Deleting g00:ntfy file ...."
    rclone delete g00:ntfy
}

welcome_remove() {
    # remove te ntfy file
    clear
    echo "Removing Welcome Page ...."
    touch .hushlogin
}


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

desktop_environment() {
    clear
    echo -e "${CYAN}Setting up Desktop Environment...${NC}"

    DE_SETUP_SCRIPT="$HOME/ms1/linux/desktop_environment.sh"

    if [ -f "$DE_SETUP_SCRIPT" ]; then
        bash "$DE_SETUP_SCRIPT"
    else
        echo -e "${RED}Error: $DE_SETUP_SCRIPT not found.${NC}"
    fi
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

