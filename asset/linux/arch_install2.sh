#!/bin/bash

# Define colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
INSTALL_DISK="/dev/sda"
HOSTNAME="archlinux"
USERNAME=""
PASSWORD=""
COMPLETED_STEPS=()

# Functions

show_menu() {
    clear
    echo -e "${CYAN}Arch Linux Installer Menu${NC}"
    echo -e "============================"
    echo -e "1) ${GREEN}Setup User & Password${NC} ${COMPLETED_STEPS[0]:-}"
    echo -e "2) ${GREEN}Partition Disk${NC} ${COMPLETED_STEPS[1]:-}"
    echo -e "3) ${GREEN}Install Base System${NC} ${COMPLETED_STEPS[2]:-}"
    echo -e "4) ${GREEN}Configure System${NC} ${COMPLETED_STEPS[3]:-}"
    echo -e "5) ${GREEN}Install Yay AUR Helper${NC} ${COMPLETED_STEPS[4]:-}"
    echo -e "6) ${GREEN}Install Bootloader${NC} ${COMPLETED_STEPS[5]:-}"
    echo -e "7) ${GREEN}Install Desktop Environment${NC} ${COMPLETED_STEPS[6]:-}"
    echo -e "8) ${GREEN}Show Installation Summary${NC}"
    echo -e "9) ${RED}Exit Installer${NC}"
    echo -e "0) ${YELLOW}Run ALL Steps Automatically${NC}"
    echo -e "\nCurrent Settings:"
    echo -e " - Disk: ${INSTALL_DISK}"
    echo -e " - Hostname: ${HOSTNAME}"
    echo -e " - Username: ${USERNAME:-Not set}"
    echo -e "\nSelect an option (1-9, 0 for auto): "
}

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
        COMPLETED_STEPS[0]="(✓)"
        read -n 1 -s -r -p "Press any key to continue..."
    fi
}

setup_disk() {
    clear
    echo -e "${CYAN}Current disk layout for $INSTALL_DISK:${NC}"
    lsblk $INSTALL_DISK
    echo -e "\n${RED}WARNING: This will erase ALL data on $INSTALL_DISK${NC}"
    read -p "Are you sure you want to continue? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}Setting up disk partitioning...${NC}"
        umount -R /mnt 2>/dev/null || true
        
        parted -s $INSTALL_DISK mklabel gpt
        parted -s $INSTALL_DISK mkpart primary fat32 1MiB 512MiB
        parted -s $INSTALL_DISK set 1 esp on
        parted -s $INSTALL_DISK mkpart primary ext4 512MiB 100%

        mkfs.fat -F32 ${INSTALL_DISK}1
        mkfs.ext4 -F ${INSTALL_DISK}2

        mount ${INSTALL_DISK}2 /mnt
        mkdir -p /mnt/boot
        mount ${INSTALL_DISK}1 /mnt/boot

        echo -e "${GREEN}Disk setup completed.${NC}"
        COMPLETED_STEPS[1]="(✓)"
    else
        echo -e "${YELLOW}Disk partitioning cancelled.${NC}"
    fi
    read -n 1 -s -r -p "Press any key to continue..."
}

install_base_system() {
    clear
    if [ ! -d /mnt/boot ]; then
        echo -e "${RED}Error: Disk not mounted. Please partition disk first.${NC}"
        read -n 1 -s -r -p "Press any key to continue..."
        return
    fi
    
    echo -e "${CYAN}Installing base system...${NC}"
    timedatectl set-ntp true

    CPU_TYPE=$(grep -m 1 -o 'GenuineIntel\|AuthenticAMD' /proc/cpuinfo)
    MICROCODE=""
    if [ "$CPU_TYPE" == "GenuineIntel" ]; then
        MICROCODE="intel-ucode"
    elif [ "$CPU_TYPE" == "AuthenticAMD" ]; then
        MICROCODE="amd-ucode"
    fi

    pacstrap /mnt base linux linux-firmware $MICROCODE nano sudo networkmanager base-devel git dhcpcd
    genfstab -U /mnt >> /mnt/etc/fstab

    echo -e "${GREEN}Base system installed.${NC}"
    COMPLETED_STEPS[2]="(✓)"
    read -n 1 -s -r -p "Press any key to continue..."
}

configure_system() {
    clear
    if [ ! -f /mnt/etc/fstab ]; then
        echo -e "${RED}Error: Base system not installed. Please install base system first.${NC}"
        read -n 1 -s -r -p "Press any key to continue..."
        return
    fi
    
    echo -e "${CYAN}Configuring system...${NC}"
    mount --bind /dev /mnt/dev
    mount --bind /proc /mnt/proc
    mount --bind /sys /mnt/sys

    arch-chroot /mnt /bin/bash -c "
        ln -sf /usr/share/zoneinfo/UTC /etc/localtime
        hwclock --systohc
        echo 'en_US.UTF-8 UTF-8' > /etc/locale.gen
        locale-gen
        echo 'LANG=en_US.UTF-8' > /etc/locale.conf
        echo '$HOSTNAME' > /etc/hostname
        echo '127.0.0.1 localhost' > /etc/hosts
        echo '::1       localhost' >> /etc/hosts
        echo '127.0.1.1 $HOSTNAME.localdomain $HOSTNAME' >> /etc/hosts
        systemctl enable NetworkManager
        systemctl enable dhcpcd
        mkinitcpio -P
    "

    if [ -n "$USERNAME" ]; then
        arch-chroot /mnt /bin/bash -c "
            useradd -m -G wheel,audio,video,storage,optical $USERNAME
            echo '$USERNAME:$PASSWORD' | chpasswd
            sed -i 's/^# %wheel ALL=(ALL) ALL/%wheel ALL=(ALL) ALL/' /etc/sudoers
        "
    fi

    echo -e "${GREEN}System configuration complete.${NC}"
    COMPLETED_STEPS[3]="(✓)"
    read -n 1 -s -r -p "Press any key to continue..."
}

