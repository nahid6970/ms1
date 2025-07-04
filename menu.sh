#!/bin/bash

# Function to display the menu
display_menu() {
    clear
    echo "========================================"
    echo "          Arch Linux Setup Menu         "
    echo "========================================"
    echo "Main Menu:"
    echo "  1) Initial Setup"
    echo "  2) Application Setup"
    echo "  3) Clone Projects"
    echo "  4) Backup & Restore"
    echo "  5) Port Management"
    echo "  6) Symbolic Links (mklink equivalents)"
    echo "  7) Github Projects (Windows-specific)"
    echo "  0) Exit"
    echo "----------------------------------------"
}

# Function to handle Initial Setup submenu
initial_setup_menu() {
    while true; do
        clear
        echo "========================================"
        echo "          Initial Setup Menu            "
        echo "========================================"
        echo "  1) Package Manager & Essential Apps"
        echo "  2) Policies (Windows-specific)"
        echo "  3) Install Common Packages"
        echo "  4) Install Pwsh Modules (if pwsh installed)"
        echo "  5) Font Setup (Oh-My-Posh)"
        echo "  6) Python pip Packages"
        echo "  7) Update All Packages"
        echo "  0) Back to Main Menu"
        echo "----------------------------------------"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Installing essential packages (pacman & yay)..."
                sudo pacman -Syu --noconfirm
                # Assuming yay is installed. If not, user needs to install it first.
                # Example: git clone https://aur.archlinux.org/yay.git && cd yay && makepkg -si
                yay -Syu --noconfirm
                sudo pacman -S --noconfirm git python oh-my-posh fzf rclone yt-dlp ffmpeg highlight zoxide
                echo "Note: 'komorebi', 'ditto', 'text-grab' are Windows-specific and not installed."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Policies are largely Windows-specific (e.g., Set-ExecutionPolicy). No direct Linux equivalent in this context."
                read -p "Press Enter to continue..."
                ;;
            3)
                echo "Installing common packages..."
                yay -S --noconfirm ack bat neovim putty rssguard rufus ventoy
                echo "Note: 'capture22text', 'winaero-tweaker' are Windows-specific."
                read -p "Press Enter to continue..."
                ;;
            4)
                echo "Installing PowerShell modules (requires PowerShell Core 'pwsh' to be installed)..."
                if command -v pwsh &> /dev/null; then
                    pwsh -Command "Install-Module -Name BurntToast -Scope CurrentUser"
                else
                    echo "PowerShell Core (pwsh) is not installed. Please install it first if you want to run PowerShell modules."
                fi
                read -p "Press Enter to continue..."
                ;;
            5)
                echo "Setting up Oh-My-Posh fonts..."
                oh-my-posh font install
                read -p "Press Enter to continue..."
                ;;
            6)
                echo "Installing Python pip packages from requirements file..."
                # Assuming pip_required.txt is in a similar asset path
                if [ -f "/ms1/asset/pip/pip_required.txt" ]; then
                    python -m pip install -r "/ms1/asset/pip/pip_required.txt"
                else
                    echo "Error: /ms1/asset/pip/pip_required.txt not found. Please adjust the path."
                fi
                read -p "Press Enter to continue..."
                ;;
            7)
                echo "Updating all packages (pacman, yay, pip)..."
                sudo pacman -Syu --noconfirm
                yay -Syu --noconfirm
                python -m pip install --upgrade pip
                python -m pip list --outdated | awk '{print $1}' | xargs -n1 pip install -U
                echo "Package update complete."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Application Setup submenu
application_setup_menu() {
    while true; do
        clear
        echo "========================================"
        echo "        Application Setup Menu          "
        echo "========================================"
        echo "  1) Jackett + qBittorrent (Manual Steps)"
        echo "  2) LDPlayer (Windows-specific)"
        echo "  3) Neovim Config 1 (Symbolic Link)"
        echo "  4) Neovim Config 2 (Symbolic Link)"
        echo "  5) Notepad++ Theme Setup (Windows-specific)"
        echo "  6) PotPlayer Register (Windows-specific)"
        echo "  0) Back to Main Menu"
        echo "----------------------------------------"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Jackett + qBittorrent Setup:"
                echo "Step 1: Install qBittorrent: sudo pacman -S qbittorrent"
                echo "Step 2: Install Jackett (e.g., from AUR: yay -S jackett-bin)"
                echo "Step 3: Open qBittorrent -> View -> Search Engine -> Go To search engine tab -> Search plugin -> Check for updates."
                echo "Step 4: Start Jackett and add necessary indexers via its web UI."
                echo "Step 5: Copy Jackett API key from web UI to qBittorrent search settings."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "LDPlayer is an Android emulator for Windows. No direct Linux equivalent."
                read -p "Press Enter to continue..."
                ;;
            3)
                echo "Creating symbolic link for Neovim config 1..."
                rm -rf ~/.config/nvim ~/.local/share/nvim
                mkdir -p ~/.config/nvim
                ln -s "/ms1/asset/linux/neovim/init.lua" ~/.config/nvim/init.lua
                echo "Neovim config 1 linked."
                read -p "Press Enter to continue..."
                ;;
            4)
                echo "Creating symbolic link for Neovim config 2..."
                rm -rf ~/.config/nvim ~/.local/share/nvim
                mkdir -p ~/.config/nvim
                ln -s "/ms1/asset/linux/neovim/init2.lua" ~/.config/nvim/init.lua
                echo "Neovim config 2 linked."
                read -p "Press Enter to continue..."
                ;;
            5)
                echo "Notepad++ is Windows-specific. Consider alternatives like Neovim, VSCode, or other Linux text editors."
                echo "For themes, you would typically follow the theme's installation instructions for your chosen editor."
                read -p "Press Enter to continue..."
                ;;
            6)
                echo "PotPlayer is a Windows media player. Registering .reg files is Windows-specific."
                echo "Consider Linux media players like VLC, MPV, or SMPlayer."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Clone Projects submenu
