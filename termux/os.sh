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
    "SSH for Android              : start_ssh_server                        :$GREEN"
    "SSH for PC                   : show_ssh_connection_info                :$GREEN"
    "Select Best Mirror           : select_best_mirror                      :$CYAN"
    "Pkg Update & Upgrade        : pkg_update_upgrade                      :$CYAN"
    "Pkg Search & Install        : pkg_search_install                      :$CYAN"
    "Pkg Uninstall               : pkg_uninstall                           :$CYAN"
    "Linux Setup                 : linux_setup                             :$MAGENTA"
    "Termux UI Restore           : termux_ui_restore                       :$MAGENTA"
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
    if [ ! -d "$ms1_folder" ]; then
        echo "The folder $ms1_folder does not exist."
        return 1
    fi

    cd "$ms1_folder" || { echo "Failed to cd into $ms1_folder."; return 1; }

    # Fetch latest from remote first
    echo -e "${CYAN}Fetching from remote...${NC}"
    git fetch origin || { echo -e "${RED}Fetch failed. Check network/auth.${NC}"; return 1; }

    # Check the state
    local local_commit remote_commit base_commit
    local_commit=$(git rev-parse HEAD)
    remote_commit=$(git rev-parse "@{u}" 2>/dev/null)
    base_commit=$(git merge-base HEAD "@{u}" 2>/dev/null)

    if [ "$local_commit" = "$remote_commit" ]; then
        echo -e "${GREEN}Already up to date.${NC}"
        return 0
    fi

    if [ "$local_commit" = "$base_commit" ]; then
        # Normal fast-forward
        echo -e "${CYAN}Fast-forwarding...${NC}"
        git pull --ff-only
    else
        # Local has diverged (reverted commits, amended, etc.)
        echo -e "${YELLOW}Local branch has diverged from remote.${NC}"
        echo -e "${YELLOW}Local:  $(git log --oneline -1 HEAD)${NC}"
        echo -e "${YELLOW}Remote: $(git log --oneline -1 "@{u}")${NC}"
        echo ""
        echo -e "  ${GREEN}1)${NC} Reset to remote  ${RED}(discards local commits)${NC}"
        echo -e "  ${CYAN}2)${NC} Rebase on top of remote"
        echo -e "  ${YELLOW}3)${NC} Cancel"
        echo ""
        read -p "Choose [1/2/3]: " sync_choice
        case "$sync_choice" in
            1)
                echo -e "${CYAN}Resetting to origin/$(git rev-parse --abbrev-ref HEAD)...${NC}"
                git reset --hard "@{u}"
                git clean -fd
                echo -e "${GREEN}Reset complete.${NC}"
                ;;
            2)
                echo -e "${CYAN}Rebasing...${NC}"
                git rebase "@{u}" || {
                    echo -e "${RED}Rebase had conflicts. Aborting.${NC}"
                    git rebase --abort
                    return 1
                }
                echo -e "${GREEN}Rebase complete.${NC}"
                ;;
            *)
                echo -e "${YELLOW}Cancelled.${NC}"
                ;;
        esac
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
    echo
    echo "If the SSH server is stopped, run these in Administrator PowerShell on the PC:"
    echo "  Set-Service sshd -StartupType Automatic"
    echo "  Start-Service sshd"
    echo
    echo "To change the Windows account password used by SSH, run in Administrator PowerShell:"
    echo "  net user $pc_user *"
    echo "Enter the new password when prompted; it will not be displayed."
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



pkg_update_upgrade() {
    clear
    echo -e "${CYAN}Running pkg update...${NC}"
    pkg update -y
    echo -e "${CYAN}Running pkg upgrade...${NC}"
    pkg upgrade -y
    echo -e "${GREEN}Done.${NC}"
}

