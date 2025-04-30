#!/bin/bash

# --- Configuration ---
hostname="myarch"
timezone="Asia/Dhaka" # Setting timezone to your current location (Dhaka)
locale="en_US.UTF-8"
keymap="us"
username="nahid"
password="your_password" # REPLACE WITH A STRONG PASSWORD
extra_packages="vim git networkmanager wpa_supplicant dialog"
bootloader="grub" # Options: grub, systemd-boot
disk="" # Will be determined dynamically
efi_size="+512M" # Recommended size for EFI partition
root_size="0"    # Remaining space for root partition
# --- End Configuration ---

set -e

echo "Starting Arch Linux installation - $(date)"
echo "------------------------------------"

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root. Please use sudo."
  exit 1
fi

# Update system clock
echo "Updating system clock..."
timedatectl set-ntp true

# Identify available disks
echo "Available disks:"
lsblk -d

# Prompt for the target disk
while [[ -z "$disk" ]]; do
  read -p "Enter the disk to install Arch Linux on (e.g., /dev/sda): " disk
  if [[ -b "$disk" ]]; then
    echo "Selected disk: $disk"
  else
    echo "Error: Invalid disk specified. Please try again."
  fi
done

# Partitioning
# Partitioning
echo "Partitioning the disk: $disk"
echo "WARNING: This will erase all existing data on $disk."
read -p "Are you sure you want to proceed? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborting installation."
  exit 1
fi

echo "Creating GPT partition table..."
parted -s "$disk" mklabel gpt

echo "Creating EFI partition (start=0%, size=512MB)..."
parted -s "$disk" mkpart ESP fat32 0% 512MB
parted -s "$disk" set 1 esp on

echo "Creating root partition (start=512MB, end=100%)..."
parted -s "$disk" mkpart primary ext4 512MB 100%

efi_part="${disk}1"
root_part="${disk}2"

echo "Formatting partitions..."
mkfs.fat -F32 "$efi_part"
mkfs.ext4 "$root_part"

# Mount filesystems
echo "Mounting filesystems..."
mount "$root_part" /mnt
mkdir -p /mnt/boot/efi
mount "$efi_part" /mnt/boot/efi

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

# test 2