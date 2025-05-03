#!/bin/bash

# Define some color variables
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Define some variables
# storage="$HOME/storage/shared"

REPO_DIR="$HOME/ms1"
BASHRC_SOURCE="$REPO_DIR/archlinux/config/bashrc"
BASHRC_DEST="$HOME/.bashrc"
NVIM_INIT_SOURCE="$REPO_DIR/dotfiles/neovim/init.lua"
NVIM_CONFIG_DEST="$HOME/.config/nvim"


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
        which zoxide yazi zsh stow expac
}

list_recent_packages() {
    echo -e "${GREEN}Listing recently installed packages...${NC}"
    expac --timefmt='%Y-%m-%d %H:%M:%S' '%l\t%n' | sort -r
}


# Function to install JetBrainsMono Nerd Font using oh-my-posh on Arch Linux
install_jetbrains_mono_font() {
    clear
    echo -e "\e[34mInstalling JetBrainsMono Nerd Font with oh-my-posh...\e[0m"

    FONT_DIR="$HOME/.local/share/fonts/jetbrainsmono-nfp/"
    FONT_PATTERN="JetBrainsMonoNerdFont*-Regular.ttf"

    # Check if the font is already present
    if find "$FONT_DIR" -type f -iname "$FONT_PATTERN" | grep -q .; then
        echo -e "\e[32mJetBrainsMono Nerd Font already exists. Skipping installation.\e[0m"
    else
        # Check and install oh-my-posh if missing
        if ! command -v oh-my-posh &> /dev/null; then
            echo -e "\e[33moh-my-posh not found. Installing with yay...\e[0m"
            if ! command -v yay &> /dev/null; then
                echo -e "\e[31myay not found. Please install yay first.\e[0m"
                return 1
            fi
            yay -Sy --noconfirm oh-my-posh || {
                echo -e "\e[31mFailed to install oh-my-posh.\e[0m"
                return 1
            }
        fi

        echo -e "\e[34mInstalling JetBrainsMono Nerd Font...\e[0m"
        oh-my-posh font install JetBrainsMono
    fi

    # Apply permissions to fonts
    if [ -d "$FONT_DIR" ]; then
        echo -e "\e[34mSetting font file permissions...\e[0m"
        find "$FONT_DIR" -type d -exec chmod 555 {} \;
        find "$FONT_DIR" -type f -iname "*.ttf" -exec chmod 444 {} \;
    fi

    # Refresh font cache
    if command -v fc-cache &> /dev/null; then
        echo -e "\e[34mUpdating font cache...\e[0m"
        fc-cache -fv
    else
        echo -e "\e[33mfc-cache not found. Install 'fontconfig' to enable font cache rebuilding.\e[0m"
    fi

    echo -e "\e[32mDone. You may need to set the font manually in your terminal emulator.\e[0m"
}






# Copy .bashrc and termux.properties
copy_files() {
    clear
    echo -e "${CYAN}Copying .bashrc...${NC}"
    cp "$BASHRC_SOURCE" "$BASHRC_DEST"

    echo -e "${GREEN}.bashrc copied.${NC}"
    echo -e "${RED}Please run 'source ~/.bashrc' to apply changes to your current shell.${NC}"
}



