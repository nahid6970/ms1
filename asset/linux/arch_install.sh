#!/bin/bash

# --- Configuration ---
hostname="myarch"
timezone="Asia/Dhaka"
locale="en_US.UTF-8"
keymap="us"
# mirror_region="BD" # Mirror region will be automatically selected
username="nahid"
password="your_password"
extra_packages="vim git networkmanager wpa_supplicant dialog"
bootloader="grub" # Options: grub, systemd-boot
# --- End Configuration ---

set -e

echo "Starting Arch Linux installation..."
echo "------------------------------------"

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root. Please use sudo."
  exit 1
fi

echo "Updating system clock..."
timedatectl set-ntp true

echo "Partitioning the disk (example: /dev/sda - adjust as needed)..."
lsblk
read -p "Enter the disk to partition (e.g., /dev/sda): " disk
sgdisk --new=1:0:+100M --typecode=1:EF00 "$disk"
sgdisk --new=2:0:0 --typecode=2:8300 "$disk"
mkfs.fat -F32 "${disk}1"
mkfs.ext4 "${disk}2"

echo "Mounting filesystems..."
mount "${disk}2" /mnt
mkdir -p /mnt/boot/efi
mount "${disk}1" /mnt/boot/efi

# Select the fastest mirrors
echo "Selecting the fastest mirrors..."
pacman -Sy reflector --noconfirm
reflector --latest 20 --sort rate --save /etc/pacman.d/mirrorlist

# Install base packages
echo "Installing base packages..."
pacstrap /mnt base base-devel linux linux-firmware iputils dhcpcd "$extra_packages"

# Generate fstab
echo "Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

echo "Entering chroot..."
arch-chroot /mnt bash -c "
  echo \"$hostname\" > /etc/hostname
  ln -sf /usr/share/zoneinfo/$timezone /etc/localtime
  hwclock --systohc
  sed -i 's/#$locale UTF-8/\"$locale UTF-8\"/' /etc/locale.gen
  locale-gen
  echo \"LANG=$locale\" > /etc/locale.conf
  echo \"KEYMAP=$keymap\" > /etc/vconsole.conf
  echo \"root:$password\" | chpasswd
  useradd -m -G wheel -s /bin/bash \"$username\"
  echo \"$username:$password\" | chpasswd
  sed -i '/# %wheel ALL=(ALL) ALL/s/^# //g' /etc/sudoers
  
  if [ \"$bootloader\" = \"grub\" ]; then
    pacman -S --noconfirm grub efibootmgr
    grub-install --target=x86_64-efi --bootloader-id=GRUB --efi-directory=/boot/efi
    grub-mkconfig -o /boot/grub/grub.cfg
  elif [ \"$bootloader\" = \"systemd-boot\" ]; then
    bootctl --path=/boot/efi install
    echo \"title Arch Linux\" > /boot/efi/loader/entries/arch.conf
    echo \"linux /vmlinuz-linux\" >> /boot/efi/loader/entries/arch.conf
    echo \"initrd /initramfs-linux.img\" >> /boot/efi/loader/entries/arch.conf
    echo \"options root=$(findmnt -no UUID /) rw\" >> /boot/efi/loader/entries/arch.conf
    echo \"default arch\" > /boot/efi/loader/loader.conf
  else
    echo \"Error: Invalid bootloader selected.\"
  fi
  
  systemctl enable NetworkManager
"

echo "Unmounting filesystems..."
umount -R /mnt

echo "Installation complete! Reboot your system."
echo "------------------------------------"