pkg_search_install() {
    clear
    if ! command -v fzf >/dev/null 2>&1; then
        echo -e "${RED}fzf is not installed. Installing...${NC}"
        pkg install fzf -y || { echo -e "${RED}Failed to install fzf.${NC}"; return 1; }
    fi

    echo -e "${CYAN}Loading package list...${NC}"
    # Get all available packages with short description
    local pkg_list
    pkg_list=$(apt-cache search . 2>/dev/null | sort)

    if [ -z "$pkg_list" ]; then
        echo -e "${RED}No packages found. Try running pkg update first.${NC}"
        return 1
    fi

    # Let user pick one or more packages with fzf (Tab to multi-select)
    local selected
    selected=$(echo "$pkg_list" | fzf \
        --multi \
        --prompt="Search packages (Tab=select, Enter=install): " \
        --preview='apt-cache show {1} 2>/dev/null | grep -E "^(Package|Version|Installed-Size|Description):"' \
        --preview-window=right:40%:wrap \
        --height=90% \
        --reverse \
        --ansi \
        --bind='ctrl-a:select-all' \
        | awk '{print $1}')

    if [ -z "$selected" ]; then
        echo -e "${YELLOW}No package selected.${NC}"
        return 0
    fi

    echo ""
    echo -e "${CYAN}Selected packages:${NC}"
    echo "$selected" | while read -r p; do
        echo -e "  ${GREEN}+${NC} $p"
    done
    echo ""
    read -p "Install these packages? [y/N]: " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        pkg install -y $selected
        echo -e "${GREEN}Done.${NC}"
    else
        echo -e "${YELLOW}Cancelled.${NC}"
    fi
}

pkg_uninstall() {
    clear
    if ! command -v fzf >/dev/null 2>&1; then
        echo -e "${RED}fzf is not installed. Installing...${NC}"
        pkg install fzf -y || { echo -e "${RED}Failed to install fzf.${NC}"; return 1; }
    fi

    echo -e "${CYAN}Loading installed packages...${NC}"
    local pkg_list
    pkg_list=$(dpkg-query -W -f='${Package}\t${Version}\t${Status}\n' 2>/dev/null \
        | awk -F'\t' '$3 ~ /installed/ {print $1"\t"$2}' | sort)

    if [ -z "$pkg_list" ]; then
        echo -e "${RED}Could not retrieve installed packages.${NC}"
        return 1
    fi

    local selected
    selected=$(echo "$pkg_list" | fzf \
        --multi \
        --prompt="Uninstall packages (Tab=select, Enter=confirm): " \
        --preview='apt-cache show {1} 2>/dev/null | grep -E "^(Package|Version|Installed-Size|Description):"' \
        --preview-window=right:40%:wrap \
        --height=90% \
        --reverse \
        --ansi \
        --bind='ctrl-a:select-all' \
        | awk '{print $1}')

    if [ -z "$selected" ]; then
        echo -e "${YELLOW}No package selected.${NC}"
        return 0
    fi

    echo ""
    echo -e "${RED}Packages to remove:${NC}"
    echo "$selected" | while read -r p; do
        echo -e "  ${RED}-${NC} $p"
    done
    echo ""
    read -p "Uninstall these packages? [y/N]: " confirm
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        pkg uninstall -y $selected
        echo -e "${GREEN}Done.${NC}"
    else
        echo -e "${YELLOW}Cancelled.${NC}"
    fi
}

# ─── Termux UI Restore ─────────────────────────────────────────────────────────