# Function to remove the repository
remove_repo() {
    clear
    echo -e "${RED}Removing the repository folder ($REPO_DIR)...${NC}"
    rm -rf "$REPO_DIR"
    echo -e "${RED}Repository folder removed successfully.${NC}"
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

# Git push repository function
git_push_repo() {
    clear
    echo -e "${BLUE}Pushing the repository to the remote...${NC}"
    cd "$REPO_DIR"
    git add .
    echo -e "${CYAN}Enter commit message:${NC}"
    read commit_message
    git commit -m "$commit_message"
    git push
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Repository pushed successfully.${NC}"
    else
        echo -e "${RED}Failed to push the repository. Please check your Git configuration.${NC}"
    fi
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

rclone_decrypt() {
    # remove te ntfy file
    clear
    echo "Clone ms1 ...."
    git clone https://github.com/nahid6970/ms1.git
    echo "Decreypt rclone conf ...."
    pip install pycryptodomex
    python ~/ms3/locker/locker.py --decrypt ~/ms1/asset/rclone/rclone.conf.enc

    SOURCE_CONF_FILE="$HOME/ms1/asset/rclone/rclone.conf"
    RCLONE_CONFIG_DIR="$HOME/.config/rclone"

    echo -e "Copying rclone.conf"
    cp "$SOURCE_CONF_FILE" "$RCLONE_CONFIG_DIR/"
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

    DE_SETUP_SCRIPT="$HOME/ms1/archlinux/config/DE_setup.sh"

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

setup_hyprland_full() {
    #! for hyprland need to enable 3d accelaration in the virtual io
  echo "📦 Installing packages..."
  sudo pacman -S --needed --noconfirm \
    hyprland kitty waybar wofi \
    xorg-xwayland xdg-desktop-portal-hyprland \
    wlroots qt5-wayland qt6-wayland \
    hyprpaper hyprlock grim slurp wl-clipboard

  echo "🛠️ Setting up config directory..."
  mkdir -p ~/.config/hypr

  echo "📄 Writing minimal hyprland.conf..."
  cat > ~/.config/hypr/hyprland.conf <<EOF
# Hyprland Minimal Config

# Autostart apps
exec-once = kitty
exec-once = waybar

# Keybindings
bind = SUPER, RETURN, exec, kitty
bind = SUPER, Q, killactive,
bind = SUPER, M, exit,

# Display
monitor = ,preferred,auto,1

# Input
input {
  kb_layout = us
}

# Aesthetics
general {
  gaps_in = 5
  gaps_out = 20
  border_size = 2
  col.active_border = rgba(33ccffee)
  col.inactive_border = rgba(595959aa)
}

decoration {
  rounding = 10
  blur = yes
  blur_size = 5
  blur_passes = 2
}

animations {
  enabled = yes
  animation = windows, 1, 7, default
}

# Wallpaper (optional, comment out if not needed)
# exec-once = hyprpaper & sleep 0.5 && hyprctl hyprpaper wallpaper "eDP-1,/path/to/wallpaper.jpg"
EOF

  echo "✅ Created: ~/.config/hypr/hyprland.conf"

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
}

sddm_theme() {
  echo "📦 Installing Sugar Candy theme..."
  if ! pacman -Q sddm-theme-sugar-candy &>/dev/null; then
    yay -S --noconfirm sddm-theme-sugar-candy
  else
    echo "✅ sddm-theme-sugar-candy is already installed."
  fi

  echo "📝 Configuring /etc/sddm.conf..."
  sudo bash -c 'cat > /etc/sddm.conf <<EOF
[Theme]
Current=Sugar-Candy

[General]
Numlock=on
EOF'

  echo "✅ SDDM theme set to Sugar-Candy and NumLock enabled."
}



disable_bell() {
    echo "Disabling terminal bell..."

    # Set bell-style to none for current user
    echo 'set bell-style none' >> ~/.inputrc
    bind -f ~/.inputrc

    # Set bell-style system-wide (optional, needs sudo)
    if [ "$(id -u)" -eq 0 ]; then
        echo 'set bell-style none' >> /etc/inputrc
    else
        echo "To disable system-wide bell, run:"
        echo "  echo 'set bell-style none' | sudo tee -a /etc/inputrc"
    fi

    # Blacklist pcspkr module to disable beep in TTY (needs sudo)
    echo "blacklist pcspkr" | sudo tee /etc/modprobe.d/nobeep.conf > /dev/null
    sudo rmmod pcspkr 2>/dev/null

    echo "Bell disabled. Reboot or re-login for full effect."
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
ln -sf "$HOME/ms1/archlinux/Hyprland/typecraft/nvim/" "$HOME/.config/nvim"
}

hyperland_config() {
    # Create destination directory if it doesn't exist
    mkdir -p "$HOME/.config/hypr"
    # Copy contents recursively and force overwrite
    cp -rf "$HOME/ms1/archlinux/Hyprland/typecraft/hypr/"* "$HOME/.config/hypr/"
}






# proton for steam games
# bottles for whatever .exe files you have laying around (including games)
# lutris if you so happen to have the .exe file of a game they support.

# Declare a combined array of menu options and function bindings
menu_items=(
    " 1:Git Pull [ms1]            : update_ms1_repo             :$GREEN"
    " 2:Copy Files                : copy_files                  :$GREEN"
    " 3:Install Necessary Packages: install_packages            :$GREEN"
    " 4:Font Setup                : install_jetbrains_mono_font :$GREEN"
    " 5:Desktop Environment       : desktop_environment         :$GREEN"
    " 6:YAY Setup                 : setup_yay                   :$GREEN"
    " 7:bottles                   : desktop_environment         :$GREEN"
    " 8:wine                      : desktop_environment         :$GREEN"
    " 9:Lutris                    : desktop_environment         :$GREEN"
    "10:steam                     : desktop_environment         :$GREEN"
    "11:About                     : about_device                :$GREEN"
    "12:GPU Drivers               : check_gpu_drivers           :$GREEN"
    "13:Heroic Games Launcher     : check_gpu_drivers           :$GREEN"
    "14:Hyprland                  : setup_hyprland_full         :$GREEN"
    "15:SDDM Theme                : sddm_theme                  :$GREEN"
    "16:Disable Bell              : disable_bell                :$GREEN"
    "17:Hyprland Config           : hyperland_config            :$GREEN"
    "18:Neovim Config             : nvim_config                 :$GREEN"
    " c:Close                     : Close_script                :$RED"
    " e:Exit                      : exit_script                 :$RED"
)

# Display the menu and handle user input
while true; do
    # Clear the screen to refresh the menu
    echo ""
    echo -e "${YELLOW}Select an option:${NC}"

    # Display menu options dynamically with assigned colors
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description functions color <<< "$item"
        echo -e "${color}$number. $description${NC}"
    done

    echo ""
    read -p "Enter choice: " choice

    # Handle 'c' and 'e' choices for Close and Exit
    if [ "$choice" == "c" ]; then
        Close_script
        continue
    elif [ "$choice" == "e" ]; then
        exit_script
        continue
    fi

    # Check if the choice is numeric and valid
    valid_choice=false
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description functions color <<< "$item"
        if [ "$choice" -eq "$number" ]; then
            valid_choice=true
            IFS=" " read -r -a function_array <<< "$functions"
            for function in "${function_array[@]}"; do
                $function
            done
            break
        fi
    done

    # If the choice is invalid, show an error message
    if [ "$valid_choice" = false ]; then
        echo -e "${RED}Invalid option. Please try again.${NC}"
    fi

    # Reload the os.sh script to refresh functions and variables
    source $HOME/ms1/archlinux/os.sh
done
