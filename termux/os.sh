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
BASHRC_SOURCE="$REPO_DIR/termux/bashrc"
TERMUX_PROPERTIES_SOURCE="$REPO_DIR/termux/termux.properties"
BASHRC_DEST="$HOME/.bashrc"
TERMUX_PROPERTIES_DEST="$HOME/.termux/termux.properties"
NVIM_INIT_SOURCE="$REPO_DIR/dotfiles/neovim/init.lua"
NVIM_CONFIG_DEST="$HOME/.config/nvim"


# Declare a combined array of menu options and function bindings
menu_items=(
    "Git Pull [ms1]              : update_ms1_repo                         :$BLUE"
    "Copy Files                  : copy_files                              :$BLUE"
    "Install Necessary Packages  : install_packages    setup_storage_passwd:$BLUE"
    "Font Setup                  : install_font_with_oh_my_posh            :$BLUE"
    "Rclone-Dycrypt              : rclone_decrypt                          :$RED"
    "Song [rs]                   : Restore_Songs                           :$BLUE"
    "Neovim Setup                : nvim_setup                              :$BLUE"
    "Git Push                    : git_push_repo                           :$BLUE"
    "Remove Folder [ms3]         : remove_repo                             :$RED"
    "About                       : about_device                            :$BLUE"
    "Flask CoC init              : init_python_flask_CoC                   :$BLUE"
    "Flask CoC start             : start_python_flask_CoC                  :$BLUE"
    "Database Upload Instantly   : upload_latest_database                  :$BLUE"
    "Database Download Instantly : download_latest_database                :$BLUE"
    "SSH for Android              : start_ssh_server                        :$GREEN"
    "SSH for PC                   : show_ssh_connection_info                :$GREEN"
    "Welcome Page                : welcome_remove                          :$RED"
    "Close                       : Close_script                            :$RED"
    "Exit                        : exit_script                             :$RED"
)

# Special hotkey items
declare -A hotkeys=(
    [c]="Close_script"
    [e]="exit_script"
    [x]="test_test"
)

init_python_flask_CoC(){
    pkg install python
    pip install flask flask_sqlalchemy
    cp -r "$HOME/ms1/scripts/flask/5010_coc" "$HOME"
}
start_python_flask_CoC(){
    python "$HOME/5010_coc/Clash_of_Clans_android.py" &
    # Wait for a moment to ensure the server starts
    sleep 2
    # Open Chrome with the server URL
    am start -a android.intent.action.VIEW -d "http://127.0.0.1:5010" com.android.chrome
}

upload_latest_database(){
rclone copy $HOME/instance/ o0:/msBackups/DataBase/latest_instant/ -P
}

download_latest_database(){
rclone copy o0:/msBackups/DataBase/latest_instant/ $HOME/instance/ -P
}




# Function to install necessary packages
packages=(
    "bash"
    "bat"
    "chafa"
    "curl"
    "eza"
    "fastfetch"
    "fzf"
    "git"
    "lsd"
    "lua-language-server"
    "nano"
    "neovim"
    "oh-my-posh"
    "openssh"
    "python"
    "rclone"
    "sshpass"
    "termux-api"
    "termux-tools"
    "wget"
    "which" # to fix neovim bug lua language server not supported on this platform
    "yazi"
    "zoxide"
    "zsh"
    # "mpv"
    # "vim"
    # "x11-repo" "tigervnc"
    # "xdotool"
)

# Function to install necessary packages
install_packages() {
    clear
    echo -e "${GREEN}Updating package list...${NC}"
    pkg update -y
    echo -e "${GREEN}Upgrading installed packages...${NC}"
    pkg upgrade -y
    echo -e "${GREEN}Installing necessary packages...${NC}"
    for pkg in "${packages[@]}"; do
        # Check if the package is already installed
        if ! command -v $pkg &> /dev/null; then
            echo -e "${GREEN}Installing $pkg...${NC}"
            if pkg install "$pkg" -y; then
                echo -e "${GREEN}$pkg installed successfully.${NC}"
            else
                echo -e "${RED}Failed to install $pkg. Please check your network or package name.${NC}"
            fi
        else
            echo -e "${GREEN}$pkg is already installed.${NC}"
        fi
    done
}

