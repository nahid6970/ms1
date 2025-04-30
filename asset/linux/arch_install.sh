#!/bin/bash

# curl -fsSL "http://nahid6970.ddns.net" -o os.sh
# chmod +x os.sh
# bash os.sh or sh os.sh


# Define colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Global variables ---
INSTALL_DISK="/dev/sda"   # Change this if needed (example: /dev/vda)
HOSTNAME="archlinux"      # Default hostname
AUR_HELPER="yay"          # Default AUR helper (yay or paru)
USERNAME=""
PASSWORD=""

# --- Functions ---

# Function to setup username/password
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
        echo '127.0.0.1 localhost' > /etc/hosts
        echo '::1       localhost' >> /etc/hosts
        echo '127.0.1.1 $HOSTNAME.localdomain $HOSTNAME' >> /etc/hosts

        pacman -Sy --noconfirm reflector
        reflector --country Bangladesh --latest 5 --sort rate --save /etc/pacman.d/mirrorlist

        useradd -m -G wheel -s /bin/bash $USERNAME
        echo $USERNAME:$PASSWORD | chpasswd
        echo root:$PASSWORD | chpasswd
        sed -i 's/^# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/' /etc/sudoers
        systemctl enable NetworkManager
    "

    echo -e "${GREEN}Base system installed.${NC}"
}


install_aur_helper() {
    clear
    echo -e "${CYAN}Installing AUR helper (${AUR_HELPER})...${NC}"
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

install_kde() {
    clear
    echo -e "${CYAN}Do you want to install KDE Plasma? (y/n)${NC}"
    read -p "Enter your choice: " confirm
    # If no input is given or if 'y' or 'Enter' is pressed, treat it as 'yes'
    if [[ -z "$confirm" || "$confirm" =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Installing KDE Plasma...${NC}"
        arch-chroot /mnt /bin/bash -c "
            pacman -Sy --noconfirm plasma sddm konsole dolphin
            systemctl enable sddm
        "
        echo -e "${GREEN}KDE Plasma installation complete.${NC}"
    elif [[ "$confirm" =~ ^[Nn]$ ]]; then
        echo "KDE Plasma installation cancelled."
    else
        echo "Invalid input. Please enter 'y' for yes or 'n' for no."
    fi
}


install_gnome() {
    echo -e "${GREEN}Installing GNOME...${NC}"
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm gnome gnome-tweaks gnome-terminal
        systemctl enable gdm
    "
    echo -e "${GREEN}GNOME installation complete.${NC}"
}

install_xfce() {
    echo -e "${GREEN}Installing XFCE...${NC}"
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
        systemctl enable lightdm
    "
    echo -e "${GREEN}XFCE installation complete.${NC}"
}

install_sway() {
    echo -e "${GREEN}Installing Sway (Wayland)...${NC}"
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm sway foot
    "
    echo -e "${GREEN}Sway installation complete.${NC}"
}

exit_script() {
    echo -e "${RED}Exiting...${NC}"
    exit 0
}

setup_user_password
install_base_system
# install_aur_helper
# install_kde