termux_ui_restore() {
    clear
    echo -e "${MAGENTA}╔══════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║       Termux UI Restore              ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════╝${NC}"
    echo ""

    local dotfiles="$REPO_DIR/termux/dotfiles"

    # ── 1. Install required packages ────────────────────────────────
    echo -e "${CYAN}[1/7] Installing required packages...${NC}"
    pkg install -y bash eza fastfetch zoxide fzf oh-my-posh git curl

    # ── 2. Catppuccin color theme ────────────────────────────────────
    echo -e "${CYAN}[2/7] Applying Catppuccin Mocha color theme...${NC}"
    mkdir -p "$HOME/.termux"
    cp "$dotfiles/colors.properties" "$HOME/.termux/colors.properties"

    # ── 3. JetBrainsMono Nerd Font ───────────────────────────────────
    echo -e "${CYAN}[3/7] Installing JetBrainsMono Nerd Font...${NC}"
    curl -fLo "$HOME/.termux/font.ttf" \
        "https://raw.githubusercontent.com/ryanoasis/nerd-fonts/v3.2.1/patched-fonts/JetBrainsMono/NoLigatures/Regular/JetBrainsMonoNLNerdFont-Regular.ttf"
    chmod 644 "$HOME/.termux/font.ttf"

    # ── 4. termux.properties ─────────────────────────────────────────
    echo -e "${CYAN}[4/7] Copying termux.properties...${NC}"
    cp "$TERMUX_PROPERTIES_SOURCE" "$TERMUX_PROPERTIES_DEST"

    # ── 5. Fastfetch config ──────────────────────────────────────────
    echo -e "${CYAN}[5/7] Copying fastfetch config...${NC}"
    mkdir -p "$HOME/.config/fastfetch"
    cp "$dotfiles/fastfetch/config.jsonc" "$HOME/.config/fastfetch/config.jsonc"

    # ── 6. Oh My Posh theme ──────────────────────────────────────────
    echo -e "${CYAN}[6/7] Copying Oh My Posh Catppuccin theme...${NC}"
    mkdir -p "$HOME/.config/ohmyposh"
    cp "$dotfiles/ohmyposh/catppuccin.omp.json" "$HOME/.config/ohmyposh/catppuccin.omp.json"

    # ── 7. .bashrc + silence welcome banner ─────────────────────────
    echo -e "${CYAN}[7/7] Copying .bashrc and silencing welcome banner...${NC}"
    cp "$BASHRC_SOURCE" "$BASHRC_DEST"
    touch "$HOME/.hushlogin"
    echo "" > "$PREFIX/etc/motd"
    [ -f "$PREFIX/etc/motd-playstore" ] && echo "" > "$PREFIX/etc/motd-playstore"
    [ -f "$PREFIX/etc/motd.sh" ] && printf '#!/bin/sh\n' > "$PREFIX/etc/motd.sh"

    # ── Reload settings ──────────────────────────────────────────────
    termux-reload-settings

    echo ""
    echo -e "${GREEN}✓ Termux UI restore complete!${NC}"
    echo -e "  • Catppuccin Mocha colors applied"
    echo -e "  • JetBrainsMono Nerd Font installed"
    echo -e "  • termux.properties updated"
    echo -e "  • Fastfetch config applied"
    echo -e "  • Oh My Posh Catppuccin theme applied"
    echo -e "  • .bashrc copied, welcome banner silenced"
    echo ""
    echo -e "${YELLOW}Run 'source ~/.bashrc' or reopen Termux to apply the prompt.${NC}"
}

# ─── Linux Setup ───────────────────────────────────────────────────────────────

linux_setup() {
    clear
    echo -e "${MAGENTA}╔══════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║          Linux Setup Menu            ║${NC}"
    echo -e "${MAGENTA}╚══════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC} Install Ubuntu           (proot-distro)"
    echo -e "  ${CYAN}2)${NC} Setup Ubuntu environment  (bashrc, nano, git, packages)"
    echo -e "  ${RED}3)${NC} Remove Ubuntu completely (Termux only)"
    echo ""
    read -p "Enter choice [1/3]: " linux_choice
    case "$linux_choice" in
        1) _install_ubuntu ;;
        2) _setup_termux_env ;;
        3) _remove_ubuntu ;;
        *) echo -e "${RED}Invalid choice.${NC}" ;;
    esac
}