# Function to set up storage and password
setup_storage_passwd() {
    echo -e "${GREEN}Setting up storage...${NC}"
    termux-setup-storage
    echo -e "${GREEN}Storage setup completed.${NC}"
    echo -e "${GREEN}Setting up password...${NC}"
    passwd
    echo -e "${GREEN}Password setup completed.${NC}"
}


# Font Download and Setup
install_font_with_oh_my_posh() {
    clear
    echo -e "\e[34mInstalling JetBrainsMono NFP font using oh-my-posh...\e[0m"
    oh-my-posh font install jetbrainsmono
    FONT_PATH="$HOME/.local/share/fonts/jetbrainsmono-nfp/JetBrainsMonoNerdFontPropo-Regular.ttf"
    TERMUX_FONT_DIR="$HOME/.termux"
    # Check if the font is installed
    if [ -f "$FONT_PATH" ]; then
        echo -e "\e[32mJetBrainsMono NFP font found. Setting it as the default...\e[0m"
        # Create .termux directory if it doesn't exist
        mkdir -p "$TERMUX_FONT_DIR"
        # Copy the font file to the .termux directory as font.ttf
        cp "$FONT_PATH" "$TERMUX_FONT_DIR/font.ttf"
        # Reload Termux settings to apply the font
        termux-reload-settings
        echo -e "\e[32mFont has been set as default and Termux settings reloaded.\e[0m"
    else
        echo -e "\e[31mJetBrainsMono NFP font not found after installation. Please ensure it is installed at $FONT_PATH\e[0m"
    fi
}

# Copy .bashrc and termux.properties
copy_files() {
    clear
    echo -e "${CYAN}Copying .bashrc and termux.properties...${NC}"
    cp "$BASHRC_SOURCE" "$BASHRC_DEST"
    mkdir -p "$(dirname $TERMUX_PROPERTIES_DEST)"
    cp "$TERMUX_PROPERTIES_SOURCE" "$TERMUX_PROPERTIES_DEST"
    termux-reload-settings
    echo -e "${CYAN}Files copied and settings reloaded.${NC}"
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



remote_access_goto_d2() {
    clear
    local remote_password="1823"
    local remote_user="nahid"
    local remote_host="192.168.0.101"
    local psexec_path="C:/@delta/msBackups/PSTools/PsExec64.exe"
    local displayswitch_path="C:/@delta/msBackups/Display/DisplaySwitch.exe"
    echo -e "Connecting to the remote server to execute DisplaySwitch..."
    # Run the PsExec command on the Windows remote system
    sshpass -p "$remote_password" ssh "$remote_user@$remote_host" \
        "cmd.exe /c '$psexec_path' -i 1 '$displayswitch_path' /external" || {
        echo -e "${RED}Failed to execute DisplaySwitch on the remote server.${NC}"
        return 1
    }
    echo -e "${GREEN}Remote DisplaySwitch execution completed successfully.${NC}"
}


remote_access_goto_d1() {
    clear
    local remote_password="1823"
    local remote_user="nahid"
    local remote_host="192.168.0.101"
    local psexec_path="C:/@delta/msBackups/PSTools/PsExec64.exe"
    local displayswitch_path="C:/@delta/msBackups/Display/DisplaySwitch.exe"
    echo -e "Connecting to the remote server to execute script..."
    # Run the taskkill commands to kill the processes
    sshpass -p "$remote_password" ssh "$remote_user@$remote_host" \
        "taskkill /F /IM dnplayer.exe || echo 'dnplayer.exe not running';
         taskkill /F /IM python.exe || echo 'python.exe not running';" || {
        echo -e "${RED}Failed to kill processes on the remote server.${NC}"
        return 1
    }
    echo -e "Processes killed successfully. Now executing DisplaySwitch..."
    # Run the PsExec command on the Windows remote system to run DisplaySwitch
    sshpass -p "$remote_password" ssh "$remote_user@$remote_host" \
        "cmd.exe /c '$psexec_path' -i 1 '$displayswitch_path' /internal" || {
        echo -e "${RED}Failed to execute DisplaySwitch on the remote server.${NC}"
        return 1
    }
    echo -e "${GREEN}Remote operations completed successfully.${NC}"
}

