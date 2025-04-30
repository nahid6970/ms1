#!/bin/bash

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
INSTALL_DISK="/dev/sda"       # Set the installation disk here (example: /dev/sda)
HOSTNAME="archlinux"         # Default hostname
USERNAME=""
PASSWORD=""
ROOT_PASSWORD=""

# Functions

# Function to setup root password
setup_root_password() {
    clear
    echo -e "${CYAN}Setting up root password...${NC}"
    read -sp "Enter root password: " ROOT_PASSWORD
    echo
    read -sp "Confirm root password: " ROOT_PASSWORD_CONFIRM
    echo

    if [ "$ROOT_PASSWORD" != "$ROOT_PASSWORD_CONFIRM" ]; then
        echo -e "${RED}Passwords do not match! Please try again.${NC}"
        setup_root_password
    else
        echo -e "${GREEN}Root password saved.${NC}"
    fi
}


# Function to setup username and password
setup_user_password() {
    clear
    echo -e "${CYAN}Setting up username and password...${NC}"
    read -p "Enter new username: " USERNAME
    read -sp "Enter password for $USERNAME: " PASSWORD
    echo
    read -sp "Confirm password: " PASSWORD_CONFIRM
    echo
    
    if [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; then
        echo -e "${RED}Passwords do not match! Please try again.${NC}"
        setup_user_password
    else
        echo -e "${GREEN}Username and password saved.${NC}"
    fi
}

# Function to set up the disk and partitions
setup_disk() {
    clear
    echo -e "${CYAN}Setting up disk partitioning...${NC}"
    
    # Unmount any existing partitions
    umount -R /mnt 2>/dev/null || true
    
    # Create partition table
    parted -s $INSTALL_DISK mklabel gpt
    parted -s $INSTALL_DISK mkpart primary fat32 1MiB 512MiB
    parted -s $INSTALL_DISK set 1 esp on
    parted -s $INSTALL_DISK mkpart primary ext4 512MiB 100%

    # Format partitions
    mkfs.fat -F32 ${INSTALL_DISK}1
    mkfs.ext4 -F ${INSTALL_DISK}2

    # Mount partitions
    mount ${INSTALL_DISK}2 /mnt
    mkdir -p /mnt/boot
    mount ${INSTALL_DISK}1 /mnt/boot

    echo -e "${GREEN}Disk setup completed.${NC}"
}

setup_mirrors() {
    clear
    echo -e "${CYAN}Selecting the fastest mirrors...${NC}"
    # Install reflector if it's not already installed
    pacman -Sy --noconfirm reflector
    # Define XeonBD mirror entries
    xeonbd_mirrors=$(cat <<EOF
Server = http://mirror.xeonbd.com/archlinux/\$repo/os/\$arch
Server = https://mirror.xeonbd.com/archlinux/\$repo/os/\$arch
EOF
)
    # Create a temporary file for the new mirrorlist
    tmpfile=$(mktemp)
    # Write the XeonBD mirrors at the top of the temp file
    echo "$xeonbd_mirrors" > "$tmpfile"
    # Use reflector to get the 5 fastest mirrors in Bangladesh (excluding XeonBD to avoid duplicates)
    reflector --country Bangladesh --sort rate --latest 5 >> "$tmpfile"
    # Move the temp file to the actual mirrorlist location
    mv "$tmpfile" /etc/pacman.d/mirrorlist
    echo -e "${GREEN}Mirrors have been updated with XeonBD at the top.${NC}"
}

# Function to install the base system
install_base_system() {
    clear
    echo -e "${CYAN}Installing base system...${NC}"
    timedatectl set-ntp true

    # Detect CPU for microcode
    CPU_TYPE=$(grep -m 1 -o 'GenuineIntel\|AuthenticAMD' /proc/cpuinfo)
    MICROCODE=""
    if [ "$CPU_TYPE" == "GenuineIntel" ]; then
        MICROCODE="intel-ucode"
    elif [ "$CPU_TYPE" == "AuthenticAMD" ]; then
        MICROCODE="amd-ucode"
    fi

    pacstrap /mnt base linux linux-firmware $MICROCODE nano sudo networkmanager base-devel git dhcpcd

    # Generate fstab
    genfstab -U /mnt >> /mnt/etc/fstab

    echo -e "${GREEN}Base system installed.${NC}"
}

# Function to prepare chroot environment
prepare_chroot() {
    clear
    echo -e "${CYAN}Preparing chroot environment...${NC}"
    mount --bind /dev /mnt/dev
    mount --bind /proc /mnt/proc
    mount --bind /sys /mnt/sys
}

# Function to create user
create_user() {
    clear
    echo -e "${CYAN}Creating user $USERNAME...${NC}"
    arch-chroot /mnt /bin/bash -c "
        useradd -m -G wheel,audio,video,storage,optical $USERNAME
        echo '$USERNAME:$PASSWORD' | chpasswd
        echo 'root:$ROOT_PASSWORD' | chpasswd # Set root password here
        sed -i 's/^# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/' /etc/sudoers
    "
    echo -e "${GREEN}User created successfully.${NC}"
}

# Function to install Yay AUR helper
install_yay() {
    clear
    echo -e "${CYAN}Installing Yay AUR helper...${NC}"
    
    # Install dependencies if not already installed
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm --needed git base-devel
    "
    
    # Install yay as the user
    arch-chroot /mnt /bin/bash -c "
        sudo -u $USERNAME bash -c '
            cd /home/$USERNAME
            git clone https://aur.archlinux.org/yay.git
            cd yay
            makepkg -si --noconfirm
            cd ..
            rm -rf yay
        '
    "
    
    echo -e "${GREEN}Yay AUR helper installed successfully.${NC}"
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
        echo '$HOSTNAME' > /etc/hostname
        echo '127.0.0.1 localhost' > /etc/hosts
        echo '::1         localhost' >> /etc/hosts
        echo '127.0.1.1 $HOSTNAME.localdomain $HOSTNAME' >> /etc/hosts
        
        # Enable essential services
        systemctl enable NetworkManager
        systemctl enable dhcpcd
        
        # Regenerate initramfs
        mkinitcpio -P
    "

    echo -e "${GREEN}System configured.${NC}"
}

# Function to install GRUB bootloader
install_grub() {
    clear
    echo -e "${CYAN}Installing GRUB bootloader...${NC}"
    
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm grub efibootmgr os-prober
        grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
        grub-mkconfig -o /boot/grub/grub.cfg
    "

    echo -e "${GREEN}GRUB bootloader installed.${NC}"
}

# Function to install the chosen desktop environment
install_desktop_environment() {
    clear
    echo -e "${CYAN}Which desktop environment would you like to install?${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    echo -e "4) None (CLI only)"
    read -p "Enter the number (1-4): " DE_CHOICE

    case $DE_CHOICE in
        1)
            echo -e "${GREEN}Installing KDE Plasma...${NC}"
            arch-chroot /mnt /bin/bash -c "
                pacman -Sy --noconfirm plasma sddm konsole dolphin plasma-wayland-session
                systemctl enable sddm
            "
            ;;
        2)
            echo -e "${GREEN}Installing GNOME...${NC}"
            arch-chroot /mnt /bin/bash -c "
                pacman -Sy --noconfirm gnome gnome-tweaks gnome-terminal gdm
                systemctl enable gdm
            "
            ;;
        3)
            echo -e "${GREEN}Installing XFCE...${NC}"
            arch-chroot /mnt /bin/bash -c "
                pacman -Sy --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
                systemctl enable lightdm
            "
            ;;
        4)
            echo -e "${YELLOW}Skipping desktop environment installation.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid choice. No desktop environment installed.${NC}"
            ;;
    esac
    
    echo -e "${GREEN}Desktop environment installation complete.${NC}"
}