# Option 3 – remove the Ubuntu rootfs from Termux
_remove_ubuntu() {
    clear
    if [ -r /etc/os-release ] && grep -qi '^ID=ubuntu$' /etc/os-release; then
        echo -e "${RED}Run this option from Termux, not inside Ubuntu.${NC}"
        return 1
    fi

    if ! command -v proot-distro >/dev/null 2>&1; then
        echo -e "${YELLOW}proot-distro is not installed; there is no Ubuntu installation to remove.${NC}"
        return 0
    fi

    if ! proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' && \
       [ ! -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ]; then
        echo -e "${YELLOW}Ubuntu is not installed.${NC}"
        return 0
    fi

    echo -e "${RED}This will permanently remove the Ubuntu root filesystem and its files.${NC}"
    read -r -p "Remove Ubuntu? [y/N]: " remove_ubuntu_confirm
    case "$remove_ubuntu_confirm" in
        y|Y|yes|YES)
            if proot-distro remove ubuntu; then
                echo -e "${GREEN}Ubuntu has been removed.${NC}"
            else
                echo -e "${RED}Failed to remove Ubuntu.${NC}"
                return 1
            fi
            ;;
        *) echo -e "${YELLOW}Removal cancelled.${NC}" ;;
    esac
}

# Option 1 – install Ubuntu via proot-distro
_install_ubuntu() {
    clear
    echo -e "${MAGENTA}Installing Ubuntu via proot-distro...${NC}"
    echo ""

    # Install proot-distro if missing
    if ! command -v proot-distro >/dev/null 2>&1; then
        echo -e "${CYAN}Installing proot-distro...${NC}"
        pkg install proot-distro -y || {
            echo -e "${RED}Failed to install proot-distro.${NC}"
            return 1
        }
    fi

    # Install Ubuntu if not already present
    if proot-distro list | grep -q "ubuntu.*installed"; then
        echo -e "${GREEN}Ubuntu is already installed.${NC}"
    else
        echo -e "${CYAN}Downloading and installing Ubuntu...${NC}"
        proot-distro install ubuntu || {
            echo -e "${RED}Failed to install Ubuntu.${NC}"
            return 1
        }
        echo -e "${GREEN}Ubuntu installed successfully.${NC}"
    fi

    echo ""
    echo -e "${CYAN}Setting up Ubuntu (update + essential packages)...${NC}"
    proot-distro login ubuntu -- bash -c "
        apt update -y && apt upgrade -y
        apt install -y curl wget git nano vim sudo locales tzdata
        locale-gen en_US.UTF-8
        echo 'Ubuntu ready. Run: proot-distro login ubuntu'
    "
    echo ""
    echo -e "${GREEN}Done! Launch Ubuntu with:${NC} proot-distro login ubuntu"
}

