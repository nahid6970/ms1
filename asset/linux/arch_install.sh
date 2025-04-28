#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global Variables
INSTALL_DISK="/dev/sda"  # Change if needed
HOSTNAME="archlinux"
USERNAME=""
PASSWORD=""
AUR_HELPER="yay"  # Default aur helper

# Function to setup user and password
setup_user_password() {
    clear
    echo -e "${CYAN}Setting up username and password...${NC}"
    read -p "Enter new username: " USERNAME
    read -sp "Enter password for $USERNAME: " PASSWORD
    echo
    echo -e "${GREEN}Username and password saved.${NC}"
}

# Function to install base system
install_base_system() {
    clear
    echo -e "${CYAN}Installing base system...${NC}"
    timedatectl set-ntp true
    parted $INSTALL_DISK mklabel gpt
    parted $INSTALL_DISK mkpart primary fat32 1MiB 512MiB
    parted $INSTALL_DISK set 1 esp on
    parted $INSTALL_DISK mkpart primary ext4 512MiB 100%

    mkfs.fat -F32 ${INSTALL_DISK}1
    mkfs.ext4 ${INSTALL_DISK}2

    mount ${INSTALL_DISK}2 /mnt
    mkdir /mnt/boot
    mount ${INSTALL_DISK}1 /mnt/boot

    pacstrap /mnt base linux linux-firmware nano sudo networkmanager git

    genfstab -U /mnt >> /mnt/etc/fstab

    arch-chroot /mnt /bin/bash -c "
        ln -sf /usr/share/zoneinfo/UTC /etc/localtime
        hwclock --systohc
        echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen
        locale-gen
        echo 'LANG=en_US.UTF-8' > /etc/locale.conf
        echo $HOSTNAME > /etc/hostname
        echo '127.0.0.1 localhost' >> /etc/hosts
        echo '::1       localhost' >> /etc/hosts
        echo '127.0.1.1 $HOSTNAME.localdomain $HOSTNAME'
        
        useradd -m -G wheel -s /bin/bash $USERNAME
        echo $USERNAME:$PASSWORD | chpasswd
        echo root:$PASSWORD | chpasswd
        sed -i 's/^# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/' /etc/sudoers
        systemctl enable NetworkManager
    "
    echo -e "${GREEN}Base system installed.${NC}"
}

# Function to install AUR helper
install_aur_helper() {
    clear
    echo -e "${CYAN}Installing AUR helper ($AUR_HELPER)...${NC}"
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm base-devel git
        sudo -u $USERNAME bash -c '
            cd ~
            git clone https://aur.archlinux.org/${AUR_HELPER}.git
            cd ${AUR_HELPER}
            makepkg -si --noconfirm
        '
    "
    echo -e "${GREEN}AUR helper installed.${NC}"
}

# Function to select and install desktop environment
install_desktop_environment() {
    clear
    echo -e "${CYAN}Choose Desktop Environment:${NC}"
    echo "1) KDE Plasma"
    echo "2) GNOME"
    echo "3) XFCE"
    echo "4) Sway (Wayland)"
    read -p "Enter number (1-4): " de_choice

    arch-chroot /mnt /bin/bash -c "
        case $de_choice in
            1)
                pacman -Sy --noconfirm plasma kde-applications sddm
                systemctl enable sddm
                ;;
            2)
                pacman -Sy --noconfirm gnome gnome-extra gdm
                systemctl enable gdm
                ;;
            3)
                pacman -Sy --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
                systemctl enable lightdm
                ;;
            4)
                pacman -Sy --noconfirm sway foot waybar
                ;;
            *)
                echo 'Invalid option'
                ;;
        esac
    "
    echo -e "${GREEN}Desktop environment installed.${NC}"
}

# Function to finalize installation
finalize_installation() {
    clear
    echo -e "${GREEN}Finalizing installation...${NC}"
    umount -R /mnt
    echo -e "${MAGENTA}✅ Installation complete! You can reboot now.${NC}"
}

# Function to close script
Close_script() {
    clear
    echo -e "${RED}Closing script...${NC}"
    exit 0
}

# Function to exit script
exit_script() {
    clear
    echo -e "${RED}Exiting...${NC}"
    exit 0
}

# Menu Items
menu_items=(
    "1:Setup Username & Password:     setup_user_password         :$CYAN"
    "2:Install Base System:            install_base_system         :$BLUE"
    "3:Install AUR Helper:             install_aur_helper           :$BLUE"
    "4:Install Desktop Environment:   install_desktop_environment  :$GREEN"
    "5:Finalize Installation:          finalize_installation       :$MAGENTA"
    "c:Close:                          Close_script                 :$RED"
    "e:Exit:                           exit_script                  :$RED"
)

# Main Menu Loop
while true; do
    echo ""
    echo -e "${YELLOW}🌟 Select an option:${NC}"

    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description functions color <<< "$item"
        echo -e "${color}$number. $description${NC}"
    done

    echo ""
    read -p "Enter choice: " choice

    if [ "$choice" == "c" ]; then
        Close_script
    elif [ "$choice" == "e" ]; then
        exit_script
    fi

    valid_choice=false
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description functions color <<< "$item"
        if [[ "$choice" == "$number" ]]; then
            valid_choice=true
            IFS=" " read -r -a function_array <<< "$functions"
            for function in "${function_array[@]}"; do
                $function
            done
            break
        fi
    done

    if [ "$valid_choice" = false ]; then
        echo -e "${RED}Invalid option. Please try again.${NC}"
    fi
done