# Function to download the important sh file and update .bashrc
setup_important_script() {
    clear
    echo -e "${CYAN}Downloading and setting up important script...${NC}"
    # Download the script
    curl -fsSL https://raw.githubusercontent.com/nahid6970/ms1/refs/heads/main/asset/linux/archos.sh -o /home/$USERNAME/archos.sh
    # Make the script executable
    chmod +x /home/$USERNAME/archos.sh
    # Add the command to .bashrc to run the script using 'os'
    echo "alias os='/home/$USERNAME/archos.sh'" >> /home/$USERNAME/.bashrc
    echo -e "${GREEN}Script downloaded and setup completed.${NC}"
}

# Main function to orchestrate the install
main() {
    # Verify boot mode
    if [ ! -d /sys/firmware/efi ]; then
        echo -e "${RED}This script only supports UEFI boot mode.${NC}"
        exit 1
    fi

    setup_root_password # Get the root password
    setup_user_password
    setup_disk
    setup_mirrors
    install_base_system
    prepare_chroot
    configure_system
    create_user
    # install_yay
    install_grub
    install_desktop_environment
    # setup_important_script
    
    # Cleanup
    umount -R /mnt
    
    echo -e "${GREEN}Installation Complete! You can now reboot the system.${NC}"
    echo -e "${YELLOW}Don't forget to:"
    echo -e "1. Remove the installation media"
    echo -e "2. Login as your new user ($USERNAME) or root"
    echo -e "3. Set up your system further as needed${NC}"
}

# Run the main function
main
