#!/bin/bash

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
INSTALL_DISK="/dev/sda"    # Set the installation disk here (example: /dev/sda)
HOSTNAME="archlinux"       # Default hostname
AUR_HELPER="yay"           # AUR helper (yay or paru)
USERNAME=""
PASSWORD=""

# Functions

# Function to setup username and password
setup_user_password() {
    clear
    echo -e "${CYAN}Setting up username and password...${NC}"
    read -p "Enter new username: " USERNAME
    read -sp "Enter password for $USERNAME: " PASSWORD
    echo
    echo -e "${GREEN}Username and password saved.${NC}"
}

# Function to set up the disk and partitions
setup_disk() {
    clear
    echo -e "${CYAN}Setting up disk partitioning...${NC}"
    # Create partition table
    parted $INSTALL_DISK mklabel gpt
    parted $INSTALL_DISK mkpart primary fat32 1MiB 512MiB
    parted $INSTALL_DISK set 1 esp on
    parted $INSTALL_DISK mkpart primary ext4 512MiB 100%

    # Format partitions
    mkfs.fat -F32 ${INSTALL_DISK}1
    mkfs.ext4 ${INSTALL_DISK}2

    # Mount partitions
    mount ${INSTALL_DISK}2 /mnt
    mkdir /mnt/boot
    mount ${INSTALL_DISK}1 /mnt/boot

    echo -e "${GREEN}Disk setup completed.${NC}"
}

# Function to install the base system
install_base_system() {
    clear
    echo -e "${CYAN}Installing base system...${NC}"
    timedatectl set-ntp true

    pacstrap /mnt base linux linux-firmware nano sudo networkmanager git

    # Generate fstab
    genfstab -U /mnt >> /mnt/etc/fstab

    echo -e "${GREEN}Base system installed.${NC}"
}

# Function to set up the fastest mirrors
setup_mirrors() {
    clear
    echo -e "${CYAN}Selecting the fastest mirrors...${NC}"

    # Install reflector if it's not already installed
    pacman -Sy --noconfirm reflector

    # Use reflector to select the fastest mirrors (up to 5 of the most recent ones)
    reflector --country Bangladesh --sort rate --latest 5 --save /etc/pacman.d/mirrorlist

    # Alternatively, uncomment the line below to use 6 mirrors
    # reflector --country Bangladesh --sort rate --latest 6 --save /etc/pacman.d/mirrorlist

    # Inform the user that the mirrors have been updated
    echo -e "${GREEN}Mirrors have been updated.${NC}"
}

# Function to prepare chroot environment
prepare_chroot() {
    clear
    echo -e "${CYAN}Preparing chroot environment...${NC}"

    # Bind mount /dev, /proc, and /sys to /mnt
    mount --bind /dev /mnt/dev
    mount --bind /proc /mnt/proc
    mount --bind /sys /mnt/sys
}

# Function to configure the system in chroot
configure_system() {
    clear
    echo -e "${CYAN}Configuring system in chroot...${NC}"

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
    "

    echo -e "${GREEN}System configured.${NC}"
}

# Function to install GRUB bootloader
install_grub() {
    clear
    echo -e "${CYAN}Installing GRUB bootloader...${NC}"
    
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm grub efibootmgr
        mkdir -p /boot/EFI
        mount ${INSTALL_DISK}1 /boot/EFI
        grub-install --target=x86_64-efi --efi-directory=/boot/EFI --bootloader-id=GRUB
        grub-mkconfig -o /boot/grub/grub.cfg
    "

    echo -e "${GREEN}GRUB bootloader installed.${NC}"
}

# Function to install the chosen desktop environment (KDE, GNOME, XFCE)
install_desktop_environment() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    read -p "Enter the number (1, 2, or 3): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing KDE Plasma...${NC}"
            arch-chroot /mnt /bin/bash -c "
                pacman -Sy --noconfirm plasma sddm konsole dolphin
                systemctl enable sddm
            "
            echo -e "${GREEN}KDE Plasma installation complete.${NC}"
            ;;
        2)
            echo -e "${GREEN}Installing GNOME...${NC}"
            arch-chroot /mnt /bin/bash -c "
                pacman -Sy --noconfirm gnome gnome-tweaks gnome-terminal
                systemctl enable gdm
            "
            echo -e "${GREEN}GNOME installation complete.${NC}"
            ;;
        3)
            echo -e "${GREEN}Installing XFCE...${NC}"
            arch-chroot /mnt /bin/bash -c "
                pacman -Sy --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
                systemctl enable lightdm
            "
            echo -e "${GREEN}XFCE installation complete.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac
}

# Main function to orchestrate the install
main() {
    setup_user_password
    setup_disk
    setup_mirrors   # Move this before base system installation
    install_base_system
    prepare_chroot
    configure_system
    install_grub
    install_desktop_environment
    echo -e "${GREEN}Installation Complete! Reboot now.${NC}"
}

# Run the main function
main