# Option 2 – set up a nice environment inside Ubuntu (proot-distro)
_setup_termux_env() {
    clear
    echo -e "${CYAN}Setting up Ubuntu environment...${NC}"
    echo ""

    # This script can be run from either Termux or from inside Ubuntu.
    local inside_ubuntu=false
    if [ -r /etc/os-release ] && grep -qi '^ID=ubuntu$' /etc/os-release; then
        inside_ubuntu=true
    fi

    # Make sure Ubuntu is actually installed when running from Termux. The
    # installed-rootfs directory is also a reliable fallback across versions
    # whose `proot-distro list` output differs.
    if [ "$inside_ubuntu" = false ] && {
        ! command -v proot-distro >/dev/null 2>&1 || {
            ! proot-distro list 2>/dev/null | grep -qi 'ubuntu.*installed' &&
            [ ! -d "$HOME/.local/share/proot-distro/installed-rootfs/ubuntu" ];
        }
    }; then
        echo -e "${RED}Ubuntu is not installed yet. Run option 1 first.${NC}"
        return 1
    fi

    local ub_home
    if [ "$inside_ubuntu" = true ]; then
        ub_home="$HOME"
    else
        local ubuntu_root="$HOME/.local/share/proot-distro/installed-rootfs/ubuntu"
        ub_home="$ubuntu_root/root"
    fi

    # ── 1. Create useful directories ────────────────────────────────
    echo -e "${CYAN}[1/5] Creating standard directories in Ubuntu...${NC}"
    mkdir -p "$ub_home/projects" "$ub_home/scripts" "$ub_home/tmp" "$ub_home/bin"

    # ── 2. Write ~/.bashrc ───────────────────────────────────────────
    echo -e "${CYAN}[2/5] Writing Ubuntu ~/.bashrc...${NC}"
    cat > "$ub_home/.bashrc" << 'BASHRC'
# ── Ubuntu .bashrc ───────────────────────────────────────────────────

# ── Prompt: user@host  dir  (git-branch)  ❯ ────────────────────────
_git_branch() {
    git rev-parse --is-inside-work-tree &>/dev/null || return
    local b
    b=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
    printf " \033[0;33m(%s)\033[0m" "$b"
}
PS1='\[\033[0;32m\]\u@\h\[\033[0m\] \[\033[0;34m\]\w\[\033[0m\]$(_git_branch) \[\033[0;36m\]❯\[\033[0m\] '

# ── History ──────────────────────────────────────────────────────────
HISTSIZE=5000
HISTFILESIZE=10000
HISTCONTROL=ignoreboth:erasedups
shopt -s histappend

# ── Navigation ───────────────────────────────────────────────────────
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias -- -='cd -'

# ── ls ───────────────────────────────────────────────────────────────
if command -v eza &>/dev/null; then
    alias ls='eza --group-directories-first'
    alias la='eza -a --group-directories-first'
    alias ll='eza -l --header --group-directories-first'
    alias lla='eza -la --header --group-directories-first'
    alias lt='eza --tree --level=2'
    alias tree='eza --tree'
else
    alias ls='ls --color=auto'
    alias la='ls -a --color=auto'
    alias ll='ls -lah --color=auto'
    alias lla='ls -lah --color=auto'
    alias tree='tree -C'
fi
alias cls='clear'
alias grep='grep --color=auto'
alias diff='diff --color=auto'

# ── Common shortcuts ──────────────────────────────────────────────────
alias c='clear'
alias q='exit'
alias reload='source ~/.bashrc && echo "reloaded"'
alias bashrc='nano ~/.bashrc'
alias rb='reload'
alias myip='curl -s https://ipinfo.io/ip && echo'
alias ports='ss -tulpn'
alias now='date "+%Y-%m-%d %H:%M:%S"'
alias df='df -h'
alias du='du -sh *'
alias free='free -h'
alias update='apt update && apt upgrade -y'

# ── Git shortcuts ─────────────────────────────────────────────────────
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gpl='git pull'
alias gl='git log --oneline --graph --decorate -15'

# Termux-style shortcuts that are safe to use from Ubuntu.
os() {
    local termux_home="/data/data/com.termux/files/home"
    if [ -f "$HOME/ms1/termux/os.sh" ]; then
        bash "$HOME/ms1/termux/os.sh"
    elif [ -f "$termux_home/ms1/termux/os.sh" ]; then
        HOME="$termux_home" bash "$termux_home/ms1/termux/os.sh"
    else
        echo "Could not find ms1/termux/os.sh in Ubuntu or Termux home."
        return 1
    fi
}

# ── Handy functions ───────────────────────────────────────────────────
mkcd()   { mkdir -p "$1" && cd "$1"; }
ff()     { find . -name "*$1*" 2>/dev/null; }
extract() {
    case "$1" in
        *.tar.gz|*.tgz)  tar xzf "$1" ;;
        *.tar.bz2|*.tbz) tar xjf "$1" ;;
        *.tar.xz)        tar xJf "$1" ;;
        *.tar)           tar xf  "$1" ;;
        *.zip)           unzip   "$1" ;;
        *.gz)            gunzip  "$1" ;;
        *.bz2)           bunzip2 "$1" ;;
        *.xz)            unxz    "$1" ;;
        *.7z)            7z x    "$1" ;;
        *) echo "Unknown archive: $1" ;;
    esac
}