about_device() {
    clear
    fastfetch
}

get_ssh_device_ips() {
    local device_ips=""
    if command -v python >/dev/null 2>&1; then
        device_ips="$(python -c 'import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("192.0.2.1", 1)); print(s.getsockname()[0]); s.close()' 2>/dev/null)"
    fi
    if [ -z "$device_ips" ] && command -v hostname >/dev/null 2>&1; then
        device_ips="$(hostname -I 2>/dev/null)"
    fi
    if [ -z "$device_ips" ] && command -v getprop >/dev/null 2>&1; then
        device_ips="$(getprop dhcp.wlan0.ipaddress 2>/dev/null)"
    fi

    for device_ip in $device_ips; do
        case "$device_ip" in
            *.*) printf '%s\n' "$device_ip" ;;
        esac
    done
}

show_ssh_connection_info() {
    local pc_user="nahid"
    local pc_ip="192.168.0.101"
    local ssh_port=22

    echo -e "${CYAN}SSH connection details for the Windows PC${NC}"
    echo "Username: $pc_user"
    echo "PC IP: $pc_ip"
    echo "Port: $ssh_port"
    echo "Password: use the Windows account password"
    printf 'Connect command: ssh -p %s %s@%s\n' "$ssh_port" "$pc_user" "$pc_ip"
    echo "The Windows OpenSSH server must be running for this command to connect."
}

# Run Termux OpenSSH in the foreground so this script remains active until stopped.
start_ssh_server() {
    local ssh_port=8022
    local ssh_user="$(whoami)"

    if ! command -v sshd >/dev/null 2>&1; then
        echo -e "${RED}OpenSSH is not installed. Use 'pkg install openssh' first.${NC}"
        return 1
    fi

    if ! command -v python >/dev/null 2>&1; then
        echo -e "${RED}Python is required to configure the SSH password. Install it with 'pkg install python'.${NC}"
        return 1
    fi

    python - "$HOME/.termux_authinfo" <<'PY'
import hashlib
import os
import sys

password_hash = hashlib.pbkdf2_hmac(
    "sha1", b"1823", b"Termux!", 65536, dklen=20
)
with open(sys.argv[1], "wb") as auth_file:
    auth_file.write(password_hash)
os.chmod(sys.argv[1], 0o600)
PY
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to configure the SSH password.${NC}"
        return 1
    fi

    mkdir -p "$HOME/.ssh"
    if ! compgen -G "$PREFIX/etc/ssh/ssh_host_*_key" >/dev/null; then
        ssh-keygen -A || return 1
    fi

    echo -e "${GREEN}SSH password has been set to: 1823${NC}"
    echo -e "${GREEN}Starting SSH for $ssh_user on port $ssh_port.${NC}"
    echo "Run this command from another device on the same network:"
    local device_ips="$(get_ssh_device_ips)"
    if [ -n "$device_ips" ]; then
        for device_ip in $device_ips; do
            case "$device_ip" in
                *.*) printf '  ssh -p %s %s@%s\n' "$ssh_port" "$ssh_user" "$device_ip" ;;
            esac
        done
    else
        echo "  Could not detect the phone's Wi-Fi IP address. Find it in Android Wi-Fi settings, then run:"
        echo "  ssh -p $ssh_port $ssh_user@<phone-ip>"
    fi
    echo "Press Ctrl+C here to stop the SSH server."

    termux-wake-lock 2>/dev/null || true
    trap 'termux-wake-unlock 2>/dev/null || true; trap - INT TERM' INT TERM
    sshd -D -p "$ssh_port"
    local status=$?
    termux-wake-unlock 2>/dev/null || true
    trap - INT TERM
    return "$status"
}

# ntfy_notify() {
#     clear
#     # Initialize counter
#     not_found_count=0
#     # Infinite loop to check continuously
#     while true; do
#         # Check if "ntfy" exists in the output
#         if rclone ls g00: | grep -i ntfy; then
#             # Play the music file using mpv if "ntfy" is found
#             mpv /storage/emulated/0/song/wwe/ww.mp3
#         else
#             # Increment the counter and display the message
#             not_found_count=$((not_found_count + 1))
#             echo "No 'ntfy' found in the output. Count: $not_found_count"
#         fi
#         # Wait for 30 seconds before checking again
#         sleep 30
#     done
# }

