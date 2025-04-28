#!/bin/bash

set -e

# 🛜 Update mirrorlist
echo "🔄 Setting fastest mirrors..."
reflector --country Bangladesh --age 12 --protocol https --sort rate --save /etc/pacman.d/mirrorlist

# ⚡ Partition Disk (Assumes /dev/sda)
echo "🖥 Partitioning disk..."
(
echo o      # Clear partition table
echo n      # New partition
echo p      # Primary
echo 1      # Partition 1
echo        # Default first sector
echo +512M  # Size
echo t      # Change type
echo 1      # EFI (if BIOS boot, skip this)
echo n      # New partition
echo p
echo 2
echo
echo        # Use rest of the disk
echo w      # Write
) | fdisk /dev/sda

# Format partitions
echo "🧹 Formatting partitions..."
mkfs.fat -F32 /dev/sda1
mkfs.ext4 /dev/sda2

# Mount partitions
mount /dev/sda2 /mnt
mkdir /mnt/boot
mount /dev/sda1 /mnt/boot

# 📦 Install base system
echo "📦 Installing base system..."
pacstrap /mnt base base-devel linux linux-firmware networkmanager sudo nano bash-completion reflector git

# 🔗 Generate fstab
echo "🔗 Generating fstab..."
genfstab -U /mnt >> /mnt/etc/fstab

# Ask for username and password BEFORE chroot
echo "👤 Creating user..."
read -p "Enter your username: " username
read -sp "Enter your password: " password
echo

# Desktop Environment selection
echo "🎨 Choose your Desktop Environment:"
echo "1) KDE Plasma"
echo "2) GNOME"
echo "3) XFCE"
echo "4) Sway (Wayland)"
read -p "Enter number (1-4): " de_choice

# Set desktop environment packages
if [[ $de_choice == 1 ]]; then
    DE_PACKAGES="plasma kde-applications sddm"
    DM_SERVICE="sddm"
elif [[ $de_choice == 2 ]]; then
    DE_PACKAGES="gnome gnome-extra gdm"
    DM_SERVICE="gdm"
elif [[ $de_choice == 3 ]]; then
    DE_PACKAGES="xfce4 xfce4-goodies lightdm lightdm-gtk-greeter"
    DM_SERVICE="lightdm"
elif [[ $de_choice == 4 ]]; then
    DE_PACKAGES="sway foot waybar"
    DM_SERVICE=""
else
    echo "⚠ Invalid choice, no DE will be installed."
    DE_PACKAGES=""
    DM_SERVICE=""
fi

# 📥 Chroot and configure
arch-chroot /mnt /bin/bash <<EOF
set -e

# 🕰️ Timezone
ln -sf /usr/share/zoneinfo/Asia/Dhaka /etc/localtime
hwclock --systohc

# 🗣️ Locale
sed -i 's/#en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# 🏠 Hostname
echo "archlinux" > /etc/hostname
echo "127.0.0.1 localhost" >> /etc/hosts
echo "::1       localhost" >> /etc/hosts
echo "127.0.1.1 archlinux.localdomain archlinux" >> /etc/hosts

# 🔒 Root password
echo "root:$password" | chpasswd

# 👤 Create user
useradd -m -G wheel -s /bin/bash $username
echo "$username:$password" | chpasswd
sed -i 's/# %wheel ALL=(ALL:ALL) ALL/%wheel ALL=(ALL:ALL) ALL/' /etc/sudoers

# 🛜 Enable networking
systemctl enable NetworkManager

# 🖼️ Install Desktop Environment
if [[ ! -z "$DE_PACKAGES" ]]; then
    echo "✨ Installing Desktop Environment..."
    pacman -Sy --noconfirm $DE_PACKAGES
    if [[ ! -z "$DM_SERVICE" ]]; then
        echo "⚙️ Enabling Display Manager..."
        systemctl enable $DM_SERVICE
    else
        echo "ℹ️ No Display Manager (Wayland login from TTY)"
    fi
fi

# 🚀 Install yay AUR helper
cd /home/$username
git clone https://aur.archlinux.org/yay.git
chown -R $username:$username yay
cd yay
sudo -u $username makepkg -si --noconfirm

EOF

# ✅ Done
echo "✅ Installation completed! You can now reboot."