export PATH="$HOME/bin:$PATH"

# ── zoxide (smarter cd) ───────────────────────────────────────────────
command -v zoxide &>/dev/null && eval "$(zoxide init bash)"

# Fastfetch on interactive startup, like the Termux shell configuration.
if [[ $- == *i* ]] && command -v fastfetch &>/dev/null; then
    fastfetch
fi
BASHRC

    # ── 3. Write ~/.nanorc ───────────────────────────────────────────
    echo -e "${CYAN}[3/5] Writing Ubuntu ~/.nanorc...${NC}"
    cat > "$ub_home/.nanorc" << 'NANORC'
set autoindent
set linenumbers
set mouse
set tabsize 4
set tabstospaces
set trimblanks
set constantshow
include "/usr/share/nano/*.nanorc"
NANORC

    # ── 4. Install extra packages inside Ubuntu ──────────────────────
    echo -e "${CYAN}[4/5] Installing useful packages inside Ubuntu...${NC}"
    if [ "$inside_ubuntu" = true ]; then
        apt update -y
        apt install -y curl wget git nano vim htop tree zsh tmux unzip zip \
            python3 python3-pip build-essential
    else
        proot-distro login ubuntu -- bash -c "
        apt update -y
        apt install -y \
            curl wget git nano vim htop tree \
            zsh tmux unzip zip \
            python3 python3-pip \
            build-essential \
            2>/dev/null || true
        "
    fi

    # ── 5. Git config inside Ubuntu ──────────────────────────────────
    echo -e "${CYAN}[5/5] Configuring git inside Ubuntu...${NC}"
    if [ "$inside_ubuntu" = true ]; then
        git config --global core.editor nano
        git config --global pull.rebase false
        git config --global init.defaultBranch main
        git config --global color.ui auto
        git config --global alias.st status
        git config --global alias.lg 'log --oneline --graph --decorate -15'
    else
        proot-distro login ubuntu -- bash -c "
            git config --global core.editor nano
            git config --global pull.rebase false
            git config --global init.defaultBranch main
            git config --global color.ui auto
            git config --global alias.st status
            git config --global alias.lg 'log --oneline --graph --decorate -15'
        "
    fi

    echo ""
    echo -e "${GREEN}✓ Ubuntu environment setup complete!${NC}"
    echo -e "  • ${CYAN}~/.bashrc${NC}   — prompt, aliases, git shortcuts, history"
    echo -e "  • ${CYAN}~/.nanorc${NC}   — line numbers, autoindent, syntax highlight"
    echo -e "  • ${CYAN}~/.gitconfig${NC} — sensible git defaults"
    echo -e "  • ${CYAN}~/projects  ~/scripts  ~/tmp  ~/bin${NC}  created"
    echo -e "  • curl wget git nano vim htop tree zsh tmux python3 installed"
    echo ""
    if [ "$inside_ubuntu" = true ]; then
        echo -e "${YELLOW}Ubuntu environment configured for $HOME.${NC}"
    else
        echo -e "${YELLOW}Login with: proot-distro login ubuntu${NC}"
    fi
}


# ─── Mirror helpers ────────────────────────────────────────────────────────────

# Apply a mirror URL directly to sources.list and run pkg update
_apply_mirror() {
    local label="$1"
    local url="$2"
    local sources_file="$PREFIX/etc/apt/sources.list"
    echo "deb $url stable main" > "$sources_file"
    echo -e "${GREEN}sources.list set to: $label${NC}"
    echo -e "${CYAN}Running pkg update...${NC}"
    pkg update -y
    echo -e "${GREEN}Done.${NC}"
}

