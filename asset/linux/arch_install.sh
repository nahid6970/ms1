#!/bin/bash

set -e  # Exit if any command fails

echo "⚡ Starting Arch Linux installation..."

# Ask username and password
read -p "👤 Enter your new username: " username
read -s -p "🔒 Enter your password: " userpass
echo ""

# 1. Set keyboard layout
loadkeys us

# 2. Update system clock
timedatectl set-ntp true

# 3. Install reflector and optimize mirrors
echo "🌏 Setting fastest mirrors (Bangladesh)..."
pacman -Sy --noconfirm reflector
reflector --country Bangladesh --age 12 --sort rate --save /etc/pacman.d/mirrorlist

# 4. Partition the disk (WARNING: this will wipe /dev/sda)
echo "💾 Partitioning /dev/sda..."
(
  echo g    # Create a new empty GPT partition table
  echo n    # New partition
  echo      # Partition number 1
  echo      # First sector (default)
  echo +300M  # 300MB boot partition
  echo t    # Change partition type
  echo 1    # EFI System
  echo n    # New partition
  echo      # Partition number 2
  echo      # First sector (default)
  echo      # Last sector (use rest of disk)
  echo w    # Write changes
) | fdisk /dev/sda

# 5. Format partitions
echo "🧹 Formatting partitions..."
mkfs.fat -F32 /dev/sda1
mkfs.ext4 /dev/sda2

# 6. Mount partitions
echo "📂 Mounting partitions..."
mount /dev/sda2 /mnt
mkdir /mnt/boot
mount /dev/sda1 /mnt/boot

# 7. Install base system
echo "📦 Installing base system..."
pacstrap /mnt base linux linux-firmware vim networkmanager sudo grub efibootmgr

# 8. Generate fstab
echo "🛠 Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

# 9. System configuration inside chroot
echo "🔧 Configuring system inside chroot..."

arch-chroot /mnt /bin/bash <<EOF
# Set timezone
ln -sf /usr/share/zoneinfo/Asia/Dhaka /etc/localtime
hwclock --systohc

# Localization
sed -i 's/^#en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# Hostname
echo "myarch" > /etc/hostname
cat <<HOSTS > /etc/hosts
127.0.0.1 localhost
::1       localhost
127.0.1.1 myarch.localdomain myarch
HOSTS

# Root password
echo "root:$userpass" | chpasswd

# Create user
useradd -m -G wheel -s /bin/bash $username
echo "$username:$userpass" | chpasswd

# Allow sudo for wheel group
sed -i 's/^# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

# Enable NetworkManager
systemctl enable NetworkManager

# Install and configure bootloader
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=Arch
grub-mkconfig -o /boot/grub/grub.cfg

# Install paru (AUR helper)
echo "🌟 Installing paru AUR helper..."

# Install base-devel and git
pacman -Sy --noconfirm base-devel git

# Switch to your user (safe install without root)
sudo -u $username bash <<EOP
cd ~
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si --noconfirm
EOP

echo "✅ paru installed successfully!"

# Ask user for Desktop Environment selection
echo "🎨 Choose your Desktop Environment:"
echo "1) KDE Plasma"
echo "2) GNOME"
echo "3) XFCE"
echo "4) Sway (Wayland)"
read -p "Enter number (1-4): " de_choice

case $de_choice in
  1)
    echo "✨ Installing KDE Plasma..."
    pacman -Sy --noconfirm plasma kde-applications sddm
    systemctl enable sddm
    ;;
  2)
    echo "✨ Installing GNOME..."
    pacman -Sy --noconfirm gnome gnome-extra gdm
    systemctl enable gdm
    ;;
  3)
    echo "✨ Installing XFCE..."
    pacman -Sy --noconfirm xfce4 xfce4-goodies lightdm lightdm-gtk-greeter
    systemctl enable lightdm
    ;;
  4)
    echo "✨ Installing Sway (Wayland)..."
    pacman -Sy --noconfirm sway foot waybar
    # Sway doesn't use display manager, login from tty
    ;;
  *)
    echo "⚠ Invalid choice, skipping Desktop Environment install."
    ;;
esac


EOF

echo "✅ Installation complete! You can reboot now."
echo "⚡ Your user '$username' is ready with sudo access!"