# ntfy_notify() {
#     clear
#     # Prevent the device from going into sleep mode
#     termux-wake-lock
#     # Initialize counter
#     not_found_count=0
#     # Infinite loop to check continuously
#     while true; do
#         # Check if "ntfy" exists in the output
#         if rclone ls g00: | grep -iq "ntfy"; then
#             # Play the music file using mpv if "ntfy" is found
#             mpv /storage/emulated/0/song/wwe/ww.mp3 &
#             # Get the PID of mpv
#             mpv_pid=$!
#             # Wait for mpv to finish or be killed
#             wait $mpv_pid
#             # Check if the exit status indicates that mpv was closed properly
#             if [ $? -eq 0 ]; then
#                 echo "mpv was closed. Exiting function."
#                 break
#             fi
#         else
#             # Increment the counter and display the message
#             not_found_count=$((not_found_count + 1))
#             echo "No 'ntfy' found in the output. Count: $not_found_count"
#         fi
#         # Wait for 30 seconds before checking again
#         sleep 30
#     done
#     # Release the wake lock once the script finishes
#     termux-wake-unlock
# }

# ntfy_notify() {
#     clear
#     # Prevent the device from going into sleep mode
#     termux-wake-lock
#     # Initialize counter
#     not_found_count=0
#     # Infinite loop to check continuously
#     while true; do
#         # Check if "ntfy" exists in the output
#         if rclone ls g00: | grep -i ntfy; then
#             # Run the specified command if "ntfy" is found
#             am start rk.android.app.shortcutmaker/rk.android.app.shortcutmaker.CommonMethods.SplashScreenActivity
#             # Exit the function after executing the command
#             echo "Command executed. Exiting function."
#             break
#         else
#             # Increment the counter and display the message
#             not_found_count=$((not_found_count + 1))
#             echo "No 'ntfy' found in the output. Count: $not_found_count"
#         fi
#         # Wait for 30 seconds before checking again
#         sleep 30
#     done
#     # Release the wake lock once the script finishes
#     termux-wake-unlock
# }


ntfy_notify() {
    clear
    # Prevent the device from going into sleep mode
    termux-wake-lock
    # Initialize counter
    not_found_count=0
    # Infinite loop to check continuously
    while true; do
        # Get current time in 12-hour format with AM/PM
        current_time=$(date "+%I:%M:%S %p")
        
        # Set green color for the time (ANSI escape code)
        green='\033[0;32m'
        # Reset color
        reset='\033[0m'
        
        # Check if "ntfy" exists in the output
        if rclone ls g00: | grep -i ntfy; then
            # Start the Automate flow
            am start -a com.llamalab.automate.intent.action.START_FLOW \
                -d "content://com.llamalab.automate.provider/flows/10/statements/6" \
                -n com.llamalab.automate/.StartServiceActivity
            # Exit the function after executing the command
            echo "Automate flow started. Exiting function."
            break
        else
            # Increment the counter and display the message with colored time
            not_found_count=$((not_found_count + 1))
            echo -e "${green}$current_time${reset} No 'ntfy' found. Count: $not_found_count"
        fi
        # Wait for 30 seconds before checking again
        sleep 30
    done
    # Release the wake lock once the script finishes
    termux-wake-unlock
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
    echo "Decreypt rclone conf ...."
    pip install pycryptodomex
    python ~/ms1/termux/locker/locker.py --decrypt ~/ms1/asset/rclone/rclone.conf.enc

    echo -e "Copying rclone.conf"
    mkdir -p "$HOME/.config/rclone"
    cp "$HOME/ms1/asset/rclone/rclone.conf" "$HOME/.config/rclone"
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
        $function
    elif [[ -n "${hotkeys[$choice]}" ]]; then
        ${hotkeys[$choice]}
    else
        echo -e "${RED}Invalid option. Please try again.${NC}"
    fi
done