select_best_mirror() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     Termux Mirror Selector           ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Choose mode:${NC}"
    echo -e "  ${GREEN}1)${NC} termux-change-repo  – full official mirror list (interactive)"
    echo -e "  ${CYAN}2)${NC} Auto benchmark       – ping mirrors and pick the fastest"
    echo ""
    read -p "Enter choice [1/2]: " mirror_mode

    case "$mirror_mode" in
        2) _mirror_auto_pick ;;
        *)
            if command -v termux-change-repo >/dev/null 2>&1; then
                termux-change-repo
            else
                echo -e "${RED}termux-change-repo not found. Falling back to auto benchmark...${NC}"
                _mirror_auto_pick
            fi
            ;;
    esac
}

# Benchmark mirrors – reads from Termux's own mirror files when available,
# falls back to a hardcoded list otherwise.
_mirror_auto_pick() {
    local mirror_dir="$PREFIX/etc/termux/mirrors"

    declare -a bm_labels=()
    declare -a bm_urls=()

    if [ -d "$mirror_dir" ]; then
        while IFS= read -r -d '' mfile; do
            local label url
            label="$(basename "$mfile")"
            # Mirror files are shell scripts; extract the MAIN= variable value
            url="$(grep -m1 '^MAIN=' "$mfile" 2>/dev/null | cut -d'"' -f2)"
            if [[ "$url" == https://* ]]; then
                bm_labels+=("$label")
                bm_urls+=("$url")
            fi
        done < <(find "$mirror_dir" -type f ! -name "*.dpkg-*" ! -name "*~" -print0 2>/dev/null)
    fi

    # Fallback list if Termux mirror directory is empty or missing
    if [ ${#bm_labels[@]} -eq 0 ]; then
        bm_labels=(
            "default (Cloudflare)"
            "packages.termux.dev"
            "grimler.se"
            "mirrors.tuna.tsinghua.edu.cn"
            "mirrors.bfsu.edu.cn"
            "mirrors.ustc.edu.cn"
            "mirror.nju.edu.cn"
            "ftp.fau.de"
        )
        bm_urls=(
            "https://packages.termux.dev/apt/termux-main"
            "https://packages.termux.dev/apt/termux-main"
            "https://grimler.se/termux/termux-packages-24"
            "https://mirrors.tuna.tsinghua.edu.cn/termux/termux-packages-24"
            "https://mirrors.bfsu.edu.cn/termux/termux-packages-24"
            "https://mirrors.ustc.edu.cn/termux/termux-packages-24"
            "https://mirror.nju.edu.cn/termux/termux-packages-24"
            "https://ftp.fau.de/termux/termux-packages-24"
        )
    fi

    echo ""
    echo -e "${CYAN}Benchmarking ${#bm_labels[@]} mirrors...${NC}"
    echo ""

    local best_label="" best_url="" best_time=99999999

    for i in "${!bm_labels[@]}"; do
        local label="${bm_labels[$i]}"
        local url="${bm_urls[$i]}"
        local response_ms
        response_ms=$(curl -o /dev/null -s -w "%{time_starttransfer}" \
            --connect-timeout 5 --max-time 8 \
            "$url/dists/stable/Release" 2>/dev/null)

        if [ $? -eq 0 ] && [ -n "$response_ms" ]; then
            local response_int
            response_int=$(echo "$response_ms" | awk '{printf "%d", $1 * 1000}')
            printf "  %-42s %b%d ms%b\n" "$label" "$GREEN" "$response_int" "$NC"
            if [ "$response_int" -lt "$best_time" ]; then
                best_time="$response_int"
                best_label="$label"
                best_url="$url"
            fi
        else
            printf "  %-42s %bunreachable%b\n" "$label" "$RED" "$NC"
        fi
    done

    echo ""
    if [ -z "$best_label" ]; then
        echo -e "${RED}No mirror was reachable. Check your network.${NC}"
        return 1
    fi

    echo -e "${GREEN}★ Best mirror: $best_label — ${best_time} ms${NC}"
    echo ""
    _apply_mirror "$best_label" "$best_url"
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
