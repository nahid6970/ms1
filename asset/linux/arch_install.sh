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
INSTALL_DISK="/dev/sda"   # Change this if needed
HOSTNAME="archlinux"
USERNAME=""
PASSWORD=""
TIMEZONE="Asia/Kolkata"    # Change your timezone if needed
LOCALE="en_US.UTF-8 UTF-8"

# Setup Username and Password
setup_user_password() {
    clear
    echo -e "${CYAN}Setting up Username and Password...${NC}"
    read -p "Enter new username: " USERNAME
    read -sp "Enter password for $USERNAME: " PASSWORD
    echo
    echo -e "${GREEN}✔ Username and password saved.${NC}"
}

# Partition Disk and Install Base System
install_base_system() {
    clear
    echo -e "${CYAN}Installing Base System...${NC}"
    timedatectl set-ntp true

    parted $INSTALL_DISK --script mklabel gpt
    parted $INSTALL_DISK --script mkpart ESP fat32 1MiB 512MiB
    parted $INSTALL_DISK --script set 1 esp on
    parted $INSTALL_DISK --script mkpart primary ext4 512MiB 100%

    mkfs.fat -F32 "${INSTALL_DISK}1"
    mkfs.ext4 "${INSTALL_DISK}2"

    mount "${INSTALL_DISK}2" /mnt
    mkdir /mnt/boot
    mount "${INSTALL_DISK}1" /mnt/boot

    pacstrap /mnt base linux linux-firmware vim nano sudo networkmanager grub efibootmgr git

    genfstab -U /mnt >> /mnt/etc/fstab

    echo -e "${GREEN}✔ Base System Installed.${NC}"
}

# Configure System
configure_system() {
    clear
    echo -e "${CYAN}Configuring System...${NC}"
    arch-chroot /mnt /bin/bash << EOF
ln -sf /usr/share/zoneinfo/$TIMEZONE /etc/localtime
hwclock --systohc

echo "$LOCALE" > /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

echo "$HOSTNAME" > /etc/hostname
cat << HOSTS > /etc/hosts
127.0.0.1 localhost
::1       localhost
127.0.1.1 $HOSTNAME.localdomain $HOSTNAME
HOSTS

useradd -mG wheel,audio,video,storage,optical -s /bin/bash $USERNAME
echo "$USERNAME:$PASSWORD" | chpasswd
echo "root:$PASSWORD" | chpasswd

sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

systemctl enable NetworkManager

grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=Arch
grub-mkconfig -o /boot/grub/grub.cfg
EOF
    echo -e "${GREEN}✔ System Configured.${NC}"
}

# Install Kernel and Microcode
install_kernel_microcode() {
    clear
    echo -e "${CYAN}Installing Kernel and Microcode...${NC}"
    arch-chroot /mnt pacman -Sy --noconfirm intel-ucode # or amd-ucode if AMD CPU
    echo -e "${GREEN}✔ Kernel and Microcode Installed.${NC}"
}

# Install Basic Applications
install_basic_apps() {
    clear
    echo -e "${CYAN}Installing Basic Applications...${NC}"
    arch-chroot /mnt pacman -Sy --noconfirm firefox neofetch htop zip unzip p7zip
    echo -e "${GREEN}✔ Basic Applications Installed.${NC}"
}

# Enable Services
enable_services() {
    clear
    echo -e "${CYAN}Enabling Essential Services...${NC}"
    arch-chroot /mnt systemctl enable NetworkManager
    echo -e "${GREEN}✔ Services Enabled.${NC}"
}

# Finalize Installation
finalize_installation() {
    clear
    echo -e "${GREEN}Finalizing Installation...${NC}"
    umount -R /mnt
    echo -e "${MAGENTA}✅ Installation Complete! You can reboot now.${NC}"
}

# Close Script
close_script() {
    clear
    echo -e "${RED}Closing Script...${NC}"
    exit 0
}

# Exit Script
exit_script() {
    clear
    echo -e "${RED}Exiting...${NC}"
    exit 0
}

# Menu Items
menu_items=(
    " 1: Setup Username and Password:   setup_user_password    :$CYAN"
    " 2: Install Base System:           install_base_system    :$BLUE"
    " 3: Configure System:              configure_system       :$GREEN"
    " 4: Install Kernel and Microcode:  install_kernel_microcode:$MAGENTA"
    " 5: Install Basic Apps:            install_basic_apps     :$BLUE"
    " 6: Enable Services:               enable_services        :$GREEN"
    " 7: Finalize Installation:         finalize_installation  :$MAGENTA"
    " c: Close Script:                  close_script           :$RED"
    " e: Exit:                          exit_script            :$RED"
)

# Main Menu Loop
while true; do
    echo ""
    echo -e "${YELLOW}🌟 Select an Option:${NC}"

    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description function color <<< "$item"
        echo -e "${color}$number. $description${NC}"
    done

    echo ""
    read -p "Enter choice: " choice

    if [ "$choice" == "c" ]; then
        close_script
    elif [ "$choice" == "e" ]; then
        exit_script
    fi

    valid_choice=false
    for item in "${menu_items[@]}"; do
        IFS=":" read -r number description function color <<< "$item"
        if [[ "$choice" == "$number" ]]; then
            valid_choice=true
            IFS=" " read -r -a function_array <<< "$function"
            for func in "${function_array[@]}"; do
                $func
            done
            break
        fi
    done

    if [ "$valid_choice" = false ]; then
        echo -e "${RED}Invalid Option. Please Try Again.${NC}"
    fi
done