clone_projects_menu() {
    while true; do
        clear
        echo "========================================"
        echo "          Clone Projects Menu           "
        echo "========================================"
        echo "  1) Clone ms1"
        echo "  2) Clone ms2"
        echo "  3) Clone ms3"
        echo "  0) Back to Main Menu"
        echo "----------------------------------------"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Cloning ms1 to /opt/ms1 (requires sudo for /opt)..."
                sudo git clone https://github.com/nahid6970/ms1 /opt/ms1
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Cloning ms2 to /opt/ms2 (requires sudo for /opt)..."
                sudo git clone https://github.com/nahid6970/ms2 /opt/ms2
                read -p "Press Enter to continue..."
                ;;
            3)
                echo "Cloning ms3 to /opt/ms3 (requires sudo for /opt)..."
                sudo git clone https://github.com/nahid6970/ms3 /opt/ms3
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Backup & Restore submenu
backup_restore_menu() {
    while true; do
        clear
        echo "========================================"
        echo "         Backup & Restore Menu          "
        echo "========================================"
        echo "  1) Decrypt rclone.conf & Move (Not Implemented)"
        echo "  2) msBackups [rs] (Not Implemented)"
        echo "  3) msBackups [bk] (Not Implemented)"
        echo "  4) Nilesoft NSS [bk] (Windows-specific)"
        echo "  5) Song [rclone] [bk]"
        echo "  0) Back to Main Menu"
        echo "----------------------------------------"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "This feature is not implemented in the original C# program and is highly specific to your setup."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "This feature is not implemented in the original C# program and is highly specific to your setup."
                read -p "Press Enter to continue..."
                ;;
            3)
                echo "This feature is not implemented in the original C# program and is highly specific to your setup."
                read -p "Press Enter to continue..."
                ;;
            4)
                echo "Nilesoft Shell is a Windows-specific tool. No direct Linux equivalent for backing up its configuration."
                read -p "Press Enter to continue..."
                ;;
            5)
                echo "Running rclone sync for song backup..."
                # Adjust paths as per your Linux setup
                rclone sync ~/song/ google_drive_remote:/song/ -P --check-first --transfers=1 --track-renames --fast-list
                echo "rclone sync command executed. Please ensure 'google_drive_remote' is configured in your rclone."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Port Management submenu
