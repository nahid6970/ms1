#!/bin/bash

# 🎨 Ask for Desktop Environment selection
echo "🎨 Choose your Desktop Environment:"
echo "1) KDE Plasma"
echo "2) GNOME"
echo "3) XFCE"
echo "4) Sway (Wayland)"
read -p "Enter number (1-4): " de_choice

case $de_choice in
    1)
        DE_PACKAGES="plasma kde-applications"
        DM_SERVICE="sddm.service"
        ;;
    2)
        DE_PACKAGES="gnome gnome-extra"
        DM_SERVICE="gdm.service"
        ;;
    3)
        DE_PACKAGES="xfce4 xfce4-goodies"
        DM_SERVICE="lightdm.service"
        ;;
    4)
        DE_PACKAGES="sway swaybg swaylock"
        DM_SERVICE=""
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

# Ask for username and password BEFORE chroot
echo "👤 Creating user..."
read -p "Enter your username: " username
read -sp "Enter your password: " password
echo

# 🏠 Partition, Mount, and Prepare
# [Assuming earlier steps for partitioning and mounting are handled]

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

# 👤 Create user and set password
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

# Prompt for password change after installation
echo "🎉 Installation Complete. Please set your password (if needed)!"
passwd $username

# Final message
echo "✅ Arch Linux Installation Completed Successfully!"