install_yay() {
    clear
    if [ -z "$USERNAME" ]; then
        echo -e "${RED}Error: No user created. Please setup user first.${NC}"
        read -n 1 -s -r -p "Press any key to continue..."
        return
    fi
    
    echo -e "${CYAN}Installing Yay AUR helper...${NC}"
    
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm --needed git base-devel
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
    COMPLETED_STEPS[4]="(✓)"
    read -n 1 -s -r -p "Press any key to continue..."
}

install_grub() {
    clear
    if [ ! -d /mnt/boot ]; then
        echo -e "${RED}Error: System not mounted. Please install base system first.${NC}"
        read -n 1 -s -r -p "Press any key to continue..."
        return
    fi
    
    echo -e "${CYAN}Installing GRUB bootloader...${NC}"
    
    arch-chroot /mnt /bin/bash -c "
        pacman -Sy --noconfirm grub efibootmgr os-prober
        grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=GRUB
        grub-mkconfig -o /boot/grub/grub.cfg
    "

    echo -e "${GREEN}GRUB bootloader installed.${NC}"
    COMPLETED_STEPS[5]="(✓)"
    read -n 1 -s -r -p "Press any key to continue..."
}

install_desktop_environment() {
    clear
    if [ ! -d /mnt/boot ]; then
        echo -e "${RED}Error: System not mounted. Please install base system first.${NC}"
        read -n 1 -s -r -p "Press any key to continue..."
        return
    fi
    
    echo -e "${CYAN}Desktop Environment Selection${NC}"
    echo -e "1) KDE Plasma"
    echo -e "2) GNOME"
    echo -e "3) XFCE"
    echo -e "4) None (CLI only)"
    read -p "Enter your choice (1-4): " de_choice

    case $de_choice in
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
    COMPLETED_STEPS[6]="(✓)"
    read -n 1 -s -r -p "Press any key to continue..."
}

show_summary() {
    clear
    echo -e "${CYAN}Installation Summary${NC}"
    echo -e "====================="
    echo -e "Disk: ${INSTALL_DISK}"
    echo -e "Hostname: ${HOSTNAME}"
    echo -e "Username: ${USERNAME:-Not set}"
    echo -e "\nCompleted Steps:"
    for i in "${!COMPLETED_STEPS[@]}"; do
        case $i in
            0) echo -e " - User Setup ${COMPLETED_STEPS[$i]:-✗}";;
            1) echo -e " - Disk Partitioning ${COMPLETED_STEPS[$i]:-✗}";;
            2) echo -e " - Base System ${COMPLETED_STEPS[$i]:-✗}";;
            3) echo -e " - System Configuration ${COMPLETED_STEPS[$i]:-✗}";;
            4) echo -e " - Yay AUR Helper ${COMPLETED_STEPS[$i]:-✗}";;
            5) echo -e " - Bootloader ${COMPLETED_STEPS[$i]:-✗}";;
            6) echo -e " - Desktop Environment ${COMPLETED_STEPS[$i]:-✗}";;
        esac
    done
    
    echo -e "\n${YELLOW}Next Steps:"
    if [[ "${COMPLETED_STEPS[5]}" == "(✓)" ]]; then
        echo -e " - You can now reboot into your new system"
    else
        echo -e " - Complete the remaining installation steps"
    fi
    echo -e "${NC}"
    read -n 1 -s -r -p "Press any key to continue..."
}

run_all() {
    echo -e "${CYAN}Running all installation steps automatically...${NC}"
    setup_user_password
    setup_disk
    install_base_system
    configure_system
    install_yay
    install_grub
    install_desktop_environment
    
    echo -e "${GREEN}All steps completed!${NC}"
    echo -e "\n${YELLOW}You can now reboot into your new Arch Linux system."
    echo -e "Don't forget to remove the installation media.${NC}"
    read -n 1 -s -r -p "Press any key to continue..."
}

# Main loop
while true; do
    show_menu
    read -p "Select an option: " choice
    
    case $choice in
        1) setup_user_password;;
        2) setup_disk;;
        3) install_base_system;;
        4) configure_system;;
        5) install_yay;;
        6) install_grub;;
        7) install_desktop_environment;;
        8) show_summary;;
        9) 
            echo -e "${RED}Exiting installer...${NC}"
            exit 0
            ;;
        0) 
            read -p "Run all steps automatically? (y/N): " confirm
            [[ $confirm =~ ^[Yy]$ ]] && run_all
            ;;
        *) 
            echo -e "${RED}Invalid option. Please try again.${NC}"
            sleep 1
            ;;
    esac
done