port_management_menu() {
    while true; do
        clear
        echo "========================================"
        echo "         Port Management Menu           "
        echo "========================================"
        echo "  1) Allow Port 22 (SSH)"
        echo "  2) Allow Port 5000"
        echo "  3) Allow Port 5001"
        echo "  4) Allow Port 5002"
        echo "  0) Back to Main Menu"
        echo "----------------------------------------"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Allowing incoming TCP traffic on port 22 (SSH)..."
                echo "Using UFW (Uncomplicated Firewall). If UFW is not installed, use iptables."
                echo "  - sudo pacman -S ufw"
                echo "  - sudo ufw enable"
                sudo ufw allow 22/tcp
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Allowing incoming TCP traffic on port 5000..."
                sudo ufw allow 5000/tcp
                read -p "Press Enter to continue..."
                ;;
            3)
                echo "Allowing incoming TCP traffic on port 5001..."
                sudo ufw allow 5001/tcp
                read -p "Press Enter to continue..."
                ;;
            4)
                echo "Allowing incoming TCP traffic on port 5002..."
                sudo ufw allow 5002/tcp
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Function to handle Symbolic Links submenu
symbolic_links_menu() {
    while true; do
        clear
        echo "========================================"
        echo "        Symbolic Links Menu             "
        echo "========================================"
        echo "  1) Komorebi (Windows-specific)"
        echo "  2) Reference.py"
        echo "  3) PowerShell Profile"
        echo "  4) Prowlarr (Windows-specific install)"
        echo "  5) Radarr (Windows-specific install)"
        echo "  6) RssGuard Config/Database"
        echo "  7) Sonarr (Windows-specific install)"
        echo "  8) Terminal Profile (Windows-specific)"
        echo "  9) VSCode Configs"
        echo "  0) Back to Main Menu"
        echo "----------------------------------------"
        read -p "Enter your choice: " choice
        case $choice in
            1)
                echo "Komorebi is a Windows tiling window manager. No direct Linux equivalent for this setup."
                echo "Consider i3, Sway, AwesomeWM, or other Linux tiling window managers."
                read -p "Press Enter to continue..."
                ;;
            2)
                echo "Creating symbolic link for Reference.py..."
                # Adjust path for your Python installation on Arch
                sudo ln -sf "/ms1/Reference.py" "$(python -c 'import sys; print(sys.prefix)')/lib/python*/site-packages/Reference.py"
                echo "Symbolic link for Reference.py created. Adjust target path if needed."
                read -p "Press Enter to continue..."
                ;;
            3)
                echo "Creating symbolic link for PowerShell Profile..."
                # Adjust path for your PowerShell profile on Linux
                mkdir -p ~/.config/powershell
                ln -sf "/ms1/asset/Powershell/Microsoft.PowerShell_profile.ps1" ~/.config/powershell/Microsoft.PowerShell_profile.ps1
                echo "Symbolic link for PowerShell profile created."
                read -p "Press Enter to continue..."
                ;;
            4)
                echo "Prowlarr installation via Winget is Windows-specific. On Linux, you would typically install it via Docker or a package manager."
                echo "Manual restore required message is from original C#."
                read -p "Press Enter to continue..."
                ;;
            5)
                echo "Radarr installation via Winget is Windows-specific. On Linux, you would typically install it via Docker or a package manager."
                echo "Manual restore required message is from original C#."
                read -p "Press Enter to continue..."
                ;;
            6)
                echo "Creating symbolic links for RssGuard config and database..."
                # Adjust paths based on your RssGuard installation and backup location
                killall rssguard 2>/dev/null
                rm -rf ~/.config/rssguard/data4/database ~/.config/rssguard/data4/config
                mkdir -p ~/.config/rssguard/data4
                ln -sf "/msBackups/@mklink/rssguard/config" ~/.config/rssguard/data4/config
                ln -sf "/msBackups/@mklink/rssguard/database" ~/.config/rssguard/data4/database
                echo "Symbolic links for RssGuard created."
                read -p "Press Enter to continue..."
                ;;
            7)
                echo "Sonarr installation via Winget is Windows-specific. On Linux, you would typically install it via Docker or a package manager."
                echo "Manual restore required message is from original C#."
                read -p "Press Enter to continue..."
                ;;
            8)
                echo "Windows Terminal profile linking is Windows-specific. Linux terminals have different configuration files (e.g., ~/.bashrc, ~/.zshrc, ~/.config/alacritty/alacritty.yml)."
                read -p "Press Enter to continue..."
                ;;
            9)
                echo "Creating symbolic links for VSCode configs..."
                # Adjust paths based on your VSCode installation and config location
                mkdir -p ~/.config/Code/User
                ln -sf "/ms1/asset/vscode/keybindings.json" ~/.config/Code/User/keybindings.json
                ln -sf "/ms1/asset/vscode/settings.json" ~/.config/Code/User/settings.json
                echo "Symbolic links for VSCode configs created."
                read -p "Press Enter to continue..."
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid choice. Please try again."
                read -p "Press Enter to continue..."
                ;;
        esac
    done
}

# Main loop
while true; do
    display_menu
    read -p "Enter your choice: " main_choice
    case $main_choice in
        1)
            initial_setup_menu
            ;;
        2)
            application_setup_menu
            ;;
        3)
            clone_projects_menu
            ;;
        4)
            backup_restore_menu
            ;;
        5)
            port_management_menu
            ;;
        6)
            symbolic_links_menu
            ;;
        7)
            clear
            echo "========================================"
            echo "        Github Projects Menu            "
            echo "========================================"
            echo "These projects are primarily PowerShell scripts for Windows system management."
            echo "They do not have direct Linux equivalents."
            echo "  - Microsoft Activation Scripts (MAS)"
            echo "  - ChrisTitus WinUtility"
            echo "  - WIMUtil"
            echo "  - AppControl Manager"
            echo "  - Harden Windows Security Using GUI"
            echo "  - WIMUtil"
            echo "  - AppControl Manager"
            echo "  - Harden Windows Security Using GUI"
            echo "  - Winhance"
            echo "----------------------------------------"
            read -p "Press Enter to return to Main Menu..."
            ;;
        0)
            echo "Exiting. Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            read -p "Press Enter to continue..."
            ;;
    esac
done
